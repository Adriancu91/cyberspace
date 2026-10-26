"""S29: rădăcinile românești, indexul cu rădăcini, RRF și reordonarea cu judecătorul (fără model adevărat, fără placă)."""

import sqlite3

import pytest

from unelte import e3_memorie as e3
from unelte import e3_reordonare as r

GRUPE = [  # aceeași rădăcină pentru pluraluri, articolul hotărât și diacritice (și ş/ţ cu sedilă)
    ("casă", "case", "casa", "casele", "caselor"),
    ("oraș", "orașul", "orașe", "orașele", "orașelor"),
    ("județ", "județul", "județe", "județele", "județelor"),
    ("biserică", "biserica", "biserici", "bisericile", "bisericilor"),
    ("comună", "comuna", "comune", "comunele", "comunelor"),
    ("partid", "partidul", "partide", "partidele", "partidelor"),
    ("sat", "satul", "sate", "satele", "satelor"),
    ("știință", "ştiinţă", "științe", "științele"),
    ("românesc", "românească", "românești"),
    ("naționalitate", "naționalitatea", "naționalități"),
]


@pytest.mark.parametrize("grupa", GRUPE, ids=lambda g: g[0])
def test_radacina_aceeasi_pe_forme(grupa):
    assert len({r.radacina(c) for c in grupa}) == 1


def test_radacina_cazuri_fixe():
    assert sum(len(g) for g in GRUPE) >= 30
    assert r.radacina("casele") == "cas"
    assert r.radacina("lucrează") == "lucr"  # pasul 3 (verb), după consoană
    assert r.radacina("abilități") == "abil"  # pasul 1
    assert r.radacina("orașelor") == "oraș"  # pasul 0 („elor” → „e”), apoi pasul 4
    assert r.radacina("1966") == "1966"
    assert r.radacina("a") == "a"
    assert r.radacina("CASELE") == "cas"


def test_regiunile_si_marcarea():
    assert r._marcheaza("ploaia") == "ploaIa"  # i între vocale = consoană
    assert r.regiuni("beautiful") == (3, 5, 7)
    assert r.regiuni("a") == (1, 1, 1)


def test_interogarea_cu_radacini_pastreaza_operatorii():
    q = '"casele" AND ("orașelor" OR "satele mari" OR "a""b")'
    assert r.interogare_radacini(q) == '"cas" AND ("oraș" OR "sat mar" OR "a""b")'
    assert r.text_radacini("Casele, orașelor!") == "cas oraș"


def test_rrf():
    assert r.rrf([[1, 2, 3], [3, 4]]) == [3, 1, 2, 4]  # 3: 1/63 + 1/61 e primul
    assert r.rrf([[1, 2], [2, 1]]) == [1, 2]  # la egalitate, ordinea primei apariții
    assert r.rrf([]) == []


def test_reordoneaza_doar_primele_si_nenormalizat():
    gasite = [{"rowid": i} for i in range(5)]
    scoruri = {0: (-9.0, 3), 1: (-3.0, 3), 2: (-6.0, 3), 3: (-1.0, 3), 4: (0.0, 3)}
    assert [g["rowid"] for g in r.reordoneaza(gasite, scoruri, cate=3)] == [1, 2, 0, 3, 4]
    assert [g["rowid"] for g in r.reordoneaza(gasite, scoruri, False, cate=3)] == [1, 2, 0, 3, 4]


def test_alege_k3_si_cea_mai_simpla():
    pe = {v: {"k3": {"bune": b}} for v, b in zip(r.VARIANTE_S29, (10, 12, 12, 11))}
    assert r.alege(pe) == "rrf"


def _index(cale, randuri, transforma=lambda t: t):
    con = e3.creeaza(cale)
    con.executemany("INSERT INTO bucati(rowid, text, articol, nr, sursa) VALUES (?, ?, ?, ?, ?)",
                    [(i, transforma(t), a, 0, "wikipedia") for i, (t, a) in enumerate(randuri, 1)])
    con.commit()
    return con


def test_index_radacini_si_cautarea_unita(tmp_path):
    lucru = tmp_path / "e3"
    randuri = [("Orașele mari ale țării sunt multe.", "w0"), ("Orașul Brașov are o cetate veche.", "w1"),
               ("Satele din Brașov sunt mici.", "w2"), ("Se poate referi la Brașov sau la alte orașe.", "w3")]
    _index(lucru / "index.sqlite", randuri).close()
    info = r.cmd_index_radacini(lucru)
    assert info["bucati"] == 4
    with pytest.raises(SystemExit):
        r.cmd_index_radacini(lucru)
    con, con_r = e3.deschide(lucru / "index.sqlite"), e3.deschide(lucru / "index_radacini.sqlite")
    assert con_r.execute("SELECT text FROM bucati WHERE rowid = 2").fetchone()[0] == r.text_radacini(randuri[1][0])
    liste = {"fraze_lista": {"w3"}, "randuri_scurte": set()}
    simpla, unite = r.cauta_rrf(con, con_r, "Ce orașe are Brașov?", "nume_obligatorii_liste", liste)
    assert all(g["text"] in {t for t, _ in randuri} for g in unite)  # textul original, nu rădăcinile
    assert unite[-1]["articol"] == "w3"  # pagina-listă rămâne la urmă și după unire
    assert {g["rowid"] for g in simpla} <= {g["rowid"] for g in unite}


