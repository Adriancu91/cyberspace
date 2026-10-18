"""Importă dicționarul ortografic Hunspell ro_RO (rospell) în bază, interpretând regulile .aff.

Ce intră:
  - intrările cu clasă de flexiune (flaguri) → lexeme cu categorie și gen deduse din clasa descrisă în antetul
    fișierului .aff (A = substantiv feminin, L = masculin, C/M/P/z/n = neutru, Q/D/S… = adjectiv, K/B/E/H/G/I = verb,
    U/T = nume propriu); pentru verbe, intrarea e forma de persoana I singular, iar infinitivul (lema) se derivă
    prin regulă și se acceptă doar dacă e confirmat (intrare în .dic sau lexem din altă sursă);
  - forma de bază = formă atestată („atestare:hunspell:intrare”); formele produse de reguli = „regula:hunspell:SFX A 7”,
    cu trăsături doar când regula e anotată în .aff (s.f.sg.art. etc.); statutul lor rămâne „generat” până le
    confirmă altă sursă;
  - intrările fără flag → proveniență suplimentară pentru formele deja cunoscute (orice lexem) sau, dacă nu există
    nicio analiză, tabela `ortografie` (cuvânt cunoscut doar ortografic).
Ce NU intră: formele cu prefix (re-, ne-, auto-) și cele cu clitice lipite (vezi morfologie/hunspell.py).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ..baza import Baza, canonic_trasaturi
from ..morfologie.hunspell import citeste
from ..morfologie.trasaturi import canonic_pentru_pos, din_hunspell
from ..text import normalizeaza
from .comun import DIR_SURSE, Numarator, lexeme_tinta, manifest_sursa

SURSA_ID = "hunspell_ro"

# flag → (categorie, gen, descriere) conform antetului din ro_RO.aff
CLASE = {
    "A": ("NOUN", "Fem", "substantiv feminin"), "F": ("NOUN", "Fem", "substantiv feminin"), "f": ("NOUN", "Fem", "substantiv feminin"),
    "R": ("NOUN", "Fem", "substantiv feminin"), "r": ("NOUN", "Fem", "substantiv feminin"), "s": ("NOUN", "Fem", "substantiv feminin"),
    "u": ("NOUN", "Fem", "substantiv feminin"), "a": ("NOUN", "Fem", "substantiv feminin (plural în -ele)"),
    "C": ("NOUN", "Neut", "substantiv neutru, plural în -uri"), "c": ("NOUN", "Neut", "substantiv neutru cu defect de plural"),
    "M": ("NOUN", "Neut", "substantiv neutru, plural în -e"), "P": ("NOUN", "Neut", "substantiv neutru, plural în -e"),
    "z": ("NOUN", "Neut", "substantiv neutru cu alternanța oa"), "n": ("NOUN", "Neut", "neologism neutru (cd-ul)"),
    "L": ("NOUN", "Masc", "substantiv masculin"), "l": ("NOUN", "Masc", "substantiv masculin cu defect de plural"),
    "D": ("ADJ", None, "adjectiv"), "Q": ("ADJ", None, "adjectiv"), "S": ("ADJ", None, "adjectiv în -ic"),
    "t": ("ADJ", None, "adjectiv în -eț"), "e": ("ADJ", None, "adjectiv în -e (invariabil în gen)"), "q": ("ADJ", None, "adjectiv în -fag"),
    "U": ("PROPN", "Fem", "nume propriu feminin"), "T": ("PROPN", "Masc", "nume propriu masculin"),
    "K": ("VERB", None, "verb conj. I fără -ez"), "B": ("VERB", None, "verb conj. I cu -ez"),
    "E": ("VERB", None, "verb conj. III (-e)"), "H": ("VERB", None, "verb conj. III (-e)"), "G": ("VERB", None, "verb conj. III (-e)"),
    "I": ("VERB", None, "verb conj. IV cu -esc/-ăsc"),
}
FLAGURI_IGNORATE = {"O", "o", "N"}  # prefixe re-/auto-; N = clitice de gerunziu

TR_LEMA = {
    "NOUN": {"Number": "Sing", "Definite": "Ind"},
    "PROPN": {"Number": "Sing", "Definite": "Ind"},
    "ADJ": {"Number": "Sing", "Definite": "Ind", "Gender": "Masc", "Degree": "Pos"},
    "VERB": {"Mood": "Ind", "Number": "Sing", "Person": "1", "Tense": "Pres", "VerbForm": "Fin"},
}


def infinitive_candidate(stem: str, flag: str) -> list[str]:
    """Candidații de infinitiv pentru forma de persoana I singular din dicționar."""
    c: list[str] = []
    if flag == "B" and stem.endswith("ez"):
        c.append(stem[:-2] + "a")
    elif flag == "K":
        c.append(stem + "a")
        # alternanțe vocalice frecvente în ultima silabă: o→u (port→purta), oa→o? (joc→juca)
        if "o" in stem[-4:]:
            i = stem.rfind("o")
            c.append(stem[:i] + "u" + stem[i + 1:] + "a")
        if stem.endswith("ăt") or stem.endswith("ăr"):
            c.append(stem[:-2] + "a" + stem[-1] + "a")
    elif flag in ("E", "H", "G"):
        c.append(stem + "e")
        c.append(stem + "ea")
    elif flag == "I":
        if stem.endswith("esc"):
            c.append(stem[:-3] + "i")
        elif stem.endswith("ăsc"):
            c.append(stem[:-3] + "î")
        else:
            c.append(stem + "i")
    return c


def importa(baza: Baza, director: Path | None = None, verbos: bool = True) -> dict:
    director = director or (DIR_SURSE / "hunspell")
    n = Numarator()
    m = manifest_sursa("hunspell")
    baza.adauga_sursa(
        SURSA_ID, "Dicționarul ortografic Hunspell ro_RO (rospell), din pachetul LibreOffice dictionaries/ro",
        licenta="GPL 2.0 / LGPL 2.1 / MPL 1.1 (tri-licență, la alegere)", url="https://github.com/LibreOffice/dictionaries/tree/master/ro",
        versiune="word list 3.3.10; commit 67032ee957631908098a72edf48dc81cac27e369 (12 octombrie 2026)",
        atribuire="Rospell Team (2005–2013): Lucian Constantin, Andrei Cipu, Sorin Sbârnea, Alexandru Szasz, Ionuț Păduraru, Adrian Stoica, Nicu Buculei, Cătălin Frâncu, Ionel Mugurel Ciobică, Mihai Budiu",
        obligatii="păstrarea notiței de copyright; datele derivate rămân sub licența aleasă (recomandat MPL 1.1)",
        fisiere=[k for k in m] or ["hunspell/ro_RO.aff", "hunspell/ro_RO.dic"],
        transformari="interpretarea regulilor SFX (fără prefixe și fără clitice); categoria/genul din clasa de flaguri; infinitivul derivat și confirmat",
        limitari="formele generate fără anotare nu au trăsături; infinitivele neconfirmate nu intră (numărate)",
        data_descarcarii=next((v["data"] for v in m.values()), ""),
    )
    d = citeste(director / "ro_RO.aff", director / "ro_RO.dic")
    cuvinte_fara_flag: set[str] = {w for w, fl in d.intrari if not fl}
    leme_existente: set[tuple[str, str]] = {(r[0], r[1]) for r in baza.con.execute("SELECT lema_norm, pos FROM lexeme")}
    randuri: list[tuple[str, str, str, str, str, str, str, int]] = []
    gerunzii: list[str] = []
    cache_lexeme: dict[tuple[str, str], list[str]] = {}

    def tinta(lema: str, pos: str, gen: str | None, clasa: str, detalii: str) -> list[str]:
        cheie = (normalizeaza(lema), pos)
        if cheie not in cache_lexeme:
            cache_lexeme[cheie] = lexeme_tinta(baza, lema, pos, SURSA_ID, statut="importat", gen=gen, clasa=clasa, detalii=detalii)
        return cache_lexeme[cheie]

    for cuvant, flaguri in d.intrari:
        n("intrari")
        if not flaguri:
            continue
        flaguri_utile = [f for f in flaguri if f not in FLAGURI_IGNORATE]
        if "N" in flaguri and not flaguri_utile:
            gerunzii.append(cuvant)
            continue
        if not flaguri_utile:
            cuvinte_fara_flag.add(cuvant)  # doar prefix re-/auto-: cuvântul e o intrare simplă
            continue
        clase = [CLASE.get(f) for f in flaguri_utile]
        if any(c is None for c in clase):
            n("flag_necunoscut"); continue
        pos, gen, descriere = clase[0]
        clasa = "hunspell:" + "".join(flaguri_utile)
        if pos == "VERB":
            lema = None
            for cand in infinitive_candidate(cuvant, flaguri_utile[0]):
                if cand in cuvinte_fara_flag or (normalizeaza(cand), "VERB") in leme_existente:
                    lema = cand
                    break
            if lema is None:
                n("verbe_fara_infinitiv_confirmat"); continue
            n("verbe")
            ids = tinta(lema, "VERB", None, clasa, f"infinitiv derivat din „{cuvant}” ({descriere})")
        else:
            n(f"lexeme_{pos}")
            ids = tinta(cuvant, pos, gen, clasa, descriere)
        tr_lema = canonic_trasaturi(canonic_pentru_pos(pos, dict(TR_LEMA.get(pos, {})), gen))
        for lid in ids:
            randuri.append((cuvant, lid, tr_lema, "atestat", SURSA_ID, "atestare:hunspell:intrare", descriere, 1))
        for forma, regula in d.forme(cuvant, "".join(flaguri_utile)):
            anot = regula.anotare if regula.anotare and not regula.anotare.startswith("#") else ""
            tr = canonic_trasaturi(canonic_pentru_pos(pos, din_hunspell(anot), gen)) if anot else ""
            for lid in ids:
                randuri.append((forma, lid, tr, "generat", SURSA_ID, f"regula:hunspell:SFX {regula.flag} {regula.index}", anot or regula.anotare, 0))
            n("forme_generate")
        if len(randuri) >= 50000:
            n("forme_noi", baza.adauga_forme_in_bloc(randuri)); randuri = []
            baza.commit()
    n("forme_noi", baza.adauga_forme_in_bloc(randuri)); randuri = []
    baza.commit()
    # gerunziile listate ca intrări (flag N): proveniență pentru formele de gerunziu deja cunoscute
    for g in gerunzii:
        tinte = baza.con.execute("SELECT id FROM forme WHERE forma = ? AND trasaturi LIKE '%VerbForm=Ger%'", (g,)).fetchall()
        if not tinte:
            n("gerunzii_fara_lexem"); cuvinte_fara_flag.add(g); continue
        for t in tinte:
            baza.con.execute("INSERT INTO forme_provenienta(forma_id, sursa_id, origine, detalii, frecventa) VALUES (?,?,?,?,?) ON CONFLICT DO NOTHING",
                             (t[0], SURSA_ID, "atestare:hunspell:intrare", "gerunziu listat în dicționar", 1))
        n("gerunzii_atestate")
    # intrările fără flag: atestare pentru formele cunoscute, altfel doar ortografie
    ortografie: list[tuple[str, str, str]] = []
    for cuvant in sorted(cuvinte_fara_flag):
        forme = baza.con.execute("SELECT id FROM forme WHERE forma = ?", (cuvant,)).fetchall()
        if forme:
            for f in forme:
                baza.con.execute("INSERT INTO forme_provenienta(forma_id, sursa_id, origine, detalii, frecventa) VALUES (?,?,?,?,?) ON CONFLICT DO NOTHING",
                                 (f[0], SURSA_ID, "atestare:hunspell:intrare", "intrare fără clasă de flexiune", 1))
            n("intrari_simple_confirmand_forme")
            continue
        leme = baza.con.execute("SELECT id, pos, gen FROM lexeme WHERE lema_norm = ?", (normalizeaza(cuvant),)).fetchall()
        if leme:
            for lx in leme:
                tr = canonic_trasaturi(canonic_pentru_pos(lx["pos"], dict(TR_LEMA.get(lx["pos"], {})), lx["gen"])) if lx["pos"] in TR_LEMA else ""
                baza.adauga_forma(cuvant, lx["id"], tr, "atestat", SURSA_ID, "atestare:hunspell:intrare", "intrare fără clasă, potrivită cu lema", 1)
            n("intrari_simple_potrivite_cu_lema")
            continue
        ortografie.append((cuvant, SURSA_ID, "intrare fără clasă de flexiune; fără analiză cunoscută"))
    baza.adauga_ortografie(ortografie)
    n("doar_ortografie", len(ortografie))
    baza.commit()
    if verbos:
        print("Hunspell:", json.dumps(n.dict(), ensure_ascii=False))
    return n.dict()


if __name__ == "__main__":
    with Baza() as b:
        importa(b)
