"""„Răspuns din text” (19 octombrie 2026, hotărât de Adrian), pe procesor: perechi „Text: … / Întrebare: … / Răspuns: …”.

- **Textul** = primul paragraf al unui articol din Wikipedia în română (partea de antrenare), cu început curat (aceleași
  filtre ca la Wikipedia v3: unelte/conversatie_wikipedia.py), între --min-text și --max-text litere, fără cuvinte
  necunoscute și fără bucăți de 8 cuvinte din examene sau validări.
- **Întrebările cu răspunsul în text** (fel „text”) se fac după șabloane, iar răspunsul e luat din text, cuvânt cu cuvânt:
  „Ce este X?” (prima propoziție), „În ce județ / comună se află X?”, „Cine a regizat / scris / fondat / dezvoltat X?”,
  „În ce an s-a născut / a murit X?” (din paranteza „n. … / d. …”), „Din ce an este X?”, „Câți locuitori are X?”.
- **Întrebările fără răspuns în text** (fel „nu_scrie”, cam --fara din total), cu răspunsul „Nu scrie în text.”:
  jumătate despre același X, cu un lucru care lipsește din text („Cine a regizat X?” la un film fără „regizat”, „Câți
  locuitori are X?” la un sat fără „locuitori”, „În ce an s-a născut X?” la un om fără niciun an), jumătate despre alt
  subiect („Ce este Y?”, cu textul despre X).
- **Conversația simplă** (fel „conversatie”, fără text): docs/conversatie/conversatie_simpla.json, scrise de mână; în
  antrenare de --conversatie-ori ori, ca să nu se piardă printre celelalte.
- **Examenul pus deoparte**: --examen-text întrebări „text” și --examen-fara „nu_scrie”, din articole care nu intră deloc
  în antrenare, plus cele 10 de conversație din docs/conversatie/examen_scris_de_mana.json (doar urmărite).
Ies: date/conversatie/text/antrenare.jsonl, examen.json, info.json. Licența: Wikipedia, CC BY-SA 4.0.

**--formulari (S6, 20 octombrie 2026; implicit oprită, ca datele nopții 10 să rămână aceleași).** S4 a arătat că #401 a
învățat cuvintele întrebării, nu sensul. Cu --formulari, la antrenare (examenul rămâne neschimbat):
- fiecare șablon (în afară de „Ce este X?”) are 5–8 formulări (FORMULARI), alese la întâmplare, la fel și întrebările
  „Nu scrie în text.” despre același subiect; nicio formulare din examenul S4 (docs/conversatie/examen_generalizare_401.json)
  și niciun tip nou de întrebare;
- cam --da-nu din perechile cu text sunt da/nu, doar pe șabloanele an, locuitori, județ, comună, regizat, scris: „Da.”
  cu ce scrie în text, „Nu.” cu alt an / alt număr / alt nume, schimbat de unealtă (jumătate-jumătate).
Formulările și da/nu au întâmplarea lor (--samanta + 1), deci articolele și examenul sunt aceleași ca fără --formulari.

**--tipuri-noi (S11, 21 octombrie 2026; implicit oprită, ca datele nopților 10 și 11 să rămână aceleași).** Noaptea 11 a
arătat că formulările ajută la tipurile știute, nu la cele nevăzute. Cu --tipuri-noi, PESTE perechile de mai sus (care
rămân exact aceleași), din aceleași articole de antrenare: tipuri noi de întrebări (TIPURI_NOI: râuri, specii, deputați,
raioane, anul fondării / construcției), cu 3–5 formulări, „Nu scrie în text.” despre același subiect (cam --fara) și da/nu
(cam --da-nu, „Nu.” cu valoarea altui articol, niciodată cu una din text). Niciun tip din examenul S4 (b) (verificat de
verificari_tipuri_noi). Au întâmplarea lor (--samanta + 2).

    python unelte/conversatie_text.py --articole 6000
    python unelte/conversatie_text.py --articole 16000 --formulari --dosar date/conversatie/text_v2
    python unelte/conversatie_text.py --articole 16000 --formulari --tipuri-noi --dosar date/conversatie/text_v3
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

DOSAR = "date/conversatie/text"
NU_SCRIE = "Nu scrie în text."
CONVERSATIE = "docs/conversatie/conversatie_simpla.json"
SCRISE_DE_MANA = "docs/conversatie/examen_scris_de_mana.json"

_MARE = r"[A-ZĂÂÎȘȚ][\w-]*"
_NUME = rf"{_MARE}(?: {_MARE}){{1,2}}"  # 2–3 cuvinte cu literă mare: „Sergiu Nicolaescu”
_AN = r"(1[0-9]{3}|20[0-2][0-9])"
_JUDET = re.compile(rf"\bjudețul ({_MARE}(?:[- ]{_MARE})?)")
_COMUNA = re.compile(rf"\bcomuna ({_MARE}(?: {_MARE})?)")
_FACUT_DE = {
    "regizat": (re.compile(rf"\bregizat(?:ă)? de ({_NUME})"), "Cine a regizat {x}?"),
    "scris": (re.compile(rf"\bscris(?:ă)? de ({_NUME})"), "Cine a scris {x}?"),
    "fondat": (re.compile(rf"\b(?:fondat|fondată|înființat|înființată) de ({_NUME})"), "Cine a fondat {x}?"),
    "dezvoltat": (re.compile(rf"\bdezvoltat de ({_NUME})"), "Cine a dezvoltat {x}?"),
}
_NASCUT = re.compile(rf"\(n\. (?:\d{{1,2}} [a-zăâîșț]+ )?{_AN}\b")
_MURIT = re.compile(rf"\bd\. (?:\d{{1,2}} [a-zăâîșț]+ )?{_AN}\b")
_OPERA = re.compile(rf"^[^.]*?\b(?:film|album|joc video|roman|serial|cântec|single)\b[^.]*?\bdin {_AN}\b")
_LOCUITORI = re.compile(r"\b(\d{1,3}(?:\.\d{3})*|\d+) (?:de )?locuitori\b")
_PARANTEZA = re.compile(r"\s*\([^()]*\)")
# rupte de curățarea Wikimedia: „(în , în trad. Baia de Sus, în )”, „(născută Rotaru, )”, „(AFI )”
_PARANTEZA_RUPTA = re.compile(r"\s*\((?:[^()]*\bîn\s*,[^()]*|[^()]*\s)\)")
_STRAINE = re.compile(r"[^\x00-ɏ„”“–—’‘…²³°•·×]")  # alte alfabete (arabă, chirilică, greacă…)
_REGIUNE = re.compile(rf"\bîn regiunea ({_MARE}(?:[- ]{_MARE})?)")
_CAPITALA = re.compile(rf"\b(?:cu capitala (?:la|în)|[Aa]re capitala în orașul|[Cc]apitala (?:sa|lui|ei) este(?: orașul)?) "
                       rf"({_MARE}(?:[- ]{_MARE})?)")
_SUPRAFATA = re.compile(r"\bsuprafață (?:totală )?de (?:aproximativ )?(\d[\d.,]* (?:km²|ha))")
_DISTANTA = re.compile(rf"\bla (?:aproximativ |circa )?(\d+ km) (?:(?:spre )?(?:nord|sud|est|vest)(?:-(?:est|vest))? )?"
                       rf"de ({_MARE}(?:[- ]{_MARE})?)")


EXAMEN_S4 = "docs/conversatie/examen_generalizare_401.json"
# Formulările fiecărui șablon (prima e cea veche, în afară de murit și atestat). Răspunsul rămâne cel vechi, în afară de „Din …” → „În …” unde scrie.
# Lăsate deoparte, ca examenul S4 să rămână cinstit: „Ce populație are”, „Câți oameni trăiesc în”, „Ce număr de
# locuitori”, „Cine este autorul”, „Cine a făcut filmul”, „Cine a scris scenariul”, „Cât de mare este”, „În care județ
# e”, „Care este data nașterii”, „Când a fost lansat”, „Când s-a stins din viață”, „Când a venit pe lume”, „În ce an a …”
# (de aceea, cu --formulari, nici cele vechi „În ce an a murit / a apărut / a fost atestat documentar X?” nu mai apar).
FORMULARI: dict[str, list[str]] = {
    "nascut": ["În ce an s-a născut {x}?", "Când s-a născut {x}?", "Care e anul nașterii lui {x}?",
               "Ce an de naștere are {x}?", "{x} s-a născut în ce an?", "În ce an e născut {x}?"],
    "murit": ["În ce an moare {x}?", "Când a murit {x}?", "Care e anul morții lui {x}?", "Când a decedat {x}?",
              "{x} a murit în ce an?"],
    "locuitori": ["Câți locuitori are {x}?", "Câte persoane locuiesc în {x}?", "Câți locuitori sunt în {x}?",
                  "Câți locuitori numără {x}?", "Câtă lume locuiește în {x}?", "{x} câți locuitori are?"],
    "judet": ["În ce județ se află {x}?", "În ce județ este {x}?", "{x} se află în ce județ?",
              "În ce județ se găsește {x}?", "În ce județ e {x}?"],
    "comuna": ["În ce comună se află {x}?", "În ce comună este {x}?", "{x} se află în ce comună?",
               "În ce comună se găsește {x}?", "În ce comună e {x}?"],
    "distanta": ["La ce distanță de {y} se află {x}?", "La câți kilometri de {y} se află {x}?",
                 "La ce distanță se află {x} de {y}?", "Cât de departe de {y} se află {x}?",
                 "Cât de departe este {x} de {y}?"],
    "regiune": ["În ce regiune se află {x}?", "În ce regiune este {x}?", "{x} se află în ce regiune?",
                "În ce regiune se găsește {x}?", "În ce regiune e {x}?"],
    "capitala": ["Ce capitală are {x}?", "{x} ce capitală are?", "Unde își are capitala {x}?",
                 "Ce oraș are {x} drept capitală?", "Ce oraș e capitală pentru {x}?"],
    "suprafata": ["Ce suprafață are {x}?", "Ce întindere are {x}?", "Pe ce suprafață se întinde {x}?",
                  "{x} ce suprafață are?", "Ce suprafață ocupă {x}?"],
    "regizat": ["Cine a regizat {x}?", "Cine e regizorul lui {x}?", "Sub ce regie e {x}?",
                "Cine a făcut regia pentru {x}?", "Cine semnează regia lui {x}?"],
    "scris": ["Cine a scris {x}?", "Cine semnează {x}?", "Cine e cel care a scris {x}?",
              "Cine a fost cel care a scris {x}?", "Cine a pus pe hârtie {x}?"],
    "fondat": ["Cine a fondat {x}?", "Cine a înființat {x}?", "Cine e fondatorul lui {x}?",
               "Cine a pus bazele lui {x}?", "Cine a creat {x}?"],
    "dezvoltat": ["Cine a dezvoltat {x}?", "Cine e dezvoltatorul lui {x}?", "Cine a realizat {x}?",
                  "De cine a fost dezvoltat {x}?", "{x} a fost dezvoltat de cine?"],
    "an": ["Din ce an este {x}?", "Din ce an e {x}?", "Când a apărut {x}?", "Ce an de apariție are {x}?",
           "Care e anul apariției lui {x}?", "{x} e din ce an?"],
    # „Nu scrie în text.” despre același subiect (cele vechi: lipsa_*)
    "murit_unde": ["Unde a murit {x}?", "În ce loc a murit {x}?", "Unde a decedat {x}?", "{x} unde a murit?",
                   "În ce localitate a murit {x}?"],
    "parinti": ["Cine au fost părinții lui {x}?", "Cum se numeau părinții lui {x}?", "Ce părinți a avut {x}?",
                "Cine erau părinții lui {x}?", "Cine i-au fost părinți lui {x}?"],
    "altitudine": ["La ce altitudine se află {x}?", "Ce altitudine are {x}?", "La ce înălțime se află {x}?",
                   "{x} la ce altitudine se află?", "Cât de sus se află {x}?"],
    "atestat": ["În ce an e atestat documentar {x}?", "Când a fost atestat documentar {x}?",
                "Din ce an e atestat documentar {x}?", "Când apare {x} prima dată în documente?",
                "În ce an apare prima dată în documente {x}?"],
}
# cele vechi „Nu scrie” care au alt șablon decât perechea „text” cu același nume
_LIPSA_VECHI = {"fondat": "Cine a creat {x}?"}
_RASPUNS_IN = {"Când a apărut {x}?", "Ce an de apariție are {x}?", "Care e anul apariției lui {x}?"}
# da/nu: (întrebarea, de unde vine valoarea din răspuns)
DA_NU: dict[str, list[str]] = {
    "nascut": ["S-a născut {x} în {v}?", "{x} s-a născut în {v}?", "E adevărat că {x} s-a născut în {v}?"],
    "murit": ["A murit {x} în {v}?", "{x} a murit în {v}?", "E adevărat că {x} a murit în {v}?"],
    "an": ["Este {x} din {v}?", "{x} e din {v}?", "A apărut {x} în {v}?"],
    "locuitori": ["Are {x} {v}?", "{x} are {v}?", "E adevărat că {x} are {v}?"],
    "judet": ["Se află {x} în județul {v}?", "{x} e în județul {v}?", "E adevărat că {x} e în județul {v}?"],
    "comuna": ["Se află {x} în comuna {v}?", "{x} e în comuna {v}?", "E adevărat că {x} e în comuna {v}?"],
    "regizat": ["A regizat {v} {x}?", "E {v} regizorul lui {x}?", "E adevărat că {v} a regizat {x}?"],
    "scris": ["A scris {v} {x}?", "{v} a scris {x}?", "E adevărat că {v} a scris {x}?"],
}


def _valoare(q: dict[str, str]) -> str:
    """Ce e de verificat la da/nu: anul, „1.204 locuitori”, „Tulcea”, „Leigh Jason”."""
    r = q["raspuns"].rstrip(".")
    for prefix in ("În județul ", "În comuna ", "Din ", "În "):
        r = r.removeprefix(prefix)
    return r


def _alta_valoare(tip: str, v: str, text: str, alte: dict[str, list[str]], rng: random.Random) -> str | None:
    """O valoare greșită pentru „Nu.”: alt an (±1–30), alt număr de locuitori, alt nume de același fel (din alte
    articole); niciodată una care apare în text."""
    for _ in range(20):
        if tip in ("nascut", "murit", "an"):
            nou = str(int(v) + rng.choice([-1, 1]) * rng.randint(1, 30))
        elif tip == "locuitori":
            m = re.match(r"([\d.]+) ((?:de )?locuitori)", v)
            if m is None:
                return None
            n = int(m.group(1).replace(".", ""))
            alt = max(2, round(n * rng.choice([0.4, 0.6, 0.75, 1.3, 1.5, 2.5]) + rng.randint(-9, 9)))
            nou = f"{alt:,}".replace(",", ".") + (" de locuitori" if alt % 100 >= 20 or alt % 100 == 0 else " locuitori")
        else:
            if not alte.get(tip):
                return None
            nou = rng.choice(alte[tip])
        if nou != v and nou not in text and nou.split()[0] not in text:
            return nou
    return None


def da_nu_pentru(pozitive: list[dict[str, Any]], cate: int, rng: random.Random) -> list[dict[str, Any]]:
    """`cate` perechi da/nu din perechile „text” cu șabloanele din DA_NU, jumătate „Da.” (valoarea din text) și jumătate
    „Nu.” (altă valoare, schimbată de unealtă). Câte una pe articol, cel mult."""
    bune = [p for p in pozitive if p["tip"] in DA_NU]
    alte: dict[str, list[str]] = {}
    for p in bune:
        if p["tip"] in ("judet", "comuna", "regizat", "scris"):
            alte.setdefault(p["tip"], []).append(_valoare(p))
    rng.shuffle(bune)
    perechi: list[dict[str, Any]] = []
    grupuri: set[str] = set()
    for p in bune:
        if len(perechi) >= cate:
            break
        if p["grup"] in grupuri:
            continue
        v = _valoare(p)
        da = len(perechi) % 2 == 0
        if not da and (v := _alta_valoare(p["tip"], v, p["text"], alte, rng)) is None:
            continue
        intrebare = rng.choice(DA_NU[p["tip"]]).format(x=p["x"], v=v)
        grupuri.add(p["grup"])
        perechi.append({"fel": "text", "limba": "ro", "grup": p["grup"], "text": p["text"], "tip": f"da_nu_{p['tip']}",
                        "intrebare": intrebare, "raspuns": "Da." if da else "Nu."})
    return perechi


def reformuleaza(p: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Aceeași pereche, cu o formulare aleasă la întâmplare (și „Din” → „În” unde formularea o cere)."""
    tip = p["tip"].removeprefix("lipsa_")
    if tip not in FORMULARI or "x" not in p:
        return p
    sablon = rng.choice(FORMULARI[tip])
    if p["tip"].startswith("lipsa_") and tip in _LIPSA_VECHI and sablon == FORMULARI[tip][0]:
        sablon = _LIPSA_VECHI[tip]
    y = p["intrebare"].removeprefix("La ce distanță de ").split(" se află ")[0] if tip == "distanta" else ""
    nou = {**p, "intrebare": sablon.format(x=p["x"], y=y)}
    if sablon in _RASPUNS_IN and nou["raspuns"].startswith("Din "):
        nou["raspuns"] = "În " + nou["raspuns"].removeprefix("Din ")
    return nou


