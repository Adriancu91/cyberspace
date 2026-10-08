"""După prima buclă: rata care scade singură (față de rata fixă), bucla cinstită în două faze și antrenarea lungă."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from teste.tinystories_mic import scrie_surse
from unelte import antrenare_lunga, bucla_pe_faze, compara_scaderea_ratei

CONFIG = """
[platforma]
nume = "{nume}"
director_lucru = "lucru"
buget_antrenare_secunde = {buget}
experimente = 10
prag_zgomot = 0.005

[paznic]
timp_max_secunde = 120
timp_test_secunde = 60
porturi_modificabile = ["model"]

# hrana = "": fără hrană (din 8 octombrie 2026 unealta de antrenare lungă o pune implicit, iar aici nu există)
[porturi.model]
modul = "module.model_continuu:ModelGPTContinuu"
setari = {{ n_straturi = 1, n_capete = 2, n_emb = 32, context = 16, lot = 4, rata_invatare = 0.002, dispozitiv = "cpu", tokenizer = "bpe", cale_tokenizer = "{tokenizer}", rata_care_scade = true, incalzire_pasi = 2, director_cache = "lucru/cache", samanta = 0, hrana = ""{model} }}

[porturi.date]
modul = "module.date_tinystories:DateTinyStories"
setari = {{ director = "{director}", megaocteti = 0.004, procent_validare = 0.25, url_antrenare = "{url_antrenare}", url_validare = "{url_validare}" }}

[porturi.examen]
modul = "module.examen_bpb:ExamenBpb"

[porturi.cercetator]
modul = "module.cercetator_local:CercetatorLocal"
setari = {{ amesteca = false, strangere = false, spatiu = {{ model = {{ {spatiu} }} }} }}

[porturi.profesor]
modul = "module.jucarii:ProfesorGol"

[porturi.rulare]
modul = "module.rulare_locala:RulareLocala"

[porturi.stocare]
modul = "module.stocare_disc:StocareDisc"
setari = {{ director = "lucru/stocare" }}

[porturi.interfata]
modul = "module.interfata_consola:InterfataConsola"
setari = {{ tacut = true }}

[porturi.traducere]
modul = "module.jucarii:TraducereIdentitate"

