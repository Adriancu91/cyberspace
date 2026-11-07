"""S86: unealta unelte/masoara_memorie_mare.py (fără placă)."""

from __future__ import annotations

from pathlib import Path

import pytest

from unelte import masoara_memorie_mare as mm


def test_variantele_sunt_cele_din_sarcina():
    assert mm.VARIANTE == {
        "a": {"optimizator": "adamw", "lot": 4, "adunare_loturi": 24},
        "b": {"optimizator": "muon", "lot": 4, "adunare_loturi": 24},
        "c": {"optimizator": "muon", "lot": 6, "adunare_loturi": 16},
        "d": {"optimizator": "muon", "lot": 12, "adunare_loturi": 8},
    }


@pytest.mark.parametrize("varianta", ["a", "b", "c", "d"])
def test_setarile_modelului_vin_din_config_cu_copia(varianta, tmp_path):
    copie = tmp_path / "gpt.pt"
    s = mm.setari_model(varianta, copie, 100)
    assert s["n_straturi"] == 24 and s["n_emb"] == 768 and s["context"] == 512
    assert s["cale_stare"] == str(copie)
    assert s["pasi_max"] == 100 * mm.VARIANTE[varianta]["adunare_loturi"]
    assert s["optimizator"] == mm.VARIANTE[varianta]["optimizator"]
    assert s["lot"] * s["adunare_loturi"] == 96  # același număr de secvențe pe pas de optimizator


def test_originalul_nu_e_cale_stare():
    s = mm.setari_model("a", Path("x/gpt.pt"), 1)
    assert "w2_mare" not in s["cale_stare"]


@pytest.mark.parametrize("alocat,asteptat", [([], False), ([3000], False), ([3000, 3050, 3090], False),
                                             ([3000, 3500, 4000], True), ([3000, 3101], True)],
                         ids=["gol", "una", "sub_prag", "creste", "la_limita"])
def test_creste(alocat, asteptat):
    assert mm.creste(alocat) is asteptat


def test_urmaritorul_tine_varful_pe_faza():
    citiri = iter([(1000, 40), (5000, 60), (3000, 50)])
    u = mm.Urmaritor(citeste=lambda: next(citiri, None))
    u.faza = "1_antrenare"
    assert u.citeste_acum() == 1000
    assert u.citeste_acum() == 5000
    u.faza = "1_test_rapid"
    assert u.citeste_acum() == 3000
    assert u.varfuri == {"1_antrenare": 5000, "1_test_rapid": 3000}
    assert u.temperatura_max == 60
    assert u.citeste_acum() is None


