"""Cercetătorul în două faze: fiecare valoare din listă o dată, apoi strângerea în jurul celor mai bune 3 rețete."""

from __future__ import annotations

import copy

from module.cercetator_local import CercetatorLocal, _rotunjeste

SPATIU = {"model": {"straturi": [4, 8, 12], "rata": [0.0001, 0.0003, 0.0009]}}
START = {"model": {"straturi": 8, "rata": 0.0003, "tokenizer": "bpe"}}


def _ruleaza(cercetator, scor, pasi=20):
    """Simulează bucla lui Kronos: păstrează rețeta dacă scorul e mai bun; întoarce propunerile și jurnalul."""
    istoric = [{"id": 1, "setari": copy.deepcopy(START), "scoruri": {"val_bpb": scor(START["model"])}, "decizie": "pastrat"}]
    curente, cel_mai_bun = copy.deepcopy(START), istoric[0]["scoruri"]["val_bpb"]
    propuneri = []
    for i in range(2, pasi + 2):
        p = cercetator.propune(istoric, copy.deepcopy(curente))
        if not p.modificari:
            break
        noi = copy.deepcopy(curente)
        for port, m in p.modificari.items():
            noi[port].update(m)
        s = scor(noi["model"])
        decizie = "pastrat" if s < cel_mai_bun - 0.005 else "respins"
        istoric.append({"id": i, "setari": noi, "scoruri": {"val_bpb": s}, "decizie": decizie})
        propuneri.append((p.descriere, noi["model"]))
        if decizie == "pastrat":
            curente, cel_mai_bun = noi, s
    return propuneri, istoric


def _scor(model):  # cel mai bun: 12 straturi, rata 0,0003
    return abs(model["straturi"] - 12) * 0.01 + abs(model["rata"] - 0.0003) * 100 + 1.0


def test_lista_incearca_fiecare_valoare_o_data_apoi_strange():
    propuneri, istoric = _ruleaza(CercetatorLocal(SPATIU, samanta=0), _scor)
    din_lista = [d for d, _ in propuneri if d.startswith("lista")]
    assert len(din_lista) == 4  # straturi 4, 12 și rata 0,0001, 0,0009: fiecare o dată
    assert all(d.startswith("lista") for d, _ in propuneri[:4])  # întâi lista, apoi strângerea
    assert propuneri[4][0].startswith("strângere în jurul locului 1")
    retete = [str(sorted(f["setari"]["model"].items())) for f in istoric]
    assert len(retete) == len(set(retete))  # nicio rețetă repetată
    assert {m["straturi"] for _, m in propuneri} >= {4, 12, 10}  # 10 = la jumătatea drumului între 8 și 12


def test_strangerea_cauta_intre_valori_si_rotunjeste():
    cercetator = CercetatorLocal(SPATIU, samanta=0, pasi={"straturi": 2})
    istoric = [
        {"id": i + 1, "setari": {"model": {**START["model"], "straturi": s, "rata": r}}, "scoruri": {"val_bpb": v}}
        for i, (s, r, v) in enumerate([(8, 0.0003, 1.0), (4, 0.0003, 1.1), (12, 0.0003, 1.2), (8, 0.0001, 1.3), (8, 0.0009, 1.4)])
    ]
    p = cercetator.propune(istoric, copy.deepcopy(START))
    # Golul cel mai mare: rata de la 0,0003 spre 0,0009 (de 2 ori mai departe decât spre 0,0001).
    assert p.descriere == "strângere în jurul locului 1 (#1, scor 1.0000): model.rata: 0.0003 → 0.0006"
    assert p.modificari["model"] == {**START["model"], "rata": 0.0006}  # toată rețeta: poate fi alta decât cea curentă
    istoric.append({"id": 6, "setari": {"model": p.modificari["model"]}, "scoruri": {"val_bpb": 1.5}})
    p = cercetator.propune(istoric, copy.deepcopy(START))
    assert p.modificari["model"]["rata"] == 0.00045  # golul s-a micșorat: acum între 0,0003 și 0,0006
    for i, rata in enumerate((0.00045, 0.0002, 0.00037, 0.00025), start=7):  # tot mai fin, până la 10%
        istoric.append({"id": i, "setari": {"model": {**START["model"], "rata": rata}}, "scoruri": {"val_bpb": 1.5}})
    p = cercetator.propune(istoric, copy.deepcopy(START))
    assert p.modificari["model"]["rata"] != 0.000275  # între 0,00025 și 0,0003: sub 10% față de 0,0003, nu se mai încearcă


def test_strangerea_la_numere_intregi_merge_pana_la_pas():
    # Un strat în plus sau în minus față de 12 (sub 10%) se încearcă: pragul de 10% e doar pentru numere cu virgulă.
    cercetator = CercetatorLocal({"model": {"straturi": [10, 12, 14]}}, samanta=0)
    istoric = [{"id": i, "setari": {"model": {"straturi": s}}, "scoruri": {"val_bpb": v}}
               for i, (s, v) in enumerate([(12, 1.0), (10, 1.1), (14, 1.2)], start=1)]
    assert cercetator.propune(istoric, {"model": {"straturi": 12}}).modificari == {"model": {"straturi": 11}}
    istoric.append({"id": 4, "setari": {"model": {"straturi": 11}}, "scoruri": {"val_bpb": 1.3}})
    assert cercetator.propune(istoric, {"model": {"straturi": 12}}).modificari == {"model": {"straturi": 13}}
    istoric.append({"id": 5, "setari": {"model": {"straturi": 13}}, "scoruri": {"val_bpb": 1.4}})
    assert cercetator.propune(istoric, {"model": {"straturi": 12}}).modificari == {}  # nimic între pași întregi


def test_cand_nu_mai_e_nimic_de_incercat_se_opreste():
    spatiu = {"model": {"straturi": [8, 9]}}
    cercetator = CercetatorLocal(spatiu, samanta=0)
    istoric = [{"id": 1, "setari": {"model": {"straturi": 8}}, "scoruri": {"val_bpb": 1.0}},
               {"id": 2, "setari": {"model": {"straturi": 9}}, "scoruri": {"val_bpb": 1.1}}]
    assert cercetator.propune(istoric, {"model": {"straturi": 8}}).modificari == {}


def test_rotunjirea():
    assert _rotunjeste(608.0, 640, 32) == 608 and _rotunjeste(600.0, 640, 32) == 608 and _rotunjeste(9.0, 10, None) == 9
    assert _rotunjeste(0.00025, 0.0003, None) == 0.00025 and _rotunjeste(0.000123456, 0.0001, None) == 0.000123
    assert _rotunjeste(1.0, 16, 2) == 2  # niciodată sub un pas


def test_in_ordinea_din_configurare_si_fara_strangere():
    spatiu = {"model": {"straturi": [4, 12], "rata": [0.0001]}}  # în configurare: întâi straturile, apoi rata
    cercetator = CercetatorLocal(spatiu, amesteca=False, strangere=False)
    assert cercetator._ordine == [("model", "straturi", 4), ("model", "rata", 0.0001), ("model", "straturi", 12)]
    propuneri, _ = _ruleaza(cercetator, _scor)
    assert [m["straturi"] if "straturi" in d else m["rata"] for d, m in propuneri] == [4, 0.0001, 12]
    assert all(d.startswith("lista") for d, _ in propuneri)  # după listă se oprește, fără strângere
