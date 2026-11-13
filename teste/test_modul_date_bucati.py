"""S98 (C-85 pasul 5, partea b): module/date_bucati.py — ferestrele de antrenare citite prin mmap din bucăți sunt
aceleași ca din tensorul întreg (și la granița dintre bucăți), modulul refuză bucățile stricate și își ia amprenta din
index, fără textul brut. Modulul nu e legat de nicio configurare în uz."""

import hashlib
import json
import tomllib
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from kronos.registru import Registru  # noqa: E402
from module.date_bucati import DateBucati, SirBucati  # noqa: E402
from teste.bucati_mici import TEXT, VALIDARE, scrie_bucati  # noqa: E402
from unelte import date_bucati as db  # noqa: E402

RADACINA = Path(__file__).resolve().parents[1]
CTX = 16


def _intreg(setari):
    """Șirul întreg, cum îl ține antrenarea de acum (tensorul din cache)."""
    return torch.load(Path(setari["director"]).parent / "simboluri_mici.pt", weights_only=True)


@pytest.fixture
def setari(tmp_path):
    return scrie_bucati(tmp_path, marime=10)  # bucăți mai mici decât fereastra: o fereastră trece prin 2–3 bucăți


def test_toate_ferestrele_identice_si_la_granita(setari):
    d = DateBucati(**setari)
    t = _intreg(setari)
    assert d.numar_simboluri() == len(t) > 500 and len(d.index["bucati"]) > 50
    pozitii = list(range(len(t) - CTX - 1))  # toate locurile posibile, deci toate granițele
    x, y = d.ferestre(pozitii, CTX)
    assert x.dtype == y.dtype == torch.int64 and x.shape == (len(pozitii), CTX)
    assert torch.equal(x, torch.stack([t[p:p + CTX].long() for p in pozitii]))
    assert torch.equal(y, torch.stack([t[p + 1:p + CTX + 1].long() for p in pozitii]))
    sir = d.sir_antrenare()
    assert len(sir.bucati_atinse(5, 5 + CTX + 1)) == 3  # fereastra de la 5 trece prin bucățile 0, 1, 2
    with pytest.raises(ValueError, match="iese din șir"):
        d.ferestre([len(t) - CTX], CTX)


def test_loturile_cu_aceeasi_samanta_sunt_cele_din_bucla_de_antrenare(setari):
    d = DateBucati(**setari)
    date_t = torch.as_tensor(_intreg(setari))
    sir = d.sir_antrenare()
    lot, samanta = 4, 0
    g_vechi = torch.Generator(device="cpu").manual_seed(samanta)
    g_nou = torch.Generator(device="cpu").manual_seed(samanta)
    g_sir = torch.Generator(device="cpu").manual_seed(samanta)
    for _ in range(200):
        # calea veche: rândurile din module/model_gpt.py (bucla de antrenare, fără hrană)
        pozitii = torch.randint(len(date_t) - CTX - 1, (lot,), generator=g_vechi)
        x = torch.stack([date_t[p: p + CTX] for p in pozitii]).long()
        y = torch.stack([date_t[p + 1: p + CTX + 1] for p in pozitii]).long()
        x_nou, y_nou = d.lot(lot, CTX, g_nou)
        assert torch.equal(x, x_nou) and torch.equal(y, y_nou)
        # aceleași rânduri, cu șirul pe bucăți în locul tensorului (capetele feliei sunt tensori, ca în buclă)
        pozitii = torch.randint(len(sir) - CTX - 1, (lot,), generator=g_sir)
        assert torch.equal(x, torch.stack([sir[p: p + CTX] for p in pozitii]).long())
        assert torch.equal(y, torch.stack([sir[p + 1: p + CTX + 1] for p in pozitii]).long())


