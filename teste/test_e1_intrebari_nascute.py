"""E1 „întrebări născute de Kronos” (S17, 22 octombrie 2026): bucățile, tiparele, filtrele fără LLM, alegerea pe tipare,
notarea examenelor cu verificatorul și generarea (pe un model de jucărie, fără placă)."""

import random
from collections import Counter

import torch

from unelte import e1_intrebari_nascute as e1

TEXT = ("Mărturie mortală este un film de acțiune american din 2006, regizat de Richard Donner. Rolurile principale "
        "sunt interpretate de Bruce Willis, Mos Def și David Morse.")


def test_tiparul_se_opreste_la_primul_nume():
    assert e1.tipar("Cine a regizat Mărturie mortală?") == "cine a regizat"
    assert e1.tipar("Ce este Gușoeni?") == "ce este"
    assert e1.tipar("În ce an s-a născut Ion Popescu?") == "în ce an s-a"
    assert e1.tipar("Câți locuitori avea satul în 1992?") == "câți locuitori avea satul"


def test_inceputul_e_cel_din_conversatie_text():
    assert e1.inceput("În ce județ se află Gușoeni?") == "în ce județ se"


def test_bucata_din_raspuns():
    assert e1.bucata_din_raspuns(TEXT, "Richard Donner.") == "Richard Donner"
    assert e1.bucata_din_raspuns("Satul e în județul Bihor.", "În județul Bihor.") == "județul Bihor"
    assert e1.bucata_din_raspuns("S-a născut în 1959 la Cluj.", "În 1959.") == "1959"
    assert e1.bucata_din_raspuns("Joacă pe postul de mijlocaș.", "Mijlocaș.") == "mijlocaș"
    assert e1.bucata_din_raspuns(TEXT, "Nicăieri.") is None


def test_bucatile_sunt_din_text_si_echilibrate():
    b = e1.bucati_candidate(TEXT)
    assert "Richard Donner" in b and "regizat de Richard Donner" in b
    assert all(x in TEXT for x in b)
    assert all(x.count("„") == x.count("”") for x in e1.bucati_candidate("Piesele „Dragon”, „Forever” și altele."))
    assert all(any(len(c) >= 3 or c.isdigit() for c in x.split()) for x in b)


def test_alege_bucati_intai_cate_una_pe_articol():
    articole = [{"text": TEXT, "x": "A"}, {"text": "Orașul Bielefeld are o universitate mare din 1969.", "x": "B"}]
    b = e1.alege_bucati(articole, 2, random.Random(1))
    assert [x["articol"] for x in b[:2]] == [0, 1]
    assert len(b) <= 4 and all(x["bucata"] in articole[x["articol"]]["text"] for x in b)


def test_forma():
    assert e1.forma_buna("Cine joacă în Mărturie mortală?", "Bruce Willis")
    assert not e1.forma_buna("Cine joacă în Mărturie mortală", "Bruce Willis")  # fără „?”
    assert not e1.forma_buna("Cine?", "Bruce Willis")  # prea scurtă
    assert not e1.forma_buna("Text: ceva aici acum?", "x")
    assert not e1.forma_buna("Bruce Willis joacă în Mărturie mortală?", "Bruce Willis")  # își spune răspunsul


class MotorDeJucarie:
    def verifica_text(self, text):
        probleme = []
        if "au fost fondată" in text:
            probleme.append({"tip": "acord_subiect_predicat", "cuvinte": ["au", "fondată"]})
        for c in text.rstrip("?").split():
            if c in ("Donner", "Zorglub", "développement"):
                probleme.append({"tip": "ipoteza" if c[0].isupper() else "necunoscut", "cuvinte": [c]})
        return {"probleme": probleme}


def test_motorul_lasa_doar_cuvintele_necunoscute_din_text():
    m = MotorDeJucarie()
    assert e1.motor_ok(m, "Ce a făcut Donner?", TEXT)
    assert not e1.motor_ok(m, "Ce a făcut Zorglub?", TEXT)  # nume inventat
    assert not e1.motor_ok(m, "În ce an au fost fondată echipa?", TEXT)


