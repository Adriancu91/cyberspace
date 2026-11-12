"""S104 (C-110): unealta probei pe placă a datelor pe bucăți (unelte/proba_placa.py), verificată aici pe procesor, cu un
model mic: V1, V2 (datele vechi) și B (bucățile) din aceeași stare de pornire; verdictul după pragurile sarcinii; paza
plăcii; cele două configurări de probă din config/."""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from teste.bucati_mici import TEXT  # noqa: E402
from teste.test_legare_bucati import mic  # noqa: E402, F401  (setul mic pe bucăți + cele două configurări mici)
from unelte import antrenare_recalcul  # noqa: E402
from unelte import proba_placa as pp  # noqa: E402

RADACINA = Path(__file__).resolve().parents[1]
CTX = 16
ADUNARE = 4
PASI = 3  # pași de optimizare → 12 loturi


def _in_plus(**altele):
    return dict(n_straturi=2, n_capete=2, n_emb=32, context=CTX, lot=4, dispozitiv="cpu", rata_invatare=1e-3,
                optimizator="muon", rata_muon=0.0001, adunare_loturi=ADUNARE) | altele


def _stare_de_pornire(mic, cale, pasi_total=100):  # noqa: F811
    """O stare ca a platformei (fără optimizator pornit), din care pornesc toate rulările."""
    from kronos.registru import Registru
    from module.model_continuu import salveaza_atomic

    c = tomllib.loads(mic["vechi"].read_text(encoding="utf-8"))
    setari = dict(c["porturi"]["model"]["setari"]) | _in_plus()
    model = Registru().creeaza("model", c["porturi"]["model"]["modul"], setari).instanta
    from module.tokenizer_bpe import TokenizerBPE

    model.tok = TokenizerBPE.incarca(model.cale_tokenizer)
    model._pregateste_reteaua()
    salveaza_atomic({"setari": model.setari, "retea": model.retea.state_dict(),
                     "optimizator": {"state": {}, "param_groups": []}, "pasi_total": pasi_total, "minute": 0.0,
                     "scor": 1.0}, cale)
    return pp.sha_fisier(cale)


def test_proba_mica_da_din_aceeasi_stare(mic, tmp_path):  # noqa: F811
    stare = tmp_path / "pornire" / "gpt.pt"
    sha = _stare_de_pornire(mic, stare)
    dosar = tmp_path / "proba"
    rez = pp.tot(mic["vechi"], mic["bucati"], dosar, pasi_optimizare=PASI, in_proces=True,
                 in_plus=_in_plus(cale_stare=str(stare)))
    assert rez == json.loads((dosar / "s104.json").read_text(encoding="utf-8"))
    assert rez["verdict"] == "DA" and rez["pe_loturi_informativ"]["verdict"] == "DA"
    assert rez["pe_pasi_de_optimizare"]["prag"] == pp.PRAG_MINIM  # procesorul se repetă: zgomot 0
    assert rez["starea_de_pornire_neschimbata"] and rez["aceeasi_stare_de_pornire"]
    assert rez["doar_citite_neschimbate"] == {"bucati": True}
    for pereche in ("V1_fata_de_B", "V1_fata_de_V2", "V2_fata_de_B"):
        c = rez[pereche]
        assert c["loturi_identice"] and c["greutati_identice"] and c["primul_lot_diferit"] is None
        assert c["pe_pasi"]["identice"] and c["pe_pasi"]["maxima"] == 0.0 and c["pe_pasi"]["comparate"] == PASI
        assert c["pe_loturi"]["identice"] and c["pe_loturi"]["comparate"] == PASI * ADUNARE
    assert set(rez["tabel"]) == {"1", str(PASI)} and rez["tabel"]["1"]["V1"] == rez["tabel"]["1"]["B"]
    for nume in pp.RULARI:
        r = json.loads((dosar / f"{nume}.json").read_text(encoding="utf-8"))
        assert r["loturi_facute"] == PASI * ADUNARE and r["pasi_optimizare"] == PASI == len(r["pierderi_pe_pas"])
        assert r["statistici"]["pasi_optimizator"] == PASI and r["optimizator"] == "MuonCuAdamW"
        assert r["sha256_stare_inainte"] == r["sha256_stare_dupa"] == sha  # starea de pornire e doar citită
        assert r["continuat"] is True and r["pasi_total_la_pornire"] == 100
        assert r["straturi_cu_recalcul"] == 2 and sum(r["randuri"].values()) == PASI * ADUNARE * 4
        assert r["randuri"]["conversatie"] > 0 and r["randuri"]["text"] > 0
        assert r["date_modul"].endswith("DateBucati") == (nume == "B")
        assert ("date_pe_bucati" in r["statistici"]) == (nume == "B")
        assert sorted(g["muon"] for g in r["grupuri"]) == [False, True, True]
        assert max(g["rata"] for g in r["grupuri"] if g["muon"]) == pytest.approx(0.0001)
    from module.model_muon import ModelGPTConversatieMuon

    assert not getattr(ModelGPTConversatieMuon._pregateste_reteaua, "_cu_recalcul", False)  # recalculul a fost scos
    with pytest.raises(FileExistsError):
        pp.tot(mic["vechi"], mic["bucati"], dosar, pasi_optimizare=PASI, in_proces=True, in_plus=_in_plus())