def inceputuri_interzise(cuvinte: int = 4) -> set[str]:
    """Primele `cuvinte` cuvinte ale fiecărei întrebări din examenul S4 (litere mici, fără semne)."""
    s4 = json.loads((RADACINA / EXAMEN_S4).read_text(encoding="utf-8"))["perechi"]
    return {_inceput(p["intrebare"], cuvinte) for p in s4}


def _inceput(intrebare: str, cuvinte: int = 4) -> str:
    return " ".join(intrebare.lower().replace("?", " ").replace(",", " ").split()[:cuvinte])


def verificari(antrenare: list[dict[str, Any]]) -> dict[str, Any]:
    """Ce cere S6 la 3.(ii)–(iii): câte întrebări de antrenare încep cu primele 4 cuvinte ale unei întrebări din S4 (pe
    începuturi, cu felul lor), câte texte din examenul nopții 10 sau din S4 au ajuns în antrenare (trebuie 0)."""
    interzise = inceputuri_interzise()
    gasite: Counter[str] = Counter()
    for p in antrenare:
        if (inceput := _inceput(p["intrebare"])) in interzise:
            gasite[f"{inceput} ({p['tip']})"] += 1
    texte = {p["text"] for p in json.loads((RADACINA / DOSAR / "examen.json").read_text(encoding="utf-8"))["perechi"]
             if "text" in p}
    texte |= {p["text"] for p in json.loads((RADACINA / EXAMEN_S4).read_text(encoding="utf-8"))["perechi"]}
    return {"inceputuri_din_S4": sum(gasite.values()), "inceputuri_din_S4_pe_fel": dict(gasite),
            "texte_din_examene": sum(p.get("text") in texte for p in antrenare),
            "da_nu": dict(Counter(p["raspuns"] for p in antrenare if p["tip"].startswith("da_nu"))),
            "formulari_pe_sablon": {t: len(f) for t, f in FORMULARI.items()}}


