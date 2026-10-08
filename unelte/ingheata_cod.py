"""Înghețul și rollback-ul școlii de cod (planul, secțiunea 2).

- **Îngheț** (`--eticheta <nume>`):
  - un tag Git `cod/<nume>` pe versiunea de acum a codului;
  - o arhivă `lucru/cod/inghet/<nume>.zip` cu:
    - modelele liniilor (cu optimizatorul lor) și bibliotecile lor;
    - starea, cu temperatura fiecărei linii;
    - o copie a jurnalului `runde.jsonl`;
    - la un îngheț al tuturor liniilor, și modelul pregătit.
  - `--linie A` îngheață doar linia A (modelul ei, biblioteca ei, partea ei din stare).
- **Rollback** (`--revino <nume> --motiv "..."`):
  - pune înapoi modelele, bibliotecile și starea din arhivă; la un îngheț al unei singure linii, doar partea ei din
    stare, iar cealaltă linie rămâne cum e;
  - jurnalul nu se suprascrie (ca jurnalul Kronos, doar crește). În el intră un rând nou: „rollback la <nume>,
    motiv: …”.
- **Când e obligatoriu:** înainte de pilot, după fiecare nivel trecut, înainte de orice schimbare de configurare.
  Școala refuză să continue dacă configurarea s-a schimbat de la ultima rundă fără un îngheț între ele.

    python unelte/ingheata_cod.py --eticheta inainte_de_schimbare --motiv "înainte de schimbarea configurării"
    python unelte/ingheata_cod.py --revino inainte_de_pilot --motiv "…"
    python unelte/ingheata_cod.py --lista
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))


def scrie_in_jurnal(cod: Path, rand: dict[str, Any]) -> None:
    """Un rând nou în lucru/cod/runde.jsonl (jurnalul școlii doar crește)."""
    cod.mkdir(parents=True, exist_ok=True)
    with (cod / "runde.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"timp": datetime.now().isoformat(timespec="seconds"), **rand}, ensure_ascii=False) + "\n")


def _scrie_starea(cod: Path, stare: dict[str, Any]) -> None:
    temporar = cod / "stare.json.tmp"
    temporar.write_text(json.dumps(stare, ensure_ascii=False, indent=1), encoding="utf-8")
    temporar.replace(cod / "stare.json")


def _linii_existente(cod: Path) -> list[str]:
    return sorted(d.name for d in (cod / "linii").iterdir() if d.is_dir()) if (cod / "linii").exists() else []


def _de_arhivat(cod: Path, linii: list[str] | None) -> list[Path]:
    fisiere: list[Path] = []
    for linie in linii or _linii_existente(cod):
        dosar = cod / "linii" / linie
        if dosar.exists():
            fisiere += [f for f in sorted(dosar.rglob("*")) if f.is_file() and not f.name.endswith(".tmp")]
        fisiere += [f for f in (cod / f"biblioteca_{linie}.txt", cod / f"biblioteca_{linie}.jsonl") if f.exists()]
    comune = [cod / "stare.json", cod / "runde.jsonl"] + ([] if linii else [cod / "pregatit.pt"])
    return fisiere + [f for f in comune if f.exists()]


def _tag_exista(tag: str, radacina: Path) -> bool:
    return subprocess.run(["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"], cwd=radacina,
                          capture_output=True).returncode == 0


def exista(lucru: Path, eticheta: str, git: bool = True, radacina: Path = RADACINA) -> bool:
    """Există deja un îngheț (arhivă sau tag Git) cu acest nume?"""
    return (lucru / "cod" / "inghet" / f"{eticheta}.zip").exists() or (git and _tag_exista(f"cod/{eticheta}", radacina))


def ingheata(lucru: Path, eticheta: str, motiv: str, linii: list[str] | None = None, git: bool = True,
             radacina: Path = RADACINA) -> Path:
    """Arhiva și tag-ul Git. Întoarce arhiva. Un nume folosit deja nu se suprascrie.

    Tag-ul e unul simplu (fără mesaj): unul cu mesaj cere un nume și un email în Git, iar laptopul nu le are. Motivul
    înghețului stă în jurnal și în arhivă (inghet.json). Arhiva ajunge la locul ei doar după ce tag-ul a reușit: un
    îngheț pe jumătate nu rămâne."""
    cod = lucru / "cod"
    arhiva = cod / "inghet" / f"{eticheta}.zip"
    if exista(lucru, eticheta, git, radacina):
        raise FileExistsError(f"înghețul „{eticheta}” există deja (arhiva sau tag-ul Git cod/{eticheta})")
    arhiva.parent.mkdir(parents=True, exist_ok=True)
    fisiere = _de_arhivat(cod, linii)
    temporar = arhiva.with_name(arhiva.name + ".tmp")
    with zipfile.ZipFile(temporar, "w") as z:
        for f in fisiere:
            fel = zipfile.ZIP_STORED if f.suffix == ".pt" else zipfile.ZIP_DEFLATED  # modelele nu se comprimă
            z.write(f, f.relative_to(cod).as_posix(), compress_type=fel)
        z.writestr("inghet.json", json.dumps({"eticheta": eticheta, "motiv": motiv, "linii": linii or "toate",
                                              "timp": datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False))
    tag = None
    if git:
        tag = f"cod/{eticheta}"
        rezultat = subprocess.run(["git", "tag", tag], cwd=radacina, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace")
        if rezultat.returncode != 0:
            temporar.unlink()
            raise RuntimeError(f"tag-ul Git {tag} n-a mers ({rezultat.stderr.strip()}); înghețul nu s-a făcut")
    temporar.replace(arhiva)
    if (cod / "stare.json").exists():  # pentru regula „îngheț înainte de orice schimbare de configurare”
        stare = json.loads((cod / "stare.json").read_text(encoding="utf-8"))
        stare["inghetat_dupa_ultima_runda"] = True
        _scrie_starea(cod, stare)
    scrie_in_jurnal(cod, {"tip": "inghet", "eticheta": eticheta, "motiv": f"îngheț „{eticheta}”: {motiv}",
                          "linii": linii or "toate", "arhiva": f"lucru/cod/inghet/{arhiva.name}",
                          "marime_mb": round(arhiva.stat().st_size / 2 ** 20, 1), "fisiere": len(fisiere),
                          "tag_git": tag})
    return arhiva


def _pune_starea(cod: Path, din_arhiva: dict[str, Any], linii: list[str] | str) -> None:
    """Starea din arhivă: toată, la un îngheț al tuturor liniilor; altfel, doar partea liniilor înghețate."""
    if linii == "toate" or not (cod / "stare.json").exists():
        stare = din_arhiva
    else:
        stare = json.loads((cod / "stare.json").read_text(encoding="utf-8"))
        for linie in linii:
            if linie in din_arhiva.get("linii", {}):
                stare.setdefault("linii", {})[linie] = din_arhiva["linii"][linie]
    stare["inghetat_dupa_ultima_runda"] = True
    _scrie_starea(cod, stare)


def revino(lucru: Path, eticheta: str, motiv: str) -> list[str]:
    """Pune înapoi ce e în arhivă (fără jurnal) și notează rollback-ul în jurnal. Întoarce fișierele puse înapoi."""
    cod = lucru / "cod"
    arhiva = cod / "inghet" / f"{eticheta}.zip"
    if not arhiva.exists():
        raise FileNotFoundError(f"nu există înghețul „{eticheta}” ({arhiva})")
    puse = []
    with zipfile.ZipFile(arhiva) as z:
        info = json.loads(z.read("inghet.json"))
        for nume in z.namelist():
            if nume in ("inghet.json", "runde.jsonl"):
                continue
            if nume == "stare.json":
                _pune_starea(cod, json.loads(z.read(nume)), info["linii"])
            else:
                tinta = cod / nume
                tinta.parent.mkdir(parents=True, exist_ok=True)
                temporar = tinta.with_name(tinta.name + ".tmp")
                with z.open(nume) as sursa, open(temporar, "wb") as destinatie:
                    shutil.copyfileobj(sursa, destinatie)
                temporar.replace(tinta)
            puse.append(nume)
    scrie_in_jurnal(cod, {"tip": "rollback", "eticheta": eticheta, "motiv": f"rollback la {eticheta}, motiv: {motiv}",
                          "linii": info["linii"], "fisiere": len(puse)})
    return puse


def lista(lucru: Path) -> list[dict[str, Any]]:
    rezultat = []
    for arhiva in sorted((lucru / "cod" / "inghet").glob("*.zip")):
        with zipfile.ZipFile(arhiva) as z:
            rezultat.append({**json.loads(z.read("inghet.json")), "marime_mb": round(arhiva.stat().st_size / 2 ** 20, 1)})
    return rezultat


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Înghețul și rollback-ul școlii de cod.")
    ce = parser.add_mutually_exclusive_group(required=True)
    ce.add_argument("--eticheta", help="îngheață starea de acum sub acest nume (și tag-ul Git cod/<nume>)")
    ce.add_argument("--revino", help="rollback la înghețul cu acest nume")
    ce.add_argument("--lista", action="store_true")
    parser.add_argument("--motiv", default="", help="de ce (intră în jurnal)")
    parser.add_argument("--linie", action="append", choices=("A", "B"), help="doar linia dată; implicit toate")
    parser.add_argument("--director-lucru", default=str(RADACINA / "lucru"))
    parser.add_argument("--fara-git", action="store_true", help="fără tag Git (doar arhiva)")
    args = parser.parse_args(argv)
    lucru = Path(args.director_lucru)
    if args.lista:
        for i in lista(lucru):
            print(f"{i['eticheta']:<24} {i['timp']}  {i['marime_mb']:>7} MB  {i['motiv']}")
        return 0
    if args.revino:
        if not args.motiv:
            print("Un rollback cere --motiv (intră în jurnal).")
            return 1
        puse = revino(lucru, args.revino, args.motiv)
        print(f"Rollback la „{args.revino}”: {len(puse)} fișiere puse înapoi. Motiv: {args.motiv}")
        return 0
    arhiva = ingheata(lucru, args.eticheta, args.motiv or "îngheț de mână", args.linie, git=not args.fara_git)
    print(f"Înghețat „{args.eticheta}”: {arhiva} ({arhiva.stat().st_size / 2 ** 20:.1f} MB)"
          + ("" if args.fara_git else f", tag Git cod/{args.eticheta}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