def test_filtrele_ieftine_in_ordine():
    inceputuri = {"cine a regizat mărturie"}
    tipare = {"ce este"}
    c = [{"text": TEXT, "bucata": "Richard Donner", "intrebare": q} for q in (
        "Fără semn la final",                        # (0)
        "Cine a regizat Mărturie mortală?",          # (ii) 4 cuvinte
        "Ce este Mărturie mortală?",                 # (ii) tipar
        "Cine a fost regizorul filmului din 2006?",  # trece
        "Cine a fost regizorul filmului din 2006 ?",  # (iii) duplicat după normalizare
        "Ce a făcut Zorglub?",                       # (iv)
    )]
    raman, cazute = e1.filtre_ieftine(c, inceputuri, tipare, MotorDeJucarie())
    assert [r["intrebare"] for r in raman] == ["Cine a fost regizorul filmului din 2006?"]
    assert cazute == {"0_forma": 1, "iii_duplicat": 1, "ii_noutate_4_cuvinte": 1, "ii_noutate_tipar": 1, "iv_motor": 1}


def test_alegerea_pe_tipare_tine_toate_tiparele():
    q = [{"intrebare": f"Cine a fost X{i}?"} for i in range(50)] + [{"intrebare": "Ce culoare are X?"},
                                                                       {"intrebare": "Unde trăiește X?"}]
    alese = e1.alege_pe_tipare(q, 5, random.Random(1023))
    assert len(alese) == 5
    assert {e1.tipar(a["intrebare"]) for a in alese} >= {"ce culoare are", "unde trăiește", "cine a fost"}
    assert len(e1.alege_pe_tipare(q, 1000, random.Random(1))) == 52


def test_raspunsul_de_antrenare():
    assert e1.raspuns_de_antrenare("județul Bihor") == "Județul Bihor."
    assert e1.raspuns_de_antrenare("Bruce Willis.") == "Bruce Willis."


def test_date_generator():
    antrenari = [[
        {"fel": "text", "text": TEXT, "tip": "regizat", "intrebare": "Cine a regizat Mărturie mortală?",
         "raspuns": "Richard Donner."},
        {"fel": "text", "text": TEXT, "tip": "regizat", "intrebare": "Cine a regizat Mărturie mortală?",
         "raspuns": "Richard Donner."},
        {"fel": "text", "text": TEXT, "tip": "da_nu_regizat", "intrebare": "L-a regizat Donner?", "raspuns": "Da."},
        {"fel": "nu_scrie", "text": TEXT, "tip": "lipsa_x", "intrebare": "Cine a scris?", "raspuns": "Nu scrie în text."},
        {"fel": "text", "text": TEXT, "tip": "an", "intrebare": "Din ce an e?", "raspuns": "Din 1999."},
    ]]
    perechi, motive = e1.date_generator(antrenari)
    assert len(perechi) == 1
    p = perechi[0]
    assert p["intrebare"] == e1.CERERE.format(b="Richard Donner") and p["raspuns"] == "Cine a regizat Mărturie mortală?"
    assert motive["repetată"] == 1 and motive["răspunsul nu e în text"] == 1


def test_verificari_articole():
    a = [{"text": "t1", "x": "A"}, {"text": "t2", "x": "A"}, {"text": "t3", "x": "C"}]
    v = e1.verificari_articole(a, {"t1"}, [[{"text": "t3"}]])
    assert v == {"texte_de_examen": 1, "texte_din_antrenare": 1, "subiecte_repetate": 1}


