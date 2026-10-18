"""Paradigmele explicite ale limbii române: declinarea substantivelor și adjectivelor, conjugarea verbelor regulate.

Toate regulile sunt scrise de mână, cu nume, și produc forme etichetate în convenția UD RRT. O formă generată de
paradigmă are statutul „generat”; devine „validat” doar când o confirmă o sursă independentă (Wiktionary, UD,
Hunspell). Când o sursă atestă o formă diferită pentru aceleași trăsături, regula e „contrazisă” și raportul de
acoperire o numără (verbele neregulate, alternanțele netratate).

Documentare: GALR (Academia Română, 2005/2008), capitolele de morfologie; convențiile de etichetare UD RRT.
Regulile acoperă: articolul hotărât enclitic, genitiv-dativul, vocativul (parțial), pluralul (când e cunoscut
din dovezi; altfel e ghicit cu reguli simple, marcate „ghicit”), cele patru conjugări regulate (cu -ez / -esc / -ăsc),
participiul cu acord, gerunziul; alternanțele vocalice/consonantice uzuale (t→ț, s→ș, d→z, c→ci, sc→șt, oa→o, ea→e).
Nu acoperă: verbele neregulate (a fi, a avea, a vrea, a da, a sta, a lua, a bea, a ști…) — acestea vin din
tabelele surselor; pluralele neregulate (om→oameni) vin tot din surse.
"""

from __future__ import annotations

import json
from collections import defaultdict

from ..baza import Baza, canonic_trasaturi
from ..identificatori import id_regula
from .trasaturi import canonic_pentru_pos

SURSA_ID = "rlc_reguli"
VOCALE = "aeiouăâî"

# ---- ajutătoare fonologice -------------------------------------------------------------------------------------
def _ultima_vocala(s: str) -> int:
    for i in range(len(s) - 1, -1, -1):
        if s[i] in VOCALE:
            return i
    return -1


def palatalizeaza(stem: str) -> str:
    """Alternanța consonantică dinaintea desinenței -i: t→ț, d→z, s→ș, st→șt, sc→șt, z→j (rar), c→ci? (nu: c rămâne)."""
    if stem.endswith("st"):
        return stem[:-2] + "șt"
    if stem.endswith("sc"):
        return stem[:-2] + "șt"
    if stem.endswith("t"):
        return stem[:-1] + "ț"
    if stem.endswith("d"):
        return stem[:-1] + "z"
    if stem.endswith("s"):
        return stem[:-1] + "ș"
    return stem


def _oa_la_o(stem: str) -> str:
    """frumoasă → frumos: inversul alternanței o→oa (folosit la feminin: oa apare când urmează ă/e)."""
    i = stem.rfind("oa")
    if i >= 0 and i == _ultima_vocala(stem) - 1:
        return stem[:i] + "o" + stem[i + 2:]
    return stem


def _o_la_oa(stem: str) -> str:
    i = _ultima_vocala(stem)
    if i >= 0 and stem[i] == "o" and not stem[i - 1:i + 1] == "oo":
        return stem[:i] + "oa" + stem[i + 1:]
    return stem


def diftongheaza(stem: str) -> str:
    """Alternanța dinaintea desinenței -ă/-e la verbele vechi: o→oa (cobor→coboară), e→ea (plec→pleacă), ă→a (învăț→învață).
    Se aplică o singură dată, pe ultima vocală a temei. Neologismele nu o au (adoră), de aceea e doar „generat”."""
    i = _ultima_vocala(stem)
    if i < 0:
        return stem
    v = stem[i]
    if v == "o" and stem[i - 1:i] != "o" and stem[i + 1:i + 2] != "a":
        return stem[:i] + "oa" + stem[i + 1:]
    if v == "e" and stem[i - 1:i] not in ("e", "i") and stem[i + 1:i + 2] != "a":
        return stem[:i] + "ea" + stem[i + 1:]
    if v == "ă":
        return stem[:i] + "a" + stem[i + 1:]
    return stem


def _ea_la_e(stem: str) -> str:
    i = stem.rfind("ea")
    if i >= 0 and i == _ultima_vocala(stem) - 1:
        return stem[:i] + "e" + stem[i + 2:]
    return stem