def test_proba_mica_vede_date_diferite(mic, tmp_path, monkeypatch):  # noqa: F811
    """Dacă textul vechi nu e cel din care s-au făcut bucățile: NU, cu primul lot diferit; comanda iese cu cod 1."""
    (mic["dosar"] / "antrenare.txt").write_bytes(TEXT.replace("garden", "forest").encode("utf-8"))
    dosar = tmp_path / "proba_nu"
    adevarata = pp.tot
    monkeypatch.setattr(pp, "tot", lambda *a: adevarata(*a[:5], _in_plus(), *a[6:]))
    assert pp.main(["tot", "--config-vechi", str(mic["vechi"]), "--config-bucati", str(mic["bucati"]), "--iesire",
                    str(dosar), "--pasi-optimizare", "6", "--in-proces"]) == 1
    rez = json.loads((dosar / "s104.json").read_text(encoding="utf-8"))
    assert rez["verdict"] == "NU" and not rez["V1_fata_de_B"]["loturi_identice"]
    assert rez["V1_fata_de_B"]["primul_lot_diferit"] is not None
    assert rez["V1_fata_de_B"]["primul_pas_de_optimizare_cu_lot_diferit"] is not None
    assert rez["V1_fata_de_V2"]["loturi_identice"] and rez["V1_fata_de_V2"]["pe_pasi"]["identice"]


def test_proba_cere_cele_doua_feluri_de_date(mic, tmp_path):  # noqa: F811
    with pytest.raises(ValueError, match="portul date nu e"):
        pp.tot(mic["vechi"], mic["vechi"], tmp_path / "x", in_proces=True)
    with pytest.raises(ValueError, match="cel vechi"):
        pp.tot(mic["bucati"], mic["bucati"], tmp_path / "y", in_proces=True)


def _comp(maxima, loturi_identice=True):
    return {"loturi_identice": loturi_identice, "pe_pasi": {"maxima": maxima}, "pe_loturi": {"maxima": maxima}}


@pytest.mark.parametrize("b_v1, v2_v1, loturi, asteptat", [
    (0.0, 0.0, True, "DA"),          # totul identic
    (1e-5, 0.0, True, "DA"),         # la pragul minim
    (1.1e-5, 0.0, True, "NU"),       # placa se repetă, B nu
    (0.0019, 0.001, True, "DA"),     # sub de două ori zgomotul plăcii
    (0.0021, 0.001, True, "NU"),     # peste de două ori zgomotul plăcii
    (0.0, 0.0, False, "NU"),         # loturi diferite, orice ar fi pierderile
], ids=["identic", "prag_minim", "peste_prag_minim", "sub_2x", "peste_2x", "loturi_diferite"])
def test_verdictul_dupa_pragurile_sarcinii(b_v1, v2_v1, loturi, asteptat):
    v = pp.verdict(_comp(b_v1, loturi), _comp(v2_v1))
    assert v["verdict"] == asteptat and v["prag"] == max(2 * v2_v1, 1e-5)


def test_pierderea_pe_pasi_si_diferenta_maxima():
    assert pp.pe_pasi([1.0, 3.0, 2.0, 4.0, 9.0], 2) == [2.0, 3.0]  # lotul rămas la sfârșit nu face un pas
    d = pp._dif_max([1.0, 2.0, 3.0], [1.0, 2.5, 3.25])
    assert d == {"comparate": 3, "maxima": 0.5, "la": 2, "primul_diferit": 2, "identice": False}
    assert pp._dif_max([1.0], [1.0])["identice"] and not pp._dif_max([], [])["identice"]