def test_notarea_cu_verificatorul():
    intrebari = [
        {"fel": "text", "categorie": "b2", "raspuns": "În Elveția.", "raspuns_elev": "În Elveția."},
        {"fel": "text", "categorie": "b2", "raspuns": "În Elveția.", "raspuns_elev": "Nu scrie în text."},
        {"fel": "text", "categorie": "e", "raspuns": "Pe Cartoon Network.", "raspuns_elev": "Da."},
        {"fel": "nu_scrie", "raspuns": "Nu scrie în text.", "raspuns_elev": "Nu scrie în text."},
        {"fel": "text", "raspuns": "Da.", "raspuns_elev": "Nu."},
        {"fel": "text", "categorie": "a", "raspuns": "Nu scrie în text.", "raspuns_elev": "Nu."},
        {"fel": "conversatie", "raspuns": "Bună!", "raspuns_elev": "Salut!"},
    ]
    n = e1.noteaza(intrebari)
    assert n["intrebari"] == {"b2": 2, "e": 1, "nu_scrie": 1, "text": 1, "a": 1, "conversatie": 1}
    assert n["corecte"] == {"b2": 1, "e": 0, "nu_scrie": 1, "text": 0, "a": 0}
    assert n["nu_scrie_pe_nedrept"] == 1 and n["da_nu_gresit"] == 2


class TokDeJucarie:
    """Un simbol = o literă."""
    litere = list("abcdefghijklmnopqrstuvwxyz ?\n:ÎÂăîâșțCeTxRp.")

    def codifica(self, text):
        return [self.litere.index(c) if c in self.litere else 0 for c in text]

    def decodeaza(self, s):
        return "".join(self.litere[i] for i in s)


class ReteaDeJucarie(torch.nn.Module):
    """Scrie mereu „ce?⏎”: după „?” vine rând nou, după rând nou „c”, după „c” „e”, după „e” „?”."""

    def __init__(self, tok):
        super().__init__()
        self.tok = tok
        self.urm = {tok.litere.index(a): tok.litere.index(b) for a, b in (("c", "e"), ("e", "?"), ("?", "\n"))}
        self.implicit = tok.litere.index("c")

    def forward(self, idx, memorie=None):
        v = len(self.tok.litere)
        logits = torch.full((idx.shape[0], idx.shape[1], v), -20.0)
        for b in range(idx.shape[0]):
            logits[b, -1, self.urm.get(int(idx[b, -1]), self.implicit)] = 20.0
        return logits


class ModelDeJucarie:
    def __init__(self):
        self.tok = TokDeJucarie()
        self.retea = ReteaDeJucarie(self.tok)
        self.setari = {"context": 64}
        self.dispozitiv = torch.device("cpu")


def test_esantionarea_si_raspunsul_se_opresc_la_rand_nou():
    m = ModelDeJucarie()
    gen = torch.Generator().manual_seed(0)
    assert e1.esantioneaza(m, "Text: x\nÎntrebare: p\nRăspuns:", n=3, generator=gen) == ["ce?"] * 3
    assert e1.raspunde(m, "Răspuns:") == "ce?"


def _noaptea_cu(monkeypatch, tmp_path, coduri, pastrate=5):
    import json

    chemate = []

    def call(comanda, cwd=None):
        chemate.append(comanda)
        return coduri.get(len(chemate), 0)

    monkeypatch.setattr(e1.subprocess, "call", call)
    monkeypatch.setattr(e1, "DOSAR", tmp_path / "auto")
    monkeypatch.setattr(e1, "LUCRU", tmp_path / "e1")
    (tmp_path / "auto").mkdir()
    (tmp_path / "auto" / "info.json").write_text(json.dumps({"filtre": {"pastrate": pastrate}}), encoding="utf-8")
    return chemate


def test_noaptea_ruleaza_pasii_in_ordine(monkeypatch, tmp_path):
    chemate = _noaptea_cu(monkeypatch, tmp_path, {})
    assert e1.noaptea(60, 45) == 0
    pasi = [" ".join(c[3:]) for c in chemate]
    assert pasi[0] == "unelte/antrenare_lunga.py --config config/e1_generator.toml --ore 1 --porneste-din 415"
    assert pasi[1].endswith("genereaza --minute 60") and pasi[2].endswith("filtreaza --minute 45")
    assert pasi[3] == "unelte/antrenare_lunga.py --config config/conv_w2_auto_v1.toml --ore 3 --porneste-din 415"
    assert pasi[4].endswith("examene --linie w2_conv_auto_v1")
    assert pasi[5] == "unelte/examen_validari_ws.py --linie w2_conv_auto_v1"
    assert (tmp_path / "e1" / "noaptea.json").exists()


