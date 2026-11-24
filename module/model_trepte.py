"""S135 (C-163): „laboratorul treptelor” — antrenarea în trepte (Patch-Level Training, ICLR 2025, arxiv 2407.12665).

Aceeași rețea ca `module/model_gpt.py` (#513: straturile, LayerNorm, GELU, capul legat de încorporări), cu o singură
noutate, la antrenare:

- **faza pe bucăți** (primele `minute_bucati` minute, dacă `k_bucata` > 1): fiecare fereastră de `context` simboluri
  se taie în `context / k_bucata` bucăți de câte K simboluri; intrarea unei poziții = **media încorporărilor celor K
  simboluri** (+ încorporarea de poziție, ca la o secvență de `context / K` poziții); ieșirea fiecărei poziții e o
  singură distribuție peste vocabular, iar eroarea = **media erorilor (cross-entropy) față de cele K simboluri ale
  bucății următoare**. Același număr de simboluri pe lot ca pe simboluri → pașii merg de ~K ori mai repede;
- **faza pe simboluri** (restul timpului): exact pasul de azi, cu aceleași greutăți și același AdamW (nu se repornește).

Cu `k_bucata = 1` (implicit) sau `minute_bucati = 0` nu există fază pe bucăți: pasul e cel din `ModelGPT._pas`
(aceeași pierdere, același AdamW), plus, opțional:

- `adunare_loturi` (implicit 1): pasul optimizatorului la fiecare N loturi (gradientele adunate, pierderea ÷ N);
- `abatere_incorporari` (implicit niciuna): încorporările pornesc din N(0, abatere), ca la `model_gpt_cod` (S61);
- rata **după ceas**: `incalzire_secunde` (creștere liniară de la 0) și `racire_secunde` (scădere liniară la 0 în
  ultimele secunde ale bugetului); amândouă 0 = rata fixă, ca la ModelGPT.

Răspunsurile (biti_pentru, genereaza, completeaza) și salvarea sunt cele din ModelGPT: modelul de la sfârșit e un
Kronos obișnuit. Modulul nu schimbă niciun modul existent.
"""

from __future__ import annotations

import math
import time
from typing import Any, Callable

import torch
import torch.nn.functional as F

from module.model_gpt import NECUNOSCUT, ModelGPT, _GPT
from module.tokenizer_bpe import TokenizerBPE


class _GPTTrepte(_GPT):
    """Rețeaua GPT, cu o trecere în plus pe bucăți (fără parametri noi: aceeași inițializare, aceleași greutăți)."""

    def inainte_bucati(self, blocuri: torch.Tensor) -> torch.Tensor:
        """blocuri [lot, n, K] (simboluri) → logits [lot, n, vocabular]; poziția i = media încorporărilor bucății i."""
        n = blocuri.size(1)
        if n > self.context:
            raise ValueError(f"{n} bucăți > contextul {self.context}")
        x = self.emb_token(blocuri).mean(dim=2) + self.emb_pozitie(torch.arange(n, device=blocuri.device))
        for strat in self.straturi:
            x = strat(x)
        return self.cap(self.ln(x))


def pierdere_bucati(logits: torch.Tensor, tinte: torch.Tensor) -> torch.Tensor:
    """logits [lot, n, V], tinte [lot, n, K] → media, pe poziții și pe cele K ținte, a lui −log p(țintă)."""
    if logits.dtype != torch.float64:  # bf16 sub autocast → F32 (ca la pasul de azi); F64 rămâne (testul de gradient)
        logits = logits.float()
    logp = F.log_softmax(logits, dim=-1)
    return -logp.gather(-1, tinte).mean()


