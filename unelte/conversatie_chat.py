"""S116 (C-126 A1, 16 nov 2026): date de conversație FĂRĂ text alături, făcute automat (reguli și șabloane scrise de noi,
din Wikipedia RO deja descărcată — niciun alt AI, nimic descărcat) + examenul de chat ținut deoparte.

Forma fiecărei perechi = exact forma din fila „Chat” a interfeței (S114): „Întrebare: …⏎Răspuns:” fără „Text:” în față
(`module.model_conversatie.intrebarea(intrebare)`); perechile n-au câmpul „text”.

Pașii (fiecare refuză să scrie peste un fișier care există):
    python unelte/conversatie_chat.py candidati   → lucru/conversatie_chat/candidati.jsonl (articolele bune, o trecere)
    python unelte/conversatie_chat.py deoparte    → docs/conversatie/chat_deoparte_titluri.json (~5 %, Random(126))
    python unelte/conversatie_chat.py examen      → docs/conversatie/examen_chat.json (200 + 4 informative)
    python unelte/conversatie_chat.py perechi     → lucru/conversatie_chat/perechi.jsonl + perechi_info.json (Random(1126))
    python unelte/conversatie_chat.py amesteca    → lucru/conversatie_chat/antrenare.jsonl + antrenare_info.json

NU schimbă generatoarele vechi; doar le importă filtrele (conversatie_wikipedia, conversatie_text, conversatie_tipuri,
romana_raspunsuri, genereaza_conversatie).
"""
from __future__ import annotations

import argparse
import hashlib
import json
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

DOSAR = "lucru/conversatie_chat"
CANDIDATI = f"{DOSAR}/candidati.jsonl"
DEOPARTE = "docs/conversatie/chat_deoparte_titluri.json"
EXAMEN = "docs/conversatie/examen_chat.json"
PERECHI = f"{DOSAR}/perechi.jsonl"
ANTRENARE = f"{DOSAR}/antrenare.jsonl"
R2 = "lucru/romana_raspunsuri_r2/antrenare.jsonl"
SAMANTA_DEOPARTE = 126
SAMANTA_GENERATOR = 1126
FRACTIE_DEOPARTE = 0.05
PLAFON_PE_TIP = 1000  # ca la S109

# --------------------------------------------------------------------------------------------------------------------
# Faptele: tipurile, categoria lor la examen și formulările (cel puțin 3 pe tip).
CATEGORIE = {
    "definitie": "ce_este",
    "nascut": "cand", "murit": "cand", "an": "cand",
    "locuitori": "cati", "suprafata": "cati",
    "judet": "unde", "comuna": "unde", "regiune": "unde", "tara": "unde", "oras": "unde",
    "capitala": "cine_ce", "regizat": "cine_ce", "scris": "cine_ce", "fondat": "cine_ce", "dezvoltat": "cine_ce",
    "profesie": "cine_ce", "post": "cine_ce", "functie": "cine_ce", "actori": "cine_ce", "producator": "cine_ce",
    "pictor": "cine_ce", "canal": "cine_ce", "castigator": "cine_ce", "sot": "cine_ce", "premiu": "cine_ce",
    "personaj": "cine_ce",
}
FORMULARI: dict[str, list[str]] = {
    "definitie_ce": ["Ce este {x}?", "Ce e {x}?", "Spune-mi ce este {x}.", "Ce știi despre {x}?"],
    "definitie_om_e": ["Cine este {x}?", "Cine e {x}?", "Spune-mi cine este {x}.", "Ce știi despre {x}?"],
    "definitie_om_a": ["Cine a fost {x}?", "Cine era {x}?", "Spune-mi cine a fost {x}.", "Ce știi despre {x}?"],
    "nascut": ["În ce an s-a născut {x}?", "Când s-a născut {x}?", "În ce an a venit pe lume {x}?"],
    "murit": ["În ce an a murit {x}?", "Când a murit {x}?", "În ce an s-a stins din viață {x}?"],
    "an": ["Din ce an este {x}?", "Când a apărut {x}?", "În ce an a apărut {x}?"],
    "locuitori": ["Câți locuitori are {x}?", "Ce populație are {x}?", "Câți oameni locuiesc în {x}?"],
    "suprafata": ["Ce suprafață are {x}?", "Cât de mare este {x}?", "Ce întindere are {x}?"],
    "judet": ["În ce județ se află {x}?", "În ce județ este {x}?", "{x} se află în ce județ?"],
    "comuna": ["În ce comună se află {x}?", "Din ce comună face parte {x}?", "{x} ține de ce comună?"],
    "regiune": ["În ce regiune se află {x}?", "În ce regiune este {x}?", "{x} se află în ce regiune?"],
    "capitala": ["Ce capitală are {x}?", "Care este capitala pentru {x}?", "Care e orașul capitală pentru {x}?"],
    "regizat": ["Cine a regizat {x}?", "Cine este regizorul pentru {x}?", "Cine a făcut regia pentru {x}?"],
    "scris": ["Cine a scris {x}?", "Cine este autorul pentru {x}?", "Cine e cel care a scris {x}?"],
    "fondat": ["Cine a fondat {x}?", "Cine a înființat {x}?", "Cine este fondatorul pentru {x}?"],
    "dezvoltat": ["Cine a dezvoltat {x}?", "Cine este dezvoltatorul pentru {x}?", "Cine s-a ocupat de dezvoltarea {x}?"],
}
# răspunsul scurt, ca propoziție de chat ({x} = subiectul, {v} = valoarea)
RASPUNS = {
    "nascut": "{x} s-a născut în {v}.", "murit": "{x} a murit în {v}.", "an": "{x} este din {v}.",
    "locuitori": "{x} are {v} locuitori.", "suprafata": "{x} are o suprafață de {v}.",
    "judet": "{x} se află în județul {v}.", "comuna": "{x} se află în comuna {v}.",
    "regiune": "{x} se află în regiunea {v}.", "capitala": "Capitala este {v}.",
    "regizat": "{x} a fost regizat de {v}.", "scris": "{x} a fost scris de {v}.", "fondat": "{x} a fost fondat de {v}.",
    "dezvoltat": "{x} a fost dezvoltat de {v}.",
}