# --tipuri-noi (S11). {x} = subiectul, {f} = cuvântul din text („descrisă”, „fondat”, „deputat”), {v} = valoarea (da/nu).
# Lăsate deoparte: „În ce an a …” (început din S4), „Cât de lung …” (S4 (d)), „Cărui … îi este …” (S4 (b), zeul).
TIPURI_NOI: dict[str, list[str]] = {
    "afluent": ["Al cărui râu este afluent {x}?", "{x} este afluent al cărui râu?", "Al cărui râu e afluent {x}?",
                "Afluent al cărui râu este {x}?"],
    "bazin": ["Din ce bazin face parte {x}?", "{x} face parte din ce bazin?", "Din ce bazin hidrografic face parte {x}?",
              "Din bazinul cărui râu face parte {x}?"],
    "lungime": ["Ce lungime are {x}?", "{x} ce lungime are?", "Ce lungime măsoară {x}?", "Câți kilometri are {x}?"],
    "familie": ["Din ce familie face parte {x}?", "Din ce familie este {x}?", "{x} face parte din ce familie?",
                "Din ce familie e {x}?", "{x} este din ce familie?"],
    "gen": ["Din ce gen face parte {x}?", "Din ce gen este {x}?", "{x} face parte din ce gen?", "Din ce gen e {x}?",
            "{x} este din ce gen?"],
    "descris_cine": ["Cine a descris specia {x}?", "Cine a descris prima dată specia {x}?",
                     "De cine a fost {f} specia {x}?", "Specia {x} a fost {f} de cine?"],
    "descris_an": ["Când a fost {f} {x}?", "În ce an e {f} {x}?", "{x} a fost {f} în ce an?",
                   "Care e anul în care a fost {f} {x}?"],
    "legislatura": ["În ce legislatură a fost {f} {x}?", "În ce legislatură a fost {x} {f}?",
                    "{x} a fost {f} în ce legislatură?", "În care legislatură a fost {f} {x}?",
                    "Care e legislatura în care {x} a fost {f}?"],
    "partid": ["Pe listele cărui partid a fost ales {x}?", "{x} a candidat pe listele cărui partid?",
               "Pe listele cărui partid a candidat {x}?", "Pe ce liste a candidat {x}?",
               "Pe listele cărui partid a intrat {x} în parlament?"],
    "rau": ["Pe ce râu se află {x}?", "{x} se află pe ce râu?", "Pe ce râu e {x}?", "Lângă ce râu se află {x}?",
            "Pe malul cărui râu se află {x}?"],
    "raion": ["În ce raion se află {x}?", "În ce raion este {x}?", "{x} se află în ce raion?",
              "În ce raion se găsește {x}?", "În ce raion e {x}?"],
    "fondat_an": ["Când a fost {f} {x}?", "În ce an e {f} {x}?", "{x} a fost {f} în ce an?",
                  "Care e anul în care a fost {f} {x}?"],
    "construit_an": ["Când a fost {f} {x}?", "În ce an e {f} {x}?", "{x} a fost {f} în ce an?",
                     "Care e anul în care a fost {f} {x}?"],
}
DA_NU_NOI: dict[str, list[str]] = {
    "afluent": ["Este {x} afluent al râului {v}?", "{x} e afluent al râului {v}?", "E adevărat că {x} e afluent al râului {v}?"],
    "familie": ["Face parte {x} din familia {v}?", "{x} e din familia {v}?", "E adevărat că {x} face parte din familia {v}?"],
    "gen": ["Face parte {x} din genul {v}?", "{x} e din genul {v}?", "E adevărat că {x} face parte din genul {v}?"],
    "descris_cine": ["A descris {v} specia {x}?", "{v} a descris specia {x}?", "E adevărat că {v} a descris specia {x}?"],
    "descris_an": ["{x} a fost {f} în {v}?", "E adevărat că {x} a fost {f} în {v}?", "Este {x} {f} în {v}?"],
    "legislatura": ["{x} a fost {f} în legislatura {v}?", "E adevărat că {x} a fost {f} în legislatura {v}?",
                    "A fost {x} {f} în legislatura {v}?"],
    "partid": ["{x} a candidat pe listele {v}?", "E adevărat că {x} a candidat pe listele {v}?",
               "A candidat {x} pe listele {v}?"],
    "rau": ["Se află {x} pe râul {v}?", "{x} e pe râul {v}?", "E adevărat că {x} se află pe râul {v}?"],
    "raion": ["Se află {x} în raionul {v}?", "{x} e în raionul {v}?", "E adevărat că {x} e în raionul {v}?"],
    "fondat_an": ["{x} a fost {f} în {v}?", "E adevărat că {x} a fost {f} în {v}?", "Este {x} {f} în {v}?"],
    "construit_an": ["{x} a fost {f} în {v}?", "E adevărat că {x} a fost {f} în {v}?", "Este {x} {f} în {v}?"],
}
# Tipurile din S4 (b), interzise la antrenare (verificat pe șabloane și pe întrebările făcute, fără subiect și valoare).
INTERZISE_S4_B = re.compile(
    r"\bțar[aăi]|\btrup[aăe]|\bformați|\bclub|\bechip|\bevolue|\bjoac[ăa]\b|s-a născut|\bnaștere|științific|\bzeu|"
    r"dedicat|\bfirm[aăe]|\blansat|\bprodus|\bmedali|\bprofesor|\breședinț|\bmar(?:e|ea)\b|scufund|\blocuri\b|"
    r"\bmembri|\bmeseri|\bocupați", re.IGNORECASE)