# ---- substantive -----------------------------------------------------------------------------------------------
def ghiceste_plural(lema: str, gen: str) -> tuple[str, str]:
    """Pluralul nearticulat ghicit prin reguli simple. Întoarce (formă, numele regulii). Doar ca ipoteză."""
    if gen == "Fem":
        if lema.endswith("ie"):
            return lema[:-1] + "i", "subst_fem_ie_ii"           # familie → familii
        if lema.endswith("ea"):
            return lema[:-2] + "ele", "subst_fem_ea_ele"         # cafea → cafele
        if lema.endswith("a"):
            return lema + "le", "subst_fem_a_ale"                 # basma → basmale
        if lema.endswith("ă"):
            return lema[:-1] + "e", "subst_fem_ă_e"              # casă → case (sau -i: grădini — nedeterminabil fără dovezi)
        if lema.endswith("e"):
            return palatalizeaza(lema[:-1]) + "i", "subst_fem_e_i"  # carte → cărți (fără alternanța a→ă)
        return lema + "i", "subst_fem_consoana_i"
    if gen == "Masc":
        if lema.endswith("u") and len(lema) > 2 and lema[-2] not in VOCALE:
            return lema[:-1] + "i", "subst_masc_u_i"             # codru → codri
        if lema.endswith("u"):
            return lema[:-1] + "i", "subst_masc_eu_ei"           # leu → lei
        if lema.endswith("e"):
            return palatalizeaza(lema[:-1]) + "i", "subst_masc_e_i"  # frate → frați
        if lema.endswith("ă"):
            return lema[:-1] + "i", "subst_masc_ă_i"              # tată → tați
        if lema.endswith("i"):
            return lema, "subst_masc_i_invariabil"
        return palatalizeaza(lema) + "i", "subst_masc_consoana_i"   # lup → lupi, băiat → băieți (fără a→e)
    # neutru
    if lema.endswith("u") and len(lema) > 2 and lema[-2] in VOCALE:
        return lema + "ri", "subst_neut_vocala_u_uri"             # tablou → tablouri
    if lema.endswith("u"):
        return lema[:-1] + "e", "subst_neut_u_e"                    # lucru → lucre? (teatru → teatre)
    if lema.endswith("iu"):
        return lema[:-1] + "i", "subst_neut_iu_ii"
    if len(lema) <= 4:
        return lema + "uri", "subst_neut_scurt_uri"               # loc → locuri, gând → gânduri
    return lema + "e", "subst_neut_lung_e"                         # scaun → scaune