def test_noaptea_se_opreste_la_prima_eroare(monkeypatch, tmp_path):
    import json
    import pytest

    chemate = _noaptea_cu(monkeypatch, tmp_path, {2: 1})
    with pytest.raises(SystemExit):
        e1.noaptea(60, 45)
    assert len(chemate) == 2
    assert json.loads((tmp_path / "e1" / "noaptea.json").read_text(encoding="utf-8"))["pasi"][-1]["cod"] == 1


def test_noaptea_nu_antreneaza_fara_intrebari(monkeypatch, tmp_path):
    import pytest

    chemate = _noaptea_cu(monkeypatch, tmp_path, {}, pastrate=0)
    with pytest.raises(SystemExit):
        e1.noaptea(60, 45)
    assert len(chemate) == 3


def test_tipurile_numarate_pe_patru_cuvinte_si_pe_tipar():
    t = e1.tipuri([{"intrebare": "Ce este Ana?"}, {"intrebare": "Ce este Ion?"}, {"intrebare": "Unde stă Ana?"}])
    assert t["tipuri_4_cuvinte"] == 3 and t["tipuri_tipar"] == 2
    assert Counter(dict(t["cele_mai_dese_tipare"]))["ce este"] == 2


# ---- S18: repetarea cu 3× date --------------------------------------------------------------------------------------

def test_articolele_s18_sunt_cele_de_dupa_primele_2000(monkeypatch):
    import unelte.conversatie_text as ct

    cerute = []

    def articole_bune(*args):
        cerute.append(args[6])
        return [{"x": i} for i in range(args[6])]

    monkeypatch.setattr(ct, "articole_bune", articole_bune)
    noi = e1.articole_noi(4, sari=2)
    assert [a["x"] for a in noi] == [e1.FOLOSITE + 2 + i for i in range(4)]
    assert noi == e1.articole_noi(6)[2:] and cerute[0] == e1.FOLOSITE + 6
    assert [a["x"] for a in e1.articole_noi(3)] == [e1.FOLOSITE + i for i in range(3)]


def test_filtrul_fara_dubluri_fata_de_intrebarile_de_dinainte():
    c = [{"text": TEXT, "bucata": "Richard Donner", "intrebare": q} for q in (
        "Cine a fost regizorul filmului din 2006?",       # e deja în auto_v1
        "Cine a fost regizorul filmului din 2006 ?",      # duplicat în lotul nou (după normalizare)
        "Care este numele regizorului din 2006?",         # trece
    )]
    deja = {e1.normalizeaza("Cine a fost regizorul filmului din 2006?")}
    raman, cazute = e1.filtre_ieftine(c, set(), set(), MotorDeJucarie(), deja)
    assert [r["intrebare"] for r in raman] == ["Care este numele regizorului din 2006?"]
    assert cazute["iii_duplicat"] == 1 and cazute["iii_duplicat_deja"] == 1
    _, fara = e1.filtre_ieftine(c, set(), set(), MotorDeJucarie())
    assert "iii_duplicat_deja" not in fara


def _repetare_cu(monkeypatch, tmp_path, nascute, coduri=None):
    import json

    chemate = _noaptea_cu(monkeypatch, tmp_path, coduri or {})
    info = {"filtre": {"pastrate": nascute - 516, "nascute_total": nascute}}
    (tmp_path / "auto" / "info.json").write_text(json.dumps(info), encoding="utf-8")
    return chemate


