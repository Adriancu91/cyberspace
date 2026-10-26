"""Muon + gradient adunat + răcire la final (S30, C-21.2, aprobat de Adrian pe 26 octombrie 2026).

Ca model_conversatie, plus trei opțiuni, toate oprite implicit (fără ele, aceiași pași exact ca ModelGPTConversatie):
- `optimizator = "muon"` (implicit "adamw"): Muon pe matricile din straturi (atenția și MLP-ul), AdamW ca până acum pe
  rest (intrarea, care e legată de ieșire, pozițiile, LayerNorm, bias). Muon, scris de noi după descrierea publică a lui
  Keller Jordan (2024, „Muon: An optimizer for hidden layers in neural networks”): momentum 0,95 Nesterov, apoi
  gradientul se „ortogonalizează” cu 5 pași Newton-Schulz în bf16 (valorile singulare ajung în ~[0,7; 1,1]), scalat cu
  √max(1, rânduri/coloane). `rata_muon` (implicit 0,02) e rata lui la vârf; urmează aceeași formă ca rata_invatare
  (încălzire, răcire). Matricea combinată q/k/v a atenției se ortogonalizează pe cele 3 bucăți, separat.
- `adunare_loturi = 8` (implicit 1): optimizatorul face un pas la 8 loturi (gradientul lor adunat, pierderea ÷ 8).
  „pasi” rămâne numărul de loturi (textul văzut se socotește la fel); `pasi_optimizator` e în statistici. Loturile de la
  sfârșit care nu mai fac 8 se aruncă (cel mult 7).
- `racire_finala = 0.25` (implicit 0): în ultimele 25% din antrenarea plănuită (durata_scaderii_secunde, care trebuie
  dată) rata scade în linie dreaptă până la `fractie_dupa_racire` (implicit 0) din ea.
Optimizatorul n-are un port al lui în kronos/, de aceea stă aici, într-un modul de model.
"""

from __future__ import annotations

import math
from typing import Any

import torch
import torch.nn.functional as F

from module.model_continuu import ia_placa
from module.model_conversatie import IGNORAT, ModelGPTConversatie

OPTIMIZATOARE = ("adamw", "muon")
NS_COEFICIENTI = (3.4445, -4.7750, 2.0315)  # ai polinomului de gradul 5 din descrierea publică Muon


def newton_schulz(g: torch.Tensor, pasi: int = 5) -> torch.Tensor:
    """Aproape „ortogonalizează” matricea g (aceleași direcții, valorile singulare aduse spre 1), în bf16."""
    a, b, c = NS_COEFICIENTI
    x = g.bfloat16()
    x = x / (x.norm() + 1e-7)
    intoarsa = x.size(0) > x.size(1)
    if intoarsa:
        x = x.T
    for _ in range(pasi):
        m = x @ x.T
        x = a * x + (b * m + c * m @ m) @ x
    return (x.T if intoarsa else x).to(g.dtype)


