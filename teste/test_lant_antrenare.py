"""Lanțul de antrenare (unelte/lant_antrenare.py), fără placă video: alegerea celui mai bun model după fapte, citirea
plăcii și ordinea etapelor (cu etape și placă de probă)."""

from __future__ import annotations

import json
import subprocess

import pytest

from unelte import lant_antrenare as lant


def fisa(id, decizie="pastrat", fapte_noi=None, model=True, linie="fapte_1"):
    f = {"id": id, "linie": linie, "decizie": decizie}
    if model and decizie == "pastrat":
        f["model_salvat"] = f"lucru/stocare/modele/experiment_{id}.pt"
    if fapte_noi is not None:
        f["criterii"] = {"fapte_noi": fapte_noi, "nota_profesor": 4.0}
    return f


def test_cel_mai_bun_dupa_fapte():
    fise = [fisa(249, fapte_noi=59), fisa(250, "respins", fapte_noi=80), fisa(251, fapte_noi=71),
            fisa(252, fapte_noi=90, linie="alta"), fisa(253, fapte_noi=95, model=False)]
    assert lant.cel_mai_bun_dupa_fapte(fise, "fapte_1", "fapte_noi") == (
        251, "#251: fapte_noi 71, cel mai mare dintre cele păstrate")  # nu cel respins, nu altă linie, nu fără model
    fara_criteriu = [fisa(249), fisa(250)]
    assert lant.cel_mai_bun_dupa_fapte(fara_criteriu, "fapte_1", "fapte_noi") == (
        250, "#250: ultimul păstrat (niciunul n-are fapte_noi)")
    assert lant.cel_mai_bun_dupa_fapte([fisa(249, "respins")], "fapte_1", "fapte_noi") == (
        None, "linia fapte_1 n-are niciun experiment păstrat")


def test_fisele_din_jurnal_sar_peste_randurile_stricate(tmp_path):
    jurnal = tmp_path / "jurnal" / "experimente.jsonl"
    jurnal.parent.mkdir(parents=True)
    jurnal.write_text(json.dumps(fisa(1)) + "\n{stricat\n" + json.dumps(fisa(2)) + "\n", encoding="utf-8")
    assert [f["id"] for f in lant.fise_din_jurnal(tmp_path)] == [1, 2]
    assert lant.fise_din_jurnal(tmp_path / "nu_exista") == []


def placa_de_proba(monkeypatch, gpu="50, 300, 6144", procese=""):
    monkeypatch.setattr(lant.shutil, "which", lambda _: "nvidia-smi")

    def run(comanda, **_):
        iesire = gpu if "--query-gpu=temperature.gpu,memory.used,memory.total" in comanda else procese
        return subprocess.CompletedProcess(comanda, 0, stdout=iesire + "\n", stderr="")
    monkeypatch.setattr(lant.subprocess, "run", run)


def test_placa_libera(monkeypatch):
    placa_de_proba(monkeypatch)
    assert lant.placa_libera(5500, 85) is None  # 5.844 MB liberi: încape o antrenare cu profesorul, sub 5,5 GB
    placa_de_proba(monkeypatch, procese="28624, C:\\...\\python.exe")
    assert lant.placa_libera(5500, 85) == "altă sarcină grea e pe placă: 28624, C:\\...\\python.exe"
    placa_de_proba(monkeypatch, gpu="50, 2285, 6144")
    assert lant.placa_libera(5500, 85) == "placa are deja 2285 MB ocupați"
    placa_de_proba(monkeypatch, gpu="88, 300, 6144")
    assert lant.placa_libera(5500, 85) == "placa are 88 °C, peste 85 °C"
    monkeypatch.setattr(lant.shutil, "which", lambda _: None)
    assert lant.placa_libera(5500, 85) == "nu găsesc nvidia-smi"


def test_lantul_porneste_a_doua_etapa_din_cel_mai_bun_model(tmp_path, monkeypatch):
    jurnal = tmp_path / "jurnal" / "experimente.jsonl"
    jurnal.parent.mkdir(parents=True)
    etape: list[tuple[str, list[str]]] = []

    def etapa(nume, comanda):
        etape.append((nume, comanda))
        if len(etape) == 1:  # antrenarea pe fapte scrie orele ei în jurnal
            jurnal.write_text("\n".join(json.dumps(f) for f in [fisa(249, fapte_noi=59), fisa(250, "respins", fapte_noi=60)]),
                              encoding="utf-8")
        return True

    monkeypatch.setattr(lant, "etapa", etapa)
    monkeypatch.setattr(lant, "asteapta_placa", lambda args: True)
    assert lant.main(["--director-lucru", str(tmp_path)]) == 0
    assert [n for n, _ in etape] == ["Antrenarea pe fapte", "A cincea antrenare lungă"]
    assert etape[0][1][2:] == ["unelte/antrenare_lunga.py", "--config", "config/laptop_fapte.toml", "--ore", "4",
                               "--porneste-din", "239", "--compara-cu", "239", "--inceput", lant.INCEPUT_POVESTE]
    assert etape[1][1][2:10] == ["unelte/antrenare_lunga.py", "--config", "config/laptop_antrenare_lunga_5.toml",
                                 "--ore", "5", "--porneste-din", "249", "--compara-cu"]


def test_lantul_se_opreste_la_o_etapa_cazuta(tmp_path, monkeypatch):
    etape: list[str] = []
    monkeypatch.setattr(lant, "etapa", lambda nume, comanda: etape.append(nume) or False)
    monkeypatch.setattr(lant, "asteapta_placa", lambda args: True)
    assert lant.main(["--director-lucru", str(tmp_path)]) == 1 and etape == ["Antrenarea pe fapte"]