def declina_substantiv(lema: str, gen: str, plural: str | None = None, cu_vocativ: bool = True) -> list[tuple[str, dict[str, str], str]]:
    """(formă, trăsături, numele regulii) pentru toate formele regulate ale unui substantiv.
    `plural` = pluralul nearticulat cunoscut din dovezi; dacă lipsește, e ghicit (regula are sufixul „ghicit”)."""
    rez: list[tuple[str, dict[str, str], str]] = []
    gen_sg = "Fem" if gen == "Fem" else "Masc"
    gen_pl = "Masc" if gen == "Masc" else "Fem"
    sufix = ""
    if plural is None:
        plural, regula_pl = ghiceste_plural(lema, gen)
        sufix = "/ghicit"
    else:
        regula_pl = "plural_din_dovezi"

    def f(forma: str, tr: dict[str, str], nume: str) -> None:
        rez.append((forma, dict(tr), nume + sufix if "plural" in nume or "pl" in nume else nume))

    f(lema, {"Number": "Sing", "Definite": "Ind", "Gender": gen_sg, "Case": "Acc,Nom"}, "subst_sg_neart")
    # articolul hotărât la singular
    if gen in ("Masc", "Neut"):
        if lema.endswith("ă"):
            sg_def, gd_def = lema[:-1] + "a", lema + "lui"             # tată → tata, tatălui
        elif lema.endswith("u") and not lema.endswith("iu"):
            sg_def, gd_def = lema + "l", lema + "lui"                   # codru → codrul; leu → leul
        elif lema.endswith("iu"):
            sg_def, gd_def = lema + "l", lema + "lui"                   # fiu → fiul, fiului
        elif lema.endswith("e"):
            sg_def, gd_def = lema + "le", lema + "lui"                  # frate → fratele, fratelui
        elif lema.endswith("i"):
            sg_def, gd_def = lema + "ul", lema + "ului"                 # taxi → taxiul
        else:
            sg_def, gd_def = lema + "ul", lema + "ului"                 # om → omul, omului
        f(sg_def, {"Number": "Sing", "Definite": "Def", "Gender": gen_sg, "Case": "Acc,Nom"}, "subst_masc_sg_art")
        f(lema, {"Number": "Sing", "Definite": "Ind", "Gender": gen_sg, "Case": "Dat,Gen"}, "subst_masc_sg_gd_neart")
        f(gd_def, {"Number": "Sing", "Definite": "Def", "Gender": gen_sg, "Case": "Dat,Gen"}, "subst_masc_sg_gd_art")
        if cu_vocativ and gen == "Masc" and lema[-1] not in VOCALE:
            f(lema + "ule", {"Number": "Sing", "Definite": "Def", "Gender": gen_sg, "Case": "Voc"}, "subst_masc_voc_ule")
    else:  # feminin
        if lema.endswith("ie"):
            sg_def, gd_indef, gd_def = lema[:-1] + "a", lema[:-1] + "i", lema + "i"     # familie → familia, familii, familiei
        elif lema.endswith("ea"):
            sg_def, gd_indef, gd_def = lema + "ua", plural, plural + "i"               # cafea → cafeaua, cafele, cafelei
        elif lema.endswith("a"):
            sg_def, gd_indef, gd_def = lema + "ua", plural, plural + "i"               # basma → basmaua
        elif lema.endswith("ă"):
            if plural.endswith("uri"):
                gd_indef, gd_def = lema[:-1] + "e", lema[:-1] + "ei"                   # lipsă → lipse, lipsei (plural lipsuri)
            else:
                gd_indef, gd_def = plural, plural + "i"                                 # casă → case, casei; grădină → grădini, grădinii
            sg_def = lema[:-1] + "a"
        elif lema.endswith("e"):
            sg_def, gd_indef, gd_def = lema + "a", plural, plural + "i"                 # carte → cartea, cărți, cărții
        elif lema.endswith("i"):
            sg_def, gd_indef, gd_def = lema + "ua", plural, plural + "i"                # zi → ziua (zile, zilei)
        else:
            sg_def, gd_indef, gd_def = lema + "a", plural, plural + "i"
        f(sg_def, {"Number": "Sing", "Definite": "Def", "Gender": "Fem", "Case": "Acc,Nom"}, "subst_fem_sg_art")
        f(gd_indef, {"Number": "Sing", "Definite": "Ind", "Gender": "Fem", "Case": "Dat,Gen"}, "subst_fem_sg_gd_neart")
        f(gd_def, {"Number": "Sing", "Definite": "Def", "Gender": "Fem", "Case": "Dat,Gen"}, "subst_fem_sg_gd_art")
        if cu_vocativ and lema.endswith("ă"):
            f(lema[:-1] + "o", {"Number": "Sing", "Definite": "Def", "Gender": "Fem", "Case": "Voc"}, "subst_fem_voc_o")
    # pluralul
    f(plural, {"Number": "Plur", "Definite": "Ind", "Gender": gen_pl, "Case": "Acc,Nom"}, "subst_pl_neart")
    f(plural, {"Number": "Plur", "Definite": "Ind", "Gender": gen_pl, "Case": "Dat,Gen"}, "subst_pl_gd_neart")
    if gen == "Masc":
        pl_def = plural + "i" if plural.endswith("i") else plural + "ii"   # lupi → lupii; tați → tații
    else:
        pl_def = plural + "le"                                              # case → casele; scaune → scaunele; zile → zilele
    f(pl_def, {"Number": "Plur", "Definite": "Def", "Gender": gen_pl, "Case": "Acc,Nom"}, "subst_pl_art")
    f(plural + "lor", {"Number": "Plur", "Definite": "Def", "Gender": gen_pl, "Case": "Dat,Gen"}, "subst_pl_gd_art")
    if cu_vocativ:
        f(plural + "lor", {"Number": "Plur", "Definite": "Def", "Gender": gen_pl, "Case": "Voc"}, "subst_pl_voc")
    return [(fo, canonic_pentru_pos("NOUN", tr, gen), nume) for fo, tr, nume in rez]


# ---- adjective ----------------------------------------------------------------------------------------------------
def forme_de_baza_adjectiv(lema: str) -> tuple[str, str, str, str]:
    """(m sg, f sg, m pl, f pl) ghicite din forma de masculin singular (fără dovezi)."""
    m = lema
    if lema.endswith("esc"):
        return m, lema[:-3] + "ească", lema[:-3] + "ești", lema[:-3] + "ești"
    if lema.endswith("iu"):
        return m, lema[:-1] + "e", lema[:-1] + "i", lema[:-1] + "i"              # argintiu → argintie, argintii
    if lema.endswith("ău"):
        return m, lema[:-2] + "ea", lema[:-1] + "i", lema[:-2] + "ele"           # rău → rea, răi, rele
    if lema.endswith("eu"):
        return m, lema[:-2] + "ea", lema[:-1] + "i", lema[:-2] + "ele"           # greu → grea, grei, grele
    if lema.endswith("u") and lema[-2] in VOCALE:
        return m, lema + "ă", lema[:-1] + "i", lema[:-1] + "i"                 # nou → nouă, noi, noi
    if lema.endswith("e"):
        return m, m, palatalizeaza(lema[:-1]) + "i", palatalizeaza(lema[:-1]) + "i"   # mare → mare, mari, mari
    if lema.endswith("os"):
        return m, _o_la_oa(lema[:-2]) + "oasă", lema[:-1] + "și", _o_la_oa(lema[:-2]) + "oase"  # frumos → frumoasă, frumoși, frumoase
    if lema.endswith("tor"):
        return m, lema[:-2] + "oare", lema + "i", lema[:-2] + "oare"            # muncitor → muncitoare, muncitori
    if lema.endswith("ic") or lema.endswith("ag") or lema.endswith("og"):
        return m, lema + "ă", lema + "i", lema + "i"                           # mic → mică, mici, mici (f pl = m pl la -ic)
    if lema.endswith("ă") or lema.endswith("i") or lema.endswith("o"):
        return m, m, m, m                                                      # invariabile (gri, roz…)
    return m, lema + "ă", palatalizeaza(lema) + "i", lema + "e"                # bun → bună, buni, bune


