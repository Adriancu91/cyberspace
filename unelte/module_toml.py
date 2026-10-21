"""Descrierile modulelor Kronos în formatul comun din Cyber Hub (`modul-v0`, copiat în plan/hub_modul-v0.md).

Pentru fiecare clasă din module/ care are fișa MANIFEST, scrie `module/manifeste/<nume>.toml`. Modulele Kronos sunt
fișiere, nu dosare, de aceea descrierile stau toate într-un singur dosar.

Ce vine din MANIFEST (rescris la fiecare rulare, ca să nu se poată desincroniza): nume, versiune, port,
versiune_contract, intrarea (`pachet.fisier:Clasa`) și comanda de teste.
Ce completează omul o dată și unealta PĂSTREAZĂ: `descriere`, `[depinde]` și `[ofera]`. Pentru un modul nou, unealta
le pune ea la început: `[depinde]` din importurile altor module cu MANIFEST, `[ofera]` din contractul portului, iar
`descriere` = „DE COMPLETAT”.

Nu importă modulele (citește fișierele cu ast), deci merge și fără PyTorch.

    python -X utf8 unelte/module_toml.py            # scrie / actualizează fișierele
    python -X utf8 unelte/module_toml.py --verifica # doar spune ce nu se potrivește (cod 1 dacă e ceva)
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
DE_COMPLETAT = "DE COMPLETAT"

# Ce oferă fiecare funcție a contractelor din kronos/contracte.py, pe scurt (pentru [ofera] la un modul nou).
OFERA_PORT = {
    "model": {
        "antreneaza": "antrenează cel mult un buget de secunde și întoarce statistici",
        "biti_pentru": "câți biți îi trebuie ca să ghicească un text (mai puțin = mai bine)",
        "genereaza": "continuă un text cu exact atâtea caractere câte se cer",
        "salveaza": "salvează modelul și întoarce calea fișierului",
        "incarca": "readuce un model salvat",
    },
    "date": {
        "text_antrenare": "textul de antrenare, mereu același",
        "text_validare": "textul de validare, nefolosit la antrenare",
    },
    "examen": {
        "examineaza": "notează un model pe textul de validare și întoarce scorurile",
        "scor_principal": "numele scorului după care se decide",
        "mai_mic_e_mai_bun": "în ce direcție e mai bun scorul",
    },
    "cercetator": {"propune": "citește istoricul și propune următoarea schimbare de setări"},
    "profesor": {"genereaza_exercitii": "scrie exerciții pe o temă"},
    "rulare": {"executa": "rulează o sarcină cu limită de timp și măsoară consumul"},
    "stocare": {
        "salveaza_json": "salvează un rezultat",
        "incarca_json": "readuce un rezultat salvat",
        "cale_pentru": "calea unui fișier în folderul proiectului, fără ieșire din el",
    },
    "interfata": {"anunta": "arată omului ce se întâmplă"},
    "traducere": {"traduce": "traduce un text între limbi"},
    "memorie": {
        "caracteristici": "codul ultimului cuvânt terminat, pentru fiecare literă",
        "cod": "locul unui cuvânt în bibliotecă, pe niveluri",
        "cauta": "sensurile unui cuvânt, pentru oameni",
        "nivele": "câte niveluri are codul",
        "statistici": "cifrele bibliotecii",
    },
}


@dataclass
class Modul:
    fisier: Path              # module/model_gpt.py
    pachet: str               # module.model_gpt
    clasa: str
    manifest: dict
    importuri: set[str] = field(default_factory=set)  # pachetele din module/ importate de fișier

    @property
    def nume(self) -> str:
        return str(self.manifest["nume"])

    @property
    def intrare(self) -> str:
        return f"{self.pachet}:{self.clasa}"


def _manifest(clasa: ast.ClassDef) -> dict | None:
    for instr in clasa.body:
        if isinstance(instr, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MANIFEST" for t in instr.targets):
            return ast.literal_eval(instr.value)
    return None


def descopera(radacina: Path = RADACINA) -> list[Modul]:
    """Toate clasele cu MANIFEST din module/ (și din subdosare), în ordinea fișierelor."""
    gasite = []
    for fisier in sorted((radacina / "module").rglob("*.py")):
        rel = fisier.relative_to(radacina).with_suffix("")
        pachet = ".".join(rel.parts)
        arbore = ast.parse(fisier.read_text(encoding="utf-8"))
        importuri = set()
        for nod in ast.walk(arbore):
            if isinstance(nod, ast.ImportFrom):
                if nod.level:  # import relativ: .x din același pachet
                    baza = rel.parts[: len(rel.parts) - nod.level]
                    importuri.add(".".join([*baza, *(nod.module.split(".") if nod.module else [])]))
                elif nod.module and nod.module.split(".")[0] == "module":
                    importuri.add(nod.module)
                    importuri.update(f"{nod.module}.{a.name}" for a in nod.names)  # from module import tokenizer_bpe
            elif isinstance(nod, ast.Import):
                importuri.update(a.name for a in nod.names if a.name.split(".")[0] == "module")
        for nod in arbore.body:
            if isinstance(nod, ast.ClassDef) and (m := _manifest(nod)) is not None:
                gasite.append(Modul(fisier, pachet, nod.name, m, importuri))
    return gasite


def comanda_teste(modul: Modul, radacina: Path = RADACINA) -> str:
    contract = f"python -m pytest teste_contracte -k {modul.clasa}"
    proprii = radacina / "teste" / f"test_{modul.fisier.stem}.py"
    return f"python -m pytest teste/{proprii.name} && {contract}" if proprii.exists() else contract


def depinde_initial(modul: Modul, toate: list[Modul]) -> dict[str, str]:
    """Celelalte module cu MANIFEST din fișierele importate, cu versiunea lor de acum ca minimă."""
    return {m.nume: f">={m.manifest['versiune']}" for m in toate
            if m.pachet in modul.importuri and m.pachet != modul.pachet}


def _text(valoare: str) -> str:
    return json.dumps(valoare, ensure_ascii=False)  # șirurile JSON sunt șiruri TOML valide


def _tabel(nume: str, valori: dict[str, str]) -> list[str]:
    return [f"[{nume}]", *(f"{_text(k)} = {_text(v)}" for k, v in valori.items()), ""]


def continut(modul: Modul, descriere: str, depinde: dict[str, str], ofera: dict[str, str],
             radacina: Path = RADACINA) -> str:
    m = modul.manifest
    randuri = [
        "# Scris de unelte/module_toml.py din MANIFEST-ul clasei; „descriere”, [depinde] și [ofera] se păstrează.",
        "[modul]",
        f"nume = {_text(str(m['nume']))}",
        'proiect = "kronos"',
        f"versiune = {_text(str(m['versiune']))}",
        f"descriere = {_text(descriere)}",
        'format = "modul-v0"',
        "",
        "[contract]",
        f"port = {_text(str(m['port']))}",
        f"versiune_contract = {_text(str(m['versiune_contract']))}",
        "",
        *_tabel("depinde", depinde),
        *_tabel("ofera", ofera),
        "[rulare]",
        'limbaj = "python"',
        f"intrare = {_text(modul.intrare)}",
        f"teste = {_text(comanda_teste(modul, radacina))}",
    ]
    return "\n".join(randuri) + "\n"


def dosar_manifeste(radacina: Path = RADACINA) -> Path:
    return radacina / "module" / "manifeste"


def asteptat(radacina: Path = RADACINA) -> dict[Path, str]:
    """Ce trebuie să conțină fiecare fișier, păstrând partea completată de om din fișierele existente."""
    toate = descopera(radacina)
    nume = [m.nume for m in toate]
    dubluri = sorted({n for n in nume if nume.count(n) > 1})
    if dubluri:
        raise SystemExit(f"Două clase cu același nume în MANIFEST: {', '.join(dubluri)}")
    rezultat = {}
    for modul in toate:
        cale = dosar_manifeste(radacina) / f"{modul.nume}.toml"
        vechi = tomllib.loads(cale.read_text(encoding="utf-8")) if cale.exists() else {}
        descriere = vechi.get("modul", {}).get("descriere", DE_COMPLETAT)
        depinde = vechi.get("depinde", depinde_initial(modul, toate))
        ofera = vechi.get("ofera", OFERA_PORT.get(str(modul.manifest["port"]), {}))
        rezultat[cale] = continut(modul, descriere, depinde, ofera, radacina)
    return rezultat


def probleme(radacina: Path = RADACINA) -> list[str]:
    """Ce nu se potrivește între MANIFEST-uri și fișierele scrise (gol = totul e la zi)."""
    gasite = []
    dorit = asteptat(radacina)
    for cale, text in dorit.items():
        if not cale.exists():
            gasite.append(f"lipsește {cale.name}")
        elif cale.read_text(encoding="utf-8") != text:
            gasite.append(f"{cale.name} nu e la zi cu MANIFEST-ul")
        if DE_COMPLETAT in text:
            gasite.append(f"{cale.name}: descrierea e încă „{DE_COMPLETAT}”")
    dosar = dosar_manifeste(radacina)
    if dosar.exists():
        gasite += [f"{c.name} nu mai are clasă cu MANIFEST" for c in sorted(dosar.glob("*.toml")) if c not in dorit]
    return gasite


def scrie(radacina: Path = RADACINA) -> list[Path]:
    dosar = dosar_manifeste(radacina)
    dosar.mkdir(parents=True, exist_ok=True)
    scrise = []
    for cale, text in asteptat(radacina).items():
        if not cale.exists() or cale.read_text(encoding="utf-8") != text:
            cale.write_text(text, encoding="utf-8", newline="\n")
            scrise.append(cale)
    return scrise


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifica", action="store_true", help="nu scrie nimic, doar spune ce nu se potrivește")
    p.add_argument("--radacina", type=Path, default=RADACINA, help=argparse.SUPPRESS)
    a = p.parse_args(argv)
    if a.verifica:
        gasite = probleme(a.radacina)
        for g in gasite:
            print(g)
        print("Totul e la zi." if not gasite else f"{len(gasite)} probleme.")
        return 1 if gasite else 0
    scrise = scrie(a.radacina)
    for c in scrise:
        print(f"scris: {c.relative_to(a.radacina)}")
    print(f"{len(scrise)} fișiere scrise, {len(descopera(a.radacina))} module în total.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
