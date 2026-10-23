"""E2 „3 specialiști + ruter” (S22, 23 octombrie 2026): familiile, împărțirea, ruterul, configurările și nota sistemului
(cu răspunsuri inventate, fără model)."""

from unelte import e2_specialisti as e2

TIPURI_NOI = {"nou_familie", "lipsa_nou_rau", "da_nu_nou_raion"}


def _p(intrebare, raspuns, tip="definitie", grup="text_1", fel="text"):
    return {"fel": fel, "grup": grup, "text": "Un text.", "tip": tip, "intrebare": intrebare, "raspuns": raspuns}


def test_familiile_cu_regula_fixa():
    assert e2.familia(_p("Bilca e în raionul Hliboca?", "Da.", "da_nu_nou_raion"), TIPURI_NOI) == "F2"
    assert e2.familia(_p("Ion s-a născut în 1959?", "Nu.", "da_nu_nascut"), TIPURI_NOI) == "F2"
    assert e2.familia(_p("Din ce familie face parte X?", "Din familia Viperidae.", "nou_familie"), TIPURI_NOI) == "F3"
    assert e2.familia(_p("Pe ce râu e X?", "Nu scrie în text.", "lipsa_nou_rau"), TIPURI_NOI) == "F3"
    assert e2.familia(_p("Cine i-au fost părinții lui X?", "Nu scrie în text.", "lipsa_parinti"), TIPURI_NOI) == "F1"
    assert e2.familia(_p("Ce este X?", "X este un film.", "definitie"), TIPURI_NOI) == "F1"
    # „Da, …” din conversația simplă nu e „Da.”: rămâne în F1
    assert e2.familia(_p("Știi românește?", "Da, știu română.", "conversatie", fel="conversatie"), TIPURI_NOI) == "F1"


def test_imparte_fiecare_pereche_o_data_si_pune_deoparte_grupuri_intregi():
    perechi = [_p(f"Ce este X{i}?", "Un film.", grup=f"text_{i // 2}") for i in range(40)]
    perechi += [_p(f"X{i} e din 2000?", "Da.", "da_nu_an", grup=f"text_{i}") for i in range(10)]
    pe_familii, validare, deoparte = e2.imparte(perechi, TIPURI_NOI, samanta=7, fractie=0.1)
    assert sum(len(v) for v in pe_familii.values()) == len(perechi)
    assert len(pe_familii["F1"]) == 40 and len(pe_familii["F2"]) == 10 and pe_familii["F3"] == []
    assert len(deoparte) == round(20 * 0.1)
    assert {p["grup"] for p in validare} == set(deoparte)
    assert len(validare) == sum(p["grup"] in deoparte for p in perechi)
    assert e2.imparte(perechi, TIPURI_NOI, samanta=7, fractie=0.1)[2] == deoparte


def test_ruterul_ia_cel_mai_lung_inceput_si_pragul():
    intrebari = ([("E adevărat că X e din 2000?", "F2")] * 5 + [("E adevărat că X e mare?", "F2")] * 2
                 + [("Din ce familie face parte X?", "F3")] * 5 + [("Din ce an e X?", "F1")] * 6
                 + [("Rar început aici?", "F2")] * 4)
    r = e2.construieste_ruter(intrebari, (1, 2, 3), 5)
    assert e2.ruteaza(r, "E adevărat că Y e din 1990?") == "F2"
    assert e2.ruteaza(r, "Din ce familie face parte Y?") == "F3"   # „din ce familie” bate „din ce” (F1)
    assert e2.ruteaza(r, "Din ce județ e Y?") == "F1"
    assert e2.ruteaza(r, "Rar început aici?") == "F1"   # doar 4 < 5: implicit
    assert e2.ruteaza(r, "Ce este Y?") == "F1"
    m = e2.masoara(r, [{"intrebare": "Din ce familie e Z?", "familie": "F3"},
                       {"intrebare": "Rar început aici?", "familie": "F2"}])
    assert m["procent"] == 50.0 and len(m["gresite"]) == 1