def declina_adjectiv(lema: str, baza: tuple[str, str, str, str] | None = None) -> list[tuple[str, dict[str, str], str]]:
    sufix = ""
    if baza is None:
        baza = forme_de_baza_adjectiv(lema)
        sufix = "/ghicit"
    m_sg, f_sg, m_pl, f_pl = baza
    if m_pl == f_pl == m_sg == f_sg:
        rez = [(m_sg, {"Degree": "Pos"}, "adj_invariabil")]
        return [(fo, canonic_pentru_pos("ADJ", tr), nume) for fo, tr, nume in rez]
    rez: list[tuple[str, dict[str, str], str]] = []

    def f(forma: str, tr: dict[str, str], nume: str) -> None:
        rez.append((forma, {**tr, "Degree": "Pos"}, nume + sufix))

    f(m_sg, {"Gender": "Masc", "Number": "Sing", "Definite": "Ind"}, "adj_m_sg")
    f(f_sg, {"Gender": "Fem", "Number": "Sing", "Definite": "Ind", "Case": "Acc,Nom"}, "adj_f_sg")
    f(f_pl, {"Gender": "Fem", "Number": "Sing", "Definite": "Ind", "Case": "Dat,Gen"}, "adj_f_sg_gd")
    f(m_pl, {"Gender": "Masc", "Number": "Plur", "Definite": "Ind"}, "adj_m_pl")
    f(f_pl, {"Gender": "Fem", "Number": "Plur", "Definite": "Ind"}, "adj_f_pl")
    # forme articulate (adjectivul antepus: frumosul băiat, frumoasei fete)
    m_sg_def = m_sg + "l" if m_sg.endswith("u") else (m_sg + "le" if m_sg.endswith("e") else m_sg + "ul")
    m_sg_gd = m_sg + "lui" if m_sg.endswith(("u", "e")) else m_sg + "ului"
    f(m_sg_def, {"Gender": "Masc", "Number": "Sing", "Definite": "Def", "Case": "Acc,Nom"}, "adj_m_sg_art")
    f(m_sg_gd, {"Gender": "Masc", "Number": "Sing", "Definite": "Def", "Case": "Dat,Gen"}, "adj_m_sg_gd_art")
    if f_sg.endswith("ă"):
        f(f_sg[:-1] + "a", {"Gender": "Fem", "Number": "Sing", "Definite": "Def", "Case": "Acc,Nom"}, "adj_f_sg_art")
    elif f_sg.endswith("ie"):
        f(f_sg[:-1] + "a", {"Gender": "Fem", "Number": "Sing", "Definite": "Def", "Case": "Acc,Nom"}, "adj_f_sg_art")
    elif f_sg.endswith("e"):
        f(f_sg + "a", {"Gender": "Fem", "Number": "Sing", "Definite": "Def", "Case": "Acc,Nom"}, "adj_f_sg_art")
    elif f_sg.endswith("ea"):
        f(f_sg + "ua", {"Gender": "Fem", "Number": "Sing", "Definite": "Def", "Case": "Acc,Nom"}, "adj_f_sg_art")
    f(f_pl + "i", {"Gender": "Fem", "Number": "Sing", "Definite": "Def", "Case": "Dat,Gen"}, "adj_f_sg_gd_art")
    f(m_pl + "i", {"Gender": "Masc", "Number": "Plur", "Definite": "Def", "Case": "Acc,Nom"}, "adj_m_pl_art")
    f(m_pl + "lor", {"Gender": "Masc", "Number": "Plur", "Definite": "Def", "Case": "Dat,Gen"}, "adj_m_pl_gd_art")
    f(f_pl + "le", {"Gender": "Fem", "Number": "Plur", "Definite": "Def", "Case": "Acc,Nom"}, "adj_f_pl_art")
    f(f_pl + "lor", {"Gender": "Fem", "Number": "Plur", "Definite": "Def", "Case": "Dat,Gen"}, "adj_f_pl_gd_art")
    return [(fo, canonic_pentru_pos("ADJ", tr), nume) for fo, tr, nume in rez]


