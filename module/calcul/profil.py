"""S47: unde se duce timpul la o completare greedy, pe operații.

`MotorCronometrat` face exact calculul din `MotorBrut` (aceleași funcții, aceeași ordine), cu un cronometru în jurul
fiecărei operații. Că e același calcul se verifică la fiecare profil: simbolurile trebuie să fie identice cu ale
referinței (altfel profilul e refuzat).
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from unelte.exporta_greutati import TensorQ8
from unelte.inferenta_bruta import MotorBrut, gelu, layer_norm, softmax

OPERATII = ("desfacere_q8", "inmultire_qkv", "inmultire_out", "inmultire_mlp", "inmultire_cap", "atentie",
            "normalizare", "gelu", "intrare", "esantionare")


class MotorCronometrat(MotorBrut):
    def __init__(self, cale: str | Path, desfacere: str = "la_incarcare") -> None:
        t0 = time.perf_counter()
        super().__init__(cale, desfacere)
        self.secunde_incarcare = time.perf_counter() - t0
        self.timp: dict[str, float] = defaultdict(float)

    def _cronometru(self, op: str, t0: float) -> float:
        t1 = time.perf_counter()
        self.timp[op] += t1 - t0
        return t1

    def _w(self, nume: str) -> np.ndarray:
        w = self.t[nume]
        if not isinstance(w, TensorQ8):
            return w
        t0 = time.perf_counter()
        d = w.desfa()
        self._cronometru("desfacere_q8", t0)
        return d

    def _ln(self, x: np.ndarray, w: np.ndarray, b: np.ndarray) -> np.ndarray:
        t0 = time.perf_counter()
        y = layer_norm(x, w, b, self.eps)
        self._cronometru("normalizare", t0)
        return y

    def _atentie(self, i: int, h: np.ndarray, cache: list[Any] | None, start: int) -> np.ndarray:
        p = f"straturi.{i}.atentie."
        e, nh = self.n_emb, self.n_capete
        d = e // nh
        lot, t, _ = h.shape
        w = self._w(p + "in_proj_weight")
        t0 = time.perf_counter()
        qkv = h @ w.T + self.t[p + "in_proj_bias"]
        t0 = self._cronometru("inmultire_qkv", t0)
        q, k, v = (qkv[..., j * e:(j + 1) * e].reshape(lot, t, nh, d).transpose(0, 2, 1, 3) for j in range(3))
        if cache is not None:
            if cache[i] is not None:
                k = np.concatenate([cache[i][0], k], axis=2)
                v = np.concatenate([cache[i][1], v], axis=2)
            cache[i] = (k, v)
        n = k.shape[2]
        scor = (q.astype(np.float64) @ k.astype(np.float64).transpose(0, 1, 3, 2)) / math.sqrt(d)
        masca = np.arange(n)[None, :] > (start + np.arange(t))[:, None]
        scor = np.where(masca, -np.inf, scor)
        a = (softmax(scor) @ v.astype(np.float64)).astype(np.float32)
        a = a.transpose(0, 2, 1, 3).reshape(lot, t, e)
        self._cronometru("atentie", t0)
        w = self._w(p + "out_proj.weight")
        t0 = time.perf_counter()
        y = (a @ w.T + self.t[p + "out_proj.bias"]).astype(np.float32)
        self._cronometru("inmultire_out", t0)
        return y

    def _mlp(self, i: int, h: np.ndarray) -> np.ndarray:
        p = f"straturi.{i}.mlp."
        w0 = self._w(p + "0.weight")
        t0 = time.perf_counter()
        f = h @ w0.T + self.t[p + "0.bias"]
        t0 = self._cronometru("inmultire_mlp", t0)
        f = gelu(f)
        self._cronometru("gelu", t0)
        w2 = self._w(p + "2.weight")
        t0 = time.perf_counter()
        y = (f @ w2.T + self.t[p + "2.bias"]).astype(np.float32)
        self._cronometru("inmultire_mlp", t0)
        return y

    def _strat(self, i: int, x: np.ndarray, cache: list[Any] | None = None, start: int = 0) -> np.ndarray:
        p = f"straturi.{i}."
        x = x + self._atentie(i, self._ln(x, self.t[p + "ln1.weight"], self.t[p + "ln1.bias"]), cache, start)
        return x + self._mlp(i, self._ln(x, self.t[p + "ln2.weight"], self.t[p + "ln2.bias"]))

    def _intrare(self, idx: np.ndarray, start: int = 0) -> np.ndarray:
        emb, poz = self._w("emb_token.weight"), self._w("emb_pozitie.weight")
        t0 = time.perf_counter()
        y = (emb[idx] + poz[start:start + idx.shape[1]]).astype(np.float32)
        self._cronometru("intrare", t0)
        return y

    def _cap(self, x: np.ndarray) -> np.ndarray:
        h = self._ln(x, self.t["ln.weight"], self.t["ln.bias"])
        w = self._w("emb_token.weight")
        t0 = time.perf_counter()
        y = h @ w.T
        self._cronometru("inmultire_cap", t0)
        return _Argmax(y, self)


class _Argmax(np.ndarray):
    """Logit-urile capului; `argmax` (eșantionarea greedy) e cronometrat separat."""

    def __new__(cls, a: np.ndarray, motor: MotorCronometrat) -> "_Argmax":
        o = np.asarray(a).view(cls)
        o._motor = motor
        return o

    def __array_finalize__(self, o: Any) -> None:
        self._motor = getattr(o, "_motor", None)

    def argmax(self, *a: Any, **k: Any) -> Any:
        t0 = time.perf_counter()
        r = np.asarray(self).argmax(*a, **k)
        if self._motor is not None:
            self._motor._cronometru("esantionare", t0)
        return r


def profil(cale: str | Path, text: str | list[int], simboluri: int = 64, desfacere: str = "la_incarcare") -> dict[str, Any]:
    """Un profil: încărcarea, apoi completarea greedy de `simboluri` după `text` (sau după simbolurile date). Refuză dacă
    simbolurile diferă de referință (MotorBrut cu aceeași desfacere)."""
    m = MotorCronometrat(cale, desfacere)
    s = list(text) if isinstance(text, list) else m.tok.codifica(text)
    t0 = time.perf_counter()
    noi, timpi = m.completeaza_simboluri(s, simboluri)
    total = time.perf_counter() - t0
    ref, _ = MotorBrut(cale, desfacere).completeaza_simboluri(s, simboluri)
    if [int(x) for x in noi] != [int(x) for x in ref]:
        raise RuntimeError("profilul nu dă aceleași simboluri ca referința: cronometrul a schimbat calculul")
    ms = {op: 1000 * m.timp.get(op, 0.0) for op in OPERATII}
    ms["restul"] = 1000 * total - sum(ms.values())
    return {
        "fisier": str(cale), "desfacere": desfacere, "text": text, "simboluri_inceput": len(s),
        "simboluri_noi": len(noi), "text_nou": m.tok.decodeaza(noi) if m.tok is not None else "",
        "ms_incarcare": 1000 * m.secunde_incarcare, "ms_completare": 1000 * total,
        "ms_inceput": 1000 * timpi["secunde_inceput"], "simboluri_pe_secunda": timpi["simboluri_pe_secunda"],
        "ms_pe_operatie": ms,
        "procent_pe_operatie": {op: 100 * v / (1000 * total) for op, v in ms.items()},
    }
