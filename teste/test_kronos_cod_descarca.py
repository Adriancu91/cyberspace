"""Unealta de descărcare Kronos-Cod: pilotul (S43a) — licențe, data-limită, filtre, spațiu, reluare, ritm, nimic pe disc —
și modul `complet` (S46a) — reluare fără dubluri, duplicate între surse, FreeBSD, `--limita-ore`, dump-ul crates. FĂRĂ rețea."""

import csv
import hashlib
import io
import json
import socket
import tarfile
import urllib.request
import zipfile
from datetime import datetime, timezone

import pytest

from unelte.kronos_cod import descarca as d

MIT = "MIT License\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software\n"
APACHE = "Apache License\nVersion 2.0, January 2004\nhttp://www.apache.org/licenses/\n"
BSD3 = ("Redistribution and use in source and binary forms, with or without modification, are permitted...\n"
        "Neither the name of the copyright holder nor the names of its contributors may be used\n")
GPL = "GNU GENERAL PUBLIC LICENSE\nVersion 3, 29 June 2007\n"
PY_BUN = "def aduna(a, b):\n    return a + b\n\n\nclass Punct:\n    x = 1\n    y = 2\n"
RS_BUN = "pub fn aduna(a: i32, b: i32) -> i32 {\n    let v = [a, b];\n    v[0] + v[1]\n}\n"
C_BUN = "#include <stdio.h>\n\nint aduna(int a, int b) {\n    return a + b; /* ( */\n}\n"
GB = 1024**3


@pytest.fixture(autouse=True)
def fara_retea(monkeypatch):
    """Orice încercare de conexiune face testul să pice."""
    def interzis(*a, **k):
        raise AssertionError("testul a încercat să deschidă o conexiune")
    monkeypatch.setattr(socket.socket, "connect", interzis)
    monkeypatch.setattr(socket.socket, "connect_ex", interzis)
    monkeypatch.setattr(socket, "create_connection", interzis)
    monkeypatch.setattr(socket, "getaddrinfo", interzis)
    monkeypatch.setattr(urllib.request, "urlopen", interzis)


def tar(fisiere: dict, mtime: float = datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp()) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for nume, text in fisiere.items():
            date = text.encode("utf-8") if isinstance(text, str) else text
            info = tarfile.TarInfo(nume)
            info.size, info.mtime = len(date), mtime
            t.addfile(info, io.BytesIO(date))
    return buf.getvalue()