def test_sirul_se_poarta_ca_tensorul_intreg(setari):
    d = DateBucati(**setari)
    t = _intreg(setari)
    sir = d.sir_antrenare()
    assert isinstance(sir, SirBucati) and len(sir) == len(t) and sir.tip == np.dtype("<i2")
    assert torch.equal(sir[:], t) and sir[:].dtype == t.dtype
    assert torch.equal(sir[7:43], t[7:43]) and torch.equal(sir[-5:], t[-5:]) and len(sir[20:20]) == 0
    assert torch.equal(sir[len(t) - 3:len(t) + 50], t[len(t) - 3:])
    with pytest.raises(TypeError):
        sir[3]
    with pytest.raises(TypeError):
        sir[0:10:2]


def test_refuza_bucata_stricata_lipsa_sau_indexul_partial(setari, tmp_path):
    dosar = Path(setari["director"])
    DateBucati(**setari)  # întreg: pornește
    bucata = dosar / "bucata_00003.bin"
    bun = bucata.read_bytes()
    bucata.write_bytes(bytes([bun[0] ^ 1]) + bun[1:])
    with pytest.raises(ValueError, match="nu trec verificarea.*bucata_00003.bin.*SHA diferit"):
        DateBucati(**setari)
    assert not db.verifica(dosar)["ok"]  # la fel zice și unealta din S96
    bucata.write_bytes(bun + b"\0\0")
    with pytest.raises(ValueError, match="altă mărime"):
        DateBucati(**setari)
    bucata.unlink()
    with pytest.raises(ValueError, match="lipsește"):
        DateBucati(**setari)
    bucata.write_bytes(bun)
    assert DateBucati(**setari).verificare == {"bucati": len(db.citeste_index(dosar)["bucati"]), "gresite": [], "ok": True}
    index = json.loads((dosar / "index.json").read_text(encoding="utf-8"))
    (dosar / "index.json").write_text(json.dumps(index | {"partial": True}), encoding="utf-8")
    with pytest.raises(ValueError, match="parțial"):
        DateBucati(**setari)
    (dosar / "index.json").write_text(json.dumps(index | {"sha256_tot": "0" * 64}), encoding="utf-8")
    with pytest.raises(ValueError, match="tot șirul"):
        DateBucati(**setari)
    (dosar / "index.json").write_text(json.dumps(index | {"versiune": 2}), encoding="utf-8")
    with pytest.raises(ValueError, match="versiune necunoscută"):
        DateBucati(**setari)
    (dosar / "index.json").write_text(json.dumps(index), encoding="utf-8")
    alt_tokenizer = tmp_path / "alt.json"
    alt_tokenizer.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="alt tokenizer"):
        DateBucati(**(setari | {"cale_tokenizer": str(alt_tokenizer)}))
    with pytest.raises(ValueError, match="index.json"):
        DateBucati(**(setari | {"director": str(tmp_path / "nu_exista")}))


def test_amprenta_vine_din_index_fara_textul_brut(setari, tmp_path, monkeypatch):
    citite = []
    citeste_text = Path.read_text

    def spion(self, *a, **k):
        citite.append(self.name)
        return citeste_text(self, *a, **k)

    monkeypatch.setattr(Path, "read_text", spion)
    d = DateBucati(**setari)
    amprenta = d.amprenta()
    assert sorted(citite) == ["index.json", "validare_bucati.txt"]  # niciun text de antrenare (nici nu există pe disc)
    index = db.citeste_index(Path(setari["director"]))
    tok_sha = hashlib.sha256(Path(setari["cale_tokenizer"]).read_bytes()).hexdigest()
    assert index["tokenizer"]["sha256"] == tok_sha
    assert amprenta == hashlib.sha256(f"{index['sha256_tot']}:{tok_sha}".encode("ascii")).hexdigest()[:16]
    descriere = d.descriere()
    assert descriere["amprenta"] == amprenta and descriere["sha256_tot"] == index["sha256_tot"]
    assert descriere["simboluri"] == index["simboluri_total"] and descriere["bucati"] == len(index["bucati"])
    # alte simboluri → altă amprentă
    alt = tmp_path / "alt"
    alt.mkdir()
    sursa = alt / "s.pt"
    torch.save(torch.arange(300, dtype=torch.int16), sursa)
    db.scrie(sursa, alt / "bucati", 64, Path(setari["cale_tokenizer"]), 0.0)
    assert DateBucati(**(setari | {"director": str(alt / "bucati")})).amprenta() != amprenta


