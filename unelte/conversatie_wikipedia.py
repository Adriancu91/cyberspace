"""Perechi întrebare → răspuns din Wikipedia în română (15 octombrie 2026, hotărât de Adrian), pe procesor.

Întrebarea: „Ce este X?”, „Cine a fost X?” / „Cine este X?” sau „Unde se află X?”, unde X e subiectul primei propoziții
a articolului. Răspunsul: primele 1–3 propoziții ale articolului, scrise de oameni, neschimbate, în afară de
parantezele scurte, care se scot întregi (ex. „(n. 15 ianuarie 1850, Botoșani – d. 1889)”).
Doar articole cu început curat:
- primul paragraf începe cu literă mare și are forma „X este / a fost / sunt …”;
- fără semne de liste, tabele sau formule (= | { } [ ] < > # * •), fără paranteze lungi (peste --paranteza litere) sau
  una în alta;
- răspunsul are între 40 și 350 de litere, iar prima propoziție nu se termină într-o prescurtare („n.”, „d.”, „I.”).
Se iau doar articole din partea de antrenare (validarea e alt fișier); în plus, ies perechile cu o bucată de 8 cuvinte
din examene sau validări, cele cu cuvinte necunoscute (filtrul de ortografie) și întrebările repetate.
Ca locurile (sate, comune) și oamenii să nu fie aproape tot, fiecare fel are cel mult --cote din total.
Licența: Wikipedia, CC BY-SA 4.0 (atribuirea: docs/DATE_surse.md).

Versiunea 2 (16 octombrie 2026, după fișa din 15 octombrie: 5 greșite din 15, cerută de Adrian):
- **propozițiile rupte ies** (curățarea Wikimedia a scos legături și numere, iar propoziția a rămas fără un cuvânt):
  o prepoziție chiar înainte de semn („din.”, „de,”), „a lui.”, o prepoziție urmată de „și” („de soții și după”),
  paranteze sau ghilimele goale, cuvinte lipite (literă mică urmată de literă mare, „ComitatulWestchester”), o
  propoziție fără niciun verb. Prima propoziție ruptă = articolul iese; una de după ea = răspunsul se oprește înainte;
- **oamenii**: „Cine este / a fost…?” și după textul articolului („s-a născut”, „a murit”, „a decedat”), nu doar
  după paranteza cu anii, după meserie sau după naționalitate;
- **satele, comunele, localitățile și sportivii** sunt împreună cel mult --mici din total (10%);
- **articolele lungi** (subiecte cunoscute) au întâietate: se aleg dintre cele mai lungi --din-cele-mai-lungi × total.

    python unelte/conversatie_wikipedia.py --perechi 8000
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

SURSA = "date/ws/curat/wikipedia_ro/antrenare.txt"
IESIRE = "date/conversatie/wikipedia.jsonl"
INTERZISE_SEMNE = set("=|{}[]<>#*•")
LOCURI = ("sat", "oraș", "municipiu", "comună", "râu", "lac", "munte", "stat", "țară", "regiune", "județ", "insulă",
          "localitate", "cartier", "fluviu", "vârf", "deal", "peninsulă", "district", "provincie", "capitală", "comitat")
PROFESII = set("""actor actriță cântăreț cântăreață politician politiciană general regizor regizoare jucător jucătoare
scriitor scriitoare poet poetă pictor pictoriță compozitor compozitoare fotbalist fotbalistă sportiv sportivă cercetător
profesor profesoară inginer medic preot episcop rege regină prinț prințesă împărat împărăteasă filozof filosof istoric
matematician fizician chimist biolog arhitect sculptor muzician dirijor jurnalist jurnalistă avocat judecător economist
diplomat militar ofițer boxer ciclist atlet atletă handbalist handbalistă baschetbalist baschetbalistă model fotomodel
prezentator prezentatoare rapper solist solistă chitarist pianist pianistă violonist dansator balerină fotograf scenarist
producător antreprenor teolog lingvist filolog critic traducător traducătoare sfânt cardinal papă duce ducesă conte
contesă voievod domnitor senator deputat ministru președinte primar astronom geograf botanist zoolog explorator navigator
aviator pilot alpinist șahist tenismen gimnast gimnastă înotător înotătoare canotor canotoare luptător halterofil schior
patinator patinatoare arbitru antrenor informatician fost fostă""".split())
NATIONALITATI = tuple("""român românc rus kazah ceh german francez american englez italian spaniol polonez ungur maghiar
sârb croat bulgar grec turc chinez japonez brazilian argentinian mexican canadian australian belgian olandez neerlandez
suedez norvegian danez finlandez elvețian austriac portughez irlandez scoțian ucrainean moldovean chilian cilian slovac
sloven bosniac albanez estonian leton lituanian belarus georgian armean azer israelian egiptean indian pakistanez iranian
irakian sirian libanez coreean vietnamez thailandez filipinez indonezian columbian venezuelean peruan uruguayan
paraguayan bolivian ecuadorian cubanez nigerian kenyan sud-african galez britanic islandez luxemburghez""".split())
NEPERSOANE = set("""film serial album proiect joc roman program post partid club companie firmă grup ziar revistă trupă
formație cântec single operă festival monument tablou produs vehicul avion automobil tanc vas navă dans fel preparat
sport limbaj dialect stil curent concurs premiu turneu episod sistem aparat instrument organizație institut""".split())
ADJECTIVE_INAINTE = set("""fost fostă important importantă mare celebru celebră cunoscut cunoscută renumit renumită
faimos faimoasă talentat talentată prolific prolifică influent influentă reputat reputată eminent eminentă""".split())
PERSOANE_IN_PLUS = set("""dramaturg dramaturgă activist activistă cineast cineastă cântăreț cântăreață compozitoare
eseist eseistă romancier romancieră publicist publicistă cărturar savant savantă om femeie bărbat călugăr călugăriță
mitropolit patriarh pictoriță graficiană grafician artist artistă animator animatoare comic cântăreață ilustrator
ilustratoare poetă vocalist vocalistă interpret interpretă textier textieră muzicolog muzicologă aforist folclorist
etnograf arheolog arheologă psiholog psihologă sociolog sociologă antropolog filantrop om de afaceri""".split())
SPORTIVI = set("""fotbalist fotbalistă jucător jucătoare sportiv sportivă boxer ciclist ciclistă atlet atletă handbalist
handbalistă baschetbalist baschetbalistă tenismen gimnast gimnastă înotător înotătoare canotor canotoare luptător
luptătoare halterofil halterofilă schior schioare patinator patinatoare arbitru antrenor scrimer scrimeră judoka
voleibalist voleibalistă hocheist pilot bober jucătoare""".split())
LOCURI_MICI = set("""sat comună localitate cătun cartier așezare raion district comitat""".split())
_LIPITE = re.compile(r"[a-zăâîșț][A-ZĂÂÎȘȚ]")
_PREP_SEMN = re.compile(r"(?i)\b(de|din|la|cu|în|pe|lui|al|ale|ai|după|pentru|prin|către|despre|între|și|sau|ca|decât|iar)"
                        r"\s*[.,;:!?)]")
_PREP_SI = re.compile(r"\b(de|din|la|cu|în|pe|după|pentru|prin|către|despre|între)\s+(și|sau|iar)\b")
_GOALE = re.compile(r"\(\s*\)|„\s*”|\"\s*\"|«\s*»")
_A_LUI = re.compile(r"\ba lui\s*[.,;:]")
_VERB = re.compile(r"\b(este|sunt|era|erau|fost|fi|fie|are|au|avea|aveau|a|s-a|s-au|se|și-a|și-au|poate|pot|putea|"
                   r"devine|face|fac|\w+ează|\w+ește|\w+esc|\w+ază|\w+at|\w+ată|\w+ați|\w+ate|\w+it|\w+ită|\w+iți|"
                   r"\w+ite|\w+ut|\w+ută|\w+uți|\w+ute|\w+ât|\w+ește)\b")


def propozitie_rupta(p: str) -> str | None:
    """De ce e ruptă propoziția (după curățarea Wikimedia), sau None dacă pare întreagă."""
    if _LIPITE.search(p):
        return "cuvinte lipite"
    if _PREP_SEMN.search(p) or _A_LUI.search(p):
        return "prepoziție fără cuvântul de după ea"
    if _PREP_SI.search(p):
        return "prepoziție urmată de „și”"
    if _GOALE.search(p) or re.search(r":\s*[.;]", p):
        return "paranteze sau ghilimele goale"
    if p.count("„") != p.count("”") or p.count("(") != p.count(")"):
        return "ghilimele sau paranteze neînchise (propoziție tăiată)"
    if _PRESCURTARE.search(p.rstrip()):
        return "se termină într-o prescurtare (propoziție tăiată)"
    if not _VERB.search(p.lower()):
        return "fără verb"
    return None


def greseala_de_tipar(text: str, numarate: dict[str, int], raport: int = 200, maxim: int = 1000) -> str | None:
    """Un cuvânt cu literă mică, rar (sub `maxim` apariții), care are o rudă de o literă de cel puțin `raport` ori mai
    deasă („aceast” față de „această”): de obicei o greșeală de tipar din Wikipedia. Întoarce cuvântul sau None."""
    for cuvant in re.findall(r"\b[a-zăâîșț]+\b", text.lower()):
        n = numarate.get(cuvant, 0)
        if not n or n >= maxim:
            continue
        rude = {cuvant + "ă", cuvant + "a", cuvant + "e", cuvant + "i", cuvant + "u", cuvant[:-1]}
        if any(numarate.get(r, 0) >= raport * n for r in rude if r != cuvant):
            return cuvant
    return None


# Bucăți rămase după ce curățarea a scos un număr sau un șablon din text (ex. „la circa de ani-lumină”, „cu din”).
_RUPT = re.compile(r"(?i)\b(circa de|aproximativ de|peste de|cu din|de de|la de|în de|din de|cu de|populație de locuitori|la,|are locuitori|avea locuitori|cu locuitori|cu sediul,|— sau —|—\s*—)\b")
_PREFIX = re.compile(r"^(?P<x>[A-ZĂÂÎȘȚ][^,;:]{1,60}?) (?P<verb>este|sunt|a fost|au fost) (?P<rest>\S.*)$", re.S)
_PROPOZITII = re.compile(r"(?<=[.!?])\s+(?=[A-ZĂÂÎȘȚ„])")
_PARANTEZA = re.compile(r"\s*\(([^()]*)\)")
_PRESCURTARE = re.compile(r"(?:\b[A-ZĂÂÎȘȚa-z]\.|\b(?:n|d|sec|etc|cca|aprox|nr|lb|î\.Hr|d\.Hr)\.)$")


def curata_inceputul(articol: str, paranteza_max: int = 60) -> str | None:
    """Primul paragraf, fără parantezele scurte; None dacă începutul nu e curat."""
    paragraf = articol.strip().split("\n", 1)[0].strip()
    if not paragraf or not paragraf[0].isupper() or INTERZISE_SEMNE & set(paragraf):
        return None
    if paragraf.count("(") != paragraf.count(")") or re.search(r"\([^()]*\(", paragraf):
        return None
    if any(len(m.group(1)) > paranteza_max for m in _PARANTEZA.finditer(paragraf)):
        return None
    curat = _PARANTEZA.sub("", paragraf)
    return re.sub(r"\s+([,.;:])", r"\1", re.sub(r"\s{2,}", " ", curat)).strip()


def pereche_din(articol: str, paranteza_max: int = 60) -> dict[str, str] | None:
    paragraf = articol.strip().split("\n", 1)[0]
    curat = curata_inceputul(articol, paranteza_max)
    if curat is None:
        return None
    propozitii = _PROPOZITII.split(curat)
    if _PRESCURTARE.search(propozitii[0].rstrip(".!?") + ".") and len(propozitii[0]) < 40:
        return None
    if _PRESCURTARE.search(propozitii[0][:-1].split()[-1] + ".") if propozitii[0].endswith(".") and propozitii[0][:-1].split() else False:
        return None
    m = _PREFIX.match(propozitii[0])
    if m is None or propozitie_rupta(propozitii[0]):
        return None
    x, verb, rest = m.group("x").strip(), m.group("verb"), m.group("rest")
    if x.split()[0] in ("Un", "O", "Niște", "Unul", "Una"):
        return None
    raspuns = ""
    for p in propozitii[:3]:
        if len(raspuns) + len(p) + 1 > 350 or propozitie_rupta(p):
            break
        raspuns = (raspuns + " " + p).strip()
    if not 40 <= len(raspuns) <= 350 or not raspuns.endswith((".", "!", "?")):
        return None
    if _RUPT.search(raspuns):
        return None
    cuvant = rest.split()[1].strip(",.") if len(rest.split()) > 1 else ""
    cuvinte_rest = [c.strip(",.") for c in rest.split()]
    i = 1
    while i < len(cuvinte_rest) - 1 and cuvinte_rest[i] in ADJECTIVE_INAINTE:
        i += 1
    cuvant = cuvinte_rest[i] if len(cuvinte_rest) > i else ""
    om = (bool(re.match(r"[^(]{1,80}\((?:n\.|născut|născută|\d{3,4}\s*[–-]\s*\d{3,4})[^)]*\)\s*(este|a fost)\b", paragraf))
          and rest.startswith(("un ", "o ")) and cuvant not in LOCURI) \
        or (rest.startswith(("un ", "o ")) and cuvant in PROFESII) or rest.split()[0].strip(",.") in ("fiul", "fiica") \
        or (rest.startswith(("un ", "o ")) and cuvant not in LOCURI and len(rest.split()) > 2
            and rest.split()[2].strip(",.").lower().startswith(NATIONALITATI) and not rest.split()[2][0].isupper()
            and cuvant not in NEPERSOANE)
    loc = (rest.startswith(("un ", "o ")) and cuvant in LOCURI) or rest.startswith(
        ("localitatea de reședință", "satul de reședință", "o așezare"))
    corp = articol[len(paragraf):]
    inceput_corp = (curat + " " + corp[:1500]).lower()
    om = om or (rest.startswith(("un ", "o ")) and cuvant in PERSOANE_IN_PLUS)
    mic = cuvant in LOCURI_MICI or cuvant in SPORTIVI or rest.startswith(
        ("localitatea de reședință", "satul de reședință", "o așezare"))
    primul = x.split()[0]
    if not om and " " not in x and primul.lower() in corp.split() and f" {primul} " not in corp:  # substantiv comun: cu literă mică
        x = x[0].lower() + x[1:]
    if not om and not rest.startswith(("un ", "o ", "unul ", "una ", "cel ", "cea ", "cei ", "cele ", "singurul ",
                                         "singura ", "al ", "a ", "localitatea", "satul", "denumirea", "numele")):
        return None  # „Ce este X?” doar când răspunsul îl definește („este un…”), nu „a fost adoptată în…”
    if om:
        tip, intrebare = "om", f"Cine {'a fost' if verb == 'a fost' else 'este'} {x}?"
    elif loc and re.search(r"\b(din|în|situat|situată)\b", rest):
        tip, intrebare = "loc", f"Unde se află {x}?"
    elif verb in ("este", "sunt"):
        tip, intrebare = "ce", f"Ce {'este' if verb == 'este' else 'sunt'} {x}?"
    else:
        tip, intrebare = "ce", f"Ce {verb} {x}?"
    return {"tip": tip, "intrebare": intrebare, "raspuns": raspuns, "mic": mic, "lungime": len(articol)}


def articole(cale: Path):
    with cale.open(encoding="utf-8") as f:
        rest = ""
        while bucata := f.read(64 * 2**20):
            parti = (rest + bucata).split("<|endoftext|>")
            rest = parti.pop()
            yield from parti
        if rest.strip():
            yield rest


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Perechi întrebare → răspuns din Wikipedia în română.")
    parser.add_argument("--perechi", type=int, default=8000)
    parser.add_argument("--cote", default="om=0.3,loc=0.15,ce=1.0", help="partea maximă din total, pe feluri")
    parser.add_argument("--paranteza", type=int, default=60)
    parser.add_argument("--samanta", type=int, default=0)
    parser.add_argument("--mici", type=float, default=0.10, help="sate, comune, localități și sportivi: cel mult atât")
    parser.add_argument("--din-cele-mai-lungi", type=float, default=3.0,
                        help="se alege dintre cele mai lungi (articole) atâtea × perechi")
    args = parser.parse_args(argv)

    from unelte.genereaza_conversatie import bucati, bucati_interzise, normalizat
    from unelte.ortografie_ro import citeste_exceptii, citeste_lista, necunoscute

    interzise = bucati_interzise()
    cunoscute, exceptii = citeste_lista(), citeste_exceptii()
    candidati: list[dict[str, str]] = []
    motive: Counter[str] = Counter()
    vazute: set[str] = set()
    for articol in articole(RADACINA / SURSA):
        p = pereche_din(articol, args.paranteza)
        if p is None:
            motive["început necurat"] += 1
            continue
        if normalizat(p["intrebare"]) in vazute:
            motive["întrebare repetată"] += 1
            continue
        if bucati(p["intrebare"] + " " + p["raspuns"]) & interzise:
            motive["bucată dintr-un examen sau dintr-o validare"] += 1
            continue
        if necunoscute(p["intrebare"] + "\n" + p["raspuns"], cunoscute, exceptii):
            motive["cuvânt necunoscut"] += 1
            continue
        if greseala_de_tipar(p["raspuns"], cunoscute.numarate):
            motive["greșeală de tipar"] += 1
            continue
        vazute.add(normalizat(p["intrebare"]))
        candidati.append(p)
    rng = random.Random(args.samanta)
    candidati.sort(key=lambda p: -p["lungime"])  # v2: subiectele cunoscute au articole lungi
    candidati = candidati[: int(args.din_cele_mai_lungi * args.perechi)]
    rng.shuffle(candidati)
    cote = {k: float(v) for k, v in (x.split("=") for x in args.cote.split(","))}
    alese: list[dict[str, str]] = []
    pe_tip: Counter[str] = Counter()
    for p in candidati:
        if len(alese) >= args.perechi:
            break
        if pe_tip[p["tip"]] + 1 > cote.get(p["tip"], 1.0) * args.perechi:
            continue
        if p["mic"] and pe_tip["mici"] + 1 > args.mici * args.perechi:
            continue
        pe_tip[p["tip"]] += 1
        pe_tip["mici"] += p["mic"]
        alese.append(p)
    iesire = RADACINA / IESIRE
    iesire.parent.mkdir(parents=True, exist_ok=True)
    with iesire.open("w", encoding="utf-8") as f:
        for i, p in enumerate(alese):
            f.write(json.dumps({"fel": "wiki", "limba": "ro", "tip": p["tip"], "intrebare": p["intrebare"],
                                "raspuns": p["raspuns"], "profesor": "wikipedia", "sursa": "wikipedia_ro (CC BY-SA 4.0)",
                                "grup": f"wiki_{i}"}, ensure_ascii=False) + "\n")
    print(f"{len(alese)} perechi din Wikipedia ({dict(pe_tip)}), din {len(candidati)} candidați; scoase: {dict(motive)}. "
          f"În {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
