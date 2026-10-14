"""Școala de cod: elevul (rețeaua GPT a lui Kronos), pe un model minuscul, pe procesor."""

from __future__ import annotations

import math

import pytest
import torch

from module.cod.elev import ElevCod, model_de_proba
from module.cod.mediu import citeste_abecedar, incercarea
from module.model_gpt import ModelGPT
from teste.cod_proba import RADACINA

ABECEDAR = citeste_abecedar(RADACINA / "date" / "cod" / "abecedar.txt")
REPETAT = "TEST: show 4\nWRITE:\n4\nRESULT:\n4\npassed\n\n" * 60


@pytest.fixture(scope="module")
def model_mic(tmp_path_factory):
    return model_de_proba(tmp_path_factory.mktemp("elev") / "mic.pt", ABECEDAR.text, context=256)


def greutati(elev: ElevCod) -> dict[str, torch.Tensor]:
    return {k: v.detach().clone() for k, v in elev.model.retea.state_dict().items()}


def test_generarea_e_reproductibila(model_mic):
    elev = ElevCod(model_mic, "cpu")
    fata = "TEST: show 4\nWRITE:\n"
    a = elev.genereaza(fata, 3, 1.0, 12, samanta=7)
    assert a == elev.genereaza(fata, 3, 1.0, 12, samanta=7) and len(a) == 3
    assert all(elev.numara(x) <= 12 + 1 for x in a)  # cel mult max_simboluri (+1 la recodificare)
    lacom = elev.genereaza(fata, 3, 0.0, 12, samanta=1)
    assert lacom[0] == lacom[1] == lacom[2] == elev.genereaza(fata, 1, 0.0, 12, samanta=99)[0]


def test_antrenarea_invata_si_generarea_se_opreste_la_result(tmp_path):
    """Pe un text repetat, câțiva pași ajung ca modelul să scrie „4” și să se oprească la „RESULT:”. Fără
    reconstruirea rețelei: zero pași = aceleași greutăți."""
    cale = model_de_proba(tmp_path / "rep.pt", REPETAT, context=64, marime_vocabular=280)
    elev = ElevCod(cale, "cpu")
    inainte = greutati(elev)
    elev.antreneaza(REPETAT, 0, 1e-3, 8, samanta=0)
    assert all(torch.equal(inainte[k], v) for k, v in greutati(elev).items())
    prima = elev.antreneaza(REPETAT, 5, 3e-3, 8, samanta=0)["pierdere_finala"]
    ultima = elev.antreneaza(REPETAT, 300, 3e-3, 8, samanta=1)["pierdere_finala"]
    assert ultima < prima / 3
    scris = elev.genereaza("TEST: show 4\nWRITE:\n", 2, 0.0, 20, samanta=0)[0]
    assert incercarea(scris) == ("4", True) and scris.endswith("RESULT:")


def test_salvarea_pastreaza_optimizatorul_si_ramane_model_kronos(model_mic, tmp_path):
    elev = ElevCod(model_mic, "cpu")
    elev.antreneaza(ABECEDAR.text, 3, 1e-3, 2, samanta=0)
    elev.salveaza(tmp_path / "linie.pt")
    inapoi = ElevCod(tmp_path / "linie.pt", "cpu")
    assert inapoi.pasi == 3 and inapoi.optimizator is not None
    assert all(torch.equal(greutati(elev)[k], v) for k, v in greutati(inapoi).items())
    stare = elev.optimizator.state_dict()["state"]
    assert all(torch.equal(stare[i]["exp_avg"], inapoi.optimizator.state_dict()["state"][i]["exp_avg"]) for i in stare)
    kronos = ModelGPT(tokenizer="bpe", dispozitiv="cpu")  # fișierul se încarcă și ca model Kronos obișnuit
    kronos.incarca(str(tmp_path / "linie.pt"))
    assert math.isclose(kronos.biti_pentru(ABECEDAR.text[:500]), inapoi.model.biti_pentru(ABECEDAR.text[:500]))
    assert 0 < inapoi.biti_pe_octet(ABECEDAR.text[:500]) < 50
    assert not (tmp_path / "linie.pt.tmp").exists()


def test_lotul_pe_bucati_face_acelasi_pas(model_mic):
    """v0.4: micro_lot trece lotul prin rețea pe bucăți; greutățile ies (aproape) la fel ca dintr-o singură trecere."""
    intreg, pe_bucati = ElevCod(model_mic, "cpu"), ElevCod(model_mic, "cpu")
    a = intreg.antreneaza(ABECEDAR.text, 3, 1e-3, 8, samanta=0)
    b = pe_bucati.antreneaza(ABECEDAR.text, 3, 1e-3, 8, samanta=0, micro_lot=3)  # 3 + 3 + 2
    assert b["micro_lot"] == 3 and "micro_lot" not in a and a["ferestre"] == b["ferestre"] == 24
    assert math.isclose(a["pierdere_finala"], b["pierdere_finala"], rel_tol=1e-3)
    for k, v in greutati(intreg).items():
        assert torch.allclose(v, greutati(pe_bucati)[k], atol=1e-4), k  # Adam mărește rotunjirile la gradienți ~0


def test_textul_prea_scurt_e_refuzat(model_mic):
    with pytest.raises(ValueError, match="sub contextul"):
        ElevCod(model_mic, "cpu").antreneaza("print(1)", 1, 1e-3, 2, samanta=0)


def test_povestile_intra_in_fiecare_lot(model_mic):
    """v0.2: 70% din fiecare lot vine din povești; la 0,7 × 10 = 7 ferestre pe pas."""
    elev = ElevCod(model_mic, "cpu")
    povesti = torch.tensor(elev.simboluri("Once upon a time, a little dog ran in the park. " * 80), dtype=torch.int16)
    cu = elev.antreneaza(ABECEDAR.text, 3, 1e-3, 10, samanta=0, povesti=povesti, fractie_povesti=0.7)
    assert cu["ferestre_povesti"] == 21 and cu["ferestre"] == 30
    fara = elev.antreneaza(ABECEDAR.text, 3, 1e-3, 10, samanta=0)
    assert fara["ferestre_povesti"] == 0
    impar = elev.antreneaza(ABECEDAR.text, 10, 1e-3, 24, samanta=0, povesti=povesti, fractie_povesti=0.7)
    assert impar["ferestre_povesti"] == 168  # 16,8 pe pas: pe rând 16 și 17, în medie exact 0,7


def test_pierderea_pe_abecedar_scade_cand_invata(tmp_path):
    cale = model_de_proba(tmp_path / "rep.pt", REPETAT, context=64, marime_vocabular=280)
    elev = ElevCod(cale, "cpu")
    inainte = elev.pierdere_pe(REPETAT)
    elev.antreneaza(REPETAT, 150, 3e-3, 8, samanta=0)
    dupa = elev.pierdere_pe(REPETAT)
    assert math.isfinite(inainte) and dupa < inainte / 2
    assert abs(dupa - elev.model.biti_pentru(REPETAT) * math.log(2) / len(elev.simboluri(REPETAT))) < 0.5
