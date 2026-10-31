"""Verificarea scurgerii setului ascuns în codul descărcat (S53): pe date mici făcute aici, FĂRĂ rețea și fără setul real."""

import json

import pytest

from unelte.kronos_cod import scurgere as s

P1 = {"id": "t01_01", "sablon": "t01_suma", "functie": "suma_pare",
      "enunt": 'def suma_pare(xs):\n    """Return the sum of the even integers in `xs`, ignoring the odd ones."""\n',
      "referinta": "    total = 0\n    for x in xs:\n        if x % 2 == 0:\n            total += x\n    return total\n",
      "teste": ["assert suma_pare([]) == 0", "assert suma_pare([1, 2, 3, 4]) == 6"]}
P2 = {"id": "t02_01", "sablon": "t02_scurt", "functie": "inverseaza",
      "enunt": 'def inverseaza(s):\n    """Return the string `s` written backwards, from the last character."""\n',
      "referinta": "    return s[::-1]\n",
      "teste": ["assert inverseaza('abc') == 'cba'"]}


def test_simbolurile_ignora_comentariile_spatiile_si_literele_mari():
    assert s.simboluri("X  =  1  # un comentariu\nreturn   X") == ["x", "=", "1", "return", "x"]


def test_scanarea_gaseste_solutia_exacta_cu_alte_spatii_si_comentarii():
    idx = s.indexeaza([P1, P2])
    text = "def alta(v):\n    # comentariu\n    TOTAL = 0\n    for x in xs:\n        if x%2==0:  total += x\n    return total\n"
    g = s.scaneaza_text(text, idx)
    assert 0 in g["exacte"] and 0 in g["atinse"] and g["atinse"][0] >= s.N


def test_solutia_scurta_se_cauta_pe_lungimea_ei_si_fisierul_curat_nu_e_atins():
    idx = s.indexeaza([P1, P2])
    assert s.scaneaza_text("def f(s):\n    return s[::-1]\n", idx)["exacte"] == [1]
    assert s.scaneaza_text("def f(a, b):\n    return a + b\n", idx) is None


def test_numele_functiei_se_numara_separat_fara_excludere():
    idx = s.indexeaza([P1, P2])
    g = s.scaneaza_text("def suma_pare(v):\n    pass\n", idx)
    assert g["nume"] == [0] and not g["atinse"] and not g["exacte"]


def _scrie_date(tmp_path, texte):
    ex = tmp_path / "examen"
    ex.mkdir()
    (ex / "probleme.jsonl").write_text("".join(json.dumps(p) + "\n" for p in (P1, P2)), encoding="utf-8")
    cod = tmp_path / "cod"
    cod.mkdir()
    (cod / "cod.jsonl").write_text("".join(json.dumps({"sursa": "t", "cale": f"f{i}.py", "sha256": f"h{i}", "text": t})
                                           + "\n" for i, t in enumerate(texte)), encoding="utf-8")
    return ex, cod


def test_rularea_cap_coada_scrie_lista_si_refuza_a_doua_oara(tmp_path):
    texte = ["def a(x):\n    return x\n", P1["enunt"] + P1["referinta"], "def b(s):\n    return s[::-1]\n",
             P1["enunt"] + P1["referinta"]]
    ex, cod = _scrie_date(tmp_path, texte)
    (cod / "aproape_duplicate.json").write_text("[3]", encoding="utf-8")
    sha = s.sha256_fisier(ex / "probleme.jsonl")
    rez = s.ruleaza(ex, cod, tmp_path / "iesire", procese=2, sha_asteptat=sha, jurnal=lambda m: None)
    assert rez["fisiere_scanate"] == 4 and rez["fisiere_curat"] == 3 and rez["sha_neschimbat"]
    assert rez["totaluri_curat"] == {"probleme_cu_suprapunere": 1, "probleme_cu_solutia_exacta": 2,
                                     "probleme_cu_def_nume": 1}
    assert rez["de_exclus_curat"]["fisiere"] == 2 and rez["de_exclus_tot"]["fisiere"] == 3
    assert rez["verdict"] == "de curățat"
    randuri = (tmp_path / "iesire" / "fisiere_de_exclus.txt").read_text(encoding="utf-8").splitlines()
    assert [r.split("\t")[0] for r in randuri] == ["1", "2", "3"]
    with pytest.raises(SystemExit):
        s.ruleaza(ex, cod, tmp_path / "iesire", procese=2, sha_asteptat=sha, jurnal=lambda m: None)


def test_suma_gresita_a_setului_opreste_rularea(tmp_path):
    ex, cod = _scrie_date(tmp_path, ["x = 1\n"])
    with pytest.raises(SystemExit):
        s.ruleaza(ex, cod, tmp_path / "iesire", procese=1, sha_asteptat="0" * 64, jurnal=lambda m: None)
    assert not (tmp_path / "iesire").exists()


def test_fara_nicio_atingere_verdictul_e_curat(tmp_path):
    ex, cod = _scrie_date(tmp_path, ["def a(x):\n    return x * 3\n"])
    rez = s.ruleaza(ex, cod, tmp_path / "iesire", procese=1, sha_asteptat=None, jurnal=lambda m: None)
    assert rez["verdict"] == "curat" and rez["de_exclus_curat"]["fisiere"] == 0