class MuonCuAdamW(torch.optim.Optimizer):
    """Un singur optimizator cu grupuri: cele cu muon=True merg cu Muon, celelalte cu AdamW (ca torch.optim.AdamW, fără
    amsgrad). Rata reală a unui grup = lr × multiplicator_lr: bucla de antrenare scrie în lr doar forma ratei (aceeași
    pentru toate grupurile), iar multiplicatorul ține rata Muon (ex. 0,02 / 0,00005 = 400)."""

    def __init__(self, grupuri: list[dict[str, Any]], lr: float, betas: tuple[float, float] = (0.9, 0.999),
                 eps: float = 1e-8, weight_decay: float = 0.1, momentum: float = 0.95, nesterov: bool = True,
                 pasi_ns: int = 5) -> None:
        implicite = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay, momentum=momentum, nesterov=nesterov,
                         pasi_ns=pasi_ns, muon=False, bucati=1, multiplicator_lr=1.0)
        super().__init__(grupuri, implicite)

    @torch.no_grad()
    def step(self, closure: Any = None) -> Any:
        pierdere = None
        if closure is not None:
            with torch.enable_grad():
                pierdere = closure()
        for grup in self.param_groups:
            rata = grup["lr"] * grup["multiplicator_lr"]
            for p in grup["params"]:
                if p.grad is None:
                    continue
                if grup["muon"]:
                    self._pas_muon(p, grup, rata)
                else:
                    self._pas_adamw(p, grup, rata)
        return pierdere

    def _pas_muon(self, p: torch.Tensor, grup: dict[str, Any], rata: float) -> None:
        stare = self.state[p]
        if "momentum" not in stare:
            stare["momentum"] = torch.zeros_like(p)
        buf = stare["momentum"]
        buf.mul_(grup["momentum"]).add_(p.grad)
        g = p.grad.add(buf, alpha=grup["momentum"]) if grup["nesterov"] else buf
        update = torch.cat([newton_schulz(b, grup["pasi_ns"]) for b in g.chunk(grup["bucati"], dim=0)], dim=0)
        rand, col = update.size(0) // grup["bucati"], update.size(1)
        if grup["weight_decay"]:
            p.mul_(1 - rata * grup["weight_decay"])
        p.add_(update, alpha=-rata * max(1.0, rand / col) ** 0.5)

    def _pas_adamw(self, p: torch.Tensor, grup: dict[str, Any], rata: float) -> None:
        stare = self.state[p]
        if not stare:
            stare["step"] = 0  # număr simplu: fără o sincronizare cu placa la fiecare parametru
            stare["exp_avg"] = torch.zeros_like(p)
            stare["exp_avg_sq"] = torch.zeros_like(p)
        b1, b2 = grup["betas"]
        stare["step"] += 1
        pas = stare["step"]
        p.mul_(1 - rata * grup["weight_decay"])
        stare["exp_avg"].lerp_(p.grad, 1 - b1)
        stare["exp_avg_sq"].mul_(b2).addcmul_(p.grad, p.grad, value=1 - b2)
        numitor = (stare["exp_avg_sq"].sqrt() / math.sqrt(1 - b2**pas)).add_(grup["eps"])
        p.addcdiv_(stare["exp_avg"], numitor, value=-rata / (1 - b1**pas))


def grupuri_muon(retea: torch.nn.Module, rata_invatare: float, rata_muon: float,
                 scadere_muon: float = 0.0) -> list[dict[str, Any]]:
    """Grupurile pentru MuonCuAdamW: matricile din straturi (Muon; q/k/v combinate în 3 bucăți) și restul (AdamW)."""
    simple, qkv, restul = [], [], []
    for nume, p in retea.named_parameters():
        if nume.startswith("straturi.") and p.ndim == 2:
            (qkv if nume.endswith("in_proj_weight") else simple).append(p)
        else:
            restul.append(p)
    multiplicator = rata_muon / rata_invatare
    grupuri = [{"params": restul}]
    for params, bucati in ((simple, 1), (qkv, 3)):
        if params:
            grupuri.append({"params": params, "muon": True, "bucati": bucati, "multiplicator_lr": multiplicator,
                            "weight_decay": scadere_muon})
    return grupuri


