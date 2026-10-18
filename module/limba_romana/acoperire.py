"""Raportul de acoperire: ce conține baza, ce e atestat / generat / validat, ce contrazic sursele, ce lipsește.

Toate cifrele au numitor cunoscut și se calculează din bază (reproductibil): nu se raportează procente „din
întreaga limbă română” (nu există un inventar de referință), ci față de sursele și seturile de test folosite.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from . import VERSIUNE
from .baza import Baza


def _q(baza: Baza, sql: str, *p) -> list[tuple]:
    return [tuple(r) for r in baza.con.execute(sql, p)]


def _d(baza: Baza, sql: str, *p) -> dict:
    return {str(r[0]): r[1] for r in baza.con.execute(sql, p)}


def raport_acoperire(baza: Baza, cu_evaluare: bool = True) -> dict:
    r: dict = {"versiune_motor": VERSIUNE, "data": datetime.now(timezone.utc).isoformat(timespec="seconds"), "baza": str(baza.cale)}
    # 1. leme importate
    r["1_leme"] = {
        "total": _q(baza, "SELECT COUNT(*) FROM lexeme")[0][0],
        "pe_categorie": _d(baza, "SELECT pos, COUNT(*) FROM lexeme GROUP BY pos ORDER BY 2 DESC"),
        "pe_sursa": _d(baza, "SELECT sursa_id, COUNT(*) FROM lexeme_surse GROUP BY sursa_id"),
        "confirmate_de_doua_surse": _q(baza, "SELECT COUNT(*) FROM (SELECT lexem_id FROM lexeme_surse GROUP BY lexem_id HAVING COUNT(DISTINCT sursa_id) >= 2)")[0][0],
        "cu_gen_cunoscut_substantive": _q(baza, "SELECT COUNT(*) FROM lexeme WHERE pos = 'NOUN' AND gen IS NOT NULL")[0][0],
        "substantive_fara_gen": _q(baza, "SELECT COUNT(*) FROM lexeme WHERE pos = 'NOUN' AND gen IS NULL")[0][0],
        "omonime_distinse": _q(baza, "SELECT COUNT(*) FROM lexeme WHERE omonim > 0")[0][0],
        "multicuvant": _q(baza, "SELECT COUNT(*) FROM lexeme WHERE multicuvant = 1")[0][0],
        "categorie_necunoscuta_X": _q(baza, "SELECT COUNT(*) FROM lexeme WHERE pos = 'X'")[0][0],
        "cu_etimologie": _q(baza, "SELECT COUNT(*) FROM lexeme WHERE atribute LIKE '%etimologie%'")[0][0],
        "cu_registru_marcat": _q(baza, "SELECT COUNT(*) FROM lexeme WHERE atribute LIKE '%registru%'")[0][0],
        "doar_ortografic": _q(baza, "SELECT COUNT(*) FROM ortografie")[0][0],
    }
    # 2-4. forme
    r["2_forme_atestate"] = {
        "total_forme_cu_atestare": _q(baza, "SELECT COUNT(DISTINCT forma_id) FROM forme_provenienta WHERE origine LIKE 'atestare%'")[0][0],
        "pe_sursa": _d(baza, "SELECT sursa_id, COUNT(DISTINCT forma_id) FROM forme_provenienta WHERE origine LIKE 'atestare%' GROUP BY sursa_id"),
        "din_corpus_ud_cu_frecventa": _q(baza, "SELECT COUNT(DISTINCT forma_id), SUM(frecventa) FROM forme_provenienta WHERE origine LIKE 'atestare:ud_rrt%'")[0],
    }
    r["3_forme_generate"] = {
        "total_forme_cu_regula": _q(baza, "SELECT COUNT(DISTINCT forma_id) FROM forme_provenienta WHERE origine LIKE 'regula%'")[0][0],
        "pe_origine": _d(baza, "SELECT CASE WHEN origine LIKE 'regula:hunspell%' THEN 'hunspell' WHEN origine LIKE 'regula:paradigma%' THEN 'paradigme' ELSE origine END, COUNT(DISTINCT forma_id) FROM forme_provenienta WHERE origine LIKE 'regula%' GROUP BY 1"),
        "doar_generate_neconfirmate": _q(baza, "SELECT COUNT(*) FROM forme WHERE statut = 'generat'")[0][0],
    }
    r["4_forme_validate"] = {
        "validate_doua_surse": _q(baza, "SELECT COUNT(*) FROM forme WHERE statut = 'validat'")[0][0],
        "atestate_o_sursa": _q(baza, "SELECT COUNT(*) FROM forme WHERE statut = 'atestat'")[0][0],
        "generate_neconfirmate": _q(baza, "SELECT COUNT(*) FROM forme WHERE statut = 'generat'")[0][0],
        "total": _q(baza, "SELECT COUNT(*) FROM forme")[0][0],
    }
    # paradigmele: validare / contradicții pe fiecare regulă
    reguli = _q(baza, """
        SELECT p.origine,
               COUNT(DISTINCT p.forma_id) AS generate,
               SUM(CASE WHEN f.statut = 'validat' THEN 1 ELSE 0 END) AS validate
        FROM forme_provenienta p JOIN forme f ON f.id = p.forma_id
        WHERE p.origine LIKE 'regula:paradigma:%' GROUP BY p.origine ORDER BY 2 DESC""")
    contrazise = _q(baza, """
        SELECT p.origine, COUNT(*) FROM forme_provenienta p JOIN forme f ON f.id = p.forma_id
        WHERE p.origine LIKE 'regula:paradigma:%' AND f.statut = 'generat' AND EXISTS (
            SELECT 1 FROM forme g JOIN forme_provenienta q ON q.forma_id = g.id
            WHERE g.lexem_id = f.lexem_id AND g.trasaturi = f.trasaturi AND g.forma <> f.forma AND q.origine LIKE 'atestare%')
        GROUP BY p.origine""")
    contra = {o: n for o, n in contrazise}
    r["4b_paradigme_pe_regula"] = [{"regula": o.replace("regula:paradigma:", ""), "forme_generate": g, "validate_de_surse": v,
                                    "contrazise_de_surse": contra.get(o, 0), "neconfirmate": g - v - contra.get(o, 0),
                                    "procent_validate_din_cele_verificabile": round(100 * v / max(1, v + contra.get(o, 0)), 1)} for o, g, v in reguli]
    # 5. categorii gramaticale
    r["5_categorii_gramaticale"] = {"reprezentate": sorted(c for c, in _q(baza, "SELECT DISTINCT pos FROM lexeme")),
                                    "lipsa_din_inventar": sorted(set(("NOUN PROPN VERB AUX ADJ ADV PRON DET NUM ADP CCONJ SCONJ PART INTJ").split()) - {c for c, in _q(baza, "SELECT DISTINCT pos FROM lexeme")})}
    # 6. trăsături morfologice (cu numărul de forme pe fiecare)
    r["6_trasaturi_morfologice"] = {
        "inventar": _q(baza, "SELECT COUNT(*) FROM trasaturi")[0][0],
        "perechi_cheie_valoare_folosite": {},
        "combinatii_distincte_de_trasaturi": _q(baza, "SELECT COUNT(DISTINCT trasaturi) FROM forme WHERE trasaturi <> ''")[0][0],
        "forme_fara_trasaturi": _q(baza, "SELECT COUNT(*) FROM forme WHERE trasaturi = ''")[0][0],
    }
    folosite: dict[str, int] = {}
    for tr, n in _q(baza, "SELECT trasaturi, COUNT(*) FROM forme WHERE trasaturi <> '' GROUP BY trasaturi"):
        for p in tr.split("|"):
            folosite[p] = folosite.get(p, 0) + n
    r["6_trasaturi_morfologice"]["perechi_cheie_valoare_folosite"] = dict(sorted(folosite.items()))
    r["6_trasaturi_morfologice"]["valori_din_inventar_nefolosite"] = sorted(f"{c}={v}" for c, v in _q(baza, "SELECT cheie, valoare FROM trasaturi") if f"{c}={v}" not in folosite)
    # 7. reguli
    r["7_reguli"] = {"pe_tip_si_statut": {}, "total": _q(baza, "SELECT COUNT(*) FROM reguli")[0][0]}
    for tip, statut, n in _q(baza, "SELECT tip, statut, COUNT(*) FROM reguli GROUP BY tip, statut"):
        r["7_reguli"]["pe_tip_si_statut"][f"{tip}/{statut}"] = n
    r["7_reguli"]["relatii_sintactice_in_inventar"] = _q(baza, "SELECT COUNT(*) FROM relatii_sintactice")[0][0]
    # 8. sensuri
    r["8_sensuri"] = {
        "total": _q(baza, "SELECT COUNT(*) FROM sensuri")[0][0],
        "pe_sursa": _d(baza, "SELECT sursa_id, COUNT(*) FROM sensuri GROUP BY sursa_id"),
        "concepte": _q(baza, "SELECT COUNT(*) FROM concepte")[0][0],
        "concepte_cu_definitie": _q(baza, "SELECT COUNT(*) FROM concepte WHERE definitie IS NOT NULL AND definitie <> ''")[0][0],
        "lexeme_cu_cel_putin_un_sens": _q(baza, "SELECT COUNT(DISTINCT lexem_id) FROM sensuri")[0][0],
        "lexeme_cu_sens_in_romana_rown": _q(baza, "SELECT COUNT(DISTINCT lexem_id) FROM sensuri WHERE sursa_id = 'rown'")[0][0],
        "lexeme_fara_niciun_sens": _q(baza, "SELECT COUNT(*) FROM lexeme l WHERE NOT EXISTS (SELECT 1 FROM sensuri s WHERE s.lexem_id = l.id)")[0][0],
        "lexeme_polisemantice_rown": _q(baza, "SELECT COUNT(*) FROM (SELECT lexem_id FROM sensuri WHERE sursa_id = 'rown' GROUP BY lexem_id HAVING COUNT(*) >= 2)")[0][0],
    }
    # 9. relații semantice
    r["9_relatii_semantice"] = {"total": _q(baza, "SELECT COUNT(*) FROM relatii_semantice")[0][0],
                                "pe_tip": _d(baza, "SELECT tip, COUNT(*) FROM relatii_semantice GROUP BY tip ORDER BY 2 DESC"),
                                "pe_nivel": _d(baza, "SELECT nivel, COUNT(*) FROM relatii_semantice GROUP BY nivel"),
                                "cicluri_in_ierarhii_din_sursa": len(baza.detecteaza_cicluri(("hypernym", "instance_hypernym", "mero_part", "mero_member", "mero_substance")))}
    # 10. expresii
    r["10_expresii_si_locutiuni"] = {"lexeme_multicuvant": _q(baza, "SELECT COUNT(*) FROM lexeme WHERE multicuvant = 1")[0][0],
                                     "pe_categorie": _d(baza, "SELECT pos, COUNT(*) FROM lexeme WHERE multicuvant = 1 GROUP BY pos ORDER BY 2 DESC"),
                                     "pe_sursa": _d(baza, "SELECT ls.sursa_id, COUNT(*) FROM lexeme l JOIN lexeme_surse ls ON ls.lexem_id = l.id WHERE l.multicuvant = 1 GROUP BY ls.sursa_id")}
    # 11-12. evaluare (din tabela validari, ultima rulare pe fiecare set)
    r["11_evaluare"] = {}
    for nume, rez in _q(baza, "SELECT nume, rezultat FROM validari WHERE nume LIKE 'evaluare_%' ORDER BY id"):
        r["11_evaluare"][nume] = json.loads(rez)
        for cheie in ("exemple_alarme_false", "exemple_greseli_lema", "greseli_relatie_frecvente", "greseli_categorie_frecvente"):
            r["11_evaluare"][nume].pop(cheie, None)
    r["12_ambiguitati"] = {nume: rez.get("ambiguitate") for nume, rez in r["11_evaluare"].items()}
    # 13. neacoperite (măsurate + declarate)
    r["13_neacoperite"] = {
        "masurate": {
            "substantive_fara_gen_(fara_paradigma)": r["1_leme"]["substantive_fara_gen"],
            "lexeme_cu_categorie_necunoscuta_X": r["1_leme"]["categorie_necunoscuta_X"],
            "cuvinte_doar_ortografice_fara_analiza": r["1_leme"]["doar_ortografic"],
            "lexeme_fara_sens_documentat": r["8_sensuri"]["lexeme_fara_niciun_sens"],
            "forme_generate_neconfirmate": r["4_forme_validate"]["generate_neconfirmate"],
            "reguli_de_paradigma_contrazise_(forme)": sum(contra.values()),
            "verbe_cu_grup_de_conjugare_nedeterminat": _q(baza, "SELECT COUNT(*) FROM (SELECT DISTINCT f.lexem_id FROM forme f JOIN forme_provenienta p ON p.forma_id = f.id WHERE p.origine LIKE 'regula:paradigma:verb_I_ez%' AND EXISTS (SELECT 1 FROM forme_provenienta q WHERE q.forma_id IN (SELECT id FROM forme WHERE lexem_id = f.lexem_id) AND q.origine LIKE 'regula:paradigma:verb_I_a%'))")[0][0],
        },
        "declarate": [
            "verbele neregulate (a fi, a avea, a vrea, a da, a sta, a lua, a bea, a ști, a mânca…): formele vin doar din surse (Wiktionary/UD/Hunspell), nu din paradigme",
            "alternanțele vocalice/consonantice neregulate la plural (om→oameni, băiat→băieți) și la verbe (a purta → port): paradigma e contrazisă de surse și rămâne „generat”",
            "gradele de comparație sunt tratate sintactic (mai/cel mai/foarte + adjectiv), nu ca forme",
            "sintaxa: arbore de dependențe de bază (fără valență verbală, fără coreferință); atașarea grupurilor prepoziționale rămâne ambiguă",
            "semantica: glosele Wiktionary sunt în engleză; sensurile RoWordNet acoperă doar lexemele din RoWN; fără restricții de selecție din surse (doar animat/inanimat din ierarhia RoWN)",
            "dezambiguizarea sensurilor: metodă de suprapunere lexicală (Lesk) explicabilă, fără evaluare pe un corpus adnotat semantic",
            "dialoguri / contextul conversației: infrastructura există (tabela contexte, parametrul context), dar nu influențează încă analiza",
            "textul fără diacritice: potrivirea pe forma plată există, dar ambiguitatea crește (mult/mulț, sa/să)",
        ],
    }
    return r


def scrie_raport(baza: Baza, cale: str) -> dict:
    r = raport_acoperire(baza)
    with open(cale, "w", encoding="utf8") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    return r
