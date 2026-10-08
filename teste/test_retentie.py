"""Unealta de antrenare lungă (8 octombrie 2026): retenția R = faptele noi ale orei ÷ faptele noi la plecare (doar
raportată), punctul de plecare cu criteriile din fișa modelului de pornire și referința de pornire pentru kronos."""

from __future__ import annotations

import json

from kronos.jurnal import Jurnal
from unelte import antrenare_lunga
from teste.test_cap_coada import RADACINA


def test_retentia():
    assert antrenare_lunga.retentia({"fapte_noi": 59}, {"fapte_noi": 72}) == 0.819
    assert antrenare_lunga.retentia({"fapte_noi": 59}, None) is None
    assert antrenare_lunga.retentia({}, {"fapte_noi": 72}) is None
    assert antrenare_lunga.retentia({"fapte_noi": 5}, {"fapte_noi": 0}) is None


def test_punctul_de_plecare_ia_criteriile_din_fisa_si_uneltele_peste_ele(tmp_path):
    jurnal = Jurnal(tmp_path)
    jurnal.adauga({"id": 1, "linie": "fapte_1", "decizie": "pastrat", "scoruri": {"val_bpb": 0.434},
                   "criterii": {"fapte_noi": 72, "nota_profesor": 4.75}})
    inainte = {"experiment": 1, "linie": "fapte_1", "ore": 4, "scor": 0.434}
    assert antrenare_lunga.punct_de_plecare(jurnal, inainte) == {"scor": 0.434, "fapte_noi": 72, "nota_profesor": 4.75}
    jurnal.adauga({"id": 2, "linie": "examen_fapte_nou", "decizie": "masurat", "module": {"elev": {"experiment": 1}},
                   "scoruri": {"fapte_noi": 70}})  # unealta de examen, mai nouă: are întâietate
    assert antrenare_lunga.punct_de_plecare(jurnal, inainte)["fapte_noi"] == 70
    assert antrenare_lunga.punct_de_plecare(jurnal, None) is None


def ora(numar, fapte_noi=None):
    criterii = {} if fapte_noi is None else {"fapte_noi": fapte_noi}
    return {"ora": numar, "experiment": 10 + numar, "scor": 0.45, "pasi": 100, "pasi_total": 100 * numar,
            "minute_total": 60.0 * numar, "simboluri": 1000, "simboluri_total": 1000 * numar, "treceri_prin_text": 0.1,
            "rata_la_final": 0.0001, "memorie_rezervata_mb": 2000, "decizie": "pastrat", "model_salvat": "x",
            "criterii": criterii}


def test_tabelul_are_coloana_r_doar_cand_se_poate_calcula():
    cu_r = antrenare_lunga.tabel([ora(1, 65), ora(2, 57)], pornire={"scor": 0.434, "fapte_noi": 72})
    assert cu_r[0].split()[:5] == ["ora", "val_bpb", "fapte", "fapte", "noi"] and " R " in cu_r[0]
    assert cu_r[1].endswith("1.00  (punctul de plecare)")
    assert "0.90" in cu_r[2] and "0.79" in cu_r[3]
    fara = antrenare_lunga.tabel([ora(1), ora(2)], pornire={"scor": 0.434})
    assert " R " not in fara[0]


def test_unealta_da_lui_kronos_modelul_de_pornire(tmp_path, monkeypatch):
    """Cu pornire.json lângă stare (linia a pornit dintr-un model), configurarea primită de kronos are porneste_din."""
    monkeypatch.chdir(tmp_path)
    text = (RADACINA / "config" / "proba.toml").read_text(encoding="utf-8")
    text = text.replace('modul = "module.model_ngram:ModelNgram"\nsetari = { ordin = 1, netezire = 1.0 }',
                        'modul = "teste.module_spion:ModelCuCriterii"\nsetari = { n_straturi = 2, n_capete = 2, '
                        'n_emb = 8, context = 8, lot = 2, rata_invatare = 0.001, cale_stare = "lucru/linia/gpt.pt" }')
    (tmp_path / "linie.toml").write_text(text, encoding="utf-8")
    (tmp_path / "lucru" / "linia").mkdir(parents=True)
    (tmp_path / "lucru" / "linia" / "gpt.pt").write_bytes(b"stare")
    (tmp_path / "lucru" / "linia" / "pornire.json").write_text(json.dumps(
        {"experiment": 252, "linie": "fapte_1", "ore": 4, "scor": 0.434}), encoding="utf-8")
    primite = []

    def ruleaza(config, *argumente, **optiuni):
        primite.append(config.porneste_din)
        return None  # ca o oprire: nicio oră făcută

    monkeypatch.setattr(antrenare_lunga, "ruleaza", ruleaza)
    assert antrenare_lunga.main(["--config", "linie.toml", "--ore", "1"]) == 1
    assert primite == [252]