# --------------------------------------------------------------------------------------------------------------------
# Conversația socială. GENERATOR = ce intră la antrenare; EXAMEN_SOCIAL = formulări care NU apar în generator.
SOCIAL_INTREBARI: dict[str, list[str]] = {
    "salut": ["Salut!", "Salut", "Bună!", "Bună", "Bună ziua!", "Bună ziua", "Bună dimineața!", "Bună seara!", "Hei!",
              "Salutare!", "Salut, Kronos!", "Bună, Kronos!", "Hei, Kronos!", "Bună ziua, Kronos!", "Servus!",
              "Salut tuturor!", "Bună ziua, cum merge?"],
    "ce_faci": ["Ce faci?", "Ce mai faci?", "Cum ești?", "Cum te simți?", "Ce mai faci, Kronos?", "Cum îți merge?",
                "Totul bine?", "Ești bine?", "Cum o mai duci?", "Ce faci azi?"],
    "multumesc": ["Mulțumesc!", "Mulțumesc", "Mersi!", "Mersi", "Mulțumesc mult!", "Îți mulțumesc!",
                  "Mulțumesc pentru răspuns!", "Mersi frumos!", "Mulțumesc, Kronos!", "Îți mulțumesc mult!"],
    "la_revedere": ["La revedere!", "La revedere", "Pa!", "Pa", "Pe curând!", "Ne vedem!", "Noapte bună!",
                    "O zi bună!", "Pa, Kronos!", "La revedere, Kronos!", "Plec acum, pa!"],
    "cine_esti": ["Cine ești?", "Cine ești tu?", "Ce ești?", "Ce ești tu?", "Cum te cheamă?", "Cum te numești?",
                  "Care e numele tău?", "Ești un om?", "Ești om sau program?", "Tu cine ești?", "Cine te-a făcut?"],
    "ce_poti": ["Ce poți face?", "Ce știi să faci?", "La ce mă poți ajuta?", "Cu ce mă poți ajuta?",
                "Ce poți face pentru mine?", "Ce întrebări pot să îți pun?", "Ce fel de întrebări știi?",
                "Cum mă poți ajuta?"],
    "nu_stiu": ["La ce număr mă gândesc acum?", "Ce am mâncat ieri?", "Câți bani am în buzunar?",
                "Cum mă cheamă pe mine?", "Ce vreme va fi mâine la mine acasă?", "Ce culoare are mașina mea?",
                "Câți ani am?", "Unde am lăsat cheile?", "Ce o să mănânc diseară?", "Cine va câștiga meciul de mâine?",
                "Ce număr va ieși la loto săptămâna viitoare?", "Ce face acum prietenul meu?",
                "Ce gândește vecinul meu?", "Cât e ceasul la mine acum?", "Ce scrie în scrisoarea din sertarul meu?"],
}
SOCIAL_RASPUNSURI: dict[str, list[str]] = {
    "salut": ["Salut! Cu ce te pot ajuta?", "Bună! Ce vrei să afli?", "Salut! Pune-mi o întrebare.",
              "Bună ziua! Cu ce te pot ajuta?"],
    "ce_faci": ["Sunt bine, mulțumesc! Cu ce te pot ajuta?", "Bine, mulțumesc. Tu ce faci?",
                "Sunt un program, dar merg bine. Ce vrei să afli?"],
    "multumesc": ["Cu plăcere!", "Cu plăcere! Mai ai o întrebare?", "Nicio problemă, cu plăcere!"],
    "la_revedere": ["La revedere! O zi bună!", "Pa! Pe curând!", "La revedere! Mai vorbim."],
    "cine_esti": ["Sunt Kronos, un model mic de limbă română, făcut de la zero.",
                  "Mă numesc Kronos. Sunt un model mic de limbă română, făcut de la zero.",
                  "Sunt Kronos, un program care scrie în română. Am fost făcut de la zero."],
    "ce_poti": ["Pot răspunde la întrebări scurte în română, mai ales despre lucruri din enciclopedie.",
                "Pot să răspund la întrebări scurte în română și să găsesc răspunsul într-un text pe care mi-l dai.",
                "Răspund la întrebări scurte în română. Cu un text alături, răspund mai bine."],
    "nu_stiu": ["Nu știu. Nu am de unde să știu asta.", "Nu știu asta.", "Nu pot să știu asta, îmi pare rău."],
}
EXAMEN_SOCIAL: dict[str, list[str]] = {
    "salut": ["Salut, ce zici?", "Bună, mă auzi?", "Hei, e cineva aici?", "Bună seara, Kronos!", "Salutări!",
              "Neața!", "Bună dimineața, Kronos!", "Ziua bună!"],
    "ce_faci": ["Cum merg treburile?", "Cum a fost ziua ta?", "Ești în formă azi?", "Ce mai e nou cu tine?",
                "Cum stai cu sănătatea?", "Te simți bine azi?", "Cum te mai simți, Kronos?"],
    "multumesc": ["Mulțumiri!", "Îți sunt recunoscător!", "Mersi mult de ajutor!", "Mulțumesc frumos!",
                  "Apreciez, mersi!", "Mii de mulțumiri!", "Mulțumesc pentru ajutor, Kronos!"],
    "la_revedere": ["Gata, plec.", "Vorbim mâine!", "Pa pa!", "Te las acum, la revedere!", "Rămâi cu bine!",
                    "Ne auzim mai târziu!", "Somn ușor!"],
    "cine_esti": ["Cu cine vorbesc?", "Spune-mi ceva despre tine.", "Ce fel de program ești?", "Ești robot?",
                  "Cine te-a creat?", "Prezintă-te, te rog.", "Ce nume ai?"],
    "ce_poti": ["La ce ești bun?", "Ce știi tu să faci?", "Cum poți să mă ajuți?", "Ce fel de lucruri poți face?",
                "Mă poți ajuta cu ceva?", "Pentru ce ai fost făcut?", "Ce pot să te întreb?"],
    "nu_stiu": ["Ce culoare are tricoul meu azi?", "Câte pisici am acasă?", "Ce visez la noapte?",
                "Unde mi-am parcat bicicleta?", "Ce scor va fi la meciul de sâmbătă?", "Cum o cheamă pe bunica mea?",
                "Ce număr de telefon are fratele meu?"],
}
# Notarea (b): răspunsul are categoria bună dacă conține (după normalizare) măcar o expresie din lista categoriei.
# Scrise ÎNAINTE de orice rulare a modelului.
CUVINTE_CHEIE: dict[str, list[str]] = {
    "salut": ["salut", "buna", "buna ziua", "buna seara", "buna dimineata", "hei", "salutare", "ziua buna", "neata",
              "cu ce te pot ajuta"],
    "ce_faci": ["sunt bine", "bine", "foarte bine", "merg bine", "ma simt bine", "excelent", "in forma"],
    "multumesc": ["cu placere", "nicio problema", "pentru putin", "oricand", "n ai pentru ce"],
    "la_revedere": ["la revedere", "pa", "pe curand", "o zi buna", "noapte buna", "mai vorbim", "ne vedem",
                    "ne auzim", "cu bine", "somn usor", "drum bun"],
    "cine_esti": ["kronos", "model", "program", "limba romana", "facut de la zero", "inteligenta artificiala", "robot"],
    "ce_poti": ["intrebari", "raspund", "raspunde", "sa raspund", "pot raspunde", "pot sa raspund", "ajut", "text"],
    "nu_stiu": ["nu stiu", "nu pot sa stiu", "nu pot sti", "nu am de unde", "nu cunosc", "nu am cum sa stiu",
                "nu am informatii", "imi pare rau"],
}
INFORMATIVE = ["salut", "Care este capitala României?", "Ce este fotosinteza? Explică pe scurt.",
               "Scrie trei sfaturi pentru un somn mai bun."]
