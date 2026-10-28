"""Unealta pilotului Kronos-Cod (S43a): licențe, data-limită, filtre, spațiu, reluare, ritm, nimic pe disc. FĂRĂ rețea."""

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