# ---- verbe ---------------------------------------------------------------------------------------------------------
PERS = [("1", "Sing"), ("2", "Sing"), ("3", "Sing"), ("1", "Plur"), ("2", "Plur"), ("3", "Plur")]


def grup_conjugare(infinitiv: str, prezent_3sg: str | None = None) -> str:
    """I-a, I-ez, II-ea, III-e, IV-i, IV-esc, IV-î, IV-ăsc; din infinitiv și (dacă e cunoscută) forma de persoana a III-a singular prezent."""
    if infinitiv.endswith("ea"):
        return "II-ea"
    if infinitiv.endswith("a"):
        if prezent_3sg and prezent_3sg.endswith("ează"):
            return "I-ez"
        if prezent_3sg:
            return "I-a"
        return "I-a?"  # necunoscut: fără forma de prezent nu știm dacă ia -ez
    if infinitiv.endswith("e"):
        return "III-e"
    if infinitiv.endswith("i"):
        if prezent_3sg and prezent_3sg.endswith("ește"):
            return "IV-esc"
        return "IV-i" if prezent_3sg else "IV-i?"
    if infinitiv.endswith("î"):
        if prezent_3sg and prezent_3sg.endswith("ăște"):
            return "IV-ăsc"
        return "IV-î" if prezent_3sg else "IV-î?"
    return "?"