[porturi.memorie]
modul = "module.jucarii:MemorieGoala"
"""


def config_mic(tmp_path: Path, nume: str, buget: float = 0.3, model: str = "", spatiu: str = "n_straturi = [2]") -> Path:
    """O configurare minusculă (pe procesor, câteva zecimi de secundă de antrenare), cu datele și tokenizerul ei."""
    from module.tokenizer_bpe import antreneaza_bpe

    surse = scrie_surse(tmp_path)
    tokenizer = tmp_path / "bpe.json"
    if not tokenizer.exists():
        antreneaza_bpe((tmp_path / "train.txt").read_text(encoding="utf-8"), 300).salveaza(tokenizer)
    cale = tmp_path / f"{nume}.toml"
    cale.write_text(CONFIG.format(
        nume=nume, buget=buget, tokenizer=tokenizer.as_posix(), model=model, spatiu=spatiu,
        director=Path(surse["director"]).as_posix(), url_antrenare=surse["url_antrenare"], url_validare=surse["url_validare"],
    ), encoding="utf-8")
    return cale


def fise(tmp_path: Path) -> list[dict]:
    jurnal = tmp_path / "lucru" / "jurnal" / "experimente.jsonl"
    return [json.loads(r) for r in jurnal.read_text(encoding="utf-8").splitlines() if r.strip()]


# --- pasul 1: rata care scade, față de rata fixă --------------------------------------------------------


def test_scaderea_ratei_aceeasi_reteta_de_la_zero(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "bucla_arhitecturi", model=', director_stari = "lucru/arhitecturi", de_la_zero = true')
    argumente = ["--config", str(cale), "--seminte", "1", "--minute", "0.01", "--pauza", "0", "--racire", "0"]
    assert compara_scaderea_ratei.main(argumente) == 0

    rezultat = json.loads(next((tmp_path / "lucru").glob("scaderea_ratei_*.json")).read_text(encoding="utf-8"))
    rand = rezultat["randuri"][0]
    assert rand["samanta"] == 1 and rand["fara"]["rata_la_final"] is None
    assert 0 < rand["cu"]["rata_la_final"] < 0.002  # a scăzut față de rata de pornire
    assert not (tmp_path / "lucru" / "arhitecturi").exists()  # n-a scris nicio stare: nu atinge stările buclei
    toate = fise(tmp_path)
    assert len(toate) == 2 and len({f["linie"] for f in toate}) == 1
    assert [f["setari"]["model"]["rata_care_scade"] for f in toate] == [False, True]
    assert all(not f["statistici_antrenare"]["continuat"] and f["setari"]["model"]["samanta"] == 1 for f in toate)
    assert "Verdict:" in capsys.readouterr().out

    # Cu --fara-din și --rata-cu: rata fixă se ia din rezultatul de mai sus, se rulează doar varianta cu scădere.
    primul = next((tmp_path / "lucru").glob("scaderea_ratei_*.json"))
    assert compara_scaderea_ratei.main(argumente + ["--fara-din", str(primul), "--rata-cu", "0.004"]) == 0
    assert len(fise(tmp_path)) == 3 and fise(tmp_path)[-1]["setari"]["model"]["rata_invatare"] == 0.004
    al_doilea = max((tmp_path / "lucru").glob("scaderea_ratei_*.json"), key=lambda p: p.stat().st_mtime)
    rezultat_2 = json.loads(al_doilea.read_text(encoding="utf-8"))
    assert rezultat_2["randuri"][0]["fara"] == rand["fara"] and rezultat_2["rata_cu"] == 0.004
    assert compara_scaderea_ratei.main(argumente[:-6] + ["--minute", "0.02", "--pauza", "0", "--racire", "0",
                                                         "--fara-din", str(primul)]) == 1  # alt timp: nu e cinstit
    # Cu --rata și --cu-din: aceeași rețetă la rata 0,004; varianta cu scădere se ia din rezultatul al doilea.
    assert compara_scaderea_ratei.main(argumente + ["--cu-din", str(al_doilea), "--rata", "0.004"]) == 0
    ultima = fise(tmp_path)[-1]["setari"]["model"]
    assert len(fise(tmp_path)) == 4 and ultima["rata_invatare"] == 0.004 and not ultima["rata_care_scade"]
    assert compara_scaderea_ratei.main(argumente + ["--cu-din", str(al_doilea)]) == 1  # altă rată: nu e cinstit


def _rand(samanta, fara, cu):
    return {"samanta": samanta, "fara": {"scor": fara}, "cu": {"scor": cu}}


@pytest.mark.parametrize(
    "randuri,inceput",
    [
        ([_rand(0, 1.0, 0.98), _rand(1, 1.0, 0.97)], "AJUTĂ"),
        ([_rand(0, 1.0, 1.02), _rand(1, 1.0, 1.03)], "STRICĂ"),
        ([_rand(0, 1.0, 1.002), _rand(1, 1.0, 0.999)], "NU CONTEAZĂ"),
        ([_rand(0, 1.0, 0.98), _rand(1, 1.0, 1.04)], "NECONCLUDENT"),
    ],
)
def test_verdictul_scaderii(randuri, inceput):
    assert compara_scaderea_ratei.verdict(randuri, 0.005).startswith(inceput)


# --- pasul 2: bucla cinstită, în două faze -----------------------------------------------------------------


def test_bucla_pe_faze_nu_amesteca_cele_doua_feluri(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    a = config_mic(tmp_path, "arhitecturi", model=', director_stari = "lucru/arhitecturi", de_la_zero = true')
    b = config_mic(tmp_path, "lot_rata", model=', stare_de_pornire = "lucru/lipsa.pt"', spatiu="rata_invatare = [0.001], lot = [8]")
    assert bucla_pe_faze.main(["--config-arhitecturi", str(a), "--config-lot-rata", str(b), "--minute", "2"]) == 0

    toate = fise(tmp_path)
    faza1 = [f for f in toate if f["linie"] == "arhitecturi"]
    assert sorted(f["setari"]["model"]["n_straturi"] for f in faza1) == [1, 2]  # reperul și lista
    assert all(not f["statistici_antrenare"]["continuat"] for f in faza1)  # arhitecturile: doar de la zero
    castigator = min((f for f in faza1 if f["decizie"] == "pastrat"), key=lambda f: f["scoruri"]["val_bpb"])
    pornire = tmp_path / "lucru" / "bucla_cinstita" / "stari_de_pornire" / f"din_{castigator['id']}.pt"
    assert pornire.read_bytes() == Path(castigator["dupa_examen"]["continuare"]["fisier"]).read_bytes()
    faza2 = [f for f in toate if f["linie"] == f"lot_rata_din_{castigator['id']}"]
    assert len(faza2) == 3 and len(toate) == 5  # faza 2 pe linia ei: nu se amestecă în deciziile fazei 1
    for f in faza2:  # lotul și rata: toate din aceeași stare, nu una din alta
        s = f["statistici_antrenare"]
        assert s["continuat"] and s["pornit_din"] == str(pornire)
        assert s["pasi_total"] == castigator["statistici_antrenare"]["pasi_total"] + s["pasi"]
        assert f["setari"]["model"]["n_straturi"] == castigator["setari"]["model"]["n_straturi"]
    modele = [f["setari"]["model"] for f in faza2]
    assert (modele[0]["rata_invatare"], modele[0]["lot"]) == (0.002, 4)  # reperul: rețeta câștigătoare neschimbată
    assert (modele[1]["rata_invatare"], modele[1]["lot"]) == (0.001, 4) and modele[2]["lot"] == 8
    rezultat = json.loads(next((tmp_path / "lucru" / "bucla_cinstita").glob("rezultat_*.json")).read_text(encoding="utf-8"))
    assert rezultat["castigator_1"] == castigator["id"] and len(rezultat["faza1"]) == 2 and len(rezultat["faza2"]) == 3
    assert "Câștigă:" in capsys.readouterr().out


# --- pasul 3: antrenarea lungă --------------------------------------------------------------------------


def test_antrenarea_lunga_continua_ora_cu_ora_si_se_reia(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "antrenare_lunga", model=', cale_stare = "lucru/antrenare_lunga/gpt.pt", '
                      'durata_scaderii_secunde = 0.6', spatiu="lot = [4]")
    argumente = ["--config", str(cale), "--pauza", "0", "--racire", "0", "--lungime", "40"]
    assert antrenare_lunga.main(argumente + ["--ore", "1"]) == 0
    assert antrenare_lunga.main(argumente + ["--ore", "2"]) == 0  # se reia: face doar ora a doua

    rezultat = json.loads((tmp_path / "lucru" / "antrenare_lunga" / "rezultat.json").read_text(encoding="utf-8"))
    ore = rezultat["ore"]
    assert [o["ora"] for o in ore] == [1, 2]
    assert ore[1]["pasi_total"] == ore[0]["pasi_total"] + ore[1]["pasi"]  # ora 2 a continuat din starea orei 1
    assert ore[1]["simboluri_total"] == ore[0]["simboluri"] + ore[1]["simboluri"]
    assert ore[1]["rata_la_final"] < ore[0]["rata_la_final"]  # o singură scădere, pe toate orele
    assert rezultat["poveste"]["text"].startswith("Once upon a time")
    assert antrenare_lunga.main(argumente + ["--ore", "2"]) == 0  # nimic de făcut: doar raportul
    assert len(fise(tmp_path)) == 2
    assert "Povestea modelului" in capsys.readouterr().out


def test_antrenarea_lunga_porneste_din_modelul_altui_experiment(tmp_path, monkeypatch, capsys):
    torch = pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    prima = config_mic(tmp_path, "antrenare_lunga", model=', cale_stare = "lucru/antrenare_lunga/gpt.pt"', spatiu="lot = [4]")
    comun = ["--pauza", "0", "--racire", "0", "--lungime", "40"]
    assert antrenare_lunga.main(["--config", str(prima), "--ore", "2"] + comun) == 0
    sursa = [f for f in fise(tmp_path) if f["linie"] == "antrenare_lunga" and f.get("model_salvat")][0]

    # Starea de pornire: greutățile modelului salvat, optimizator nou, numărătoarea de la zero.
    config = antrenare_lunga.citeste_config(str(prima))
    stare, inainte = antrenare_lunga.stare_de_pornire(config, antrenare_lunga.Jurnal(config.director_lucru), sursa["id"], "val_bpb")
    salvat = torch.load(sursa["model_salvat"], map_location="cpu", weights_only=True)["stare"]
    assert all(torch.equal(stare["retea"][k].cpu(), salvat[k].cpu()) for k in salvat)
    assert stare["pasi_total"] == 0 and stare["minute"] == 0.0 and stare["optimizator"]["state"] == {}
    assert inainte["ore"] == 1 and inainte["pasi"] == sursa["statistici_antrenare"]["pasi_total"]
    assert inainte["simboluri"] == sursa["statistici_antrenare"]["pasi"] * 4 * 16  # lot 4, context 16

    a_doua = config_mic(tmp_path, "antrenare_lunga_2", model=', cale_stare = "lucru/antrenare_lunga_2/gpt.pt", '
                        'durata_scaderii_secunde = 0.6', spatiu="lot = [4]")
    argumente = ["--config", str(a_doua), "--ore", "1", "--porneste-din", str(sursa["id"]), "--compara-cu", str(sursa["id"]),
                 "--inceput", "Once upon a time, there was"] + comun
    assert antrenare_lunga.main(argumente) == 0
    ora = [f for f in fise(tmp_path) if f["linie"] == "antrenare_lunga_2"][0]["statistici_antrenare"]
    assert ora["continuat"] and ora["pasi_total"] == ora["pasi"]  # din starea de pornire, cu numărătoarea de la zero
    rezultat = json.loads((tmp_path / "lucru" / "antrenare_lunga_2" / "rezultat.json").read_text(encoding="utf-8"))
    assert rezultat["inainte"]["experiment"] == sursa["id"]
    assert rezultat["total"]["pasi"] == inainte["pasi"] + ora["pasi"]
    assert rezultat["total"]["simboluri"] == inainte["simboluri"] + ora["pasi"] * 4 * 16
    assert rezultat["poveste"]["text"].startswith("Once upon a time, there was")
    assert rezultat["poveste_comparatie"]["experiment"] == sursa["id"]
    assert rezultat["poveste_comparatie"]["text"].startswith("Once upon a time, there was")
    assert "Cu cele 1 ore de dinainte" in capsys.readouterr().out
    assert antrenare_lunga.main(argumente) == 0  # reluat: starea nu se mai face din nou, ora e deja făcută
    assert len([f for f in fise(tmp_path) if f["linie"] == "antrenare_lunga_2"]) == 1


def test_povestea_vine_din_starea_de_la_final(tmp_path, monkeypatch):
    torch = pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "antrenare_lunga", model=', cale_stare = "lucru/antrenare_lunga/gpt.pt"', spatiu="lot = [4]")
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "1", "--pauza", "0", "--racire", "0", "--lungime", "40"]) == 0
    config, fisa = antrenare_lunga.citeste_config(str(cale)), fise(tmp_path)[0]
    stare = tmp_path / "lucru" / "antrenare_lunga" / "gpt.pt"
    # După o oră păstrată, starea și modelul salvat de Kronos au aceleași greutăți: exact aceeași poveste.
    salvata = antrenare_lunga.poveste(config, fisa, "Once upon a time", 40)
    assert antrenare_lunga.poveste_din_stare(config, fisa, stare, "Once upon a time", 40) == salvata
    # Alte greutăți în stare (ca după o oră pe care Kronos n-a salvat-o separat): povestea o scriu ele.
    s = torch.load(stare, weights_only=True)
    s["retea"] = {k: v * 0 for k, v in s["retea"].items()}
    torch.save(s, stare)
    assert antrenare_lunga.poveste_din_stare(config, fisa, stare, "Once upon a time", 40) != salvata


def test_antrenarea_lunga_alaturi_de_alta_antrenare(tmp_path, monkeypatch, capsys):
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    comun = ["--pauza", "0", "--racire", "0", "--lungime", "40"]
    prima = config_mic(tmp_path, "antrenare_lunga", model=', cale_stare = "lucru/antrenare_lunga/gpt.pt"', spatiu="lot = [4]")
    assert antrenare_lunga.main(["--config", str(prima), "--ore", "2"] + comun) == 0
    a_treia = config_mic(tmp_path, "antrenare_lunga_3", model=', cale_stare = "lucru/antrenare_lunga_3/gpt.pt"',
                         spatiu="lot = [4]")
    capsys.readouterr()
    assert antrenare_lunga.main(["--config", str(a_treia), "--ore", "1", "--alaturi-de", "antrenare_lunga"] + comun) == 0
    iesire = capsys.readouterr().out
    rezultat = json.loads((tmp_path / "lucru" / "antrenare_lunga_3" / "rezultat.json").read_text(encoding="utf-8"))
    prima_ora = [f for f in fise(tmp_path) if f["linie"] == "antrenare_lunga"][0]["scoruri"]["val_bpb"]
    assert rezultat["alaturi"]["scoruri"]["1"] == prima_ora and len(rezultat["alaturi"]["scoruri"]) == 2
    assert "la ora 1:" in rezultat["alaturi"]["verdict"] and rezultat["alaturi"]["prag"] == 0.02
    assert "alături" in iesire and f"{prima_ora:.4f}" in iesire


@pytest.mark.parametrize("scor,inceput", [(0.46, "MAI BUN"), (0.52, "MAI SLAB"), (0.49, "ÎN ZGOMOT"), (0.475, "ÎN ZGOMOT")])
def test_verdictul_alaturi(scor, inceput):
    ore = [{"ora": 1, "scor": 0.6}, {"ora": 8, "scor": scor}]
    verdict = antrenare_lunga.verdict_alaturi(ore, {1: 0.58, 8: 0.4921}, "antrenare_lunga", 0.02)
    assert verdict.startswith(inceput) and "la ora 8: " in verdict and "0.4921" in verdict
    assert antrenare_lunga.verdict_alaturi(ore, {1: 0.58}, "antrenare_lunga", 0.02) is None  # nicio oră 8 alături