_MARE_LAT = r"[A-ZĂÂÎȘȚÀ-ÖØ-ÞŠŽČĆŁ][\w'’-]*"
_RAU = rf"{_MARE}(?: (?:de |lui )?{_MARE}){{0,2}}"
_ESTE_RAU = re.compile(r"\b(?:este|e) (?:un |o )?(?:râu|fluviu|pârâu|curs de apă|afluent)\b")
_AFLUENT = re.compile(rf"\bafluent (?:de (?:dreapta|stânga) )?al (râului|fluviului) ({_RAU})")
_BAZIN = re.compile(rf"\bdin bazinul (?:hidrografic al )?(râului|fluviului) ({_RAU})")
_LUNGIME = re.compile(r"\b(?:are|având|cu|în) (?:o )?lungime(?:a)? (?:totală )?de (?:aproximativ |circa )?(\d[\d.,]* km)\b")
_FAMILIE = re.compile(r"\bfamilia ([A-Z][a-z]+(?:idae|aceae|inae))\b")
_GEN = re.compile(r"\bdin genul ([A-Z][a-z]+)\b")
_UN_AUTOR = rf"{_MARE_LAT}(?: (?:(?:von|van|de|der|du|da|la) )?{_MARE_LAT}){{0,4}}"
_AUTOR = rf"{_UN_AUTOR}(?:(?:, | și | & ){_UN_AUTOR})*"
_E_SPECIE = re.compile(r"\b(?:este|sunt|e) (?:o |un |singura |unica )?(?:specie|gen)\b")
_DESCRIS = re.compile(rf"\b(descris|descrisă) (?:pentru prima (?:dată|oară) |prima dată )?de ({_AUTOR})"
                      rf"(?:,? (?:în )?(?:anul )?{_AN}\b)?")
_ROL = r"deputat|deputată|senator|senatoare"
_LEGISLATURA = re.compile(rf"\b({_ROL})\b(?:(?!{_ROL})[^.]){{0,90}}?\bîn legislatura (\d{{4}} ?[-–] ?\d{{4}})")
_PARTID = re.compile(rf"\bpe listele ((?:partidului |Partidului |formațiunii )?({_MARE}(?: {_MARE}){{0,5}}))")
_PE_RAU = re.compile(rf"\b(pe (?:malul (?:(?:stâng|drept|de (?:est|vest|nord|sud)) )?(?:al )?)?(?:râului|fluviului|râul|"
                     rf"fluviul) ({_RAU}))")
_RAION = re.compile(rf"\braionul ({_MARE}(?:[- ]{_MARE})?)")
_FONDAT_AN = re.compile(rf"\b(fondat|fondată|înființat|înființată) (?:în|la)(?: \d{{1,2}} [a-zăâîșț]+)? (?:anul )?{_AN}\b"
                        rf"(?!\s*[-–])")
_CONSTRUIT_AN = re.compile(rf"\b(construit|construită|ridicat|ridicată) (?:în|la)(?: \d{{1,2}} [a-zăâîșț]+)? (?:anul )?"
                           rf"{_AN}\b(?!\s*[-–])")
_DESPRE_X = ("A fost", "Este", "Se ", "Are ", "Acesta", "Aceasta", "El ", "Ea ", "Localitatea", "Orașul", "Satul",
             "Comuna", "Râul", "Clubul", "Clădirea", "Biserica", "Specia", "Lacul", "Situat", "Situată", "Aflat", "Aflată")


def _subiect(x: str) -> str:
    """„Râul Doftana” → „râul Doftana” în mijlocul întrebării."""
    return "râul " + x.removeprefix("Râul ") if x.startswith("Râul ") else x


def _despre_x(text: str, x: str) -> list[str]:
    """Propozițiile care sigur vorbesc despre X: prima și cele care încep cu X sau cu „Este”, „Localitatea”…"""
    from unelte.conversatie_wikipedia import _PROPOZITII

    prop = _PROPOZITII.split(text)
    return [p for k, p in enumerate(prop) if k == 0 or p.startswith((x, *_DESPRE_X))]


def intrebari_noi(text: str, x: str, tip: str) -> list[dict[str, str]]:
    """Tipurile noi (S11) al căror răspuns e în text, cuvânt cu cuvânt. `valoare` e ce se verifică la da/nu, `f` cuvântul
    din text care intră în întrebare („descrisă”, „fondat”, „deputat”)."""
    fara_paranteze = _PARANTEZA.sub("", text)
    despre = " ".join(_despre_x(fara_paranteze, x))
    q: list[dict[str, str]] = []

    def adauga(t: str, raspuns: str, valoare: str, f: str = "") -> None:
        if valoare and valoare not in x and x not in valoare:
            q.append({"tip": f"nou_{t}", "raspuns": raspuns, "valoare": valoare, "f": f})

    rau = x.startswith(("Râul ", "Pârâul ")) or bool(_ESTE_RAU.search(_prima_propozitie(fara_paranteze)))
    if rau:
        if m := _AFLUENT.search(despre):
            adauga("afluent", f"Al {m.group(1)} {m.group(2)}.", m.group(2))
        if m := _BAZIN.search(despre):
            adauga("bazin", f"Din bazinul {m.group(1)} {m.group(2)}.", m.group(2))
        if m := _LUNGIME.search(despre):
            adauga("lungime", f"{m.group(1)}.", m.group(1))
    if tip == "ce" and _E_SPECIE.search(despre):  # X e o specie sau un gen, nu o boală sau o familie
        if len(set(_FAMILIE.findall(fara_paranteze))) == 1 and (m := _FAMILIE.search(despre)):
            adauga("familie", f"Din familia {m.group(1)}.", m.group(1))
        if len(set(_GEN.findall(fara_paranteze))) == 1 and (m := _GEN.search(despre)):
            adauga("gen", f"Din genul {m.group(1)}.", m.group(1))
        e_specie = re.search(r"\b(?:este|e) (?:o |singura |unica )?specie\b", despre)  # „specia X”, nu un gen
        if e_specie and len(_DESCRIS.findall(fara_paranteze)) == 1 and (m := _DESCRIS.search(fara_paranteze)):
            autor = m.group(2) if m.group(2).endswith(".") and len(m.group(2).split()[-1]) <= 2 else m.group(2).rstrip(".")
            adauga("descris_cine", autor if autor.endswith(".") else f"{autor}.", autor, "descrisă")
            if m.group(3):
                adauga("descris_an", f"În {m.group(3)}.", m.group(3), m.group(1))
    if tip == "om":
        if fara_paranteze.count("legislatur") == 1 and (m := _LEGISLATURA.search(fara_paranteze)):
            adauga("legislatura", f"În legislatura {m.group(2)}.", m.group(2), m.group(1))
        if fara_paranteze.count("pe listele") == 1 and (m := _PARTID.search(fara_paranteze)):
            adauga("partid", f"Pe listele {m.group(1)}.", m.group(1))
    if tip in ("loc", "ce") and not rau:
        if len({g[1] for g in _PE_RAU.findall(despre)}) == 1 and (m := _PE_RAU.search(despre)):
            adauga("rau", f"{m.group(1)[0].upper()}{m.group(1)[1:]}.", m.group(2))
        if not x.startswith("Raionul") and len(set(_RAION.findall(fara_paranteze))) == 1 and (m := _RAION.search(fara_paranteze)):
            adauga("raion", f"În raionul {m.group(1)}.", m.group(1))
    if tip == "ce":
        if len(_FONDAT_AN.findall(fara_paranteze)) == 1 and (m := _FONDAT_AN.search(despre)):
            adauga("fondat_an", f"În {m.group(2)}.", m.group(2), _acord(m.group(1), x))
        if len(_CONSTRUIT_AN.findall(fara_paranteze)) == 1 and (m := _CONSTRUIT_AN.search(despre)):
            adauga("construit_an", f"În {m.group(2)}.", m.group(2), _acord(m.group(1), x))
    return q


