"""Lanțul de antrenare (unelte/lant_antrenare.py), fără placă video: alegerea celui mai bun model după fapte, citirea
plăcii și ordinea etapelor (cu etape și placă de probă)."""

from __future__ import annotations

import json
import subprocess

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