def zipul(fisiere: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for nume, text in fisiere.items():
            z.writestr(nume, text)
    return buf.getvalue()


class ReteaFalsa:
    """Răspunsuri scrise în test; ține minte fiecare cerere."""

    def __init__(self, raspunsuri: dict):
        self.raspunsuri = raspunsuri
        self.cerute: list[str] = []
        self.cereri = 0
        self.octeti = 0

    def ia(self, url, maxim=d.ARHIVA_MAX):
        self.cerute.append(url)
        self.cereri += 1
        if url not in self.raspunsuri:
            raise d.EroareRetea(url, 404, "lipsește")
        r = self.raspunsuri[url]
        return r if isinstance(r, bytes) else json.dumps(r).encode("utf-8")

    def json(self, url):
        return json.loads(self.ia(url))


def pypi_json(nume, versiuni):
    """versiuni: {versiune: data ISO}; fiecare cu un sdist."""
    return {"releases": {v: [{"packagetype": "sdist", "upload_time_iso_8601": t, "filename": f"{nume}-{v}.tar.gz",
                              "url": f"https://files.pythonhosted.org/{nume}-{v}.tar.gz", "size": 100}]
                         for v, t in versiuni.items()}}


def lume(tmp_path, pypi=None, crates=None, git=None):
    """O lume falsă: listele, metadatele și arhivele. pypi/crates: {nume: (versiuni, clasificatori/licență, fișiere)}."""
    r = {}
    pypi = pypi or {}
    crates = crates or {}
    r[d.LISTA_PYPI] = {"rows": [{"project": n} for n in pypi]}
    r["https://crates.io/api/v1/crates?sort=downloads&per_page=100&page=1"] = {"crates": [{"id": n} for n in crates]}
    r["https://crates.io/api/v1/crates?sort=downloads&per_page=100&page=2"] = {"crates": []}
    for nume, (versiuni, clasif, fisiere) in pypi.items():
        r[f"https://pypi.org/pypi/{nume}/json"] = pypi_json(nume, versiuni)
        for v in versiuni:
            r[f"https://pypi.org/pypi/{nume}/{v}/json"] = {"info": {"classifiers": clasif}}
            r[f"https://files.pythonhosted.org/{nume}-{v}.tar.gz"] = tar({f"{nume}-{v}/{k}": t for k, t in fisiere.items()})
    for nume, (versiuni, licenta, fisiere) in crates.items():
        r[f"https://crates.io/api/v1/crates/{nume}/versions"] = {"versions": [
            {"num": v, "created_at": t, "license": licenta, "yanked": False, "crate_size": 100} for v, t in versiuni.items()]}
        for v in versiuni:
            r[f"https://static.crates.io/crates/{nume}/{nume}-{v}.crate"] = tar({f"{nume}-{v}/{k}": t for k, t in fisiere.items()})
    for depozit in git or []:
        r[f"https://codeload.github.com/{depozit['depozit']}/tar.gz/refs/tags/{depozit['tag']}"] = depozit["arhiva"]
    return ReteaFalsa(r)


def pilot(tmp_path, retea, spatiu=100 * GB):
    return d.Pilot(tmp_path / "pilot", retea=retea, spatiu=lambda p: spatiu, scrie=lambda s: None)


def pachete(tmp_path):
    return {r["cheie"]: r for r in map(json.loads, (tmp_path / "pilot" / "pachete.jsonl").read_text(encoding="utf-8").splitlines())}


VECHI = "2021-03-01T10:00:00Z"
NOU = "2021-07-15T10:00:00Z"
CL_MIT = ["License :: OSI Approved :: MIT License"]


# ---------------------------------------------------------------- licențele


def test_spdx():
    assert d.licente_din_spdx("MIT OR Apache-2.0") == {"MIT", "Apache-2.0"}
    assert d.licente_din_spdx("MIT/Apache-2.0") == {"MIT", "Apache-2.0"}
    assert d.licente_din_spdx("(MIT OR Apache-2.0) AND BSD-3-Clause") == {"MIT", "Apache-2.0", "BSD-3-Clause"}
    assert d.licente_din_spdx("MIT OR GPL-3.0") == {"MIT"}
    assert d.licente_din_spdx("MIT AND GPL-3.0") is None
    assert d.licente_din_spdx("GPL-3.0-only") is None
    assert d.licente_din_spdx("MPL-2.0") is None
    assert d.licente_din_spdx("") is None and d.licente_din_spdx(None) is None


def test_textele_de_licenta_si_potrivirea():
    assert d.licente_din_text(MIT) == ({"MIT"}, set())
    assert d.licente_din_text(APACHE) == ({"Apache-2.0"}, set())
    assert d.licente_din_text(BSD3) == ({"BSD-3-Clause"}, set())
    assert d.licente_din_text("Redistribution and use in source and binary forms, with or without")[0] == {"BSD-2-Clause"}
    assert d.licente_din_text(GPL) == (set(), {"GPL"})
    assert d.se_potrivesc({"BSD"}, {"BSD-3-Clause"}) and d.se_potrivesc({"MIT", "Apache-2.0"}, {"Apache-2.0"})
    assert not d.se_potrivesc({"MIT"}, {"Apache-2.0"})


def test_metadatele_pypi():
    assert d.licente_pypi({"classifiers": CL_MIT}) == ({"MIT"}, "")
    assert d.licente_pypi({"classifiers": CL_MIT + ["License :: OSI Approved :: GNU General Public License v3 (GPLv3)"]})[0] is None
    assert d.licente_pypi({"classifiers": [], "license": "Apache 2.0"}) == ({"Apache-2.0"}, "")
    assert d.licente_pypi({"classifiers": [], "license": ""}) == (None, "metadate_lipsa")
    assert d.licente_pypi({"classifiers": [], "license": "LGPL"})[0] is None


@pytest.mark.parametrize("clasif, fisiere, motiv", [
    (["License :: OSI Approved :: GNU General Public License v3 (GPLv3)"], {"LICENSE": GPL, "a.py": PY_BUN}, "metadate_nepermise"),
    (CL_MIT, {"a.py": PY_BUN}, "fara_fisier_licenta"),
    (CL_MIT, {"LICENSE": MIT, "COPYING": GPL, "a.py": PY_BUN}, "fisier_licenta_nepermisa"),
    (CL_MIT, {"LICENSE": APACHE, "a.py": PY_BUN}, "licente_nepotrivite"),
])
def test_licenta_respinsa(tmp_path, clasif, fisiere, motiv):
    retea = lume(tmp_path, pypi={"p": ({"1.0": VECHI}, clasif, fisiere)})
    pilot(tmp_path, retea).ruleaza(depozite=[], n_pypi=1, n_crates=0)
    rez = pachete(tmp_path)["pypi:p"]
    assert (rez["stare"], rez["motiv"]) == ("respins", motiv)
    assert not (tmp_path / "pilot" / "cod.jsonl").exists() or not (tmp_path / "pilot" / "cod.jsonl").read_text()


def test_crate_cu_licenta_dubla_si_fisierele_ei_intra(tmp_path):
    retea = lume(tmp_path, crates={"c": ({"0.3.0": VECHI}, "MIT OR Apache-2.0",
                                         {"LICENSE-MIT": MIT, "LICENSE-APACHE": APACHE, "src/lib.rs": RS_BUN})})
    pilot(tmp_path, retea).ruleaza(depozite=[], n_pypi=0, n_crates=1)
    rez = pachete(tmp_path)["crates:c"]
    assert rez["stare"] == "pastrat" and rez["pastrate"] == 1
    rand = json.loads((tmp_path / "pilot" / "cod.jsonl").read_text(encoding="utf-8"))
    assert rand["licenta"] == "Apache-2.0 OR MIT" and rand["versiune"] == "0.3.0" and rand["text"] == RS_BUN


def test_crate_gpl_nu_se_descarca(tmp_path):
    retea = lume(tmp_path, crates={"g": ({"1.0.0": VECHI}, "GPL-3.0", {"LICENSE": GPL, "src/lib.rs": RS_BUN})})
    pilot(tmp_path, retea).ruleaza(depozite=[], n_pypi=0, n_crates=1)
    assert pachete(tmp_path)["crates:g"]["motiv"] == "metadate_nepermise"
    assert not any(u.endswith(".crate") for u in retea.cerute)


# ---------------------------------------------------------------- data-limită


def test_pypi_alege_ultima_versiune_dinainte_de_data(tmp_path):
    retea = lume(tmp_path, pypi={"p": ({"1.0": "2020-01-01T00:00:00Z", "1.1": "2021-06-28T23:59:00Z", "2.0": NOU,
                                        "1.2rc1": "2021-06-01T00:00:00Z"}, CL_MIT, {"LICENSE": MIT, "a.py": PY_BUN})})
    pilot(tmp_path, retea).ruleaza(depozite=[], n_pypi=1, n_crates=0)
    assert pachete(tmp_path)["pypi:p"]["versiune"] == "1.1"
    assert "https://files.pythonhosted.org/p-2.0.tar.gz" not in retea.cerute


def test_versiunea_de_pe_29_iunie_2021_si_de_dupa_e_respinsa(tmp_path):
    retea = lume(tmp_path, pypi={"p": ({"3.0": "2021-06-29T00:00:00Z", "4.0": NOU}, CL_MIT, {"LICENSE": MIT, "a.py": PY_BUN})},
                 crates={"c": ({"1.0.0": NOU}, "MIT", {"LICENSE": MIT, "src/lib.rs": RS_BUN})})
    pilot(tmp_path, retea).ruleaza(depozite=[], n_pypi=1, n_crates=1)
    p = pachete(tmp_path)
    assert p["pypi:p"]["motiv"] == p["crates:c"]["motiv"] == "fara_versiune_inainte_de_data"
    assert not any(u.endswith((".tar.gz", ".crate")) for u in retea.cerute)


def test_depozitul_git_cu_fisiere_de_dupa_data_e_respins(tmp_path):
    nou = datetime(2021, 8, 1, tzinfo=timezone.utc).timestamp()
    dep = [{"nume": "x", "depozit": "o/x", "tag": "v1", "licenta": "MIT", "limbaj": "c",
            "arhiva": tar({"x-1/LICENSE": MIT, "x-1/a.c": C_BUN}, mtime=nou)},
           {"nume": "y", "depozit": "o/y", "tag": "v1", "licenta": "MIT", "limbaj": "c",
            "arhiva": tar({"y-1/LICENSE": MIT, "y-1/b.c": C_BUN.replace("aduna", "scade")})}]
    retea = lume(tmp_path, git=dep)
    pilot(tmp_path, retea).ruleaza(depozite=dep, n_pypi=0, n_crates=0)
    p = pachete(tmp_path)
    assert p["git:x"]["motiv"] == "dupa_data_limita"
    assert p["git:y"]["stare"] == "pastrat"


# ---------------------------------------------------------------- filtrele


@pytest.mark.parametrize("cale, text, filtru", [
    ("p/README.md", "text", "extensie"),
    ("p/_vendor/six.py", PY_BUN, "copiat"),
    ("p/third_party/x.c", C_BUN, "copiat"),
    ("p/proto/a_pb2.py", PY_BUN, "generat_nume"),
    ("p/app/migrations/0001_initial.py", PY_BUN, "generat_nume"),
    ("p/parsetab.py", PY_BUN, "generat_nume"),
    ("p/mare.py", "x = 1\n" * 200_000, "prea_mare"),
    ("p/latin.py", "# caf\xe9\n".encode("latin-1"), "utf8"),
    ("p/gen.py", "# Code generated by protoc. DO NOT EDIT.\n" + PY_BUN, "generat_antet"),
    ("p/ext.c", "/* Generated by Cython 0.29 */\n" + C_BUN, "generat_antet"),
    ("p/gpl.c", "/* SPDX-License-Identifier: GPL-2.0 */\n" + C_BUN, "licenta_fisier"),
    ("p/gpl2.py", "# This program is free software; under the GNU General Public License\n" + PY_BUN, "licenta_fisier"),
    ("p/lung.py", "x = '" + "a" * 1200 + "'\n", "rand_lung"),
    ("p/mediu.py", ("y = '" + "b" * 150 + "'\n") * 5, "rand_mediu"),
    ("p/simboluri.py", "x = [" + "{}, " * 20 + "]\n" + ("# " + "-" * 60 + "\n") * 10, "alfanumeric"),
    ("p/tests/fixtures/date.py", "D = [\n" + "".join(f"    '{i:04d}', {i},\n" for i in range(200)) + "]\n", "date_test"),
    ("p/rau.py", "def f(:\n    pass\n", "sintaxa"),
    ("p/rau.rs", "fn f() { let v = [1, 2; }\n", "sintaxa"),
    ("p/rau.c", "int f(void) { return (1; }\n", "sintaxa"),
], ids=lambda x: x if isinstance(x, str) and len(x) < 40 and "\n" not in x else "_")
def test_filtrele(cale, text, filtru):
    date = text if isinstance(text, bytes) else text.encode("utf-8")
    assert d.filtreaza(cale, date) == (None, filtru)


@pytest.mark.parametrize("cale, text", [("p/a.py", PY_BUN), ("p/lib.rs", RS_BUN), ("p/a.c", C_BUN), ("p/a.h", C_BUN),
                                        ("p/spdx.rs", "// SPDX-License-Identifier: MIT OR Apache-2.0\n" + RS_BUN),
                                        ("p/tests/fixtures/conf.py", PY_BUN),
                                        ("p/viata.rs", "fn f<'a>(x: &'a str) -> char { let c = '}'; c }\n")],
                         ids=lambda x: x if "\n" not in x else "_")
def test_codul_bun_trece(cale, text):
    assert d.filtreaza(cale, text.encode("utf-8")) == (text, None)


def test_duplicatele_exacte_dupa_normalizare_si_ordinea_surselor(tmp_path):
    copie = PY_BUN.replace("\n", "   \r\n") + "\r\n\r\n"
    dep = [{"nume": "mare", "depozit": "o/mare", "tag": "v1", "licenta": "MIT", "limbaj": "python",
            "arhiva": tar({"mare-1/LICENSE": MIT, "mare-1/a.py": PY_BUN})}]
    retea = lume(tmp_path, git=dep, pypi={"p": ({"1.0": VECHI}, CL_MIT, {"LICENSE": MIT, "b.py": copie})})
    rez = pilot(tmp_path, retea).ruleaza(depozite=dep, n_pypi=1, n_crates=0)
    p = pachete(tmp_path)
    assert p["git:mare"]["pastrate"] == 1
    assert p["pypi:p"]["pastrate"] == 0 and p["pypi:p"]["aruncate"] == {"duplicat_exact": 1}
    assert rez["aruncate_fisiere"]["duplicat_exact"] == 1


def test_aproape_duplicatele_pastreaza_cel_mai_lung():
    baza = "\n".join(f"def functia_{i}(a, b):\n    return a * {i} + b - {i * 7}\n" for i in range(60))
    aproape = baza + "\n# un comentariu in plus\n"
    altul = "\n".join(f"class Clasa{i}:\n    nume = 'x{i}'\n    def metoda(self):\n        return self.nume * {i}\n"
                      for i in range(60))
    assert d.aproape_duplicate([baza, aproape, altul]) == [0]
    assert d.aproape_duplicate([baza, altul]) == []


def test_arhivele_zip_merg_si_ele():
    z = zipul({"p-1/LICENSE": MIT, "p-1/a.py": PY_BUN, "p-1/poza.png": b"\x89PNG"})
    assert [(c, len(x)) for c, x, _, _ in d.fisiere_din_arhiva(z, "p-1.zip")] == [("p-1/LICENSE", len(MIT)),
                                                                                  ("p-1/a.py", len(PY_BUN))]


# ---------------------------------------------------------------- spațiul, reluarea, ritmul, discul


def test_se_opreste_sub_40_gb_fara_sa_descarce(tmp_path):
    retea = lume(tmp_path, pypi={"p": ({"1.0": VECHI}, CL_MIT, {"LICENSE": MIT, "a.py": PY_BUN})})
    rez = pilot(tmp_path, retea, spatiu=39 * GB).ruleaza(depozite=[], n_pypi=1, n_crates=0)
    assert "oprit" in rez and "40 GB" in rez["oprit"]
    assert not any(u.endswith(".tar.gz") for u in retea.cerute)
    assert rez["pachete"] == 0


def test_spatiul_se_verifica_inainte_de_fiecare_pachet(tmp_path):
    retea = lume(tmp_path, pypi={n: ({"1.0": VECHI}, CL_MIT, {"LICENSE": MIT, f"{n}.py": PY_BUN.replace("aduna", n)})
                                 for n in ("a", "b", "c")})
    ramas = iter([50 * GB, 50 * GB, 39 * GB])
    p = d.Pilot(tmp_path / "pilot", retea=retea, spatiu=lambda _: next(ramas), scrie=lambda s: None)
    rez = p.ruleaza(depozite=[], n_pypi=3, n_crates=0)
    assert "oprit" in rez and set(pachete(tmp_path)) == {"pypi:a", "pypi:b"}


def test_reluarea_de_unde_a_ramas(tmp_path):
    lumea = {n: ({"1.0": VECHI}, CL_MIT, {"LICENSE": MIT, f"{n}.py": PY_BUN.replace("aduna", n)}) for n in ("a", "b", "c")}
    ramas = iter([50 * GB, 50 * GB, 39 * GB])
    retea = lume(tmp_path, pypi=lumea)
    d.Pilot(tmp_path / "pilot", retea=retea, spatiu=lambda _: next(ramas), scrie=lambda s: None).ruleaza(
        depozite=[], n_pypi=3, n_crates=0)
    # o cădere la jumătatea unui pachet: rânduri scrise în cod.jsonl, fără rândul din pachete.jsonl
    cod = tmp_path / "pilot" / "cod.jsonl"
    marime = cod.stat().st_size
    with open(cod, "a", encoding="utf-8") as f:
        f.write(json.dumps({"sha256": "jumatate", "text": "x"}) + "\n")
    retea2 = lume(tmp_path, pypi=lumea)
    p = pilot(tmp_path, retea2)
    assert cod.stat().st_size == marime and "jumatate" not in p.hashuri
    rez = p.ruleaza(depozite=[], n_pypi=3, n_crates=0)
    assert [u for u in retea2.cerute if "files.pythonhosted" in u] == ["https://files.pythonhosted.org/c-1.0.tar.gz"]
    assert rez["fisiere_curat"] == 3 and len(cod.read_text(encoding="utf-8").splitlines()) == 3


def test_ritmul_cererilor():
    ceas = [0.0]
    dormit = []

    def doarme(s):
        dormit.append(round(s, 3))
        ceas[0] += s

    r = d.Ritm({"crates.io": 1.0, "pypi.org": 5.0}, ceas=lambda: ceas[0], doarme=doarme)
    for _ in range(3):
        r.asteapta("crates.io")
    assert dormit == [1.0, 1.0]
    dormit.clear()
    for _ in range(3):
        r.asteapta("pypi.org")
    assert dormit == [0.2, 0.2]
    ceas[0] += 5
    r.asteapta("crates.io")
    assert dormit == [0.2, 0.2]


def test_reteaua_trimite_user_agent_si_respecta_ritmul():
    vazute = []

    class Raspuns:
        headers = {"Content-Length": "2"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self, n):
            return b"{}"

    def deschide(cerere, timeout):
        vazute.append((cerere.full_url, cerere.get_header("User-agent")))
        return Raspuns()

    ceas, dormit = [0.0], []
    ritm = d.Ritm(d.RITM, ceas=lambda: ceas[0], doarme=lambda s: (dormit.append(s), ceas.__setitem__(0, ceas[0] + s)))
    retea = d.Retea(ritm=ritm, deschide=deschide)
    for _ in range(3):
        assert retea.json("https://crates.io/api/v1/crates/x/versions") == {}
    assert all(ua == d.USER_AGENT and "Kronos" in ua for _, ua in vazute)
    assert dormit == [1.0, 1.0]


def test_nu_scrie_arhive_pe_disc(tmp_path, monkeypatch):
    scrise = []
    deschide_vechi = open

    def open_spion(fisier, mod="r", *a, **k):
        if any(c in mod for c in "wax+"):
            scrise.append(str(fisier))
        return deschide_vechi(fisier, mod, *a, **k)

    monkeypatch.setattr("builtins.open", open_spion)
    retea = lume(tmp_path, pypi={"p": ({"1.0": VECHI}, CL_MIT, {"LICENSE": MIT, "a.py": PY_BUN})},
                 crates={"c": ({"1.0.0": VECHI}, "MIT", {"LICENSE": MIT, "src/lib.rs": RS_BUN})})
    pilot(tmp_path, retea).ruleaza(depozite=[], n_pypi=1, n_crates=1)
    pe_disc = {f.name for f in (tmp_path / "pilot").rglob("*") if f.is_file()}
    assert pe_disc <= {"cod.jsonl", "pachete.jsonl", "lista_pypi.json", "lista_crates.json", "rezumat.json",
                       "aproape_duplicate.json"}
    assert not any(s.endswith((".tar.gz", ".crate", ".zip", ".tar")) for s in scrise)
    for f in (tmp_path / "pilot").rglob("*"):
        if f.is_file():
            assert not f.read_bytes().startswith((b"\x1f\x8b", b"PK\x03\x04"))


def test_rezumatul_are_cifrele_cerute(tmp_path):
    retea = lume(tmp_path, pypi={"p": ({"1.0": VECHI}, CL_MIT, {"LICENSE": MIT, "a.py": PY_BUN, "_vendor/v.py": PY_BUN}),
                                 "g": ({"1.0": VECHI}, ["License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
                                       {"LICENSE": GPL, "a.py": PY_BUN})})
    rez = pilot(tmp_path, retea).ruleaza(depozite=[], n_pypi=2, n_crates=0)
    for cheie in ("gb_arhive_descarcate", "gb_cod_brut", "gb_curat", "fisiere_cod_brut", "fisiere_curat",
                  "simboluri_estimate", "aruncate_fisiere", "aruncate_procent_din_brut", "pachete_respinse", "pe_sursa"):
        assert cheie in rez
    assert rez["fisiere_cod_brut"] == 2 and rez["fisiere_curat"] == 1
    assert rez["aruncate_fisiere"]["copiat"] == 1
    assert rez["pachete_respinse"] == {"metadate_nepermise": 1}
    assert rez["simboluri_estimate"] == round(len(PY_BUN) / d.OCTETI_PE_SIMBOL)
    assert json.loads((tmp_path / "pilot" / "rezumat.json").read_text(encoding="utf-8"))["fisiere_curat"] == 1


# ================================================================ modul `complet` (S46a)


def test_pilotul_da_exact_aceleasi_rezultate_ca_inainte(tmp_path):
    """Amprenta ieșirii pilotului pe o lume falsă, luată cu codul de dinainte de S46a (e650232)."""
    baza = "\n".join(f"def functia_{i}(a, b):\n    return a * {i} + b - {i * 7}\n" for i in range(60))
    dep = [{"nume": "mare", "depozit": "o/mare", "tag": "v1", "licenta": "MIT", "limbaj": "python",
            "arhiva": tar({"mare-1/LICENSE": MIT, "mare-1/a.py": PY_BUN, "mare-1/b.py": baza})}]
    retea = lume(tmp_path, git=dep,
                 pypi={"p": ({"1.0": VECHI, "2.0": NOU}, CL_MIT, {"LICENSE": MIT, "x.py": PY_BUN, "y.py": baza + "\n# in plus\n",
                                                                 "_vendor/v.py": PY_BUN, "rau.py": "def f(:\n"}),
                       "g": ({"1.0": VECHI}, ["License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
                             {"LICENSE": GPL, "a.py": PY_BUN})},
                 crates={"c": ({"0.3.0": VECHI}, "MIT OR Apache-2.0", {"LICENSE-MIT": MIT, "src/lib.rs": RS_BUN,
                                                                       "src/gen.rs": "// @generated\n" + RS_BUN}),
                         "n": ({"1.0.0": NOU}, "MIT", {"LICENSE": MIT, "src/lib.rs": RS_BUN})})
    rez = pilot(tmp_path, retea).ruleaza(depozite=dep, n_pypi=2, n_crates=2)
    rez.pop("secunde_rularea_asta")
    h = hashlib.sha256()
    for f in ("pachete.jsonl", "cod.jsonl", "aproape_duplicate.json"):
        h.update((tmp_path / "pilot" / f).read_bytes())
    h.update(json.dumps(rez, sort_keys=True).encode())
    assert h.hexdigest() == "a587f7157791685b93ec6a187d3a880f3cf18e3b32622e05622dcedea7884aa7"


def dump_tar(tabele: dict) -> bytes:
    """Un `db-dump.tar.gz` fals: {nume.csv: [rânduri dict]}, sub `<data>/data/`, ca dump-ul crates.io."""
    fisiere = {}
    for nume, randuri in tabele.items():
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=list(randuri[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(randuri)
        fisiere[f"2026-10-29-020000/data/{nume}"] = buf.getvalue()
    fisiere["2026-10-29-020000/README.md"] = "dump"
    return tar(fisiere)


def _data_csv(iso: str) -> str:
    return iso.replace("T", " ").replace("Z", ".123456+00")


def lume_completa(tmp_path, git=None, pypi=None, crates=None):
    """Ca `lume`, plus dump-ul crates.io; ordinea din `crates` = cele mai descărcate întâi."""
    retea = lume(tmp_path, pypi=pypi, git=git)
    crates = crates or {}
    randuri_c, randuri_d, randuri_v = [], [], []
    for i, (nume, (versiuni, licenta, fisiere)) in enumerate(crates.items()):
        randuri_c.append({"id": str(i + 1), "name": nume, "readme": "x" * 10})
        randuri_d.append({"crate_id": str(i + 1), "downloads": str(1000 - i)})
        for v, t in versiuni.items():
            randuri_v.append({"id": str(len(randuri_v) + 1), "crate_id": str(i + 1), "num": v, "created_at": _data_csv(t),
                              "yanked": "f", "license": licenta, "crate_size": "100", "downloads": "5"})
            retea.raspunsuri[f"https://static.crates.io/crates/{nume}/{nume}-{v}.crate"] = tar(
                {f"{nume}-{v}/{k}": x for k, x in fisiere.items()})
    if crates:
        retea.raspunsuri[d.DUMP_CRATES] = dump_tar({"crates.csv": randuri_c, "crate_downloads.csv": randuri_d,
                                                    "versions.csv": randuri_v})
    return retea


def complet(tmp_path, retea, spatiu=100 * GB, ceas=None, dosar="complet"):
    return d.Pilot(tmp_path / dosar, retea=retea, spatiu=lambda p: spatiu, scrie=lambda s: None,
                   **({"ceas": ceas} if ceas else {}))


def pachete_din(dosar):
    return [json.loads(r) for r in (dosar / "pachete.jsonl").read_text(encoding="utf-8").splitlines()]


def depozit(nume, fisiere, sursa="git_py", licenta="MIT", **opt):
    return {"sursa": sursa, "nume": nume, "depozit": f"o/{nume}", "tag": "v1", "licenta": licenta,
            "arhiva": tar({f"{nume}-1/{k}": x for k, x in fisiere.items()}), **opt}


def test_lista_depozitelor_complete_urmeaza_surse_md():
    surse = [x["sursa"] for x in d.DEPOZITE_COMPLET]
    # rândurile 3, 4, 5, 6 din SURSE.md, în ordine (depozitele mari întâi)
    assert surse == sorted(surse, key=["git_py", "git_rs", "freebsd", "git_c"].index)
    nume = {x["nume"] for x in d.DEPOZITE_COMPLET}
    assert {"numpy", "pytorch", "django", "rust", "tokio", "ripgrep", "freebsd", "libuv", "redis", "zstd", "lz4"} <= nume
    assert len(nume) == len(d.DEPOZITE_COMPLET) == 39
    for x in d.DEPOZITE_COMPLET:
        assert d.licente_din_spdx(x["licenta"]), x["nume"]
        assert x["tag"] and x["arhiva_max"] == d.ARHIVA_MAX_DEPOZIT
    fb = next(x for x in d.DEPOZITE_COMPLET if x["nume"] == "freebsd")
    assert fb["tag"] == "release/13.0.0" and fb["licenta_pe_fisier"] and set(fb["fara_dosare"]) == {"contrib", "gnu"}


def test_dump_crates_alege_ultima_versiune_buna_si_ordoneaza_dupa_descarcari():
    def v(i, c, num, t, yanked="f"):
        return {"id": str(i), "crate_id": c, "num": num, "created_at": t, "yanked": yanked, "license": "MIT",
                "crate_size": "7", "downloads": "1"}

    date = dump_tar({
        "crates.csv": [{"id": "1", "name": "mic"}, {"id": "2", "name": "mare"}, {"id": "3", "name": "nou"}],
        "crate_downloads.csv": [{"crate_id": "1", "downloads": "10"}, {"crate_id": "2", "downloads": "999"},
                                {"crate_id": "3", "downloads": "5000"}],
        "versions.csv": [v(1, "1", "0.1.0", "2020-01-01 00:00:00+00"), v(2, "1", "0.2.0", "2021-06-28 23:59:59.9+00"),
                         v(3, "1", "0.3.0", "2021-06-29 00:00:00+00"), v(4, "2", "1.0.0", "2021-01-01 00:00:00+00"),
                         v(5, "2", "1.1.0", "2021-02-01 00:00:00+00", yanked="t"),
                         v(6, "2", "1.2.0-beta.1", "2021-03-01 00:00:00+00"), v(7, "3", "1.0.0", "2022-01-01 00:00:00+00")],
    })
    info = d.citeste_dump_crates(date)
    assert info["total_crates"] == 3 and info["fara_versiune_inainte_de_data"] == 1
    assert [(e["nume"], e["num"]) for e in info["crates"]] == [("mare", "1.0.0"), ("mic", "0.2.0")]
    assert info["crates"][0]["license"] == "MIT" and info["crates"][0]["crate_size"] == 7


def test_dump_vechi_cu_descarcarile_in_crates_csv():
    date = dump_tar({"crates.csv": [{"id": "1", "name": "a", "downloads": "1"}, {"id": "2", "name": "b", "downloads": "9"}],
                     "versions.csv": [{"crate_id": c, "num": "1.0.0", "created_at": "2021-01-01 00:00:00", "yanked": "false",
                                       "license": "MIT", "crate_size": ""} for c in ("1", "2")]})
    assert [e["nume"] for e in d.citeste_dump_crates(date)["crates"]] == ["b", "a"]


def test_complet_ordinea_surselor_si_duplicatele_intre_surse(tmp_path):
    copie_py = PY_BUN.replace("\n", "  \r\n")
    dep = [depozit("mare", {"LICENSE": MIT, "a.py": PY_BUN}),
           depozit("rs", {"LICENSE": MIT, "src/lib.rs": RS_BUN}, sursa="git_rs")]
    retea = lume_completa(tmp_path, git=dep,
                          pypi={"p": ({"1.0": VECHI}, CL_MIT, {"LICENSE": MIT, "a.py": copie_py,
                                                               "b.py": "import os\n\nVALOARE = os.sep\n"})},
                          crates={"c1": ({"0.1.0": VECHI, "0.2.0": NOU}, "MIT OR Apache-2.0",
                                         {"LICENSE-MIT": MIT, "src/lib.rs": RS_BUN,
                                          "src/x.rs": "pub struct Punct {\n    pub x: f64,\n}\n"}),
                                  "c2": ({"1.0.0": NOU}, "MIT", {"LICENSE": MIT, "src/lib.rs": RS_BUN})})
    rez = complet(tmp_path, retea).ruleaza_complet(depozite=dep, n_pypi=10)
    p = pachete_din(tmp_path / "complet")
    assert [x["cheie"] for x in p] == ["git_py:mare", "git_rs:rs", "pypi:p", "crates:c1"]
    assert p[2]["aruncate"] == {"duplicat_exact": 1} and p[2]["pastrate"] == 1
    assert p[3]["versiune"] == "0.1.0" and p[3]["aruncate"] == {"duplicat_exact": 1} and p[3]["pastrate"] == 1
    assert rez["terminat"] and "oprit" not in rez and rez["fisiere_curat"] == 4
    assert set(rez["pe_sursa"]) == {"git_py", "git_rs", "pypi", "crates"}
    assert rez["crates_din_dump"] == {"total": 2, "cu_versiune_inainte_de_data": 1, "fara_versiune_inainte_de_data": 1}
    assert rez["pypi_in_lista"] == 1 and "aproape_duplicat" in rez["aruncate_fisiere"]
    # crate-urile vin din dump: nicio cerere la API-ul crates.io, o singură cerere pentru dump
    assert not any("crates.io/api" in u for u in retea.cerute) and retea.cerute.count(d.DUMP_CRATES) == 1
    assert "https://static.crates.io/crates/c2/c2-1.0.0.crate" not in retea.cerute


ANTET_FB = "/*-\n * SPDX-License-Identifier: BSD-2-Clause-FreeBSD\n *\n * Copyright (c) 2003 Cineva\n */\n"


def test_freebsd_doar_fisierele_cu_antet_bsd_fara_contrib_si_gnu(tmp_path):
    fb = depozit("freebsd", {
        "COPYRIGHT": "# FreeBSD\n" + GPL,
        "sys/kern/a.c": ANTET_FB + C_BUN,
        "bin/b.c": "/* SPDX-License-Identifier: BSD-3-Clause */\n" + C_BUN.replace("aduna", "b"),
        "bin/fara.c": C_BUN.replace("aduna", "fara"),
        "lib/isc.c": "/* SPDX-License-Identifier: ISC */\n" + C_BUN.replace("aduna", "isc"),
        "lib/mit.c": "/* SPDX-License-Identifier: MIT */\n" + C_BUN.replace("aduna", "mit"),
        "contrib/llvm/x.c": ANTET_FB + C_BUN.replace("aduna", "x"),
        "sys/contrib/y.c": ANTET_FB + C_BUN.replace("aduna", "y"),
        "gnu/z.c": ANTET_FB + C_BUN.replace("aduna", "z"),
        "sys/gnu/w.h": ANTET_FB + C_BUN.replace("aduna", "w"),
    }, sursa="freebsd", licenta="BSD-2-Clause OR BSD-3-Clause", licenta_pe_fisier=True, fara_dosare=["contrib", "gnu"])
    retea = lume_completa(tmp_path, git=[fb])
    rez = complet(tmp_path, retea).ruleaza_complet(depozite=[fb], n_pypi=0, n_crates=0)
    p = pachete_din(tmp_path / "complet")[0]
    assert p["stare"] == "pastrat" and p["fisiere_cod_brut"] == 5  # contrib/ și gnu/ nici nu se citesc
    assert p["pastrate"] == 2 and p["aruncate"] == {"antet_bsd": 2, "licenta_fisier": 1}
    randuri = [json.loads(r) for r in (tmp_path / "complet" / "cod.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {(r["cale"].split("/", 1)[1], r["licenta"]) for r in randuri} == {("sys/kern/a.c", "BSD-2-Clause"),
                                                                             ("bin/b.c", "BSD-3-Clause")}
    assert rez["pe_sursa"]["freebsd"]["fisiere_curat"] == 2
    # la pilot (fără `licenta_pe_fisier`) antetul `BSD-2-Clause-FreeBSD` rămâne necunoscut, ca înainte
    assert d.filtreaza("p/a.c", (ANTET_FB + C_BUN).encode()) == (None, "licenta_fisier")


def test_optiunile_depozitelor_lz4_zstd_redis(tmp_path):
    bsd2 = "Redistribution and use in source and binary forms, with or without modification\n"
    lz4 = depozit("lz4", {"LICENSE": "lib: BSD 2-Clause; restul: GPLv2\n", "lib/LICENSE": bsd2, "lib/lz4.c": C_BUN,
                          "programs/lz4cli.c": C_BUN.replace("aduna", "cli")}, sursa="git_c", licenta="BSD-2-Clause",
                  dosar="lib")
    zstd = depozit("zstd", {"LICENSE": BSD3, "COPYING": GPL, "lib/zstd.c": C_BUN.replace("aduna", "z")}, sursa="git_c",
                   licenta="BSD-3-Clause", fisiere_licenta=["LICENSE"])
    zstd_fara = depozit("zstd2", {"LICENSE": BSD3, "COPYING": GPL, "lib/zstd.c": C_BUN.replace("aduna", "z2")},
                        sursa="git_c", licenta="BSD-3-Clause")
    redis = depozit("redis", {"COPYING": BSD3, "src/server.c": C_BUN.replace("aduna", "srv"),
                              "deps/lua/src/lapi.c": C_BUN.replace("aduna", "lua")}, sursa="git_c", licenta="BSD-3-Clause",
                    fara_dosare=["deps"])
    dep = [lz4, zstd, zstd_fara, redis]
    complet(tmp_path, lume_completa(tmp_path, git=dep)).ruleaza_complet(depozite=dep, n_pypi=0, n_crates=0)
    p = {x["pachet"]: x for x in pachete_din(tmp_path / "complet")}
    assert p["lz4"]["stare"] == "pastrat" and p["lz4"]["fisiere_cod_brut"] == 1 and p["lz4"]["pastrate"] == 1
    assert p["zstd"]["stare"] == "pastrat" and p["zstd"]["pastrate"] == 1
    assert p["zstd2"]["motiv"] == "fisier_licenta_nepermisa"
    assert p["redis"]["stare"] == "pastrat" and p["redis"]["fisiere_cod_brut"] == 1


class Ceas:
    """Timp simulat: fiecare cerere la rețea „durează” `pas` secunde."""

    def __init__(self, pas):
        self.t, self.pas = 0.0, pas

    def __call__(self):
        return self.t


class ReteaCuCeas(ReteaFalsa):
    def __init__(self, raspunsuri, ceas):
        super().__init__(raspunsuri)
        self.ceas = ceas

    def ia(self, url, maxim=d.ARHIVA_MAX):
        self.ceas.t += self.ceas.pas
        return super().ia(url, maxim)


def _lumea_mare(tmp_path, n_crates=6):
    dep = [depozit(f"g{i}", {"LICENSE": MIT, "a.py": PY_BUN.replace("aduna", f"g{i}")}) for i in range(3)]
    pypi = {f"p{i}": ({"1.0": VECHI}, CL_MIT, {"LICENSE": MIT, "a.py": PY_BUN.replace("aduna", f"p{i}"),
                                                "dublu.py": PY_BUN.replace("aduna", "comun")}) for i in range(6)}
    crates = {f"c{i}": ({"1.0.0": VECHI}, "MIT", {"LICENSE": MIT, "src/lib.rs": RS_BUN.replace("aduna", f"c{i}")})
              for i in range(n_crates)}
    return dep, lume_completa(tmp_path, git=dep, pypi=pypi, crates=crates).raspunsuri


def test_limita_ore_opreste_curat_si_reluarea_nu_dubleaza_nimic(tmp_path):
    dep, raspunsuri = _lumea_mare(tmp_path)
    # o rulare dintr-o bucată, ca reper
    complet(tmp_path, ReteaFalsa(raspunsuri), dosar="intreg").ruleaza_complet(depozite=dep, n_pypi=10)
    # aceeași descărcare, pe „nopți” de câte 1 oră; fiecare cerere durează 10 minute
    ceas = Ceas(600)
    nopti, cerute = [], []
    for _ in range(20):
        retea = ReteaCuCeas(raspunsuri, ceas)
        rez = complet(tmp_path, retea, ceas=ceas, dosar="bucati").ruleaza_complet(depozite=dep, n_pypi=10, limita_ore=1)
        nopti.append(rez)
        cerute += retea.cerute
        if rez["terminat"]:
            break
    assert len(nopti) > 3 and all("--limita-ore" in r["oprit"] and not r["terminat"] for r in nopti[:-1])
    assert all("aproape_duplicat" not in r["aruncate_fisiere"] for r in nopti[:-1])
    assert json.loads((tmp_path / "bucati" / "rezumat.json").read_text(encoding="utf-8"))["terminat"]
    for f in ("cod.jsonl", "pachete.jsonl", "aproape_duplicate.json"):
        assert (tmp_path / "bucati" / f).read_bytes() == (tmp_path / "intreg" / f).read_bytes(), f
    chei = [x["cheie"] for x in pachete_din(tmp_path / "bucati")]
    assert len(chei) == len(set(chei)) == 15
    arhive = [u for u in cerute if u.endswith((".tar.gz", ".crate")) or "/tags/" in u]
    assert len(arhive) == len(set(arhive))  # nicio arhivă descărcată de două ori
    assert cerute.count(d.DUMP_CRATES) == 1 and cerute.count(d.LISTA_PYPI) == 1


def test_complet_se_opreste_sub_40_gb(tmp_path):
    dep, raspunsuri = _lumea_mare(tmp_path)
    retea = ReteaFalsa(raspunsuri)
    rez = complet(tmp_path, retea, spatiu=39 * GB).ruleaza_complet(depozite=dep, n_pypi=10)
    assert "40 GB" in rez["oprit"] and not rez["terminat"] and rez["pachete"] == 0 and retea.cerute == []


class ReteaCazuta(ReteaFalsa):
    """Arhivele .crate dau „timed out” (eroare trecătoare)."""

    def ia(self, url, maxim=d.ARHIVA_MAX):
        if url.endswith(".crate"):
            self.cerute.append(url)
            raise d.EroareRetea(url, None, "timed out")
        return super().ia(url, maxim)


def test_reteaua_cazuta_opreste_dupa_10_erori_la_rand_fara_sa_inchida_pachetele(tmp_path):
    dep, raspunsuri = _lumea_mare(tmp_path, n_crates=12)
    retea = ReteaCazuta(raspunsuri)
    rez = complet(tmp_path, retea).ruleaza_complet(depozite=dep, n_pypi=10)
    assert "10 erori de rețea la rând" in rez["oprit"] and not rez["terminat"]
    assert sum(u.endswith(".crate") for u in retea.cerute) == 10
    assert not any(x["sursa"] == "crates" for x in pachete_din(tmp_path / "complet"))
    rez2 = complet(tmp_path, ReteaFalsa(raspunsuri)).ruleaza_complet(depozite=dep, n_pypi=10)
    assert rez2["terminat"] and rez2["pe_sursa"]["crates"]["pastrate"] == 12


def test_cateva_erori_de_retea_lasa_descarcarea_neterminata(tmp_path):
    dep, raspunsuri = _lumea_mare(tmp_path, n_crates=3)
    rez = complet(tmp_path, ReteaCazuta(raspunsuri)).ruleaza_complet(depozite=dep, n_pypi=10)
    assert not rez["terminat"] and "3 pachete amânate" in rez["oprit"]
    assert "aproape_duplicat" not in rez["aruncate_fisiere"]
    rez2 = complet(tmp_path, ReteaFalsa(raspunsuri)).ruleaza_complet(depozite=dep, n_pypi=10)
    assert rez2["terminat"] and "oprit" not in rez2 and rez2["pe_sursa"]["crates"]["pastrate"] == 3


def test_complet_inchide_pachetele_lipsa_si_erorile_neasteptate(tmp_path, monkeypatch):
    dep = [depozit("lipsa", {"LICENSE": MIT, "a.py": PY_BUN}), depozit("bun", {"LICENSE": MIT, "a.py": PY_BUN})]
    retea = lume_completa(tmp_path, git=dep[1:])
    vechi = d.Pilot.proceseaza

    def proceseaza(self, sursa, nume, *a, **k):
        if nume == "bun":
            raise KeyError("ciudat")
        return vechi(self, sursa, nume, *a, **k)

    monkeypatch.setattr(d.Pilot, "proceseaza", proceseaza)
    rez = complet(tmp_path, retea).ruleaza_complet(depozite=dep, n_pypi=0, n_crates=0)
    p = {x["pachet"]: x for x in pachete_din(tmp_path / "complet")}
    assert p["lipsa"]["motiv"] == "retea" and "404" in p["lipsa"]["detaliu"]
    assert p["bun"]["motiv"] == "eroare" and "KeyError" in p["bun"]["detaliu"]
    assert rez["terminat"]
    # la pilot, o eroare neașteptată oprește tot (ca înainte)
    with pytest.raises(KeyError):
        pilot(tmp_path, lume(tmp_path, git=dep[1:])).ruleaza(depozite=dep[1:], n_pypi=0, n_crates=0)


def test_comanda_complet_implicit(monkeypatch):
    vazut = {}

    class PilotFals:
        def __init__(self, iesire):
            vazut["iesire"] = iesire

        def ruleaza_complet(self, **k):
            vazut.update(k)
            return {"terminat": False}

    monkeypatch.setattr(d, "Pilot", PilotFals)
    assert d.main(["complet", "--limita-ore", "10"]) == 0
    assert vazut == {"iesire": d.IESIRE_COMPLET, "n_pypi": 30_000, "n_crates": None, "limita_ore": 10.0}
    assert d.IESIRE_COMPLET.parts[-3:] == ("lucru", "kronos_cod", "complet")