def _acord(f: str, x: str) -> str:
    """„construit” → „construită” când X e feminin după primul cuvânt („Biserica”, „Federația”), invers la „Muzeul”;
    altfel cum scrie în text."""
    fem = {"construit": "construită", "fondat": "fondată", "înființat": "înființată", "ridicat": "ridicată",
           "descris": "descrisă"}
    masc = {v: k for k, v in fem.items()}
    primul = x.split()[0]
    if re.fullmatch(r"[A-ZĂÂÎȘȚ][a-zăâîșț]+(?:ia|ea|ua|ca|ga|ta|ra|na|la|sa|da|za|ța|șa)", primul):
        return fem.get(f, f)
    if re.fullmatch(r"[A-ZĂÂÎȘȚ][a-zăâîșț]+(?:ul|le)", primul):
        return masc.get(f, f)
    return f


def _prima_propozitie(text: str) -> str:
    from unelte.conversatie_wikipedia import _PROPOZITII

    return _PROPOZITII.split(text)[0]


def lipsa_noi(text: str, x: str, tip: str) -> list[dict[str, str]]:
    """Tipurile noi despre același X, cu un lucru care sigur nu e în text (răspunsul: „Nu scrie în text.”). La lungime
    și la gen nu (genul se vede din numele speciei; lungimile sunt în S4 (d))."""
    mic = text.lower()
    q: list[tuple[str, str]] = []
    rau = bool(_ESTE_RAU.search(_prima_propozitie(text)))
    if rau and not re.search(r"afluen|se varsă|vărsându|vărsare|tributar|confluen|se unește|formează|braț|curge (?:spre|în)", mic):
        q.append(("afluent", ""))
    specie = tip == "ce" and re.search(r"\b(?:este|e) (?:o |singura |unica )?specie\b", " ".join(_despre_x(text, x)))
    if specie and "famili" not in mic and not re.search(r"\w(?:idae|aceae|inae)\b", text):
        q.append(("familie", ""))
    if specie and "descris" not in mic and "descoperit" not in mic and not re.search(_AN, text):
        q.append(("descris_cine", "descrisă"))
    if tip == "om" and (rol := re.search(rf"\b({_ROL})\b", text)):
        if "legislatur" not in mic and "mandat" not in mic and not re.search(_AN, _PARANTEZA.sub("", text)):
            q.append(("legislatura", rol.group(1)))
        if not re.search(r"\b[A-Z]{2,}\b|[A-Z]\.[A-Z]", text) and not re.search(
                r"partid|pe listele|din partea|ales|liberal|democrat|comunist|țărănist|socialist|legionar|naționalist|"
                r"conservator|membr", mic):
            q.append(("partid", ""))
    prima = _prima_propozitie(text)
    if tip == "loc" and re.search(r"\b(sat|oraș|comună|localitate)\b", prima) and not rau and not re.search(
            r"râu|fluvi|\bmal|pârâ|dunăr|prut|nistru|lac|vale|apa|curs", mic):
        q.append(("rau", ""))
    if (tip == "loc" and re.search(r"Republica Moldova|Ucraina", prima) and re.search(r"\b(sat|oraș|comună|localitate|așezare)\b",
                                                                                         prima)
            and "raion" not in mic and not x.startswith(("Raionul", "Județul", "Regiunea"))):
        q.append(("raion", ""))
    # nici „203”, nici „secolul al XIX-lea”, nici „fondat la în districtul” (anul șters la curățare)
    fara_ani = not re.search(r"\d|\b(?:în|la|din) (?:în|la|din|,|\.)|\b[IVX]{2,}\b", text) and not re.search(
        r"secol|sec\.|mileni|epoc|perioad|domni|antic|mediev|î\.\s?hr", mic)
    despre = " ".join(_despre_x(text, x))
    if tip == "ce" and (m := re.search(r"\b(fondat|fondată|înființat|înființată)\b", despre)) and fara_ani:
        q.append(("fondat_an", _acord(m.group(1), x)))
    if tip == "ce" and (m := re.search(r"\ba fost (construit|construită)\b", despre)) and fara_ani:
        q.append(("construit_an", _acord(m.group(1), x)))
    return [{"tip": f"lipsa_nou_{t}", "raspuns": NU_SCRIE, "valoare": "", "f": f} for t, f in q]


def _intrebare_noua(p: dict[str, Any], rng: random.Random, v: str | None = None) -> str:
    tip = p["tip"].removeprefix("lipsa_").removeprefix("nou_")
    sabloane = DA_NU_NOI[tip] if v is not None else TIPURI_NOI[tip]
    intrebare = rng.choice(sabloane).format(x=_subiect(p["x"]), f=p["f"], v=v)
    if v is not None and " și " in v:  # mai mulți autori
        intrebare = intrebare.replace(f"{v} a descris", f"{v} au descris").replace("A descris", "Au descris")
    return intrebare[0].upper() + intrebare[1:]


def _alta_valoare_noua(tip: str, v: str, text: str, alte: dict[str, list[str]], rng: random.Random) -> str | None:
    """O valoare greșită pentru „Nu.”: alt an (±1–30), altă valoare a altui articol; niciodată una care e în text."""
    for _ in range(30):
        if tip in ("descris_an", "fondat_an", "construit_an"):
            nou = str(min(2025, int(v) + rng.choice([-1, 1]) * rng.randint(1, 30)))
        elif alte.get(tip):
            nou = rng.choice(alte[tip])
        else:
            return None
        cuvinte = [c for c in re.findall(r"[\w'’]+", nou) if c not in ("partidului", "Partidului", "formațiunii") and len(c) > 1]
        if nou != v and cuvinte and not any(c in text for c in cuvinte):
            return nou
    return None


