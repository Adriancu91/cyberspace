"""S139 (C-167): „portarul” — amestecul de adâncimi (Mixture-of-Depths, Raposo et al., 2024, arXiv 2404.02258; doar
ideea, codul e scris aici).

Aceeași rețea ca `module/model_trepte.py` / S135 (0) (straturile, LayerNorm, GELU, capul legat), cu o singură noutate:
la straturile din `straturi_portar` (numerotate de la 1; implicit 2, 4, 6, 8, 10, 12) un **selector** liniar mic
(`Linear(n_emb, 1)` pe intrarea stratului) dă un scor r fiecărui simbol:

- **la antrenare (top-k):** în fiecare text se aleg cei `capacitate × lungime` simboluri cu scorul cel mai mare (256 din
  512 la capacitate 0,5), strânși **în ordinea poziției**; doar ei trec prin atenție + MLP. Întrebările (Q) vin doar de
  la cei aleși, cheile și valorile (K, V) de la **toate** simbolurile intrării stratului, cu masca cauzală după poziția
  **originală**. Ieșirea stratului (atenție + MLP) se înmulțește cu `sigmoid(r)` și se adună la locul ei peste legătura
  directă; ceilalți simboluri trec neschimbați. În plus, o eroare binară (BCE, ponderea `pondere_bce` = 0,01, media pe
  straturile cu portar) învață selectorul să prezică dacă simbolul ar fi fost în top-k (ținta fără gradient) — §3.5 din
  lucrare, „pierderea auxiliară”;
- **la examene și la scris (cauzal):** alegerea e `sigmoid(r) > 0,5`, simbol cu simbol, fără să se uite la viitor;
  ieșirea celor aleși tot cu `sigmoid(r)`. (Calculul se face pe toate pozițiile și se păstrează doar la cei aleși:
  rândurile atenției sunt independente, deci rezultatul e exact cel al trecerii doar a celor aleși.)

`mod_examen` = „cauzal” (implicit) sau „topk” (doar informativ: top-k se uită la scorurile de după, nu e cinstit).
`portar = False` → rețeaua și pasul sunt exact ale lui ModelTrepte (S135 (0)): fără selectori, fără BCE.
Selectorii se construiesc DUPĂ restul rețelei (și după încorporările din N(0; abatere)), ca restul greutăților să iasă
identice cu (0) la aceeași sămânță. Modulul nu schimbă niciun modul existent.
"""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F

from module.model_trepte import ModelTrepte, _GPTTrepte

STRATURI_PORTAR = (2, 4, 6, 8, 10, 12)
MODURI = ("cauzal", "topk")


def alege_topk(r: torch.Tensor, k: int) -> torch.Tensor:
    """r [lot, t] → indicii celor k simboluri cu scorul cel mai mare din fiecare text, în ordinea poziției [lot, k]."""
    return torch.topk(r, k, dim=1).indices.sort(dim=1).values


def masca_alesi(pozitii: torch.Tensor, t: int) -> torch.Tensor:
    """pozitii [lot, k] (originale) → masca [lot, k, t], True = interzis (cheia e după întrebare)."""
    chei = torch.arange(t, device=pozitii.device)
    return chei.view(1, 1, t) > pozitii.unsqueeze(-1)


def strange(x: torch.Tensor, pozitii: torch.Tensor) -> torch.Tensor:
    """x [lot, t, c], pozitii [lot, k] → x[b, pozitii[b, i]] [lot, k, c] (gather)."""
    return x.gather(1, pozitii.unsqueeze(-1).expand(-1, -1, x.size(-1)))


def pune_inapoi(x: torch.Tensor, pozitii: torch.Tensor, valori: torch.Tensor) -> torch.Tensor:
    """Copie a lui x cu x[b, pozitii[b, i]] = valori[b, i] (scatter); restul neschimbat."""
    return x.scatter(1, pozitii.unsqueeze(-1).expand(-1, -1, x.size(-1)), valori)


