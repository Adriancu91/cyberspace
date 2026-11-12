"""S103 (C-110): legarea datelor pe bucăți în antrenare. Dacă portul „date” are `sir_antrenare()`, modelele GPT iau
simbolurile de acolo (fără textul brut) și scriu amprenta datelor în statistici; altfel merg exact ca până acum. Proba
mică: aceiași pași cu datele vechi (text) și cu bucățile dau aceleași loturi, aceleași pierderi și aceleași greutăți."""

import hashlib
import importlib
import json
import tomllib
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from module.date_bucati import DateBucati  # noqa: E402
from teste.bucati_mici import TEXT, VALIDARE, scrie_bucati  # noqa: E402
from unelte import proba_legare as pl  # noqa: E402

RADACINA = Path(__file__).resolve().parents[1]
CTX = 16
PASI = 48  # 2 pași de optimizator la felul „muon24” (gradientul adunat pe 24 de loturi)


def _t(cale):
    return str(cale).replace("\\", "/")


@pytest.fixture
def mic(tmp_path):
    """Setul mic pe bucăți, același text într-un fișier (calea veche), hrana, conversația și cele două configurări."""
    setari = scrie_bucati(tmp_path, marime=10)
    (tmp_path / "antrenare.txt").write_bytes(TEXT.encode("utf-8"))
    (tmp_path / "hrana.txt").write_bytes(("birds have feathers and the old dog sat in the garden.\n" * 30).encode("utf-8"))
    (tmp_path / "conv.jsonl").write_text("\n".join(
        json.dumps({"intrebare": f"what did the cat do {i}?", "raspuns": "the cat sat on the mat."}) for i in range(12)),
        encoding="utf-8")
    model = ('[porturi.model]\nmodul = "module.model_muon:ModelGPTConversatieMuon"\n'
             f'setari = {{ tokenizer = "bpe", cale_tokenizer = "{_t(setari["cale_tokenizer"])}", samanta = 0, '
             f'hrana = "{_t(tmp_path / "hrana.txt")}", fractie_hrana = 0.05, '
             f'conversatie = "{_t(tmp_path / "conv.jsonl")}", fractie_conversatie = 0.45 }}\n')
    vechi = tmp_path / "vechi.toml"
    vechi.write_text(model + '[porturi.date]\nmodul = "module.date_amestec:DateAmestec"\n'
                     f'setari = {{ cale_antrenare = "{_t(tmp_path / "antrenare.txt")}", '
                     f'cale_validare = "{_t(setari["cale_validare"])}" }}\n', encoding="utf-8")
    bucati = tmp_path / "bucati.toml"
    bucati.write_text(model + '[porturi.date]\nmodul = "module.date_bucati:DateBucati"\n'
                      f'setari = {{ director = "{_t(setari["director"])}", cale_validare = "{_t(setari["cale_validare"])}", '
                      f'cale_tokenizer = "{_t(setari["cale_tokenizer"])}" }}\n', encoding="utf-8")
    return {"setari": setari, "vechi": vechi, "bucati": bucati, "dosar": tmp_path}


def _model(mic, clasa="conversatie", **in_plus):
    from module.model_continuu import ModelGPTContinuu
    from module.model_conversatie import ModelGPTConversatie

    d = mic["dosar"]
    comune = dict(n_straturi=1, n_capete=2, n_emb=32, context=CTX, lot=4, dispozitiv="cpu", tokenizer="bpe",
                  cale_tokenizer=mic["setari"]["cale_tokenizer"], rata_invatare=1e-3, pasi_max=10,
                  hrana=str(d / "hrana.txt"), fractie_hrana=0.05) | in_plus
    if clasa == "conversatie":
        return ModelGPTConversatie(conversatie=str(d / "conv.jsonl"), fractie_conversatie=0.45, **comune)
    return ModelGPTContinuu(**comune)


class _DateText:
    def text_antrenare(self):
        return TEXT

    def text_validare(self):
        return VALIDARE


