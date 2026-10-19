"""Școala de conversație (15 octombrie 2026): GPT-ul care continuă, antrenat să răspundă la întrebări.

Ca model_continuu, plus perechile întrebare → răspuns din `conversatie` (un .jsonl cu „intrebare” și „raspuns”, scris de
unelte/genereaza_conversatie.py; la „răspuns din text”, din 19 octombrie, și „text”, scris de unelte/conversatie_text.py). Fiecare pereche se scrie „Întrebare: …⏎Răspuns: …”, urmată de <|endoftext|>.
Din fiecare lot:
- `fractie_conversatie` (ex. 0,75) ferestre sunt perechi lipite una după alta. **Pierderea se socotește doar pe
  răspunsuri** (și pe <|endoftext|> de după ele), nu pe întrebări: modelul învață să răspundă, nu să pună întrebări;
- `fractie_hrana` (ex. 0,05) din hrană (poveștile cu fapte), ca la orice antrenare lungă;
- restul (ex. 0,20) din textul de antrenare (amestecul lui W2), ca să nu uite.
Întrebarea se codifică exact cum o va vedea modelul la examen și în interfață („Întrebare: …⏎Răspuns:”), iar răspunsul
separat, după ea.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

from module.model_continuu import ModelGPTContinuu

SFARSIT = "\n<|endoftext|>\n"
IGNORAT = -100


def intrebarea(text: str, context: str = "") -> str:
    """Ce vede modelul în față: „Întrebare: …⏎Răspuns:” (la antrenare, la examen și în interfață). 19 octombrie 2026
    („răspuns din text”, Adrian): cu un paragraf în față, „Text: …⏎Întrebare: …⏎Răspuns:”."""
    inainte = f"Text: {context.strip()}\n" if context.strip() else ""
    return f"{inainte}Întrebare: {text.strip()}\nRăspuns:"


def raspunsul(text: str) -> str:
    return f" {text.strip()}{SFARSIT}"


class ModelGPTConversatie(ModelGPTContinuu):
    MANIFEST = {
        "nume": "model_gpt_conversatie",
        "port": "model",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 5500},
        "permisiuni": ["citire_fisier", "scriere_fisier"],
    }

    def __init__(self, conversatie: str = "", fractie_conversatie: float = 0.0, **setari: Any) -> None:
        super().__init__(**setari)
        if bool(conversatie) != (fractie_conversatie > 0) or fractie_conversatie + self.fractie_hrana >= 1:
            raise ValueError("conversatie și fractie_conversatie merg împreună, iar conversația și hrana trebuie să lase "
                             "loc și textului de antrenare")
        self.conversatie = conversatie
        self.fractie_conversatie = fractie_conversatie

    def perechi_codificate(self) -> list[tuple[list[int], list[int]]]:
        """(simbolurile întrebării, simbolurile răspunsului) pentru fiecare pereche din fișier."""
        assert self.tok is not None
        perechi = []
        for rand in Path(self.conversatie).read_text(encoding="utf-8").splitlines():
            if rand.strip():
                p = json.loads(rand)
                perechi.append((self.tok.codifica(intrebarea(p["intrebare"], p.get("text", ""))),
                                self.tok.codifica(raspunsul(p["raspuns"]))))
        if not perechi:
            raise ValueError(f"{self.conversatie} n-are nicio pereche")
        return perechi

    @staticmethod
    def fereastra_conversatie(perechi: list[tuple[list[int], list[int]]], ctx: int,
                              generator: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
        """O fereastră de ctx simboluri din perechi lipite (alese la întâmplare) și țintele ei: la simbolurile care
        urmează într-o întrebare, ținta e IGNORAT (nu intră în pierdere)."""
        simboluri: list[int] = []
        tinte: list[int] = []
        while len(simboluri) < ctx + 1:
            q, r = perechi[int(torch.randint(len(perechi), (1,), generator=generator))]
            simboluri += q + r
            tinte += [IGNORAT] * len(q) + r
        x = torch.tensor(simboluri[:ctx], dtype=torch.long)
        y = torch.tensor(tinte[1:ctx + 1], dtype=torch.long)
        return x, y

    def _pas_mascat(self, x: torch.Tensor, y: torch.Tensor) -> float:
        assert self.retea is not None and self.optimizator is not None
        with self._autocast():
            logits = self.retea(x, None)
            loss = F.cross_entropy(logits.float().view(-1, logits.size(-1)), y.view(-1), ignore_index=IGNORAT)
        self.optimizator.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.retea.parameters(), 1.0)
        self.optimizator.step()
        return loss.item()

    def antreneaza(self, date: Any, buget_secunde: float) -> dict[str, Any]:
        if not self.conversatie:
            return super().antreneaza(date, buget_secunde)
        from module.tokenizer_bpe import TokenizerBPE

        self.tok = TokenizerBPE.incarca(self.cale_tokenizer)
        date_t = torch.as_tensor(self._simboluri(date.text_antrenare()))
        hrana_t = torch.as_tensor(self._simboluri(Path(self.hrana).read_text(encoding="utf-8"))) if self.hrana else None
        perechi = self.perechi_codificate()
        self._pregateste_reteaua()
        assert self.retea is not None
        ctx = self.setari["context"]
        generator = torch.Generator(device="cpu").manual_seed(self._samanta_loturi())
        self.retea.train()
        start = time.perf_counter()
        pasi, pierdere, rata = 0, float("nan"), self.rata_invatare
        ferestre = {"conversatie": 0, "hrana": 0, "text": 0}
        while time.perf_counter() - start < buget_secunde and not (self.pasi_max and pasi >= self.pasi_max):
            pas = self._pasi_anteriori() + pasi
            k_conv = math.floor(self.fractie_conversatie * self.lot * (pas + 1) + 1e-9) - math.floor(
                self.fractie_conversatie * self.lot * pas + 1e-9)
            k_hrana = self.bucati_din_hrana(pas) if hrana_t is not None else 0
            k_text = self.lot - k_conv - k_hrana
            xs, ys = [], []
            for _ in range(k_conv):
                x, y = self.fereastra_conversatie(perechi, ctx, generator)
                xs.append(x)
                ys.append(y)
            for sursa, k in ((hrana_t, k_hrana), (date_t, k_text)):
                for p in torch.randint(len(sursa) - ctx - 1, (k,), generator=generator) if k else []:
                    xs.append(sursa[p:p + ctx].long())
                    ys.append(sursa[p + 1:p + ctx + 1].long())
            ferestre["conversatie"] += k_conv
            ferestre["hrana"] += k_hrana
            ferestre["text"] += k_text
            if self.rata_care_scade:
                acum = time.perf_counter()
                rata = self.rata_acum(pasi, self._progres(pasi, acum - start, acum - start, buget_secunde))
                for grup in self.optimizator.param_groups:
                    grup["lr"] = rata
            pierdere = self._pas_mascat(torch.stack(xs).to(self.dispozitiv), torch.stack(ys).to(self.dispozitiv))
            pasi += 1
            if not math.isfinite(pierdere):
                raise FloatingPointError("pierderea a devenit infinită (rata de învățare prea mare?)")
        secunde = time.perf_counter() - start
        self.pasi_total += pasi
        self.minute_total += secunde / 60
        statistici: dict[str, Any] = {
            "pasi": pasi, "pierdere_finala": pierdere, "parametri": sum(p.numel() for p in self.retea.parameters()),
            "dispozitiv": str(self.dispozitiv), "secunde_bucla": round(secunde, 2), "tokenizer": "bpe",
            "simboluri_antrenare": len(date_t), "perechi_conversatie": len(perechi), "ferestre": ferestre,
            "pasi_total": self.pasi_total, "minute_total": round(self.minute_total, 1), "continuat": self.continuat,
            "pornit_din": self.pornit_din, "rata_la_final": rata,
        }
        if self.dispozitiv.type == "cuda":
            statistici["memorie_rezervata_mb"] = round(torch.cuda.max_memory_reserved() / 2**20)
        return statistici
