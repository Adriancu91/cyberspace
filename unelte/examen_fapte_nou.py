"""Examenul de fapte nou (7 octombrie 2026): propoziții reformulate, care nu apar în textele de antrenare.

**De ce.** Examenul vechi (unelte/examen_fapte.py) întreabă faptele exact cum le-a primit profesorul ca să scrie
poveștile. 97 din cele 150 de propoziții ale lui apar cuvânt cu cuvânt în poveștile cu fapte, deci după o antrenare pe
ele ar măsura mai ales memorarea.

**Ce face.**
- Pentru fiecare din cele 50 de fapte, profesorul scrie 3 propoziții REFORMULATE: alt subiect gramatical, altă
  construcție. Ele se termină cu același cuvânt-răspuns, de ex. „A bird's body is covered with ___.”
- Verificarea e automată. O propoziție e bună doar dacă:
  - răspunsul e ultimul cuvânt (după un spațiu și un cuvânt obișnuit) și nu apare mai devreme;
  - e o singură propoziție, cu 5–16 cuvinte, care nu începe cu aceleași două cuvinte ca faptul și diferă de
    celelalte două ale faptului;
  - nici ea, nici vreun fragment de 5 cuvinte consecutive din ea nu apare în date/fapte/povesti.txt sau în
    TinyStories (date/tinystories_tot: antrenare și validare);
  - nu seamănă prea mult cu celelalte două ale faptului (cel mult 60% cuvinte comune);
  - profesorul, întrebat fără întâmplare, spune că ea spune același fapt, numind despre ce e vorba, și că e adevărată.
    Fără asta, „alt subiect” ajungea uneori „alt animal”, de ex. „A worm moves through the soil without ___.” pentru
    „Snakes have no legs.”;
  - profesorul, pus să completeze golul singur, scrie chiar răspunsul (sau un sinonim acceptat). Altfel golul e
    neclar, de ex. „…a shadow shows up in the ___.” cere „light”, dar firesc ar fi „ground”.
- Cele care nu trec se regenerează, de cel mult --runde ori: profesorul primește propoziția respinsă și motivul (de
  ex. fragmentul găsit) și scrie 3 variante noi; se păstrează prima care trece.
- Fișierele:
  - date/fapte/examen_nou.json: întrebările;
  - lucru/examen_fapte_nou/generare_<data>.json: toate încercările, cu motivele.

**Cum se dă.** Ca examenul vechi: elevul completează fără întâmplare. Scorul fapte_noi numără răspunsurile care sunt
exact cuvântul din fapt; se raportează și cu sinonime, și câte fapte știe. În jurnal intră doar numere, pe liniile
„examen_fapte_nou_generare” și „examen_fapte_nou”.

    python unelte/examen_fapte_nou.py --genereaza                        # profesorul, pe placa video (~4,5 GB)
    python unelte/examen_fapte_nou.py --completeaza                      # doar propozițiile care lipsesc
    python unelte/examen_fapte_nou.py --experiment 239                   # examenul nou pe un model salvat
    python unelte/examen_fapte_nou.py --experiment 226 --dispozitiv cpu  # pe procesor, cât placa video lucrează
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.jurnal import Jurnal  # noqa: E402
from module.examene_elev import (  # noqa: E402
    CALE_EXAMEN_NOU, INTREBARI, _singular, cuvinte, e_corect, examineaza_fapte_noi, scor_fapte_noi,
)
from module.profesor_qwen import FAPTE, ProfesorQwen  # noqa: E402

TEXTE_VERIFICATE = {"povestile cu fapte": ["date/fapte/povesti.txt"],
                    "TinyStories": ["date/tinystories_tot/antrenare.txt", "date/tinystories_tot/validare.txt"]}
PROPOZITII_PE_FAPT = 3
SISTEM = "You write short, simple English sentences for a quiz for young children."


# --- fragmentele de 5 cuvinte din textele mari -------------------------------------------------------------------------

class IndexFragmente:
    """Toate fragmentele de n cuvinte consecutive ale unor texte, ca amprente de 64 de biți sortate: o căutare e
    instantanee, oricât de mare e textul. Două fragmente diferite pot avea, extrem de rar, aceeași amprentă; atunci o
    propoziție bună e luată drept găsită și se regenerează degeaba (niciodată invers: un fragment care apare e găsit)."""

    MULTIPLICATOR = 0x100000001B3

    def __init__(self, n: int = 5) -> None:
        import numpy as np

        self.np = np
        self.n = n
        self.vocabular: dict[str, int] = {}
        self._bucati: list[Any] = []
        self.amprente = np.zeros(0, dtype=np.uint64)
        self.cuvinte = 0

    def _id_uri(self, lista: list[str]) -> Any:
        v = self.vocabular
        return self.np.fromiter((v.setdefault(c, len(v)) for c in lista), dtype=self.np.int64, count=len(lista))

    def _amprentele(self, ids: Any) -> Any:
        np = self.np
        m = len(ids) - self.n + 1
        if m <= 0:
            return np.zeros(0, dtype=np.uint64)
        a = ids.astype(np.uint64)
        h = np.zeros(m, dtype=np.uint64)
        for k in range(self.n):
            h = h * np.uint64(self.MULTIPLICATOR) + a[k : k + m]
        return h

    def adauga_text(self, text: str) -> None:
        ids = self._id_uri(cuvinte(text))
        self.cuvinte += len(ids)
        self._bucati.append(self._amprentele(ids))

    def adauga_fisier(self, cale: str | Path, octeti_pe_bucata: int = 64 * 2**20) -> None:
        """Pe bucăți tăiate la sfârșit de rând (fără să rupă litere), cu ultimele n−1 cuvinte duse în bucata următoare:
        fragmentele care trec de la o bucată la alta se găsesc și ele."""
        np = self.np
        coada = np.zeros(0, dtype=np.int64)
        rest = b""
        with open(cale, "rb") as f:
            while True:
                bloc = f.read(octeti_pe_bucata)
                date = rest + bloc
                if bloc:
                    taietura = date.rfind(b"\n") + 1
                    date, rest = (date[:taietura], date[taietura:]) if taietura else (b"", date)
                else:
                    rest = b""
                ids = self._id_uri(cuvinte(date.decode("utf-8", errors="ignore")))
                self.cuvinte += len(ids)
                ids = np.concatenate([coada, ids])
                self._bucati.append(self._amprentele(ids))
                coada = ids[-(self.n - 1):] if self.n > 1 else ids[:0]
                if not bloc:
                    break

    def gata(self) -> IndexFragmente:
        """Sortează amprentele (o dată, după ultimul text adăugat)."""
        np = self.np
        self.amprente = np.sort(np.concatenate([self.amprente, *self._bucati]))
        self._bucati = []
        return self

    def gasite(self, propozitie: str) -> list[str]:
        """Fragmentele de n cuvinte ale propoziției care apar în texte. (O propoziție mai scurtă de n cuvinte nu are
        niciun fragment: verificarea formei o respinge oricum.)"""
        np = self.np
        c = cuvinte(propozitie)
        gasite = []
        for i in range(len(c) - self.n + 1):
            fragment = c[i : i + self.n]
            if any(w not in self.vocabular for w in fragment):
                continue  # un cuvânt care nu apare nicăieri: nici fragmentul nu poate apărea
            h = self._amprentele(np.array([self.vocabular[w] for w in fragment], dtype=np.int64))[0]
            poz = np.searchsorted(self.amprente, h)
            if poz < len(self.amprente) and self.amprente[poz] == h:
                gasite.append(" ".join(fragment))
        return gasite


# --- propozițiile profesorului -------------------------------------------------------------------------------------------

def raspunsul_faptului(subiect: str) -> str:
    return INTREBARI[subiect][1][0]


REGULI = (
    "- Keep it about the same thing as the fact (if the fact is about dogs, every sentence is about dogs).\n"
    '- Do not start a sentence with the same words as the fact. Start it differently, for example with "When", "Every", '
    '"If", "In", or with a possessive like "A bird\'s body ...".\n'
    '- Each sentence ends with a blank "___" and a period. The missing word is "{raspuns}"; do not write '
    '"{raspuns}" anywhere in the sentence.\n'
    "- Use simple words that a five-year-old knows. Each sentence has 6 to 14 words.\n"
    "- Avoid common phrases: say it in your own fresh words.\n"
    '- Make "{raspuns}" the clear and natural word to finish the sentence: someone who knows the fact should guess it.\n'
    '- Tip: build the sentence so that the blank comes last, for example "Your heart\'s job is to pump ___." or '
    '"... is called ___."\n'
)


def cerere_trei(subiect: str) -> list[dict[str, str]]:
    raspuns = raspunsul_faptului(subiect)
    return [{"role": "system", "content": SISTEM}, {"role": "user", "content": (
        f'Fact: "{FAPTE[subiect]}"\nAnswer word: "{raspuns}"\n\n'
        f"Write 3 different quiz sentences that say the same fact in other words. Rules:\n"
        + REGULI.format(raspuns=raspuns)
        + 'Example for the fact "Birds have feathers." with the missing word "feathers": "A bird\'s body is covered '
          'with ___."\nWrite only the 3 sentences, one per line.')}]


def cerere_inlocuire(subiect: str, respinsa: str, motiv: str, celelalte: list[str]) -> list[dict[str, str]]:
    raspuns = raspunsul_faptului(subiect)
    diferite = f"They must be different from these sentences: {' / '.join(celelalte)}\n" if celelalte else ""
    return [{"role": "system", "content": SISTEM}, {"role": "user", "content": (
        f'Fact: "{FAPTE[subiect]}"\nAnswer word: "{raspuns}"\n\n'
        f'This quiz sentence was rejected: "{respinsa}"\nReason: {motiv}.\n\n'
        f"Write 3 new, different quiz sentences that say the same fact in other words. Rules:\n"
        + REGULI.format(raspuns=raspuns) + diferite + "Write only the 3 sentences, one per line.")}]


def cerere_acelasi_fapt(subiect: str, propozitie: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": "You are a careful teacher checking quiz sentences for young children."},
            {"role": "user", "content": (
                f'Fact: "{FAPTE[subiect]}"\nSentence: "{propozitie}"\n\nDoes the sentence clearly say the same fact, '
                f"naming what it is about (not only \"it\" or \"they\"), and is it true? Answer only YES or NO.")}]


def cerere_completare(propozitie_cu_gol: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": "You answer quiz questions for young children."},
            {"role": "user", "content": f'Fill in the blank with ONE word: "{propozitie_cu_gol}"\nAnswer with only that word.'}]


def prea_asemanatoare(a: list[str], b: list[str]) -> bool:
    """Două propoziții cu cel puțin 60% cuvinte comune (din toate cuvintele lor) sunt aproape la fel."""
    x, y = set(a), set(b)
    return bool(x | y) and len(x & y) / len(x | y) >= 0.6


def umple(linie: str, raspuns: str) -> str:
    """Propoziția întreagă: răspunsul pus în golul „___” (dacă profesorul a lăsat unul), fără spațiu înainte de punct."""
    linie = re.sub(r"_{2,}(?!.*_{2,})", raspuns, linie) if re.search(r"_{2,}", linie) else linie
    return re.sub(r"\s+([.!?])$", r"\1", linie.strip())


def linii_curate(raspuns: str) -> list[str]:
    """Propozițiile dintr-un răspuns: câte una pe rând, fără numerotare, liniuțe sau ghilimele."""
    linii = []
    for rand in raspuns.splitlines():
        rand = re.sub(r"^\s*(?:\d+[.)]|[-*•])\s*", "", rand).strip().strip('"“”').strip()
        if rand:
            linii.append(rand)
    return linii


def probleme(propozitie: str, subiect: str, celelalte: list[str]) -> list[str]:
    """De ce nu e bună o propoziție, fără căutarea în texte (listă goală = bună)."""
    raspuns = raspunsul_faptului(subiect).lower()
    c = cuvinte(propozitie)
    fapt = cuvinte(FAPTE[subiect])
    motive = []
    if re.search(r"[.!?][\"”']?\s+\S", propozitie.strip()):
        motive.append(f'write only one sentence, with "{raspuns}" as its last word and nothing after the period')
    if not 5 <= len(c) <= 16:
        motive.append(f"it has {len(c)} words (it must have 6 to 14)")
    if not c or c[-1] != raspuns:
        motive.append(f'it does not end with the word "{raspuns}"')
    elif not re.search(rf"[a-z0-9',]\s+{re.escape(raspuns)}\W*$", propozitie, re.IGNORECASE):
        motive.append(f'"{raspuns}" must come after a space and a normal word')
    elif any(_singular(w) == _singular(raspuns) for w in c[:-1]):
        motive.append(f'"{raspuns}" appears before the end')
    if len(c) >= 2 and [_singular(w) for w in c[:2]] == [_singular(w) for w in fapt[:2]]:  # „A dog has” = „Dogs have”
        motive.append(f'it starts with the same words as the fact ("{" ".join(c[:2])}")')
    if any(c == cuvinte(alta) for alta in celelalte):
        motive.append("it is the same as another sentence")
    elif any(prea_asemanatoare(c, cuvinte(alta)) for alta in celelalte):
        motive.append("it is too similar to another sentence for the same fact: say it in a different way")
    return motive


def cu_gol(propozitie: str, raspuns: str) -> str:
    """Propoziția cu „___” în locul ultimului cuvânt-răspuns."""
    return re.sub(rf"\b{re.escape(raspuns)}\b(?=\W*$)", "___", propozitie.strip(), flags=re.IGNORECASE)


def verifica(propozitie: str, subiect: str, celelalte: list[str],
             indexuri: dict[str, IndexFragmente]) -> tuple[str | None, str | None]:
    """(motivul respingerii, în engleză, pentru profesor; de ce: „forma” sau textul în care s-a găsit un fragment), sau
    (None, None) dacă propoziția e bună."""
    motive = probleme(propozitie, subiect, celelalte)
    if motive:
        return "; ".join(motive), "forma"
    for sursa, index in indexuri.items():
        gasite = index.gasite(propozitie)
        if gasite:
            return f"the words \"{gasite[0]}\" already appear in children's stories; say it with other words", sursa
    return None, None


def genereaza(profesor: Any, indexuri: dict[str, IndexFragmente], runde: int,
              pastrate: dict[str, list[str]] | None = None) -> dict[str, Any]:
    """Cele 150 de propoziții. Întâi câte 3 pe fapt. Apoi, rundă după rundă, pentru fiecare respinsă profesorul scrie 3
    variante noi (știind ce a fost respins și de ce); se păstrează prima care trece de formă și de fragmente, iar la final
    profesorul spune, fără întâmplare, dacă ea spune același fapt."""
    subiecte = list(INTREBARI)
    sloturi = [(s, k) for s in subiecte for k in range(PROPOZITII_PE_FAPT)]
    alese: dict[tuple[str, int], str | None] = {}
    istoric: dict[tuple[str, int], list[dict[str, Any]]] = {cheie: [] for cheie in sloturi}
    variante: dict[tuple[str, int], list[str]] = {}
    if pastrate is not None:  # completare: propozițiile deja bune rămân; cele care lipsesc se scriu de la capăt
        for s in subiecte:
            for k, propozitie in enumerate(pastrate.get(s, [])[:PROPOZITII_PE_FAPT]):
                alese[(s, k)] = propozitie
        lipsa = [cheie for cheie in sloturi if alese.get(cheie) is None]
        for cheie in sloturi:
            alese.setdefault(cheie, None)
        for cheie in lipsa:
            istoric[cheie].append({"propozitie": "", "motiv": "there was no good sentence yet", "respinsa_pentru": None})
        subiecte_noi: list[str] = []
    else:
        subiecte_noi = subiecte
    primele = profesor.raspunde_mai_multe([cerere_trei(s) for s in subiecte_noi], max_simboluri=160) if subiecte_noi else []
    for s, raspuns in zip(subiecte_noi, primele):
        linii = [umple(linie, raspunsul_faptului(s)) for linie in linii_curate(raspuns)]
        for k in range(PROPOZITII_PE_FAPT):
            variante[(s, k)] = [linii[k]] if k < len(linii) else []

    def celelalte(cheie: tuple[str, int], doar_dinainte: bool) -> list[str]:
        """Celelalte propoziții bune ale aceluiași fapt (la prima judecată, doar cele dinainte: dintre două la fel, a
        doua se regenerează)."""
        s, k = cheie
        return [p for (t, j), p in alese.items() if t == s and j != k and p and (j < k or not doar_dinainte)]

    def judeca(chei: list[tuple[str, int]], prima: bool) -> list[tuple[str, int]]:
        verdicte: dict[tuple[str, int], tuple[str | None, str | None]] = {}
        for cheie in chei:
            alese[cheie], verdicte[cheie] = None, ("there was no sentence", "forma")
            for varianta in variante[cheie]:
                motiv, de_ce = verifica(varianta, cheie[0], celelalte(cheie, prima), indexuri)
                istoric[cheie].append({"propozitie": varianta, "motiv": motiv, "respinsa_pentru": de_ce})
                if alese[cheie] is None or motiv is None:
                    alese[cheie], verdicte[cheie] = varianta, (motiv, de_ce)
                if motiv is None:
                    break
        de_intrebat = [cheie for cheie in chei if verdicte[cheie][0] is None]
        if de_intrebat:
            acelasi = profesor.raspunde_mai_multe([cerere_acelasi_fapt(s, alese[(s, k)]) for s, k in de_intrebat],
                                                  max_simboluri=4, cu_intamplare=False)
            completari = profesor.raspunde_mai_multe(
                [cerere_completare(cu_gol(alese[(s, k)], raspunsul_faptului(s))) for s, k in de_intrebat],
                max_simboluri=6, cu_intamplare=False)
            for cheie, da, cuvant in zip(de_intrebat, acelasi, completari):
                motiv = None
                if not da.strip().upper().startswith("YES"):
                    motiv = (f'it does not clearly say the same fact as "{FAPTE[cheie[0]]}", naming what it is about', "sens")
                elif not e_corect(" " + cuvant, tuple(INTREBARI[cheie[0]][1])):
                    motiv = (f'the blank is not clear: a reader would write "{cuvant.strip()[:30]}" instead of '
                             f'"{raspunsul_faptului(cheie[0])}"', "gol")
                if motiv:
                    verdicte[cheie] = motiv
                    istoric[cheie][-1].update(motiv=motiv[0], respinsa_pentru=motiv[1])
                else:
                    istoric[cheie][-1]["completarea_profesorului"] = cuvant.strip()
        respinse = [cheie for cheie in chei if verdicte[cheie][0]]
        for cheie in respinse:
            alese[cheie] = None if verdicte[cheie][1] != "forma" or alese[cheie] is None else alese[cheie]
        return respinse

    respinse = judeca(sloturi, prima=True) if pastrate is None else lipsa
    runde_facute = 0
    while respinse and runde_facute < runde:
        runde_facute += 1
        conversatii = [cerere_inlocuire(s, istoric[(s, k)][-1]["propozitie"] or "(none)", istoric[(s, k)][-1]["motiv"],
                                        celelalte((s, k), False)) for s, k in respinse]
        for cheie, raspuns in zip(respinse, profesor.raspunde_mai_multe(conversatii, max_simboluri=160)):
            variante[cheie] = [umple(linie, raspunsul_faptului(cheie[0]))
                               for linie in linii_curate(raspuns)[:PROPOZITII_PE_FAPT]]
        respinse = judeca(respinse, prima=False)

    intrebari = []
    for (s, k) in sloturi:
        if (s, k) in respinse:
            continue
        propozitie, raspuns = alese[(s, k)], raspunsul_faptului(s)
        intrebari.append({"subiect": s, "fapt": FAPTE[s], "propozitie": cu_gol(propozitie, raspuns),
                          "propozitie_intreaga": propozitie, "raspuns": raspuns, "acceptate": list(INTREBARI[s][1]),
                          "incercari": sum(1 for h in istoric[(s, k)] if h["propozitie"])})
    respingeri = [h["respinsa_pentru"] for istorie in istoric.values() for h in istorie if h["motiv"]]
    return {
        "intrebari": intrebari,
        "istoric": {f"{s}/{k + 1}": istorie for (s, k), istorie in istoric.items()},
        "numere": {
            "propozitii": len(intrebari), "regenerate": sum(1 for i in istoric.values() if len(i) > 1),
            "incercari_total": sum(1 for i in istoric.values() for h in i if h["propozitie"]), "runde": runde_facute,
            "esuate": len(respinse),
            "respingeri_povestile_cu_fapte": respingeri.count("povestile cu fapte"),
            "respingeri_tinystories": respingeri.count("TinyStories"),
            "respingeri_forma": respingeri.count("forma"), "respingeri_sens": respingeri.count("sens"),
            "respingeri_gol_neclar": respingeri.count("gol"),
        },
    }


def construieste_indexuri(texte: dict[str, list[str]], n: int) -> dict[str, IndexFragmente]:
    indexuri = {}
    for sursa, cai in texte.items():
        start = time.perf_counter()
        index = IndexFragmente(n)
        for cale in cai:
            index.adauga_fisier(cale)
        indexuri[sursa] = index.gata()
        print(f"   {sursa}: {index.cuvinte:,} de cuvinte, {len(index.vocabular):,} diferite, "
              f"{time.perf_counter() - start:.0f} s", flush=True)
    return indexuri


# --- linia de comandă ------------------------------------------------------------------------------------------------------

def main_genereaza(args: argparse.Namespace) -> int:
    print(f"Fragmentele de {args.fragment} cuvinte din textele de antrenare (o singură dată):", flush=True)
    indexuri = construieste_indexuri(TEXTE_VERIFICATE, args.fragment)
    profesor = ProfesorQwen(lot=args.lot, doar_local=args.doar_local, samanta=args.samanta, temperatura=0.9)
    vechi = json.loads(Path(args.iesire).read_text(encoding="utf-8")) if args.completeaza else None
    pastrate: dict[str, list[str]] | None = None
    if vechi is not None:
        pastrate = {}
        for intrebare in vechi["intrebari"]:
            pastrate.setdefault(intrebare["subiect"], []).append(intrebare["propozitie_intreaga"])
        print(f"Completare: păstrez cele {len(vechi['intrebari'])} propoziții din {args.iesire}.", flush=True)
    rezultat = genereaza(profesor, indexuri, args.runde, pastrate)
    memorie = profesor.memorie_video_mb()
    profesor.elibereaza()
    numere = {**rezultat["numere"], "memorie_gpu_rezervata_mb": memorie.get("rezervata")}
    cale = Path(args.iesire)
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_text(json.dumps({
        "versiune": 1, "data": datetime.now().isoformat(timespec="seconds"), "profesor": profesor.model,
        "fragment_cuvinte": args.fragment, "verificat_in": TEXTE_VERIFICATE, "numere": numere,
        "etape_anterioare": ((vechi.get("etape_anterioare") or []) + [vechi["numere"]]) if vechi else [],
        "intrebari": rezultat["intrebari"],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    dosar = Path(args.director_lucru) / "examen_fapte_nou"
    dosar.mkdir(parents=True, exist_ok=True)
    (dosar / f"generare_{eticheta}.json").write_text(json.dumps(rezultat["istoric"], ensure_ascii=False, indent=1),
                                                       encoding="utf-8")
    jurnal = Jurnal(Path(args.director_lucru))
    jurnal.adauga({
        "id": jurnal.urmatorul_id(), "linie": "examen_fapte_nou_generare",
        "inceput": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "propunere": {"descriere": f"examenul de fapte nou: propozițiile reformulate ale profesorului ({cale.as_posix()})",
                      "modificari": {}},
        "module": {"profesor": {**ProfesorQwen.MANIFEST, "model": profesor.model}}, "decizie": "masurat",
        "scoruri": numere,
    })
    print(f"\n=== Examenul de fapte nou: {numere['propozitii']} propoziții în {cale} ===")
    print(f"Regenerate: {numere['regenerate']} din {len(INTREBARI) * PROPOZITII_PE_FAPT} (în total "
          f"{numere['incercari_total']} de încercări, {numere['runde']} runde; nereușite: {numere['esuate']}).")
    print(f"Respingeri: {numere['respingeri_povestile_cu_fapte']} cu un fragment din poveștile cu fapte, "
          f"{numere['respingeri_tinystories']} din TinyStories, {numere['respingeri_forma']} pentru formă, "
          f"{numere['respingeri_sens']} pentru că nu spuneau clar același fapt, {numere['respingeri_gol_neclar']} pentru "
          f"că golul era neclar.")
    for intrebare in rezultat["intrebari"][:: max(1, len(rezultat["intrebari"]) // 5)][:5]:
        print(f"   {intrebare['fapt']}  →  {intrebare['propozitie']}  ({intrebare['raspuns']})")
    return 0 if numere["esuate"] == 0 else 1


def main_examen(args: argparse.Namespace) -> int:
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    jurnal = Jurnal(Path(args.director_lucru))
    fisa = fisa_modelului(jurnal, args.experiment, args.linie)
    elev = incarca_modelul(fisa, args.dispozitiv)
    rezultate = examineaza_fapte_noi(elev, args.examen)
    numere = {**scor_fapte_noi(rezultate), "intrebari": len(rezultate)}
    eticheta = datetime.now().strftime("%Y%m%d_%H%M%S")
    dosar = Path(args.director_lucru) / "examen_fapte_nou"
    dosar.mkdir(parents=True, exist_ok=True)
    iesire = dosar / f"experiment_{fisa['id']}_{eticheta}.json"
    iesire.write_text(json.dumps({"experiment": fisa["id"], "linie": fisa["linie"], **numere, "rezultate": rezultate},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    jurnal.adauga({
        "id": jurnal.urmatorul_id(), "linie": "examen_fapte_nou",
        "inceput": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "propunere": {"descriere": f"examenul de fapte nou pentru modelul experimentului #{fisa['id']} "
                                   f"(răspunsurile: {iesire.as_posix()})", "modificari": {}},
        "module": {"elev": {"experiment": fisa["id"], "linie": fisa["linie"]}}, "decizie": "masurat", "scoruri": numere,
    })
    print(f"=== Examenul de fapte nou: modelul experimentului #{fisa['id']} (linia „{fisa['linie']}”) ===")
    print(f"fapte_noi (doar cu cuvântul din fapt): {numere['fapte_noi']} din {len(rezultate)}; cu sinonime: "
          f"{numere['fapte_noi_cu_sinonime']}; fapte cu măcar un răspuns corect: {numere['fapte_noi_stiute']} din "
          f"{len(INTREBARI)}.")
    for r in [r for r in rezultate if r["corect_cuvantul_din_fapt"]][:8]:
        print(f"   corect: {r['intrebare']} → „{r['completare'].strip()}”")
    print(f"Toate răspunsurile: {iesire}", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Examenul de fapte nou: propoziții reformulate, nevăzute la antrenare.")
    ce = parser.add_mutually_exclusive_group(required=True)
    ce.add_argument("--genereaza", action="store_true", help="profesorul scrie și verifică propozițiile")
    ce.add_argument("--completeaza", action="store_true",
                    help="ca --genereaza, dar păstrează propozițiile bune din --iesire și le scrie doar pe cele care lipsesc")
    ce.add_argument("--experiment", type=int, help="examenul pe modelul acestui experiment")
    ce.add_argument("--linie", help="examenul pe ultimul model salvat de pe această linie de jurnal")
    parser.add_argument("--examen", default=CALE_EXAMEN_NOU, help="fișierul cu întrebările")
    parser.add_argument("--iesire", default=CALE_EXAMEN_NOU, help="unde scrie --genereaza întrebările")
    parser.add_argument("--runde", type=int, default=60, help="de câte ori se regenerează, cel mult, cele respinse")
    parser.add_argument("--fragment", type=int, default=5, help="câte cuvinte consecutive are un fragment căutat")
    parser.add_argument("--lot", type=int, default=16, help="câte cereri trimite profesorului deodată")
    parser.add_argument("--samanta", type=int, default=0)
    parser.add_argument("--doar-local", action="store_true", help="nu descărca nimic (modelul trebuie să fie în cache)")
    parser.add_argument("--director-lucru", default="lucru")
    parser.add_argument("--dispozitiv", default="", help="ex. cpu: elevul pe procesor")
    args = parser.parse_args(argv)
    return main_genereaza(args) if args.genereaza or args.completeaza else main_examen(args)


if __name__ == "__main__":
    raise SystemExit(main())
