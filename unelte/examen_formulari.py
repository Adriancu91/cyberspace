"""Examenul de formulări (S124, C-132, 17 nov 2026): 200 de întrebări FĂRĂ text alături, în forma filei Chat
(„Întrebare: …⏎Răspuns:”), cu formulări care NU apar nicăieri în antrenare. Scris ÎNAINTE de datele S124.

    python unelte/examen_formulari.py construieste            → docs/conversatie/examen_formulari.json (o singură dată)
    python unelte/examen_formulari.py model --experiment 680 --iesire lucru/conversatie_chat3/formulari_680.json
                                                                [--dispozitiv cuda]

Examenul (`random.Random(124)`):
- 120 de calcule: adunare 24, scădere 24, înmulțire 42, împărțire 30 (aceleași feluri și limite ca la S120,
  `conversatie_chat.numere_calcul`); 6 șabloane NOI pe operație, folosite pe rând. Numerele: la adunare/scădere/împărțire
  perechi (a, b, operația) care NU sunt nici în `docs/conversatie/examen_calcule.json`, nici în calculele de antrenare
  S120 (`lucru/conversatie_chat2/perechi_calcule.jsonl`); la înmulțire (doar 144 de perechi posibile) perechi luate din
  cele 70 ale examenului de calcule, care sunt deja interzise în orice generator — așa niciun model n-a văzut numerele
  la antrenare. Perechile acestui examen se interzic și în generatorul S124.
- 80 de întrebări sociale: aceleași 7 intenții ca la S116 (salut, ce faci, mulțumesc, la revedere, cine ești, ce poți,
  „nu am de unde să știu”), formulări NOI.

Verificat automat: niciun șablon nu e în generatoarele S116/S120 (S124 se verifică la generarea lui) și nici în
examenele vechi; nicio bucată de 6 cuvinte la rând nu e comună cu vreun rând de antrenare existent.

Notarea: calculele ca `examen_calcule.corect`, socialele ca partea (b) din `examen_chat.py` (cuvintele-cheie S116).
Scorul = calcule + sociale, din 200; procentul = scorul / 200 × 100 (pragul S124 e în puncte procentuale).
Răspunsul modelului: ca fila Chat (`model.completeaza`, fără întâmplare, tăiat la primul rând nou sau la
<|endoftext|>). Refuză să scrie peste un fișier care există.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

EXAMEN = "docs/conversatie/examen_formulari.json"
SAMANTA = 124
CALCULE_S120 = "lucru/conversatie_chat2/perechi_calcule.jsonl"
# rândurile de antrenare care există la scrierea examenului (S116 și S120; ambele conțin și r2-ul lui #651)
ANTRENARE_EXISTENTA = ["lucru/conversatie_chat/antrenare.jsonl", "lucru/conversatie_chat2/antrenare.jsonl"]
COTE_CALCULE = {"adunare": 24, "scadere": 24, "inmultire": 42, "impartire": 30}  # 120
COTE_SOCIALE = {"salut": 12, "ce_faci": 12, "multumesc": 12, "la_revedere": 11, "cine_esti": 11, "ce_poti": 11,
                "nu_stiu": 11}  # 80
BUCATA = 6  # cuvinte la rând

SABLOANE_CALCULE: dict[str, list[str]] = {
    "adunare": ["Ce număr obții adunând {a} cu {b}?", "La {a} adaugă {b}. Cât iese?",
                "Ana are {a} timbre, iar Mihai are {b}. Câte timbre au împreună?",
                "Care e totalul dintre {a} și {b}?", "Pune {b} peste {a} și spune-mi cât ai.",
                "Cât ar da {a} adunat la {b}?"],
    "scadere": ["Ce număr obții scăzând {b} din {a}?", "Ia {b} din {a}. Cât rămâne?",
                "Într-un autobuz sunt {a} oameni și coboară {b}. Câți oameni rămân?",
                "Cu cât e mai mare {a} decât {b}?", "Dacă scot {b} din {a}, ce obțin?",
                "Care e rezultatul când micșorez {a} cu {b}?"],
    "inmultire": ["Ce număr obții înmulțind {a} cu {b}?", "Câte bănci sunt în {a} rânduri a câte {b} bănci?",
                  "Care e produsul numerelor {a} și {b}?", "{a} înmulțit cu {b} dă cât?",
                  "Dacă iau de {b} ori numărul {a}, cât obțin?", "Câte roți au {a} căruțe cu câte {b} roți fiecare?"],
    "impartire": ["Ce număr obții împărțind {a} la {b}?", "Câte grupe de câte {b} se pot face din {a}?",
                  "Împărțim {a} mere egal în {b} coșuri. Câte mere sunt în fiecare coș?",
                  "Care e câtul împărțirii lui {a} la {b}?",
                  "Cât primește fiecare dacă {a} lei se împart la {b} oameni?",
                  "Dacă tai {a} în {b} părți egale, cât are o parte?"],
}
SOCIALE: dict[str, list[str]] = {
    "salut": ["Te salut!", "Te salut cu drag, Kronos!", "Bună, bună!", "Noroc, Kronos!", "Hei, am venit să vorbim!",
              "Bună ziua, sunt din nou aici.", "Salut, îmi face plăcere să te cunosc!", "Bună seara tuturor!",
              "Salut, m-am întors!", "Bună dimineața și ție!", "Hei, bună!", "Bine te-am găsit!"],
    "ce_faci": ["Cum te mai descurci?", "Ce mai e pe la tine?", "Cum îți este azi?", "Ești bine dispus?",
                "Cum merge viața?", "Te simți în regulă?", "Cum ți-a mers azi?", "Ce faci de bine?",
                "Cum ești în dimineața asta?", "Ce mai zici, cum ești?", "Toate bune la tine?", "Cum mai ești, Kronos?"],
    "multumesc": ["Mulțumesc din suflet!", "Îți mulțumesc pentru tot!", "Mersi, m-ai ajutat!", "Mulțumesc foarte mult!",
                  "Mersi de răspuns!", "Ești de mare ajutor, mulțumesc!", "Mulțumesc că mi-ai răspuns!", "Merci!",
                  "Mersi tare mult!", "Mulțam!", "Îți rămân dator, mersi!", "Mulțumesc, a fost util!"],
    "la_revedere": ["Trebuie să plec, pa!", "Pe mâine!", "Gata pentru azi, la revedere!", "Ne mai auzim!",
                    "O seară bună!", "Pa, pe data viitoare!", "Mă retrag, noapte bună!", "Rămas bun!", "Hai, pa!",
                    "Ciao, Kronos!", "Pa și pe mâine!"],
    "cine_esti": ["Tu ce ești de fapt?", "Cine ești, de fapt?", "Ești un calculator?", "Ce ești, un om sau o mașină?",
                  "Aș vrea să știu cum te numești.", "Cine te-a construit?", "Cum îți spune lumea?",
                  "Ești o persoană adevărată?", "Ce fel de ființă ești?", "Cine e Kronos?", "De unde vii tu?"],
    "ce_poti": ["Ce lucruri știi să faci?", "Cu ce te ocupi?", "Ce te pricepi să faci?", "La ce te pricepi?",
                "Ce fel de ajutor oferi?", "În ce mă poți ajuta?", "Ce știi?", "Ce pot să te rog să faci?",
                "Care sunt abilitățile tale?", "Ce poți face tu bine?", "Ce întrebări accepți?"],
    "nu_stiu": ["Ce am în mână acum?", "Câți frați am?", "Ce film o să văd diseară?", "Unde o să merg în vacanță?",
                "Ce mi-a spus mama azi-dimineață?", "Ce notă o să iau la examen?", "Cum îl cheamă pe câinele meu?",
                "Ce oră arată ceasul meu acum?", "Ce gust are cafeaua mea de azi?", "Câte mesaje am primit azi?",
                "Ce carte citesc acum?"],
}


def taie(text: str) -> str:
    """Ca în fila Chat: până la primul rând nou sau la <|endoftext|>."""
    return text.split("<|endoftext|>")[0].strip().split("\n")[0].strip()


def forma(sablon: str) -> str:
    """Forma unui șablon de calcul fără numere (aceeași regulă ca la S120: `formulare_fara_numere`)."""
    from unelte.conversatie_chat import formulare_fara_numere

    return formulare_fara_numere(sablon.format(a=3, b=7))


def bucati(text: str, n: int = BUCATA) -> set[str]:
    from unelte.genereaza_conversatie import bucati as b

    return b(text, n)


# --- notarea ---------------------------------------------------------------------------------------------------------
def corect(p: dict[str, Any], raspuns: str, cuvinte_cheie: dict[str, list[str]]) -> bool:
    if p["parte"] == "calcul":
        from unelte.examen_calcule import corect as c

        return c(p, raspuns)
    from unelte.romana_raspunsuri import contine

    return any(contine(raspuns, k) for k in cuvinte_cheie[p["categorie"]])


def noteaza(examen: dict[str, Any], raspunsuri: dict[str, str]) -> dict[str, Any]:
    cuvinte = examen["cuvinte_cheie"]
    pe: dict[str, list[int]] = {}
    calc = soc = 0
    for p in examen["perechi"]:
        ok = corect(p, raspunsuri.get(p["id"], ""), cuvinte)
        k = f"{p['parte']}_{p['categorie']}"
        pe.setdefault(k, [0, 0])
        pe[k][1] += 1
        pe[k][0] += ok
        calc += ok and p["parte"] == "calcul"
        soc += ok and p["parte"] == "social"
    n = len(examen["perechi"])
    return {"total": calc + soc, "total_din": n, "procent": round(100 * (calc + soc) / n, 2),
            "calcule": calc, "calcule_din": sum(p["parte"] == "calcul" for p in examen["perechi"]),
            "sociale": soc, "sociale_din": sum(p["parte"] == "social" for p in examen["perechi"]),
            "pe_categorie": {k: f"{v[0]}/{v[1]}" for k, v in sorted(pe.items())},
            "nu_scrie_in_text": sum(1 for p in examen["perechi"] if "nu scrie" in raspunsuri.get(p["id"], "").lower())}


# --- construirea -----------------------------------------------------------------------------------------------------
def construieste(rng: random.Random, interzise: set[tuple[int, int, str]],
                 inmultire_permise: list[tuple[int, int]]) -> list[dict[str, Any]]:
    """`interzise` = perechile (a, b, operația) care nu au voie (examenul S120 + calculele de antrenare S120);
    `inmultire_permise` = perechile de înmulțire din care se aleg cele 42 (ale examenului S120)."""
    from unelte.conversatie_chat import numere_calcul, rezultat

    perechi: list[dict[str, Any]] = []
    for op, n in COTE_CALCULE.items():
        if op == "inmultire":
            pool = sorted(inmultire_permise)
            rng.shuffle(pool)
            alese = pool[:n]
        else:
            alese, vazute, k = [], set(), 0
            while len(alese) < n:
                a, b = numere_calcul(op, rng, k)
                k += 1
                if (a, b, op) in interzise or (a, b) in vazute:
                    continue
                vazute.add((a, b))
                alese.append((a, b))
        sabloane = list(SABLOANE_CALCULE[op])
        rng.shuffle(sabloane)
        for i, (a, b) in enumerate(alese):
            s = sabloane[i % len(sabloane)]
            perechi.append({"parte": "calcul", "categorie": op, "operatie": op, "a": a, "b": b,
                            "rezultat": rezultat(op, a, b), "sablon": s, "intrebare": s.format(a=a, b=b)})
    for c, n in COTE_SOCIALE.items():
        for q in SOCIALE[c][:n]:
            perechi.append({"parte": "social", "categorie": c, "sablon": q, "intrebare": q})
    for i, p in enumerate(perechi):
        p["id"] = f"form_{i:03d}"
    return perechi


def sabloane_vechi() -> dict[str, set[str]]:
    """Formele șabloanelor care există deja: generatoarele S116/S120 și examenele vechi (de chat și de calcule)."""
    from unelte.conversatie_chat import EXAMEN_SOCIAL, FORMULARI_CALCULE, SOCIAL_INTREBARI, norm
    from unelte.examen_calcule import FORMULARI_NOI

    return {"calcule_generator": {forma(f) for fs in FORMULARI_CALCULE.values() for f in fs},
            "calcule_examen_vechi": {forma(f) for fs in FORMULARI_NOI.values() for f in fs},
            "sociale_generator": {norm(q) for qs in SOCIAL_INTREBARI.values() for q in qs},
            "sociale_examen_vechi": {norm(q) for qs in EXAMEN_SOCIAL.values() for q in qs}}


def sabloane_in(perechi: list[dict[str, Any]], vechi: dict[str, set[str]]) -> dict[str, list[str]]:
    """Șabloanele examenului care apar în listele `vechi` (trebuie să fie toate goale)."""
    from unelte.conversatie_chat import norm

    r: dict[str, list[str]] = {}
    for nume, forme in vechi.items():
        if nume.startswith("calcule"):
            r[nume] = sorted({p["sablon"] for p in perechi if p["parte"] == "calcul" and forma(p["sablon"]) in forme})
        else:
            r[nume] = sorted({p["sablon"] for p in perechi if p["parte"] == "social" and norm(p["sablon"]) in forme})
    return r


def intrebari_randuri(randuri: Iterable[dict[str, Any]]) -> Iterable[str]:
    """Textele unui rând de antrenare care se compară: întrebarea (cu replicile de dinainte), răspunsul și textul."""
    for r in randuri:
        yield r.get("intrebare", "") or ""
        yield r.get("raspuns", "") or ""
        yield r.get("text", "") or ""


def bucati_comune(perechi: list[dict[str, Any]], texte: Iterable[str], n: int = BUCATA) -> dict[str, Any]:
    """Bucățile de `n` cuvinte ale întrebărilor din examen care apar în `texte`, plus întrebările sociale (adesea mai
    scurte de 6 cuvinte) care apar întocmai, normalizate, ca ultimă replică a unei întrebări de antrenare."""
    from unelte.conversatie_chat import norm

    b_ex: dict[str, str] = {}
    for p in perechi:
        for b in bucati(p["intrebare"], n):
            b_ex[b] = p["id"]
    q_soc = {norm(p["intrebare"]): p["id"] for p in perechi if p["parte"] == "social"}
    gasite: set[str] = set()
    identice: set[str] = set()
    vazute: set[str] = set()
    for t in texte:
        if not t or t in vazute:
            continue
        vazute.add(t)
        for b in bucati(t, n):
            if b in b_ex:
                gasite.add(b_ex[b])
        ultima = norm(t.split("\n")[-1].removeprefix("Întrebare: "))
        if ultima in q_soc:
            identice.add(q_soc[ultima])
    return {"cu_bucata_de_6": sorted(gasite), "sociale_identice": sorted(identice), "texte_comparate": len(vazute)}


def verificari(perechi: list[dict[str, Any]], interzise: set[tuple[int, int, str]]) -> dict[str, Any]:
    from unelte.conversatie_chat import norm

    calc = [p for p in perechi if p["parte"] == "calcul"]
    return {"pe_categorie": dict(Counter(p["categorie"] for p in perechi)),
            "calcule": len(calc), "sociale": len(perechi) - len(calc),
            "sabloane_calcule_noi": len({p["sablon"] for p in calc}),
            "sabloane_care_exista_deja": sabloane_in(perechi, sabloane_vechi()),
            "perechi_de_numere_interzise": [p["id"] for p in calc if (p["a"], p["b"], p["operatie"]) in interzise
                                            and p["operatie"] != "inmultire"],
            "perechi_de_numere_repetate": len(calc) - len({(p["a"], p["b"], p["operatie"]) for p in calc}),
            "sociale_repetate": (len(perechi) - len(calc)) - len({norm(p["intrebare"]) for p in perechi
                                                                   if p["parte"] == "social"}),
            "rezultate_gresite": [p["id"] for p in calc if not corect(p, f"{p['rezultat']}.", {})]}


def citeste_jsonl(cale: Path) -> Iterable[dict[str, Any]]:
    with cale.open(encoding="utf-8") as f:
        for r in f:
            if r.strip():
                yield json.loads(r)


def interzise_si_inmultire(rad: Path) -> tuple[set[tuple[int, int, str]], list[tuple[int, int]]]:
    from unelte.examen_calcule import EXAMEN as EX_CALC
    from unelte.examen_calcule import interzise

    ex_calc = json.loads((rad / EX_CALC).read_text(encoding="utf-8"))
    interz = interzise(ex_calc)
    for p in citeste_jsonl(rad / CALCULE_S120):
        interz.add((p["numere"][0], p["numere"][1], p["tip"]))
    inm = sorted({(p["a"], p["b"]) for p in ex_calc["perechi"] if p["operatie"] == "inmultire"})
    return interz, inm


def interzise_examen(examen: dict[str, Any]) -> set[tuple[int, int, str]]:
    """Perechile de numere ale acestui examen (a, b, operația), interzise în generatorul S124."""
    return {(p["a"], p["b"], p["operatie"]) for p in examen["perechi"] if p["parte"] == "calcul"}


# --------------------------------------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Examenul de formulări (S124): formulări nevăzute la antrenare.")
    sub = parser.add_subparsers(dest="comanda", required=True)
    c = sub.add_parser("construieste")
    c.add_argument("--iesire", default=str(RADACINA / EXAMEN))
    c.add_argument("--radacina", default=str(RADACINA))
    m = sub.add_parser("model")
    m.add_argument("--experiment", type=int, required=True)
    m.add_argument("--iesire", required=True)
    m.add_argument("--examen", default=EXAMEN)
    m.add_argument("--simboluri", type=int, default=80)
    m.add_argument("--dispozitiv", default="cpu")
    m.add_argument("--director-lucru", default="lucru")
    a = parser.parse_args(argv)
    iesire = Path(a.iesire)
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja; nu scriu peste.")

    if a.comanda == "construieste":
        from unelte.conversatie_chat import CUVINTE_CHEIE, sha

        t0 = time.time()
        rad = Path(a.radacina)
        interz, inm = interzise_si_inmultire(rad)
        perechi = construieste(random.Random(SAMANTA), interz, inm)
        v = verificari(perechi, interz)
        texte = (t for cale in ANTRENARE_EXISTENTA for t in intrebari_randuri(citeste_jsonl(rad / cale)))
        v["antrenare_existenta"] = bucati_comune(perechi, texte)
        if (any(v["sabloane_care_exista_deja"].values()) or v["perechi_de_numere_interzise"]
                or v["perechi_de_numere_repetate"] or v["sociale_repetate"] or v["rezultate_gresite"]
                or v["antrenare_existenta"]["cu_bucata_de_6"] or v["antrenare_existenta"]["sociale_identice"]
                or len(perechi) != 200):
            raise SystemExit(f"verificarea examenului a picat: {json.dumps(v, ensure_ascii=False)}")
        iesire.parent.mkdir(parents=True, exist_ok=True)
        iesire.write_bytes(json.dumps({
            "nota": "S124 (C-132, 17 nov 2026): examenul de formulări ținut deoparte, întrebări FĂRĂ text alături, în "
                    "forma filei Chat; toate formulările sunt noi (nici în generatoarele S116/S120/S124, nici în "
                    "examenele vechi; nicio bucată de 6 cuvinte comună cu antrenarea). Calcule: corect ca "
                    "examen_calcule.py; sociale: corect = o expresie din `cuvinte_cheie` a categoriei (ca partea (b) "
                    "din examen_chat.py). Scorul = calcule + sociale din 200; procentul = scorul / 2. Numerele "
                    "calculelor nu apar în nicio antrenare (vezi docstring-ul din unelte/examen_formulari.py).",
            "samanta": SAMANTA, "cote_calcule": COTE_CALCULE, "cote_sociale": COTE_SOCIALE,
            "sabloane_calcule": SABLOANE_CALCULE, "cuvinte_cheie": CUVINTE_CHEIE, "verificari": v,
            "sha256": {c_: sha(rad / c_) for c_ in ANTRENARE_EXISTENTA + [CALCULE_S120]},
            "secunde": round(time.time() - t0), "perechi": perechi,
        }, ensure_ascii=False, indent=1).encode("utf-8"))
        print(json.dumps({"scris": str(iesire), **{k: v[k] for k in ("calcule", "sociale", "sabloane_calcule_noi")},
                          "antrenare_existenta": {k: (len(x) if isinstance(x, list) else x)
                                                  for k, x in v["antrenare_existenta"].items()}}, ensure_ascii=False))
        return 0

    examen = json.loads((RADACINA / a.examen).read_text(encoding="utf-8"))
    from kronos.jurnal import Jurnal
    from module.model_conversatie import intrebarea
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    t0 = time.time()
    model = incarca_modelul(fisa_modelului(Jurnal(Path(a.director_lucru)), a.experiment), a.dispozitiv)
    raspunsuri: dict[str, str] = {}
    for p in examen["perechi"]:
        raspunsuri[p["id"]] = taie(str(model.completeaza(intrebarea(p["intrebare"]), a.simboluri)))
    nota = noteaza(examen, raspunsuri)
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_bytes(json.dumps({
        "experiment": a.experiment, "examen": a.examen, "dispozitiv": a.dispozitiv, "simboluri": a.simboluri,
        "nota": nota, "secunde": round(time.time() - t0),
        "raspunsuri": [{"id": p["id"], "parte": p["parte"], "categorie": p["categorie"], "intrebare": p["intrebare"],
                        "raspuns": raspunsuri[p["id"]],
                        "corect": corect(p, raspunsuri[p["id"]], examen["cuvinte_cheie"])} for p in examen["perechi"]],
    }, ensure_ascii=False, indent=1).encode("utf-8"))
    print(json.dumps({"experiment": a.experiment, **{k: nota[k] for k in ("total", "procent", "calcule", "sociale")},
                      "secunde": round(time.time() - t0)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