def perechi_noi(articole_: list[dict[str, Any]], fara: float, da_nu: float, rng: random.Random, prefix: str
                ) -> list[dict[str, Any]]:
    """Perechile tipurilor noi (S11), separate de cele vechi: toate cele cu text, cam `da_nu` din total da/nu (câte una pe
    articol, cel mult; jumătate „Da.”, jumătate „Nu.”), cam `fara` din total „Nu scrie în text.” despre același subiect.
    Grupul e cel al articolului, ca perechile-soră să stea împreună. Câmpul „x” rămâne (îl scoate apelantul)."""
    pozitive: list[dict[str, Any]] = []
    lipsa: list[dict[str, Any]] = []
    for i, a in enumerate(articole_):
        baza = {"fel": "text", "limba": "ro", "grup": f"{prefix}_{i}", "text": a["text"], "x": a["x"]}
        pozitive += [{**baza, **q} for q in intrebari_noi(a["text"], a["x"], a["tip"])]
        lipsa += [{**baza, "fel": "nu_scrie", **q} for q in lipsa_noi(a["text"], a["x"], a["tip"])]
    alte: dict[str, list[str]] = {}
    for p in pozitive:
        alte.setdefault(p["tip"].removeprefix("nou_"), []).append(p["valoare"])
    cate_da_nu = round(da_nu / (1 - da_nu - fara) * len(pozitive))
    candidati = [p for p in pozitive if p["tip"].removeprefix("nou_") in DA_NU_NOI]
    rng.shuffle(candidati)
    perechi: list[dict[str, Any]] = []
    grupuri: set[str] = set()
    for p in candidati:
        if len(perechi) >= cate_da_nu:
            break
        if p["grup"] in grupuri:
            continue
        tip = p["tip"].removeprefix("nou_")
        da = len(perechi) % 2 == 0
        v = p["valoare"] if da else _alta_valoare_noua(tip, p["valoare"], p["text"], alte, rng)
        if v is None:
            continue
        grupuri.add(p["grup"])
        perechi.append({**p, "tip": f"da_nu_nou_{tip}", "intrebare": _intrebare_noua(p, rng, v),
                        "raspuns": "Da." if da else "Nu.", "valoare": v})
    perechi += [{**p, "intrebare": _intrebare_noua(p, rng)} for p in pozitive]
    rng.shuffle(lipsa)
    pe_tip: dict[str, list[dict[str, Any]]] = {}
    for p in lipsa:
        pe_tip.setdefault(p["tip"], []).append(p)
    alese: list[dict[str, Any]] = []
    cate_fara = round(fara / (1 - fara) * len(perechi))
    while len(alese) < cate_fara and any(pe_tip.values()):  # pe rând din fiecare tip, ca niciunul să nu le acopere pe celelalte
        for t in sorted(pe_tip):
            if pe_tip[t] and len(alese) < cate_fara:
                alese.append(pe_tip[t].pop())
    perechi += [{**p, "intrebare": _intrebare_noua(p, rng)} for p in alese]
    return [{k: v for k, v in p.items() if k not in ("valoare", "f")} for p in perechi]


def _fara_subiect(p: dict[str, Any], valoare: str = "") -> str:
    """Întrebarea fără subiect și fără valoare, ca verificarea (i) să se uite doar la tipul întrebării."""
    q = p["intrebare"].replace(_subiect(p["x"]), " ").replace(p["x"], " ")
    return q.replace(valoare, " ") if valoare else q


def verificari_tipuri_noi(antrenare: list[dict[str, Any]], noi: list[dict[str, Any]]) -> dict[str, Any]:
    """Ce cere S11 la 3.(i)–(iii), plus perechile-soră: (i) câte șabloane și câte întrebări noi (fără subiect și valoare)
    au un tip din S4 (b); (ii) câte întrebări de antrenare încep cu primele 4 cuvinte ale unei întrebări din S4; (iii) câte
    texte din examenul nopții 10 sau din S4 au ajuns în antrenare. Toate trebuie 0."""
    sabloane = sum(TIPURI_NOI.values(), []) + sum(DA_NU_NOI.values(), [])
    interzise = inceputuri_interzise()
    v = verificari(antrenare)
    da_nu_grup = {p["grup"] for p in antrenare if p["tip"].startswith("da_nu")}
    deschise_grup = {p["grup"] for p in antrenare if p["fel"] == "text" and not p["tip"].startswith("da_nu")}
    da_nu_nou = {p["grup"] for p in noi if p["tip"].startswith("da_nu")}
    deschise_nou = {p["grup"] for p in noi if p["fel"] == "text" and not p["tip"].startswith("da_nu")}
    return {
        "i_sabloane_cu_tip_din_S4b": [s for s in sabloane if INTERZISE_S4_B.search(s.format(x="", f="", v=""))],
        "i_intrebari_noi_cu_tip_din_S4b": sum(bool(INTERZISE_S4_B.search(_fara_subiect(p))) for p in noi),
        "ii_sabloane_noi_cu_inceput_din_S4": [s for s in sabloane if _inceput(s.format(x="Xyz", f="fondat", v="1950"))
                                              in interzise],
        "ii_inceputuri_din_S4": v["inceputuri_din_S4"], "ii_inceputuri_din_S4_pe_fel": v["inceputuri_din_S4_pe_fel"],
        "iii_texte_din_examene": v["texte_din_examene"],
        "texte_cu_da_nu_si_intrebare_deschisa": len(da_nu_grup & deschise_grup),
        "texte_cu_da_nu": len(da_nu_grup),
        "texte_cu_da_nu_si_intrebare_deschisa_tipuri_noi": len(da_nu_nou & deschise_nou),
        "texte_cu_da_nu_tipuri_noi": len(da_nu_nou),
        "da_nu_tipuri_noi": dict(Counter(p["raspuns"] for p in noi if p["tip"].startswith("da_nu"))),
        "perechi_tipuri_noi": len(noi), "perechi_tipuri_noi_pe_fel": dict(Counter(p["fel"] for p in noi)),
        "perechi_tipuri_noi_pe_tip": dict(Counter(p["tip"] for p in noi)),
        "formulari_pe_tip_nou": {t: len(f) for t, f in TIPURI_NOI.items()},
    }


def text_din(articol: str) -> str:
    """Primul paragraf, cu spațiile strânse (parantezele rămân: din ele vin anii de naștere și de moarte), până la
    prima propoziție ruptă de curățarea Wikimedia („Are o populație de locuitori.”); parantezele rupte ies întregi."""
    from unelte.conversatie_wikipedia import _PROPOZITII, _RUPT, propozitie_rupta

    paragraf = _PARANTEZA_RUPTA.sub("", " ".join(articol.strip().split("\n", 1)[0].split()))
    bune: list[str] = []
    for p in _PROPOZITII.split(paragraf):
        if propozitie_rupta(p) or _RUPT.search(p) or not p.endswith((".", "!", "?")):
            break
        bune.append(p)
    return " ".join(bune)


