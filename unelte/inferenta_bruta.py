"""S32 (C-21.3): motorul de inferență fără PyTorch (Python + numpy) pentru fișierele KGR1 din unelte/exporta_greutati.py.

Face exact calculul rețelei _GPT din module/model_gpt.py, strat cu strat: intrarea (simbol + poziție), 12 blocuri (LayerNorm →
atenția cu mască spre viitor → plus; LayerNorm → MLP cu GELU exact → plus), LayerNorm-ul final și capul legat de intrare.
Atenția: nn.MultiheadAttention ține q, k, v într-o singură matrice (in_proj_weight, 3 × n_emb rânduri, în ordinea q, k, v),
capetele sunt bucăți la rând de câte n_emb / n_capete coloane.

Nu e un modul pe platformă: portul „model” cere și antrenare (antreneaza), iar motorul doar citește; un port nou
(„inferenta”) rămâne la Adrian (kronos/ și contractele se schimbă doar cu aprobarea lui).

Q8_0: cu desfacere="la_incarcare", greutățile se desfac o dată în float32 (aceeași viteză ca F32, memoria ca F32);
cu desfacere="la_pas", rămân pe un octet în memorie și se desfac la fiecare înmulțire (memorie ~4× mai puțină, mai încet
în numpy; un motor scris în C pe numere întregi n-ar avea pasul ăsta).
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

RADACINA = Path(__file__).resolve().parents[1]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.exporta_greutati import TensorQ8, citeste  # noqa: E402

DESFACERI = ("la_incarcare", "la_pas")


def erf(x: np.ndarray) -> np.ndarray:
    """erf fără scipy: Abramowitz și Stegun 7.1.26 (eroare < 1,5e-7), pe float64."""
    x = np.asarray(x, dtype=np.float64)
    s = np.sign(x)
    a = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * a)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * np.exp(-a * a)
    return s * y


def gelu(x: np.ndarray) -> np.ndarray:
    """GELU exact (ca nn.GELU()): x · Φ(x) = 0,5 · x · (1 + erf(x / √2))."""
    return (0.5 * x * (1.0 + erf(x / math.sqrt(2.0)))).astype(np.float32)


def layer_norm(x: np.ndarray, w: np.ndarray, b: np.ndarray, eps: float) -> np.ndarray:
    """S37: media și varianța adunate în float64; rezultatul înapoi în float32."""
    x = np.asarray(x, dtype=np.float64)
    m = x.mean(axis=-1, keepdims=True)
    v = ((x - m) ** 2).mean(axis=-1, keepdims=True)
    return ((x - m) / np.sqrt(v + eps) * w + b).astype(np.float32)


def softmax(x: np.ndarray) -> np.ndarray:
    """S37: în float64 (și suma); cine vrea float32 convertește după."""
    x = np.asarray(x, dtype=np.float64)
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


class MotorBrut:
    """Modelul dintr-un fișier KGR1. simboluri → logits, biți pe un text, completare fără întâmplare (cu cache k/v)."""

    def __init__(self, cale: str | Path, desfacere: str = "la_incarcare") -> None:
        if desfacere not in DESFACERI:
            raise ValueError(f"desfacere: {DESFACERI}; am {desfacere}")
        self.chei, tensori = citeste(cale)
        if self.chei.get("arhitectura") != "kronos_gpt":
            raise ValueError(f"{cale}: arhitectura {self.chei.get('arhitectura')}; știu doar kronos_gpt")
        self.desfacere = desfacere
        self.t = {k: (v.desfa() if isinstance(v, TensorQ8) and desfacere == "la_incarcare" else v) for k, v in tensori.items()}
        self.n_straturi = int(self.chei["n_straturi"])
        self.n_capete = int(self.chei["n_capete"])
        self.n_emb = int(self.chei["n_emb"])
        self.context = int(self.chei["context"])
        self.vocabular = int(self.chei["vocabular"])
        self.eps = float(self.chei["ln_eps"])
        self.tok = None
        if self.chei.get("tokenizer.bpe"):
            from module.tokenizer_bpe import TokenizerBPE

            self.tok = TokenizerBPE.din_dictionar(json.loads(self.chei["tokenizer.bpe"]))

    # ---- piesele ----------------------------------------------------------------------------------------------------

    def _w(self, nume: str) -> np.ndarray:
        w = self.t[nume]
        return w.desfa() if isinstance(w, TensorQ8) else w

    def octeti_greutati(self) -> int:
        """Cât ocupă greutățile în memorie (așa cum le ține motorul)."""
        return sum(v.scari.nbytes + v.numere.nbytes if isinstance(v, TensorQ8) else v.nbytes for v in self.t.values())

    def _atentie(self, i: int, h: np.ndarray, cache: list[Any] | None, start: int) -> np.ndarray:
        """h: (lot, t, n_emb). Cu cache (lot 1): cheile și valorile de dinainte se păstrează; pozițiile încep la start."""
        p = f"straturi.{i}.atentie."
        e, nh = self.n_emb, self.n_capete
        d = e // nh
        lot, t, _ = h.shape
        qkv = h @ self._w(p + "in_proj_weight").T + self.t[p + "in_proj_bias"]
        q, k, v = (qkv[..., j * e:(j + 1) * e].reshape(lot, t, nh, d).transpose(0, 2, 1, 3) for j in range(3))
        if cache is not None:
            if cache[i] is not None:
                k = np.concatenate([cache[i][0], k], axis=2)
                v = np.concatenate([cache[i][1], v], axis=2)
            cache[i] = (k, v)
        n = k.shape[2]
        # S37: produsele de atenție (q·k și ponderile · v) în float64, înapoi în float32 înainte de out_proj
        scor = (q.astype(np.float64) @ k.astype(np.float64).transpose(0, 1, 3, 2)) / math.sqrt(d)
        # interogarea j (poziția start + j) vede cheile 0 … start + j
        masca = np.arange(n)[None, :] > (start + np.arange(t))[:, None]
        scor = np.where(masca, -np.inf, scor)
        a = (softmax(scor) @ v.astype(np.float64)).astype(np.float32)
        a = a.transpose(0, 2, 1, 3).reshape(lot, t, e)
        return (a @ self._w(p + "out_proj.weight").T + self.t[p + "out_proj.bias"]).astype(np.float32)

    def _mlp(self, i: int, h: np.ndarray) -> np.ndarray:
        p = f"straturi.{i}.mlp."
        f = gelu(h @ self._w(p + "0.weight").T + self.t[p + "0.bias"])
        return (f @ self._w(p + "2.weight").T + self.t[p + "2.bias"]).astype(np.float32)

    def _strat(self, i: int, x: np.ndarray, cache: list[Any] | None = None, start: int = 0) -> np.ndarray:
        p = f"straturi.{i}."
        x = x + self._atentie(i, layer_norm(x, self.t[p + "ln1.weight"], self.t[p + "ln1.bias"], self.eps), cache, start)
        return x + self._mlp(i, layer_norm(x, self.t[p + "ln2.weight"], self.t[p + "ln2.bias"], self.eps))

    def _intrare(self, idx: np.ndarray, start: int = 0) -> np.ndarray:
        t = idx.shape[1]
        return (self._w("emb_token.weight")[idx] + self._w("emb_pozitie.weight")[start:start + t]).astype(np.float32)

    def _cap(self, x: np.ndarray) -> np.ndarray:
        return layer_norm(x, self.t["ln.weight"], self.t["ln.bias"], self.eps) @ self._w("emb_token.weight").T

    # ---- ce se folosește --------------------------------------------------------------------------------------------

    def straturi(self, simboluri: list[int] | np.ndarray) -> list[np.ndarray]:
        """Starea după intrare și după fiecare strat (pentru testul strat cu strat), pe un singur text."""
        x = self._intrare(np.asarray(simboluri, dtype=np.int64)[None, :])
        stari = [x[0]]
        for i in range(self.n_straturi):
            x = self._strat(i, x)
            stari.append(x[0])
        return stari

    def logits(self, idx: list[int] | np.ndarray) -> np.ndarray:
        """idx: (t,) sau (lot, t), t ≤ context → logits (… , t, vocabular), float32."""
        idx = np.asarray(idx, dtype=np.int64)
        un_text = idx.ndim == 1
        if un_text:
            idx = idx[None, :]
        if idx.shape[1] > self.context:
            raise ValueError(f"cel mult {self.context} simboluri deodată; am {idx.shape[1]}")
        x = self._intrare(idx)
        for i in range(self.n_straturi):
            x = self._strat(i, x)
        out = self._cap(x).astype(np.float32)
        return out[0] if un_text else out

    def biti_pentru_simboluri(self, simboluri: list[int], deodata: int = 4) -> float:
        """Ca ModelGPT.biti_pentru: primul simbol cu șansă uniformă (log2 vocabular), apoi ferestre de context + 1
        simboluri (ultima poate fi mai scurtă), fiecare fereastră pornind fără nimic în față."""
        idx = np.asarray(simboluri, dtype=np.int64)
        if len(idx) == 0:
            return 0.0
        ctx = self.context
        nats = 0.0
        starturi = range(0, len(idx) - 1, ctx)
        intregi = [s for s in starturi if s + ctx + 1 <= len(idx)]
        rest = [s for s in starturi if s + ctx + 1 > len(idx)]
        grupuri = [intregi[i: i + deodata] for i in range(0, len(intregi), deodata)] + [[s] for s in rest]
        for grup in grupuri:
            n = min(ctx, len(idx) - 1 - grup[0])
            x = np.stack([idx[s: s + n] for s in grup])
            y = np.stack([idx[s + 1: s + n + 1] for s in grup])
            lg = self.logits(x).astype(np.float64)
            m = lg.max(axis=-1, keepdims=True)
            lse = (m + np.log(np.exp(lg - m).sum(axis=-1, keepdims=True)))[..., 0]
            nats += float((lse - np.take_along_axis(lg, y[..., None], axis=-1)[..., 0]).sum())
        return math.log2(self.vocabular) + nats / math.log(2)

    def biti_pentru(self, text: str, deodata: int = 4) -> float:
        if not text:
            return 0.0
        assert self.tok is not None, "fișierul nu are tokenizer"
        return self.biti_pentru_simboluri(self.tok.codifica(text), deodata)

    def completeaza_simboluri(self, simboluri: list[int], max_simboluri: int) -> tuple[list[int], dict[str, float]]:
        """Fără întâmplare (argmax), cu cache k/v cât încape în context; peste context, ca ModelGPT.completeaza:
        ultimele `context` simboluri, de la capăt. Întoarce simbolurile noi și timpii (început, pe simbol)."""
        noi: list[int] = []
        t0 = time.perf_counter()
        cache: list[Any] = [None] * self.n_straturi
        x = self._intrare(np.asarray(simboluri[-self.context:], dtype=np.int64)[None, :])
        lungime = x.shape[1]
        for i in range(self.n_straturi):
            x = self._strat(i, x, cache, 0)
        urm = int(self._cap(x[:, -1:])[0, -1].argmax())
        noi.append(urm)
        t1 = time.perf_counter()
        while len(noi) < max_simboluri:
            if lungime >= self.context:  # nu mai încape: de la capăt, pe ultimele context simboluri
                lg = self.logits((list(simboluri) + noi)[-self.context:])
                noi.append(int(lg[-1].argmax()))
                continue
            x = self._intrare(np.asarray([[urm]], dtype=np.int64), lungime)
            for i in range(self.n_straturi):
                x = self._strat(i, x, cache, lungime)
            lungime += 1
            urm = int(self._cap(x)[0, -1].argmax())
            noi.append(urm)
        t2 = time.perf_counter()
        return noi, {"secunde_inceput": t1 - t0, "secunde_restul": t2 - t1,
                     "simboluri_pe_secunda": (len(noi) - 1) / (t2 - t1) if len(noi) > 1 and t2 > t1 else float("nan")}

    def completeaza(self, inceput: str, max_simboluri: int = 6) -> str:
        assert self.tok is not None, "fișierul nu are tokenizer"
        noi, _ = self.completeaza_simboluri(self.tok.codifica(inceput or " "), max_simboluri)
        return self.tok.decodeaza(noi)