class ModelTrepte(ModelGPT):
    MANIFEST = {
        "nume": "model_trepte",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 6500},
        "permisiuni": [],
    }

    def __init__(self, k_bucata: int = 1, minute_bucati: float = 0.0, adunare_loturi: int = 1,
                 abatere_incorporari: float | None = None, incalzire_secunde: float = 0.0,
                 racire_secunde: float = 0.0, **setari: Any) -> None:
        super().__init__(**setari)
        if k_bucata < 1 or minute_bucati < 0 or adunare_loturi < 1:
            raise ValueError("k_bucata și adunare_loturi cel puțin 1; minute_bucati nu poate fi negativ")
        if k_bucata > 1 and self.setari["context"] % k_bucata != 0:
            raise ValueError("contextul trebuie să se împartă exact la k_bucata")
        if abatere_incorporari is not None and abatere_incorporari <= 0:
            raise ValueError("abatere_incorporari pozitivă (sau lipsă: inițializarea implicită)")
        if incalzire_secunde < 0 or racire_secunde < 0:
            raise ValueError("incalzire_secunde și racire_secunde nu pot fi negative")
        if self.foloseste_memorie or self.hrana or self.rata_care_scade:
            raise ValueError("model_trepte: fără memorie ierarhică, fără hrană și fără rata_care_scade pe pași "
                             "(rata e după ceas: incalzire_secunde / racire_secunde)")
        self.k_bucata = k_bucata
        self.minute_bucati = float(minute_bucati)
        self.adunare_loturi = adunare_loturi
        self.abatere_incorporari = abatere_incorporari
        self.incalzire_secunde = float(incalzire_secunde)
        self.racire_secunde = float(racire_secunde)

    # --- rețeaua -------------------------------------------------------------------------------

    def _construieste(self) -> None:
        torch.manual_seed(self.samanta)
        self.retea = _GPTTrepte(self._marime_vocabular(), **self.setari).to(self.dispozitiv)
        if self.abatere_incorporari is not None:
            with torch.no_grad():
                self.retea.emb_token.weight.normal_(0.0, self.abatere_incorporari)
                self.retea.emb_pozitie.weight.normal_(0.0, self.abatere_incorporari)

    def _pregateste_reteaua(self) -> None:
        """De la zero: rețeaua și AdamW (beta 0,9/0,999, eps 1e-8, scăderea greutăților 0,1 — ca ModelGPT)."""
        self._construieste()
        assert self.retea is not None
        self.optimizator = torch.optim.AdamW(self.retea.parameters(), lr=self.rata_invatare, betas=(0.9, 0.999),
                                             eps=1e-8, weight_decay=0.1)

    # --- pierderile ----------------------------------------------------------------------------

    def pierdere_simboluri(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Pierderea de azi (ModelGPT._pas): cross-entropy pe toate pozițiile."""
        assert self.retea is not None
        with self._autocast():
            logits = self.retea(x)
            return F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.reshape(-1))

    def pierdere_pe_bucati(self, fereastra: torch.Tensor, k: int) -> torch.Tensor:
        """fereastra [lot, context + K] simboluri → (context / K) bucăți de intrare, fiecare cu ținta = bucata următoare."""
        assert self.retea is not None
        lot, lungime = fereastra.shape
        n = lungime // k - 1
        blocuri = fereastra[:, : (n + 1) * k].reshape(lot, n + 1, k)
        with self._autocast():
            logits = self.retea.inainte_bucati(blocuri[:, :n])
            return pierdere_bucati(logits, blocuri[:, 1:])

    def pas_optimizator(self, loturi: list[torch.Tensor], faza: str, rata: float | None = None) -> dict[str, float]:
        """Un pas al optimizatorului pe `adunare_loturi` loturi (pierderea ÷ N, gradientele adunate), tăierea 1,0.
        faza „simboluri”: fiecare lot e [lot, context + 1]; faza „bucati”: [lot, context + K]."""
        assert self.retea is not None and self.optimizator is not None
        if rata is not None:
            for grup in self.optimizator.param_groups:
                grup["lr"] = rata
        self.optimizator.zero_grad(set_to_none=True)
        total = 0.0
        ctx = self.setari["context"]
        for fereastra in loturi:
            if faza == "simboluri":
                loss = self.pierdere_simboluri(fereastra[:, :ctx], fereastra[:, 1 : ctx + 1])
            elif faza == "bucati":
                loss = self.pierdere_pe_bucati(fereastra, self.k_bucata)
            else:
                raise ValueError(f"fază necunoscută: {faza}")
            (loss / len(loturi)).backward()
            total += loss.item()
        norma = torch.nn.utils.clip_grad_norm_(self.retea.parameters(), 1.0)
        self.optimizator.step()
        return {"pierdere": total / len(loturi), "norma_gradient": float(norma)}

    # --- rata și fazele, după ceas ------------------------------------------------------------

    def rata_dupa_ceas(self, secunde: float, buget_secunde: float) -> float:
        """Încălzire liniară în primele `incalzire_secunde`, constantă, apoi răcire liniară la 0 în ultimele
        `racire_secunde` ale bugetului."""
        f = 1.0
        if self.incalzire_secunde > 0:
            f = min(f, secunde / self.incalzire_secunde)
        if self.racire_secunde > 0:
            f = min(f, (buget_secunde - secunde) / self.racire_secunde)
        return self.rata_invatare * max(0.0, f)

    def secunde_bucati(self, buget_secunde: float) -> float:
        return min(self.minute_bucati * 60.0, buget_secunde) if self.k_bucata > 1 else 0.0

    # --- antrenarea ----------------------------------------------------------------------------

    def _sirul(self, date: Any) -> Any:
        """Simbolurile de antrenare: din datele pe bucăți (sir_antrenare), altfel textul codificat."""
        sir, _ = self._sir_din_date(date)
        if sir is not None:
            return sir
        return torch.as_tensor(self._simboluri(date.text_antrenare()), dtype=torch.long)

    def bucla(self, sir: Any, buget_secunde: float, samanta_loturi: int | None = None,
              la_fiecare: Callable[[dict[str, Any]], str | None] | None = None,
              secunde_intre_semnale: float = 60.0) -> dict[str, Any]:
        """Bucla după ceas: faza pe bucăți, apoi pe simboluri, până la buget (sau pasi_max pași de optimizator).
        `la_fiecare(stare)` e chemat la fiecare `secunde_intre_semnale` (și la sfârșit); dacă întoarce un text, bucla
        se oprește cu acel motiv (paznicul)."""
        assert self.retea is not None and self.optimizator is not None
        ctx, k = self.setari["context"], self.k_bucata
        lungime = len(sir)
        if lungime <= ctx + k:
            raise ValueError("textul de antrenare e mai scurt decât contextul")
        generator = torch.Generator(device="cpu").manual_seed(self.samanta if samanta_loturi is None else samanta_loturi)
        prag_bucati = self.secunde_bucati(buget_secunde)
        self.retea.train()
        start = time.perf_counter()
        urmatorul_semnal = secunde_intre_semnale
        pe_faza = {f: {"pasi": 0, "simboluri": 0, "secunde": 0.0} for f in ("bucati", "simboluri")}
        pierderi_recente: list[float] = []
        ultim: dict[str, float] = {"pierdere": float("nan"), "norma_gradient": float("nan")}
        oprit = None
        rata = self.rata_invatare
        pasi = 0

        def stare(secunde: float, faza: str) -> dict[str, Any]:
            return {"secunde": secunde, "faza": faza, "pasi": pasi, "rata": rata,
                    "pasi_bucati": pe_faza["bucati"]["pasi"], "pasi_simboluri": pe_faza["simboluri"]["pasi"],
                    "simboluri_vazute": pe_faza["bucati"]["simboluri"] + pe_faza["simboluri"]["simboluri"],
                    "pierdere": (sum(pierderi_recente) / len(pierderi_recente)) if pierderi_recente else float("nan"),
                    "pierdere_ultim_pas": ultim["pierdere"], "norma_gradient": ultim["norma_gradient"]}

        faza = "bucati" if prag_bucati > 0 else "simboluri"
        while True:
            acum = time.perf_counter() - start
            if acum >= buget_secunde or (self.pasi_max and pasi >= self.pasi_max):
                break
            faza = "bucati" if acum < prag_bucati else "simboluri"
            lung = ctx + (k if faza == "bucati" else 1)
            loturi = []
            for _ in range(self.adunare_loturi):
                pozitii = torch.randint(lungime - ctx - k, (self.lot,), generator=generator)
                loturi.append(torch.stack([torch.as_tensor(sir[int(p) : int(p) + lung]) for p in pozitii])
                              .to(self.dispozitiv, torch.long))
            rata = self.rata_dupa_ceas(acum, buget_secunde)
            t0 = time.perf_counter()
            ultim = self.pas_optimizator(loturi, faza, rata)
            pasi += 1
            pe_faza[faza]["pasi"] += 1
            pe_faza[faza]["simboluri"] += self.adunare_loturi * self.lot * ctx
            pe_faza[faza]["secunde"] += time.perf_counter() - t0
            pierderi_recente.append(ultim["pierdere"])
            if not math.isfinite(ultim["pierdere"]):
                oprit = f"pierderea nu e un număr finit la pasul {pasi} (faza {faza})"
                if la_fiecare is not None:
                    la_fiecare(stare(time.perf_counter() - start, faza))
                break
            dupa = time.perf_counter() - start
            if la_fiecare is not None and dupa >= urmatorul_semnal:
                motiv = la_fiecare(stare(dupa, faza))
                pierderi_recente = []
                if secunde_intre_semnale > 0:
                    urmatorul_semnal += secunde_intre_semnale
                    while urmatorul_semnal <= dupa:
                        urmatorul_semnal += secunde_intre_semnale
                if motiv:
                    oprit = motiv
                    break
        secunde = time.perf_counter() - start
        if la_fiecare is not None and oprit is None and pierderi_recente:
            la_fiecare(stare(secunde, faza))
        return {"pasi": pasi, "secunde_bucla": round(secunde, 2), "pe_faza": pe_faza,
                "simboluri_vazute": pe_faza["bucati"]["simboluri"] + pe_faza["simboluri"]["simboluri"],
                "pierdere_finala": ultim["pierdere"], "rata_la_final": rata, "oprit": oprit}

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        if self.tokenizer == "bpe":
            self.tok = TokenizerBPE.incarca(self.cale_tokenizer)
            sir = self._sirul(date)
        else:
            text = date.text_antrenare()
            self.vocabular = sorted(set(text)) + [NECUNOSCUT]
            sir = self._codifica(text)
        self._pregateste_reteaua()
        assert self.retea is not None
        r = self.bucla(sir, buget_secunde)
        if r["oprit"]:
            raise FloatingPointError(r["oprit"])
        return {"pasi": r["pasi"], "pierdere_finala": r["pierdere_finala"],
                "parametri": sum(p.numel() for p in self.retea.parameters()), "dispozitiv": str(self.dispozitiv),
                "secunde_bucla": r["secunde_bucla"], "k_bucata": self.k_bucata, "minute_bucati": self.minute_bucati,
                "adunare_loturi": self.adunare_loturi, "pe_faza": r["pe_faza"],
                "simboluri_vazute": r["simboluri_vazute"], "rata_la_final": r["rata_la_final"]}