# --- legarea ----------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("clasa", ["conversatie", "simplu"])
def test_legarea_ia_sirul_si_scrie_amprenta(mic, clasa):
    date = DateBucati(**mic["setari"])  # fără previzualizare: text_antrenare() ar refuza
    s = _model(mic, clasa).antreneaza(date, 60.0)
    assert s["pasi"] == 10 and s["simboluri_antrenare"] == date.numar_simboluri()
    index = date.index
    assert s["date_pe_bucati"] == {
        "amprenta": date.amprenta(), "sha256_sir": index["sha256_tot"], "sha256_tokenizer": index["tokenizer"]["sha256"],
        "simboluri": date.numar_simboluri(), "bucati": len(index["bucati"])}
    assert s["date_pe_bucati"]["sha256_tokenizer"] == hashlib.sha256(
        Path(mic["setari"]["cale_tokenizer"]).read_bytes()).hexdigest()
    json.dumps(s)  # statisticile intră în jurnal: doar lucruri care se pot scrie în JSON


@pytest.mark.parametrize("clasa", ["conversatie", "simplu"])
def test_calea_veche_ramane_cum_era(mic, clasa):
    """Cu date pe text: nimic în plus în statistici, iar simbolurile se țin minte sub aceeași amprentă ca înainte
    (SHA-1 al textului + al tokenizerului, primele 16 semne)."""
    cache = mic["dosar"] / "cache"
    s = _model(mic, clasa, director_cache=str(cache)).antreneaza(_DateText(), 60.0)
    assert s["pasi"] == 10 and "date_pe_bucati" not in s
    amprenta = hashlib.sha1(TEXT.encode("utf-8") + Path(mic["setari"]["cale_tokenizer"]).read_bytes()).hexdigest()[:16]
    assert (cache / f"simboluri_{amprenta}.pt").exists()
    de_baza = {"pasi", "pierdere_finala", "parametri", "dispozitiv", "secunde_bucla", "tokenizer", "simboluri_antrenare",
               "pasi_total", "minute_total", "continuat", "pornit_din"}
    assert de_baza <= set(s) and set(s) - de_baza <= {
        "perechi_conversatie", "ferestre", "rata_la_final", "pasi_max", "secvente_hrana", "secvente_total",
        "simboluri_hrana", "scor_la_pornire"}


def test_legarea_refuza_ce_nu_se_potriveste(mic, tmp_path):
    from module.model_gpt import ModelGPT
    from module.tokenizer_bpe import antreneaza_bpe

    date = DateBucati(**mic["setari"])
    comune = dict(n_straturi=1, n_capete=2, n_emb=32, context=CTX, lot=4, dispozitiv="cpu", pasi_max=2)
    # GPT-ul simplu ține tot textul pe dispozitiv: cu bucățile n-are rost, refuză
    with pytest.raises(ValueError, match="în RAM"):
        ModelGPT(tokenizer="bpe", cale_tokenizer=mic["setari"]["cale_tokenizer"], **comune).antreneaza(date, 5.0)
    with pytest.raises(ValueError, match="bpe"):
        ModelGPT(**comune).antreneaza(date, 5.0)  # pe litere
    alt = tmp_path / "alt_bpe.json"
    antreneaza_bpe(TEXT, 300).salveaza(alt)
    for clasa in ("conversatie", "simplu"):
        with pytest.raises(ValueError, match="alt tokenizer"):
            _model(mic, clasa, cale_tokenizer=str(alt)).antreneaza(date, 5.0)


def test_un_model_fara_legare_tot_refuza(mic):
    """Comportamentul din S98 rămâne: cine cere textul întreg de la datele pe bucăți e refuzat."""
    from module.model_ngram import ModelNgram

    with pytest.raises(RuntimeError, match="nu text"):
        ModelNgram(ordin=2).antreneaza(DateBucati(**mic["setari"]), 1.0)


def test_configurarile_in_uz_raman_pe_calea_veche():
    """Doar configurarea de probă are un port `date` cu `sir_antrenare()`; toate celelalte iau textul, ca până acum."""
    cu_sir = set()
    for cale in sorted((RADACINA / "config").rglob("*.toml")):
        date = tomllib.loads(cale.read_text(encoding="utf-8")).get("porturi", {}).get("date")
        if not date:
            continue
        modul, clasa = date["modul"].split(":")
        if hasattr(getattr(importlib.import_module(modul), clasa), "sir_antrenare"):
            cu_sir.add(cale.name)
    assert cu_sir == {"conv_w2_mare_24_bucati.toml"}
    for nume in ("conv_w2_mare_24r.toml", "conv_w2_mare_24n.toml", "conv_w2.toml"):
        c = tomllib.loads((RADACINA / "config" / nume).read_text(encoding="utf-8"))
        assert c["porturi"]["date"]["modul"] == "module.date_amestec:DateAmestec"


