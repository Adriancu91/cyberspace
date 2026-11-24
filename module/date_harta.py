"""S137 (laboratorul, a treia probă): „harta greutății textului” — datele pe bucăți ale lui `module/date_bucati.py`, plus
o hartă în RAM care alege din ce parte a textului vin ferestrele de antrenare.

Ideea (RHO-LOSS, Mindermann et al., 2022, arXiv 2206.07137): nu tragem mai des textul „greu” simplu (gunoiul e greu
mereu), ci textul care **mai are ceva de învățat**:

- șirul de simboluri e împărțit în **regiuni** fixe de `marime_regiune` simboluri (ultima poate fi mai scurtă); o fereastră
  aparține regiunii în care începe;
- `ref[r]` = pierderea medie a unui model care a învățat deja textul (#513) pe regiunea r (harta de referință, calculată o
  singură dată de `unelte/laborator_harta.py harta-ref`);
- `p_acum[r]` = media mobilă (EMA, α = `alfa`) a pierderii modelului care învață, pe ferestrele din r — actualizată la
  fiecare pas din pierderile pe fereastră ale lotului (fără nicio trecere înainte în plus);
- scorul `s[r] = max(p_acum[r] − ref[r], 0)`; regiunile încă nevăzute primesc media scorurilor celor văzute;
- probabilitatea unei regiuni = `parte_uniforma` × partea ei uniformă (după simboluri, ca rețeta (0)) + restul după scor,
  apoi tăiată între `taiere_jos`× și `taiere_sus`× din partea uniformă (și normalizată din nou); fereastra în regiune, la
  întâmplare.

În modul „uniform” (primele minute ale probei, sau harta oprită) ferestrele se trag **exact** ca în bucla rețetei (0) din
`module/model_trepte.py`: `torch.randint(len − context − 1, (lot,), generator)`, aceeași sămânță → aceleași ferestre.

Totul e pe procesor și în RAM (câțiva KB pentru ~1.280 de regiuni). Modulul nu schimbă `module/date_bucati.py`; îl
moștenește (aceeași verificare de la pornire, aceeași amprentă, același contract „date”).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from module.date_bucati import DateBucati

MARIME_REGIUNE = 1_048_576


def parti_uniforme(valide: np.ndarray) -> np.ndarray:
    """Partea fiecărei regiuni la tragerea uniformă pe simboluri: locurile de start valide din ea ÷ toate."""
    valide = np.asarray(valide, dtype=np.float64)
    return valide / valide.sum()


def scoruri(p_acum: np.ndarray, ref: np.ndarray, vazut: np.ndarray) -> np.ndarray:
    """s[r] = max(p_acum[r] − ref[r], 0) pentru regiunile văzute; cele nevăzute primesc media scorurilor văzute
    (0 dacă nu s-a văzut nimic)."""
    p_acum, ref, vazut = np.asarray(p_acum, np.float64), np.asarray(ref, np.float64), np.asarray(vazut, bool)
    s = np.maximum(p_acum - ref, 0.0)
    medie = float(s[vazut].mean()) if vazut.any() else 0.0
    return np.where(vazut, s, medie)


def probabilitati_regiuni(u: np.ndarray, s: np.ndarray, parte_uniforma: float = 0.5, taiere_jos: float = 0.25,
                          taiere_sus: float = 4.0, repetari: int = 100) -> np.ndarray:
    """q = parte_uniforma · u + (1 − parte_uniforma) · s / Σs (dacă Σs = 0: q = u), apoi fiecare q[r] ținut între
    taiere_jos · u[r] și taiere_sus · u[r]. Tăierea și normalizarea se repetă până se potrivesc amândouă: regiunile
    tăiate rămân la margine, restul masei se împarte pe celelalte, proporțional cu q."""
    u = np.asarray(u, dtype=np.float64)
    s = np.asarray(s, dtype=np.float64)
    total = s.sum()
    q = u.copy() if total <= 0 else parte_uniforma * u + (1.0 - parte_uniforma) * s / total
    jos, sus = taiere_jos * u, taiere_sus * u
    for _ in range(repetari):
        q = np.clip(q, jos, sus)
        fixe = (q <= jos) | (q >= sus)
        libere = ~fixe
        rest = 1.0 - q[fixe].sum()
        if not libere.any() or q[libere].sum() <= 0:
            break
        q_nou = q.copy()
        q_nou[libere] = q[libere] * rest / q[libere].sum()
        if np.allclose(q_nou, np.clip(q_nou, jos, sus), rtol=0, atol=1e-15):
            q = q_nou
            break
        q = q_nou
    return q / q.sum()


class HartaFerestre:
    """Harta pentru o antrenare: regiunile, `ref`, `p_acum` (EMA), tragerea ferestrelor și numărătorile pe regiuni."""

    def __init__(self, lungime_sir: int, context: int, marime_regiune: int = MARIME_REGIUNE,
                 ref: np.ndarray | None = None, alfa: float = 0.05, parte_uniforma: float = 0.5,
                 taiere_jos: float = 0.25, taiere_sus: float = 4.0) -> None:
        if marime_regiune < 1 or context < 1:
            raise ValueError("marime_regiune și context cel puțin 1")
        if not 0 < alfa <= 1:
            raise ValueError("alfa între 0 (exclus) și 1")
        self.context = context
        self.marime_regiune = marime_regiune
        # locurile de start ca în bucla (0): torch.randint(lungime − context − 1) → 0 … lungime − context − 2
        self.starturi = lungime_sir - context - 1
        if self.starturi < 1:
            raise ValueError("șirul e mai scurt decât contextul")
        self.regiuni = -(-lungime_sir // marime_regiune)
        inceputuri = np.arange(self.regiuni, dtype=np.int64) * marime_regiune
        self.inceputuri = inceputuri
        self.valide = np.clip(np.minimum(inceputuri + marime_regiune, self.starturi) - inceputuri, 0, None)
        self.u = parti_uniforme(self.valide)
        if ref is not None:
            ref = np.asarray(ref, dtype=np.float64)
            if ref.shape != (self.regiuni,):
                raise ValueError(f"harta de referință are {ref.shape}, trebuia ({self.regiuni},)")
        self.ref = ref
        self.alfa = alfa
        self.parte_uniforma = parte_uniforma
        self.taiere_jos = taiere_jos
        self.taiere_sus = taiere_sus
        self.p_acum = np.zeros(self.regiuni, dtype=np.float64)
        self.vazut = np.zeros(self.regiuni, dtype=bool)
        self.trase = np.zeros(self.regiuni, dtype=np.int64)
        self._q: np.ndarray | None = None

    def regiunea(self, pozitii: Any) -> np.ndarray:
        return np.asarray(pozitii, dtype=np.int64) // self.marime_regiune

    # --- tragerea ------------------------------------------------------------------------

    def probabilitati(self) -> np.ndarray:
        """Probabilitățile regiunilor din harta de acum (fără `ref`: uniform)."""
        if self.ref is None:
            return self.u.copy()
        return probabilitati_regiuni(self.u, scoruri(self.p_acum, self.ref, self.vazut), self.parte_uniforma,
                                     self.taiere_jos, self.taiere_sus)

    def recalculeaza(self) -> np.ndarray:
        """Recalculează probabilitățile (cel mult o dată pe pas de optimizator: o cheamă bucla)."""
        self._q = self.probabilitati()
        return self._q

    def trage(self, lot: int, generator: Any, uniform: bool) -> Any:
        """`lot` locuri de start (tensor int64). Uniform: exact ca bucla (0). Altfel: regiunea după probabilitățile
        recalculate ultima dată, apoi locul în regiune la întâmplare (din același generator)."""
        import torch

        if uniform:
            pozitii = torch.randint(self.starturi, (lot,), generator=generator)
        else:
            q = self._q if self._q is not None else self.recalculeaza()
            regiuni = torch.multinomial(torch.from_numpy(q), lot, replacement=True, generator=generator)
            r = regiuni.numpy()
            u = torch.rand(lot, generator=generator, dtype=torch.float64).numpy()
            loc = np.minimum((u * self.valide[r]).astype(np.int64), self.valide[r] - 1)
            pozitii = torch.from_numpy(self.inceputuri[r] + loc)
        np.add.at(self.trase, self.regiunea(pozitii.numpy()), 1)
        return pozitii

    # --- actualizarea ----------------------------------------------------------------------

    def actualizeaza(self, pozitii: Any, pierderi: Any) -> None:
        """EMA pe regiune, fereastră cu fereastră (în ordinea din lot): prima observație a unei regiuni o pune direct."""
        for r, p in zip(self.regiunea(np.asarray(pozitii)), np.asarray(pierderi, dtype=np.float64)):
            if not np.isfinite(p):
                continue
            if self.vazut[r]:
                self.p_acum[r] += self.alfa * (p - self.p_acum[r])
            else:
                self.p_acum[r] = p
                self.vazut[r] = True

    # --- ce s-a întâmplat ------------------------------------------------------------------

    def sferturi(self) -> np.ndarray:
        """Sfertul (0 = cel mai ușor după `ref`, 3 = cel mai greu) fiecărei regiuni; fără `ref`: toate 0."""
        if self.ref is None:
            return np.zeros(self.regiuni, dtype=np.int64)
        ordine = np.argsort(self.ref, kind="stable")
        sfert = np.empty(self.regiuni, dtype=np.int64)
        sfert[ordine] = (np.arange(self.regiuni) * 4) // self.regiuni
        return sfert

    def trase_pe_sferturi(self) -> list[int]:
        return [int(x) for x in np.bincount(self.sferturi(), weights=self.trase, minlength=4).astype(np.int64)]

    def stare(self) -> dict[str, Any]:
        s = scoruri(self.p_acum, self.ref, self.vazut) if self.ref is not None else np.zeros(self.regiuni)
        return {"regiuni": self.regiuni, "marime_regiune": self.marime_regiune, "vazute": int(self.vazut.sum()),
                "p_acum": [round(float(x), 5) for x in self.p_acum], "scor": [round(float(x), 5) for x in s],
                "trase": [int(x) for x in self.trase], "trase_pe_sferturi": self.trase_pe_sferturi(),
                "probabilitati": [float(x) for x in (self._q if self._q is not None else self.u)]}


class DateHarta(DateBucati):
    MANIFEST = {
        "nume": "date_harta",
        "port": "date",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {},
        "permisiuni": ["citire_fisier"],
    }

    def __init__(self, director: str, cale_validare: str, cale_tokenizer: str = "", previzualizare: bool = False,
                 simboluri_previzualizare: int = 20_000, marime_regiune: int = MARIME_REGIUNE, alfa: float = 0.05,
                 parte_uniforma: float = 0.5, taiere_jos: float = 0.25, taiere_sus: float = 4.0) -> None:
        super().__init__(director, cale_validare, cale_tokenizer, previzualizare, simboluri_previzualizare)
        if marime_regiune < 1:
            raise ValueError("marime_regiune cel puțin 1")
        if not 0 <= parte_uniforma <= 1 or not 0 < taiere_jos <= 1 <= taiere_sus:
            raise ValueError("parte_uniforma între 0 și 1; taiere_jos ≤ 1 ≤ taiere_sus")
        self.marime_regiune = marime_regiune
        self.alfa = alfa
        self.parte_uniforma = parte_uniforma
        self.taiere_jos = taiere_jos
        self.taiere_sus = taiere_sus

    def numar_regiuni(self) -> int:
        return -(-self.numar_simboluri() // self.marime_regiune)

    def harta(self, context: int, ref: np.ndarray | None = None) -> HartaFerestre:
        """O hartă nouă pentru o antrenare cu acest context (fără `ref`: tragerea rămâne uniformă)."""
        return HartaFerestre(self.numar_simboluri(), context, self.marime_regiune, ref, self.alfa, self.parte_uniforma,
                             self.taiere_jos, self.taiere_sus)

    def descriere(self) -> dict[str, Any]:
        return {**super().descriere(), "marime_regiune": self.marime_regiune, "regiuni": self.numar_regiuni(),
                "alfa": self.alfa, "parte_uniforma": self.parte_uniforma,
                "taiere": [self.taiere_jos, self.taiere_sus]}