def conjuga(infinitiv: str, grup: str, participiu: str | None = None) -> list[tuple[str, dict[str, str], str]]:
    """Paradigma regulată a verbului. `grup` din `grup_conjugare` (fără „?”: dacă e nesigur, se iau ambele variante de apelant)."""
    rez: list[tuple[str, dict[str, str], str]] = []
    nume = "verb_" + grup.replace("-", "_")

    def fin(forma: str, mood: str, tense: str | None, pers: str, numar: str, eticheta: str) -> None:
        tr = {"Mood": mood, "Person": pers, "Number": numar, "VerbForm": "Fin"}
        if tense:
            tr["Tense"] = tense
        rez.append((forma, tr, f"{nume}_{eticheta}"))

    baza_a = grup.startswith("I")  # conjugările I și II–IV au desinențe diferite
    if grup in ("I-a", "I-ez"):
        stem = infinitiv[:-1]
        i_final = stem.endswith("i")                       # studia → studiez/studiază, studiind
        if grup == "I-ez":
            pres = [stem + "ez", stem + "ezi", stem + "ează", stem + "ăm", stem + "ați", stem + "ează"]
            if i_final:
                pres = [stem + "ez", stem + "ezi", stem + "ază", stem + "em", stem + "ați", stem + "ază"]
            subj3 = stem + "eze"
        else:
            d = diftongheaza(stem)
            pres = [stem, palatalizeaza(stem) + "i", d + "ă", stem + "ăm", stem + "ați", d + "ă"]
            subj3 = d + "e" if d != stem and stem[_ultima_vocala(stem)] == "e" else d + "e"
            if stem.endswith(("c", "g")):
                pres = [stem, stem + "i", d + "ă", stem + "ăm", stem + "ați", d + "ă"]
            if i_final:
                pres = [stem[:-1] + "i", stem[:-1] + "i", stem + "e", stem + "em", stem + "ați", stem + "e"]
                subj3 = stem + "e"
        imperf = [stem + "am", stem + "ai", stem + "a", stem + "am", stem + "ați", stem + "au"]
        perf = [stem + "ai", stem + "ași", (stem + "e") if i_final else (stem + "ă"), stem + "arăm", stem + "arăți", stem + "ară"]
        pqp = [stem + "asem", stem + "aseși", stem + "ase", stem + "aserăm", stem + "aserăți", stem + "aseră"]
        ger = stem + "ind" if i_final else stem + "ând"
        part = participiu or stem + "at"
    elif grup == "II-ea":
        stem = infinitiv[:-2]
        pres = [stem, palatalizeaza(stem) + "i", stem + "e", stem + "em", stem + "eți", stem]
        subj3 = stem + "ă"
        imperf = [stem + "eam", stem + "eai", stem + "ea", stem + "eam", stem + "eați", stem + "eau"]
        perf = [stem + "ui", stem + "uși", stem + "u", stem + "urăm", stem + "urăți", stem + "ură"]
        pqp = [stem + "usem", stem + "useși", stem + "use", stem + "userăm", stem + "userăți", stem + "useră"]
        ger = stem + "ând"
        part = participiu or stem + "ut"
    elif grup == "III-e":
        stem = infinitiv[:-1]
        pres = [stem, palatalizeaza(stem) + "i", stem + "e", stem + "em", stem + "eți", stem]
        subj3 = stem + "ă"
        imperf = [stem + "eam", stem + "eai", stem + "ea", stem + "eam", stem + "eați", stem + "eau"]
        part = participiu or stem + "ut"
        if part.endswith("s"):   # a merge → mers → mersei, merseserăm (perfectul simplu sigmatic)
            s = part
            perf = [s + "ei", s + "eși", s + "e", s + "erăm", s + "erăți", s + "eră"]
            pqp = [s + "esem", s + "eseși", s + "ese", s + "eserăm", s + "eserăți", s + "eseră"]
        else:
            perf = [stem + "ui", stem + "uși", stem + "u", stem + "urăm", stem + "urăți", stem + "ură"]
            pqp = [stem + "usem", stem + "useși", stem + "use", stem + "userăm", stem + "userăți", stem + "useră"]
        ger = stem + "ând"
    elif grup in ("IV-i", "IV-esc"):
        stem = infinitiv[:-1]
        if grup == "IV-esc":
            pres = [stem + "esc", stem + "ești", stem + "ește", stem + "im", stem + "iți", stem + "esc"]
            subj3 = stem + "ească"
        else:
            d = diftongheaza(stem)
            pres = [stem, palatalizeaza(stem) + "i", d + "e", stem + "im", stem + "iți", stem]
            subj3 = d + "ă"
        imperf = [stem + "eam", stem + "eai", stem + "ea", stem + "eam", stem + "eați", stem + "eau"]
        perf = [stem + "ii", stem + "iși", stem + "i", stem + "irăm", stem + "irăți", stem + "iră"]
        pqp = [stem + "isem", stem + "iseși", stem + "ise", stem + "iserăm", stem + "iserăți", stem + "iseră"]
        ger = stem + "ind"
        part = participiu or stem + "it"
    elif grup in ("IV-î", "IV-ăsc"):
        stem = infinitiv[:-1]
        if grup == "IV-ăsc":
            pres = [stem + "ăsc", stem + "ăști", stem + "ăște", stem + "âm", stem + "âți", stem + "ăsc"]
            subj3 = stem + "ască"
        else:
            d = diftongheaza(stem)
            pres = [stem, stem + "i", d + "ă", stem + "âm", stem + "âți", d + "ă"]
            subj3 = d + "e"
        imperf = [stem + "am", stem + "ai", stem + "a", stem + "am", stem + "ați", stem + "au"]
        perf = [stem + "âi", stem + "âși", stem + "î", stem + "ârăm", stem + "ârăți", stem + "âră"]
        pqp = [stem + "âsem", stem + "âseși", stem + "âse", stem + "âserăm", stem + "âserăți", stem + "âseră"]
        ger = stem + "ând"
        part = participiu or stem + "ât"
    else:
        return rez
    for (p, nr), fo in zip(PERS, pres):
        fin(fo, "Ind", "Pres", p, nr, "prezent")
    for (p, nr), fo in zip(PERS, imperf):
        fin(fo, "Ind", "Imp", p, nr, "imperfect")
    for (p, nr), fo in zip(PERS, perf):
        fin(fo, "Ind", "Past", p, nr, "perfect_simplu")
    for (p, nr), fo in zip(PERS, pqp):
        fin(fo, "Ind", "Pqp", p, nr, "mmcp")
    # conjunctivul: persoanele 1, 2 ca la prezent; persoana a 3-a are formă proprie (sg = pl)
    for (p, nr), fo in zip(PERS, pres):
        fin(subj3 if p == "3" else fo, "Sub", "Pres", p, nr, "conjunctiv")
    # imperativul: 2 sg = persoana a 3-a sg prezent (conj. I, IV) sau a 2-a sg (conj. II, III tranzitive — nedeterminabil fără dovezi); 2 pl = 2 pl prezent
    # 2 sg imperativ: = pers. a III-a sg la conj. I și la -esc/-ăsc/-î (cântă!, citește!, coboară!), = pers. a II-a sg la conj. II, III, IV-i (vezi!, mergi!, fugi!)
    imp_sg = pres[2] if grup in ("I-a", "I-ez", "IV-esc", "IV-ăsc", "IV-î") else pres[1]
    fin(imp_sg, "Imp", None, "2", "Sing", "imperativ")
    fin(pres[4], "Imp", None, "2", "Plur", "imperativ")
    rez.append((infinitiv, {"VerbForm": "Inf"}, f"{nume}_infinitiv"))
    rez.append((ger, {"VerbForm": "Ger"}, f"{nume}_gerunziu"))
    rez.append((part, {"VerbForm": "Part", "Gender": "Masc", "Number": "Sing"}, f"{nume}_participiu"))
    rez.append((part + "ă", {"VerbForm": "Part", "Gender": "Fem", "Number": "Sing"}, f"{nume}_participiu_acord"))
    rez.append((palatalizeaza(part) + "i", {"VerbForm": "Part", "Gender": "Masc", "Number": "Plur"}, f"{nume}_participiu_acord"))
    rez.append((part + "e", {"VerbForm": "Part", "Gender": "Fem", "Number": "Plur"}, f"{nume}_participiu_acord"))
    return [(fo, canonic_pentru_pos("VERB", tr), nume_r) for fo, tr, nume_r in rez]


