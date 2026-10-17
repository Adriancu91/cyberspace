"""Comparația externă (17 octombrie 2026): Kronos față de modele din afară de aceeași mărime, pe același examen.

Pre-înregistrarea: docs/preinregistrari/2026-10-17_comparatie_externa.md. Doar pe procesor; nu atinge placa video,
jurnalul Kronos, examenul oficial sau vreun model de-al nostru.

- **bpb** pe aceleași validări ca unelte/examen_validari_ws.py (aceleași primele --caractere litere), socotit la fel ca
  la Kronos (module/model_gpt.py, biti_pentru): ferestre de câte --fereastra bucăți, una după alta, fără suprapunere;
  prima bucată a textului cu probabilitate egală pe tot vocabularul. Separat, doar ca informație, cu fereastra
  obișnuită a fiecărui model.
- **„continuă din memorie”**: din fiecare validare românească, primele --pasaje texte de cel puțin 500 de litere; modelul
  primește primele ~300 de litere și scrie mai departe, alegând mereu bucata cea mai probabilă. Câte litere la rând se
  potrivesc exact cu textul adevărat? Kronos (care n-a văzut validările) e martorul.

Modelele din afară se descarcă doar fișierele de care e nevoie, la versiunea fixată mai jos (~1,1 GB, în
~/.cache/huggingface). Rezultatul: lucru/comparatie_externa/.

    python unelte/compara_externe.py --kronos 373
"""

from __future__ import annotations

import os

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")  # doar pe procesor: placa video rămâne a antrenării

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.examen_validari_ws import GRUPE, SEPARATOR, VALIDARI, inceput_de_text  # noqa: E402

# id-ul de pe Hugging Face, versiunea fixată (verificată pe 17 octombrie 2026, licența MIT la amândouă) și fișierele
MODELE = {
    "gpt2_small": {"id": "openai-community/gpt2", "versiune": "607a30d783dfa663caf39e06633721c8d4cfcd7e",
                   "fisiere": ["config.json", "generation_config.json", "model.safetensors", "tokenizer.json",
                               "tokenizer_config.json", "vocab.json", "merges.txt"]},
    "gpt_neo_ro_125m": {"id": "iliemihai/gpt-neo-romanian-125m", "versiune": "5b9beb8952ad97512e345d96c9e97387654562b5",
                        "fisiere": ["config.json", "generation_config.json", "pytorch_model.bin", "tokenizer.json",
                                    "tokenizer_config.json", "vocab.json", "merges.txt", "special_tokens_map.json"]},
}
DIN_MEMORIE = ["romana_wikipedia", "romana_web", "romana_carti"]
PRAG_LITERE = 50  # un pasaj „din memorie” = cel puțin atâtea litere identice la rând


class Retea:
    """Ce trebuie de la un model, oricare ar fi: bucăți din text, text din bucăți și răspunsurile pe un lot."""

    nume = ""
    context = 0
    vocabular = 0

    def codifica(self, text: str) -> list[int]:
        raise NotImplementedError

    def decodeaza(self, simboluri: list[int]) -> str:
        raise NotImplementedError

    def logits(self, x: Any) -> Any:
        raise NotImplementedError


class ReteaKronos(Retea):
    def __init__(self, model: Any, nume: str = "kronos") -> None:
        if model.tok is None or model._are_pozitii():
            raise ValueError("comparația merge doar cu modelele Kronos pe bucăți de cuvinte, fără memorie")
        self.model, self.nume = model, nume
        self.context, self.vocabular = model.setari["context"], model._marime_vocabular()

    def codifica(self, text: str) -> list[int]:
        return self.model.tok.codifica(text)

    def decodeaza(self, simboluri: list[int]) -> str:
        return self.model.tok.decodeaza(simboluri)

    def logits(self, x: Any) -> Any:
        self.model.retea.eval()
        with self.model._autocast():
            return self.model.retea(x, None).float()


class ReteaHF(Retea):
    def __init__(self, nume: str, cale: str | Path) -> None:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.nume = nume
        self.tok = AutoTokenizer.from_pretrained(cale)
        self.retea = AutoModelForCausalLM.from_pretrained(cale, dtype="float32").eval()
        self.context = int(self.retea.config.max_position_embeddings)
        self.vocabular = int(self.retea.config.vocab_size)

    def codifica(self, text: str) -> list[int]:
        return self.tok(text, add_special_tokens=False, verbose=False)["input_ids"]

    def decodeaza(self, simboluri: list[int]) -> str:
        return self.tok.decode(simboluri, clean_up_tokenization_spaces=False)

    def logits(self, x: Any) -> Any:
        return self.retea(input_ids=x).logits.float()


