"""Importă intrările în limba română din Wiktionary (ediția engleză), extrase de kaikki.org (JSONL).

Ce intră:
  - `lexeme`: (cuvânt, categorie) cu numărul de etimologie ca număr de omonim (singura sursă care distinge omonimele);
    genul substantivelor; etimologia (moștenit / împrumut din X / slav vechi / necunoscut), etichetele de registru;
  - `forme`: tabelele de flexiune (declinare, conjugare) cu trăsături traduse în inventarul UD; intrările care sunt
    ele însele forme flexionare („caselor” = formă a lui „casă”) devin forme ale lexemului de bază, nu lexeme;
  - `sensuri`: glosele (în engleză — Wiktionary în engleză descrie cuvintele românești în engleză), cu etichete;
  - `relatii_semantice` la nivel de lexem: sinonime, antonime, derivate, înrudite (doar când ținta e în bază).

Ce NU intră (numărat în raport): afixe (prefix/sufix/interfix), caractere, contracțiile scrise cu cratimă
(„s-a” — tokenizatorul le desparte), formele în alfabet chirilic, formele pronumelor/determinanților/numeralelor
(tabelele lor sunt scrise de mână în `morfologie/inchise.py`, cu trăsături UD complete).
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from ..baza import Baza, canonic_trasaturi, desparte_trasaturi
from ..identificatori import id_lexem, id_sens
from ..morfologie.trasaturi import ETICHETE_REGISTRU, canonic_pentru_pos, din_kaikki, gen_lexem_din_kaikki
from ..text import normalizeaza
from .comun import DIR_SURSE, Numarator, manifest_sursa

SURSA_ID = "wiktionary_kaikki"

POS_KAIKKI = {
    "noun": "NOUN", "name": "PROPN", "adj": "ADJ", "verb": "VERB", "adv": "ADV", "intj": "INTJ", "pron": "PRON",
    "det": "DET", "num": "NUM", "prep": "ADP", "conj": "CCONJ", "article": "DET", "particle": "PART",
    "prep_phrase": "ADP", "phrase": "X", "proverb": "X", "postp": "ADP",
}
POS_SARITE = {"suffix", "prefix", "interfix", "character", "contraction", "romanization", "punct", "symbol", "letter"}
POS_FARA_FORME = {"PRON", "DET", "NUM", "ADP", "CCONJ", "SCONJ", "PART"}
SUBORDONATOARE = {"că", "să", "dacă", "deși", "fiindcă", "deoarece", "întrucât", "încât", "căci", "precum", "ca", "decât",
                  "până", "de", "cum", "când", "unde", "cât", "fiindca", "macar", "măcar", "doar", "deoarece", "de vreme ce",
                  "din moment ce", "pentru că", "cu toate că", "chiar dacă", "în caz că", "odată ce", "de parcă", "parcă",
                  "fără să", "înainte să", "după ce", "înainte ca", "ca să", "pentru ca", "numai să", "îndată ce", "ori de câte ori"}
ETICHETE_GRAMATICALE_SENS = {"transitive", "intransitive", "reflexive", "uncountable", "countable", "plural-only", "singular-only",
                             "impersonal", "with-accusative", "with-dative", "with-genitive", "ambitransitive"}
RE_NELATIN = re.compile(r"[Ѐ-ӿͰ-Ͽ]")  # chirilic, grec


def clasifica_etimologie(text: str) -> tuple[str, str]:
    """(origine, limba) din textul etimologic al Wiktionary."""
    t = text.lower()
    if not t:
        return "", ""
    if "inherited from latin" in t or t.startswith("from latin") or t.startswith("from vulgar latin"):
        return "moștenit", "latină"
    m = re.search(r"borrowed from ([a-z ]+?)[ .,]", t)
    if m:
        return "împrumut", m.group(1).strip()
    if "old church slavonic" in t or "proto-slavic" in t or t.startswith("from slavic") or "from old slavic" in t:
        return "slav vechi", "slavă"
    if "unknown" in t[:40] or "uncertain" in t[:40] or "unclear" in t[:40]:
        return "necunoscut", ""
    m = re.search(r"from ([a-z ]+?)[ .,]", t)
    if m:
        return "din", m.group(1).strip()
    return "altă", ""


def categorie(d: dict) -> str | None:
    pos = d.get("pos")
    if pos in POS_SARITE:
        return None
    if pos == "conj":
        return "SCONJ" if normalizeaza(d["word"]) in SUBORDONATOARE else "CCONJ"
    return POS_KAIKKI.get(pos)


def _forme_intrare(d: dict, upos: str, n: Numarator) -> list[tuple[str, dict[str, str], str]]:
    """(formă, trăsături, detalii) pentru formele din tabelele de flexiune ale unei intrări."""
    rezultat: list[tuple[str, dict[str, str], str]] = []
    vazute: set[tuple[str, str]] = set()
    forme = d.get("forms") or []
    for fo in forme:
        forma = fo.get("form", "")
        etichete = fo.get("tags", []) or []
        if not forma or forma == "-" or "table-tags" in etichete or "inflection-template" in etichete or "canonical" in etichete:
            continue
        if RE_NELATIN.search(forma):
            n("forme_chirilice_sarite"); continue
        if "romanization" in etichete:
            continue
        detalii = ""
        if upos == "VERB":
            for prefix, nota in (("a ", "infinitiv fără „a”"), ("să ", "conjunctiv fără „să”"), ("nu ", "imperativ negativ fără „nu”")):
                if forma.startswith(prefix):
                    forma = forma[len(prefix):]
                    detalii = nota
                    break
        if " " in forma and d.get("pos") not in ("phrase", "prep_phrase", "proverb") and not (upos == "VERB" and "a " in forma):
            n("forme_cu_spatiu_sarite"); continue
        if "possessive" in etichete and upos == "PRON":
            continue
        tr, rest = din_kaikki(etichete, upos)
        if "error-unrecognized-form" in etichete:
            detalii = (detalii + "; " if detalii else "") + "etichete parțial nerecunoscute de extractor"
        if "alternative" in etichete:
            detalii = (detalii + "; " if detalii else "") + "variantă (" + ", ".join(e for e in etichete if e in ETICHETE_REGISTRU) + ")"
            tr = {}
        cheie = (forma, canonic_trasaturi(tr))
        if cheie in vazute:
            continue
        vazute.add(cheie)
        rezultat.append((forma, tr, detalii))
    # adjective / participii: Wiktionary nu etichetează cazul; îl deducem din structura tabelului
    if upos in ("ADJ",):
        _deduce_caz_adjectiv(rezultat)
    return rezultat


def _deduce_caz_adjectiv(forme: list[tuple[str, dict[str, str], str]]) -> None:
    grupuri: dict[str, list[int]] = defaultdict(list)
    for i, (forma, tr, _) in enumerate(forme):
        if "Case" in tr or not tr:
            continue
        grupuri[canonic_trasaturi(tr)].append(i)
    fem_pl = next((forme[i][0] for i, (f, tr, _) in enumerate(forme) if tr.get("Gender") == "Fem" and tr.get("Number") == "Plur" and tr.get("Definite") == "Ind"), None)
    for cheie, idx in grupuri.items():
        for i in idx:
            forma, tr, det = forme[i]
            tr = dict(tr)
            if tr.get("Definite") == "Def" and forma.endswith(("lui", "lor", "ei")):
                tr["Case"] = "Dat,Gen"
            elif tr.get("Definite") == "Ind" and tr.get("Gender") == "Fem" and tr.get("Number") == "Sing" and fem_pl and forma == fem_pl and len(idx) > 1:
                tr["Case"] = "Dat,Gen"
            elif "Definite" in tr:
                tr["Case"] = "Acc,Nom"
            forme[i] = (forma, tr, (det + "; " if det else "") + "caz dedus din tabel")


def importa(baza: Baza, cale: Path | None = None, verbos: bool = True, limita: int | None = None) -> dict:
    cale = cale or (DIR_SURSE / "kaikki" / "kaikki.org-dictionary-Romanian.jsonl")
    n = Numarator()
    m = manifest_sursa("kaikki")
    baza.adauga_sursa(
        SURSA_ID, "Wiktionary (ediția engleză), intrările în limba română, extrase de kaikki.org (wiktextract)",
        licenta="CC BY-SA (Wiktionary: 4.0, texte vechi 3.0) + GFDL", url="https://kaikki.org/dictionary/Romanian/",
        versiune="extracție 3 octombrie 2026 din dump-ul enwiktionary din 2 septembrie 2026",
        atribuire="contribuitorii Wiktionary; extracția: Tatu Ylonen (wiktextract)",
        obligatii="atribuire; datele derivate rămân sub CC BY-SA", fisiere=[k for k in m] or [cale.name],
        transformari="JSONL → lexeme (cu omonime după numărul de etimologie), forme din tabelele de flexiune, sensuri (glose în engleză), relații lexicale",
        limitari="glosele sunt în engleză; cazul adjectivelor e dedus din tabel; formele claselor închise nu se importă",
        data_descarcarii=next((v["data"] for v in m.values()), ""),
    )
    # pasul 1: grupăm intrările pe (cuvânt, categorie) ca să numerotăm omonimele
    grupuri: dict[tuple[str, str], list[int]] = defaultdict(list)
    intrari: list[dict] = []
    with open(cale, encoding="utf8") as f:
        for i, linie in enumerate(f):
            if limita and i >= limita:
                break
            d = json.loads(linie)
            upos = categorie(d)
            if upos is None:
                n(f"sarite_{d.get('pos')}"); continue
            sensuri = d.get("senses") or []
            e_doar_forma = bool(sensuri) and all(("form_of" in s or "alt_of" in s) for s in sensuri)
            d["_upos"], d["_doar_forma"] = upos, e_doar_forma
            intrari.append(d)
            if not e_doar_forma:
                grupuri[(normalizeaza(d["word"]), upos)].append(len(intrari) - 1)
    omonim_pentru: dict[int, int] = {}
    for cheie, idx in grupuri.items():
        if len(idx) == 1 or cheie[1] in POS_FARA_FORME:
            # clasele închise nu se despart în omonime: tabelele proprii (inchise.py) sunt lexemul de referință
            for i in idx:
                omonim_pentru[i] = 0
        else:
            idx_sortate = sorted(idx, key=lambda i: (intrari[i].get("etymology_number") or 99, i))
            for k, i in enumerate(idx_sortate, start=1):
                omonim_pentru[i] = k
            n("omonime_distinse", len(idx))
    # pasul 2: lexeme, forme, sensuri
    relatii_de_rezolvat: list[tuple[str, str, str, str]] = []   # (lexem_id, tip, cuvânt țintă, upos țintă)
    forme_de_baza: list[tuple[str, str, str, str, str, str, str, int]] = []
    forme_amanate: list[tuple[str, str, str, str, str]] = []   # (forma, cuvânt bază, upos, trăsături, detalii) — form_of/alt_of
    lexem_ids_create: set[str] = set()
    for i, d in enumerate(intrari):
        upos = d["_upos"]
        cuvant = d["word"]
        if d["_doar_forma"]:
            for s in d["senses"]:
                tinte = s.get("form_of") or s.get("alt_of") or []
                tr, _ = din_kaikki(s.get("tags", []) or [], upos)
                for t in tinte:
                    baza_cuv = t.get("word", "")
                    if not baza_cuv or " and " in baza_cuv or RE_NELATIN.search(cuvant):
                        continue
                    detalii = "intrare de formă flexionară" if "form_of" in s else "variantă ortografică (alt_of)"
                    forme_amanate.append((cuvant, baza_cuv, upos, canonic_trasaturi(tr) if "form_of" in s else "", detalii))
            n("intrari_forma_sau_varianta")
            continue
        omonim = omonim_pentru.get(i, 0)
        lid = id_lexem(cuvant, upos, omonim)
        if omonim == 0 and upos in POS_FARA_FORME and lid in lexem_ids_create:
            n("intrari_contopite_clasa_inchisa")
        sensuri = d.get("senses") or []
        etichete_sens = [t for s in sensuri for t in (s.get("tags") or [])]
        gen = gen_lexem_din_kaikki(etichete_sens) if upos in ("NOUN", "PROPN") else None
        for h in d.get("head_templates") or []:
            a = h.get("args") or {}
            if upos in ("NOUN", "PROPN") and a.get("1") in ("m", "f", "n", "mf", "m-p", "f-p", "n-p"):
                gen = {"m": "Masc", "f": "Fem", "n": "Neut", "mf": "Masc", "m-p": "Masc", "f-p": "Fem", "n-p": "Neut"}[a["1"]]
        origine, limba = clasifica_etimologie(d.get("etymology_text", ""))
        registru = sorted({t for t in etichete_sens if t in ETICHETE_REGISTRU})
        atribute = {}
        if origine:
            atribute["etimologie"] = {"origine": origine, "limba": limba, "text": (d.get("etymology_text") or "")[:160]}
        if registru:
            atribute["registru"] = registru
        if d.get("pos") in ("phrase", "prep_phrase", "proverb"):
            atribute["tip"] = {"phrase": "expresie", "prep_phrase": "locuțiune prepozițională", "proverb": "proverb"}[d["pos"]]
        multicuvant = " " in cuvant
        baza.adauga_lexem(lid, cuvant, upos, omonim, "importat", SURSA_ID, gen=gen, multicuvant=multicuvant, atribute=atribute,
                          detalii_sursa=f"etimologie nr. {d.get('etymology_number')}" if d.get("etymology_number") else "")
        lexem_ids_create.add(lid)
        n("lexeme"); n(f"lexeme_{upos}")
        # forme
        if upos not in POS_FARA_FORME and not multicuvant:
            vazute_canonic: set[tuple[str, str]] = set()
            for forma, tr, detalii in _forme_intrare(d, upos, n):
                trc = canonic_trasaturi(canonic_pentru_pos(upos, tr, gen))
                if (forma, trc) in vazute_canonic:
                    continue
                vazute_canonic.add((forma, trc))
                forme_de_baza.append((forma, lid, trc, "atestat", SURSA_ID, "atestare:kaikki:tabel", detalii, 1))
        # lema însăși e formă (fără trăsături) chiar când nu există tabel
        forme_de_baza.append((cuvant, lid, "", "atestat", SURSA_ID, "atestare:kaikki:lema", "", 1))
        # sensuri
        nr = 0
        for s in sensuri:
            if "form_of" in s or "alt_of" in s:
                for t in s.get("form_of") or s.get("alt_of") or []:
                    tr, _ = din_kaikki(s.get("tags", []) or [], upos)
                    if t.get("word") and " and " not in t["word"]:
                        forme_amanate.append((cuvant, t["word"], upos, canonic_trasaturi(tr) if "form_of" in s else "", "intrare de formă flexionară" if "form_of" in s else "variantă ortografică (alt_of)"))
                continue
            glose = s.get("glosses") or []
            if not glose:
                continue
            nr += 1
            etichete = sorted({t for t in (s.get("tags") or []) if t in ETICHETE_REGISTRU or t in ETICHETE_GRAMATICALE_SENS})
            etichete.append("glosă în engleză")
            if s.get("topics"):
                etichete.extend(f"domeniu:{t}" for t in s["topics"][:3])
            baza.adauga_sens(id_sens(lid, None, nr), lid, None, "; ".join(glose), nr, SURSA_ID, "importat", etichete)
            n("sensuri")
            for tip, cheie in (("synonym", "synonyms"), ("antonym", "antonyms"), ("hypernym", "hypernyms"), ("hyponym", "hyponyms")):
                for rel in s.get(cheie) or []:
                    if rel.get("word"):
                        relatii_de_rezolvat.append((lid, tip, rel["word"], upos))
        for tip, cheie in (("synonym", "synonyms"), ("antonym", "antonyms"), ("derived", "derived"), ("related", "related")):
            for rel in d.get(cheie) or []:
                if rel.get("word"):
                    relatii_de_rezolvat.append((lid, tip, rel["word"], ""))
        if len(forme_de_baza) >= 50000:
            n("forme_noi", baza.adauga_forme_in_bloc(forme_de_baza)); n("forme_din_tabele", len(forme_de_baza)); forme_de_baza = []
            baza.commit()
    n("forme_noi", baza.adauga_forme_in_bloc(forme_de_baza)); n("forme_din_tabele", len(forme_de_baza))
    baza.commit()
    # pasul 3: formele amânate (form_of / alt_of) → lexemul de bază, dacă există
    randuri = []
    for forma, baza_cuv, upos, tr, detalii in forme_amanate:
        tinte = [r[0] for r in baza.con.execute("SELECT id FROM lexeme WHERE lema_norm = ? AND pos = ?", (normalizeaza(baza_cuv), upos))]
        if not tinte:
            tinte = [r[0] for r in baza.con.execute("SELECT id FROM lexeme WHERE lema_norm = ?", (normalizeaza(baza_cuv),))]
        if not tinte:
            n("forme_amanate_fara_lexem"); continue
        for lid in tinte:
            lx = baza.lexem(lid)
            trc = canonic_trasaturi(canonic_pentru_pos(lx["pos"], desparte_trasaturi(tr), lx["gen"])) if tr else ""
            randuri.append((forma, lid, trc, "atestat", SURSA_ID, "atestare:kaikki:form_of", detalii, 1))
    n("forme_noi", baza.adauga_forme_in_bloc(randuri)); n("forme_form_of", len(randuri))
    # pasul 4: relațiile lexicale (doar cu ținte existente)
    for lid, tip, tinta, upos in relatii_de_rezolvat:
        tinta_norm = normalizeaza(tinta)
        if upos:
            ids = [r[0] for r in baza.con.execute("SELECT id FROM lexeme WHERE lema_norm = ? AND pos = ?", (tinta_norm, upos))]
        else:
            ids = []
        if not ids:
            ids = [r[0] for r in baza.con.execute("SELECT id FROM lexeme WHERE lema_norm = ?", (tinta_norm,))]
        if not ids:
            n("relatii_cu_tinta_necunoscuta"); continue
        for tid in ids:
            if tid != lid:
                baza.adauga_relatie_semantica(tip, "lexem", lid, tid, SURSA_ID)
                n(f"relatii_{tip}")
    baza.commit()
    if verbos:
        print("Wiktionary/kaikki:", json.dumps(n.dict(), ensure_ascii=False))
    return n.dict()


if __name__ == "__main__":
    with Baza() as b:
        importa(b)