# ---- regulile înregistrate în bază (pentru explicații și acoperire) -----------------------------------------------
REGULI = [
    ("subst_sg_art", "articolul hotărât enclitic la singular (-ul/-l/-le la masculin și neutru; -a/-ua/-ia la feminin)"),
    ("subst_sg_gd", "genitiv-dativul singular (-ului/-lui la masculin și neutru; forma de plural + -i la feminin, -ei la -ie)"),
    ("subst_pl", "pluralul nearticulat: din dovezi (Wiktionary/UD/Hunspell) sau ghicit după terminație"),
    ("subst_pl_art", "pluralul articulat (-i/-ii la masculin; -le la feminin și neutru) și genitiv-dativul plural (-lor)"),
    ("subst_voc", "vocativul (-ule, -e, -o; plural -lor) — parțial"),
    ("adj_4_forme", "adjectivul cu 4 forme (bun/bună/buni/bune), 3 forme (mic/mică/mici), 2 forme (mare/mari), invariabil"),
    ("adj_art", "formele articulate ale adjectivului antepus (frumosul, frumoasei, frumoșilor)"),
    ("verb_I_a", "conjugarea I fără -ez (a cânta: cânt, cânți, cântă, cântăm, cântați, cântă; să cânte)"),
    ("verb_I_ez", "conjugarea I cu -ez (a lucra: lucrez, lucrezi, lucrează, lucrăm, lucrați, lucrează; să lucreze)"),
    ("verb_II_ea", "conjugarea a II-a (a vedea, a părea: -ut la participiu, -ui la perfectul simplu)"),
    ("verb_III_e", "conjugarea a III-a (a merge, a face): participiu în -s/-t/-ut; perfect simplu sigmatic după participiul în -s"),
    ("verb_IV_i", "conjugarea a IV-a în -i fără -esc (a fugi) și cu -esc (a citi: citesc, citești, citește, citim, citiți, citesc)"),
    ("verb_IV_î", "conjugarea a IV-a în -î fără -ăsc (a coborî) și cu -ăsc (a hotărî)"),
    ("verb_participiu_acord", "acordul participiului (citit/citită/citiți/citite) pentru diateza pasivă și adjectivizare"),
    ("verb_timpuri_compuse", "timpurile compuse sunt sintactice: perfectul compus = AUX avea + participiu; viitorul = AUX vrea + infinitiv; condiționalul = aș/ai/ar/am/ați/ar + infinitiv; conjunctivul perfect = să fi + participiu"),
    ("alternante", "alternanțele tratate: t→ț, d→z, s→ș, st/sc→șt înaintea lui -i; o→oa / oa→o; ea→e"),
]


def scrie_reguli(baza: Baza) -> int:
    for nume, descriere in REGULI:
        baza.adauga_regula(id_regula("morfologie", nume), "morfologie", nume, descriere, None, "GALR (Academia Română); convenții UD RRT", "implementata")
    return len(REGULI)


def _forme_atestate(baza: Baza, lexem_id: str) -> dict[str, list[str]]:
    """trăsături canonice → formele atestate (nu generate) ale lexemului."""
    rez: dict[str, list[str]] = defaultdict(list)
    for r in baza.con.execute(
            "SELECT f.forma, f.trasaturi FROM forme f WHERE f.lexem_id = ? AND f.trasaturi <> '' AND EXISTS ("
            "SELECT 1 FROM forme_provenienta p WHERE p.forma_id = f.id AND p.origine LIKE 'atestare%')", (lexem_id,)):
        rez[r[1]].append(r[0])
    return rez


