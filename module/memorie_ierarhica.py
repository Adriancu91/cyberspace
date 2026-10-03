"""Memoria ierarhică: biblioteca de sensuri, cu coduri pe niveluri, relații și o plasă.

Cele trei straturi:
1. Biblioteca: fiecare SENS are un loc fix: parte de vorbire → raft (ex. noun.animal)
   → strămoșii lui din WordNet (organism → animal → ... → horse). Locul se scrie ca un
   cod pe niveluri, de ex. 1.7.1.2.3.38...
2. Relațiile: legături între sensuri: parte din, are parte, membru din, are membru, opus.
3. Plasa: ține minte drumurile deja căutate și de câte ori a fost folosit fiecare,
   ca a doua căutare a aceluiași cuvânt să meargă direct la țintă.

Ce primește modelul: pentru fiecare literă din text, codul ULTIMULUI CUVÂNT TERMINAT
până la ea. Niciodată cuvântul în curs de scriere: i-ar dezvălui literele care urmează,
adică ar trișa la examen. Testul test_memoria_nu_dezvaluie_viitorul verifică asta.

Biblioteca se construiește o singură dată: python unelte/construieste_biblioteca.py

Setarea fara_cuvinte_de_legatura (implicit oprită): cuvintele de legătură (the, a, it, in, can...)
sunt tratate ca negăsite („umplutură”), chiar dacă WordNet le are cu alt sens (a = vitamina A,
it = tehnologia informației, can = cutie de conserve, may = luna mai).

Setarea sens_dupa_context (implicit oprită) alege sensul după cum e folosit cuvântul în text:
a) formele de verb: o formă listată în bibliotecă (said → say, saw → see, went → go) sau un cuvânt
   terminat în -ed / -ing a cărui bază e verb (looked → look, smiling → smile) primește sensul de verb;
b) numele: un cuvânt cu literă mare care NU e la început de propoziție primește codul lui „person”,
   pus pe raftul noun.person (în WordNet, „person” stă pe raftul general noun.Tops); cuvintele care
   stau deja pe noun.person (Mom) își păstrează codul. Început de propoziție = primul cuvânt din text,
   un semn . ! ? sau un rând nou după cuvântul de dinainte, ori ghilimele lipite de cuvânt (said, "Look).
   Se uită doar în urmă: nimic din ce urmează după cuvânt nu schimbă codul lui;
c) cuvintele din lista scurtă și fixă ADVERBE_PREFERATE (very, then, now...) primesc sensul de adverb.
Sunt reguli simple, nu „înțeleg” propoziția, deci mai greșesc: „ground” (pământul) e și trecutul lui
„grind” (a măcina), „evening” pare forma -ing a lui „even”, iar un nume la început de propoziție rămâne
cu sensul din dicționar (Lily = crin).
"""

from __future__ import annotations

import gzip
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

GOL = 0  # nivel gol: încă niciun cuvânt terminat, sau codul cuvântului s-a terminat
NECUNOSCUT = 5  # pe primul nivel (partea de vorbire are 1-4): cuvânt care nu e în bibliotecă
SUBSTANTIV, VERB, ADVERB = 1, 2, 4  # pe primul nivel, ca PARTI_DE_VORBIRE din construieste_biblioteca
VERSIUNE_BIBLIOTECA = 1

# Ca „morphy” din WordNet: terminație → înlocuire, pentru formele regulate pe care biblioteca
# nu le are (horses → horse, galloping → gallop), plus terminații vechi din Shakespeare.
TERMINATII = (
    ("'s", ""),
    ("ies", "y"), ("ses", "s"), ("xes", "x"), ("zes", "z"), ("ches", "ch"), ("shes", "sh"),
    ("men", "man"), ("es", "e"), ("es", ""), ("s", ""),
    ("ied", "y"), ("ed", "e"), ("ed", ""), ("ing", "e"), ("ing", ""),
    ("er", ""), ("er", "e"), ("est", ""), ("est", "e"),
    ("eth", ""), ("eth", "e"), ("'st", ""), ("st", ""), ("'d", "e"), ("'d", ""),
)


