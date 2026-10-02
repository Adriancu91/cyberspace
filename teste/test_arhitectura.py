"""Regula de aur a arhitecturii: nucleul nu depinde de niciun modul."""

import ast
from pathlib import Path

NUCLEU = Path(__file__).resolve().parent.parent / "nucleu"


def test_nucleul_nu_importa_module():
    incalcari = []
    for fisier in NUCLEU.glob("*.py"):
        arbore = ast.parse(fisier.read_text(encoding="utf-8"))
        for nod in ast.walk(arbore):
            nume = []
            if isinstance(nod, ast.Import):
                nume = [a.name for a in nod.names]
            elif isinstance(nod, ast.ImportFrom) and nod.module and nod.level == 0:
                nume = [nod.module]
            for n in nume:
                if n == "module" or n.startswith("module.") or n.startswith("teste"):
                    incalcari.append(f"{fisier.name}:{nod.lineno} importă {n}")
    assert not incalcari, "Nucleul nu are voie să importe module:\n" + "\n".join(incalcari)


def test_nucleul_ramane_mic():
    linii = sum(len(f.read_text(encoding="utf-8").splitlines()) for f in NUCLEU.glob("*.py"))
    assert linii < 2000, f"Nucleul are {linii} linii; ținta e sub 2000, ca să poată fi citit integral"