def test_repetarea_ruleaza_pasii_s18_in_ordine(monkeypatch, tmp_path):
    import json

    chemate = _repetare_cu(monkeypatch, tmp_path, 1600)
    assert e1.repetare(150, 90) == 0
    pasi = [" ".join(c[3:]) for c in chemate]
    assert "genereaza --generator 422 --minute 150 --samanta 1023" in pasi[0]
    assert "filtreaza --minute 90 --deja date/conversatie/auto_v1/intrebari.jsonl" in pasi[1]
    assert pasi[2] == "unelte/antrenare_lunga.py --config config/conv_w2_auto_v2.toml --ore 3 --porneste-din 415"
    assert pasi[3].endswith("examene --linie w2_conv_auto_v2") and pasi[4].endswith("examene --experiment 415")
    assert pasi[5] == "unelte/examen_validari_ws.py --linie w2_conv_auto_v2"
    assert "analiza --experimente 415 425 --linie w2_conv_auto_v2" in pasi[6]
    assert all("--dosar" in p and "--lucru" in p for p in (pasi[0], pasi[1], pasi[3], pasi[4], pasi[6]))
    j = json.loads((tmp_path / "e1" / "repetare.json").read_text(encoding="utf-8"))
    assert j["nascute_total"] == 1600 and j["fata_de_s17"] == 3.1 and "sfarsit" in j
    assert not (tmp_path / "e1" / "noaptea.json").exists()


def test_repetarea_nu_antreneaza_sub_poarta(monkeypatch, tmp_path):
    import json

    chemate = _repetare_cu(monkeypatch, tmp_path, 1031)
    assert e1.repetare(150, 90) == 0
    assert len(chemate) == 2
    j = json.loads((tmp_path / "e1" / "repetare.json").read_text(encoding="utf-8"))
    assert j["poarta"].startswith("1031 < 1032")


def test_repetarea_se_opreste_la_prima_eroare(monkeypatch, tmp_path):
    import pytest

    chemate = _repetare_cu(monkeypatch, tmp_path, 2000, {3: 1})
    with pytest.raises(SystemExit):
        e1.repetare(150, 90)
    assert len(chemate) == 3


def test_analiza_b2_f1_lungi_si_fara_tiparele_nascute():
    r = [
        {"fel": "text", "categorie": "b2", "tip": "tara", "intrebare": "În ce țară se află X?", "raspuns": "În Elveția.",
         "raspuns_elev": "În Elveția."},
        {"fel": "text", "categorie": "b2", "tip": "tara", "intrebare": "În ce țară se află Y?", "raspuns": "În Franța.",
         "raspuns_elev": "Nu știu."},
        {"fel": "text", "categorie": "b2", "tip": "pictor", "intrebare": "Cine a pictat Z?", "raspuns": "Ion Andreescu.",
         "raspuns_elev": "Ion Andreescu, un pictor român foarte cunoscut din București."},
        {"fel": "text", "categorie": "e", "tip": "canal", "intrebare": "Pe ce canal rulează W?",
         "raspuns": "Pe Cartoon Network.", "raspuns_elev": "Pe Cartoon Network."},
    ]
    a = e1.analiza_b2(r, {"cine a pictat"})
    assert a["b2"] == "2/3" and a["b2_f1"] == "1/3"
    assert a["lungi_corecte"] == {"b2": 1}
    assert a["tipuri_scoase"] == ["pictor"] and a["b2_fara_tipare_nascute"] == "1/2"


def test_configurarea_s18_e_copia_s17_cu_alte_date():
    import tomllib

    v1 = tomllib.loads((e1.RADACINA / "config/conv_w2_auto_v1.toml").read_text(encoding="utf-8"))
    v2 = tomllib.loads((e1.RADACINA / "config/conv_w2_auto_v2.toml").read_text(encoding="utf-8"))
    s1, s2 = v1["porturi"]["model"].pop("setari"), v2["porturi"]["model"].pop("setari")
    assert v2["platforma"].pop("nume") == "w2_conv_auto_v2" and v1["platforma"].pop("nume") == "w2_conv_auto_v1"
    assert s2.pop("conversatie") == "date/conversatie/auto_v2/antrenare.jsonl"
    assert s2.pop("cale_stare") == "lucru/w2_conv_auto_v2/gpt.pt"
    s1.pop("conversatie"), s1.pop("cale_stare")
    assert s1 == s2 and v1 == v2