def intrebari_din_text(text: str, x: str, tip: str, prima: str, definitie: str) -> list[dict[str, str]]:
    """Întrebările al căror răspuns e în text, cuvânt cu cuvânt (în afară de „În județul”, „În”, „Din” din față)."""
    fara_paranteze = _PARANTEZA.sub("", text)
    q: list[dict[str, str]] = [{"tip": "definitie", "intrebare": definitie, "raspuns": prima}]
    if tip == "loc":
        if (m := _JUDET.search(fara_paranteze)) and m.group(1) != x:
            q.append({"tip": "judet", "intrebare": f"În ce județ se află {x}?", "raspuns": f"În județul {m.group(1)}."})
        if (m := _COMUNA.search(fara_paranteze)) and m.group(1) != x:
            q.append({"tip": "comuna", "intrebare": f"În ce comună se află {x}?", "raspuns": f"În comuna {m.group(1)}."})
        if m := _LOCUITORI.search(fara_paranteze):
            q.append({"tip": "locuitori", "intrebare": f"Câți locuitori are {x}?", "raspuns": f"{m.group(0)}."})
        if (m := _DISTANTA.search(fara_paranteze)) and m.group(2) != x:
            q.append({"tip": "distanta", "intrebare": f"La ce distanță de {m.group(2)} se află {x}?",
                      "raspuns": f"La {m.group(1)}."})
    if tip in ("loc", "ce"):
        if (m := _REGIUNE.search(fara_paranteze)) and m.group(1) != x:
            q.append({"tip": "regiune", "intrebare": f"În ce regiune se află {x}?", "raspuns": f"În regiunea {m.group(1)}."})
        if (m := _CAPITALA.search(fara_paranteze)) and m.group(1) != x:
            q.append({"tip": "capitala", "intrebare": f"Ce capitală are {x}?", "raspuns": f"{m.group(1)}."})
        if m := _SUPRAFATA.search(fara_paranteze):
            q.append({"tip": "suprafata", "intrebare": f"Ce suprafață are {x}?", "raspuns": f"{m.group(1)}."})
    if tip == "om":
        if m := _NASCUT.search(text):
            q.append({"tip": "nascut", "intrebare": f"În ce an s-a născut {x}?", "raspuns": f"În {m.group(1)}."})
        if (m := _MURIT.search(text)) and "(n." in text:
            q.append({"tip": "murit", "intrebare": f"În ce an a murit {x}?", "raspuns": f"În {m.group(1)}."})
    if tip == "ce":
        for nume, (sablon, intrebare) in _FACUT_DE.items():
            if (m := sablon.search(fara_paranteze)) and x not in m.group(1):
                q.append({"tip": nume, "intrebare": intrebare.format(x=x), "raspuns": f"{m.group(1)}."})
        if m := _OPERA.search(fara_paranteze):
            q.append({"tip": "an", "intrebare": f"Din ce an este {x}?", "raspuns": f"Din {m.group(1)}."})
    return q


def lipsa_din_text(text: str, x: str, tip: str) -> list[dict[str, str]]:
    """Întrebări despre același X, cu un lucru care sigur nu e în text (răspunsul: „Nu scrie în text.”)."""
    mic = text.lower()
    are_an = re.search(_AN, text) is not None
    q: list[tuple[str, str]] = []
    if tip == "om":
        if not are_an and "născut" not in mic and "(n." not in mic:
            q.append(("nascut", f"În ce an s-a născut {x}?"))
        if not re.search(r"\b(murit|decedat|decedată|d\.)", mic):
            if " a fost " in f" {mic} ":  # doar la cei care nu mai trăiesc
                q.append(("murit_unde", f"Unde a murit {x}?"))
        if not re.search(r"\b(fiul|fiica|tatăl|mama|părinț|soți|soția|soțul|căsător)", mic):
            q.append(("parinti", f"Cine au fost părinții lui {x}?"))
    if tip == "loc":
        if "locuitor" not in mic and "populați" not in mic:
            q.append(("locuitori", f"Câți locuitori are {x}?"))
        if "altitudin" not in mic and not re.search(r"\d m\b", mic):
            q.append(("altitudine", f"La ce altitudine se află {x}?"))
        if not are_an and "atestat" not in mic:
            q.append(("atestat", f"În ce an a fost atestat documentar {x}?"))
    if tip == "ce":
        if re.search(r"\bfilm\b", mic) and "regizat" not in mic and "regia" not in mic and "regizor" not in mic:
            q.append(("regizat", f"Cine a regizat {x}?"))
        if not re.search(r"\b(fondat|înființat|creat|fondator|inventat|construit|scris|realizat|dezvoltat)", mic):
            q.append(("fondat", f"Cine a creat {x}?"))
        if not are_an:
            q.append(("an", f"În ce an a apărut {x}?"))
    return [{"tip": f"lipsa_{t}", "intrebare": i, "raspuns": NU_SCRIE} for t, i in q]


def articole_bune(cale: Path, interzise: set[str], cunoscute: Any, exceptii: Any, min_text: int, max_text: int,
                  cate: int, motive: Counter[str], rng: random.Random, din_fiecare: int = 2) -> list[dict[str, Any]]:
    """Cel mult `cate` articole cu început curat, alese la întâmplare din tot fișierul (nu doar de la început, unde
    sunt mai ales sate): întâi un articol din `din_fiecare` (ales la întâmplare), apoi filtrele scumpe."""
    from unelte.conversatie_wikipedia import articole, pereche_din
    from unelte.genereaza_conversatie import bucati, normalizat
    from unelte.ortografie_ro import necunoscute

    candidati: list[dict[str, Any]] = []
    for articol in articole(cale):
        if rng.randrange(din_fiecare):
            continue
        p = pereche_din(articol)
        if p is None:
            motive["început necurat"] += 1
            continue
        text = text_din(articol)
        if (not min_text <= len(text) <= max_text or not text.startswith(p["raspuns"].split()[0])
                or _STRAINE.search(text)):
            motive["textul prea scurt, prea lung sau rupt"] += 1
            continue
        candidati.append({"x": p["x"], "tip": p["tip"], "text": text, "prima": p["raspuns"], "definitie": p["intrebare"]})
    rng.shuffle(candidati)
    bune: list[dict[str, Any]] = []
    vazute: set[str] = set()
    for a in candidati:
        if len(bune) >= cate:
            break
        if normalizat(a["x"]) in vazute:
            motive["subiect repetat"] += 1
            continue
        if bucati(a["text"]) & interzise:
            motive["bucată dintr-un examen sau dintr-o validare"] += 1
            continue
        if necunoscute(a["text"], cunoscute, exceptii):
            motive["cuvânt necunoscut"] += 1
            continue
        vazute.add(normalizat(a["x"]))
        bune.append(a)
    return bune