def aplica_peste_baza(baza: Baza, verbos: bool = True, limita: int | None = None) -> dict:
    """Generează paradigmele pentru toate lexemele NOUN/ADJ/VERB (fără expresii) și le scrie ca forme „generat”."""
    scrie_reguli(baza)
    n = {"substantive": 0, "adjective": 0, "verbe": 0, "forme_generate": 0, "forme_noi": 0, "substantive_fara_gen": 0,
         "plural_din_dovezi": 0, "plural_ghicit": 0, "adj_din_dovezi": 0, "adj_ghicit": 0, "verbe_grup_nedeterminat": 0, "verbe_cu_dovezi": 0}
    randuri: list[tuple[str, str, str, str, str, str, str, int]] = []
    lexeme = baza.con.execute("SELECT id, lema, pos, gen FROM lexeme WHERE pos IN ('NOUN','ADJ','VERB') AND multicuvant = 0 ORDER BY id").fetchall()
    if limita:
        lexeme = lexeme[:limita]
    for lx in lexeme:
        lid, lema, pos, gen = lx["id"], lx["lema"], lx["pos"], lx["gen"]
        if " " in lema or "-" in lema or not lema.islower():
            continue
        atestate = _forme_atestate(baza, lid)
        forme: list[tuple[str, dict[str, str], str]] = []
        if pos == "NOUN":
            if gen not in ("Masc", "Fem", "Neut"):
                n["substantive_fara_gen"] += 1
                continue
            gen_pl = "Masc" if gen == "Masc" else "Fem"
            pl = atestate.get(canonic_trasaturi({"Number": "Plur", "Definite": "Ind", "Gender": gen_pl}))
            if pl:
                n["plural_din_dovezi"] += 1
                forme = declina_substantiv(lema, gen, sorted(pl)[0])
            else:
                n["plural_ghicit"] += 1
                forme = declina_substantiv(lema, gen, None)
            n["substantive"] += 1
        elif pos == "ADJ":
            f_sg = atestate.get(canonic_trasaturi({"Gender": "Fem", "Number": "Sing", "Definite": "Ind", "Case": "Acc,Nom", "Degree": "Pos"}))
            m_pl = atestate.get(canonic_trasaturi({"Gender": "Masc", "Number": "Plur", "Definite": "Ind", "Degree": "Pos"}))
            f_pl = atestate.get(canonic_trasaturi({"Gender": "Fem", "Number": "Plur", "Definite": "Ind", "Degree": "Pos"}))
            if f_sg and m_pl and f_pl:
                n["adj_din_dovezi"] += 1
                forme = declina_adjectiv(lema, (lema, sorted(f_sg)[0], sorted(m_pl)[0], sorted(f_pl)[0]))
            else:
                n["adj_ghicit"] += 1
                forme = declina_adjectiv(lema, None)
            n["adjective"] += 1
        else:
            p3 = atestate.get(canonic_trasaturi({"Mood": "Ind", "Number": "Sing", "Person": "3", "Tense": "Pres", "VerbForm": "Fin"}))
            part = atestate.get(canonic_trasaturi({"VerbForm": "Part", "Gender": "Masc", "Number": "Sing"}))
            grup = grup_conjugare(lema, sorted(p3)[0] if p3 else None)
            if grup.endswith("?"):
                n["verbe_grup_nedeterminat"] += 1
                grupuri = [grup[:-1]] if grup != "I-a?" else ["I-a", "I-ez"]
                if grup == "IV-i?":
                    grupuri = ["IV-i", "IV-esc"]
                if grup == "IV-î?":
                    grupuri = ["IV-î", "IV-ăsc"]
            elif grup == "?":
                continue
            else:
                n["verbe_cu_dovezi"] += 1
                grupuri = [grup]
            for g in grupuri:
                forme.extend(conjuga(lema, g, sorted(part)[0] if part else None))
            n["verbe"] += 1
        vazute: set[tuple[str, str]] = set()
        for forma, tr, nume_regula in forme:
            trc = canonic_trasaturi(tr)
            if (forma, trc) in vazute or not forma:
                continue
            vazute.add((forma, trc))
            randuri.append((forma, lid, trc, "generat", SURSA_ID, f"regula:paradigma:{nume_regula}", "", 0))
        n["forme_generate"] += len(vazute)
        if len(randuri) >= 50000:
            n["forme_noi"] += baza.adauga_forme_in_bloc(randuri)
            randuri = []
            baza.commit()
    n["forme_noi"] += baza.adauga_forme_in_bloc(randuri)
    baza.commit()
    if verbos:
        print("Paradigme:", json.dumps(n, ensure_ascii=False))
    return n