def test_cu_stop_lantul_nici_nu_porneste(tmp_path, monkeypatch):
    etape: list[str] = []
    monkeypatch.setattr(lant, "etapa", lambda nume, comanda: etape.append(nume) or True)
    (tmp_path / "STOP").write_text("", encoding="utf-8")
    assert lant.main(["--director-lucru", str(tmp_path)]) == 1 and etape == []


# --- lanțul după un plan (config/lant_6.toml) ------------------------------------------------------------------------

def plan(tmp_path, text):
    cale = tmp_path / "plan.toml"
    cale.write_text(text, encoding="utf-8")
    return cale


ETAPA = '''
[[etapa]]
nume = "6a"
config = "config/laptop_antrenare_lunga_6a.toml"
ore = 5
porneste_din = 252
'''


def test_planul_de_diseara():
    fise = [fisa(252, fapte_noi=72), fisa(257, linie="antrenare_lunga_5")]
    p = lant.citeste_plan(lant.RADACINA / "config" / "lant_6.toml", fise)
    assert p["la_eroare"] == "continua"
    assert [(e["config"], e["ore"], e["porneste_din"], e["compara_cu"]) for e in p["etape"]] == [
        ("config/laptop_antrenare_lunga_6a.toml", 5, 252, 252),
        ("config/laptop_masurare_6c_restart.toml", 4, 252, 252),
        ("config/laptop_masurare_6c_continuare.toml", 4, 252, 252),
        ("config/laptop_antrenare_lunga_6b.toml", 5, 257, 257)]
    assert p["etape"][1]["nota"].startswith("măsurătoare, nu candidat") and p["etape"][0]["nota"] is None


@pytest.mark.parametrize("text, motiv", [
    ("[lant]\nla_eroare = \"poate\"\n" + ETAPA, "la_eroare"),
    ("[lant]\n", "nicio [[etapa]]"),
    (ETAPA.replace("ore = 5\n", ""), "lipsește ore"),
    (ETAPA.replace("lunga_6a", "lunga_99"), "nu există config/laptop_antrenare_lunga_99.toml"),
    (ETAPA.replace("ore = 5", "ore = 0"), "numere întregi"),
    (ETAPA.replace("porneste_din = 252", "porneste_din = 253"), "#253 n-are un model salvat"),
    ("[[etapa\n", "nu pot citi planul"),
])
def test_planul_se_verifica_inainte_de_pornire(tmp_path, text, motiv):
    with pytest.raises(ValueError, match=motiv.replace("[", r"\[").replace("]", r"\]").replace("#", r"\#")):
        lant.citeste_plan(plan(tmp_path, text), [fisa(252, fapte_noi=72)])


def test_lantul_dupa_plan(tmp_path, monkeypatch, capsys):
    jurnal = tmp_path / "jurnal" / "experimente.jsonl"
    jurnal.parent.mkdir(parents=True)
    jurnal.write_text(json.dumps(fisa(252, fapte_noi=72)) + "\n" + json.dumps(fisa(257, linie="antrenare_lunga_5")),
                      encoding="utf-8")
    cale = plan(tmp_path, ETAPA + ETAPA.replace('"6a"', '"6b"').replace("6a.toml", "6b.toml").replace("252", "257")
                + 'nota = "doar o probă"\n')
    etape: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(lant, "etapa", lambda nume, comanda: etape.append((nume, comanda)) or True)
    monkeypatch.setattr(lant, "asteapta_placa", lambda args: True)
    assert lant.main(["--plan", str(cale), "--director-lucru", str(tmp_path)]) == 0
    assert [n for n, _ in etape] == ["Etapa 1 din 2: 6a", "Etapa 2 din 2: 6b"]
    assert etape[1][1][2:] == ["unelte/antrenare_lunga.py", "--config", "config/laptop_antrenare_lunga_6b.toml", "--ore",
                               "5", "--porneste-din", "257", "--compara-cu", "257", "--inceput", lant.INCEPUT_POVESTE]
    iesire = capsys.readouterr().out
    assert "Etapa 2 din 2: doar o probă." in iesire and "Lanțul s-a încheiat: 2 din 2 etape reușite." in iesire


@pytest.mark.parametrize("la_eroare, etape_rulate, cod", [("opreste", 1, 1), ("continua", 2, 1)])
def test_o_etapa_cazuta_dupa_plan(tmp_path, monkeypatch, la_eroare, etape_rulate, cod):
    jurnal = tmp_path / "jurnal" / "experimente.jsonl"
    jurnal.parent.mkdir(parents=True)
    jurnal.write_text(json.dumps(fisa(252, fapte_noi=72)), encoding="utf-8")
    cale = plan(tmp_path, f'[lant]\nla_eroare = "{la_eroare}"\n' + ETAPA + ETAPA)
    etape: list[str] = []
    monkeypatch.setattr(lant, "etapa", lambda nume, comanda: etape.append(nume) or False)
    monkeypatch.setattr(lant, "asteapta_placa", lambda args: True)
    assert lant.main(["--plan", str(cale), "--director-lucru", str(tmp_path)]) == cod and len(etape) == etape_rulate


def test_un_plan_gresit_nu_porneste_nimic(tmp_path, monkeypatch):
    etape: list[str] = []
    monkeypatch.setattr(lant, "etapa", lambda nume, comanda: etape.append(nume) or True)
    assert lant.main(["--plan", str(plan(tmp_path, "[lant]\n")), "--director-lucru", str(tmp_path)]) == 1 and etape == []
