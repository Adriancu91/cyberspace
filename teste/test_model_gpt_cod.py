"""S59: modelul care citește simbolurile direct (module/model_gpt_cod.py), examenul de la fiecare oră pe un eșantion fix
al validării (module/examen_cod_validare.py) și config/cod_c1.toml pe ele — pe procesor, fără datele reale."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from module.date_cod import DateCod  # noqa: E402
from module.examen_cod_validare import ExamenCodValidare  # noqa: E402
from module.model_gpt_cod import ModelGPTCod  # noqa: E402
from module.model_muon import ModelGPTConversatieMuon  # noqa: E402
from teste.cod_mic import VALIDARE, scrie_simboluri  # noqa: E402
from unelte.kronos_cod import examen_validare as ev  # noqa: E402

RADACINA = Path(__file__).resolve().parents[1]


@pytest.fixture
def cod(tmp_path):
    """Setul mic de cod (fără previzualizare: textul e refuzat) și setările unui GPT mic pe procesor."""
    s = scrie_simboluri(tmp_path)
    date = DateCod(director=s["director"], context=16, sfarsit_de_fisier=s["sfarsit_de_fisier"],
                   cale_tokenizer=s["cale_tokenizer"])
    setari = dict(n_straturi=1, n_capete=2, n_emb=32, context=16, lot=4, dispozitiv="cpu", tokenizer="bpe",
                  cale_tokenizer=s["cale_tokenizer"], rata_invatare=3e-3, samanta=0)
    return date, setari


def test_invata_din_simboluri_fara_sa_citeasca_textul(cod):
    """date_cod fără previzualizare refuză textul: dacă antrenarea merge, modelul a luat doar simbolurile. Aceeași
    sămânță → același prim lot, deci pierderea după 40 de pași se compară cu cea de la primul pas."""
    date, setari = cod
    primul = ModelGPTCod(**setari, pasi_max=1).antreneaza(date, 600.0)
    model = ModelGPTCod(**setari, pasi_max=40)
    st = model.antreneaza(date, 600.0)
    assert st["simboluri_direct"] is True and st["pasi"] == 40
    assert st["simboluri_antrenare"] == len(date.simboluri_antrenare())
    assert st["pierdere_finala"] < primul["pierdere_finala"] - 0.5
    assert model._date_simboluri is None  # nu ține datele după antrenare


def test_simbolurile_raman_in_ram_ca_int32(cod):
    date, setari = cod
    from module.tokenizer_bpe import TokenizerBPE

    model = ModelGPTCod(**setari)
    model.tok = TokenizerBPE.incarca(setari["cale_tokenizer"])  # ca în antreneaza, înainte de simboluri
    model._date_simboluri = date
    t = model._simboluri("")
    assert t.dtype == torch.int32 and t.device.type == "cpu"
    assert np.array_equal(t.numpy(), date.simboluri_antrenare().astype(np.int32))


def test_refuza_simboluri_peste_vocabular_si_setari_cu_text(cod, tmp_path):
    date, setari = cod
    d = tmp_path / "mari"
    d.mkdir()
    np.arange(5000, dtype=np.uint16).tofile(d / "antrenare_00000.bin")
    np.arange(100, dtype=np.uint16).tofile(d / "validare_00000.bin")
    mari = DateCod(director=str(d), context=16, cale_tokenizer=setari["cale_tokenizer"])
    with pytest.raises(ValueError, match="tokenizerul are doar"):
        ModelGPTCod(**setari, pasi_max=1).antreneaza(mari, 60.0)
    with pytest.raises(ValueError, match="tokenizer"):
        ModelGPTCod(**{**setari, "tokenizer": "litere"}, pasi_max=1).antreneaza(date, 60.0)
    (tmp_path / "hrana.txt").write_text("def f(): pass\n" * 50, encoding="utf-8")
    with pytest.raises(ValueError, match="hrana"):
        ModelGPTCod(**setari, pasi_max=1, hrana=str(tmp_path / "hrana.txt"), fractie_hrana=0.25).antreneaza(date, 60.0)


def test_pe_text_face_exact_ce_face_muon(cod, tmp_path):
    """Cu date pe text (fără simboluri_antrenare), aceiași pași, bit cu bit, ca ModelGPTConversatieMuon."""
    _, setari = cod

    class Text:
        def text_antrenare(self):
            return "def aduna(a, b):\n    return a + b\n" * 40

    setari = {**setari, "pasi_max": 12, "adunare_loturi": 2}
    vechi, nou = ModelGPTConversatieMuon(**setari), ModelGPTCod(**setari)
    s_vechi = vechi.antreneaza(Text(), 600.0)
    a = {k: v.clone() for k, v in vechi.retea.state_dict().items()}
    s_nou = nou.antreneaza(Text(), 600.0)
    assert s_vechi["pierdere_finala"] == s_nou["pierdere_finala"] and "simboluri_direct" not in s_nou
    b = nou.retea.state_dict()
    assert all(torch.equal(a[k], b[k]) for k in a)


def test_starea_se_salveaza_si_se_reia(cod, tmp_path):
    """Ca linia w2: ora următoare pornește din starea salvată după examen."""
    date, setari = cod
    setari = {**setari, "pasi_max": 5, "cale_stare": str(tmp_path / "cod" / "gpt.pt")}
    m = ModelGPTCod(**setari)
    m.antreneaza(date, 600.0)
    assert m.dupa_examen({"scor": 3.0})["continuare"]["salvat"] is True
    st = ModelGPTCod(**setari).antreneaza(date, 600.0)
    assert st["continuat"] is True and st["pasi_total"] == 10


# --- examenul de la fiecare oră -----------------------------------------------------------------


def test_esantionul_e_mereu_acelasi():
    a, b = ExamenCodValidare(fisiere=100), ExamenCodValidare(fisiere=100)
    e = a.esantion(5686)
    assert e == a.esantion(5686) == b.esantion(5686)  # la două rulări și la două examene noi
    assert len(e) == len(set(e)) == 100 and e == sorted(e) and 0 <= e[0] and e[-1] < 5686
    assert ExamenCodValidare(fisiere=100, samanta=1).esantion(5686) != e
    assert ExamenCodValidare(fisiere=1000).esantion(7) == list(range(7))


def test_examenul_pe_simboluri_e_examen_validare_pe_esantion(cod):
    """val_bpb = suma pierderilor / ln 2 / octeții textului adevărat (din cod_mic), pe fișierele eșantionului."""
    date, setari = cod
    model = ModelGPTCod(**setari, pasi_max=20)
    model.antreneaza(date, 600.0)
    examen = ExamenCodValidare(fisiere=2, lot=2)
    rez = examen.examineaza(model, date)
    alese = examen.esantion(3)
    texte = [t for bloc in VALIDARE for t, _ in bloc]
    fisiere = date.fisiere_validare()
    p = ev.pierderi(lambda x: model.retea(x), [fisiere[k] for k in alese], 16, date.sfarsit_de_fisier, lot=2)
    octeti = sum(len(texte[k].encode("utf-8")) for k in alese)
    assert rez["fisiere_examinate"] == 2 and rez["octeti_examinati"] == octeti
    assert rez["val_bpb"] == pytest.approx(sum(p) / math.log(2) / octeti, abs=1e-5)
    assert examen.examineaza(model, date)["val_bpb"] == rez["val_bpb"]  # aceeași notă la a doua rulare


def test_examenul_fara_simboluri_e_pe_text(cod):
    """Pe date pe text sau pe un model fără rețea: biți pe octet pe textul de validare, prin biti_pentru."""

    class Text:
        def text_validare(self):
            return "abc" * 50

    class Model:
        retea = None

        def biti_pentru(self, text):
            return 2.0 * len(text.encode("utf-8"))

    rez = ExamenCodValidare(max_caractere=100).examineaza(Model(), Text())
    assert rez == {"val_bpb": 2.0, "caractere_examinate": 100.0}


# --- config/cod_c1.toml pe modulele noi --------------------------------------------------------


def test_cod_c1_foloseste_modelul_si_examenul_noi(tmp_path):
    from kronos.config import citeste_config
    from kronos.registru import Registru

    cfg = citeste_config(RADACINA / "config" / "cod_c1.toml")
    assert cfg.porturi["model"]["modul"] == "module.model_gpt_cod:ModelGPTCod"
    assert cfg.porturi["examen"]["modul"] == "module.examen_cod_validare:ExamenCodValidare"
    assert cfg.setari_port("examen") == {"fisiere": 1000, "samanta": 0, "lot": 8}
    assert cfg.setari_port("date")["previzualizare"] is True  # testul rapid al lui Kronos cere text_validare()
    examen = Registru().creeaza("examen", cfg.porturi["examen"]["modul"], cfg.setari_port("examen")).instanta
    assert examen.scor_principal == "val_bpb" and examen.mai_mic_e_mai_bun
    setari = {**cfg.setari_port("model"), "cale_tokenizer": scrie_simboluri(tmp_path)["cale_tokenizer"],
              "cale_stare": str(tmp_path / "cod_c1" / "gpt.pt"), "dispozitiv": "cpu"}
    model = Registru().creeaza("model", cfg.porturi["model"]["modul"], setari).instanta
    assert isinstance(model, ModelGPTCod) and model.retea is None and not (tmp_path / "cod_c1").exists()


def config_cod_c1_mic(tmp_path) -> Path:
    """config/cod_c1.toml așa cum e, doar micșorat (rețea, context, setul mic, 2 secunde pe „oră”, pe procesor)."""
    s = scrie_simboluri(tmp_path)
    text = (RADACINA / "config" / "cod_c1.toml").read_text(encoding="utf-8")
    for vechi, nou in (("buget_antrenare_secunde = 3600", "buget_antrenare_secunde = 2"),
                       ("n_straturi = 12, n_capete = 12, n_emb = 768", "n_straturi = 1, n_capete = 2, n_emb = 32"),
                       ("context = 512", "context = 16"), ("adunare_loturi = 12", "adunare_loturi = 2"),
                       ('director = "lucru/kronos_cod/simboluri"', f'director = {json.dumps(s["director"])}'),
                       ('"lucru/kronos_cod/tokenizer/bpe_cod_32768.json"', json.dumps(s["cale_tokenizer"])),
                       ("sfarsit_de_fisier = 32764", f'sfarsit_de_fisier = {s["sfarsit_de_fisier"]}'),
                       ('optimizator = "adamw"', 'optimizator = "adamw", dispozitiv = "cpu"'),
                       ('modul = "module.interfata_consola:InterfataConsola"',
                        'modul = "module.interfata_consola:InterfataConsola"\nsetari = { tacut = true }')):
        assert vechi in text, vechi
        text = text.replace(vechi, nou)
    cale = tmp_path / "cod_c1.toml"
    cale.write_text(text, encoding="utf-8")
    return cale


# --- S61: inițializarea încorporărilor (abatere_incorporari) ------------------------------------

# Amprenta greutăților de pornire ale lui config_cod_c1_mic, calculată ÎNAINTE de S61 cu module/model_gpt_cod.py din
# 614cc17 (lucru/cascada/S61_proba/amprenta.py). Fără setare, rețeaua de pornire trebuie să rămână bit cu bit aceeași.
AMPRENTA_PORNIRE_COD_C1_MIC = "cf071a34f39ee153e0c05dfc2aada301dc4ea6da7af2112435ac55ccf84d510f"


def _amprenta_pornire(setari: dict) -> str:
    import hashlib

    from module.tokenizer_bpe import TokenizerBPE

    model = ModelGPTCod(**setari)
    model.tok = TokenizerBPE.incarca(setari["cale_tokenizer"])
    model._construieste()
    h = hashlib.sha256()
    for k, v in sorted(model.retea.state_dict().items()):
        h.update(k.encode())
        h.update(v.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def test_fara_abatere_reteaua_de_pornire_e_cea_de_dinainte(tmp_path):
    from kronos.config import citeste_config

    setari = citeste_config(config_cod_c1_mic(tmp_path)).setari_port("model")
    assert "abatere_incorporari" not in setari
    assert _amprenta_pornire(setari) == AMPRENTA_PORNIRE_COD_C1_MIC
    assert _amprenta_pornire({**setari, "abatere_incorporari": 0.02}) != AMPRENTA_PORNIRE_COD_C1_MIC


def test_cu_abatere_002_primul_lot_e_sub_dublul_hazardului(cod):
    """Cu încorporările mici, la pornire modelul nu mai e sigur pe simboluri greșite: pierderea primului lot pe setul
    mic e sub 2 × ln(mărimea vocabularului)."""
    from module.tokenizer_bpe import TokenizerBPE

    date, setari = cod
    model = ModelGPTCod(**setari, pasi_max=1, abatere_incorporari=0.02)
    st = model.antreneaza(date, 600.0)
    assert st["pierdere_finala"] < 2 * math.log(TokenizerBPE.incarca(setari["cale_tokenizer"]).marime)
    e = model.retea.emb_token.weight
    assert model.retea.cap.weight is e  # capul rămâne legat de încorporări
    with pytest.raises(ValueError, match="abatere_incorporari"):
        ModelGPTCod(**setari, abatere_incorporari=0.0)


def test_cod_c1_init002_difera_de_cod_c1_doar_prin_abatere():
    from kronos.config import citeste_config

    a = citeste_config(RADACINA / "config" / "cod_c1.toml")
    b = citeste_config(RADACINA / "config" / "cod_c1_init002.toml")
    assert b.setari_port("model") == {**a.setari_port("model"), "abatere_incorporari": 0.02}
    assert b.porturi.keys() == a.porturi.keys()
    for port in a.porturi:
        assert b.porturi[port]["modul"] == a.porturi[port]["modul"]
        if port != "model":
            assert b.setari_port(port) == a.setari_port(port), port


def test_cod_c1_cap_coada_prin_antrenare_lunga_pe_setul_mic(tmp_path, monkeypatch):
    """Comanda din S58 (`antrenare_lunga.py --config config/cod_c1.toml`), cu kronos/ neschimbat, pe config-ul micșorat:
    testul rapid, antrenarea pe simboluri, examenul pe eșantion, decizia, starea salvată și ora a doua din ea."""
    from unelte import antrenare_lunga

    monkeypatch.chdir(tmp_path)
    cale = config_cod_c1_mic(tmp_path)
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "2", "--pauza", "0", "--racire", "0",
                                 "--lungime", "40"]) == 0
    fise = [json.loads(r) for r in
            (tmp_path / "lucru" / "jurnal" / "experimente.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(fise) == 2 and all(f["decizie"] != "anulat" for f in fise), [f.get("motiv") for f in fise]
    assert fise[0]["module"]["model"]["nume"] == "model_gpt_cod"
    assert fise[0]["module"]["examen"]["nume"] == "examen_cod_validare"
    assert fise[0]["setari"]["model"]["hrana"] == ""  # fără hrana implicită a antrenării lungi
    for f in fise:
        assert f["statistici_antrenare"]["simboluri_direct"] is True
        assert f["scoruri"]["fisiere_examinate"] == 3 and math.isfinite(f["scoruri"]["val_bpb"])
    assert (tmp_path / "lucru" / "cod_c1" / "gpt.pt").exists()
    assert fise[1]["statistici_antrenare"]["continuat"] is True  # ora a doua pornește din starea primei
    assert fise[1]["statistici_antrenare"]["pasi_total"] > fise[0]["statistici_antrenare"]["pasi_total"]
