"""Faptele marcate greșite de om (planul joi–sâmbătă, lecția SANDBOX-7): marcate în examene, scoase din hrana viitoare.
Fără fișierul date/fapte/fapte_gresite.json, totul merge exact ca înainte."""

from __future__ import annotations

import json
import shutil

import pytest

pytest.importorskip("numpy")

from module import examene_elev  # noqa: E402
from module.fapte_gresite import numerotate, subiectele_gresite  # noqa: E402
from module.profesor_qwen import FAPTE, SUBIECTE  # noqa: E402
from teste.test_cap_coada import RADACINA  # noqa: E402
from unelte import genereaza_fapte  # noqa: E402


class ElevCareSpuneWater:
    tokenizer = "bpe"

    def completeaza(self, text: str, max_simboluri: int) -> str:
        return " water."


def cu_fapte_gresite(tmp_path, monkeypatch, numere: list[int]) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "date" / "fapte").mkdir(parents=True)
    (tmp_path / "date" / "fapte" / "fapte_gresite.json").write_text(json.dumps({"numere": numere, "de_la": "Adrian"}),
                                                                       encoding="utf-8")
    shutil.copyfile(RADACINA / "date" / "fapte" / "examen_nou.json", tmp_path / "date" / "fapte" / "examen_nou.json")


def test_numerotarea_e_cea_a_profesorului():
    assert len(numerotate()) == 50 and numerotate()[0] == (1, SUBIECTE[0][0], SUBIECTE[0][1])
    assert numerotate()[-1][0] == 50


def test_fara_fisier_examenele_raman_la_fel(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert subiectele_gresite() == set()
    randuri = examene_elev.examineaza_fapte(ElevCareSpuneWater())
    assert not any("fapt_gresit" in r for r in randuri)
    assert set(examene_elev.scor_fapte(randuri)) == {"fapte_corecte", "fapte_corecte_cu_sinonime", "fapte_stiute"}
    noi = examene_elev.examineaza_fapte_noi(ElevCareSpuneWater(), RADACINA / "date" / "fapte" / "examen_nou.json")
    assert set(examene_elev.scor_fapte_noi(noi)) == {"fapte_noi", "fapte_noi_cu_sinonime", "fapte_noi_stiute"}


def test_cu_fisier_faptele_se_marcheaza_nu_se_sterg(tmp_path, monkeypatch):
    cu_fapte_gresite(tmp_path, monkeypatch, [1, 3])
    gresite = {SUBIECTE[0][0], SUBIECTE[2][0]}
    assert subiectele_gresite() == gresite
    randuri = examene_elev.examineaza_fapte(ElevCareSpuneWater())
    assert len(randuri) == 150 and {r["subiect"] for r in randuri if r.get("fapt_gresit")} == gresite
    scor = examene_elev.scor_fapte(randuri)
    assert scor["fapte_gresite_marcate"] == 2
    assert scor["fapte_corecte_fara_gresite"] == sum(r["corect_cuvantul_din_fapt"] for r in randuri
                                                     if r["subiect"] not in gresite)
    assert scor["fapte_corecte"] == sum(r["corect_cuvantul_din_fapt"] for r in randuri)  # scorul vechi, neschimbat
    noi = examene_elev.examineaza_fapte_noi(ElevCareSpuneWater())
    scor_nou = examene_elev.scor_fapte_noi(noi)
    assert len(noi) == 150 and scor_nou["fapte_gresite_marcate"] == 2 and "fapte_noi_fara_gresite" in scor_nou


def test_numerele_care_nu_exista_sunt_refuzate(tmp_path, monkeypatch):
    cu_fapte_gresite(tmp_path, monkeypatch, [0, 51])
    with pytest.raises(ValueError, match="nu există"):
        subiectele_gresite()


def test_faptele_gresite_ies_din_hrana_viitoare(tmp_path):
    gresite = {SUBIECTE[0][0]}
    permise = [(s, f) for s, f in SUBIECTE if s not in gresite]
    assert all(genereaza_fapte.cererea(k, permise)[0] not in gresite for k in range(200))
    assert genereaza_fapte.cererea(0) == genereaza_fapte.cererea(0, SUBIECTE)  # fără fapte greșite: ca înainte
    toate = [{"subiect": s, "fapt": FAPTE[s], "poveste": f"Povestea despre {s}.", "nota": 9, "ramane": True,
              "motiv_scoatere": None, "aparitii_fapt": 1} for s, _ in SUBIECTE[:3]]
    info = genereaza_fapte.scrie_rezultatele(tmp_path, toate, 1.0, gresite)
    hrana = (tmp_path / "povesti.txt").read_text(encoding="utf-8")
    assert f"Povestea despre {SUBIECTE[0][0]}." not in hrana and f"Povestea despre {SUBIECTE[1][0]}." in hrana
    assert info["ramase"] == 2 and info["scoase_ca_gresite"] == 1 and info["fapte_gresite"] == sorted(gresite)


def test_lista_de_verificat_si_aplicarea(tmp_path):
    from unelte import fapte_de_verificat as fv

    text = fv.text_doc()
    assert text.count("\n| ") == 51 and "| 1 | " + SUBIECTE[0][1] in text and "Traducere" not in text
    cu = fv.text_doc(["Prof " + str(i) for i in range(1, 51)], ["Claude " + str(i) for i in range(1, 51)])
    assert "| 2 | " + SUBIECTE[1][1] + " | Claude 2 | Prof 2 |" in cu and "nu judeca faptele după ea" in cu
    # traducerile stau într-un fișier: una nouă de la profesor nu o șterge pe a lui Claude
    traduceri = tmp_path / "traduceri.json"
    traduceri.write_text(json.dumps({"fapte": [fapt for _, fapt in SUBIECTE], "claude": {"traduceri": ["c"] * 50}}),
                         encoding="utf-8")
    fv.salveaza_profesorul(["p"] * 50, traduceri)
    salvate = fv.citeste_traduceri(traduceri)
    assert salvate["claude"]["traduceri"] == ["c"] * 50 and salvate["profesor"]["traduceri"] == ["p"] * 50
    traduceri.write_text(json.dumps({"fapte": ["alt fapt"]}), encoding="utf-8")
    with pytest.raises(ValueError, match="alte fapte"):
        fv.citeste_traduceri(traduceri)
    assert fv.citeste_traduceri(tmp_path / "lipsa.json") == {}
    cale = tmp_path / "fapte_gresite.json"
    date = fv.aplica([17, 3, 3], cale)
    assert date["numere"] == [3, 17] and json.loads(cale.read_text(encoding="utf-8"))["de_la"] == "Adrian"
    assert subiectele_gresite(cale) == {SUBIECTE[2][0], SUBIECTE[16][0]}
    with pytest.raises(ValueError):
        fv.aplica([99], cale)