# Cuvintele de legătură ale englezei (clase închise): articole și determinanți, pronume, prepoziții,
# conjuncții, verbe auxiliare și modale, negația, „there” existențial. Nu cuprinde adverbele cu sens
# (very, then, now) și nici cuvintele cu două roluri dese (like = a plăcea, one = unu).
CUVINTE_DE_LEGATURA = frozenset("""
a an the this that these those some any each every no all both either neither another such
i me my mine myself you your yours yourself yourselves he him his himself she her hers herself
it its itself we us our ours ourselves they them their theirs themselves
who whom whose which what whatever whoever how why where
someone somebody something anyone anybody anything everyone everybody everything nobody nothing
about above across after against along among around at before behind below beneath beside besides
between beyond by down during except for from in inside into near of off on onto out outside over
past since through throughout till to toward towards under underneath until up upon with within without
and or but nor so yet because if when while although though than as unless whether
be am is are was were been being have has had having do does did doing
will would shall should can could may might must not there
""".split())


# Regula c) a setării sens_dupa_context: cuvinte pe care poveștile le folosesc mai ales ca adverbe, dar pe care
# WordNet le pune întâi pe alt raft (very = adjectivul „exact”, then = substantivul „acel moment”, back = spatele,
# still = alambicul, well = fântâna, fast = postul). Nu intră „little” (în povești e mai ales adjectiv: „a little
# girl”) și nici too, again, soon, once (sunt deja adverbe).
ADVERBE_PREFERATE = frozenset("""
very then now back still just only here well much even away later together far fast
""".split())
SFARSIT_DE_PROPOZITIE = frozenset(".!?\n")  # regula b): după ele începe o propoziție nouă
GHILIMELE = ('"', "“")  # ... și după ghilimele lipite de cuvânt (said, "Look!)


def _e_litera(c: str) -> bool:
    return c.isascii() and c.isalpha()


def _consoana_dubla(baza: str) -> bool:
    """„runn” (din running) → run, „stopp” (din stopped) → stop."""
    return len(baza) >= 3 and baza[-1] == baza[-2] and baza[-1] not in "aeiou"


def _are_vocala(text: str) -> bool:
    return any(c in "aeiouy" for c in text)


def _vocala_consoana(baza: str) -> bool:
    """Se termină într-o singură vocală + o consoană (hop, rid, shin, us): „hoping” vine din „hope”,
    fiindcă „hop” ar fi dat „hopping”. Altfel (sing, look, eat) baza e chiar ea: „singing” → „sing”."""
    return (
        len(baza) >= 2 and baza[-1] not in "aeiouwxy" and baza[-2] in "aeiou"
        and (len(baza) == 2 or baza[-3] not in "aeiou")
    )


