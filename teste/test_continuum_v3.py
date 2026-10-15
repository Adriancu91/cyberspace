"""CONTINUUM v3 (13 octombrie 2026): româna și codul ca nevoi („deprinde”, cât timp sunt sub pragul lor), continuarea de zi
cu limită de oră și pauza care nu sare peste începutul unei ferestre. Fără placă video."""

from datetime import datetime
from pathlib import Path

import pytest

from module.continuum import EroareContinuum, citeste_config, guvernator
from module.continuum.bucla import Bucla
from teste.continuum_proba import Lume, fisa, fisa_unealta, scrie_jurnal
from teste.test_continuum_v2 import CRITERII, SCADE, argumente, bucla, proiect

RADACINA = Path(__file__).resolve().parent.parent
CAPACITATI = '''
[capacitati.romana]
metrica = "bpb_romana"
mai_mare_e_mai_bine = false
prag_zgomot = 0.05
prag_deprins = 3.0
module = ["model"]
unealta = { linie = "examen_validari_ws", scor = "bpb_romana" }

[capacitati.cod]
metrica = "bpb_cod"
mai_mare_e_mai_bine = false
prag_zgomot = 0.05
prag_deprins = 3.0
module = ["model"]
unealta = { linie = "examen_validari_ws", scor = "bpb_cod" }

[hrana.fapte]'''
DEPRINDE = '''
[nevoi.deprinde]
nivel = "ÎNVĂȚARE"
capacitati = ["romana", "cod"]
configurari = ["config/ws_w2.toml"]
prelungire_ore = 10
timeout_ore = 0.05

[nevoi.dezvolta]'''
V3 = {
    'ordinea_nevoilor = ["masoara", "continua", "linie_noua", "dezvolta"]':
        'ordinea_nevoilor = ["masoara", "deprinde", "continua", "linie_noua", "dezvolta"]',
    "\n[hrana.fapte]": CAPACITATI,
    "\n[nevoi.dezvolta]": DEPRINDE,
}
ZI = {'nivel = "ÎNVĂȚARE"\ncapacitate = "povesti"\ncastig_minim = 0.005':
      'nivel = "ÎNTREȚINERE"\nzi_pana_la = "18:20"\ncapacitate = "povesti"\ncastig_minim = 0.005'}


def lume(tmp_path, monkeypatch, romana=6.42, cod=4.77, inlocuiri=None):
    """W1 cu 10 ore (încă învață), W2 neîncepută; pe ultimul model W1 (#10), româna și codul măsurate cu unealta."""
    proiect(tmp_path, monkeypatch, SCADE, inlocuiri={**V3, **(inlocuiri or {})})
    scoruri = {k: v for k, v in (("bpb_romana", romana), ("bpb_cod", cod)) if v is not None}
    if scoruri:
        scrie_jurnal(tmp_path, [fisa_unealta(11, "examen_validari_ws", 10, scoruri)])


def test_romana_si_codul_nedeprinse_cer_linia_care_le_invata(tmp_path, monkeypatch):
    lume(tmp_path, monkeypatch)
    rand = bucla().ciclu()
    assert rand["nevoie"] == "deprinde:romana"  # cea mai departe de pragul ei; codul e pomenit în motiv
    assert "romana = 6,42" in rand["motiv"] and "cod = 4,77" in rand["motiv"] and "sub 3" in rand["motiv"]
    assert "#10, linia ws_w1" in rand["motiv"] and "config/ws_w2.toml" in rand["motiv"]
    assert "config/ws_w2.toml" in rand["actiune"] and "de la zero" in rand["actiune"]
    assert "--ore 10" in rand["comenzi"][0] and "--porneste-din" not in rand["comenzi"][0]
    # celelalte variante adevărate rămân notate
    assert [a["nevoie"] for a in rand["alternative"]] == ["continua:povesti", "linie_noua:povesti"]


def test_fara_nevoia_noua_ordinea_veche_alege_continuarea(tmp_path, monkeypatch):
    """Ce ar fi ales fără greutatea pusă pe română și cod: W1 mai departe (ca în v2)."""
    lume(tmp_path, monkeypatch, inlocuiri={
        'ordinea_nevoilor = ["masoara", "deprinde", "continua", "linie_noua", "dezvolta"]':
            'ordinea_nevoilor = ["masoara", "continua", "deprinde", "linie_noua", "dezvolta"]'})
    rand = bucla().ciclu()
    assert rand["nevoie"] == "continua:povesti" and "ws_w1" in rand["actiune"]
    assert [a["nevoie"] for a in rand["alternative"]] == ["deprinde:romana", "linie_noua:povesti"]


