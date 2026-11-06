"""Punctele de salvare `.pt`: ce s-ar păstra și ce s-ar putea șterge (S84, C-85 pasul 1, aprobat de Adrian 6 nov 2026).

DOAR LISTĂ. Unealta nu are comandă de ștergere: nu șterge, nu mută, nu redenumește și nu scrie în jurnal. Singurul
fișier pe care îl scrie e lista: `lucru/puncte_salvare/lista_<AAAA-LL-ZZ_HHMM>.json` (refuză să scrie peste una veche).

Pentru fiecare `.pt` din `lucru/`: calea, mărimea, SHA-256, experimentul și linia din jurnal (doar citit), scorurile
din jurnal (val_bpb; română curat / cod curat din examenele pe validări) și clasa:
- PĂSTREAZĂ: rezervele numite din `config/puncte_salvare.toml`, modelul în uz, tot ce e numit în pre-înregistrările
  încă deschise și în sarcinile `aprobat`/`in_lucru` din `plan/coada.md`, câștigătorul fiecărei linii;
- SE POATE ȘTERGE: legat de jurnal, dar nu e nimic din cele de mai sus (motivul e scris);
- NECUNOSCUT — păstrat: fișierul nu se poate lega de jurnal.

Comenzi:
  python -X utf8 unelte/puncte_salvare.py lista [--radacina .] [--config config/puncte_salvare.toml]
  python -X utf8 unelte/puncte_salvare.py tabel lucru/puncte_salvare/lista_....json   (tabelele pentru raport)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

PASTREAZA = "PĂSTREAZĂ"
SE_POATE_STERGE = "SE POATE ȘTERGE"
NECUNOSCUT = "NECUNOSCUT — păstrat"
CLASE = (PASTREAZA, SE_POATE_STERGE, NECUNOSCUT)
INCHISA = "## Ce a ieșit"  # același semn ca în unelte/preinregistrare.py
GB = 1e9


def _cheie(cale: str | Path) -> str:
    """Calea ca text comparabil: bare oblice, fără „./”, litere mici (Windows nu ține cont de majuscule)."""
    text = str(cale).replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text.lower()


def _relativ(cale: Path, radacina: Path) -> str:
    try:
        return cale.resolve().relative_to(radacina.resolve()).as_posix()
    except ValueError:
        return cale.as_posix()


def citeste_jurnal(radacina: Path) -> list[dict[str, Any]]:
    """Fișele din jurnal, doar citite (fără `Jurnal(...)`, care ar crea dosarul dacă lipsește)."""
    fisier = radacina / "lucru" / "jurnal" / "experimente.jsonl"
    if not fisier.exists():
        return []
    fise = []
    with fisier.open(encoding="utf-8") as f:
        for rand in f:
            rand = rand.strip()
            if not rand:
                continue
            try:
                fise.append(json.loads(rand))
            except json.JSONDecodeError:
                continue
    return fise


def _val_bpb(fisa: dict[str, Any]) -> float | None:
    v = (fisa.get("scoruri") or {}).get("val_bpb")
    return float(v) if isinstance(v, (int, float)) and math.isfinite(v) else None


def legaturi_jurnal(fise: list[dict[str, Any]]) -> dict[str, Any]:
    """Ce fișiere pomenește jurnalul: modelele salvate (pe nume) și stările de continuare ale liniilor (pe cale)."""
    modele: dict[str, dict[str, Any]] = {}      # nume fișier (experiment_N.pt) → fișa
    modele_cale: dict[str, dict[str, Any]] = {}  # cale completă → fișa
    stari: dict[str, dict[str, Any]] = {}       # cale gpt.pt → {linie, ultimul}
    examene: dict[int, dict[str, Any]] = {}     # experiment → ultimele scoruri de pe validări
    for f in fise:
        salvat = f.get("model_salvat")
        if isinstance(salvat, str) and salvat:
            modele_cale[_cheie(salvat)] = f
            modele[_cheie(salvat).rsplit("/", 1)[-1]] = f
        setari_model = (f.get("setari") or {}).get("model") or {}
        continuare = ((f.get("dupa_examen") or {}).get("continuare") or {})
        for cale in (setari_model.get("cale_stare"), continuare.get("fisier")):
            if isinstance(cale, str) and cale:
                stari[_cheie(cale)] = {"linie": f.get("linie"), "ultimul": f.get("id")}
        elev = ((f.get("module") or {}).get("elev") or {})
        scoruri = f.get("scoruri") or {}
        if isinstance(elev, dict) and isinstance(elev.get("experiment"), int) and "bpb_romana_curat" in scoruri:
            examene[elev["experiment"]] = {"bpb_romana_curat": scoruri.get("bpb_romana_curat"),
                                           "bpb_cod_curat": scoruri.get("bpb_cod_curat"),
                                           "din_fisa": f.get("id")}
    castigatori: dict[str, dict[str, Any]] = {}
    for f in fise:
        if f.get("decizie") != "pastrat" or not f.get("model_salvat") or _val_bpb(f) is None:
            continue
        linie = f.get("linie")
        if linie not in castigatori or _val_bpb(f) < _val_bpb(castigatori[linie]):
            castigatori[linie] = f
    linii = {f.get("linie") for f in fise if f.get("linie")}
    return {"modele": modele, "modele_cale": modele_cale, "stari": stari, "examene": examene,
            "castigatori": castigatori, "linii": linii}


# --- ce e numit în pre-înregistrările deschise și în sarcinile aprobat/in_lucru ---------------------------------

_RE_EXPERIMENT = re.compile(r"(?:#|experiment(?:ul)?[_ ]#?)(\d{1,5})\b")
_RE_CALE_PT = re.compile(r"lucru[/\\][^\s`'\"()\[\],;|*]+?\.pt\b", re.IGNORECASE)
_RE_DOSAR = re.compile(r"lucru[/\\]([A-Za-z0-9_\-.]+)[/\\]")
_RE_SARCINA = re.compile(r"^###\s+(S\w+)", re.MULTILINE)
_RE_STARE_VIE = re.compile(r"^\s*-\s*stare:\s*\**\s*(aprobat|in_lucru)", re.IGNORECASE | re.MULTILINE)


def sectiuni_vii(text_coada: str) -> list[tuple[str, str]]:
    """Sarcinile din coadă a căror stare începe cu `aprobat` sau `in_lucru` (numele și textul lor)."""
    potriviri = list(_RE_SARCINA.finditer(text_coada))
    vii = []
    for i, m in enumerate(potriviri):
        sfarsit = potriviri[i + 1].start() if i + 1 < len(potriviri) else len(text_coada)
        bucata = text_coada[m.start():sfarsit]
        if _RE_STARE_VIE.search(bucata):
            vii.append((m.group(1), bucata))
    return vii


def numite(radacina: Path, linii: set[str]) -> dict[str, Any]:
    """Experimentele, căile `.pt`, dosarele din lucru/ și liniile pomenite în textele „vii”."""
    surse: list[tuple[str, str]] = []
    dosar = radacina / "docs" / "preinregistrari"
    if dosar.is_dir():
        for p in sorted(dosar.glob("*.md")):
            text = p.read_text(encoding="utf-8", errors="replace")
            if INCHISA not in text:
                surse.append((f"pre-înregistrarea deschisă {p.name}", text))
    coada = radacina / "plan" / "coada.md"
    if coada.exists():
        for nume, text in sectiuni_vii(coada.read_text(encoding="utf-8", errors="replace")):
            surse.append((f"sarcina {nume} (aprobat/in_lucru) din plan/coada.md", text))
    experimente: dict[int, list[str]] = {}
    cai: dict[str, list[str]] = {}
    dosare: dict[str, list[str]] = {}
    for sursa, text in surse:
        for m in _RE_EXPERIMENT.finditer(text):
            experimente.setdefault(int(m.group(1)), []).append(sursa)
        for m in _RE_CALE_PT.finditer(text):
            cai.setdefault(_cheie(m.group(0)), []).append(sursa)
        for m in _RE_DOSAR.finditer(text):
            dosare.setdefault(m.group(1).lower(), []).append(sursa)
        for linie in linii:
            if re.search(rf"(?<![\w-]){re.escape(linie)}(?![\w-])", text):
                dosare.setdefault(linie.lower(), []).append(sursa)
    curat = lambda d: {k: sorted(set(v)) for k, v in d.items()}  # noqa: E731
    return {"surse": [s for s, _ in surse], "experimente": curat(experimente), "cai": curat(cai),
            "dosare": curat(dosare)}


# --- lista ---------------------------------------------------------------------------------------------------------

def sha256(cale: Path) -> str:
    h = hashlib.sha256()
    with cale.open("rb") as f:
        while bloc := f.read(1 << 22):
            h.update(bloc)
    return h.hexdigest()


def citeste_config(cale: Path) -> dict[str, Any]:
    with cale.open("rb") as f:
        date = tomllib.load(f)
    return {"experimente": [int(x) for x in date.get("experimente", [])],
            "model_in_uz": date.get("model_in_uz"),
            "fisiere": [_cheie(x) for x in date.get("fisiere", [])]}


def _scoruri(fisa: dict[str, Any] | None, leg: dict[str, Any]) -> dict[str, Any]:
    if not fisa:
        return {}
    s: dict[str, Any] = {"val_bpb": _val_bpb(fisa)}
    examen = leg["examene"].get(fisa.get("id"))
    if examen:
        s.update(examen)
    return s


def clasifica(rel: str, leg: dict[str, Any], config: dict[str, Any], num: dict[str, Any],
              radacina: Path) -> dict[str, Any]:
    """Clasa unui fișier și motivul; `rel` e calea de la rădăcină (cu bare oblice)."""
    cheie = _cheie(rel)
    nume = cheie.rsplit("/", 1)[-1]
    parti = cheie.split("/")
    fisa = leg["modele_cale"].get(cheie)
    if fisa is None and len(parti) == 4 and parti[1] == "stocare" and parti[2] == "modele":
        fisa = leg["modele"].get(nume)  # aceeași fișă, salvată cu altă cale (alt calculator)
        if fisa is not None and f"experiment_{fisa.get('id')}.pt" != nume:
            fisa = None
    stare = leg["stari"].get(cheie)
    exp = fisa.get("id") if fisa else None
    linie = fisa.get("linie") if fisa else (stare or {}).get("linie")
    rezultat = {"experiment": exp, "linie": linie, "decizie": fisa.get("decizie") if fisa else None,
                "scoruri": _scoruri(fisa, leg)}
    if stare and not fisa:
        rezultat["ultimul_experiment_al_liniei"] = stare.get("ultimul")

    def gata(clasa: str, motiv: str) -> dict[str, Any]:
        return {**rezultat, "clasa": clasa, "motiv": motiv}

    # 1. rezervele numite și modelul în uz
    if cheie in config["fisiere"]:
        return gata(PASTREAZA, "rezervă numită în config/puncte_salvare.toml")
    if exp is not None and exp == config.get("model_in_uz"):
        return gata(PASTREAZA, f"modelul în uz (#{exp})")
    if exp is not None and exp in config["experimente"]:
        return gata(PASTREAZA, f"rezervă numită (#{exp}) în config/puncte_salvare.toml")
    # 2. numite în pre-înregistrările deschise / sarcinile vii
    if cheie in num["cai"]:
        return gata(PASTREAZA, "numit în " + "; ".join(num["cai"][cheie]))
    if exp is not None and exp in num["experimente"]:
        return gata(PASTREAZA, f"#{exp} numit în " + "; ".join(num["experimente"][exp]))
    if len(parti) == 3 and parti[1] in num["dosare"]:
        return gata(PASTREAZA, f"dosarul lucru/{parti[1]}/ numit în " + "; ".join(num["dosare"][parti[1]]))
    # 3. legat de jurnal
    if fisa:
        castigator = leg["castigatori"].get(linie)
        if castigator is not None and castigator.get("id") == exp:
            return gata(PASTREAZA, f"câștigătorul liniei {linie} (cel mai mic val_bpb păstrat)")
        if castigator is not None:
            return gata(SE_POATE_STERGE, f"#{exp}, linia {linie}, decizie {fisa.get('decizie')}; câștigătorul liniei "
                                         f"e #{castigator.get('id')} (val_bpb {_val_bpb(castigator):.4f})")
        return gata(SE_POATE_STERGE, f"#{exp}, linia {linie}, decizie {fisa.get('decizie')}; linia nu are niciun "
                                     f"experiment păstrat cu val_bpb")
    if stare:
        castigator = leg["castigatori"].get(linie)
        if castigator is not None:
            salvat = radacina / castigator["model_salvat"]
            if not salvat.exists():
                return gata(PASTREAZA, f"starea liniei {linie}; fișierul câștigătorului #{castigator.get('id')} lipsește"
                                       f" de pe disc (poate fi singura copie)")
        return gata(SE_POATE_STERGE, f"starea de continuare a liniei {linie} (ultimul experiment #{stare.get('ultimul')});"
                                     f" modelele liniei sunt în lucru/stocare/modele/")
    # 4. nelegat
    if parti[1:2] == ["cache"]:
        return gata(NECUNOSCUT, "cache de simboluri (nu e model), nelegat de jurnal")
    if len(parti) > 1 and parti[1].startswith("teste_tmp"):
        return gata(NECUNOSCUT, f"dosar temporar al testelor (lucru/{parti[1]}/), nelegat de jurnal")
    return gata(NECUNOSCUT, "nelegat de jurnal")


def lista(radacina: Path, config_cale: Path, acum: datetime | None = None,
          iesire: Path | None = None, cu_progres: bool = False) -> Path:
    acum = acum or datetime.now()
    radacina = Path(radacina)
    iesire = iesire or radacina / "lucru" / "puncte_salvare"
    tinta = iesire / f"lista_{acum:%Y-%m-%d_%H%M}.json"
    if tinta.exists():
        raise FileExistsError(f"{tinta} există deja; nu scriu peste el")
    config = citeste_config(config_cale)
    fise = citeste_jurnal(radacina)
    leg = legaturi_jurnal(fise)
    num = numite(radacina, leg["linii"])
    fisiere = sorted((radacina / "lucru").rglob("*.pt"), key=lambda p: _relativ(p, radacina).lower())
    randuri = []
    for i, p in enumerate(fisiere, 1):
        rel = _relativ(p, radacina)
        marime = p.stat().st_size
        rand = {"cale": rel, "octeti": marime, "sha256": sha256(p)}
        rand.update(clasifica(rel, leg, config, num, radacina))
        randuri.append(rand)
        if cu_progres:
            print(f"[{i}/{len(fisiere)}] {rand['clasa']}: {rel} ({marime / GB:.2f} GB)", flush=True)
    total = {c: {"fisiere": sum(1 for r in randuri if r["clasa"] == c),
                 "octeti": sum(r["octeti"] for r in randuri if r["clasa"] == c)} for c in CLASE}
    for t in total.values():
        t["gb"] = round(t["octeti"] / GB, 3)
    date = {"facut_la": acum.isoformat(timespec="seconds"), "radacina": str(radacina.resolve()),
            "config": str(config_cale), "config_continut": config,
            "fise_jurnal": len(fise), "surse_numite": num["surse"],
            "castigatori": {l: f.get("id") for l, f in sorted(leg["castigatori"].items())},
            "total": total, "fisiere": randuri}
    iesire.mkdir(parents=True, exist_ok=True)
    tinta.write_text(json.dumps(date, ensure_ascii=False, indent=1), encoding="utf-8")
    return tinta


def tabel(cale: Path, primele: int = 20) -> str:
    date = json.loads(Path(cale).read_text(encoding="utf-8"))
    nr = lambda x: f"{x:.2f}".replace(".", ",")  # noqa: E731
    o = ["| clasa | fișiere | GB |", "|---|---|---|"]
    for c, t in date["total"].items():
        o.append(f"| {c} | {t['fisiere']} | {nr(t['octeti'] / GB)} |")
    sterge = sorted((r for r in date["fisiere"] if r["clasa"] == SE_POATE_STERGE), key=lambda r: -r["octeti"])
    o += ["", f"Primele {primele} cele mai mari din „{SE_POATE_STERGE}”:", "",
          "| # | fișier | GB | exp. | linia | val_bpb | motivul |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(sterge[:primele], 1):
        v = (r.get("scoruri") or {}).get("val_bpb")
        o.append(f"| {i} | `{r['cale']}` | {nr(r['octeti'] / GB)} | {r.get('experiment') or '—'} | {r.get('linie') or '—'}"
                 f" | {nr(v) if isinstance(v, float) else '—'} | {r['motiv']} |")
    necunoscute = [r for r in date["fisiere"] if r["clasa"] == NECUNOSCUT]
    grupuri: dict[str, list[dict[str, Any]]] = {}
    for r in necunoscute:
        parti = r["cale"].split("/")
        grup = "/".join(parti[:2]) + "/" if len(parti) > 2 else r["cale"]
        grupuri.setdefault(grup, []).append(r)
    o += ["", f"„{NECUNOSCUT}” ({len(necunoscute)} fișiere), pe dosare:", "",
          "| dosar | fișiere | GB | motivul |", "|---|---|---|---|"]
    for g, rs in sorted(grupuri.items(), key=lambda kv: -sum(r["octeti"] for r in kv[1])):
        motive = "; ".join(sorted({r["motiv"] for r in rs}))
        o.append(f"| `{g}` | {len(rs)} | {nr(sum(r['octeti'] for r in rs) / GB)} | {motive} |")
    pastrate = [r for r in date["fisiere"] if r["clasa"] == PASTREAZA]
    o += ["", f"„{PASTREAZA}” ({len(pastrate)} fișiere):", "", "| fișier | GB | exp. | motivul |", "|---|---|---|---|"]
    for r in sorted(pastrate, key=lambda r: r["cale"]):
        o.append(f"| `{r['cale']}` | {nr(r['octeti'] / GB)} | {r.get('experiment') or '—'} | {r['motiv']} |")
    return "\n".join(o) + "\n"


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comanda", required=True)
    pl = sub.add_parser("lista", help="scrie lista punctelor de salvare (nu șterge nimic)")
    pl.add_argument("--radacina", type=Path, default=Path("."))
    pl.add_argument("--config", type=Path, default=Path("config/puncte_salvare.toml"))
    pt = sub.add_parser("tabel", help="tabelele pentru raport, dintr-o listă scrisă")
    pt.add_argument("fisier", type=Path)
    pt.add_argument("--primele", type=int, default=20)
    a = p.parse_args(argv)
    if a.comanda == "lista":
        try:
            tinta = lista(a.radacina, a.config, cu_progres=True)
        except FileExistsError as e:
            print(f"Refuz: {e}")
            return 1
        print(f"Lista scrisă: {tinta}")
        print(tabel(tinta))
        return 0
    print(tabel(a.fisier, a.primele))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