class MemorieIerarhica:
    MANIFEST = {
        "nume": "memorie_ierarhica",
        "port": "memorie",
        "versiune": "0.3.0",
        "versiune_contract": 1,
        "resurse": {"ram_mb": 300},
        "permisiuni": ["citire_fisier"],
    }

    def __init__(
        self,
        cale: str = "date/biblioteca.json.gz",
        nivele: int = 12,
        fara_cuvinte_de_legatura: bool = False,
        sens_dupa_context: bool = False,
    ) -> None:
        if not 1 <= nivele <= 64:
            raise ValueError("nivele trebuie să fie între 1 și 64")
        self.fara_cuvinte_de_legatura = bool(fara_cuvinte_de_legatura)
        self.sens_dupa_context = bool(sens_dupa_context)
        fisier = Path(cale)
        if not fisier.exists():
            raise ValueError(
                f"Nu găsesc biblioteca „{cale}”. Construiește-o întâi: python unelte/construieste_biblioteca.py"
            )
        with gzip.open(fisier, "rt", encoding="utf-8") as f:
            biblioteca = json.load(f)
        if biblioteca.get("versiune") != VERSIUNE_BIBLIOTECA:
            raise ValueError(
                f"Biblioteca „{cale}” are versiunea {biblioteca.get('versiune')}, aștept {VERSIUNE_BIBLIOTECA}. "
                "Reconstruiește-o: python unelte/construieste_biblioteca.py"
            )
        self.nivele = nivele
        self.sursa: str = biblioteca["sursa"]
        self._parti: list[str] = biblioteca["parti_de_vorbire"]
        self._rafturi: list[str] = biblioteca["rafturi"]
        self.rafturi = self._rafturi  # public: raftul k din cod = rafturi[k - 1] (ex. plasa grupează nodurile pe rafturi)
        self._nume: list[str] = biblioteca["nume"]
        self._parinte: list[int] = biblioteca["parinte"]
        self._cod: list[list[int]] = biblioteca["cod"]
        self._forme: dict[str, list[int]] = biblioteca["forme"]
        self._relatii: dict[str, list[list[Any]]] = biblioteca["relatii"]
        self._forme_verb: dict[str, list[int]] = biblioteca.get("forme_verb", {})
        self._cod_persoana: tuple[int, ...] = ()
        if self.sens_dupa_context:
            if "forme_verb" not in biblioteca:
                raise ValueError(
                    f"Biblioteca „{cale}” e construită fără formele de verb, de care are nevoie sens_dupa_context. "
                    "Reconstruiește-o: python unelte/construieste_biblioteca.py"
                )
            persoana = [s for s in self._forme.get("person", []) if self._cod[s][0] == SUBSTANTIV]
            if not persoana or "noun.person" not in self._rafturi:
                raise ValueError(f"Biblioteca „{cale}” nu are „person” și raftul noun.person (regula numelor).")
            raft = self._rafturi.index("noun.person") + 1
            self._cod_persoana = self._completeaza([SUBSTANTIV, raft] + self._cod[persoana[0]][2:])
        # Plasa: cuvânt → codul deja găsit (drumul știut) și de câte ori a fost folosit.
        self._plasa: dict[str, tuple[int, ...]] = {}
        self._folosiri: Counter[str] = Counter()
        self._cautari = 0
        self._gasite = 0

    # --- căutarea în bibliotecă -----------------------------------------------

    def _sensuri(self, cuvant: str) -> list[int]:
        """Sensurile cuvântului (principalul primul); încearcă și forma de bază (horses → horse)."""
        cuvant = cuvant.lower().strip("'")
        if cuvant in self._forme:
            return self._forme[cuvant]
        for terminatie, inlocuire in TERMINATII:
            if cuvant.endswith(terminatie) and len(cuvant) - len(terminatie) >= 2:
                baza = cuvant[: -len(terminatie)]
                if baza + inlocuire in self._forme:
                    return self._forme[baza + inlocuire]
                if not inlocuire and _consoana_dubla(baza) and baza[:-1] in self._forme:
                    return self._forme[baza[:-1]]
        return []

    def _sensuri_alese(self, cuvant: str) -> list[int]:
        """Ca _sensuri, dar cu setarea sens_dupa_context sensul potrivit trece primul (regulile c și a)."""
        cheie = cuvant.lower().strip("'")
        sensuri = self._sensuri(cheie)
        if not self.sens_dupa_context:
            return sensuri
        if cheie in ADVERBE_PREFERATE:
            alese = [s for s in sensuri if self._cod[s][0] == ADVERB]
        else:
            alese = self._forme_verb.get(cheie) or self._verbe_din_baza(cheie)
        return alese + [s for s in sensuri if s not in alese]

    def _verbe_din_baza(self, cuvant: str) -> list[int]:
        """Regula a), formele regulate: sensurile de verb ale bazei (looked → look, smiling → smile,
        stopped → stop, cried → cry, lying → lie). Baza trebuie să aibă o vocală (sing, thing, red nu
        sunt forme de verb), iar la „-eed” vocala e înainte (agreed → agree; seed, need rămân cum sunt)."""
        if cuvant.endswith("ing"):
            radacina = cuvant[:-3]
        elif cuvant.endswith("ed") and (not cuvant.endswith("eed") or _are_vocala(cuvant[:-3])):
            radacina = cuvant[:-2]
        else:
            return []
        if not _are_vocala(radacina):
            return []
        baze = []
        if cuvant.endswith("ied"):
            baze.append(radacina[:-1] + "y")  # cried → cry
        if cuvant.endswith("ying"):
            baze.append(radacina[:-1] + "ie")  # lying → lie
        cu_e = radacina + "e"
        baze += [cu_e, radacina] if _vocala_consoana(radacina) else [radacina, cu_e]
        if _consoana_dubla(radacina):
            baze.append(radacina[:-1])  # stopped → stop, running → run
        for baza in baze:
            verbe = [s for s in self._forme.get(baza, []) if self._cod[s][0] == VERB]
            if verbe:
                return verbe
        return []

    def _completeaza(self, cod: list[int]) -> tuple[int, ...]:
        cod = cod[: self.nivele]
        return tuple(cod) + (GOL,) * (self.nivele - len(cod))

    def _drum(self, sens: int) -> list[str]:
        drum: list[str] = []
        vazute: set[int] = set()
        while sens != -1 and sens not in vazute:
            vazute.add(sens)
            drum.append(self._nume[sens])
            sens = self._parinte[sens]
        return drum[::-1]

    # --- contractul -------------------------------------------------------------

    def cod(self, cuvant: str, la_inceput: bool = True) -> tuple[int, ...]:
        """Codul sensului principal: exact `nivele` numere, completat cu 0 (GOL).

        la_inceput: cuvântul începe o propoziție (sau e luat singur). Contează doar pentru regula b)
        a setării sens_dupa_context: în mijlocul propoziției, un cuvânt cu literă mare e un nume.
        """
        cheie = cuvant.lower().strip("'")
        self._cautari += 1
        self._folosiri[cheie] += 1
        cod = self._plasa.get(cheie)
        if cod is None:  # drum nou: îl căutăm în bibliotecă și îl prindem în plasă
            if self.este_cuvant_de_legatura(cheie):
                sensuri = []  # umplutură: the, a, it's, can...
            else:
                sensuri = self._sensuri_alese(cheie)
            cod = self._completeaza(self._cod[sensuri[0]] if sensuri else [NECUNOSCUT])
            self._plasa[cheie] = cod
        if self._e_nume(cuvant, la_inceput) and cod[:2] != self._cod_persoana[:2]:
            cod = self._cod_persoana  # nu intră în plasă: depinde de locul din propoziție
        if cod[0] != NECUNOSCUT:
            self._gasite += 1
        return cod

    def _e_nume(self, cuvant: str, la_inceput: bool) -> bool:
        """Regula b): literă mare în mijlocul propoziției (cuvintele de legătură rămân umplutură)."""
        return (
            self.sens_dupa_context and not la_inceput and cuvant.lstrip("'")[:1].isupper()
            and not self.este_cuvant_de_legatura(cuvant)
        )

    def este_cuvant_de_legatura(self, cuvant: str) -> bool:
        """Doar cu setarea fara_cuvinte_de_legatura: the, a, it, it's, i'm... (partea dinaintea apostrofului)."""
        return self.fara_cuvinte_de_legatura and cuvant.lower().strip("'").split("'")[0] in CUVINTE_DE_LEGATURA

    @staticmethod
    def cuvinte_terminate(text: str) -> Iterator[tuple[int, str, bool]]:
        """Cuvintele terminate, în ordine: (poziția semnului care încheie cuvântul, cuvântul, la_inceput).

        Un cuvânt = litere englezești, cu apostrof în interior (know'st). Se termină la primul
        semn care nu-l poate continua. Despre un apostrof după litere nu știm încă dacă e în
        interior (know'st) sau la final (horses'), așa că decidem la semnul următor; fiecare
        decizie folosește doar ce s-a scris deja. Cuvântul în curs, la finalul textului, nu intră.
        la_inceput = cuvântul începe o propoziție: e primul din text, după cuvântul de dinainte a
        venit . ! ? sau un rând nou, ori are ghilimele lipite în față (said, "Look). Și asta se
        hotărăște doar din ce e scris înaintea cuvântului.
        """
        inceput = -1  # unde a început cuvântul în curs (-1 = niciunul)
        apostrof = False  # semnul de dinainte a fost un apostrof după litere
        sfarsit = -1  # unde s-a terminat cuvântul de dinainte (-1 = niciunul)
        for i, c in enumerate(text):
            if _e_litera(c):
                if inceput < 0:
                    inceput = i
                apostrof = False
            elif c == "'" and inceput >= 0 and not apostrof:
                apostrof = True
            elif inceput >= 0:
                intre = text[sfarsit:inceput] if sfarsit >= 0 else ""
                la_inceput = sfarsit < 0 or not SFARSIT_DE_PROPOZITIE.isdisjoint(intre) or intre.endswith(GHILIMELE)
                yield i, text[inceput:i], la_inceput
                sfarsit, inceput, apostrof = i, -1, False

    def caracteristici(self, text: str) -> list[tuple[int, ...]]:
        """Pentru fiecare literă: codul ultimului cuvânt TERMINAT până la ea, inclusiv."""
        curent = (GOL,) * self.nivele
        rezultat: list[tuple[int, ...]] = []
        ultima = 0
        for pozitie, cuvant, la_inceput in self.cuvinte_terminate(text):
            rezultat.extend([curent] * (pozitie - ultima))  # până aici, codul cuvântului de dinainte
            curent = self.cod(cuvant, la_inceput)
            ultima = pozitie
        rezultat.extend([curent] * (len(text) - ultima))
        return rezultat

    def coduri_cuvinte(self, text: str) -> list[tuple[int, ...]]:
        """Codul fiecărui cuvânt terminat, în ordine (ex. pentru a vedea ce fel de cuvinte stau alături)."""
        return [self.cod(cuvant, la_inceput) for _, cuvant, la_inceput in self.cuvinte_terminate(text)]

    def cauta(self, cuvant: str) -> list[dict[str, Any]]:
        """Toate sensurile unui cuvânt, pentru oameni: cod, parte de vorbire, raft, drum, relații."""
        rezultat = []
        for sens in self._sensuri_alese(cuvant):
            cod = self._cod[sens]
            rezultat.append({
                "cod": ".".join(str(x) for x in cod),
                "parte_de_vorbire": self._parti[cod[0] - 1],
                "raft": self._rafturi[cod[1] - 1],
                "drum": self._drum(sens),
                "relatii": [{"tip": tip, "catre": self._nume[tinta]} for tip, tinta in self._relatii.get(str(sens), [])],
            })
        return rezultat

    def statistici(self) -> dict[str, Any]:
        """Cât de des găsește memoria cuvintele căutate și ce ține minte plasa."""
        necunoscute = Counter(
            {c: n for c, n in self._folosiri.items() if self._plasa.get(c, (GOL,))[0] == NECUNOSCUT}
        )
        return {
            "cautari": self._cautari,
            "acoperire": round(self._gasite / self._cautari, 4) if self._cautari else 0.0,
            "drumuri_in_plasa": len(self._plasa),
            "cele_mai_folosite": [c for c, _ in self._folosiri.most_common(10)],
            "necunoscute_frecvente": [c for c, _ in necunoscute.most_common(10)],
        }