class _GPTPortar(_GPTTrepte):
    """Rețeaua S135 + selectorii (adăugați cu `adauga_selectori`, după inițializarea restului)."""

    def __init__(self, vocab: int, n_straturi: int, n_capete: int, n_emb: int, context: int, dropout: float,
                 portar: bool = False, capacitate: float = 0.5, straturi_portar: Any = STRATURI_PORTAR,
                 **rest: Any) -> None:
        super().__init__(vocab, n_straturi, n_capete, n_emb, context, dropout, **rest)
        self.n_capete = n_capete
        self.portar = bool(portar)
        self.capacitate = float(capacitate)
        self.straturi_portar = tuple(int(s) for s in straturi_portar) if portar else ()
        self.selectori: nn.ModuleDict | None = None
        self.mod_examen = "cauzal"
        self.cu_sigmoid = True  # doar pentru test: False = ieșirea fără sigmoid(r)
        self.pierderi_bce: list[torch.Tensor] = []
        self.statistici: dict[str, Any] = {}
        self.goleste_statistici()

    def adauga_selectori(self) -> None:
        if self.portar:
            n_emb = self.emb_token.weight.size(1)
            self.selectori = nn.ModuleDict({str(s): nn.Linear(n_emb, 1) for s in self.straturi_portar})

    def goleste_statistici(self) -> None:
        """Numărătorile (pe placă, fără sincronizare la fiecare pas): simboluri trecute prin straturile cu portar,
        câte ar fi alese în modul cauzal, câte se potrivesc cauzal ↔ top-k (doar la antrenare)."""
        self.statistici = {"simboluri": 0, "alesi_cauzal": None, "potrivite": None, "alesi_efectiv": None}

    def _numara(self, cheie: str, valoare: torch.Tensor) -> None:
        v = valoare.detach().sum().float()
        self.statistici[cheie] = v if self.statistici[cheie] is None else self.statistici[cheie] + v

    def citeste_statistici(self) -> dict[str, float | None]:
        s = self.statistici
        n = s["simboluri"]

        def parte(cheie: str) -> float | None:
            return None if not n or s[cheie] is None else float(s[cheie]) / n

        return {"simboluri": n, "parte_aleasa_cauzal": parte("alesi_cauzal"), "potrivire_topk": parte("potrivite"),
                "parte_trecuta": parte("alesi_efectiv")}

    # --- un strat ---------------------------------------------------------------------------

    def _delta(self, strat: nn.Module, h_q: torch.Tensor, h: torch.Tensor, x_q: torch.Tensor,
               masca: torch.Tensor) -> torch.Tensor:
        """Ce adaugă stratul (atenție + MLP) la simbolurile x_q, cu întrebările h_q și cheile/valorile h (toate)."""
        a, _ = strat.atentie(h_q, h, h, attn_mask=masca, need_weights=False)
        y = x_q + a
        return a + strat.mlp(strat.ln2(y))

    def delta_alesi(self, strat: nn.Module, x: torch.Tensor, h: torch.Tensor, pozitii: torch.Tensor) -> torch.Tensor:
        """Doar simbolurile de la `pozitii` (în ordinea poziției) trec prin strat: Q de la ei, K/V de la toate (h),
        masca după poziția originală. Întoarce ce adaugă stratul la ei [lot, k, c]."""
        masca = masca_alesi(pozitii, x.size(1)).repeat_interleave(self.n_capete, dim=0)
        return self._delta(strat, strange(h, pozitii), h, strange(x, pozitii), masca)

    def _strat_portar(self, strat: nn.Module, selector: nn.Module, x: torch.Tensor) -> torch.Tensor:
        lot, t, _ = x.shape
        r = selector(x).squeeze(-1)  # [lot, t]
        h = strat.ln1(x)
        mod = "topk" if self.training else self.mod_examen
        if mod == "topk":
            k = max(1, min(t, round(self.capacitate * t)))
            pozitii = alege_topk(r, k)
            x_q = strange(x, pozitii)
            delta = self.delta_alesi(strat, x, h, pozitii)
            r_q = r.gather(1, pozitii).unsqueeze(-1)
            pondere = torch.sigmoid(r_q) if self.cu_sigmoid else torch.ones_like(r_q)
            iesire = pune_inapoi(x, pozitii, (x_q + pondere * delta).to(x.dtype))
            r_bce = r if r.dtype == torch.float64 else r.float()  # bf16 sub autocast → F32; F64 rămâne (testul)
            with torch.no_grad():
                tinta = torch.zeros_like(r_bce).scatter_(1, pozitii, 1.0)
                cauzal = (r > 0).float()
                self._numara("alesi_cauzal", cauzal)
                self._numara("potrivite", (cauzal == tinta).float())
                self._numara("alesi_efectiv", tinta)
            if self.training:
                self.pierderi_bce.append(F.binary_cross_entropy_with_logits(r_bce, tinta))
        else:
            alesi = (torch.sigmoid(r) > 0.5).unsqueeze(-1)
            masca = self.masca_cauzala(t, x.device)
            delta = self._delta(strat, h, h, x, masca)
            pondere = torch.sigmoid(r).unsqueeze(-1) if self.cu_sigmoid else torch.ones_like(r).unsqueeze(-1)
            iesire = torch.where(alesi, x + pondere * delta, x).to(x.dtype)
            self._numara("alesi_cauzal", alesi)
            self._numara("alesi_efectiv", alesi)
        self.statistici["simboluri"] += lot * t
        return iesire

    def masca_cauzala(self, t: int, dispozitiv: torch.device) -> torch.Tensor:
        return self.straturi[0].masca[:t, :t].to(dispozitiv)

    def trunchi(self, idx: torch.Tensor, memorie: torch.Tensor | None = None) -> torch.Tensor:
        if self.selectori is None:
            return super().trunchi(idx, memorie)
        t = idx.size(1)
        x = self.emb_token(idx) + self.emb_pozitie(torch.arange(t, device=idx.device))
        for i, strat in enumerate(self.straturi, start=1):
            cheie = str(i)
            x = self._strat_portar(strat, self.selectori[cheie], x) if cheie in self.selectori else strat(x)
        return x