def test_configurarea_schimba_doar_cele_trei_valori():
    baza = ('# antet\r\n[platforma]\r\nnume = "w2_conv_text_v3"\r\n[porturi.model]\r\nsetari = { lot = 12, '
            'cale_stare = "lucru/w2_conv_text_v3/gpt.pt", conversatie = "date/conversatie/text_v3/antrenare.jsonl" }\r\n')
    nou = e2.configurare(baza, "F2")
    assert 'nume = "w2_spec_f2"' in nou and 'cale_stare = "lucru/w2_spec_f2/gpt.pt"' in nou
    assert 'conversatie = "date/conversatie/e2/f2/antrenare.jsonl"' in nou
    assert nou.count("\r\n") == baza.count("\r\n")
    assert nou.replace("w2_spec_f2", "w2_conv_text_v3").replace("e2/f2", "text_v3") == baza


def _examene(raspunsuri_elev, intrebari, experiment):
    """Un fișier `examene_*.json` inventat: totul în S15, celelalte examene goale."""
    return {"experiment": experiment,
            "S15": {"raspunsuri": [{**p, "raspuns_elev": r} for p, r in zip(intrebari, raspunsuri_elev)]},
            "S4": {"raspunsuri": []}, "noaptea10": {"raspunsuri": []}}


def test_sistemul_ia_raspunsul_specialistului_ales_de_ruter():
    intrebari = [
        {"fel": "text", "categorie": "b2", "intrebare": "Cine a regizat Filmul?", "raspuns": "Richard Donner.", "tip": "x"},
        {"fel": "text", "categorie": "b2", "intrebare": "E adevărat că Filmul e din 2006?", "raspuns": "Da.", "tip": "y"},
        {"fel": "text", "categorie": "b2", "intrebare": "Ion e din 1990?", "raspuns": "Nu.", "tip": "y"},
        {"fel": "text", "categorie": "b2", "intrebare": "Ce este Gușoeni?", "raspuns": "Un sat din Vâlcea.", "tip": "x"},
    ]
    toate = [{**p, "examen": "S15", "index": i, "grup_examen": "S15 b2",
              "familie": "F2" if p["raspuns"] in ("Da.", "Nu.") else "F1"} for i, p in enumerate(intrebari)]
    ruter = e2.construieste_ruter([("E adevărat că X e mare?", "F2")] * 5 + [("Cine a scris X?", "F1")] * 5, (1, 2, 3), 5)
    f1 = _examene(["Richard Donner.", "Nu.", "Da.", "Gușoeni este un sat din județul Vâlcea, România, foarte vechi."],
                  intrebari, 1)
    f2 = _examene(["Nu scrie în text.", "Da.", "Nu.", "Nu."], intrebari, 2)
    monolit = _examene(["Richard Donner.", "Da.", "Da.", "Nu scrie în text."], intrebari, 0)
    rez = e2.sistem(ruter, {"F1": f1, "F2": f2}, set(), monolit, toate)
    # ruterul: 1 → F1 („cine a regizat” nu e în tabel, „cine a” da), 2 → F2, 3 → F1 (începe cu un nume: implicit,
    # greșit), 4 → F1 (implicit)
    assert rez["ruter"]["total"] == "3/4 = 75.0 %"
    # sistemul: 1 F1 corect, 2 F2 corect, 3 F1 „Da.” greșit, 4 F1 corect (acoperire 1,0; lung: 11 > 2×4 cuvinte)
    assert rez["sistem"]["total"] == {"intrebari": 4, "corecte": 3, "corecte_f1": 2, "lungi_corecte": 1}
    # ruterul perfect: și 3 merge la F2 („Nu.”) → 4/4
    assert rez["sistem_ruter_perfect"]["total"]["corecte"] == 4
    assert rez["criteriul_A_examene"] == {"F1": {"specialist": 2, "monolit": 1}, "F2": {"specialist": 2, "monolit": 1}}
    assert rez["criteriul_B"] == {"sistem": 3, "monolit": 2}
