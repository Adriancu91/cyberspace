"""S109 (C-119 E1, 13 nov 2026): perechi „răspuns din text” pentru cele 13 tipuri (b2) ale examenului S15, pe care linia
lui #513 nu le-a văzut (S108), plus examenul nou ținut deoparte (`docs/conversatie/examen_tipuri_noi.json`).

Sursa: Wikipedia RO deja descărcată (`date/ws/curat/wikipedia_ro/antrenare.txt`), cu aceleași filtre ca generatorul
`unelte/conversatie_text.py` (funcțiile lui `pereche_din`, `text_din`, 150–700 litere, început curat, fără alte alfabete,
fără subiect repetat, fără bucăți din validări, fără cuvinte necunoscute) și aceleași excluderi ca S108: orice text cu o
bucată de 8 cuvinte la rând din S15, S4, `text*/examen.json`, setul ascuns S76a (și cel reformulat), examenul neutru; plus
textele deja folosite la antrenare în linia lui #513 (cele patru fișiere de conversație) nu se refolosesc.

Pașii (fiecare refuză să scrie peste un fișier care există):
    python unelte/conversatie_tipuri.py examen      → docs/conversatie/examen_tipuri_noi.json
    python unelte/conversatie_tipuri.py antrenare   → lucru/romana_raspunsuri_r2/antrenare.jsonl + info.json
`antrenare` citește examenul și scoate explicit textele și subiectele lui (și orice text cu o bucată de 8 cuvinte din el).

Răspunsul fiecărei perechi: „cheia” (valoarea din răspuns) trebuie să apară întocmai în text, altfel perechea se aruncă.
NU schimbă `unelte/conversatie_text.py`; doar îi importă funcțiile.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.conversatie_text import _MARE_LAT, _PARANTEZA, _STRAINE, NU_SCRIE, text_din  # noqa: E402

SAMANTA = 109
PLAFON_PE_TIP = 1000
FRACTIE_NU_SCRIE = 0.10
EXAMEN = "docs/conversatie/examen_tipuri_noi.json"
DOSAR_ANTRENARE = "lucru/romana_raspunsuri_r2"
VECHI = "lucru/romana_raspunsuri/antrenare.jsonl"
# fișierele de conversație ale liniei lui #513 (din jurnalul Kronos, S108): textele lor nu se refolosesc
LANT = ["date/conversatie/text/antrenare.jsonl", "date/conversatie/text_v2/antrenare.jsonl",
        "date/conversatie/text_v3/antrenare.jsonl", VECHI]
EXAMENE_VECHI = ["docs/conversatie/examen_generalizare_mare.json", "docs/conversatie/examen_generalizare_401.json",
                 "date/conversatie/text/examen.json", "date/conversatie/text_v2/examen.json",
                 "date/conversatie/text_v3/examen.json"]
ASCUNSE = ["lucru/romana_raspunsuri/ascuns.jsonl", "lucru/romana_raspunsuri/ascuns_reformulat.jsonl"]

TIPURI_B2 = ["actori", "canal", "castigator", "functie", "oras", "personaj", "pictor", "premiu", "producator",
             "profesie", "sot", "tara", "post"]

_MIC = r"[a-zăâîșț-]+"
_NUME = rf"{_MARE_LAT}(?: (?:(?:von|van|de|der|du|da|la|del|della|di|dos|y) )?{_MARE_LAT}){{1,3}}"  # 2–4 cuvinte
_ORG = rf"{_MARE_LAT}(?:[ -](?:(?:of|de|and|&|the|for|du|des) )?{_MARE_LAT}){{0,4}}"
TARI = ("România|Republica Moldova|Ucraina|Rusia|Franța|Germania|Italia|Spania|Portugalia|Grecia|Turcia|Bulgaria|"
        "Serbia|Ungaria|Austria|Elveția|Olanda|Țările de Jos|Belgia|Polonia|Cehia|Slovacia|Croația|Slovenia|Bosnia și "
        "Herțegovina|Muntenegru|Albania|Macedonia de Nord|Suedia|Norvegia|Finlanda|Danemarca|Islanda|Irlanda|"
        "Regatul Unit|Marea Britanie|Anglia|Scoția|Țara Galilor|Statele Unite ale Americii|Statele Unite|SUA|Canada|Mexic|"
        "Brazilia|Argentina|Chile|Peru|Columbia|Venezuela|Cuba|China|Japonia|Coreea de Sud|Coreea de Nord|India|Pakistan|"
        "Iran|Irak|Israel|Egipt|Maroc|Algeria|Tunisia|Nigeria|Africa de Sud|Kenya|Etiopia|Australia|Noua Zeelandă|"
        "Indonezia|Filipine|Vietnam|Thailanda|Belarus|Lituania|Letonia|Estonia|Armenia|Azerbaidjan|Kazahstan|"
        "Uzbekistan|Luxemburg|Liechtenstein|Monaco|Malta|Cipru|Arabia Saudită|Siria|Liban|Iordania|Afganistan|"
        "Bangladesh|Nepal|Mongolia|Bolivia|Ecuador|Uruguay|Paraguay|Ghana|Senegal|Camerun|Angola|Mozambic|Madagascar|"
        "Tanzania")
_TARA = re.compile(rf"\b(?:din|în) (?:țara )?({TARI})\b(?! de )")
_TOATE_TARILE = re.compile(rf"\b({TARI})\b")
# la subiectele „ce”: doar lucrurile care stau undeva (nu oamenii clasați greșit, nu organizațiile „din Statele Unite”)
_E_LOC = re.compile(r"\b(?:comun|oraș|sat|localitat|munte|munți|râu|lac|insul|parc|pod|palat|catedral|biseric|mănăstir|"
                    r"castel|muze|stadion|aeroport|peșter|cetat|templ|monument|clădir|regiun|provinci|district|comitat|"
                    r"departament|universitat|școal|liceu|club|cartier|zon|rezervați|port|gar[aă]|piaț|strad|bulevard|"
                    r"cascad|vulcan|deal|vârf|câmpi|golf|peninsul|arhipelag|mină|baraj|far|hotel|teatru|sală|arenă)")
_ORAS_NUME = rf"{_MARE_LAT}(?:[- ](?:de |pe |la )?{_MARE_LAT}){{0,2}}"
_SEDIU = re.compile(rf"\bsediul (?:central |principal |social )?(?:se află |este |își are |e |în )?(?:în|la) "
                    rf"(?:orașul |municipiul )?({_ORAS_NUME})")
_IN_ORAS = re.compile(rf"\b(?:din|în) (?:orașul|municipiul) ({_ORAS_NUME})")
_MEDALIE = re.compile(r"\b(?:câștigat|obținut|cucerit|câștigă|obține|cucerește)\w* (?:și )?(medalia de (?:aur|argint|bronz))\b")
_PREMIU = re.compile(r"\b(?:câștigat|obținut|primit|câștigă|obține|primește)\w* (?:și )?((?:[Pp]remiul|[Tt]rofeul) "
                     r"[^,.;()]{2,60}?)(?= la | în | pentru | cu | din | al | acordat|[,.;]|$)")
_ACTORI = re.compile(r"(?:[Rr]olurile principale (?:au fost |sunt )?(?:interpretate|jucate) de(?: către)?(?: actorii| actori)?"
                     r"|[Îî]n rolurile principale(?: (?:joacă|apar|au jucat|i-au avut pe|îi are pe))?(?: actorii)?"
                     r"|[Cc]u actorii|[Ii]nterpretat\w* de actorii|[Îî]n distribuție (?:se află |apar |sunt )?(?:actorii )?)"
                     r" ([^.;()]+)")
_PROF_FRAZA = re.compile(r"\b(este|era|a fost) (?:un|o) (?:(?:fost|fostă|celebru|celebră|renumit|renumită|mare|cunoscut|"
                         r"cunoscută|important|importantă) )?([\wăâîșț-]+)(?: și ([\wăâîșț-]+))?")
_POSTURI = ("fundaș central|fundaș stânga|fundaș dreapta|fundaș|portar|mijlocaș|atacant|extremă|inter|vârf|pivot|"
            "coordonator|intermediar|aripă|libero|centru|conducător de joc")
_POST = re.compile(rf"\b(joacă|evoluează|juca|evolua|a jucat|a evoluat|activează|activa|a activat) (?:pe (?:postul|poziția) "
                   rf"de|ca|pe post de) ((?:{_POSTURI})(?: (?:central|centrală|dreapta|stânga|defensiv|ofensiv|lateral|"
                   rf"de bandă|de margine))?)\b")
_E_PICTURA = re.compile(r"\b(?:pictur|tablou|portret|frescă|acuarel)")
_PICTOR = re.compile(rf"\b(?:pictat\w*|realizat\w*|executat\w*|creat\w*) de (?:către )?(?:(?:pictorul|artistul|pictorița) "
                     rf"(?:{_MIC} ){{0,2}})?({_NUME})|\b(?:pictur[ăa]|tablou\w*|portret\w*|frescă) (?:[^.]{{0,60}}? )?"
                     rf"(?:a|al) (?:pictorului |artistului )(?:{_MIC} ){{0,2}}({_NUME})|\bde pictorul (?:{_MIC} ){{0,2}}"
                     rf"({_NUME})")
_PRODUS = re.compile(rf"\bprodus\w* de (?:către )?(?:(?:compania|studioul|studiourile|casa de producție|casa de discuri|"
                     rf"firma|producătorul|producătoarea) )?({_ORG})")
_FUNCTII = ("prim-ministru|prim-ministrul|ministru|ministrul|președinte|președintele|primar|primarul|guvernator|"
            "guvernatorul|ambasador|ambasadorul|prefect|prefectul|rector|rectorul|cancelar|cancelarul|vicepreședinte|"
            "vicepreședintele|premier|director|directorul|secretar general|secretarul general|consul|consulul")
_FUNCTIE = re.compile(rf"\b(a fost|este|era|a deținut funcția de|a ocupat funcția de|a îndeplinit funcția de|"
                      rf"deține funcția de|ocupă funcția de|a ocupat postul de|a servit ca) (?:în funcția de |ca )?"
                      rf"((?:{_FUNCTII})\b[^,.;()]{{3,80}}?)(?= în (?:perioada |anii |anul |timpul )?\d| între \d| din \d|"
                      rf" până | sub | în guvernul| în cabinetul| în mandatul|[,.;]|$)")
_E_EMISIUNE = re.compile(r"\b(?:serial|emisiun|show|desen|program|telenovel|sitcom|reality|documentar|talk)")
_CANAL = re.compile(rf"\b(?:difuzat\w*|transmis\w*|premiera|rulat\w*) (?:în premieră |inițial |original |"
                    rf"pentru prima dată )?(?:pe|de) (?:canalul |postul |rețeaua |televiziunea |postul de televiziune |"
                    rf"canalul de televiziune )?({_MARE_LAT}(?:[ -](?:{_MARE_LAT}|\d{{1,2}}\b)){{0,3}})")
_LUNI = {"Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie", "Iulie", "August", "Septembrie", "Octombrie",
         "Noiembrie", "Decembrie"}
_MIC_TITLU = r"(?:de|din|la|și|of|the|and|în|cu|pe|a|al|le|la)"
_ROL_FILM = re.compile(rf"\b(?:rolul|personajul) (?:lui |ei |principal al lui |principal, )?({_NUME})\b,? (?:din|în) "
                       rf"(?:serialul |filmul |filmele |sitcomul |telenovela |serialul de televiziune |producția )?"
                       rf"(?:„([^”]{{2,50}})”|([A-ZĂÂÎȘȚ0-9][^,.;()]{{1,50}}?)(?=[,.;(]| și | pentru | alături | unde |$))")
_ROL_CUNOSCUT = re.compile(rf"\b(cunoscut|cunoscută) (?:mai ales |în special |mai ales )?(?:pentru|prin) rolul "
                           rf"(?:lui |ei |său |sau )?({_NUME})")
_E_COMPETITIE = re.compile(r"\b(?:ediți|turul|cursa|campionat|cupa|competiți|turneu|maraton|grand prix|marele premiu|"
                           r"concurs|finala|sezonul)", re.IGNORECASE)
_ROLURI_CASTIG = r"(?:ciclistul|echipa|clubul|jucătorul|jucătoarea|pilotul|tenismanul|sportivul|sportiva|formația|selecționata)"
_CASTIGAT_DE = re.compile(rf"\b(?:câștigat\w*|cucerit\w*) de (?:către )?(?:{_ROLURI_CASTIG} (?:{_MIC} )?)?({_ORG})")
_CASTIGATOR = re.compile(rf"\bcâștigător(?:ul|ii)?(?: [^.]{{0,40}}?)? (?:a fost|este|au fost|e) (?:{_ROLURI_CASTIG} "
                         rf"(?:{_MIC} )?)?({_ORG})")
_SOT_NUME = rf"{_NUME}(?: (?:al |a )?[IVX]+(?:-lea)?)?"
_CASATORIT = re.compile(rf"\b(căsătorit|căsătorită|s-a căsătorit|se căsătorește) (?:(?:în |din )(?:\d{{1,2}} {_MIC} )?"
                        rf"\d{{4}},? )?cu ({_SOT_NUME})")
# doar „X a fost soția lui Y” (nu „soția sa, Y”: „sa” poate fi tatăl lui X; nici „rolul Lisei, soția lui Y”)
_SOTIA_LUI = re.compile(rf"\b(?:a fost|este|era|fiind) (?:a doua |prima )?soția (?:lui |regelui |împăratului |prințului |"
                        rf"ducelui )({_SOT_NUME})")
# propozițiile al căror subiect e X (la premiu și funcție): prima, cele care încep cu X sau cu un pronume / „A …”
_DESPRE = ("A ", "Ea ", "El ", "Acesta", "Aceasta", "Filmul", "Romanul", "Cartea", "Albumul", "Piesa", "Serialul",
           "Cântecul", "Melodia", "Lucrarea", "Jocul", "Opera", "Nuvela", "Poemul", "Între ", "Din ", "În perioada ")
_ALT_SUBIECT = re.compile(r"([A-ZĂÂÎȘȚ][\w'’-]+|\bcare|\bce) (?:a|au|și-a) (?:mai )?$")


def _in_propozitie_despre_x(rx: re.Pattern, fara: str, x: str) -> re.Match | None:
    """Prima potrivire într-o propoziție despre X, fără alt subiect cu literă mare chiar înaintea verbului („România a
    câștigat”, „O'Quinn a câștigat”)."""
    from unelte.conversatie_wikipedia import _PROPOZITII

    for k, p in enumerate(_PROPOZITII.split(fara)):
        if k and not p.startswith((x, *_DESPRE)):
            continue
        if (m := rx.search(p)) and not ((a := _ALT_SUBIECT.search(p[: m.start()])) and a.group(1) not in x.split()):
            return m
    return None

# ---------------------------------------------------------------------------------------------------------------------
# Formulările. GENERATOR = ce intră la antrenare (cel puțin 3 pe tip și pe fel). EXAMEN_NOI = formulări care NU apar în
# generator (cel puțin 1 din 3 întrebări din examenul (i) le folosește). Cheia a doua e „felul” extragerii (timp, gen…).
GENERATOR: dict[str, dict[str, list[str]]] = {
    "tara": {"": ["În ce țară se află {x}?", "{x} se află în ce țară?", "În ce țară se găsește {x}?",
                  "Care e țara în care se află {x}?"]},
    "oras": {"sediu": ["În ce oraș își are sediul {x}?", "Unde își are sediul {x}?", "{x} își are sediul în ce oraș?",
                       "În ce oraș se află sediul lui {x}?"],
             "loc": ["În ce oraș se află {x}?", "În ce oraș se găsește {x}?", "{x} se află în ce oraș?",
                     "În ce oraș e {x}?"]},
    "premiu": {"premiu": ["Ce premiu a câștigat {x}?", "Ce premiu a obținut {x}?", "Ce premiu a primit {x}?"],
               "medalie": ["Ce medalie a câștigat {x}?", "Ce medalie a obținut {x}?", "Ce medalie a cucerit {x}?"]},
    "actori": {"": ["Ce actori joacă rolurile principale în {x}?", "Cine joacă în rolurile principale din {x}?",
                    "Ce actori apar în {x}?", "Cine sunt actorii principali din {x}?"]},
    "profesie": {"prezent": ["Ce profesie are {x}?", "Cu ce se ocupă {x}?", "Ce meserie are {x}?",
                             "Care e profesia lui {x}?"],
                 "trecut": ["Ce profesie a avut {x}?", "Cu ce se ocupa {x}?", "Ce meserie a avut {x}?",
                            "Care a fost profesia lui {x}?"]},
    "post": {"prezent": ["Pe ce post joacă {x}?", "Pe ce post evoluează {x}?", "Ce post ocupă {x} în echipă?",
                         "{x} joacă pe ce post?"],
             "trecut": ["Pe ce post a jucat {x}?", "Pe ce post a evoluat {x}?", "Ce post ocupa {x} în echipă?",
                        "{x} a jucat pe ce post?"]},
    "pictor": {"": ["Cine a pictat {x}?", "Al cui tablou este {x}?", "Ce pictor a realizat {x}?",
                    "Cine e pictorul lui {x}?"]},
    "producator": {"": ["Cine a produs {x}?", "Cine e producătorul lui {x}?", "Cine s-a ocupat de producția lui {x}?",
                        "Cine a realizat producția lui {x}?"]},
    "functie": {"prezent": ["Ce funcție are {x}?", "Ce funcție ocupă {x}?", "Ce funcție îndeplinește {x}?",
                            "Care e funcția lui {x}?"],
                "trecut": ["Ce funcție a avut {x}?", "Ce funcție a ocupat {x}?", "Ce funcție a îndeplinit {x}?",
                           "Care a fost funcția lui {x}?"]},
    "canal": {"": ["Pe ce canal a avut premiera {x}?", "Pe ce canal a rulat {x}?", "Ce canal a difuzat {x}?",
                   "Pe ce post de televiziune a rulat {x}?"]},
    "personaj": {"film": ["Ce rol a interpretat {x} în {y}?", "Pe cine a jucat {x} în {y}?",
                          "Ce personaj a jucat {x} în {y}?", "Ce rol a avut {x} în {y}?"],
                 "cunoscut": ["Pentru ce rol e {c} {x}?", "Prin ce rol e {c} {x}?", "Datorită cărui rol e {c} {x}?"]},
    "castigator": {"": ["Cine a câștigat {x}?", "Cine a fost câștigătorul în {x}?", "Cine a ieșit învingător în {x}?"]},
    "sot": {"cu": ["Cu cine s-a căsătorit {x}?", "{x} s-a căsătorit cu cine?", "Cu cine s-a unit prin căsătorie {x}?"],
            "sotia_lui": ["Cu cine a fost căsătorită {x}?", "Cine a fost soțul lui {x}?", "A cui soție a fost {x}?"]},
}
EXAMEN_NOI: dict[str, dict[str, list[str]]] = {
    "tara": {"": ["Ce țară găzduiește {x}?", "În care țară se află {x}?"]},
    "oras": {"sediu": ["Care e orașul în care își are sediul {x}?", "Ce oraș găzduiește sediul lui {x}?"],
             "loc": ["Care e orașul în care se află {x}?", "Ce oraș găzduiește {x}?"]},
    "premiu": {"premiu": ["Ce distincție a primit {x}?", "Ce premiu i s-a acordat lui {x}?"],
               "medalie": ["Ce medalie i-a revenit lui {x}?", "Cu ce medalie s-a ales {x}?"]},
    "actori": {"": ["Ce interpreți are {x} în rolurile principale?", "Pe cine vedem în rolurile principale din {x}?"]},
    "profesie": {"prezent": ["Ce ocupație are {x}?", "Ce face {x} de meserie?"],
                 "trecut": ["Ce ocupație a avut {x}?", "Ce lucra {x}?"]},
    "post": {"prezent": ["Pe ce poziție joacă {x}?", "În ce poziție evoluează {x}?"],
             "trecut": ["Pe ce poziție a jucat {x}?", "În ce poziție a evoluat {x}?"]},
    "pictor": {"": ["Cărui pictor i se datorează {x}?", "Care artist e autorul lui {x}?"]},
    "producator": {"": ["Cine semnează producția lui {x}?", "Cui îi aparține producția lui {x}?"]},
    "functie": {"prezent": ["În ce funcție servește {x}?", "Ce demnitate are {x}?"],
                "trecut": ["În ce funcție a servit {x}?", "Ce demnitate a avut {x}?"]},
    "canal": {"": ["Care televiziune a transmis {x}?", "La ce televiziune a apărut {x}?"]},
    "personaj": {"film": ["Pe cine a întruchipat {x} în {y}?", "În pielea cărui personaj a intrat {x} în {y}?"],
                 "cunoscut": ["Care e rolul cel mai cunoscut al lui {x}?", "Ce rol a adus faima lui {x}?"]},
    "castigator": {"": ["Cui i-a revenit victoria în {x}?", "Cine s-a impus în {x}?"]},
    "sot": {"cu": ["Pe cine a luat în căsătorie {x}?", "Cine i-a fost partener de viață lui {x}?"],
            "sotia_lui": ["Pe cine a luat de soț {x}?", "Cine i-a fost partener de viață lui {x}?"]},
}
# „Nu scrie în text.”: întrebarea tipului despre același X, pe un text care sigur n-are informația (felul folosit)
FEL_NU_SCRIE = {"tara": "", "oras": "sediu", "premiu": "premiu", "actori": "", "post": "prezent", "pictor": "",
                "producator": "", "functie": "trecut", "canal": "", "personaj": "cunoscut", "castigator": "", "sot": "cu"}


def cap(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def _prima(fara: str) -> str:
    from unelte.conversatie_wikipedia import _PROPOZITII

    return _PROPOZITII.split(fara)[0]


def _unic(rx: re.Pattern, text: str, grup: int = 1) -> re.Match | None:
    """Potrivirea doar dacă toate potrivirile din text dau aceeași valoare (altfel răspunsul ar fi îndoielnic)."""
    toate = list(rx.finditer(text))
    if not toate or len({m.group(grup) for m in toate}) != 1:
        return None
    return toate[0]


def _lista_nume(sir: str) -> str | None:
    """„Ion Barbu, Cătălin Cenușă și Dorel Vișan în rolurile …” → „Ion Barbu, Cătălin Cenușă și Dorel Vișan” (2–6 nume,
    exact cum scrie)."""
    nume = re.compile(rf"{_NUME}")
    poz, gasite = 0, 0
    sfarsit = 0
    while gasite < 6:
        m = nume.match(sir, poz)
        if not m:
            break
        gasite += 1
        sfarsit = m.end()
        sep = re.match(r", | și |, și ", sir[sfarsit:])
        if not sep:
            break
        poz = sfarsit + sep.end()
    if gasite < 2:
        return None
    return sir[:sfarsit]


def extrage(tip: str, text: str, x: str, tip_subiect: str, verb: str = "este") -> dict[str, str] | None:
    """Răspunsul tipului `tip` din text: {"cheie", "raspuns", "fel", "y"?, "c"?} sau None. `cheie` apare întocmai în text."""
    fara = _PARANTEZA.sub("", text)
    prima = _prima(fara)
    timp = "prezent" if verb in ("este", "sunt") else "trecut"
    r: dict[str, str] | None = None
    if tip == "tara" and tip_subiect in ("loc", "ce"):
        e_loc = tip_subiect == "loc" or bool(_E_LOC.search(prima.lower()))
        if e_loc and "originar" not in prima and (m := _unic(_TARA, prima)) and len(set(_TOATE_TARILE.findall(prima))) == 1:
            r = {"cheie": m.group(1), "raspuns": f"În {m.group(1)}.", "fel": ""}
    elif tip == "oras" and tip_subiect == "ce":
        if m := _unic(_SEDIU, fara):
            r = {"cheie": m.group(1), "raspuns": f"În {m.group(1)}.", "fel": "sediu"}
        elif (m := _unic(_IN_ORAS, prima)) and not re.search(r"\b(?:satul|comuna|comunei|ieșirea|lângă)\b", prima):
            r = {"cheie": m.group(1), "raspuns": f"În {m.group(1)}.", "fel": "loc"}
        if r and _TOATE_TARILE.search(r["cheie"]):  # „cu sediul în România” nu e un oraș
            r = None
    elif tip == "premiu" and tip_subiect in ("ce", "om"):
        if fara.count("medali") == 1 and (m := _in_propozitie_despre_x(_MEDALIE, fara, x)):
            r = {"cheie": m.group(1), "raspuns": f"{cap(m.group(1))}.", "fel": "medalie"}
        elif len(re.findall(r"[Pp]remi", fara)) == 1 and (m := _in_propozitie_despre_x(_PREMIU, fara, x)) \
                and not re.search(r" (?:la|de|din|al|a|pentru)$| la ", m.group(1).strip()):
            r = {"cheie": m.group(1).strip(), "raspuns": f"{cap(m.group(1).strip())}.", "fel": "premiu"}
    elif tip == "actori" and tip_subiect == "ce":
        if (m := _ACTORI.search(fara)) and (lista := _lista_nume(m.group(1))):
            r = {"cheie": lista, "raspuns": f"{lista}.", "fel": ""}
    elif tip == "profesie" and tip_subiect == "om":
        from unelte.conversatie_wikipedia import PROFESII

        profesii = PROFESII - {"fost", "fostă"}
        if (m := _PROF_FRAZA.search(prima)) and m.group(2).lower() in profesii:
            cheie = m.group(2) + (f" și {m.group(3)}" if m.group(3) and m.group(3).lower() in profesii else "")
            r = {"cheie": cheie, "raspuns": f"{cap(cheie)}.", "fel": timp}
    elif tip == "post" and tip_subiect == "om":
        if m := _unic(_POST, fara, 2):
            fel = "prezent" if m.group(1) in ("joacă", "evoluează", "activează") else "trecut"
            r = {"cheie": m.group(2), "raspuns": f"{cap(m.group(2))}.", "fel": fel}
    elif tip == "pictor" and tip_subiect == "ce" and _E_PICTURA.search(prima.lower()):
        if m := _PICTOR.search(fara):
            nume = next(g for g in m.groups() if g)
            r = {"cheie": nume, "raspuns": f"{nume}.", "fel": ""}
    elif tip == "producator" and tip_subiect == "ce":
        if m := _unic(_PRODUS, fara):
            r = {"cheie": m.group(1), "raspuns": f"{m.group(1)}.", "fel": ""}
    elif tip == "functie" and tip_subiect == "om":
        if (m := _in_propozitie_despre_x(_FUNCTIE, fara, x)) and len(m.group(2).split()) >= 2:
            fel = "prezent" if m.group(1) in ("este", "deține funcția de", "ocupă funcția de") else "trecut"
            cheie = m.group(2).strip()
            r = {"cheie": cheie, "raspuns": f"{cap(cheie)}.", "fel": fel}
    elif tip == "canal" and tip_subiect == "ce" and _E_EMISIUNE.search(prima.lower()):
        if (m := _unic(_CANAL, fara)) and m.group(1) not in _LUNI and not _TOATE_TARILE.fullmatch(m.group(1)):
            r = {"cheie": m.group(1), "raspuns": f"Pe {m.group(1)}.", "fel": ""}
    elif tip == "personaj" and tip_subiect == "om":
        if m := _ROL_FILM.search(fara):
            titlu = (m.group(2) or m.group(3) or "").strip()
            titlu = re.sub(rf"(?: {_MIC_TITLU})+$", "", titlu)
            if titlu and titlu not in x and x not in titlu:
                r = {"cheie": m.group(1), "raspuns": f"{m.group(1)}.", "fel": "film", "y": titlu}
        if r is None and (m := _ROL_CUNOSCUT.search(fara)):
            r = {"cheie": m.group(2), "raspuns": f"{m.group(2)}.", "fel": "cunoscut", "c": m.group(1)}
    elif tip == "castigator" and tip_subiect == "ce" and _E_COMPETITIE.search(prima):
        if m := (_unic(_CASTIGAT_DE, fara) or _unic(_CASTIGATOR, fara)):
            r = {"cheie": m.group(1), "raspuns": f"{m.group(1)}.", "fel": ""}
    elif tip == "sot" and tip_subiect == "om":
        mic = fara.lower()
        if mic.count("căsători") + mic.count("soți") + mic.count("soțul") <= 1 and "recăsători" not in mic:
            if m := _CASATORIT.search(fara):
                r = {"cheie": m.group(2), "raspuns": f"Cu {m.group(2)}.", "fel": "cu"}
            elif m := _in_propozitie_despre_x(_SOTIA_LUI, fara, x):
                r = {"cheie": m.group(1), "raspuns": f"{m.group(1)}.", "fel": "sotia_lui"}
    if r is None:
        return None
    cheie = r["cheie"]
    if len(cheie) < 2 or cheie not in text or cheie in x or x in cheie:
        return None
    return r


_NU_TARA = re.compile(r"județ|raion|comitat|regiun|provinci|\bland|canton|departament|țar|stat|uniun|imperi|regat")
_NU_PREMIU = re.compile(r"premi|medali|trofe|distin|câștig|laureat|oscar|glob|nominaliz|decor|ordin|onoare|titl|campion|cucer")
_NU_ACTORI = re.compile(r"rol|actor|actriț|interpret|distribuți|joacă|jucat|vedet|star|regizat|regia|regizor")
_NU_POST = re.compile(rf"\b(?:{_POSTURI})|post|pozi")
_NU_PICTOR = re.compile(r"pictor|artist|autor|maestr|realizat|pictat|creat|lucrare a")
_NU_PRODUCATOR = re.compile(r"produ|studio|compani|casa|firm|label|realizat|regizat|regia|regizor")
_NU_FUNCTIE = re.compile(rf"\b(?:{_FUNCTII})|funcți|mandat|ales|numit|deputat|senator|consilier|lider|șef|conduc|membru")
_NU_CANAL = re.compile(r"canal|post|rețea|televiziun|difuz|premier|transmis|rulat|netflix|hbo|youtube|online")
_NU_PERSONAJ = re.compile(r"rol|personaj|interpret|jucat|joacă|apar|film|serial|teatr")
_NU_CASTIG = re.compile(r"câștig|învin|campion|cucer|victori|locul|impus|trofeu|titlu|medali|final|clasament|primul")
_NU_SOT = re.compile(r"căsător|soț|soți|văduv|nunt|partener|logodn|divorț|cuplu|iubit")


def lipseste(tip: str, text: str, x: str, tip_subiect: str) -> dict[str, str] | None:
    """Dacă textul sigur n-are informația tipului (despre X): {"fel", "c"?}; altfel None. Fără „profesie” (aproape orice
    text despre un om o spune)."""
    mic = text.lower()
    prima = _prima(text).lower()
    if tip == "tara" and tip_subiect == "loc" and not _TOATE_TARILE.search(text) and not _NU_TARA.search(mic):
        return {"fel": ""}
    if tip == "oras" and tip_subiect == "ce" and "sediu" not in mic and "oraș" not in mic and "municip" not in mic \
            and not re.search(r"\b(?:în|din|la) [A-ZĂÂÎȘȚ]", text):
        return {"fel": "sediu"}
    if tip == "premiu" and tip_subiect in ("om", "ce") and not _NU_PREMIU.search(mic):
        return {"fel": "premiu"}
    if tip == "actori" and tip_subiect == "ce" and re.search(r"\bfilm\b", prima) and not _NU_ACTORI.search(mic) \
            and not re.search(r"\bcu [A-ZĂÂÎȘȚ]", text):
        return {"fel": ""}
    if tip == "post" and tip_subiect == "om" and re.search(r"fotbalist|handbalist|jucător|jucătoare|baschetbalist|"
                                                           r"voleibalist|hocheist", prima) and not _NU_POST.search(mic):
        return {"fel": "prezent" if " este " in f" {prima} " else "trecut"}
    if tip == "pictor" and tip_subiect == "ce" and _E_PICTURA.search(prima) and not _NU_PICTOR.search(mic) \
            and not re.search(r"\b(?:de|lui|al|a) [A-ZĂÂÎȘȚ]", text):
        return {"fel": ""}
    if tip == "producator" and tip_subiect == "ce" and re.search(r"\b(?:film|album|serial|joc video|single)\b", prima) \
            and not _NU_PRODUCATOR.search(mic):
        return {"fel": ""}
    if tip == "functie" and tip_subiect == "om" and re.search(r"politician|diplomat|om politic", prima) \
            and not _NU_FUNCTIE.search(mic):
        return {"fel": "prezent" if " este " in f" {prima} " else "trecut"}
    if tip == "canal" and tip_subiect == "ce" and _E_EMISIUNE.search(prima) and not _NU_CANAL.search(mic) \
            and not re.search(r"\b[A-Z]{2,}\b", text):
        return {"fel": ""}
    if tip == "personaj" and tip_subiect == "om" and (m := re.search(r"\b(actor|actriță)\b", prima)) \
            and not _NU_PERSONAJ.search(mic):
        return {"fel": "cunoscut", "c": "cunoscută" if m.group(1) == "actriță" else "cunoscut"}
    if tip == "castigator" and tip_subiect == "ce" and _E_COMPETITIE.search(prima) and not _NU_CASTIG.search(mic):
        return {"fel": ""}
    if tip == "sot" and tip_subiect == "om" and not _NU_SOT.search(mic):
        return {"fel": "cu"}
    return None


def intrebare(tip: str, info: dict[str, str], x: str, rng: random.Random, noua: bool = False) -> str:
    sabloane = (EXAMEN_NOI if noua else GENERATOR)[tip][info["fel"]]
    q = rng.choice(sabloane).format(x=x, y=info.get("y", ""), c=info.get("c", ""))
    return cap(q)


# ---------------------------------------------------------------------------------------------------------------------
# Partea (ii) a examenului: tipuri care nu sunt nici în S15, nici în generator, nici la antrenarea liniei.
_NAT = re.compile(r"\b(este|era|a fost) (?:un|o) (?:(?:fost|fostă|celebru|celebră|renumit|renumită|mare|cunoscut|"
                  r"cunoscută|important|importantă) )?([\wăâîșț-]+)(?: și [\wăâîșț-]+)? ([a-zăâîșț-]+)\b")
_CONTINENT = re.compile(r"\b(?:din|în) (Europa|Asia|Africa|America de Nord|America de Sud|America Centrală|Oceania|"
                        r"Antarctica)\b(?! de | Centrală| Mică)")
_ABSOLVIT = re.compile(r"\ba absolvit (?:cursurile )?((?:Universitatea|Facultatea|Academia|Conservatorul|Institutul|"
                       r"Colegiul|Școala|Liceul)\b[^,.;()]{3,70}?)(?=[,.;]| în (?:anul )?\d| din \d| la \d| unde | cu |$)")
_E_PUBLICATIE = re.compile(r"\b(?:ziar|revist|publicați|cotidian|săptămânal|post de radio|film|carte|roman|cântec|album|"
                           r"poezi|serial|imn|enciclopedi|dicționar)")
_LIMBA = re.compile(r"\b(?:în|de) limb(?:a|ă) ([a-zăâîșț]+)\b")
_GEN = re.compile(r"\b(?:formați|trup|grup|cântăreț|cântăreaț|muzician|compozitor|rapper|interpret|album|single|cântec)"
                  r"\w* (?:[a-zăâîșț-]+ )?(?:de )?(?:muzică )?(rock|pop|jazz|heavy metal|punk|hip hop|hip-hop|folk|blues|"
                  r"country|reggae|soul|funk|disco|techno|trance|manele|muzică populară|muzică ușoară|gospel|indie)\b")
_INSTRUMENT = re.compile(r"\bcânt(?:ă|a|at|ând) (?:\w+ )?la (pian|vioară|chitară bas|chitară|violoncel|orgă|flaut|tobe|"
                         r"saxofon|trompetă|clarinet|nai|țambal|acordeon|harpă|contrabas|oboi|fagot|trombon|baterie)\b")
_SPORT = re.compile(r"\b(?:jucător|jucătoare|campion|campioană|sportiv|sportivă|antrenor|antrenoare)(?: [a-zăâîșț-]+)? de "
                    r"(tenis de masă|tenis|fotbal|handbal|baschet|volei|șah|polo pe apă|rugby|hochei pe gheață|hochei|"
                    r"golf|badminton|snooker|biliard|squash|baseball|cricket|bowling|darts)\b")
TIPURI_II = ["nationalitate", "continent", "absolvit", "limba", "gen_muzical", "instrument", "sport"]
FORMULARI_II = {"nationalitate": {"prezent": "Ce naționalitate are {x}?", "trecut": "Ce naționalitate a avut {x}?"},
                "continent": {"": "Pe ce continent se află {x}?"},
                "absolvit": {"": "Ce instituție a absolvit {x}?"},
                "limba": {"": "În ce limbă este {x}?"},
                "gen_muzical": {"": "Ce gen de muzică face {x}?"},
                "instrument": {"": "La ce instrument cântă {x}?"},
                "sport": {"": "Ce sport practică {x}?"}}


def extrage_ii(tip: str, text: str, x: str, tip_subiect: str, verb: str = "este") -> dict[str, str] | None:
    from unelte.conversatie_wikipedia import NATIONALITATI, PROFESII

    fara = _PARANTEZA.sub("", text)
    prima = _prima(fara)
    r = None
    if tip == "nationalitate" and tip_subiect == "om":
        if (m := _NAT.search(prima)) and m.group(2).lower() in PROFESII - {"fost", "fostă"} \
                and m.group(3).startswith(NATIONALITATI) and not m.group(3).endswith(("esc", "ească", "ești")):
            r = {"cheie": m.group(3), "raspuns": f"{cap(m.group(3))}.",
                 "fel": "prezent" if verb in ("este", "sunt") else "trecut"}
    elif tip == "continent" and (tip_subiect == "loc" or (tip_subiect == "ce" and _E_LOC.search(prima.lower()))):
        if m := _unic(_CONTINENT, prima):
            r = {"cheie": m.group(1), "raspuns": f"În {m.group(1)}.", "fel": ""}
    elif tip == "absolvit" and tip_subiect == "om":
        if fara.count("absolvit") == 1 and (m := _ABSOLVIT.search(fara)):
            r = {"cheie": m.group(1).strip(), "raspuns": f"{m.group(1).strip()}.", "fel": ""}
    elif tip == "limba" and tip_subiect == "ce" and _E_PUBLICATIE.search(prima.lower()):
        if (m := _unic(_LIMBA, prima)) and len(set(_LIMBA.findall(fara))) == 1 and not re.search(
                r"\b(?:tradus|dublat|traducere)", fara):
            r = {"cheie": m.group(1), "raspuns": f"În limba {m.group(1)}.", "fel": ""}
    elif tip == "gen_muzical" and tip_subiect in ("om", "ce"):
        if m := _unic(_GEN, prima):
            r = {"cheie": m.group(1), "raspuns": f"{cap(m.group(1))}.", "fel": ""}
    elif tip == "instrument" and tip_subiect == "om":
        if m := _unic(_INSTRUMENT, fara):
            r = {"cheie": m.group(1), "raspuns": f"La {m.group(1)}.", "fel": ""}
    elif tip == "sport" and tip_subiect == "om":
        if m := _unic(_SPORT, prima):
            r = {"cheie": m.group(1), "raspuns": f"{cap(m.group(1))}.", "fel": ""}
    if r is None or r["cheie"] not in text or r["cheie"] in x or x in r["cheie"]:
        return None
    return r


# ---------------------------------------------------------------------------------------------------------------------
def sha(cale: Path) -> str:
    h = hashlib.sha256()
    with cale.open("rb") as f:
        while b := f.read(2**20):
            h.update(b)
    return h.hexdigest()


def _texte_din(obiect: Any) -> list[str]:
    if isinstance(obiect, dict):
        return [t for v in obiect.values() for t in _texte_din(v)]
    if isinstance(obiect, list):
        return [t for v in obiect for t in _texte_din(v)]
    return [obiect] if isinstance(obiect, str) and len(obiect.split()) >= 8 else []


def bucati_examene(radacina: Path = RADACINA) -> set[str]:
    """Bucățile de 8 cuvinte din examenele vechi (S15, S4, text*/examen.json), seturile ascunse S76a și examenul neutru."""
    from unelte.genereaza_conversatie import bucati

    toate: set[str] = set()
    for c in EXAMENE_VECHI:
        toate |= {b for t in _texte_din(json.loads((radacina / c).read_text(encoding="utf-8"))) for b in bucati(t)}
    for c in ASCUNSE:
        for rand in (radacina / c).read_text(encoding="utf-8").splitlines():
            if rand.strip():
                toate |= bucati(json.loads(rand).get("text", "") or "")
    for c in sorted((radacina / "date/neutru").glob("*/validare.txt")):
        toate |= bucati(c.read_text(encoding="utf-8"))
    return toate


def texte_folosite(radacina: Path = RADACINA) -> set[str]:
    folosite: set[str] = set()
    for c in LANT:
        for rand in (radacina / c).read_text(encoding="utf-8").splitlines():
            if rand.strip() and (t := json.loads(rand).get("text")):
                folosite.add(t)
    return folosite


def candidati(motive: Counter, radacina: Path = RADACINA) -> list[dict[str, Any]]:
    """Articolele bune din Wikipedia descărcată (filtrele generatorului + excluderile S108), în ordinea din fișier."""
    from unelte.conversatie_wikipedia import SURSA, articole, pereche_din
    from unelte.genereaza_conversatie import bucati, bucati_interzise, normalizat
    from unelte.ortografie_ro import citeste_exceptii, citeste_lista, necunoscute

    interzise = bucati_interzise()
    examene = bucati_examene(radacina)
    folosite = texte_folosite(radacina)
    s15 = {p["text"] for p in json.loads((radacina / EXAMENE_VECHI[0]).read_text(encoding="utf-8"))["perechi"]}
    cunoscute, exceptii = citeste_lista(), citeste_exceptii()
    vazute: set[str] = set()
    bune: list[dict[str, Any]] = []
    for articol in articole(radacina / SURSA):
        p = pereche_din(articol)
        if p is None:
            motive["început necurat"] += 1
            continue
        text = text_din(articol)
        if not 150 <= len(text) <= 700 or not text.startswith(p["raspuns"].split()[0]) or _STRAINE.search(text):
            motive["textul prea scurt, prea lung sau rupt"] += 1
            continue
        if normalizat(p["x"]) in vazute:
            motive["subiect repetat"] += 1
            continue
        b = bucati(text)
        if b & interzise:
            motive["bucată dintr-o validare (regula generatorului)"] += 1
            continue
        if b & examene or text in s15:
            motive["bucată dintr-un examen S15/S4/text*/S76a/neutru"] += 1
            continue
        if text in folosite:
            motive["text deja folosit la antrenare în linia lui #513"] += 1
            continue
        if necunoscute(text, cunoscute, exceptii):
            motive["cuvânt necunoscut"] += 1
            continue
        vazute.add(normalizat(p["x"]))
        motive["bune"] += 1
        bune.append({"x": p["x"], "tip": p["tip"], "verb": p["verb"], "text": text})
    return bune


def construieste_examen(cand: list[dict[str, Any]], rng: random.Random, pe_tip: int = 10, total_ii: int = 50
                        ) -> dict[str, Any]:
    """(i) `pe_tip` întrebări pe fiecare tip (b2), cel puțin 1 din 3 cu formulări din EXAMEN_NOI; (ii) `total_ii`
    întrebări din tipurile TIPURI_II (cel mult `pe_tip` pe tip). Un text, o singură întrebare."""
    ordine = list(range(len(cand)))
    rng.shuffle(ordine)
    folosite: set[int] = set()
    perechi: list[dict[str, Any]] = []
    disponibile_i: dict[str, int] = {}
    for tip in TIPURI_B2:
        alese = []
        n = 0
        for i in ordine:
            a = cand[i]
            if i in folosite or (info := extrage(tip, a["text"], a["x"], a["tip"], a["verb"])) is None:
                continue
            n += 1
            if len(alese) < pe_tip:
                alese.append((i, info))
                folosite.add(i)
        disponibile_i[tip] = n
        noi = set(rng.sample(range(len(alese)), math.ceil(0.4 * len(alese)))) if alese else set()
        for k, (i, info) in enumerate(alese):
            a = cand[i]
            perechi.append({"fel": "text", "limba": "ro", "categorie": "i", "tip": tip, "text": a["text"],
                            "intrebare": intrebare(tip, info, a["x"], rng, noua=k in noi), "raspuns": info["raspuns"],
                            "cheie": [info["cheie"]], "formulare": "noua" if k in noi else "generator",
                            "subiect": a["x"]})
    pe_tip_ii: dict[str, list] = {t: [] for t in TIPURI_II}
    for tip in TIPURI_II:
        for i in ordine:
            a = cand[i]
            if i in folosite or len(pe_tip_ii[tip]) >= pe_tip:
                continue
            if (info := extrage_ii(tip, a["text"], a["x"], a["tip"], a["verb"])) is not None:
                pe_tip_ii[tip].append((i, info))
                folosite.add(i)
    ii: list[dict[str, Any]] = []
    k = 0
    while len(ii) < total_ii and any(k < len(v) for v in pe_tip_ii.values()):  # pe rând din fiecare tip
        for tip in TIPURI_II:
            if k < len(pe_tip_ii[tip]) and len(ii) < total_ii:
                i, info = pe_tip_ii[tip][k]
                a = cand[i]
                ii.append({"fel": "text", "limba": "ro", "categorie": "ii", "tip": tip, "text": a["text"],
                           "intrebare": cap(FORMULARI_II[tip][info["fel"]].format(x=a["x"])),
                           "raspuns": info["raspuns"], "cheie": [info["cheie"]], "formulare": "tip_neantrenat",
                           "subiect": a["x"]})
        k += 1
    perechi += ii
    for n, p in enumerate(perechi):
        p["grup"] = f"tipuri_noi_{n}"
    return {"perechi": perechi, "disponibile_i": disponibile_i,
            "disponibile_ii": {t: len(v) for t, v in pe_tip_ii.items()}}


def verifica_examen(perechi: list[dict[str, Any]]) -> dict[str, Any]:
    gen = {s for felur in GENERATOR.values() for lista in felur.values() for s in lista}
    return {
        "raspunsuri_care_nu_sunt_in_text": [p["intrebare"] for p in perechi if p["cheie"][0] not in p["text"]],
        "texte_repetate": len(perechi) - len({p["text"] for p in perechi}),
        "pe_categorie": dict(Counter(p["categorie"] for p in perechi)),
        "i_pe_tip": dict(Counter(p["tip"] for p in perechi if p["categorie"] == "i")),
        "i_formulari_noi_pe_tip": dict(Counter(p["tip"] for p in perechi if p["formulare"] == "noua")),
        "ii_pe_tip": dict(Counter(p["tip"] for p in perechi if p["categorie"] == "ii")),
        "sabloane_noi_care_sunt_si_in_generator": sorted({s for felur in EXAMEN_NOI.values() for lista in felur.values()
                                                          for s in lista} & gen),
    }


def _rand(tip: str, fel: str, text: str, q: str, raspuns: str, cheie: str, x: str, n: int) -> dict[str, Any]:
    return {"fel": fel, "tip": tip, "prompt": f"Text: {text}\nÎntrebare: {q}\nRăspuns:", "text": text,
            "intrebare": q, "raspuns": raspuns, "cheie": [cheie] if cheie else [], "subiect": x,
            "articol": f"wikipedia_ro: {x}", "id": f"r2_{n:05d}"}


def construieste_antrenare(cand: list[dict[str, Any]], examen: list[dict[str, Any]], rng: random.Random,
                           plafon: int = PLAFON_PE_TIP, fractie: float = FRACTIE_NU_SCRIE
                           ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Perechile noi: pe fiecare tip (b2) cel mult `plafon`, din care ~`fractie` „Nu scrie în text.”. Scoate textele,
    subiectele și orice text cu o bucată de 8 cuvinte din examen."""
    from unelte.genereaza_conversatie import bucati, normalizat

    bucati_ex = {b for p in examen for b in bucati(p["text"])}
    texte_ex = {p["text"] for p in examen}
    subiecte_ex = {normalizat(p["subiect"]) for p in examen}
    scoase = Counter()
    bune = []
    for a in cand:
        if a["text"] in texte_ex:
            scoase["text din examen"] += 1
        elif normalizat(a["x"]) in subiecte_ex:
            scoase["subiect din examen"] += 1
        elif bucati(a["text"]) & bucati_ex:
            scoase["bucată de 8 cuvinte din examen"] += 1
        else:
            bune.append(a)
    noi: list[dict[str, Any]] = []
    numar: dict[str, dict[str, int]] = {}
    for tip in TIPURI_B2:
        poz, neg = [], []
        for a in bune:
            if (info := extrage(tip, a["text"], a["x"], a["tip"], a["verb"])) is not None:
                poz.append((a, info))
            elif tip in FEL_NU_SCRIE and (l := lipseste(tip, a["text"], a["x"], a["tip"])) is not None:
                neg.append((a, l))
        rng.shuffle(poz)
        rng.shuffle(neg)
        cate_neg = min(len(neg), round(fractie * plafon)) if tip in FEL_NU_SCRIE else 0
        cate_poz = min(len(poz), plafon - cate_neg)
        cate_neg = min(cate_neg, round(fractie / (1 - fractie) * cate_poz))
        for a, info in poz[:cate_poz]:
            noi.append(_rand(tip, "text", a["text"], intrebare(tip, info, a["x"], rng), info["raspuns"], info["cheie"],
                             a["x"], 0))
        for a, l in neg[:cate_neg]:
            noi.append(_rand(f"lipsa_{tip}", "nu_scrie", a["text"], intrebare(tip, l, a["x"], rng), NU_SCRIE, "",
                             a["x"], 0))
        numar[tip] = {"cu_raspuns": cate_poz, "nu_scrie": cate_neg, "disponibile_cu_raspuns": len(poz),
                      "disponibile_nu_scrie": len(neg)}
    rng.shuffle(noi)
    for n, r in enumerate(noi):
        r["id"] = f"r2_{n:05d}"
    return noi, {"pe_tip": numar, "scoase_din_cauza_examenului": dict(scoase)}


def _scrie_json(cale: Path, obiect: Any) -> None:
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_bytes(json.dumps(obiect, ensure_ascii=False, indent=1).encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="S109: tipurile (b2) — examenul ținut deoparte și perechile noi.")
    parser.add_argument("pas", choices=["examen", "antrenare"])
    parser.add_argument("--radacina", default=str(RADACINA))
    a = parser.parse_args(argv)
    rad = Path(a.radacina)
    from unelte.conversatie_wikipedia import SURSA

    t0 = time.time()
    if a.pas == "examen":
        iesire = rad / EXAMEN
        if iesire.exists():
            raise SystemExit(f"{iesire} există deja; examenul se face o singură dată.")
        motive: Counter = Counter()
        cand = candidati(motive, rad)
        ex = construieste_examen(cand, random.Random(SAMANTA))
        v = verifica_examen(ex["perechi"])
        if v["raspunsuri_care_nu_sunt_in_text"] or v["texte_repetate"] or v["sabloane_noi_care_sunt_si_in_generator"]:
            raise SystemExit(f"verificarea examenului a picat: {v}")
        _scrie_json(iesire, {
            "nota": "S109 (C-119 E1, 13 nov 2026): examenul ținut deoparte pentru tipurile de întrebări. (i) = cele 13 "
                    "tipuri (b2) din S15, acum antrenate de `unelte/conversatie_tipuri.py`, pe texte și subiecte scoase "
                    "din antrenare; „formulare”: „noua” = o formulare care NU apare în generator. (ii) = tipuri care nu "
                    "sunt nici în S15, nici în generator, nici în antrenarea liniei. Fără „Nu scrie” și fără da/nu. "
                    "Sursa: Wikipedia RO descărcată, aceleași filtre și excluderi ca S108; sămânța 109.",
            "sursa": SURSA, "sha256_sursa": sha(rad / SURSA), "candidati": len(cand), "motive": dict(motive),
            "disponibile_i": ex["disponibile_i"], "disponibile_ii": ex["disponibile_ii"], "verificari": v,
            "perechi": ex["perechi"]})
        print(json.dumps({"scris": str(iesire), "secunde": round(time.time() - t0), **v}, ensure_ascii=False))
        return 0
    dosar = rad / DOSAR_ANTRENARE
    iesire, info = dosar / "antrenare.jsonl", dosar / "info.json"
    if iesire.exists() or info.exists():
        raise SystemExit(f"{dosar} are deja fișierele; antrenarea se scrie o singură dată.")
    examen = json.loads((rad / EXAMEN).read_text(encoding="utf-8"))["perechi"]
    motive = Counter()
    cand = candidati(motive, rad)
    noi, numar = construieste_antrenare(cand, examen, random.Random(SAMANTA))
    vechi = (rad / VECHI).read_bytes().decode("utf-8").splitlines()
    vechi = [r for r in vechi if r.strip()]
    dosar.mkdir(parents=True, exist_ok=True)
    randuri = vechi + [json.dumps(r, ensure_ascii=False) for r in noi]
    iesire.write_bytes(("\n".join(randuri) + "\n").encode("utf-8"))
    _scrie_json(info, {
        "nota": "S109: cele vechi (lucru/romana_raspunsuri/antrenare.jsonl, neschimbate, în aceeași ordine), apoi cele noi "
                "amestecate cu random.Random(109).",
        "perechi_vechi": len(vechi), "perechi_noi": len(noi), "perechi_total": len(randuri),
        "noi_pe_tip": dict(Counter(r["tip"] for r in noi)), "pe_tip": numar["pe_tip"],
        "scoase_din_cauza_examenului": numar["scoase_din_cauza_examenului"], "candidati": len(cand),
        "motive": dict(motive), "sha256": {"sursa": sha(rad / SURSA), "vechi": sha(rad / VECHI),
                                           "examen": sha(rad / EXAMEN), "antrenare": sha(iesire)},
        "secunde": round(time.time() - t0)})
    print(json.dumps({"scris": str(iesire), "noi": len(noi), "total": len(randuri)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
