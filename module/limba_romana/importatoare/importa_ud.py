"""Importă corpusul UD Romanian RRT (CoNLL-U) în bază.

Ce intră:
  - `exemple` + `exemple_cuvinte`: toate propozițiile, cu setul lor: train → „antrenare”, dev → „dezvoltare”,
    test → „evaluare”. Setul de EVALUARE nu alimentează lexiconul (altfel evaluarea ar fi trucată).
  - `lexeme`: perechile (lemă, categorie) din antrenare + dezvoltare; genul substantivelor doar când e clar
    din corpus (Masc la plural ⇒ masculin; Fem la singular ⇒ feminin; Masc-sg + Fem-pl ⇒ neutru).
  - `forme`: (formă, lexem, trăsături) atestate în antrenare + dezvoltare, cu frecvență;
  - expresiile fixe (relația `fixed`): lexeme multicuvânt cu categoria din `ExtPos` (de ex. „din cauza” ADP);
  - `relatii_sintactice`: inventarul relațiilor de dependență întâlnite, cu descrieri în română.

Observații din README-ul corpusului (păstrate în proveniență): lemele sunt automate, trăsăturile convertite
cu corecturi, relațiile adnotate manual.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from ..baza import Baza, canonic_trasaturi, desparte_trasaturi
from ..morfologie.trasaturi import canonic_pentru_pos
from ..identificatori import id_exemplu
from ..text import normalizeaza
from .comun import DIR_SURSE, Numarator, lexeme_tinta, manifest_sursa

SURSA_ID = "ud_rrt"
SETURI = {"ro_rrt-ud-train.conllu": "antrenare", "ro_rrt-ud-dev.conllu": "dezvoltare", "ro_rrt-ud-test.conllu": "evaluare"}

GENURI_TEXT = {  # din README: prefixul id-ului de document → genul textului
    "Acquis": "juridic", "JRC": "juridic", "Agenda": "știri", "1984Orwell": "literatură", "Literatura": "literatură",
    "EMEA": "medical", "Medical": "medical", "PhysicsCompSciMath": "nonficțiune", "DGLR": "academic", "FrameNet": "FrameNet",
    "Wikipedia": "wikipedia", "Wiki": "wikipedia", "Diverse": "diverse", "Misc": "diverse",
}

DESCRIERI_RELATII = {
    "root": "rădăcina propoziției (de obicei predicatul)", "nsubj": "subiect", "nsubj:pass": "subiect al unui verb la diateza pasivă",
    "csubj": "subiect exprimat printr-o propoziție", "csubj:pass": "subiect propozițional al unui pasiv", "obj": "complement direct",
    "iobj": "complement indirect (dativ)", "obl": "complement prepozițional / circumstanțial", "obl:pmod": "complement prepozițional cerut de verb",
    "obl:agent": "complement de agent (de către)", "obl:tmod": "circumstanțial de timp exprimat nominal", "advmod": "modificator adverbial",
    "advmod:tmod": "adverb de timp", "advcl": "propoziție subordonată circumstanțială", "advcl:tcl": "propoziție circumstanțială de timp",
    "ccomp": "propoziție completivă", "ccomp:pmod": "completivă cerută de o prepoziție", "xcomp": "complement predicativ deschis (fără subiect propriu)",
    "nmod": "modificator nominal (de ex. genitiv, prepozițional)", "amod": "modificator adjectival", "nummod": "modificator numeral",
    "det": "determinant (articol, adjectiv pronominal)", "case": "prepoziție / marcă de caz", "mark": "marcă de subordonare (că, să, dacă…)",
    "cc": "conjuncție coordonatoare", "cc:preconj": "prima parte a unei conjuncții corelative (nici… nici)", "conj": "element coordonat",
    "aux": "verb auxiliar (am, voi, aș…)", "aux:pass": "auxiliar al pasivului (a fi)", "cop": "verb copulativ (a fi)",
    "expl": "pronume expletiv", "expl:pv": "pronume reflexiv al verbului pronominal (se, își)", "expl:pass": "reflexiv cu valoare pasivă",
    "expl:poss": "dativ posesiv clitic", "expl:impers": "reflexiv impersonal (se spune)", "acl": "propoziție / participiu care determină un substantiv",
    "appos": "apoziție", "flat": "nume compus (prenume + nume)", "fixed": "expresie fixă (locuțiune)", "compound": "cuvânt compus",
    "parataxis": "parataxă (propoziții alăturate)", "punct": "punctuație", "vocative": "vocativ", "discourse": "element de discurs (interjecție)",
    "list": "element de listă", "orphan": "orfan (elipsă)", "goeswith": "fragment al aceluiași cuvânt", "reparandum": "reformulare",
    "dep": "dependență nespecificată", "dislocated": "element dislocat",
}


def citeste_conllu(cale: Path):
    """Produce (meta, cuvinte) pentru fiecare propoziție; cuvintele sunt dicționare cu cheile CoNLL-U."""
    meta: dict[str, str] = {}
    cuvinte: list[dict] = []
    with open(cale, encoding="utf8") as f:
        for linie in f:
            linie = linie.rstrip("\n")
            if not linie:
                if cuvinte:
                    yield meta, cuvinte
                meta, cuvinte = {}, []
                continue
            if linie.startswith("#"):
                if "=" in linie:
                    k, v = linie[1:].split("=", 1)
                    meta[k.strip()] = v.strip()
                continue
            c = linie.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue  # fără intervale multi-cuvânt / noduri goale în RRT
            cuvinte.append({"idx": int(c[0]), "forma": c[1], "lema": c[2], "upos": c[3], "xpos": c[4],
                            "trasaturi": canonic_trasaturi(c[5]), "cap": int(c[6]), "rel": c[7], "misc": c[9]})
    if cuvinte:
        yield meta, cuvinte


def gen_din_corpus(perechi: set[tuple[str, str]]) -> str | None:
    """perechi = {(Gender, Number)} observate pentru lema unui substantiv."""
    masc_pl = ("Masc", "Plur") in perechi
    fem_sg = ("Fem", "Sing") in perechi
    masc_sg = ("Masc", "Sing") in perechi
    fem_pl = ("Fem", "Plur") in perechi
    if masc_pl and not fem_sg:
        return "Masc"
    if fem_sg and not masc_pl:
        return "Fem"
    if masc_sg and fem_pl and not masc_pl and not fem_sg:
        return "Neut"
    return None


def importa(baza: Baza, director: Path | None = None, verbos: bool = True) -> dict:
    director = director or (DIR_SURSE / "ud_rrt")
    n = Numarator()
    m = manifest_sursa("ud_rrt")
    baza.adauga_sursa(
        SURSA_ID, "UD Romanian RRT (RoRefTrees), corpus de referință adnotat, Universal Dependencies",
        licenta="CC BY-SA 4.0", url="https://github.com/UniversalDependencies/UD_Romanian-RRT",
        versiune="commit ee6055b4b1f725eb48d9436bc5902a5685be7d96 (6 mai 2026)",
        atribuire="Verginica Barbu Mititelu, Elena Irimia, Cenel-Augusto Perez, Radu Ion, Radu Simionescu, Martin Popel și colab.",
        obligatii="atribuire; datele derivate rămân sub CC BY-SA 4.0",
        fisiere=[k for k in m] or list(SETURI), transformari="CoNLL-U → exemple, lexeme (lemă, UPOS), forme atestate (train+dev), expresii fixe",
        limitari="lemele sunt automate (README); setul test nu alimentează lexiconul",
        data_descarcarii=next((v["data"] for v in m.values()), ""),
    )
    forme_frecvente: Counter = Counter()      # (forma, lema, upos, trasaturi, set) → frecvență
    genuri: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    relatii: Counter = Counter()
    expresii: Counter = Counter()             # (text expresie, leme, ExtPos/upos) → frecvență
    for fisier, set_ in SETURI.items():
        cale = director / fisier
        if not cale.exists():
            n(f"lipsa {fisier}")
            continue
        for meta, cuvinte in citeste_conllu(cale):
            sid = meta.get("sent_id", f"{set_}-{n.c.get('propozitii', 0)}")
            doc = meta.get("newdoc id", "")
            gen = next((g for p, g in GENURI_TEXT.items() if sid.split("-")[0].startswith(p) or doc.startswith(p)), "")
            text = meta.get("text", " ".join(c["forma"] for c in cuvinte))
            baza.adauga_exemplu(id_exemplu(SURSA_ID, sid), text, SURSA_ID, set_,
                                [{k: v for k, v in c.items() if k != "misc"} for c in cuvinte], gen=gen, doc=doc)
            n("propozitii"); n(f"propozitii_{set_}")
            for c in cuvinte:
                relatii[c["rel"]] += 1
                n("cuvinte")
            if set_ == "evaluare":
                continue
            # expresii fixe: capul + copiii „fixed” (în ordinea din propoziție)
            copii_fixed: dict[int, list[dict]] = defaultdict(list)
            for c in cuvinte:
                if c["rel"] == "fixed":
                    copii_fixed[c["cap"]].append(c)
            for cap_idx, copii in copii_fixed.items():
                cap = cuvinte[cap_idx - 1]
                grup = sorted([cap] + copii, key=lambda x: x["idx"])
                if grup[-1]["idx"] - grup[0]["idx"] != len(grup) - 1:
                    n("expresii_necontigue"); continue
                tr = dict(p.split("=") for p in cap["trasaturi"].split("|") if "=" in p)
                pos = tr.get("ExtPos", cap["upos"])
                expresii[(" ".join(x["forma"] for x in grup), " ".join(x["lema"] for x in grup), pos)] += 1
            for c in cuvinte:
                if c["upos"] in ("PUNCT", "SYM") or (c["upos"] == "NUM" and "NumForm=Digit" in c["trasaturi"]) or c["upos"] == "X":
                    continue
                if c["rel"] == "fixed":
                    pass  # cuvântul intră și singur în lexicon (așa e adnotat), expresia intră separat
                tr = c["trasaturi"]
                forma = c["forma"]
                # „Fata” la început de propoziție e aceeași formă cu „fata”: coborâm majuscula când lema e cu minuscule
                if c["upos"] != "PROPN" and c["lema"] == c["lema"].lower() and forma[:1].isupper() and (forma[1:].islower() or len(forma.strip("-")) == 1):
                    forma = forma[0].lower() + forma[1:]
                forme_frecvente[(forma, c["lema"], c["upos"], tr, set_)] += 1
                if c["upos"] == "NOUN":
                    d = dict(p.split("=") for p in tr.split("|") if "=" in p)
                    if "Gender" in d and "Number" in d:
                        genuri[(normalizeaza(c["lema"]), c["upos"])].add((d["Gender"], d["Number"]))
    # lexeme + forme
    lexeme_vazute: dict[tuple[str, str], list[str]] = {}
    randuri = []
    for (forma, lema, upos, tr, set_), frecv in sorted(forme_frecvente.items()):
        cheie = (normalizeaza(lema), upos)
        if cheie not in lexeme_vazute:
            gen = gen_din_corpus(genuri.get(cheie, set())) if upos == "NOUN" else None
            lexeme_vazute[cheie] = lexeme_tinta(baza, lema, upos, SURSA_ID, gen=gen, detalii="lemă automată (UD RRT)")
            n("lexeme")
        trc = canonic_trasaturi(canonic_pentru_pos(upos, {k: v for k, v in desparte_trasaturi(tr).items() if k != "ExtPos"}, None))
        for lid in lexeme_vazute[cheie]:
            randuri.append((forma, lid, trc, "atestat", SURSA_ID, f"atestare:ud_rrt:{set_}", "", frecv))
    n("forme_noi", baza.adauga_forme_in_bloc(randuri))
    n("forme_atestate", len(randuri))
    for (text, leme, pos), frecv in sorted(expresii.items()):
        if pos not in ("ADP", "ADV", "CCONJ", "SCONJ", "DET", "PRON", "INTJ", "ADJ", "NOUN", "NUM", "PART", "VERB", "AUX"):
            pos = "X"
        ids = lexeme_tinta(baza, leme, pos, SURSA_ID, multicuvant=True, atribute={"tip": "expresie_fixa"}, detalii="expresie fixă (relația fixed)")
        for lid in ids:
            baza.adauga_forma(text, lid, "", "atestat", SURSA_ID, "atestare:ud_rrt:fixed", frecventa=frecv)
        n("expresii_fixe")
    baza.seteaza_relatii_sintactice([(r, DESCRIERI_RELATII.get(r, ""), f) for r, f in sorted(relatii.items())])
    n("relatii_sintactice", len(relatii))
    baza.commit()
    if verbos:
        print("UD RRT:", json.dumps(n.dict(), ensure_ascii=False))
    return n.dict()


if __name__ == "__main__":
    with Baza() as b:
        importa(b)