def test_toate_refuza_a_doua_oara(tmp_path, monkeypatch):
    monkeypatch.setattr(mm, "DOSAR", tmp_path)
    (tmp_path / "s86.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit):
        mm.toate(1, 5800)


def test_toate_ruleaza_golirea_doar_daca_memoria_creste(tmp_path, monkeypatch):
    monkeypatch.setattr(mm, "DOSAR", tmp_path)
    chemari = []

    def fals(varianta, repetari, pasi, goleste, eticheta, memorie):
        chemari.append((eticheta, repetari, goleste))
        return {"memoria_creste": eticheta == "a"}

    monkeypatch.setattr(mm, "in_proces_nou", fals)
    r = mm.toate(5, 5800)
    assert chemari == [("a", 3, False), ("b", 1, False), ("c", 1, False), ("d", 1, False), ("a_golit", 3, True)]
    assert (tmp_path / "s86.json").exists() and "a_golit" in r["variante"]


def test_main_toate_merge_cap_coada(tmp_path, monkeypatch):
    monkeypatch.setattr(mm, "DOSAR", tmp_path)
    monkeypatch.setattr(mm, "in_proces_nou", lambda *a, **k: {"memoria_creste": False})
    assert mm.main(["toate", "--pasi-optimizator", "2"]) == 0
    assert (tmp_path / "s86.json").exists()


# --- S87: ordinea orchestratorului ---

def _ora(i, alocat, dupa_golire=None, varf=0):
    o = {"ora": i, "inceput": {"alocat_mb": alocat}, "antrenare": {"varf_nvidia_smi_mb": varf}}
    if dupa_golire is not None:
        o["inceput_dupa_golire"] = {"alocat_mb": dupa_golire}
    return o


def test_alocat_inceput_foloseste_valoarea_dupa_golire():
    ore = [_ora(1, 1000, 900), _ora(2, 1500, 950), _ora(3, 2000)]
    assert mm.alocat_inceput(ore) == [900, 950, 2000]
    assert mm.crestere_ora3({"ore": ore}) == 1100
    assert mm.crestere_ora3({"ore": ore[:2]}) is None


def _var(alocari, terminat=True, varf=5000, **extra):
    return {"ore": [_ora(i + 1, a) for i, a in enumerate(alocari)], "terminat": terminat,
            "nvidia_smi_varf_parinte_mb": varf, "cod": 0 if terminat else 1, **extra}


def test_verdicte_memoria_creste_si_golirea_ajuta():
    v = mm.verdicte_s87({"b_orch": _var([1000, 1200, 1400]), "b_orch_gc": _var([1000, 1010, 1050], varf=6600),
                         "b_orch_del": _var([1000, 1000, 1000])})
    assert v["P1_memoria_creste"] == "DA" and v["crestere_b_orch_mb"] == 400
    assert v["P2_golirea_ajuta"] == "DA" and v["crestere_b_orch_gc_mb"] == 50
    assert v["b_orch_del_trece"] is True


def test_verdicte_nu_cand_nu_creste_si_golirea_trece_de_6600():
    v = mm.verdicte_s87({"b_orch": _var([1000, 1100, 1299]), "b_orch_gc": _var([1000, 1000, 1000], varf=6601),
                         "b_orch_del": _var([1000])})
    assert v["P1_memoria_creste"] == "NU" and v["P2_golirea_ajuta"] == "NU"


def test_verdicte_caderea_inainte_de_ora3_e_da_la_p1_si_nu_la_p2():
    cazut = _var([1000, 1500], terminat=False, eroare="out of memory: x")
    v = mm.verdicte_s87({"b_orch": cazut, "b_orch_gc": cazut, "b_orch_del": cazut})
    assert v["P1_memoria_creste"] == "DA" and v["P2_golirea_ajuta"] == "NU" and v["b_orch_del_trece"] is False
    peste = _var([1000, 1000, 1000], varf=6701)
    assert mm.verdicte_s87({"b_orch": peste, "b_orch_gc": peste})["P1_memoria_creste"] == "DA"


def test_varful_ia_si_fazele_copilului():
    r = {"ore": [_ora(1, 0, varf=6650)], "nvidia_smi_varf_parinte_mb": 6000}
    assert mm.varf_nvidia(r) == 6650


def test_ore_refuza_a_doua_oara(tmp_path, monkeypatch):
    monkeypatch.setattr(mm, "DOSAR_ORE", tmp_path)
    (tmp_path / "s87.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit):
        mm.ore(1, 5800)


def test_ore_ruleaza_cele_trei_variante_in_ordinea_orchestratorului(tmp_path, monkeypatch):
    monkeypatch.setattr(mm, "DOSAR_ORE", tmp_path)
    monkeypatch.setattr(mm, "SURSA", tmp_path / "nu_exista.pt")
    chemari = []

    def fals(varianta, repetari, pasi, goleste, eticheta, memorie, dosar=None, golire=None):
        chemari.append((varianta, repetari, goleste, eticheta, dosar, golire))
        return _var([1000, 1000, 1000])

    monkeypatch.setattr(mm, "in_proces_nou", fals)
    assert mm.main(["ore", "--pasi-optimizator", "2"]) == 0
    assert chemari == [("b", 3, False, "b_orch", tmp_path, "nimic"), ("b", 3, False, "b_orch_gc", tmp_path, "gc"),
                       ("b", 3, False, "b_orch_del", tmp_path, "del")]
    assert (tmp_path / "s87.json").exists()


def test_unul_cu_ordinea_orchestratorului_alege_functia_noua(tmp_path, monkeypatch):
    primit = {}

    def fals(varianta, repetari, pasi, golire, iesire, memorie):
        primit.update(varianta=varianta, repetari=repetari, golire=golire)
        return {"terminat": True}

    monkeypatch.setattr(mm, "ruleaza_orchestrator", fals)
    assert mm.main(["unul", "--varianta", "b", "--repetari", "3", "--iesire", str(tmp_path / "r.json"),
                    "--ordine", "orchestrator", "--golire", "del"]) == 0
    assert primit == {"varianta": "b", "repetari": 3, "golire": "del"}
