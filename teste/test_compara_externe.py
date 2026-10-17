"""Comparația externă (unelte/compara_externe.py): aceleași note ca examenul Kronos și testul „continuă din memorie”."""

from __future__ import annotations

import json
import math

import pytest

from teste.test_bucla_cinstita import config_mic, fise
from unelte import antrenare_lunga
from unelte import compara_externe as ce

SEP = "<|endoftext|>"


class Numaratoare(ce.Retea):
    """Bucățile sunt literele; după litera k vine sigur litera k+1 (fără să-i pese de ce era înainte)."""

    nume, context, vocabular = "numaratoare", 8, 64

    def codifica(self, text):
        return [ord(c) - 32 for c in text]

    def decodeaza(self, simboluri):
        return "".join(chr(s + 32) for s in simboluri)

    def logits(self, x):
        import torch

        out = torch.full((*x.shape, self.vocabular), -1e9)
        out.scatter_(-1, ((x + 1) % self.vocabular).unsqueeze(-1), 0.0)
        return out


def test_bitii_pe_un_model_sigur_si_pe_unul_uniform():
    pytest.importorskip("torch")
    sigur = Numaratoare()
    # doar primul simbol costă (log2 din vocabular); restul sunt ghicite sigur, în oricâte ferestre
    for fereastra in (3, 8, 100):
        assert ce.biti(sigur, "0123456789:;<=>?@AB", fereastra) == pytest.approx(math.log2(64), abs=1e-3)
    assert ce.biti(sigur, "", 8) == 0.0

    class Uniform(Numaratoare):
        def logits(self, x):
            import torch

            return torch.zeros((*x.shape, self.vocabular))

    assert ce.biti(Uniform(), "0123456789:;<=>?@ABC", 7) == pytest.approx(20 * math.log2(64))


def test_continuarea_lacoma_si_literele_identice():
    pytest.importorskip("torch")
    assert ce.continua_lacom(Numaratoare(), "0123", litere=5) == "45678"
    assert ce.litere_identice("abcdef", "abcxyz") == 3 and ce.litere_identice("", "abc") == 0
    r = ce.din_memorie(Numaratoare(), [("0123", "456789" * 10), ("0123", "4x")])
    assert r["pasaje"] == 2 and r["parte_din_memorie"] == 0.0 and r["potriviri"][1] == 1
    r = ce.din_memorie(Numaratoare(), [("!", "".join(chr(c) for c in range(34, 34 + 60)))])
    assert r["potriviri"] == [60] and r["parte_din_memorie"] == 1.0  # 60 ≥ 50 de litere: „din memorie”


def test_pasajele_si_regula_de_verdict(tmp_path):
    fisier = tmp_path / "v.txt"
    texte = ["scurt"] + [f"textul {k} " + "cuvânt " * 100 for k in range(5)]
    fisier.write_text("".join(f"{t}\n{SEP}\n" for t in texte), encoding="utf-8")
    p = ce.pasaje(fisier, 3)
    assert len(p) == 3 and p[0][0].startswith("textul 0") and not p[0][0].endswith(" ") and p[0][1].startswith(" ")
    assert len(p[0][0]) <= 300 and len(p[0][1]) == 120
    assert ce.verdict_memorie(0.30, 0.10) == "a văzut probabil"
    assert ce.verdict_memorie(0.18, 0.10) == "nu se vede că le-a văzut"  # sub 10 puncte peste martor
    assert ce.verdict_memorie(0.35, 0.20) == "nu se vede că le-a văzut"  # sub dublul martorului


def test_aceleasi_note_ca_examenul_kronos(tmp_path, monkeypatch, capsys):
    """Pe un model Kronos mic, bitii socotiți aici sunt exact cei ai lui Kronos; rularea scrie raportul, fără jurnal."""
    pytest.importorskip("torch")
    monkeypatch.chdir(tmp_path)
    cale = config_mic(tmp_path, "antrenare_lunga_3", model=', cale_stare = "lucru/antrenare_lunga_3/gpt.pt"', spatiu="lot = [4]")
    assert antrenare_lunga.main(["--config", str(cale), "--ore", "1", "--pauza", "0", "--racire", "0", "--lungime", "20"]) == 0
    model_id = [f for f in fise(tmp_path) if f.get("model_salvat")][-1]["id"]
    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    model = incarca_modelul(fisa_modelului(Jurnal(tmp_path / "lucru"), model_id), "cpu")
    text = "Pisica doarme pe covor, iar câinele aleargă prin grădină. " * 30
    retea = ce.ReteaKronos(model)
    assert ce.biti(retea, text, model.setari["context"]) == pytest.approx(model.biti_pentru(text), rel=1e-5)

    ro = tmp_path / "ro.txt"
    ro.write_text("".join(f"Textul {k}: " + "pisica doarme pe covor " * 30 + f"\n{SEP}\n" for k in range(4)), encoding="utf-8")
    monkeypatch.setattr(ce, "VALIDARI", {"romana_wikipedia": str(ro), "romana_web": str(tmp_path / "lipsa.txt")})
    randuri = len(fise(tmp_path))
    capsys.readouterr()
    assert ce.main(["--kronos", str(model_id), "--modele", "", "--pasaje", "2", "--fire", "2"]) == 0
    raport = json.loads(next((tmp_path / "lucru" / "comparatie_externa").glob("comparatie_*.json")).read_text(encoding="utf-8"))
    memorie = raport["modele"][f"kronos_{model_id}"]["din_memorie"]
    assert list(memorie) == ["romana_wikipedia"] and memorie["romana_wikipedia"]["pasaje"] == 2
    assert len(fise(tmp_path)) == randuri  # jurnalul Kronos nu se atinge
    assert "Toate cifrele" in capsys.readouterr().out


def test_intervalul_si_diferenta_pe_texte():
    iv = ce.interval([10.0, 20.0, 30.0], [10, 10, 10], ori=500)
    assert iv["bpb"] == 2.0 and iv["jos"] <= 2.0 <= iv["sus"] and iv["jos"] >= 1.0 and iv["sus"] <= 3.0
    assert ce.interval([5.0] * 4, [10] * 4) == {"bpb": 0.5, "jos": 0.5, "sus": 0.5}
    a = [{"biti": 8.0, "octeti": 10}, {"biti": 9.0, "octeti": 10}, {"biti": 12.0, "octeti": 10}]
    b = [{"biti": 10.0, "octeti": 10}, {"biti": 10.0, "octeti": 10}, {"biti": 10.0, "octeti": 10}]
    d = ce.diferenta(a, b, ori=500)
    assert d["diferenta"] == pytest.approx(-0.0333, abs=1e-4) and d["texte_mai_bun"] == 2 and d["texte"] == 3
    assert d["jos"] <= d["diferenta"] <= d["sus"]