@pytest.mark.parametrize("romana, cod, asteptat", [
    (2.4, 1.7, None),          # amândouă deprinse: nevoia dispare
    (None, None, None),        # nemăsurate pe ultimul model: nu se ghicește
    (2.9, 3.4, "deprinde:cod"),
    (3.0, 3.0, None),          # exact pe prag: deprins
])
def test_nevoia_apare_doar_cat_timp_o_capacitate_masurata_e_sub_prag(tmp_path, monkeypatch, romana, cod, asteptat):
    lume(tmp_path, monkeypatch, romana, cod)
    rand = bucla().ciclu()
    cerute = [n["nevoie"] for n in rand["nevoi"] if n["nevoie"].startswith("deprinde")]
    assert cerute == ([asteptat] if asteptat else [])
    assert rand["nevoie"] == (asteptat or "continua:povesti")


def test_linia_inceputa_si_inca_nedeprinsa_se_prelungeste(tmp_path, monkeypatch):
    lume(tmp_path, monkeypatch)
    scrie_jurnal(tmp_path, [fisa(20 + i, "ws_w2", 0.44 - 0.001 * i, criterii=CRITERII, straturi=12, minute=60,
                                 inceput="2026-10-07T00:00:00+00:00") for i in range(10)]
                 + [fisa_unealta(40, "examen_validari_ws", 29, {"bpb_romana": 3.4, "bpb_cod": 2.2})])
    rand = bucla().ciclu()
    assert rand["nevoie"] == "deprinde:romana" and "#29, linia ws_w2" in rand["motiv"] and "cod" not in rand["motiv"].split(".")[0]
    assert "prelungită cu 10 ore, de la ora 11" in rand["actiune"] and "--ore 20" in rand["comenzi"][0]


def test_ziua_se_continua_linia_veche_cu_limita_de_ora_iar_deprinderea_asteapta_noaptea(tmp_path, monkeypatch):
    lume(tmp_path, monkeypatch, inlocuiri=ZI)
    rand = bucla(ora="09:30").ciclu()
    assert rand["nivel"] == "ÎNTREȚINERE" and rand["nevoie"] == "continua:povesti"
    assert rand["comenzi"][0].endswith("--pana-la 18:20") and "cel mult până la 18:20" in rand["actiune"]
    assert {"nevoie": "deprinde:romana", "de_ce_nu": "nivelul ÎNTREȚINERE nu o permite (cere ÎNVĂȚARE)"} in rand["sarite"]
    # după-amiaza târziu nu mai încape o oră întreagă: nu mai pornește
    tarziu = bucla(ora="17:15").ciclu()
    assert tarziu.get("nevoie") != "continua:povesti"
    assert "până la 18:20 nu mai încape o oră întreagă" in next(
        s["de_ce_nu"] for s in tarziu["sarite"] if s["nevoie"] == "continua:povesti")
    # noaptea, limita de zi nu se aplică, iar deprinderea are întâietate
    noaptea = bucla(ora="23:30").ciclu()
    assert noaptea["nevoie"] == "deprinde:romana" and "--pana-la" not in " ".join(noaptea["comenzi"])
    assert "--pana-la" not in noaptea["alternative"][0]["actiune"]


def test_pe_bune_deprinderea_porneste_w2(tmp_path, monkeypatch):
    lume(tmp_path, monkeypatch)
    rand = bucla(simuleaza=False).ciclu()
    assert rand["nevoie"] == "deprinde:romana" and rand["rezultat"]["reusit"]
    args = argumente(tmp_path)
    assert args[args.index("--config") + 1] == "config/ws_w2.toml" and args[args.index("--ore") + 1] == "10"
    assert rand["verdict"] == "NECONCLUDENT"  # româna nu e încă măsurată pe modelul nou: o măsoară „masoara”, apoi