def test_paza_opreste_rularea(tmp_path):
    """Peste pragul de memorie (sau la temperatura-limită), procesul rulării e oprit și se ridică PazaPlacii."""
    config = tmp_path / "doarme.toml"
    config.write_text("", encoding="utf-8")
    porniri = []
    adevarat = subprocess.Popen

    def doarme(comanda, **k):  # în locul rulării adevărate: un proces care doar așteaptă
        porniri.append(adevarat([sys.executable, "-c", "import time; time.sleep(120)"]))
        return porniri[-1]

    pp.subprocess.Popen = doarme
    try:
        for citire, text in (((6701, 60), "6701 MB"), ((5000, 83), "83 °C")):
            with pytest.raises(pp.PazaPlacii, match=text):
                pp._in_proces_nou("V1", config, 1, tmp_path, 6700, 83, citeste=lambda c=citire: c, pauza=0.05)
            assert porniri[-1].poll() is not None  # procesul a fost oprit
    finally:
        pp.subprocess.Popen = adevarat
        for p in porniri:
            if p.poll() is None:
                p.kill()
    randuri = [json.loads(r) for r in (tmp_path / "smi.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["mb"] for r in randuri] == [6701, 5000] and randuri[0]["rulare"] == "V1"


def test_tot_scrie_nemasurat_cand_paza_opreste(mic, tmp_path, monkeypatch):  # noqa: F811
    def paza(*a, **k):
        raise pp.PazaPlacii("rularea V1: placa la 6900 MB")

    monkeypatch.setattr(pp, "_in_proces_nou", paza)
    monkeypatch.setattr(pp, "nvidia_smi", lambda: (400, 30))
    dosar = tmp_path / "oprit"
    assert pp.main(["tot", "--config-vechi", str(mic["vechi"]), "--config-bucati", str(mic["bucati"]), "--iesire",
                    str(dosar)]) == pp.COD_PAZA
    rez = json.loads((dosar / "s104.json").read_text(encoding="utf-8"))
    assert rez["verdict"] == "NEMĂSURAT" and "6900 MB" in rez["oprit"] and rez["rulari_terminate"] == []


def test_nu_porneste_cu_placa_ocupata(mic, tmp_path, monkeypatch):  # noqa: F811
    monkeypatch.setattr(pp, "nvidia_smi", lambda: (900, 30))
    with pytest.raises(SystemExit, match="placa nu e goală"):
        pp.tot(mic["vechi"], mic["bucati"], tmp_path / "ocupata")
    assert not (tmp_path / "ocupata").exists()


def test_felurile_randurilor_umplu_lotul():
    class _M:
        lot, fractie_conversatie, hrana = 4, 0.45, "x"

        def bucati_din_hrana(self, pas):
            return 1 if pas % 5 == 0 else 0

    for pas in range(231488, 231488 + 50):
        feluri = pp.feluri_de_randuri(_M(), pas)
        assert len(feluri) == 4 and feluri == sorted(feluri, key=["conversatie", "hrana", "text"].index)
    assert sum(pp.feluri_de_randuri(_M(), p).count("conversatie") for p in range(100)) == 180  # 0,45 × 4 × 100


# --- cele două configurări de probă din config/ ---------------------------------------------------------------------


def _config(nume):
    return tomllib.loads((RADACINA / "config" / nume).read_text(encoding="utf-8"))


def test_configurarea_veche_e_24n_cu_doar_numele_starea_si_eticheta():
    n, v = _config("conv_w2_mare_24n.toml"), _config("proba_placa_vechi.toml")
    assert v["platforma"]["nume"] == "proba_placa_vechi"
    assert v["porturi"]["model"]["setari"]["cale_stare"] == "lucru/proba_placa/vechi/gpt.pt"
    assert v["antrenare_lunga"]["eticheta"] != n["antrenare_lunga"]["eticheta"]
    v["platforma"]["nume"] = n["platforma"]["nume"]
    v["porturi"]["model"]["setari"]["cale_stare"] = n["porturi"]["model"]["setari"]["cale_stare"]
    v["antrenare_lunga"]["eticheta"] = n["antrenare_lunga"]["eticheta"]
    assert v == n


def test_configurarea_pe_bucati_e_cea_veche_cu_doar_portul_date():
    v, b, s98 = (_config(c) for c in ("proba_placa_vechi.toml", "proba_placa_bucati.toml", "conv_w2_mare_24_bucati.toml"))
    assert b["platforma"]["nume"] == "proba_placa_bucati"
    assert b["porturi"]["model"]["setari"]["cale_stare"] == "lucru/proba_placa/bucati/gpt.pt"
    assert b["porturi"]["date"] == s98["porturi"]["date"]
    assert b["porturi"]["date"]["modul"] == "module.date_bucati:DateBucati"
    b["platforma"]["nume"] = v["platforma"]["nume"]
    b["porturi"]["model"]["setari"]["cale_stare"] = v["porturi"]["model"]["setari"]["cale_stare"]
    b["antrenare_lunga"]["eticheta"] = v["antrenare_lunga"]["eticheta"]
    b["porturi"]["date"] = v["porturi"]["date"]
    assert b == v


def test_unealta_nu_salveaza_si_nu_atinge_kronos():
    sursa = (RADACINA / "unelte" / "proba_placa.py").read_text(encoding="utf-8")
    cod = sursa.split('"""', 2)[2]  # fără textul explicativ de la început
    for interzis in ("dupa_examen(", "salveaza_atomic", "Jurnal", "torch.save", "_salveaza_starea("):
        assert interzis not in cod, interzis
    assert antrenare_recalcul.PRAG_PAZA_MB == 6700  # aceeași pază ca la antrenările liniei de 24