class _Tok:
    def codifica(self, text):
        return [ord(c) % 50 for c in text]


class _Retea:
    """Logits fixe: la fiecare poziție, simbolul curent e cel mai probabil să urmeze (depinde doar de poziția ei)."""

    def __init__(self, torch):
        self.torch = torch

    def eval(self):
        return self

    def __call__(self, x, _):
        logits = self.torch.zeros(x.shape[0], x.shape[1], 50)
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                logits[i, j, int(x[i, j]) % 50] = 5.0  # prezice că se repetă simbolul curent
        return logits


def test_scorurile_judecatorului():
    torch = pytest.importorskip("torch")

    class Model:
        tok, setari, dispozitiv = _Tok(), {"context": 64}, torch.device("cpu")
        retea = _Retea(torch)

    s = r.scoruri_intrebare(Model(), "aa", ["x", "x" * 200])
    assert len(s) == 2 and s[0][1] == s[1][1] == 3  # „ aa” = 3 simboluri, același număr la ambele bucăți
    assert s[0][0] == pytest.approx(s[1][0])  # bucata lungă e tăiată la început; sfârșitul e același
    assert r.scoruri_intrebare(Model(), "aa", []) == []


def _pe(k3_baza, k20_baza, k3, k20):
    return {"s25": {"k3": {"procent": k3_baza}, "k20": {"procent": k20_baza}},
            "rrf_reord": {"k3": {"procent": k3}, "k20": {"procent": k20}}}


def test_verdictul_dupa_pragurile_c21():
    assert r.verdict_s29(_pe(72, 94, 77, 94))["verdict"] == "CONFIRMAT"  # +5, k20 la fel
    assert r.verdict_s29(_pe(72, 94, 77, 93))["verdict"] == "INFIRMAT"  # k20 scade
    assert r.verdict_s29(_pe(72, 94, 76, 95))["verdict"] == "NECLAR"  # +4
    assert r.verdict_s29(_pe(72, 94, 74, 94))["verdict"] == "NECLAR"  # +2
    assert r.verdict_s29(_pe(72, 94, 73, 95))["verdict"] == "INFIRMAT"  # +1
    assert r.verdict_s29(_pe(72, 94, 70, 94))["puncte_k3"] == -2


def test_examenul_o_singura_rulare_si_amprenta(tmp_path):
    import hashlib
    import json

    lucru = tmp_path / "e3"
    randuri = [("Orașul Brașov are o cetate veche din 1400.", "w1"), ("Satele din Brașov sunt mici.", "w2"),
               ("Cluj are o universitate mare.", "w3")]
    _index(lucru / "index.sqlite", randuri).close()
    r.cmd_index_radacini(lucru)
    intrebari = [{"intrebare": "Ce are orașul Brașov?", "raspuns": "o cetate veche", "tip": "text"},
                 {"intrebare": "Ce are Cluj?", "raspuns": "o universitate", "tip": "text"}]
    (lucru / "examen_nou_4096.json").write_text(json.dumps(intrebari, ensure_ascii=False), encoding="utf-8")
    (lucru / "validare_s25.json").write_text(json.dumps({"aleasa": "nume_obligatorii_liste"}), encoding="utf-8")
    (lucru / "validare_s29.json").write_text(json.dumps({"aleasa": "rrf_reord"}), encoding="utf-8")
    (lucru / "liste_s25.json").write_text(json.dumps({"fraze_lista": [], "randuri_scurte": []}), encoding="utf-8")
    sha = hashlib.sha256((lucru / "examen_nou_4096.json").read_bytes()).hexdigest()

    class Model:
        tok = _Tok()

    paznic = []
    argumente = dict(incarca=lambda exp: (Model(), {"id": exp, "linie": "proba"}), paznic=lambda: paznic.append(1),
                     judecator=lambda q, texte: [(-float(len(t)), 1) for t in texte])
    with pytest.raises(SystemExit):
        r.cmd_examen(lucru, 438, sha_examen="altceva", **argumente)
    info = r.cmd_examen(lucru, 438, sha_examen=sha, **argumente)
    assert info["intrebari"] == 2 and info["judecator"] == 438 and paznic == [1]
    assert set(info["variante"]["rrf_reord"]) >= {"k1", "k2", "k3", "k5", "k20", "incap"}
    assert info["variante"]["s25"]["k3"]["bune"] == 2 and info["verdict"] == "INFIRMAT"  # +0 puncte
    assert (lucru / "examen_s29.json").exists()
    with pytest.raises(SystemExit):
        r.cmd_examen(lucru, 438, sha_examen=sha, **argumente)