def test_pauza_nu_sare_peste_inceputul_ferestrei(tmp_path, monkeypatch):
    ferestre = {'fereastra_invatare = "22:00-07:00"': 'fereastra_invatare = "19:00-21:00"',
                'fereastra_intretinere = "07:00-22:00"': 'fereastra_intretinere = "07:45-18:50"',
                'REPAUS = 0': 'REPAUS = 5'}
    lume(tmp_path, monkeypatch, inlocuiri=ferestre)
    config = citeste_config("config/continuum.toml")
    assert guvernator.secunde_pana_la_fereastra(datetime(2026, 10, 13, 18, 57), config) == 180
    assert guvernator.secunde_pana_la_fereastra(datetime(2026, 10, 13, 19, 0), config) == (12 * 60 + 45) * 60
    assert guvernator.secunde_pana_la_fereastra(datetime(2026, 10, 13, 6, 0), config) == 105 * 60
    for ora, asteptat in (("18:57", 182), ("18:52", 300)):  # aproape de 19:00: fix atunci; altfel pauza nivelului
        pauze: list[float] = []
        b = Bucla("config/continuum.toml", simuleaza=True, senzori=Lume(ora=ora).senzori(), dormi=pauze.append,
                  iesire=lambda s: None)
        b.ruleaza(cicluri=2)
        assert pauze == [pytest.approx(asteptat)], ora
    assert bucla(ora="18:57").ciclu()["nivel"] == "REPAUS"  # în afara ferestrelor: doar observă
    assert bucla(ora="19:00").ciclu()["nevoie"] == "deprinde:romana"
    assert bucla(ora="21:30").ciclu()["nivel"] == "REPAUS"  # după 21:00 nu se mai pornește o antrenare de noapte


def test_cand_alegerea_e_a_omului_doar_observa_si_spune_de_ce(tmp_path, monkeypatch):
    lume(tmp_path, monkeypatch, inlocuiri={'procese_grele = ["python"]': 'procese_grele = ["python"]\n'
                                           'om_decide_pana_la = "2026-10-08T07:45"\nom_decide_motiv = "azi alege Adrian"'})
    rand = bucla(ora="23:30").ciclu()  # Lume: 7 octombrie
    assert rand["nivel"] == "REPAUS" and "nevoie" not in rand
    assert rand["de_ce_nivelul"].startswith("azi alege Adrian (până la 08.10 07:45)")
    assert "deprinde:romana" in [n["nevoie"] for n in rand["nevoi"]]  # nevoile se văd, dar nu se aleg


def test_configurarea_gresita_e_refuzata(tmp_path, monkeypatch):
    lume(tmp_path, monkeypatch, inlocuiri={'prag_deprins = 3.0\nmodule = ["model"]\nunealta = { linie = "examen_validari_ws", scor = "bpb_cod" }':
                                           'module = ["model"]\nunealta = { linie = "examen_validari_ws", scor = "bpb_cod" }'})
    with pytest.raises(EroareContinuum, match="prag_deprins.*cod"):
        citeste_config("config/continuum.toml")


def test_configurarea_adevarata_v3():
    config = citeste_config(RADACINA / "config" / "continuum_ws.toml")
    assert config["capacitati"]["romana"]["unealta"] == {"linie": "examen_validari_ws", "scor": "bpb_romana"}
    d = config["nevoi"]["deprinde"]
    assert (d["nivel"], d["capacitati"], d["configurari"], d["prelungire_ore"]) == (
        "ÎNVĂȚARE", ["romana", "cod"], ["config/ws_w2.toml"], 10)
    assert (d["scadere_minima"], d["copii"], d["pornire"]) == (0.05, "ws_w2_racit_*", 312)
    c = config["nevoi"]["continua"]  # din 14 octombrie: W1 nu mai primește ore; continuarea e doar W2, doar noaptea
    assert c["nivel"] == "ÎNVĂȚARE" and "zi_pana_la" not in c and c["configurari"] == ["config/ws_w2.toml"]
    assert config["anti_bucla"]["racire_cicluri"] == 20
    assert "greutățile date de Adrian" in d["nota"] and "nu dintr-o reglare a lui CONTINUUM" in d["nota"]
    assert "0,05" in d["nota"]