class ModelGPTConversatieMuon(ModelGPTConversatie):
    MANIFEST = {
        "nume": "model_gpt_conversatie_muon",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 5500},
        "permisiuni": ["citire_fisier", "scriere_fisier"],
    }

    def __init__(self, optimizator: str = "adamw", rata_muon: float = 0.02, scadere_muon: float = 0.0,
                 adunare_loturi: int = 1, racire_finala: float = 0.0, fractie_dupa_racire: float = 0.0,
                 **setari: Any) -> None:
        super().__init__(**setari)
        if optimizator not in OPTIMIZATOARE:
            raise ValueError(f"optimizator: unul din {', '.join(OPTIMIZATOARE)}")
        if rata_muon <= 0 or scadere_muon < 0 or adunare_loturi < 1:
            raise ValueError("rata_muon pozitivă, scadere_muon nu negativă, adunare_loturi cel puțin 1")
        if not 0 <= racire_finala < 1 or not 0 <= fractie_dupa_racire <= 1:
            raise ValueError("racire_finala între 0 și 1 (fără 1), fractie_dupa_racire între 0 și 1")
        if racire_finala and not (self.rata_care_scade and self.durata_scaderii_secunde > 0):
            raise ValueError("racire_finala cere rata_care_scade = true și durata_scaderii_secunde (toată antrenarea)")
        self.optimizator_ales = optimizator
        self.rata_muon = rata_muon
        self.scadere_muon = scadere_muon
        self.adunare_loturi = adunare_loturi
        self.racire_finala = racire_finala
        self.fractie_dupa_racire = fractie_dupa_racire
        self._loturi_adunate = 0
        self.pasi_optimizator = 0

    def _optimizator_nou(self) -> torch.optim.Optimizer:
        assert self.retea is not None
        if self.optimizator_ales == "adamw":  # exact ca în model_gpt
            return torch.optim.AdamW(self.retea.parameters(), lr=self.rata_invatare, weight_decay=0.1)
        return MuonCuAdamW(grupuri_muon(self.retea, self.rata_invatare, self.rata_muon, self.scadere_muon),
                           lr=self.rata_invatare, weight_decay=0.1)

    def _pregateste_reteaua(self) -> None:
        """Ca în model_continuu, cu optimizatorul ales. Starea optimizatorului se încarcă doar dacă are ceva în ea: starea
        de pornire a lui antrenare_lunga.py --porneste-din are un AdamW gol (pornește din nou oricum)."""
        ia_placa(self)
        stare = self._stare_salvata()
        self._construieste()
        self.optimizator = self._optimizator_nou()
        self.continuat = stare is not None
        if stare is not None:
            self.retea.load_state_dict(stare["retea"])
            if stare["optimizator"].get("state"):
                self.optimizator.load_state_dict(stare["optimizator"])
            for grup in self.optimizator.param_groups:  # rata de învățare a rețetei de acum, nu a celei salvate
                grup["lr"] = self.rata_invatare
            self.pasi_total = stare["pasi_total"]
            self.minute_total = stare.get("minute", 0.0)
            self.scor_la_pornire = stare.get("scor")
        self._loturi_adunate = 0
        self.pasi_optimizator = 0

    def rata_acum(self, pasi: int, progres: float) -> float:
        rata = super().rata_acum(pasi, progres)
        inceput = 1 - self.racire_finala
        if self.racire_finala and progres > inceput:
            parcurs = min(1.0, (progres - inceput) / self.racire_finala)
            rata *= 1 - (1 - self.fractie_dupa_racire) * parcurs
        return rata

    def _pas_adunat(self, loss: torch.Tensor) -> float:
        """Înapoi prin rețea cu pierderea ÷ adunare_loturi; pasul optimizatorului la fiecare adunare_loturi loturi."""
        assert self.retea is not None and self.optimizator is not None
        if self.adunare_loturi == 1:  # exact ca în model_gpt / model_conversatie
            self.optimizator.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.retea.parameters(), 1.0)
            self.optimizator.step()
            self.pasi_optimizator += 1
            return loss.item()
        if self._loturi_adunate == 0:
            self.optimizator.zero_grad(set_to_none=True)
        (loss / self.adunare_loturi).backward()
        self._loturi_adunate += 1
        if self._loturi_adunate == self.adunare_loturi:
            torch.nn.utils.clip_grad_norm_(self.retea.parameters(), 1.0)
            self.optimizator.step()
            self.pasi_optimizator += 1
            self._loturi_adunate = 0
        return loss.item()

    def _pas_mascat(self, x: torch.Tensor, y: torch.Tensor) -> float:
        assert self.retea is not None
        with self._autocast():
            logits = self.retea(x, None)
            loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1), ignore_index=IGNORAT)
        return self._pas_adunat(loss)

    def _pas(self, x: torch.Tensor, y: torch.Tensor, m: torch.Tensor | None) -> float:
        assert self.retea is not None
        with self._autocast():
            logits = self.retea(x, m)
            loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1))
        return self._pas_adunat(loss)

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        statistici = super().antreneaza(date, buget_secunde)
        statistici.update(optimizator=self.optimizator_ales, adunare_loturi=self.adunare_loturi,
                          pasi_optimizator=self.pasi_optimizator, loturi_aruncate=self._loturi_adunate)
        if self.optimizator_ales == "muon":
            statistici["rata_muon"] = self.rata_muon
        if self.racire_finala:
            statistici["racire_finala"] = self.racire_finala
        return statistici