# --- proba mică: aceiași pași cu datele vechi și cu bucățile -------------------------------------------------------


def test_proba_mica_a_egal_b(mic, tmp_path):
    determinist, fire = torch.are_deterministic_algorithms_enabled(), torch.get_num_threads()
    dosar = tmp_path / "proba"
    rez = pl.tot(mic["vechi"], mic["bucati"], dosar, pasi=PASI, context=CTX, in_proces=True)
    assert (determinist, fire) == (torch.are_deterministic_algorithms_enabled(), torch.get_num_threads())
    assert rez == json.loads((dosar / "s103.json").read_text(encoding="utf-8"))
    assert rez["verdict"] == "DA" and rez["procesorul_se_repeta"] and rez["toate_identice"]
    assert set(rez["feluri"]) == set(pl.FELURI) and rez["doar_citite_neschimbate"] == {"bucati": True}
    for fel, f in rez["feluri"].items():
        ab = f["A1_fata_de_B"]
        assert ab["identic"] and ab["pierderi_identice"] and ab["loturi_identice"] and ab["greutati_identice"], fel
        assert ab["primul_pas_cu_pierdere_diferita"] is None and ab["diferenta_maxima"] == 0.0
        a, b = (json.loads((dosar / f"{fel}_{n}.json").read_text(encoding="utf-8")) for n in ("A1", "B"))
        assert a["pasi"] == b["pasi"] == PASI and a["pierderi_hex"] == b["pierderi_hex"]
        assert a["date_modul"].endswith("DateAmestec") and "date_pe_bucati" not in a["statistici"]
        assert b["date_modul"].endswith("DateBucati")
        assert b["statistici"]["date_pe_bucati"]["amprenta"] == DateBucati(**mic["setari"]).amprenta()
        assert a["pierderi"][-1] < a["pierderi"][0]  # modelul chiar învață în pașii de probă
        assert f["tabel"]["1"]["A1"] == f["tabel"]["1"]["B"] and str(PASI) in f["tabel"]
    conv = rez["feluri"]["conversatie"]["ferestre"]
    assert conv["conversatie"] > 0 and conv["hrana"] > 0 and conv["text"] > 0 and sum(conv.values()) == PASI * 4
    assert rez["feluri"]["simplu"]["ferestre"]["conversatie"] == 0
    assert rez["feluri"]["muon24"]["rulari"]["B"]["statistici"]["pasi_optimizator"] == PASI // 24
    with pytest.raises(FileExistsError):
        pl.tot(mic["vechi"], mic["bucati"], dosar, pasi=PASI, context=CTX, in_proces=True)


def test_proba_mica_vede_date_diferite(mic, tmp_path):
    """Dacă textul vechi nu e cel din care s-au făcut bucățile, verdictul e NU: primul pas diferit și felul ferestrei."""
    (mic["dosar"] / "antrenare.txt").write_bytes(TEXT.replace("garden", "forest").encode("utf-8"))
    dosar = tmp_path / "proba_nu"
    assert pl.main(["tot", "--config-vechi", str(mic["vechi"]), "--config-bucati", str(mic["bucati"]), "--iesire",
                    str(dosar), "--pasi", "30", "--context", str(CTX), "--feluri", "conversatie", "--in-proces"]) == 1
    rez = json.loads((dosar / "s103.json").read_text(encoding="utf-8"))
    ab = rez["feluri"]["conversatie"]["A1_fata_de_B"]
    assert rez["verdict"] == "NU" and rez["procesorul_se_repeta"] and not ab["identic"]
    assert ab["primul_pas_cu_lot_diferit"] is not None and ab["randuri_diferite"]
    assert {r["fel"] for r in ab["randuri_diferite"]} == {"text"}
    assert ab["primul_pas_cu_pierdere_diferita"] >= ab["primul_pas_cu_lot_diferit"]


def test_proba_cere_cele_doua_feluri_de_date(mic, tmp_path):
    with pytest.raises(ValueError, match="portul date nu e"):
        pl.tot(mic["vechi"], mic["vechi"], tmp_path / "x", in_proces=True)
    with pytest.raises(ValueError, match="cel vechi"):
        pl.tot(mic["bucati"], mic["bucati"], tmp_path / "y", in_proces=True)