def test_textul_e_doar_previzualizare(setari):
    d = DateBucati(**setari)
    assert d.text_validare() == VALIDARE
    with pytest.raises(RuntimeError, match="nu text"):
        d.text_antrenare()
    p = DateBucati(**setari, previzualizare=True, simboluri_previzualizare=50)
    text = p.text_antrenare()
    assert TEXT.startswith(text) and 20 < len(text) < len(TEXT)
    assert DateBucati(**setari, previzualizare=True).text_antrenare() == TEXT  # tot șirul mic încape în previzualizare


def test_modelele_de_acum_refuza_modulul_nelegat(setari):
    """Neactivat: un model care cere textul întreg nu poate învăța din greșeală din acest modul."""
    date = Registru().creeaza("date", "module.date_bucati:DateBucati", setari).instanta
    model = Registru().creeaza("model", "module.model_ngram:ModelNgram", {"ordin": 2}).instanta
    with pytest.raises(RuntimeError, match="nu text"):
        model.antreneaza(date, 1.0)


# --- unelte/bucati_legare.py: proba de identitate și măsurarea pornirii, cap-coadă pe un set mic -----------------


def _config_mic(tmp_path, setari):
    def t(cale):
        return str(cale).replace("\\", "/")

    config = tmp_path / "proba.toml"
    config.write_text(
        '[porturi.model]\nmodul = "module.model_ngram:ModelNgram"\n'
        f'setari = {{ context = {CTX}, lot = 4, samanta = 0 }}\n'
        '[porturi.date]\nmodul = "module.date_bucati:DateBucati"\n'
        f'setari = {{ director = "{t(setari["director"])}", cale_validare = "{t(setari["cale_validare"])}", '
        f'cale_tokenizer = "{t(setari["cale_tokenizer"])}" }}\n', encoding="utf-8")
    return config


def test_proba_de_identitate_cap_coada(setari, tmp_path, capsys):
    from unelte import bucati_legare as bl

    config = _config_mic(tmp_path, setari)
    iesire = tmp_path / "iesire" / "identitate.json"
    assert bl.main(["identitate", "--config", str(config), "--loturi", "50", "--iesire", str(iesire)]) == 0
    rez = json.loads(iesire.read_text(encoding="utf-8"))
    assert json.loads(capsys.readouterr().out.strip().splitlines()[-1]) == rez
    assert rez["verdict"] == "DA" and rez["identic"] and rez["primul_lot_diferit"] is None and rez["cache_neschimbat"]
    assert len(set(rez["sha256_loturi"].values())) == 1 and rez["loturi"] == 50
    assert rez["ferestre_la_granita_in_loturile_trase"] == 200  # bucăți de 10, ferestre de 17: toate trec o graniță
    granite = rez["loturi_la_granita"]
    assert len(granite) == 4 and all(g["identic"] for g in granite)
    assert all(len(b) > 1 for g in granite[:3] for b in g["bucati_atinse"])
    assert granite[3]["pozitii"][0] == 0 and granite[3]["pozitii"][-1] == rez["simboluri_bucati"] - CTX - 2
    with pytest.raises(FileExistsError):
        bl.main(["identitate", "--config", str(config), "--loturi", "50", "--iesire", str(iesire)])


