"""Variantele pe placa video (S49): același calcul ca `MotorBrut` (referința), în PyTorch, pe CUDA.

- placa_fp32: înmulțirile cu greutățile în float32 (fără TF32);
- placa_fp16 / placa_bf16: greutățile și înmulțirile cu ele în float16 / bfloat16, rezultatul înapoi în float32.

În toate trei, ca la referință (S37): LayerNorm, GELU, produsele de atenție și softmax-ul în float64; intrarea (simbol +
poziție) din greutățile float32. Greutățile se citesc o dată cu `MotorBrut` (Q8_0 desfăcut la încărcare) și se mută pe
placă: timpul de încărcare cuprinde și transferul. Fără placă (CUDA) → eroare la încărcare; `inferenta_ccm` ia atunci
rezerva. `dispozitiv="cpu"` doar pentru teste.
"""

from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any

import numpy as np

from unelte.inferenta_bruta import MotorBrut

PRECIZII = ("fp32", "fp16", "bf16")


def placa_disponibila() -> bool:
    try:
        import torch
    except ImportError:
        return False
    return bool(torch.cuda.is_available())


class MotorPlaca:
    def __init__(self, cale: str | Path, precizie: str = "fp32", dispozitiv: str | None = None) -> None:
        import torch

        if precizie not in PRECIZII:
            raise ValueError(f"precizie: {PRECIZII}; am {precizie}")
        if dispozitiv is None:
            if not torch.cuda.is_available():
                raise RuntimeError("fără placă video (CUDA)")
            dispozitiv = "cuda"
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        self.torch = torch
        self.dispozitiv = torch.device(dispozitiv)
        self.precizie = precizie
        self.dtype = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}[precizie]
        ref = MotorBrut(cale, "la_incarcare")
        for k in ("chei", "n_straturi", "n_capete", "n_emb", "context", "vocabular", "eps", "tok"):
            setattr(self, k, getattr(ref, k))
        self.desfacere = "la_incarcare"
        with torch.no_grad():
            # matricile în precizia variantei; vectorii (deplasări, LayerNorm) în float64, ca la referință
            self.m = {k: torch.from_numpy(np.ascontiguousarray(v)).to(self.dispozitiv, self.dtype)
                      for k, v in ref.t.items() if v.ndim == 2}
            self.v = {k: torch.from_numpy(np.asarray(v, dtype=np.float64)).to(self.dispozitiv)
                      for k, v in ref.t.items() if v.ndim == 1}
            self.emb_tok = torch.from_numpy(ref.t["emb_token.weight"]).to(self.dispozitiv, torch.float32)
            self.emb_poz = torch.from_numpy(ref.t["emb_pozitie.weight"]).to(self.dispozitiv, torch.float32)
            if self.dispozitiv.type == "cuda":
                torch.cuda.synchronize(self.dispozitiv)

    # ---- piesele (ca în MotorBrut) -----------------------------------------------------------------------------------

    def _lin(self, x: Any, w: str, b: str | None = None) -> Any:
        y = (x.to(self.dtype) @ self.m[w].T).float()
        return y if b is None else (y.double() + self.v[b]).float()

    def _ln(self, x: Any, p: str) -> Any:
        x = x.double()
        m = x.mean(dim=-1, keepdim=True)
        v = ((x - m) ** 2).mean(dim=-1, keepdim=True)
        return ((x - m) / (v + self.eps).sqrt() * self.v[p + "weight"] + self.v[p + "bias"]).float()

    def _atentie(self, i: int, h: Any, cache: list[Any] | None, start: int) -> Any:
        torch = self.torch
        p = f"straturi.{i}.atentie."
        e, nh = self.n_emb, self.n_capete
        d = e // nh
        lot, t, _ = h.shape
        qkv = self._lin(h, p + "in_proj_weight", p + "in_proj_bias")
        q, k, v = (qkv[..., j * e:(j + 1) * e].reshape(lot, t, nh, d).transpose(1, 2) for j in range(3))
        if cache is not None:
            if cache[i] is not None:
                k = torch.cat([cache[i][0], k], dim=2)
                v = torch.cat([cache[i][1], v], dim=2)
            cache[i] = (k, v)
        n = k.shape[2]
        scor = (q.double() @ k.double().transpose(2, 3)) / math.sqrt(d)
        masca = torch.arange(n, device=self.dispozitiv)[None, :] > (start + torch.arange(t, device=self.dispozitiv))[:, None]
        scor = scor.masked_fill(masca, -math.inf)
        a = (torch.softmax(scor, dim=-1) @ v.double()).float()
        a = a.transpose(1, 2).reshape(lot, t, e)
        return self._lin(a, p + "out_proj.weight", p + "out_proj.bias")

    def _mlp(self, i: int, h: Any) -> Any:
        p = f"straturi.{i}.mlp."
        f = self._lin(h, p + "0.weight", p + "0.bias").double()
        f = (0.5 * f * (1.0 + self.torch.erf(f / math.sqrt(2.0)))).float()
        return self._lin(f, p + "2.weight", p + "2.bias")

    def _strat(self, i: int, x: Any, cache: list[Any] | None = None, start: int = 0) -> Any:
        p = f"straturi.{i}."
        x = x + self._atentie(i, self._ln(x, p + "ln1."), cache, start)
        return x + self._mlp(i, self._ln(x, p + "ln2."))

    def _intrare(self, idx: Any, start: int = 0) -> Any:
        t = idx.shape[1]
        return self.emb_tok[idx] + self.emb_poz[start:start + t]

    def _cap(self, x: Any) -> Any:
        return self._lin(self._ln(x, "ln."), "emb_token.weight")

    def _idx(self, simboluri: Any) -> Any:
        return self.torch.as_tensor(np.asarray(simboluri, dtype=np.int64), device=self.dispozitiv)

    # ---- ce se folosește (ca în MotorBrut) ---------------------------------------------------------------------------

    def logits(self, idx: list[int] | np.ndarray) -> np.ndarray:
        idx = np.asarray(idx, dtype=np.int64)
        un_text = idx.ndim == 1
        if un_text:
            idx = idx[None, :]
        if idx.shape[1] > self.context:
            raise ValueError(f"cel mult {self.context} simboluri deodată; am {idx.shape[1]}")
        with self.torch.no_grad():
            x = self._intrare(self._idx(idx))
            for i in range(self.n_straturi):
                x = self._strat(i, x)
            out = self._cap(x).cpu().numpy().astype(np.float32)
        return out[0] if un_text else out

    def completeaza_simboluri(self, simboluri: list[int], max_simboluri: int) -> tuple[list[int], dict[str, float]]:
        """Ca MotorBrut.completeaza_simboluri (argmax, cache k/v, peste context de la capăt). `.item()` așteaptă placa,
        deci timpii sunt reali."""
        noi: list[int] = []
        with self.torch.no_grad():
            t0 = time.perf_counter()
            cache: list[Any] = [None] * self.n_straturi
            x = self._intrare(self._idx(list(simboluri)[-self.context:])[None, :])
            lungime = x.shape[1]
            for i in range(self.n_straturi):
                x = self._strat(i, x, cache, 0)
            urm = int(self._cap(x[:, -1:])[0, -1].argmax().item())
            noi.append(urm)
            t1 = time.perf_counter()
            while len(noi) < max_simboluri:
                if lungime >= self.context:
                    lg = self.logits((list(simboluri) + noi)[-self.context:])
                    noi.append(int(lg[-1].argmax()))
                    continue
                x = self._intrare(self._idx([[urm]]), lungime)
                for i in range(self.n_straturi):
                    x = self._strat(i, x, cache, lungime)
                lungime += 1
                urm = int(self._cap(x)[0, -1].argmax().item())
                noi.append(urm)
            t2 = time.perf_counter()
        return noi, {"secunde_inceput": t1 - t0, "secunde_restul": t2 - t1,
                     "simboluri_pe_secunda": (len(noi) - 1) / (t2 - t1) if len(noi) > 1 and t2 > t1 else float("nan")}

    def octeti_greutati(self) -> int:
        """Cât ocupă greutățile pe dispozitiv, așa cum le ține motorul (cu copiile float32 ale intrării)."""
        tensori = [*self.m.values(), *self.v.values(), self.emb_tok, self.emb_poz]
        return int(sum(t.numel() * t.element_size() for t in tensori))

    def memorie_placa_mb(self) -> dict[str, float] | None:
        """Cât a ocupat PyTorch pe placă în procesul acesta (maxim), fără contextul CUDA."""
        if self.dispozitiv.type != "cuda":
            return None
        c = self.torch.cuda
        return {"alocat_max": c.max_memory_allocated(self.dispozitiv) / 2 ** 20,
                "rezervat_max": c.max_memory_reserved(self.dispozitiv) / 2 ** 20}


VARIANTE = {f"placa_{p}": (lambda cale, p=p: MotorPlaca(cale, p)) for p in PRECIZII}