class ModelPortar(ModelTrepte):
    MANIFEST = {
        "nume": "model_portar",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 6500},
        "permisiuni": [],
    }

    def __init__(self, portar: bool = False, capacitate: float = 0.5, straturi_portar: Any = STRATURI_PORTAR,
                 pondere_bce: float = 0.01, **setari: Any) -> None:
        super().__init__(**setari)
        if self.k_bucata != 1:
            raise ValueError("model_portar: fără faza pe bucăți (k_bucata = 1)")
        straturi = tuple(int(s) for s in straturi_portar)
        if portar:
            if not 0 < capacitate <= 1:
                raise ValueError("capacitate între 0 (exclus) și 1")
            n = self.setari["n_straturi"]
            if not straturi or any(s < 1 or s > n for s in straturi) or len(set(straturi)) != len(straturi):
                raise ValueError(f"straturi_portar: numere distincte între 1 și {n}")
            if pondere_bce < 0:
                raise ValueError("pondere_bce nu poate fi negativă")
            self.setari.update(portar=True, capacitate=float(capacitate), straturi_portar=list(straturi))
        self.pondere_bce = float(pondere_bce)
        self.bce_recente: list[float] = []  # BCE pe fiecare pas (unealta le citește și le golește la fiecare rând)

    @property
    def portar(self) -> bool:
        return bool(self.setari.get("portar", False))

    def _construieste(self) -> None:
        torch.manual_seed(self.samanta)
        retea = _GPTPortar(self._marime_vocabular(), **self.setari)
        if self.abatere_incorporari is not None:
            with torch.no_grad():
                retea.emb_token.weight.normal_(0.0, self.abatere_incorporari)
                retea.emb_pozitie.weight.normal_(0.0, self.abatere_incorporari)
        retea.adauga_selectori()  # după tot restul: aceleași greutăți ca (0) la aceeași sămânță
        self.retea = retea.to(self.dispozitiv)

    def pas_optimizator(self, loturi: list[torch.Tensor], faza: str, rata: float | None = None) -> dict[str, float]:
        """Pasul ModelTrepte pe simboluri; cu portar, eroarea de optimizat = cross-entropy + pondere_bce × BCE (media pe
        straturile cu portar). „pierdere” rămâne doar cross-entropy (comparabilă cu (0)); BCE separat."""
        if not self.portar:
            return super().pas_optimizator(loturi, faza, rata)
        if faza != "simboluri":
            raise ValueError("model_portar are doar faza „simboluri”")
        assert self.retea is not None and self.optimizator is not None
        if rata is not None:
            for grup in self.optimizator.param_groups:
                grup["lr"] = rata
        self.optimizator.zero_grad(set_to_none=True)
        ctx = self.setari["context"]
        total_ce, total_bce = 0.0, 0.0
        for fereastra in loturi:
            self.retea.pierderi_bce = []
            ce = self.pierdere_simboluri(fereastra[:, :ctx], fereastra[:, 1 : ctx + 1])
            bce = torch.stack(self.retea.pierderi_bce).mean()
            ((ce + self.pondere_bce * bce) / len(loturi)).backward()
            total_ce += ce.item()
            total_bce += bce.item()
        self.retea.pierderi_bce = []
        norma = torch.nn.utils.clip_grad_norm_(self.retea.parameters(), 1.0)
        self.optimizator.step()
        self.bce_recente.append(total_bce / len(loturi))
        return {"pierdere": total_ce / len(loturi), "norma_gradient": float(norma), "bce": total_bce / len(loturi)}

    def _restaureaza(self, salvat: dict[str, Any]) -> None:
        super()._restaureaza(salvat)
        self.setari.setdefault("portar", False)
