"""S32 (C-21.3): greutățile unui model GPT al lui Kronos într-un fișier binar propriu, citibil fără PyTorch.

Formatul (ideea GGUF, cod scris de noi; descrierea completă, contractul pentru Cyber Universe OS: docs/format_greutati.md):
- antetul: „KGR1”, versiunea, numărul de chei-valori și de tensori (little-endian);
- cheile-valori: setările modelului (straturi, capete, mărimi, tokenizerul ca text JSON);
- lista tensorilor: nume, dimensiuni, felul (F32 sau Q8_0), locul în zona de date;
- zona de date, aliniată la 32 de octeți, fiecare tensor aliniat la 32.
Q8_0 (doar pe greutăți = tensorii cu 2 dimensiuni; LayerNorm și deplasările rămân F32): pe fiecare rând, blocuri de câte
32 de numere, fiecare bloc = o scară float32 (max |x| / 127) + 32 de numere întregi pe un octet (round(x / scară)).

Folosire:
    python unelte/exporta_greutati.py --experiment 415 --fel f32 --iesire lucru/s32/experiment_415_f32.kgr
    python unelte/exporta_greutati.py --experiment 415 --fel q8_0 --iesire lucru/s32/experiment_415_q8_0.kgr
Citirea (fără PyTorch, doar numpy): citeste(cale) → (chei-valori, {nume: tensor}); Q8_0 rămâne Q8_0 până la desfacere.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

import numpy as np

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

MAGIC = b"KGR1"
VERSIUNE = 1
ALINIERE = 32
BLOC_Q8 = 32

# felurile valorilor din chei-valori
VAL_INT, VAL_FLOAT, VAL_TEXT = 1, 2, 3
# felurile tensorilor
F32, Q8_0 = 0, 1
NUME_FEL = {F32: "f32", Q8_0: "q8_0"}
FEL_DIN_NUME = {v: k for k, v in NUME_FEL.items()}


@dataclass
class TensorQ8:
    """Un tensor Q8_0: forma de origine (rânduri × coloane), scările (rânduri × blocuri) și numerele (rânduri × coloane)."""

    forma: tuple[int, ...]
    scari: np.ndarray  # float32
    numere: np.ndarray  # int8

    def desfa(self) -> np.ndarray:
        r, c = self.forma
        return (self.numere.reshape(r, c // BLOC_Q8, BLOC_Q8).astype(np.float32)
                * self.scari[:, :, None]).reshape(r, c)


def cuantizeaza_q8(w: np.ndarray) -> TensorQ8:
    """Q8_0 pe rânduri: blocuri de 32, scara = max |x| / 127 (0 → scara 0 și numerele 0)."""
    w = np.ascontiguousarray(w, dtype=np.float32)
    if w.ndim != 2 or w.shape[1] % BLOC_Q8:
        raise ValueError(f"Q8_0 cere 2 dimensiuni și coloane multiplu de {BLOC_Q8}; am {w.shape}")
    r, c = w.shape
    blocuri = w.reshape(r, c // BLOC_Q8, BLOC_Q8)
    scari = (np.abs(blocuri).max(axis=2) / 127.0).astype(np.float32)
    impartitor = np.where(scari == 0, 1.0, scari)[:, :, None]
    numere = np.clip(np.rint(blocuri / impartitor), -127, 127).astype(np.int8)
    return TensorQ8((r, c), scari, numere.reshape(r, c))


def _pad(n: int) -> int:
    return (-n) % ALINIERE


def _scrie_text(f: BinaryIO, s: str) -> None:
    b = s.encode("utf-8")
    f.write(struct.pack("<Q", len(b)))
    f.write(b)


def _citeste_text(b: memoryview, poz: int) -> tuple[str, int]:
    (n,) = struct.unpack_from("<Q", b, poz)
    poz += 8
    return bytes(b[poz: poz + n]).decode("utf-8"), poz + n


def octeti_tensor(t: np.ndarray | TensorQ8) -> bytes:
    """Zona de date a unui tensor: F32 = numerele la rând; Q8_0 = pe fiecare rând, pe fiecare bloc: scara (4 octeți) +
    32 de octeți (36 de octeți pe bloc)."""
    if isinstance(t, TensorQ8):
        r, c = t.forma
        blocuri = c // BLOC_Q8
        tabel = np.empty((r, blocuri, 4 + BLOC_Q8), dtype=np.uint8)
        tabel[:, :, :4] = t.scari.astype("<f4").view(np.uint8).reshape(r, blocuri, 4)
        tabel[:, :, 4:] = t.numere.reshape(r, blocuri, BLOC_Q8).view(np.uint8)
        return tabel.tobytes()
    return np.ascontiguousarray(t, dtype="<f4").tobytes()


def scrie(cale: str | Path, chei: dict[str, Any], tensori: dict[str, np.ndarray | TensorQ8]) -> int:
    """Scrie fișierul; întoarce mărimea lui în octeți. Ordinea tensorilor = ordinea din dicționar."""
    cale = Path(cale)
    cale.parent.mkdir(parents=True, exist_ok=True)
    date = [(nume, t, octeti_tensor(t)) for nume, t in tensori.items()]
    with cale.open("wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<IQQ", VERSIUNE, len(chei), len(date)))
        for k, v in chei.items():
            _scrie_text(f, k)
            if isinstance(v, bool) or isinstance(v, int):
                f.write(struct.pack("<Iq", VAL_INT, int(v)))
            elif isinstance(v, float):
                f.write(struct.pack("<Id", VAL_FLOAT, v))
            elif isinstance(v, str):
                f.write(struct.pack("<I", VAL_TEXT))
                _scrie_text(f, v)
            else:
                raise TypeError(f"cheia {k}: știu doar int, float, text; am {type(v).__name__}")
        loc = 0
        for nume, t, b in date:
            forma = t.forma if isinstance(t, TensorQ8) else t.shape
            _scrie_text(f, nume)
            f.write(struct.pack("<I", len(forma)))
            f.write(struct.pack(f"<{len(forma)}Q", *forma))
            f.write(struct.pack("<IQ", Q8_0 if isinstance(t, TensorQ8) else F32, loc))
            loc += len(b) + _pad(len(b))
        f.write(b"\0" * _pad(f.tell()))
        for _, _, b in date:
            f.write(b)
            f.write(b"\0" * _pad(len(b)))
        return f.tell()


def citeste(cale: str | Path) -> tuple[dict[str, Any], dict[str, np.ndarray | TensorQ8]]:
    """Cheile-valori și tensorii (F32 ca np.ndarray float32, Q8_0 ca TensorQ8). Fără PyTorch."""
    b = memoryview(Path(cale).read_bytes())
    if bytes(b[:4]) != MAGIC:
        raise ValueError(f"{cale}: nu e un fișier KGR1 (începe cu {bytes(b[:4])!r})")
    versiune, n_chei, n_tensori = struct.unpack_from("<IQQ", b, 4)
    if versiune != VERSIUNE:
        raise ValueError(f"{cale}: versiunea {versiune}; știu doar {VERSIUNE}")
    poz = 4 + struct.calcsize("<IQQ")
    chei: dict[str, Any] = {}
    for _ in range(n_chei):
        k, poz = _citeste_text(b, poz)
        (fel,) = struct.unpack_from("<I", b, poz)
        poz += 4
        if fel == VAL_INT:
            (chei[k],) = struct.unpack_from("<q", b, poz)
            poz += 8
        elif fel == VAL_FLOAT:
            (chei[k],) = struct.unpack_from("<d", b, poz)
            poz += 8
        elif fel == VAL_TEXT:
            chei[k], poz = _citeste_text(b, poz)
        else:
            raise ValueError(f"{cale}: cheia {k} are felul necunoscut {fel}")
    lista = []
    for _ in range(n_tensori):
        nume, poz = _citeste_text(b, poz)
        (n_dim,) = struct.unpack_from("<I", b, poz)
        poz += 4
        forma = struct.unpack_from(f"<{n_dim}Q", b, poz)
        poz += 8 * n_dim
        fel, loc = struct.unpack_from("<IQ", b, poz)
        poz += struct.calcsize("<IQ")
        lista.append((nume, tuple(int(x) for x in forma), fel, loc))
    start = poz + _pad(poz)
    tensori: dict[str, np.ndarray | TensorQ8] = {}
    for nume, forma, fel, loc in lista:
        n = int(np.prod(forma))
        if fel == F32:
            tensori[nume] = np.frombuffer(b, dtype="<f4", count=n, offset=start + loc).reshape(forma).astype(np.float32)
        elif fel == Q8_0:
            r, c = forma
            tabel = np.frombuffer(b, dtype=np.uint8, count=r * (c // BLOC_Q8) * (4 + BLOC_Q8),
                                  offset=start + loc).reshape(r, c // BLOC_Q8, 4 + BLOC_Q8)
            scari = np.ascontiguousarray(tabel[:, :, :4]).view("<f4").reshape(r, c // BLOC_Q8).astype(np.float32)
            numere = np.ascontiguousarray(tabel[:, :, 4:]).view(np.int8).reshape(r, c)
            tensori[nume] = TensorQ8(forma, scari, numere)
        else:
            raise ValueError(f"{cale}: tensorul {nume} are felul necunoscut {fel}")
    return chei, tensori


# ---- exportul din PyTorch --------------------------------------------------------------------------------------------

def tensori_din_retea(retea: Any, setari: dict[str, Any], fel: str) -> dict[str, np.ndarray | TensorQ8]:
    """Tensorii rețelei _GPT (module/model_gpt.py), cu numele din state_dict, în ordinea lui. Capul are aceleași greutăți
    ca intrarea (cap.weight = emb_token.weight), deci nu se scrie de două ori. Q8_0: doar cei cu 2 dimensiuni."""
    if getattr(retea, "memorie", None) is not None:
        raise ValueError("exportul știe doar GPT fără memorie ierarhică (ca W2)")
    stare = retea.state_dict()
    if not (stare["cap.weight"].data_ptr() == stare["emb_token.weight"].data_ptr()):
        raise ValueError("capul nu mai e legat de emb_token: exportul de acum nu știe asta")
    tensori: dict[str, np.ndarray | TensorQ8] = {}
    for nume, t in stare.items():
        if nume == "cap.weight":
            continue
        w = t.detach().float().cpu().numpy()
        tensori[nume] = cuantizeaza_q8(w) if fel == "q8_0" and w.ndim == 2 else w
    return tensori


def chei_model(model: Any, fel: str, sursa: str = "") -> dict[str, Any]:
    s = model.setari
    return {
        "arhitectura": "kronos_gpt",
        "fel": fel,
        "sursa": sursa,
        "n_straturi": int(s["n_straturi"]),
        "n_capete": int(s["n_capete"]),
        "n_emb": int(s["n_emb"]),
        "context": int(s["context"]),
        "vocabular": int(model._marime_vocabular()),
        "ln_eps": 1e-5,
        "cap_legat": 1,
        "tokenizer.bpe": json.dumps(model.tok.ca_dictionar(), ensure_ascii=False) if model.tok is not None else "",
    }


def exporta_model(model: Any, cale: str | Path, fel: str, sursa: str = "") -> int:
    if fel not in FEL_DIN_NUME:
        raise ValueError(f"fel: f32 sau q8_0; am {fel}")
    if model.tokenizer != "bpe" or model._are_pozitii():
        raise ValueError("exportul știe doar modele BPE fără memorie (ca W2)")
    return scrie(cale, chei_model(model, fel, sursa), tensori_din_retea(model.retea, model.setari, fel))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    care = p.add_mutually_exclusive_group(required=True)
    care.add_argument("--experiment", type=int)
    care.add_argument("--gpt", help="S77a: un fișier cale_stare (gpt.pt) dat, ex. lucru/w2_mare/gpt_24.pt (linia w2)")
    p.add_argument("--fel", choices=sorted(FEL_DIN_NUME), required=True)
    p.add_argument("--iesire", required=True)
    a = p.parse_args(argv)
    if a.gpt:
        from unelte.creste_model import model_din_gpt

        model = model_din_gpt(a.gpt, "cpu")
        marime = exporta_model(model, a.iesire, a.fel, sursa=f"{Path(a.gpt).as_posix()} (S77a)")
        print(json.dumps({"gpt": a.gpt, "fel": a.fel, "iesire": a.iesire, "octeti": marime}, ensure_ascii=False))
        return 0
    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    fisa = fisa_modelului(Jurnal(RADACINA / "lucru"), a.experiment)
    model = incarca_modelul(fisa, "cpu")
    marime = exporta_model(model, a.iesire, a.fel, sursa=f"#{fisa['id']} {fisa.get('linie', '')}")
    print(json.dumps({"experiment": fisa["id"], "fel": a.fel, "iesire": a.iesire, "octeti": marime}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
