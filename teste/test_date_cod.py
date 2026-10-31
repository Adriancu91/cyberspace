"""S57: modulul date_cod, examenul pe validare în biți pe octet și configurarea cod_c1 — fără placă și fără datele reale."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest

from module.date_cod import DateCod
from unelte.kronos_cod import examen_validare as ev

ARE_TORCH = importlib.util.find_spec("torch") is not None
RADACINA = Path(__file__).resolve().parents[1]
SF = 32_764  # sfârșitul de fișier, ca în setul real


def _scrie(d: Path, nume: str, fisiere: list[list[int]]) -> None:
    np.asarray([x for f in fisiere for x in f + [SF]], dtype=np.uint16).tofile(d / nume)


@pytest.fixture
def simboluri(tmp_path):
    """Antrenarea: simboluri 0–999, două blocuri; validarea: 2.000–2.999, trei fișiere în două blocuri."""
    g = np.random.default_rng(0)
    d = tmp_path / "simboluri"
    d.mkdir()
    _scrie(d, "antrenare_00000.bin", [g.integers(0, 1000, 700).tolist() for _ in range(3)])
    _scrie(d, "antrenare_00001.bin", [g.integers(0, 1000, 900).tolist() for _ in range(2)])
    _scrie(d, "validare_00000.bin", [list(range(2000, 2010)), list(range(2100, 2700))])
    _scrie(d, "validare_00001.bin", [list(range(2800, 2805))])
    return d


def test_bucatile_de_antrenare_au_512_simboluri(simboluri):
    date = DateCod(director=str(simboluri))
    b = date.bucati_antrenare(32, np.random.default_rng(1))
    assert b.shape == (32, 513) and b.dtype == np.int64  # 512 de intrare + ținta mutată cu unu
    assert len(date.simboluri_antrenare()) == 3 * 701 + 2 * 901
    # aceeași sămânță = aceleași bucăți
    assert np.array_equal(b, date.bucati_antrenare(32, np.random.default_rng(1)))


def test_validarea_nu_apare_in_antrenare(simboluri):
    date = DateCod(director=str(simboluri), context=64)
    vazute = date.bucati_antrenare(2000, np.random.default_rng(2))
    assert set(np.unique(vazute).tolist()) <= set(range(1000)) | {SF}  # nicio bucată cu simboluri de validare
    assert not np.isin(date.simboluri_validare(), date.simboluri_antrenare()[date.simboluri_antrenare() != SF]).any()
    assert all(f.name.startswith("antrenare_") for f in date.fisiere_antrenare)


def test_validarea_pe_fisiere_si_pe_bucati(simboluri):
    date = DateCod(director=str(simboluri), context=64)
    fisiere = date.fisiere_validare()
    assert [len(f) for f in fisiere] == [10, 600, 5]
    assert fisiere[1][0] == 2100 and fisiere[2][-1] == 2804 and SF not in np.concatenate(fisiere)
    b = date.bucati_validare()
    assert b.shape == ((618 - 1) // 64, 65)
    assert np.array_equal(b[1, 0], b[0, -1])  # una după alta, fiecare țintă o singură dată


def test_textul_cere_previzualizarea(simboluri):
    with pytest.raises(RuntimeError, match="simboluri"):
        DateCod(director=str(simboluri)).text_antrenare()


def test_director_lipsa_sau_gol(tmp_path):
    with pytest.raises(ValueError, match="Nu găsesc"):
        DateCod(director=str(tmp_path / "nu_exista"))
    with pytest.raises(ValueError, match="lipsesc"):
        DateCod(director=str(tmp_path))


def test_previzualizarea_decodeaza_textul(tmp_path):
    from teste.cod_mic import scrie_simboluri

    date = DateCod(**scrie_simboluri(tmp_path), context=16, previzualizare=True)
    assert date.text_antrenare().startswith("def aduna(a, b):")
    assert date.text_validare() == "def scade(a, b):\n    return a - b\nfn doi() -> u8 {\n    2\n}\nint zero(void) { return 0; }\n"


# --- examenul pe validare ------------------------------------------------------


def test_biti_pe_octet_calculat_de_mana():
    # 2 fișiere Python (4 + 6 simboluri, 10 + 20 octeți, 4 și 6 nats) și unul Rust (5 simboluri, 15 octeți, 10 nats)
    rez = ev.biti_pe_octet([4.0, 6.0, 10.0], [4, 6, 5], [("python", 10), ("python", 20), ("rust", 15)])
    # tot: 20 nats / ln 2 / 45 octeți = 0,64119…; pierderea medie 20 / 15 = 1,3333; 45 / 15 = 3 octeți pe simbol
    assert rez["tot"] == {"fisiere": 3, "octeti": 45, "simboluri": 15, "octeti_pe_simbol": 3.0,
                          "pierdere_medie": 1.33333, "biti_pe_octet": round(20 / math.log(2) / 45, 5)}
    assert rez["tot"]["biti_pe_octet"] == pytest.approx(rez["tot"]["pierdere_medie"] / math.log(2) / 3.0, abs=1e-4)
    assert rez["python"]["biti_pe_octet"] == round(10 / math.log(2) / 30, 5)
    assert rez["rust"]["octeti_pe_simbol"] == 3.0 and "c" not in rez
    with pytest.raises(ValueError, match="numere diferite"):
        ev.biti_pe_octet([1.0], [1, 2], [("c", 3)])


def test_bucatile_unui_fisier_noteaza_fiecare_simbol_o_data():
    f = np.arange(10, 21)  # 11 simboluri, context 4 → bucăți de 4, 4, 3
    b = ev.bucati_fisier(f, 4, SF)
    assert [len(y) for _, y in b] == [4, 4, 3]
    assert np.array_equal(np.concatenate([y for _, y in b]), f)
    assert b[0][0][0] == SF and b[1][0][0] == f[3]  # fiecare bucată pornește cu simbolul de dinaintea ei


@pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat")
def test_pierderea_cu_un_model_care_nu_stie_nimic():
    import torch

    vocab = 8

    def uniform(x):  # aceeași șansă pentru fiecare simbol: ln 8 nats pe simbol
        return torch.zeros(x.size(0), x.size(1), vocab)

    fisiere = [np.array([1, 2, 3, 4, 5, 6, 7]), np.array([2, 3])]
    p = ev.pierderi(uniform, fisiere, context=3, sfarsit=0, lot=2)
    assert p == pytest.approx([7 * math.log(8), 2 * math.log(8)], rel=1e-6)  # umplutura nu se notează
    rez = ev.biti_pe_octet(p, [7, 2], [("c", 21), ("c", 6)])
    assert rez["tot"]["biti_pe_octet"] == pytest.approx(9 * 3 / 27, abs=1e-5)  # 3 biți pe simbol, 3 octeți pe simbol


# --- configurarea cod_c1 ---------------------------------------------------------


def test_configurarea_cod_c1_se_incarca():
    from kronos.config import citeste_config

    cfg = citeste_config(RADACINA / "config" / "cod_c1.toml")
    assert cfg.nume == "cod_c1"
    m = cfg.setari_port("model")
    assert {k: m[k] for k in ("n_straturi", "n_capete", "n_emb", "context", "lot", "adunare_loturi", "rata_invatare",
                              "incalzire_pasi", "fractie_rata_finala", "durata_scaderii_secunde", "samanta",
                              "optimizator")} == {
        "n_straturi": 12, "n_capete": 12, "n_emb": 768, "context": 512, "lot": 8, "adunare_loturi": 12,
        "rata_invatare": 6e-4, "incalzire_pasi": 1000, "fractie_rata_finala": 0.1, "durata_scaderii_secunde": 36000,
        "samanta": 0, "optimizator": "adamw"}
    assert m["lot"] * m["adunare_loturi"] == 12 * 8  # același lot efectiv ca linia w2
    assert m["cale_tokenizer"].endswith("bpe_cod_32768.json") and "porneste_din" not in m
    assert cfg.porneste_din is None  # de la zero, nu din #477
    assert cfg.porturi["date"]["modul"] == "module.date_cod:DateCod"
    assert cfg.setari_port("date")["context"] == m["context"]
    assert cfg.paznic["memorie_gpu_max_mb"] == 7000 and cfg.paznic["temperatura_gpu_max"] == 83


@pytest.mark.skipif(not ARE_TORCH, reason="PyTorch nu e instalat")
def test_modelul_cod_c1_se_construieste_fara_sa_porneasca(tmp_path):
    """Setările modelului sunt primite de modul (fără antrenare, fără placă), cu un tokenizer mic în locul celui real."""
    from kronos.config import citeste_config
    from kronos.registru import Registru
    from teste.cod_mic import scrie_simboluri

    cfg = citeste_config(RADACINA / "config" / "cod_c1.toml")
    setari = {**cfg.setari_port("model"), "cale_tokenizer": scrie_simboluri(tmp_path)["cale_tokenizer"],
              "cale_stare": str(tmp_path / "cod_c1" / "gpt.pt"), "director_cache": str(tmp_path / "cache")}
    model = Registru().creeaza("model", cfg.porturi["model"]["modul"], setari).instanta
    assert model.retea is None and model.adunare_loturi == 12 and model.optimizator_ales == "adamw"
    assert not (tmp_path / "cod_c1").exists()