EXAMEN_COTE = {"ce_este": 30, "cand": 30, "cati": 25, "unde": 35, "cine_ce": 30}  # 150 de fapte
SOCIAL_EXAMEN_COTE = {"salut": 8, "ce_faci": 7, "multumesc": 7, "la_revedere": 7, "cine_esti": 7, "ce_poti": 7,
                      "nu_stiu": 7}  # 50


# --------------------------------------------------------------------------------------------------------------------
def sha(cale: Path) -> str:
    h = hashlib.sha256()
    with cale.open("rb") as f:
        while b := f.read(2**20):
            h.update(b)
    return h.hexdigest()


def norm(s: str) -> str:
    from unelte.romana_raspunsuri import norm as n

    return n(s)


def contine(raspuns: str, bucata: str) -> bool:
    from unelte.romana_raspunsuri import contine as c

    return c(raspuns, bucata)


def cheie_subiect(x: str) -> str:
    from unelte.genereaza_conversatie import normalizat

    return normalizat(x)


def _scrie_json(cale: Path, obiect: Any) -> None:
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_bytes(json.dumps(obiect, ensure_ascii=False, indent=1).encode("utf-8"))


def _scrie_jsonl(cale: Path, randuri: list[dict[str, Any]]) -> None:
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_bytes(("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in randuri)).encode("utf-8"))


def citeste_jsonl(cale: Path) -> list[dict[str, Any]]:
    return [json.loads(r) for r in cale.read_text(encoding="utf-8").splitlines() if r.strip()]


# --- candidații ------------------------------------------------------------------------------------------------------
def candidati(radacina: Path, motive: Counter) -> list[dict[str, Any]]:
    """Articolele bune din Wikipedia descărcată, în ordinea din fișier: început curat (`pereche_din`), primul paragraf
    150–700 litere fără alte alfabete, subiect nerepetat, fără bucăți de 8 cuvinte din validări și din examenele vechi
    (aceleași liste ca S109), fără cuvinte necunoscute. „folosit_text” = textul a fost deja la antrenare „din text”
    (linia lui #651) sau are o bucată de 8 cuvinte cu acele texte."""
    from unelte.conversatie_text import _STRAINE, text_din
    from unelte.conversatie_tipuri import bucati_examene, texte_folosite
    from unelte.conversatie_wikipedia import SURSA, articole, pereche_din
    from unelte.genereaza_conversatie import bucati, bucati_interzise
    from unelte.ortografie_ro import citeste_exceptii, citeste_lista, necunoscute

    interzise = bucati_interzise() | bucati_examene(radacina)
    folosite = texte_folosite(radacina)
    for r in citeste_jsonl(radacina / R2):
        if r.get("text"):
            folosite.add(r["text"])
    b_folosite: set[str] = set()
    for t in folosite:
        b_folosite |= bucati(t)
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
        k = cheie_subiect(p["x"])
        if k in vazute:
            motive["subiect repetat"] += 1
            continue
        b = bucati(text)
        if b & interzise:
            motive["bucată dintr-o validare sau dintr-un examen vechi"] += 1
            continue
        if necunoscute(text, cunoscute, exceptii):
            motive["cuvânt necunoscut"] += 1
            continue
        vazute.add(k)
        motive["bune"] += 1
        bune.append({"x": p["x"], "tip": p["tip"], "verb": p["verb"], "prima": p["raspuns"], "definitie": p["intrebare"],
                     "text": text, "folosit_text": text in folosite or bool(b & b_folosite)})
    return bune


# --- faptele unui articol ---------------------------------------------------------------------------------------------
def _formulari_definitie(a: dict[str, Any]) -> list[str]:
    if a["tip"] != "om":
        return FORMULARI["definitie_ce"]
    return FORMULARI["definitie_om_a" if a["verb"] in ("a fost", "au fost") else "definitie_om_e"]


def fapte_din(a: dict[str, Any]) -> list[dict[str, Any]]:
    """Toate faptele unui articol: {"tip", "categorie", "formulari", "raspuns", "cheie"}; cheia apare în articol
    (la „definitie”: cuvântul-gen din prima propoziție)."""
    from unelte.conversatie_text import intrebari_din_text
    from unelte.conversatie_tipuri import GENERATOR, extrage
    from unelte.romana_raspunsuri import scurtata, substantiv, valoare_cheie

    x, text = a["x"], a["text"]
    fapte: list[dict[str, Any]] = []
    for q in intrebari_din_text(text, x, a["tip"], a["prima"], a["definitie"]):
        t = q["tip"]
        if t == "definitie":
            gen = substantiv(a["prima"])
            s = scurtata(a["prima"], 20, la_virgula=True)
            if gen and s and contine(s, gen):
                fapte.append({"tip": "definitie", "formulari": _formulari_definitie(a), "raspuns": s, "cheie": gen})
            continue
        if t not in RASPUNS:
            continue
        if t in ("judet", "comuna", "regiune"):
            v = re.sub(r"^În (?:județul|comuna|regiunea) ", "", q["raspuns"]).rstrip(".")
        elif t in ("nascut", "murit", "an", "locuitori"):
            v = valoare_cheie(q["raspuns"])
        else:
            v = q["raspuns"].rstrip(".")
        if not v or norm(v) not in norm(text):
            continue
        cheie = valoare_cheie(v) if t == "suprafata" else v
        fapte.append({"tip": t, "formulari": FORMULARI[t], "raspuns": RASPUNS[t].format(x=x, v=v), "cheie": cheie})
    for t, felur in GENERATOR.items():
        if t == "personaj":  # are nevoie de al doilea subiect ({y}); fără text alături e prea încâlcit
            continue
        info = extrage(t, text, x, a["tip"], a["verb"])
        if info is None or not felur.get(info["fel"]):
            continue
        formulari = [s.replace("{c}", info.get("c", "")) for s in felur[info["fel"]]]
        fapte.append({"tip": t, "formulari": formulari, "raspuns": info["raspuns"], "cheie": info["cheie"]})
    # răspunsul nu are voie să fie deja în întrebare („Comuna Parchowo … ține de ce comună?” → „Parchowo”)
    fapte = [f for f in fapte if f["tip"] == "definitie" or norm(f["cheie"]) not in norm(x)]
    for f in fapte:
        f["categorie"] = CATEGORIE[f["tip"]]
    return fapte


def _intrebare(sablon: str, x: str) -> str:
    q = sablon.format(x=x)
    return q[0].upper() + q[1:]


# --- pasul 1: titlurile ținute deoparte -------------------------------------------------------------------------------
def alege_deoparte(cand: list[dict[str, Any]], rng: random.Random, fractie: float = FRACTIE_DEOPARTE) -> list[str]:
    """~`fractie` din subiectele candidaților care NU au fost văzute la antrenarea „din text” (ca examenul să fie pe
    lucruri nevăzute), alese la întâmplare; întoarce subiectele (cum scriu în articol), sortate."""
    pool = sorted(a["x"] for a in cand if not a["folosit_text"])
    cate = round(fractie * len(cand))
    return sorted(rng.sample(pool, min(cate, len(pool))))


# --- pasul 2: examenul ---------------------------------------------------------------------------------------------
def construieste_examen(cand: list[dict[str, Any]], deoparte: set[str], rng: random.Random) -> list[dict[str, Any]]:
    """(a) 150 de fapte din articolele ținute deoparte (o întrebare pe articol, cotele EXAMEN_COTE, cel mult 15 pe tip
    în afară de „definitie”); (b) 50 sociale din EXAMEN_SOCIAL; (c) informativ."""
    arts = [a for a in cand if cheie_subiect(a["x"]) in deoparte]
    rng.shuffle(arts)
    pe_cat: dict[str, list] = defaultdict(list)
    pe_tip: Counter = Counter()
    folosite: set[str] = set()
    total = sum(EXAMEN_COTE.values())
    # trecerea 1: cotele pe categorii; trecerea 2: dacă o categorie n-are destule fapte, restul până la 150 din celelalte
    for trecere in (1, 2):
        for a in arts:
            if a["x"] in folosite:
                continue
            fapte = fapte_din(a)
            rng.shuffle(fapte)
            # categoria cea mai rară întâi, ca să se umple toate cotele
            fapte.sort(key=lambda f: len(pe_cat[f["categorie"]]) / EXAMEN_COTE[f["categorie"]])
            for f in fapte:
                c = f["categorie"]
                loc = len(pe_cat[c]) < EXAMEN_COTE[c] if trecere == 1 else sum(map(len, pe_cat.values())) < total
                if loc and (f["tip"] == "definitie" and len(pe_cat[c]) < 2 * EXAMEN_COTE[c] or pe_tip[f["tip"]] < 15):
                    pe_cat[c].append((a, f))
                    pe_tip[f["tip"]] += 1
                    folosite.add(a["x"])
                    break
            if sum(map(len, pe_cat.values())) >= total:
                break
    perechi: list[dict[str, Any]] = []
    for c in EXAMEN_COTE:
        for a, f in pe_cat[c]:
            perechi.append({"parte": "a", "categorie": c, "tip": f["tip"],
                            "intrebare": _intrebare(rng.choice(f["formulari"]), a["x"]),
                            "raspuns_asteptat": f["raspuns"], "cheie": f["cheie"], "subiect": a["x"],
                            "articol": f"wikipedia_ro: {a['x']}", "text_sursa": a["text"]})
    for c, n in SOCIAL_EXAMEN_COTE.items():
        for q in EXAMEN_SOCIAL[c][:n]:
            perechi.append({"parte": "b", "categorie": c, "intrebare": q})
    for q in INFORMATIVE:
        perechi.append({"parte": "c", "categorie": "informativ", "intrebare": q})
    for i, p in enumerate(perechi):
        p["id"] = f"chat_{i:03d}"
    return perechi


# --- pasul 3: perechile de antrenare ------------------------------------------------------------------------------
def _pereche(fel: str, tip: str, intrebare: str, raspuns: str, cheie: str = "", subiect: str = "") -> dict[str, Any]:
    from module.model_conversatie import intrebarea

    return {"fel": fel, "tip": tip, "prompt": intrebarea(intrebare), "intrebare": intrebare, "raspuns": raspuns,
            "cheie": [cheie] if cheie else [], "subiect": subiect}


def perechi_fapte(cand: list[dict[str, Any]], deoparte: set[str], rng: random.Random, plafon: int = PLAFON_PE_TIP
                  ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Întrebări–răspunsuri scurte din articolele care NU sunt ținute deoparte; pe tip cel mult `plafon`; formularea
    aleasă la întâmplare din cele (≥ 3) ale tipului."""
    pe_tip: dict[str, list] = defaultdict(list)
    for a in cand:
        if cheie_subiect(a["x"]) in deoparte:
            continue
        for f in fapte_din(a):
            pe_tip[f["tip"]].append((a, f))
    perechi: list[dict[str, Any]] = []
    numar: dict[str, dict[str, int]] = {}
    for t in sorted(pe_tip):
        lista = pe_tip[t]
        rng.shuffle(lista)
        for a, f in lista[:plafon]:
            perechi.append(_pereche("chat_fapt", t, _intrebare(rng.choice(f["formulari"]), a["x"]), f["raspuns"],
                                    f["cheie"], a["x"]))
        numar[t] = {"disponibile": len(lista), "alese": min(plafon, len(lista))}
    return perechi, numar


def perechi_sociale(rng: random.Random, ori: int = 15) -> list[dict[str, Any]]:
    """Fiecare întrebare socială de `ori` ori (sunt puține: fără repetare s-ar pierde printre fapte), cu un răspuns ales
    la întâmplare din categoria ei; plus salut + „ce faci” lipite („Salut! Ce faci?”), o dată fiecare combinație."""
    perechi = []
    for c, intrebari in SOCIAL_INTREBARI.items():
        for q in intrebari:
            for _ in range(ori):
                perechi.append(_pereche("chat_social", c, q, rng.choice(SOCIAL_RASPUNSURI[c])))
    for s in SOCIAL_INTREBARI["salut"]:
        for f in SOCIAL_INTREBARI["ce_faci"]:
            q = f"{s.rstrip('!')}! {f}" if s.endswith("!") or "," not in s else f"{s} {f}"
            r = f"{rng.choice(['Salut!', 'Bună!'])} {rng.choice(SOCIAL_RASPUNSURI['ce_faci'])}"
            perechi.append(_pereche("chat_social", "salut_ce_faci", q, r))
    return perechi


def perechi_dialog(fapte: list[dict[str, Any]], rng: random.Random, cate: int) -> list[dict[str, Any]]:
    """Conversații pe 2–3 replici în aceeași formă: replicile de dinainte stau în întrebare („Salut!⏎Răspuns: …⏎
    Întrebare: <fapt>”), iar răspunsul e al ultimei replici. Felurile: salut → fapt; salut → fapt → mulțumesc;
    fapt → mulțumesc."""
    perechi = []
    for k in range(cate):
        f = rng.choice(fapte)
        salut, r_salut = rng.choice(SOCIAL_INTREBARI["salut"]), rng.choice(SOCIAL_RASPUNSURI["salut"])
        mersi, r_mersi = rng.choice(SOCIAL_INTREBARI["multumesc"]), rng.choice(SOCIAL_RASPUNSURI["multumesc"])
        fel = k % 3
        if fel == 0:
            q, r, tip = f"{salut}\nRăspuns: {r_salut}\nÎntrebare: {f['intrebare']}", f["raspuns"], "salut_fapt"
        elif fel == 1:
            q = f"{salut}\nRăspuns: {r_salut}\nÎntrebare: {f['intrebare']}\nRăspuns: {f['raspuns']}\nÎntrebare: {mersi}"
            r, tip = r_mersi, "salut_fapt_multumesc"
        else:
            q, r, tip = f"{f['intrebare']}\nRăspuns: {f['raspuns']}\nÎntrebare: {mersi}", r_mersi, "fapt_multumesc"
        perechi.append(_pereche("chat_dialog", tip, q, r, subiect=f.get("subiect", "")))
    return perechi


def bucati_examen(examen: list[dict[str, Any]]) -> set[str]:
    """Bucățile de 8 cuvinte din examen: întrebarea, răspunsul așteptat și textul articolului."""
    from unelte.genereaza_conversatie import bucati

    b: set[str] = set()
    for p in examen:
        for camp in ("intrebare", "raspuns_asteptat", "text_sursa"):
            b |= bucati(p.get(camp, "") or "")
    return b


def bucati_pereche(p: dict[str, Any]) -> set[str]:
    from unelte.genereaza_conversatie import bucati

    return bucati(p["intrebare"]) | bucati(p["raspuns"])


def scoate_scurgeri(perechi: list[dict[str, Any]], examen: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Scoate perechile care au o bucată de 8 cuvinte comună cu examenul sau a căror întrebare (normalizată) e una
    din întrebările NOTATE ale examenului ((a) și (b); cele informative (c), ca „salut”, rămân voie la antrenare:
    sunt exact ce trebuie să învețe chat-ul, iar (c) nu intră în scor)."""
    b_ex = bucati_examen(examen)
    q_ex = {norm(p["intrebare"]) for p in examen if p["parte"] in ("a", "b")}
    bune = [p for p in perechi if not (bucati_pereche(p) & b_ex) and norm(p["intrebare"].split("\n")[-1]
                                                                          .removeprefix("Întrebare: ")) not in q_ex]
    return bune, len(perechi) - len(bune)


def verifica_scurgeri(perechi: list[dict[str, Any]], examen: list[dict[str, Any]]) -> dict[str, int]:
    b_ex = bucati_examen(examen)
    q_ex = {norm(p["intrebare"]) for p in examen if p["parte"] in ("a", "b")}
    q_gen = {norm(p["intrebare"].split("\n")[-1].removeprefix("Întrebare: ")) for p in perechi}
    deop = {cheie_subiect(p["subiect"]) for p in examen if p.get("subiect")}
    return {"perechi_cu_bucata_de_8_din_examen": sum(1 for p in perechi if bucati_pereche(p) & b_ex),
            "intrebari_examen_care_apar_in_generator": len(q_ex & q_gen),
            "perechi_despre_subiecte_din_examen": sum(1 for p in perechi if cheie_subiect(p.get("subiect", "")) in deop
                                                      and p.get("subiect"))}


# --- pasul 4: amestecul ---------------------------------------------------------------------------------------------
def numar_simboluri(perechi: list[dict[str, Any]], tok: Any) -> int:
    from module.model_conversatie import intrebarea, raspunsul

    return sum(len(tok.codifica(intrebarea(p["intrebare"], p.get("text", "")))) + len(tok.codifica(raspunsul(p["raspuns"])))
               for p in perechi)


def ori_pentru_jumatate(simb_noi: int, simb_vechi: int) -> int:
    """De câte ori intră perechile noi ca simbolurile lor să fie cât mai aproape de jumătate (cel puțin o dată)."""
    return max(1, round(simb_vechi / max(1, simb_noi)))


# --------------------------------------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="S116: date de chat fără text alături + examenul de chat.")
    parser.add_argument("pas", choices=["candidati", "deoparte", "examen", "perechi", "amesteca"])
    parser.add_argument("--radacina", default=str(RADACINA))
    a = parser.parse_args(argv)
    rad = Path(a.radacina)
    t0 = time.time()

    if a.pas == "candidati":
        iesire = rad / CANDIDATI
        if iesire.exists():
            raise SystemExit(f"{iesire} există deja.")
        motive: Counter = Counter()
        cand = candidati(rad, motive)
        _scrie_jsonl(iesire, cand)
        from unelte.conversatie_wikipedia import SURSA
        _scrie_json(rad / DOSAR / "candidati_info.json", {
            "candidati": len(cand), "folositi_la_text": sum(a_["folosit_text"] for a_ in cand), "motive": dict(motive),
            "sha256_sursa": sha(rad / SURSA), "secunde": round(time.time() - t0)})
        print(json.dumps({"candidati": len(cand), "secunde": round(time.time() - t0)}, ensure_ascii=False))
        return 0

    cand = citeste_jsonl(rad / CANDIDATI)
    if a.pas == "deoparte":
        iesire = rad / DEOPARTE
        if iesire.exists():
            raise SystemExit(f"{iesire} există deja; titlurile se aleg o singură dată.")
        titluri = alege_deoparte(cand, random.Random(SAMANTA_DEOPARTE))
        _scrie_json(iesire, {
            "nota": "S116 (C-126 A1): subiectele (titlurile) articolelor Wikipedia RO ținute deoparte pentru examenul de "
                    "chat; nicio pereche de antrenare nu se face din ele. ~5 % din candidații buni (filtrele lui "
                    "unelte/conversatie_chat.py candidati), aleși doar dintre cei nevăzuți la antrenarea „din text”, "
                    "cu random.Random(126).",
            "candidati": len(cand), "fractie": FRACTIE_DEOPARTE, "samanta": SAMANTA_DEOPARTE,
            "sha256_candidati": sha(rad / CANDIDATI), "numar": len(titluri), "titluri": titluri})
        print(json.dumps({"titluri": len(titluri), "din": len(cand)}, ensure_ascii=False))
        return 0

    deoparte = {cheie_subiect(t) for t in json.loads((rad / DEOPARTE).read_text(encoding="utf-8"))["titluri"]}
    if a.pas == "examen":
        iesire = rad / EXAMEN
        if iesire.exists():
            raise SystemExit(f"{iesire} există deja; examenul se face o singură dată.")
        perechi = construieste_examen(cand, deoparte, random.Random(SAMANTA_DEOPARTE + 1))
        gen = {norm(q) for qs in SOCIAL_INTREBARI.values() for q in qs}
        verif = {"pe_parte": dict(Counter(p["parte"] for p in perechi)),
                 "a_pe_categorie": dict(Counter(p["categorie"] for p in perechi if p["parte"] == "a")),
                 "a_pe_tip": dict(Counter(p["tip"] for p in perechi if p["parte"] == "a")),
                 "a_cheia_nu_e_in_articol": [p["id"] for p in perechi if p["parte"] == "a" and p["tip"] != "definitie"
                                             and norm(p["cheie"]) not in norm(p["text_sursa"])],
                 "b_formulari_care_sunt_in_generator": [p["intrebare"] for p in perechi if p["parte"] == "b"
                                                        and norm(p["intrebare"]) in gen],
                 "a_subiecte_repetate": sum(c - 1 for c in Counter(p.get("subiect") for p in perechi
                                                                   if p["parte"] == "a").values())}
        if verif["a_cheia_nu_e_in_articol"] or verif["b_formulari_care_sunt_in_generator"] or verif["a_subiecte_repetate"]:
            raise SystemExit(f"verificarea examenului a picat: {verif}")
        _scrie_json(iesire, {
            "nota": "S116 (C-126 A1, 16 nov 2026): examenul de chat ținut deoparte, întrebări FĂRĂ text alături, în forma "
                    "filei Chat. (a) fapte din articolele ținute deoparte (docs/conversatie/chat_deoparte_titluri.json): "
                    "corect = cheia apare în răspunsul modelului (normalizare: diacritice, majuscule, punctuație, cifre "
                    "cu/fără punct; la „definitie” cheia = cuvântul-gen din prima propoziție). (b) sociale, formulări care "
                    "NU apar în generator: corect = răspunsul conține o expresie din `cuvinte_cheie` a categoriei. (c) "
                    "informativ, nenotat. Notarea: unelte/examen_chat.py.",
            "samanta": SAMANTA_DEOPARTE + 1, "sha256_deoparte": sha(rad / DEOPARTE), "cuvinte_cheie": CUVINTE_CHEIE,
            "verificari": verif, "perechi": perechi})
        print(json.dumps({"scris": str(iesire), **verif}, ensure_ascii=False))
        return 0

    examen = json.loads((rad / EXAMEN).read_text(encoding="utf-8"))["perechi"]
    if a.pas == "perechi":
        iesire = rad / PERECHI
        if iesire.exists():
            raise SystemExit(f"{iesire} există deja.")
        rng = random.Random(SAMANTA_GENERATOR)
        fapte, numar = perechi_fapte(cand, deoparte, rng)
        sociale = perechi_sociale(rng)
        dialog = perechi_dialog(fapte, rng, cate=len(fapte) // 10)
        toate = fapte + sociale + dialog
        toate, scoase = scoate_scurgeri(toate, examen)
        rng.shuffle(toate)
        for i, p in enumerate(toate):
            p["id"] = f"chat_{i:06d}"
        _scrie_jsonl(iesire, toate)
        verif = verifica_scurgeri(toate, examen)
        exemple = random.Random(1160).sample(toate, 20)
        _scrie_json(rad / DOSAR / "perechi_info.json", {
            "nota": "S116: perechile de chat fără text alături, random.Random(1126).",
            "pe_fel": dict(Counter(p["fel"] for p in toate)), "pe_tip": dict(Counter(p["tip"] for p in toate)),
            "fapte_pe_tip": numar, "scoase_pentru_scurgeri": scoase, "verificare_scurgeri": verif,
            "exemple_random_1160": exemple, "sha256": {"perechi": sha(iesire), "examen": sha(rad / EXAMEN),
                                                       "deoparte": sha(rad / DEOPARTE)},
            "secunde": round(time.time() - t0)})
        print(json.dumps({"perechi": len(toate), "pe_fel": dict(Counter(p["fel"] for p in toate)), "scoase": scoase,
                          **verif}, ensure_ascii=False))
        return 0

    # amesteca
    iesire = rad / ANTRENARE
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja.")
    from module.tokenizer_bpe import TokenizerBPE

    tok = TokenizerBPE.incarca(rad / "date/ws/bpe_16384.json")
    noi = citeste_jsonl(rad / PERECHI)
    vechi_randuri = [r for r in (rad / R2).read_bytes().decode("utf-8").splitlines() if r.strip()]
    vechi = [json.loads(r) for r in vechi_randuri]
    s_noi, s_vechi = numar_simboluri(noi, tok), numar_simboluri(vechi, tok)
    ori = ori_pentru_jumatate(s_noi, s_vechi)
    randuri = vechi_randuri + [json.dumps(p, ensure_ascii=False) for _ in range(ori) for p in noi]
    random.Random(SAMANTA_GENERATOR + 1).shuffle(randuri)
    iesire.write_bytes(("\n".join(randuri) + "\n").encode("utf-8"))
    _scrie_json(rad / DOSAR / "antrenare_info.json", {
        "nota": "S116: perechile de chat (fără text) de `ori` ori + toate perechile „din text” ale lui #651 "
                "(lucru/romana_raspunsuri_r2/antrenare.jsonl), amestecate cu random.Random(1127).",
        "perechi_noi": len(noi), "ori": ori, "perechi_vechi": len(vechi), "perechi_total": len(randuri),
        "simboluri_noi_o_data": s_noi, "simboluri_noi_total": s_noi * ori, "simboluri_vechi": s_vechi,
        "fractie_noi_dupa_simboluri": round(s_noi * ori / (s_noi * ori + s_vechi), 4),
        "sha256": {"antrenare": sha(iesire), "perechi": sha(rad / PERECHI), "r2": sha(rad / R2)},
        "secunde": round(time.time() - t0)})
    print(json.dumps({"total": len(randuri), "ori": ori,
                      "fractie_noi": round(s_noi * ori / (s_noi * ori + s_vechi), 4)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