def descarca(nume: str) -> Path:
    from huggingface_hub import snapshot_download

    m = MODELE[nume]
    return Path(snapshot_download(m["id"], revision=m["versiune"], allow_patterns=m["fisiere"]))


def biti(retea: Retea, text: str, fereastra: int) -> float:
    """Biții pe tot textul, socotiți ca la Kronos (module/model_gpt.py, biti_pentru), cu ferestre de `fereastra`."""
    import torch
    import torch.nn.functional as F

    if not text:
        return 0.0
    idx = torch.tensor(retea.codifica(text), dtype=torch.long)
    total = math.log2(retea.vocabular)  # primul simbol nu are context
    deodata = max(1, min(64, 2**26 // (fereastra * retea.vocabular)))
    starturi = range(0, len(idx) - 1, fereastra)
    intregi = [s for s in starturi if s + fereastra + 1 <= len(idx)]
    rest = [s for s in starturi if s + fereastra + 1 > len(idx)]
    nats = 0.0
    with torch.no_grad():
        for grup in [intregi[i: i + deodata] for i in range(0, len(intregi), deodata)] + [[s] for s in rest]:
            n = min(fereastra, len(idx) - 1 - grup[0])
            x = torch.stack([idx[s: s + n] for s in grup])
            y = torch.stack([idx[s + 1: s + n + 1] for s in grup])
            out = retea.logits(x)
            nats += F.cross_entropy(out.reshape(-1, out.size(-1)), y.reshape(-1), reduction="sum").item()
    return total + nats / math.log(2)


def examen(retea: Retea, caractere: int, fereastra: int, validari: dict[str, str] | None = None) -> dict[str, Any]:
    """bpb pe fiecare validare și mediile pe grupe (pe octeți), ca unelte/examen_validari_ws.py."""
    rezultate: dict[str, Any] = {}
    for nume, cale in (validari or VALIDARI).items():
        if not Path(cale).exists():
            rezultate[nume] = {"lipseste": cale}
            continue
        text = inceput_de_text(Path(cale), caractere)
        octeti = len(text.encode("utf-8"))
        rezultate[nume] = {"bpb": round(biti(retea, text, fereastra) / octeti, 4), "octeti": octeti}
    for grupa, parti in GRUPE.items():
        avem = [rezultate[p] for p in parti if "bpb" in rezultate.get(p, {})]
        if avem:
            octeti = sum(r["octeti"] for r in avem)
            rezultate[f"media_{grupa}"] = {"bpb": round(sum(r["bpb"] * r["octeti"] for r in avem) / octeti, 4),
                                           "octeti": octeti}
    return rezultate


def pasaje(cale: Path, cate: int, minim: int = 500, prefix: int = 300, adevar: int = 120) -> list[tuple[str, str]]:
    """Primele `cate` texte de cel puțin `minim` litere: începutul (~`prefix` litere, tăiat la un spațiu) și ce urmează."""
    gasite: list[tuple[str, str]] = []
    bucata = ""
    with cale.open(encoding="utf-8") as f:
        for rand in f:
            bucata += rand
            if SEPARATOR not in bucata:
                continue
            *texte, bucata = bucata.split(SEPARATOR)
            for text in texte:
                text = text.strip()
                if len(text) < minim:
                    continue
                taietura = text.rfind(" ", 0, prefix)
                taietura = taietura if taietura > prefix // 2 else prefix
                gasite.append((text[:taietura], text[taietura: taietura + adevar]))
                if len(gasite) >= cate:
                    return gasite
    return gasite


def continua_lacom(retea: Retea, inceput: str, litere: int = 100, maxim_bucati: int = 64) -> str:
    """Ce scrie modelul după `inceput`, alegând mereu bucata cea mai probabilă, până are cel puțin `litere` litere."""
    import torch

    simboluri = retea.codifica(inceput)
    noi: list[int] = []
    with torch.no_grad():
        for _ in range(maxim_bucati):
            x = torch.tensor([(simboluri + noi)[-retea.context:]], dtype=torch.long)
            noi.append(int(retea.logits(x)[0, -1].argmax()))
            if len(retea.decodeaza(noi)) >= litere:
                break
    return retea.decodeaza(noi)


def litere_identice(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def din_memorie(retea: Retea, lista: list[tuple[str, str]]) -> dict[str, Any]:
    potriviri = [litere_identice(continua_lacom(retea, inceput), adevar) for inceput, adevar in lista]
    if not potriviri:
        return {"pasaje": 0}
    return {"pasaje": len(potriviri), "parte_din_memorie": round(sum(p >= PRAG_LITERE for p in potriviri) / len(potriviri), 4),
            "mediana_litere": statistics.median(potriviri), "potriviri": potriviri}


def verdict_memorie(neo: float, kronos: float) -> str:
    """Regula din pre-înregistrare: cel puțin 10 puncte procentuale peste Kronos și cel puțin dublu."""
    return "a văzut probabil" if neo - kronos >= 0.10 and neo >= 2 * kronos else "nu se vede că le-a văzut"


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Kronos față de GPT-2 small și GPT-Neo românesc 125M, pe procesor.")
    parser.add_argument("--kronos", type=int, required=True, help="modelul salvat de Kronos la acest experiment (martorul)")
    parser.add_argument("--modele", default=",".join(MODELE), help="care din modelele din afară")
    parser.add_argument("--caractere", type=int, default=100_000)
    parser.add_argument("--fereastra", type=int, default=512, help="cifra principală: ferestre de atâtea bucăți")
    parser.add_argument("--pasaje", type=int, default=150, help="câte texte din fiecare validare la „din memorie”")
    parser.add_argument("--fire", type=int, default=6)
    parser.add_argument("--director-lucru", default="lucru")
    args = parser.parse_args(argv)

    import torch

    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    torch.set_num_threads(max(1, args.fire))
    dosar = Path(args.director_lucru) / "comparatie_externa"
    dosar.mkdir(parents=True, exist_ok=True)
    iesire = dosar / f"comparatie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    raport: dict[str, Any] = {"kronos": args.kronos, "caractere": args.caractere, "fereastra": args.fereastra,
                              "fire": args.fire, "modele": {}}

    def salveaza() -> None:
        iesire.write_text(json.dumps(raport, ensure_ascii=False, indent=1), encoding="utf-8")

    seturi = {v: pasaje(Path(VALIDARI[v]), args.pasaje) for v in DIN_MEMORIE if Path(VALIDARI.get(v, "")).is_file()}
    kronos = ReteaKronos(incarca_modelul(fisa_modelului(Jurnal(Path(args.director_lucru)), args.kronos), "cpu"),
                         f"kronos_{args.kronos}")
    retele: list[tuple[str, Any]] = [(kronos.nume, lambda: kronos)]
    for nume in [m for m in args.modele.split(",") if m]:
        retele.append((nume, lambda nume=nume: ReteaHF(nume, descarca(nume))))

    for nume, fa in retele:
        inceput = time.monotonic()
        retea = fa()
        r: dict[str, Any] = {"context": retea.context, "vocabular": retea.vocabular}
        if nume in MODELE:
            r.update({"id": MODELE[nume]["id"], "versiune": MODELE[nume]["versiune"]})
            r["examen"] = examen(retea, args.caractere, args.fereastra)
            r["examen_fereastra_proprie"] = examen(retea, args.caractere, retea.context)
        if nume == kronos.nume or "neo" in nume:
            r["din_memorie"] = {v: din_memorie(retea, lista) for v, lista in seturi.items()}
        r["secunde"] = round(time.monotonic() - inceput, 1)
        raport["modele"][nume] = r
        salveaza()
        print(f"=== {nume} ({r['secunde']:.0f} s) ===", flush=True)
        for v, x in r.get("examen", {}).items():
            if "bpb" in x:
                proprie = r["examen_fereastra_proprie"][v]["bpb"]
                print(f"  {v:<18} bpb {x['bpb']:.4f}   (fereastra {retea.context}: {proprie:.4f})", flush=True)
        for v, x in r.get("din_memorie", {}).items():
            if x.get("pasaje"):
                print(f"  din memorie, {v:<17} {x['parte_din_memorie']:.1%} (mediana {x['mediana_litere']} litere)", flush=True)
        del retea

    neo = next((n for n in raport["modele"] if "neo" in n), None)
    if neo:
        raport["verdict_memorie"] = {
            v: verdict_memorie(raport["modele"][neo]["din_memorie"][v]["parte_din_memorie"],
                               raport["modele"][kronos.nume]["din_memorie"][v]["parte_din_memorie"])
            for v in seturi if raport["modele"][neo]["din_memorie"][v].get("pasaje")}
        salveaza()
        for v, ce in raport["verdict_memorie"].items():
            print(f"{v}: {neo} {ce} textele noastre", flush=True)
    print(f"Toate cifrele: {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