def test_nota_omului_intra_in_motivul_din_jurnal(tmp_path, monkeypatch):
    lume(tmp_path, monkeypatch, inlocuiri={'capacitati = ["romana", "cod"]':
                                           'nota = "greutatea e dată de om"\ncapacitati = ["romana", "cod"]'})
    b = bucla()
    rand = b.ciclu()
    assert rand["nevoie"] == "deprinde:romana" and rand["motiv"].endswith(". Notă: greutatea e dată de om")
    assert "Notă: greutatea e dată de om" in rand["pe_scurt"]
    assert all("Notă" not in n["motiv"] for n in rand["nevoi"] if not n["nevoie"].startswith("deprinde"))


# --- regula din 14 octombrie 2026: „deprinde” cât timp ultima noapte a scăzut nota cu cel puțin 0,05 (copiile răcite) ---

SCADERE = {'capacitati = ["romana", "cod"]\nconfigurari = ["config/ws_w2.toml"]':
           'capacitati = ["romana", "cod"]\nscadere_minima = 0.05\ncopii = "ws_w2_racit_*"\npornire = 10\n'
           'configurari = ["config/ws_w2.toml"]'}


def nopti_w2(tmp_path, copii):
    """W2 cu 10 ore pe noapte și, după fiecare noapte, copia răcită (pe linia ei) cu româna și codul măsurate."""
    fise, id_ = [], 20
    for noapte, (romana, cod) in enumerate(copii, start=1):
        for ora in range(10):
            fise.append(fisa(id_, "ws_w2", 0.43 - 0.001 * (10 * noapte + ora), criterii=CRITERII, straturi=12,
                             minute=60, inceput="2026-10-07T00:00:00+00:00"))
            id_ += 1
        fise.append(fisa(id_, f"ws_w2_racit_{10 * noapte:03d}", 0.46, criterii=CRITERII, straturi=12, minute=30))
        scoruri = {k: v for k, v in (("bpb_romana", romana), ("bpb_cod", cod)) if v is not None}
        if scoruri:
            fise.append(fisa_unealta(id_ + 1, "examen_validari_ws", id_, scoruri))
        id_ += 2
    scrie_jurnal(tmp_path, fise)


def test_dupa_prima_noapte_amandoua_au_scazut_mult_iar_w2_se_prelungeste(tmp_path, monkeypatch):
    lume(tmp_path, monkeypatch, inlocuiri=SCADERE)
    nopti_w2(tmp_path, [(1.38, 0.78)])
    rand = bucla().ciclu()
    assert [n["nevoie"] for n in rand["nevoi"] if n["nevoie"].startswith("deprinde")] == ["deprinde:romana",
                                                                                          "deprinde:cod"]
    assert rand["nevoie"] == "deprinde:romana"
    assert "6,42 → 1,38" in rand["motiv"] and "cel puțin 0,05" in rand["motiv"] and "#10 → #30" in rand["motiv"]
    assert "prelungită cu 10 ore, de la ora 11" in rand["actiune"] and "--ore 20" in rand["comenzi"][0]
    assert [list(p) for p in rand["organism"]["nopti"]["cod"]] == [[10, 4.77], [30, 0.78]]


@pytest.mark.parametrize("a_doua, asteptat", [
    ((1.35, 0.70), ["deprinde:cod"]),                      # româna doar −0,03: nu; codul −0,08: da
    ((1.33, 0.73), ["deprinde:romana", "deprinde:cod"]),   # exact 0,05 la amândouă: „cel puțin”
    ((1.36, 0.77), []),                                    # amândouă aproape de plafon
    ((1.50, 0.90), []),                                    # au crescut
    ((None, None), []),                                    # copia nu e măsurată încă: nu se ghicește
])
def test_a_doua_noapte_cere_cel_putin_0_05(tmp_path, monkeypatch, a_doua, asteptat):
    lume(tmp_path, monkeypatch, inlocuiri=SCADERE)
    nopti_w2(tmp_path, [(1.38, 0.78), a_doua])
    rand = bucla().ciclu()
    assert sorted(n["nevoie"] for n in rand["nevoi"] if n["nevoie"].startswith("deprinde")) == sorted(asteptat)


def test_fara_nicio_noapte_nevoia_nu_apare(tmp_path, monkeypatch):
    lume(tmp_path, monkeypatch, inlocuiri=SCADERE)  # doar măsurătoarea de pornire, nicio copie răcită
    rand = bucla().ciclu()
    assert all(not n["nevoie"].startswith("deprinde") for n in rand["nevoi"])