def perechi_pentru(articole_: list[dict[str, Any]], fara: float, rng: random.Random, prefix: str,
                   definitii: float = 0.5, formulari: random.Random | None = None,
                   da_nu: float = 0.15) -> list[dict[str, Any]]:
    """Întrebările „text” ale articolelor („Ce este X?” cel mult `definitii` din ele, ca modelul să nu învețe doar să
    copieze prima propoziție), plus cam `fara` din total „nu_scrie” (jumătate același subiect, jumătate alt subiect).
    Cu `formulari` (întâmplarea lor): formulări diferite (FORMULARI) și cam `da_nu` din total perechi da/nu."""
    pozitive: list[dict[str, Any]] = []
    defs: list[dict[str, Any]] = []
    lipsa: list[dict[str, Any]] = []
    for i, a in enumerate(articole_):
        grup = f"{prefix}_{i}"
        for q in intrebari_din_text(a["text"], a["x"], a["tip"], a["prima"], a["definitie"]):
            (defs if q["tip"] == "definitie" else pozitive).append(
                {"fel": "text", "limba": "ro", "grup": grup, "text": a["text"], **q, "x": a["x"]})
    rng.shuffle(defs)
    if formulari is not None:
        pozitive += da_nu_pentru(pozitive, round(da_nu / (1 - da_nu - fara) * (len(pozitive) + min(
            len(defs), round(definitii / (1 - definitii) * len(pozitive))))), formulari)
    pozitive += defs[: round(definitii / (1 - definitii) * len([p for p in pozitive if not p["tip"].startswith("da_nu")]))]
    for i, a in enumerate(articole_):
        grup = f"{prefix}_{i}"
        for q in lipsa_din_text(a["text"], a["x"], a["tip"]):
            lipsa.append({"fel": "nu_scrie", "limba": "ro", "grup": grup, "text": a["text"], **q, "x": a["x"]})
    cate_fara = round(fara / (1 - fara) * len(pozitive))
    rng.shuffle(lipsa)
    alese = lipsa[: cate_fara // 2]
    while len(alese) < cate_fara:  # alt subiect: întrebarea „Ce este Y?” a altui articol, cu textul lui X
        a, b = rng.sample(range(len(articole_)), 2)
        if articole_[b]["x"].lower() in articole_[a]["text"].lower():
            continue
        alese.append({"fel": "nu_scrie", "limba": "ro", "grup": f"{prefix}_{a}", "text": articole_[a]["text"],
                      "tip": "alt_subiect", "intrebare": articole_[b]["definitie"], "raspuns": NU_SCRIE})
    perechi = pozitive + alese
    if formulari is not None:
        perechi = [reformuleaza(p, formulari) for p in perechi]
    return [{k: v for k, v in p.items() if k != "x"} for p in perechi]


def examenul(articole_: list[dict[str, Any]], cate_text: int, cate_fara: int, rng: random.Random
             ) -> list[dict[str, Any]]:
    """O întrebare pe articol: `cate_text` „text” (jumătate „Ce este X?”, jumătate celelalte șabloane, cât se poate) și
    `cate_fara` „nu_scrie” (jumătate același subiect, jumătate alt subiect)."""
    ordine = list(range(len(articole_)))
    rng.shuffle(ordine)
    folosite: set[int] = set()
    def_, alte, lipsa, alt_subiect = [], [], [], []
    for i in ordine:
        a = articole_[i]
        q = intrebari_din_text(a["text"], a["x"], a["tip"], a["prima"], a["definitie"])
        if len(alte) < cate_text - cate_text // 2 and len(q) > 1:
            alte.append((i, rng.choice(q[1:])))
        elif len(def_) < cate_text // 2:
            def_.append((i, q[0]))
        elif len(lipsa) < cate_fara // 2 and (l := lipsa_din_text(a["text"], a["x"], a["tip"])):
            lipsa.append((i, rng.choice(l)))
        elif len(alt_subiect) < cate_fara - cate_fara // 2:
            alt_subiect.append((i, None))
        else:
            continue
        folosite.add(i)
    if len(def_) + len(alte) < cate_text:  # prea puține cu alte șabloane: restul, „Ce este X?”
        for i in ordine:
            if i not in folosite and len(def_) + len(alte) < cate_text:
                def_.append((i, intrebari_din_text(**_args(articole_[i]))[0]))
                folosite.add(i)
    rest = [i for i in ordine if i not in folosite]
    examen = [{"fel": "text", "limba": "ro", "text": articole_[i]["text"], **q} for i, q in def_ + alte]
    examen += [{"fel": "nu_scrie", "limba": "ro", "text": articole_[i]["text"], **q} for i, q in lipsa]
    for (i, _), j in zip(alt_subiect, rest):
        examen.append({"fel": "nu_scrie", "limba": "ro", "text": articole_[i]["text"], "tip": "alt_subiect",
                       "intrebare": articole_[j]["definitie"], "raspuns": NU_SCRIE})
    return examen


def _args(a: dict[str, Any]) -> dict[str, str]:
    return {"text": a["text"], "x": a["x"], "tip": a["tip"], "prima": a["prima"], "definitie": a["definitie"]}


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="„Răspuns din text”: perechi Text / Întrebare / Răspuns din Wikipedia.")
    parser.add_argument("--articole", type=int, default=6000, help="atâtea articole pentru antrenare")
    parser.add_argument("--fara", type=float, default=0.2, help="partea „Nu scrie în text.” din perechile cu text")
    parser.add_argument("--min-text", type=int, default=150)
    parser.add_argument("--max-text", type=int, default=700)
    parser.add_argument("--examen-text", type=int, default=50)
    parser.add_argument("--examen-fara", type=int, default=20)
    parser.add_argument("--conversatie-ori", type=int, default=5)
    parser.add_argument("--samanta", type=int, default=1019)
    parser.add_argument("--dosar", default=DOSAR)
    parser.add_argument("--formulari", action="store_true", help="formulări diferite și da/nu la antrenare (S6)")
    parser.add_argument("--da-nu", type=float, default=0.15, help="cu --formulari: partea da/nu din perechile cu text")
    parser.add_argument("--tipuri-noi", action="store_true", help="tipuri noi de întrebări, peste celelalte (S11)")
    args = parser.parse_args(argv)

    from unelte.conversatie_wikipedia import SURSA
    from unelte.genereaza_conversatie import bucati_interzise, normalizat
    from unelte.ortografie_ro import citeste_exceptii, citeste_lista

    rng = random.Random(args.samanta)
    motive: Counter[str] = Counter()
    rezerva = 4 * (args.examen_text + args.examen_fara)
    bune = articole_bune(RADACINA / SURSA, bucati_interzise(), citeste_lista(), citeste_exceptii(), args.min_text,
                         args.max_text, args.articole + rezerva, motive, rng)
    rng.shuffle(bune)
    de_examen, de_antrenare = bune[:rezerva], bune[rezerva:]
    examen = examenul(de_examen, args.examen_text, args.examen_fara, rng)
    scrise = json.loads((RADACINA / SCRISE_DE_MANA).read_text(encoding="utf-8"))
    examen += [{"fel": "conversatie", "limba": c["limba"], "tip": "conversatie", "intrebare": c["intrebare"],
                "raspuns": c["raspuns"]} for c in scrise["conversatie"]]
    for k, p in enumerate(examen):
        p["grup"] = f"examen_{k}"

    antrenare = perechi_pentru(de_antrenare, args.fara, rng, "text",
                               formulari=random.Random(args.samanta + 1) if args.formulari else None, da_nu=args.da_nu)
    noi: list[dict[str, Any]] = []
    if args.tipuri_noi:
        noi = perechi_noi(de_antrenare, args.fara, args.da_nu, random.Random(args.samanta + 2), "text")
        antrenare += [{k: v for k, v in p.items() if k != "x"} for p in noi]
    simple =json.loads((RADACINA / CONVERSATIE).read_text(encoding="utf-8"))["perechi"]
    la_examen = {normalizat(p["intrebare"]) for p in examen}
    simple = [p for p in simple if normalizat(p["intrebare"]) not in la_examen]
    for k in range(args.conversatie_ori):
        antrenare += [{"fel": "conversatie", "limba": p["limba"], "tip": "conversatie", "grup": f"conv_{i}",
                       "intrebare": p["intrebare"], "raspuns": p["raspuns"]} for i, p in enumerate(simple)]
    rng.shuffle(antrenare)
    texte_examen = {p["text"] for p in examen if "text" in p}
    assert not any(p.get("text") in texte_examen for p in antrenare), "un text de examen a ajuns în antrenare"

    dosar = RADACINA / args.dosar
    dosar.mkdir(parents=True, exist_ok=True)
    with (dosar / "antrenare.jsonl").open("w", encoding="utf-8") as f:
        for p in antrenare:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    (dosar / "examen.json").write_text(json.dumps({"perechi": examen}, ensure_ascii=False, indent=1), encoding="utf-8")
    info = {"facut": "unelte/conversatie_text.py", "argumente": vars(args), "articole_antrenare": len(de_antrenare),
            "articole_examen": len(de_examen),
            "antrenare": dict(Counter(p["fel"] for p in antrenare)),
            "antrenare_pe_tip": dict(Counter(p["tip"] for p in antrenare)),
            "examen": dict(Counter(p["fel"] for p in examen)), "examen_pe_tip": dict(Counter(p["tip"] for p in examen)),
            "conversatie_simpla": len(simple), "scoase": dict(motive), "sursa": "wikipedia_ro (CC BY-SA 4.0)"}
    if args.formulari:
        info["verificari"] = verificari(antrenare)
    if args.tipuri_noi:
        info["verificari_tipuri_noi"] = verificari_tipuri_noi(antrenare, noi)
        with (dosar / "tipuri_noi.jsonl").open("w", encoding="utf-8") as f:
            for p in noi:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
    (dosar / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