def test_proba_de_identitate_vede_un_cache_diferit(setari, tmp_path):
    """Dacă tensorul întreg nu mai e cel din care s-au făcut bucățile, verdictul e NU, cu primul lot diferit."""
    from unelte import bucati_legare as bl

    sursa = Path(setari["director"]).parent / "simboluri_mici.pt"
    t = torch.load(sursa, weights_only=True)
    t[len(t) // 2:] += 1
    torch.save(t, sursa)
    iesire = tmp_path / "identitate.json"
    assert bl.main(["identitate", "--config", str(_config_mic(tmp_path, setari)), "--loturi", "50",
                    "--iesire", str(iesire)]) == 1
    rez = json.loads(iesire.read_text(encoding="utf-8"))
    assert rez["verdict"] == "NU" and rez["primul_lot_diferit"]["sha_vechi"] != rez["primul_lot_diferit"]["sha_nou"]
    assert rez["primul_lot_diferit"]["sha_nou"] == rez["primul_lot_diferit"]["sha_sir"]


def test_masurarea_pornirii_cap_coada(setari, tmp_path):
    from unelte import bucati_legare as bl

    reper = tmp_path / "reper.json"
    reper.write_text(json.dumps({"pornire_linie": {"ram_varf_mb": 41685, "secunde_total": 40.56}}), encoding="utf-8")
    iesire = tmp_path / "pornire.json"
    assert bl.main(["pornire", "--config", str(_config_mic(tmp_path, setari)), "--iesire", str(iesire),
                    "--reper", str(reper)]) == 0
    rez = json.loads(iesire.read_text(encoding="utf-8"))
    assert rez["nou"]["verificare"]["ok"] and rez["nou"]["simboluri"] == DateBucati(**setari).numar_simboluri()
    assert rez["nou"]["amprenta"] == DateBucati(**setari).amprenta() and len(rez["nou"]["primul_lot_sha256"]) == 64
    assert rez["vechi_s96"]["ram_varf_mb"] == 41685 and rez["asteptare_sub_4000_mb"] and rez["ram_de_cate_ori_mai_putin"] > 1


def test_portul_date_trebuie_sa_fie_modulul_pe_bucati(tmp_path):
    from unelte import bucati_legare as bl

    with pytest.raises(ValueError, match="portul date"):
        bl.identitate(RADACINA / "config" / "conv_w2_mare_24r.toml", 1)


# --- configurarea de probă (nu se antrenează cu ea) -------------------------------------------------------------


def _toml(nume):
    return tomllib.loads((RADACINA / "config" / nume).read_text(encoding="utf-8"))


def test_configurarea_de_proba_difera_de_24r_doar_prin_portul_date_si_nume():
    r, b = _toml("conv_w2_mare_24r.toml"), _toml("conv_w2_mare_24_bucati.toml")
    assert b["platforma"]["nume"] == "proba_bucati"
    assert b["porturi"]["model"]["setari"]["cale_stare"] == "lucru/proba_bucati/gpt.pt"
    assert b["porturi"]["date"] == {
        "modul": "module.date_bucati:DateBucati",
        "setari": {"director": "lucru/bucati/w2_amestec_be12", "cale_validare": "date/tinystories_r2/validare.txt",
                   "cale_tokenizer": "date/ws/bpe_16384.json"}}
    assert b["porturi"]["date"]["setari"]["cale_validare"] == r["porturi"]["date"]["setari"]["cale_validare"]
    assert b["porturi"]["date"]["setari"]["cale_tokenizer"] == r["porturi"]["model"]["setari"]["cale_tokenizer"]
    b["platforma"]["nume"] = r["platforma"]["nume"]
    b["porturi"]["model"]["setari"]["cale_stare"] = r["porturi"]["model"]["setari"]["cale_stare"]
    b["porturi"]["date"] = r["porturi"]["date"]
    b["antrenare_lunga"]["eticheta"] = r["antrenare_lunga"]["eticheta"]
    assert b == r


def test_modulul_nu_e_in_nicio_configurare_in_uz():
    """S98: neactivat. O configurare de antrenare cu datele pe bucăți se adaugă aici doar cu sarcina care o cere."""
    cu_bucati = {c.name for c in (RADACINA / "config").rglob("*.toml") if "date_bucati" in c.read_text(encoding="utf-8")}
    # S104 (C-110, 12 nov 2026): proba_placa_bucati.toml = configurarea de probă a rulării B de pe placă (nu o linie de model)
    # S110 (C-119 E2, Adrian 13 nov 2026): conv_w2_mare_24z.toml = prima linie de model pe bucăți, cerută de sarcină
    assert cu_bucati == {"conv_w2_mare_24_bucati.toml", "proba_placa_bucati.toml", "conv_w2_mare_24z.toml"}
