"""E1 „întrebări născute de Kronos” (S17, 22 octombrie 2026; direcția aprobată de Adrian pe 22 oct 01:45, §8 din
docs/rapoarte/2026-10-22_0200_strategie_nucleu_fara_llm.md): Kronos își face singur întrebări de tipuri noi și le
verifică fără niciun model străin.

Pașii (fiecare e o comandă; `noaptea` le rulează pe toate, unul după altul, și se oprește la prima eroare):
  articole        pe procesor: 2.000 de articole Wikipedia noi (după cele 16.000 de antrenare și cele 280 puse deoparte
                  de unelte/conversatie_text.py, sămânța 1019), cu verificarea automată „0 texte de examen”;
  date-generator  pe procesor: perechile (text, bucată) → întrebare, din antrenările existente (text, text_v2, text_v3):
                  „bucata” e răspunsul, așa cum apare în text (fără „În …” / „.”);
  generator       pe placă: config/e1_generator.toml, 1 oră din #415 (unelte/antrenare_lunga.py, linia w2_e1_generator);
  genereaza       pe placă: pe fiecare articol nou, cel mult 2 bucăți; 8 întrebări pe bucată (temperatura 1,0, nucleu
                  0,9), cel mult --minute minute;
  filtreaza       procesor + placă: filtrele, toate fără LLM, în ordinea asta (cele ieftine întâi, ca dus-întorsul să
                  ruleze doar pe ce a rămas):
                    (0) formă: se termină cu „?”, 3–30 de cuvinte, fără „Text:”/„Răspuns:”, nu conține bucata întreagă
                        (altfel întrebarea își spune singură răspunsul);
                    (iii) fără duplicate;
                    (ii) noutate: primele 4 cuvinte nu apar ca început de întrebare în nicio antrenare; ȘI tiparul
                        (cuvintele dinaintea primului cuvânt cu literă mare sau cifră, cel mult 4) nu apare în nicio
                        antrenare — altfel „Ce este Gușoeni?” ar trece drept tip nou doar pentru că numele e nou;
                    (iv) motorul de română: `verifica_text` fără nicio problemă, în afară de cuvintele necunoscute
                        motorului („ipoteza”, „necunoscut”: nume proprii, cuvinte străine) luate din text;
                    (i) dus-întors: #415 răspunde la întrebare (din text, fără întâmplare) și răspunsul trece
                        verificatorul din S16 (unelte/verificator_text.py) față de bucată (acoperire ≥ 0,8);
                  apoi cel mult 3.300 de întrebări (cât S11), luate pe rând din fiecare tipar (Random(1023)), în
                  date/conversatie/auto_v1/intrebari.jsonl; antrenare.jsonl = text_v3 + ele. Se numără și câte
                  păstrate au același tipar ca o întrebare (b2) din S15 (nu e scurgere: textele de examen nu intră
                  niciodată, verificat; dar spune de unde ar putea veni o creștere la (b2));
  antrenare       pe placă: config/conv_w2_auto_v1.toml, 3 ore din #415 (ca noaptea 12, alte date);
  examene         pe placă: S15 (b2, e), S4 și examenul nopții 10, notate de verificator (fără Qwen), apoi
                  unelte/examen_validari_ws.py (română, cod, povești).

    python -X utf8 unelte/e1_intrebari_nascute.py articole
    python -X utf8 unelte/e1_intrebari_nascute.py date-generator
    python -X utf8 unelte/e1_intrebari_nascute.py noaptea          # pașii de pe placă, în ordine
    python -X utf8 unelte/e1_intrebari_nascute.py examene --experiment 415

Ies: date/conversatie/auto_v1/ (articole.jsonl, generator.jsonl, candidati.jsonl, intrebari.jsonl, antrenare.jsonl,
info.json) și lucru/e1/ (examene_<exp>_<data>.json, noaptea.json). Nu atinge kronos/, examenul BPB, paznicul sau
datele de examen. Licența textelor: Wikipedia, CC BY-SA 4.0.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.verificator_text import _fel_special, cuvinte, normalizeaza, verifica  # noqa: E402

DOSAR = RADACINA / "date" / "conversatie" / "auto_v1"
LUCRU = RADACINA / "lucru" / "e1"
ANTRENARI = ("date/conversatie/text/antrenare.jsonl", "date/conversatie/text_v2/antrenare.jsonl",
             "date/conversatie/text_v3/antrenare.jsonl")
TEXT_V3 = "date/conversatie/text_v3/antrenare.jsonl"
EXAMENE = {"S15": "docs/conversatie/examen_generalizare_mare.json",
           "S4": "docs/conversatie/examen_generalizare_401.json",
           "noaptea10": "date/conversatie/text/examen.json"}
CONFIG_GENERATOR = "config/e1_generator.toml"
CONFIG_ANTRENARE = "config/conv_w2_auto_v1.toml"
LINIE_GENERATOR = "w2_e1_generator"
LINIE_ANTRENARE = "w2_conv_auto_v1"
ELEV = 415
# Câte articole a ales unelte/conversatie_text.py (16.000 de antrenare + 280 puse deoparte, sămânța 1019): cele noi vin după.
FOLOSITE = 16000 + 280
CERERE = "Pune o întrebare la care răspunsul este: {b}"
MAX_PASTRATE = 3300
_PREFIXE = ("În ", "Pe ", "Din ", "Cu ", "Al ", "La ", "De ", "Prin ")
_PREPOZITII = {"de", "în", "din", "la", "pe", "cu", "lui", "prin", "pentru", "între", "după"}
_MARE_SAU_CIFRA = re.compile(r"^[A-ZĂÂÎȘȚ0-9„\"(]")


def _citeste_jsonl(cale: str | Path) -> list[dict[str, Any]]:
    return [json.loads(r) for r in Path(RADACINA / cale).read_text(encoding="utf-8").splitlines() if r.strip()]


def _scrie_jsonl(cale: Path, randuri: Iterable[dict[str, Any]]) -> int:
    cale.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with cale.open("w", encoding="utf-8") as f:
        for r in randuri:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    return n


# ---- tipare și noutate ---------------------------------------------------------------------------------------------

def inceput(intrebare: str, n: int = 4) -> str:
    """Primele n cuvinte, ca în unelte/conversatie_text.py (_inceput): litere mici, fără „?” și „,”."""
    from unelte.conversatie_text import _inceput

    return _inceput(intrebare, n)


def tipar(intrebare: str, n: int = 4) -> str:
    """Cuvintele dinaintea primului cuvânt cu literă mare sau cifră (în afară de primul cuvânt), cel mult n, litere mici:
    „Cine a regizat Mărturie mortală?” → „cine a regizat”; „Ce este Gușoeni?” → „ce este”."""
    cuv = intrebare.replace("?", " ").replace(",", " ").split()
    luate: list[str] = []
    for i, c in enumerate(cuv):
        if i and _MARE_SAU_CIFRA.match(c):
            break
        luate.append(c.lower())
        if len(luate) >= n:
            break
    return " ".join(luate)


def inceputuri_antrenare(antrenari: list[list[dict[str, Any]]]) -> tuple[set[str], set[str]]:
    """(începuturile de 4 cuvinte, tiparele) ale tuturor întrebărilor din antrenări."""
    toate = [p["intrebare"] for a in antrenari for p in a]
    return {inceput(q) for q in toate}, {tipar(q) for q in toate}


# ---- bucăți --------------------------------------------------------------------------------------------------------

def bucata_din_raspuns(text: str, raspuns: str) -> str | None:
    """Răspunsul de antrenare, așa cum apare în text: fără punctul de la final și, dacă trebuie, fără „În …”/„Din …”
    din față (și cu prima literă mică, dacă așa e în text). None dacă nu se găsește în text."""
    r = raspuns.strip().rstrip(".").strip()
    variante = [r]
    for p in _PREFIXE:
        if r.startswith(p):
            variante.append(r[len(p):])
    for v in list(variante):
        if v[:1].isupper():
            variante.append(v[:1].lower() + v[1:])
    for v in variante:
        if v and len(v.split()) >= 1 and v in text:
            return v
    return None


def bucati_candidate(text: str) -> list[str]:
    """Bucățile din care se pot face întrebări: propozițiile (4–25 de cuvinte), bucățile dintre virgule (1–8 cuvinte) și
    ce urmează după o prepoziție (1–5 cuvinte). Fără paranteze, fără bucăți doar din cuvinte mici."""
    from unelte.conversatie_text import _PARANTEZA
    from unelte.conversatie_wikipedia import _PROPOZITII

    fara = _PARANTEZA.sub("", text)
    gasite: list[str] = []
    for prop in _PROPOZITII.split(fara):
        prop = prop.strip().rstrip(".!?").strip()
        if 4 <= len(prop.split()) <= 25:
            gasite.append(prop)
        for seg in re.split(r"[,;:]", prop):
            w = seg.split()
            if 1 <= len(w) <= 8:
                gasite.append(" ".join(w))
            for i, x in enumerate(w[:-1]):
                if x.lower() in _PREPOZITII and 1 <= len(w) - i - 1 <= 5:
                    gasite.append(" ".join(w[i + 1:]))
    bune: list[str] = []
    for b in gasite:
        b = b.strip(" „”\"'-–")
        if (b and b not in bune and any(len(c) >= 3 or c.isdigit() for c in b.split()) and b in text
                and b.count("„") == b.count("”") and b.count("(") == b.count(")")):
            bune.append(b)
    return bune


# ---- articole și datele generatorului ------------------------------------------------------------------------------

def articole_noi(cate: int = 2000) -> list[dict[str, Any]]:
    """Articole noi: aceeași alegere ca unelte/conversatie_text.py (sămânța 1019), dar mai multe; primele FOLOSITE sunt
    exact cele de atunci (16.000 de antrenare + 280 puse deoparte), deci le iau pe cele de după."""
    from unelte.conversatie_text import articole_bune
    from unelte.conversatie_wikipedia import SURSA
    from unelte.genereaza_conversatie import bucati_interzise
    from unelte.ortografie_ro import citeste_exceptii, citeste_lista

    rng = random.Random(1019)
    bune = articole_bune(RADACINA / SURSA, bucati_interzise(), citeste_lista(), citeste_exceptii(), 150, 700,
                         FOLOSITE + cate, Counter(), rng)
    return bune[FOLOSITE:FOLOSITE + cate]


def texte_de_examen() -> set[str]:
    """Toate textele din examene: S15, S4, noaptea 10, plus cele 280 de articole puse deoparte."""
    from unelte.examen_generalizare_mare import articole_deoparte

    texte = {a["text"] for a in articole_deoparte()}
    for cale in EXAMENE.values():
        texte |= {p["text"] for p in json.loads((RADACINA / cale).read_text(encoding="utf-8"))["perechi"] if p.get("text")}
    return texte


def verificari_articole(articole_: list[dict[str, Any]], examen: set[str], antrenari: list[list[dict[str, Any]]]
                        ) -> dict[str, int]:
    """Toate trebuie 0: texte de examen printre articolele noi, texte care sunt deja în vreo antrenare, subiecte repetate."""
    din_antrenare = {p.get("text") for a in antrenari for p in a}
    return {"texte_de_examen": sum(a["text"] in examen for a in articole_),
            "texte_din_antrenare": sum(a["text"] in din_antrenare for a in articole_),
            "subiecte_repetate": len(articole_) - len({a["x"] for a in articole_})}


def date_generator(antrenari: list[list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], Counter[str]]:
    """Perechile generatorului: „Text: … / Întrebare: Pune o întrebare la care răspunsul este: <bucata> / Răspuns:
    <întrebarea>”, din perechile „text” (fără da/nu și fără „Nu scrie”) ale căror răspunsuri se găsesc în text."""
    vazute: set[tuple[str, str]] = set()
    perechi: list[dict[str, Any]] = []
    motive: Counter[str] = Counter()
    for a in antrenari:
        for p in a:
            if p.get("fel") != "text" or not p.get("text") or str(p.get("tip", "")).startswith("da_nu"):
                motive["nu e „text” cu răspuns"] += 1
                continue
            cheie = (p["text"], p["intrebare"])
            if cheie in vazute:
                motive["repetată"] += 1
                continue
            vazute.add(cheie)
            b = bucata_din_raspuns(p["text"], p["raspuns"])
            if b is None:
                motive["răspunsul nu e în text"] += 1
                continue
            perechi.append({"fel": "text", "limba": "ro", "grup": p.get("grup", ""), "text": p["text"],
                            "tip": f"gen_{p.get('tip', '')}", "intrebare": CERERE.format(b=b), "raspuns": p["intrebare"]})
    return perechi, motive


# ---- placa și modelele ---------------------------------------------------------------------------------------------

def paznic_placa(memorie_max: int = 7000, temperatura_max: int = 83) -> None:
    """Oprește (cu excepție) dacă placa trece de 7.000 MB sau de 83 °C. Fără nvidia-smi: nu oprește."""
    from unelte.cascada import placa

    p = placa()
    if p and (p["memorie_mb"] >= memorie_max or p["temperatura"] >= temperatura_max):
        raise RuntimeError(f"paznicul S17: placa {p['memorie_mb']} MB, {p['temperatura']} °C — oprit")


def modelul(experiment: int | None = None, linie: str | None = None) -> tuple[Any, dict[str, Any]]:
    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    fisa = fisa_modelului(Jurnal(RADACINA / "lucru"), experiment, linie)
    model = incarca_modelul(fisa)
    if model.tokenizer != "bpe" or model._are_pozitii():
        raise ValueError(f"#{fisa['id']}: generarea de aici știe doar modele BPE fără memorie (ca W2)")
    return model, fisa


def _gata(text: str) -> bool:
    return "\n" in text or "<|endoftext|>" in text


def esantioneaza(model: Any, prompt: str, n: int = 8, max_simboluri: int = 48, temperatura: float = 1.0,
                 nucleu: float = 0.9, generator: Any = None) -> list[str]:
    """n continuări cu întâmplare (temperatura, nucleu), toate din același început (deci un lot fără umplutură); fiecare
    se taie la primul rând nou sau la <|endoftext|>."""
    import torch
    import torch.nn.functional as F
    from unelte.examen_conversatie import taie

    tok, ctx = model.tok, model.setari["context"]
    model.retea.eval()
    x = torch.tensor([tok.codifica(prompt)] * n, dtype=torch.long, device=model.dispozitiv)
    noi: list[list[int]] = [[] for _ in range(n)]
    gata = [False] * n
    with torch.no_grad():
        for _ in range(max_simboluri):
            logits = model.retea(x[:, -ctx:], None)[:, -1, :].float() / temperatura
            prob = F.softmax(logits, dim=-1).cpu()
            sortate, ordine = torch.sort(prob, descending=True, dim=-1)
            cumul = torch.cumsum(sortate, dim=-1)
            sortate[(cumul - sortate) > nucleu] = 0.0
            ales = torch.multinomial(sortate / sortate.sum(dim=-1, keepdim=True), 1, generator=generator)
            urm = ordine.gather(-1, ales)
            x = torch.cat([x, urm.to(model.dispozitiv)], dim=1)
            for i in range(n):
                if not gata[i]:
                    noi[i].append(int(urm[i, 0]))
                    gata[i] = _gata(tok.decodeaza(noi[i]))
            if all(gata):
                break
    return [taie(tok.decodeaza(s)) for s in noi]


def raspunde(model: Any, prompt: str, max_simboluri: int = 80) -> str:
    """Ca model.completeaza (fără întâmplare) + taie, dar se oprește la primul rând nou (dus-întorsul, mai repede)."""
    import torch
    from unelte.examen_conversatie import taie

    tok, ctx = model.tok, model.setari["context"]
    model.retea.eval()
    simboluri = tok.codifica(prompt)
    noi: list[int] = []
    with torch.no_grad():
        for _ in range(max_simboluri):
            idx = torch.tensor([(simboluri + noi)[-ctx:]], dtype=torch.long, device=model.dispozitiv)
            noi.append(int(model.retea(idx, None)[0, -1].argmax().item()))
            if _gata(tok.decodeaza(noi)):
                break
    return taie(tok.decodeaza(noi))


# ---- generarea -----------------------------------------------------------------------------------------------------

def alege_bucati(articole_: list[dict[str, Any]], pe_articol: int, rng: random.Random) -> list[dict[str, Any]]:
    """Cel mult `pe_articol` bucăți pe articol, la întâmplare; în ordinea: prima bucată a fiecărui articol, apoi a doua
    (dacă timpul se termină, toate articolele au măcar una)."""
    alese: list[list[dict[str, Any]]] = []
    for i, a in enumerate(articole_):
        c = bucati_candidate(a["text"])
        alese.append([{"articol": i, "text": a["text"], "x": a["x"], "bucata": b}
                      for b in rng.sample(c, min(pe_articol, len(c)))])
    return [lista[k] for k in range(pe_articol) for lista in alese if k < len(lista)]


def genereaza(generator_exp: int | None, minute: float, pe_bucata: int = 8, pe_articol: int = 2,
              samanta: int = 1022) -> dict[str, Any]:
    import torch
    from module.model_conversatie import intrebarea

    articole_ = _citeste_jsonl(DOSAR / "articole.jsonl")
    bucati = alege_bucati(articole_, pe_articol, random.Random(samanta))
    model, fisa = modelul(generator_exp, None if generator_exp else LINIE_GENERATOR)
    gen = torch.Generator(device="cpu").manual_seed(samanta)
    start = time.perf_counter()
    candidati: list[dict[str, Any]] = []
    facute = 0
    for k, b in enumerate(bucati):
        if time.perf_counter() - start > minute * 60:
            break
        if k % 200 == 0:
            paznic_placa()
            print(f"generare: {k}/{len(bucati)} bucăți, {len(candidati)} întrebări, "
                  f"{(time.perf_counter() - start) / 60:.1f} min", flush=True)
        prompt = intrebarea(CERERE.format(b=b["bucata"]), b["text"])
        for q in esantioneaza(model, prompt, pe_bucata, generator=gen):
            candidati.append({**b, "intrebare": q})
        facute += 1
    _scrie_jsonl(DOSAR / "candidati.jsonl", candidati)
    rez = {"generator": fisa["id"], "bucati_posibile": len(bucati), "bucati_facute": facute,
           "articole_atinse": len({b["articol"] for b in bucati[:facute]}), "intrebari": len(candidati),
           "minute": round((time.perf_counter() - start) / 60, 1), "pe_bucata": pe_bucata, "temperatura": 1.0,
           "nucleu": 0.9, "samanta": samanta}
    _actualizeaza_info({"generare": rez})
    print(json.dumps(rez, ensure_ascii=False), flush=True)
    return rez


# ---- filtrele ------------------------------------------------------------------------------------------------------

def forma_buna(intrebare: str, bucata: str) -> bool:
    """(0): se termină cu „?”, 3–30 de cuvinte, fără etichetele formatului, nu-și conține bucata (răspunsul) întreagă."""
    q = intrebare.strip()
    if not q.endswith("?") or not 3 <= len(q.split()) <= 30:
        return False
    if any(e in q for e in ("Text:", "Întrebare:", "Răspuns:", "<|")):
        return False
    b = normalizeaza(bucata)
    return not (b and f" {b} " in f" {normalizeaza(q)} ")


NECUNOSCUTE = ("ipoteza", "necunoscut")


def motor_ok(motor: Any, intrebare: str, text: str = "") -> bool:
    """(iv): verifica_text fără nicio problemă; singura excepție: cuvinte pe care motorul nu le știe („ipoteza”,
    „necunoscut”: nume proprii, cuvinte străine) DAR care sunt luate din text. Un cuvânt necunoscut inventat cade."""
    for p in motor.verifica_text(intrebare)["probleme"]:
        if p["tip"] not in NECUNOSCUTE or not p.get("cuvinte") or any(c not in text for c in p["cuvinte"]):
            return False
    return True


def filtre_ieftine(candidati: list[dict[str, Any]], inceputuri: set[str], tipare: set[str], motor: Any
                   ) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """(0), (iii), (ii), (iv), în ordinea asta; câte cad la fiecare (din ce a rămas după cele de dinainte)."""
    cazute = {"0_forma": 0, "iii_duplicat": 0, "ii_noutate_4_cuvinte": 0, "ii_noutate_tipar": 0, "iv_motor": 0}
    vazute: set[str] = set()
    raman: list[dict[str, Any]] = []
    for c in candidati:
        q = c["intrebare"]
        if not forma_buna(q, c["bucata"]):
            cazute["0_forma"] += 1
            continue
        cheie = normalizeaza(q)
        if cheie in vazute:
            cazute["iii_duplicat"] += 1
            continue
        vazute.add(cheie)
        if inceput(q) in inceputuri:
            cazute["ii_noutate_4_cuvinte"] += 1
            continue
        if tipar(q) in tipare:
            cazute["ii_noutate_tipar"] += 1
            continue
        if not motor_ok(motor, q, c["text"]):
            cazute["iv_motor"] += 1
            continue
        raman.append(c)
    return raman, cazute


def raspuns_de_antrenare(bucata: str) -> str:
    b = bucata.strip()
    b = b[:1].upper() + b[1:]
    return b if b.endswith((".", "!", "?")) else b + "."


def alege_pe_tipare(intrebari: list[dict[str, Any]], cate: int, rng: random.Random) -> list[dict[str, Any]]:
    """Cel mult `cate`, luate pe rând din fiecare tipar (câte una din fiecare, apoi a doua…), ca să rămână cât mai multe
    tipuri; în fiecare tipar, ordinea e la întâmplare."""
    grupe: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for q in intrebari:
        grupe[tipar(q["intrebare"])].append(q)
    chei = sorted(grupe)
    rng.shuffle(chei)
    for k in chei:
        rng.shuffle(grupe[k])
    alese: list[dict[str, Any]] = []
    runda = 0
    while len(alese) < cate and any(runda < len(grupe[k]) for k in chei):
        for k in chei:
            if runda < len(grupe[k]) and len(alese) < cate:
                alese.append(grupe[k][runda])
        runda += 1
    return alese


def tipuri(intrebari: list[dict[str, Any]]) -> dict[str, Any]:
    pe4 = Counter(inceput(q["intrebare"]) for q in intrebari)
    pet = Counter(tipar(q["intrebare"]) for q in intrebari)
    return {"tipuri_4_cuvinte": len(pe4), "tipuri_tipar": len(pet), "cele_mai_dese_tipare": pet.most_common(40)}


def filtreaza(elev: int, minute: float) -> dict[str, Any]:
    from module.limba_romana.motor import Motor
    from module.model_conversatie import intrebarea

    candidati = _citeste_jsonl(DOSAR / "candidati.jsonl")
    antrenari = [_citeste_jsonl(c) for c in ANTRENARI]
    inceputuri, tipare = inceputuri_antrenare(antrenari)
    raman, cazute = filtre_ieftine(candidati, inceputuri, tipare, Motor())
    print(f"filtrele ieftine: {len(candidati)} → {len(raman)} ({cazute})", flush=True)
    model, fisa = modelul(elev)
    start = time.perf_counter()
    trec: list[dict[str, Any]] = []
    neincercate = 0
    for k, c in enumerate(raman):
        if time.perf_counter() - start > minute * 60:
            neincercate = len(raman) - k
            break
        if k % 500 == 0:
            paznic_placa()
            print(f"dus-întors: {k}/{len(raman)}, trec {len(trec)}", flush=True)
        r = raspunde(model, intrebarea(c["intrebare"], c["text"]))
        v = verifica(c["bucata"], r)
        if v["corect"]:
            trec.append({**c, "raspuns_elev": r, "acoperire": v["acoperire"]})
    cazute["i_dus_intors"] = len(raman) - neincercate - len(trec)
    pastrate = alege_pe_tipare(trec, MAX_PASTRATE, random.Random(1023))
    perechi = [{"fel": "text", "limba": "ro", "grup": f"auto_{q['articol']}", "text": q["text"], "tip": "auto",
                "intrebare": q["intrebare"], "raspuns": raspuns_de_antrenare(q["bucata"])} for q in pastrate]
    _scrie_jsonl(DOSAR / "intrebari.jsonl", perechi)
    v3 = _citeste_jsonl(TEXT_V3)
    toate = v3 + perechi
    random.Random(1024).shuffle(toate)
    _scrie_jsonl(DOSAR / "antrenare.jsonl", toate)
    examen = texte_de_examen()
    b2 = [p for p in json.loads((RADACINA / EXAMENE["S15"]).read_text(encoding="utf-8"))["perechi"]
          if p.get("categorie") == "b2"]
    tipare_b2 = {tipar(p["intrebare"]) for p in b2}
    rez = {"elev": fisa["id"],
           "pastrate_cu_tipar_din_b2": dict(Counter(t for t in (tipar(p["intrebare"]) for p in perechi) if t in tipare_b2)), "candidati": len(candidati), "dupa_filtrele_ieftine": len(raman), "cazute": cazute,
           "dus_intors_neincercate_timp": neincercate, "trec_toate": len(trec), "pastrate": len(perechi),
           "minute_dus_intors": round((time.perf_counter() - start) / 60, 1),
           "tipuri_dupa_filtre": tipuri(trec), "tipuri_pastrate": tipuri(pastrate),
           "verificari": {"texte_de_examen_in_pastrate": sum(p["text"] in examen for p in perechi),
                          "inceput_din_antrenare_in_pastrate": sum(inceput(p["intrebare"]) in inceputuri for p in perechi)},
           "antrenare": {"text_v3": len(v3), "auto_v1": len(perechi), "total": len(toate)}}
    _actualizeaza_info({"filtre": rez})
    print(json.dumps({k: v for k, v in rez.items() if k not in ("tipuri_dupa_filtre",)}, ensure_ascii=False), flush=True)
    return rez


# ---- examenele (notate de verificator) -----------------------------------------------------------------------------

def noteaza(intrebari: list[dict[str, Any]]) -> dict[str, Any]:
    """Pe fiecare grup (categoria din S15/S4, felul la noaptea 10): câte sunt și câte corecte după verificator; plus
    „Nu scrie în text.” spus pe nedrept (la întrebări care nu sunt „Nu scrie”) și „Da./Nu.” spus la întrebări care nu
    sunt da/nu. Conversația simplă (noaptea 10) nu se notează de verificator: doar se numără."""
    n: Counter[str] = Counter()
    corecte: Counter[str] = Counter()
    nu_scrie_pe_nedrept = 0
    da_nu_gresit = 0
    for p in intrebari:
        g = p.get("categorie") or p["fel"]
        n[g] += 1
        if p["fel"] == "conversatie":
            continue
        v = verifica(p["raspuns"], p["raspuns_elev"])
        p["verificator"] = {k: v[k] for k in ("corect", "motiv", "acoperire")}
        corecte[g] += v["corect"]
        fel = _fel_special(p["raspuns"])
        if fel != "nu_scrie" and v["motiv"] == "refuz":
            nu_scrie_pe_nedrept += 1
        if fel not in ("da", "nu") and (cuvinte(p["raspuns_elev"])[:1] in (["da"], ["nu"])) \
                and not normalizeaza(p["raspuns_elev"]).startswith("nu scrie"):
            da_nu_gresit += 1
    return {"intrebari": dict(n), "corecte": dict(corecte), "nu_scrie_pe_nedrept": nu_scrie_pe_nedrept,
            "da_nu_gresit": da_nu_gresit}


def examene(experiment: int | None, linie: str | None = None, max_simboluri: int = 80, cate: int = 0) -> dict[str, Any]:
    """Examenele S15, S4, noaptea 10 pe un model, cu răspunsurile date exact ca în unelte/examen_conversatie.py
    (model.completeaza, fără întâmplare, 80 de simboluri, taie), notate de verificator. Fără Qwen."""
    import torch
    from module.model_conversatie import intrebarea
    from unelte.examen_conversatie import taie

    model, fisa = modelul(experiment, linie)
    rez: dict[str, Any] = {"experiment": fisa["id"], "linie": fisa["linie"], "creat": datetime.now().isoformat(timespec="seconds"),
                           "judecator": "unelte/verificator_text.py (S16), fără Qwen"}
    for nume, cale in EXAMENE.items():
        paznic_placa()
        intrebari = [dict(p) for p in json.loads((RADACINA / cale).read_text(encoding="utf-8"))["perechi"]]
        intrebari = intrebari[:cate] if cate else intrebari
        for p in intrebari:
            p["raspuns_elev"] = taie(model.completeaza(intrebarea(p["intrebare"], p.get("text", "")), max_simboluri))
        rez[nume] = {"examen": cale, **noteaza(intrebari), "raspunsuri": intrebari}
        print(f"#{fisa['id']} {nume}: {rez[nume]['corecte']} din {rez[nume]['intrebari']}, „Nu scrie” pe nedrept "
              f"{rez[nume]['nu_scrie_pe_nedrept']}, „Da./Nu.” greșit {rez[nume]['da_nu_gresit']}", flush=True)
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    LUCRU.mkdir(parents=True, exist_ok=True)
    iesire = LUCRU / f"examene_{fisa['id']}_{datetime.now():%Y%m%d_%H%M%S}.json"
    iesire.write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    print("scris:", iesire.relative_to(RADACINA).as_posix(), flush=True)
    return rez


# ---- info și noaptea -----------------------------------------------------------------------------------------------

def _actualizeaza_info(bucata: dict[str, Any]) -> None:
    cale = DOSAR / "info.json"
    info = json.loads(cale.read_text(encoding="utf-8")) if cale.exists() else {}
    info.update(bucata)
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")


def _python() -> list[str]:
    return [sys.executable, "-X", "utf8"]


def _ruleaza(pas: str, comanda: list[str], jurnal_noapte: dict[str, Any]) -> None:
    print(f"\n=== S17 {datetime.now():%H:%M:%S} — {pas}: {' '.join(comanda)}", flush=True)
    start = datetime.now()
    cod = subprocess.call(comanda, cwd=RADACINA)
    jurnal_noapte["pasi"].append({"pas": pas, "comanda": comanda, "inceput": start.isoformat(timespec="seconds"),
                                  "sfarsit": datetime.now().isoformat(timespec="seconds"), "cod": cod})
    LUCRU.mkdir(parents=True, exist_ok=True)
    (LUCRU / "noaptea.json").write_text(json.dumps(jurnal_noapte, ensure_ascii=False, indent=1), encoding="utf-8")
    if cod != 0:
        raise SystemExit(f"S17: pasul „{pas}” a ieșit cu codul {cod}; mă opresc aici")


def noaptea(minute_generare: float, minute_dus_intors: float) -> int:
    """Pașii de pe placă, unul după altul; la prima eroare, oprire (codul pasului, în lucru/e1/noaptea.json)."""
    jurnal_noapte: dict[str, Any] = {"inceput": datetime.now().isoformat(timespec="seconds"), "pasi": []}
    unealta = str(Path(__file__).relative_to(RADACINA))
    lunga = "unelte/antrenare_lunga.py"
    _ruleaza("generator", _python() + [lunga, "--config", CONFIG_GENERATOR, "--ore", "1", "--porneste-din", str(ELEV)],
             jurnal_noapte)
    _ruleaza("genereaza", _python() + [unealta, "genereaza", "--minute", str(minute_generare)], jurnal_noapte)
    _ruleaza("filtreaza", _python() + [unealta, "filtreaza", "--minute", str(minute_dus_intors)], jurnal_noapte)
    info = json.loads((DOSAR / "info.json").read_text(encoding="utf-8"))
    if info["filtre"]["pastrate"] == 0:
        raise SystemExit("S17: nicio întrebare n-a trecut filtrele; nu antrenez (rezultatul se raportează așa)")
    _ruleaza("antrenare", _python() + [lunga, "--config", CONFIG_ANTRENARE, "--ore", "3", "--porneste-din", str(ELEV)],
             jurnal_noapte)
    _ruleaza("examene", _python() + [unealta, "examene", "--linie", LINIE_ANTRENARE], jurnal_noapte)
    _ruleaza("validari", _python() + ["unelte/examen_validari_ws.py", "--linie", LINIE_ANTRENARE], jurnal_noapte)
    jurnal_noapte["sfarsit"] = datetime.now().isoformat(timespec="seconds")
    (LUCRU / "noaptea.json").write_text(json.dumps(jurnal_noapte, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n=== S17 gata la {datetime.now():%H:%M:%S}", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="E1: întrebări născute de Kronos (S17).")
    parser.add_argument("--dosar", default="", help="alt dosar decât date/conversatie/auto_v1 (pentru probe)")
    sub = parser.add_subparsers(dest="pas", required=True)
    a = sub.add_parser("articole")
    a.add_argument("--cate", type=int, default=2000)
    sub.add_parser("date-generator")
    g = sub.add_parser("genereaza")
    g.add_argument("--generator", type=int, default=None, help="experimentul generatorului (implicit: ultimul de pe linie)")
    g.add_argument("--minute", type=float, default=60)
    g.add_argument("--pe-bucata", type=int, default=8)
    g.add_argument("--pe-articol", type=int, default=2)
    f = sub.add_parser("filtreaza")
    f.add_argument("--elev", type=int, default=ELEV)
    f.add_argument("--minute", type=float, default=45)
    e = sub.add_parser("examene")
    e.add_argument("--experiment", type=int, default=None)
    e.add_argument("--linie", default=None)
    e.add_argument("--cate", type=int, default=0, help="doar primele atâtea întrebări din fiecare examen (probă)")
    n = sub.add_parser("noaptea")
    n.add_argument("--minute-generare", type=float, default=60)
    n.add_argument("--minute-dus-intors", type=float, default=45)
    args = parser.parse_args(argv)
    global DOSAR, LUCRU
    if args.dosar:
        DOSAR = RADACINA / args.dosar
        LUCRU = DOSAR / "lucru_e1"

    if args.pas == "articole":
        articole_ = articole_noi(args.cate)
        antrenari = [_citeste_jsonl(c) for c in ANTRENARI]
        v = verificari_articole(articole_, texte_de_examen(), antrenari)
        _scrie_jsonl(DOSAR / "articole.jsonl", articole_)
        _actualizeaza_info({"articole": {"cate": len(articole_), "verificari": v, "sursa": "wikipedia_ro (CC BY-SA 4.0)",
                                         "pe_tip": dict(Counter(a["tip"] for a in articole_)),
                                         "bucati_candidate_medie": round(sum(len(bucati_candidate(a["text"]))
                                                                             for a in articole_) / max(1, len(articole_)), 1)}})
        print(json.dumps({"articole": len(articole_), "verificari": v}, ensure_ascii=False))
        return 1 if any(v.values()) or len(articole_) < args.cate else 0
    if args.pas == "date-generator":
        perechi, motive = date_generator([_citeste_jsonl(c) for c in ANTRENARI])
        examen = texte_de_examen()
        v = {"texte_de_examen": sum(p["text"] in examen for p in perechi)}
        _scrie_jsonl(DOSAR / "generator.jsonl", perechi)
        _actualizeaza_info({"date_generator": {"perechi": len(perechi), "scoase": dict(motive), "verificari": v,
                                               "pe_tip": dict(Counter(p["tip"] for p in perechi))}})
        print(json.dumps({"perechi": len(perechi), "scoase": dict(motive), "verificari": v}, ensure_ascii=False))
        return 1 if v["texte_de_examen"] else 0
    if args.pas == "genereaza":
        genereaza(args.generator, args.minute, args.pe_bucata, args.pe_articol)
        return 0
    if args.pas == "filtreaza":
        filtreaza(args.elev, args.minute)
        return 0
    if args.pas == "examene":
        examene(args.experiment, args.linie, cate=args.cate)
        return 0
    return noaptea(args.minute_generare, args.minute_dus_intors)


if __name__ == "__main__":
    raise SystemExit(main())
