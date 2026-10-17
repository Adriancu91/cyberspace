"""Examenul neutru (17 octombrie 2026): texte create după 12 octombrie 2026, pe care nu le-a văzut niciun model.

Pre-înregistrarea: docs/preinregistrari/2026-10-17_examen_neutru.md. Trei seturi, fiecare în date/neutru/<set>/validare.txt
(texte despărțite ca în validările noastre), cu atribuirea fiecărui text în date/neutru/surse.json:
- **wikipedia_ro_nou**: toate articolele noi din Wikipedia în română (fără redirecționări, pagini recreate și traduceri
  făcute cu unealta Wikipediei), de cel puțin 300 de litere, ca text simplu (TextExtracts);
- **wikipedia_en_nou**: la fel în engleză, 200 alese la întâmplare;
- **cod_python_nou**: din proiecte GitHub noi (cel puțin 3 stele, fără copii), cu licență permisivă (MIT, Apache-2.0,
  BSD), 40 alese la întâmplare, cel mult 5 fișiere .py din fiecare.

Seturile se scriu o singură dată (nu se suprascriu). Notele se dau apoi cu unelte/compara_externe.py --validari.

    python unelte/examen_neutru.py --descarca
    python unelte/compara_externe.py --kronos 373 --validari date/neutru/seturi.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.examen_validari_ws import SEPARATOR  # noqa: E402

DE_LA = "2026-10-13T00:00:00Z"  # după 12 octombrie 2026, ziua în care am descărcat datele lui Kronos
SAMANTA = 1018
AGENT = "KronosResearch/1.0 (evaluare locala; un singur om, putine cereri)"
LICENTE = {"mit": "MIT", "apache-2.0": "Apache-2.0", "bsd-3-clause": "BSD-3-Clause", "bsd-2-clause": "BSD-2-Clause"}
ETICHETE_SCOASE = {"mw-recreated", "contenttranslation", "contenttranslation-v2"}
SECTIUNI_FINALE = {"referințe", "note", "bibliografie", "legături externe", "vezi și", "surse", "lectură suplimentară",
                   "references", "notes", "bibliography", "external links", "see also", "sources", "further reading",
                   "citations", "footnotes"}
CAI_SCOASE = re.compile(r"(^|/)(vendor|vendored|_vendor|third_party|thirdparty|external|extern|site-packages|node_modules|"
                        r"dist|build|migrations|\.venv|venv)/", re.I)
# fișiere tipice copiate dintr-un șablon de proiect (completarea lui Adrian, 17 octombrie)
NUME_SCOASE = {"setup.py", "conftest.py", "manage.py", "wsgi.py", "asgi.py", "__init__.py"}
MINIM_LITERE = 300
MINIM_COD = 300
ROBOT = re.compile(r"(bot$|^robot)", re.I)


def cere(url: str, parametri: dict[str, Any] | None = None, json_: bool = True, pauza: float = 1.0) -> Any:
    if parametri:
        url += "?" + urllib.parse.urlencode(parametri)
    cerere = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept": "application/vnd.github+json"})
    for incercare in range(6):
        try:
            with urllib.request.urlopen(cerere, timeout=60) as r:
                date = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code not in (403, 429, 503) or incercare == 5:
                raise
            # GitHub fără cont: 60 de cereri pe oră (10 pe minut la căutare), cu ora la care se reface limita;
            # Wikipedia: „Retry-After”, sau așteptăm tot mai mult (30 s, 60 s, 120 s...)
            reset, dupa = e.headers.get("X-RateLimit-Reset"), e.headers.get("Retry-After")
            if reset:
                asteapta = int(reset) - time.time() + 5
            elif dupa and dupa.isdigit():
                asteapta = int(dupa) + 1
            elif e.code == 403:
                raise
            else:
                asteapta = 30 * 2**incercare
            time.sleep(min(3700, max(5, asteapta)))
    time.sleep(pauza)
    return json.loads(date) if json_ else date.decode("utf-8")


# --- Wikipedia ----------------------------------------------------------------------------------------------------

def articole_noi(limba: str, de_la: str = DE_LA, cere_: Callable = cere) -> list[dict[str, Any]]:
    """Articolele create din `de_la` încoace: fără redirecționări, pagini recreate și traduceri cu unealta Wikipediei."""
    api = f"https://{limba}.wikipedia.org/w/api.php"
    p: dict[str, Any] = {"action": "query", "list": "recentchanges", "rctype": "new", "rcnamespace": 0,
                         "rcshow": "!redirect", "rcprop": "title|timestamp|ids|tags|sizes|user|flags", "rclimit": 500,
                         "rcend": de_la, "format": "json", "formatversion": 2}
    gasite: list[dict[str, Any]] = []
    while True:
        d = cere_(api, p)
        for r in d["query"]["recentchanges"]:
            if not ETICHETE_SCOASE & set(r.get("tags", [])):
                gasite.append({"titlu": r["title"], "pageid": r["pageid"], "creat": r["timestamp"],
                               "creator": r.get("user", ""), "semn_bot": bool(r.get("bot"))})
        if "continue" not in d:
            break
        p.update(d["continue"])
    marcheaza_robotii(api, gasite, cere_)
    return gasite


def marcheaza_robotii(api: str, articole: list[dict[str, Any]], cere_: Callable = cere) -> None:
    """robot = crearea are semnul „bot”, contul e în grupul „bot” sau numele lui se termină în „bot” / începe cu „robot”."""
    conturi = sorted({a["creator"] for a in articole if a["creator"]})
    in_grup: set[str] = set()
    for i in range(0, len(conturi), 50):
        d = cere_(api, {"action": "query", "list": "users", "ususers": "|".join(conturi[i: i + 50]), "usprop": "groups",
                        "format": "json", "formatversion": 2})
        in_grup |= {u["name"] for u in d["query"]["users"] if "bot" in u.get("groups", [])}
    for a in articole:
        a["robot"] = a["semn_bot"] or a["creator"] in in_grup or bool(ROBOT.search(a["creator"].replace("_", " ").strip()))


def curata_articol(text: str) -> str:
    """Textul fără secțiunile de la sfârșit (referințe, legături externe...) și fără rândurile goale în plus."""
    randuri = text.replace("\r", "").split("\n")
    for i, rand in enumerate(randuri):
        if rand.strip().strip("=").strip().lower() in SECTIUNI_FINALE:
            randuri = randuri[:i]
            break
    return re.sub(r"\n{3,}", "\n\n", "\n".join(randuri)).strip()


def text_articol(limba: str, pageid: int, cere_: Callable = cere) -> dict[str, Any] | None:
    d = cere_(f"https://{limba}.wikipedia.org/w/api.php", {
        "action": "query", "prop": "extracts|revisions", "explaintext": 1, "exsectionformat": "plain",
        "rvprop": "ids|timestamp", "pageids": pageid, "format": "json", "formatversion": 2}, pauza=2.0)
    pagina = d["query"]["pages"][0]
    if pagina.get("missing") or "extract" not in pagina:
        return None
    rev = (pagina.get("revisions") or [{}])[0]
    return {"text": curata_articol(pagina["extract"]), "revizie": rev.get("revid"), "revizie_din": rev.get("timestamp"),
            "titlu": pagina["title"], "adresa": f"https://{limba}.wikipedia.org/?curid={pageid}"}


def set_wikipedia(limba: str, cate: int | None, cere_: Callable = cere, spune=print) -> list[dict[str, Any]]:
    lista = articole_noi(limba, cere_=cere_)
    spune(f"Wikipedia {limba}: {len(lista)} articole noi (după filtre)", flush=True)
    random.Random(SAMANTA).shuffle(lista)
    texte: list[dict[str, Any]] = []
    for a in lista:
        if cate is not None and len(texte) >= cate:
            break
        t = text_articol(limba, a["pageid"], cere_)
        if t and len(t["text"]) >= MINIM_LITERE:
            texte.append({**t, "creat": a["creat"], "creator": a["creator"], "robot": a["robot"],
                          "licenta": "CC BY-SA 4.0"})
    return texte


# --- GitHub -------------------------------------------------------------------------------------------------------

def proiecte_noi(cere_: Callable = cere, de_la: str = DE_LA[:10]) -> list[dict[str, Any]]:
    gasite: dict[str, dict[str, Any]] = {}
    for cheie in LICENTE:
        for pagina in range(1, 11):
            d = cere_("https://api.github.com/search/repositories", {
                "q": f"language:python created:>={de_la} license:{cheie} stars:>=3 fork:false",
                "per_page": 100, "page": pagina, "sort": "stars"}, pauza=7.0)
            for r in d.get("items", []):
                spdx = (r.get("license") or {}).get("spdx_id")
                if spdx in LICENTE.values() and r["created_at"] >= DE_LA and not r.get("fork"):
                    gasite[r["full_name"]] = {"proiect": r["full_name"], "creat": r["created_at"], "licenta": spdx,
                                              "ramura": r["default_branch"], "autor": r["owner"]["login"]}
            if len(d.get("items", [])) < 100:
                break
    return sorted(gasite.values(), key=lambda r: r["proiect"])


def fisiere_bune(arbore: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def bun(cale: str) -> bool:
        nume = cale.rsplit("/", 1)[-1]
        return (cale.endswith(".py") and not CAI_SCOASE.search("/" + cale) and nume not in NUME_SCOASE
                and cale != "docs/conf.py" and not re.search(r"_pb2(_grpc)?\.py$", nume))

    return [f for f in arbore if f.get("type") == "blob" and MINIM_COD <= f.get("size", 0) <= 50_000 and bun(f["path"])]


def are_licenta(arbore: list[dict[str, Any]]) -> bool:
    return any(f.get("type") == "blob" and "/" not in f["path"] and re.match(r"(licen[cs]e|copying)", f["path"], re.I)
               for f in arbore)


def generat_automat(text: str) -> bool:
    cap = text[:600].lower()
    return any(s in cap for s in ("do not edit", "auto-generated", "autogenerated", "generated by", "@generated"))


def cod_vechi(text: str) -> bool:
    """O notă de drepturi de autor dinainte de 2026 la început: cod vechi adus în proiect."""
    ani = re.findall(r"copyright\s*(?:\(c\)|©)?\s*((?:19|20)\d\d)", text[:600], re.I)
    return bool(ani) and min(int(a) for a in ani) < 2026


def set_cod(proiecte_: int = 40, fisiere_pe_proiect: int = 5, cere_: Callable = cere, spune=print) -> list[dict[str, Any]]:
    toate = proiecte_noi(cere_)
    spune(f"GitHub: {len(toate)} proiecte noi cu licență permisivă", flush=True)
    noroc = random.Random(SAMANTA)
    noroc.shuffle(toate)
    texte: list[dict[str, Any]] = []
    luate = 0
    for p in toate:
        if luate >= proiecte_:
            break
        try:
            d = cere_(f"https://api.github.com/repos/{p['proiect']}/git/trees/{p['ramura']}", {"recursive": 1}, pauza=1.0)
        except Exception as e:  # proiect șters sau ascuns între timp
            spune(f"  sar peste {p['proiect']}: {e}", flush=True)
            continue
        arbore = d.get("tree", [])
        bune = fisiere_bune(arbore)
        if not are_licenta(arbore) or not bune:
            continue
        noroc.shuffle(bune)
        din_proiect = 0
        for f in bune:
            if din_proiect >= fisiere_pe_proiect:
                break
            adresa = f"https://raw.githubusercontent.com/{p['proiect']}/{d['sha']}/{urllib.parse.quote(f['path'])}"
            try:
                text = cere_(adresa, json_=False, pauza=0.3)
            except Exception:
                continue
            if len(text.strip()) < MINIM_COD or generat_automat(text) or cod_vechi(text):
                continue
            texte.append({"text": text.strip("\n"), "proiect": p["proiect"], "fisier": f["path"], "arbore": d["sha"],
                          "adresa": adresa, "licenta": p["licenta"], "autor": p["autor"], "creat": p["creat"]})
            din_proiect += 1
        luate += din_proiect > 0
    return texte


# --- seturile -----------------------------------------------------------------------------------------------------

def scrie_set(dosar: Path, nume: str, texte: list[dict[str, Any]]) -> dict[str, Any]:
    """date/neutru/<nume>/validare.txt, o singură dată: un set scris nu se mai suprascrie."""
    cale = dosar / nume / "validare.txt"
    if cale.exists():
        raise FileExistsError(f"{cale} există deja: setul neutru se scrie o singură dată")
    cale.parent.mkdir(parents=True, exist_ok=True)
    continut = "".join(f"{t['text']}\n{SEPARATOR}\n" for t in texte)
    cale.write_text(continut, encoding="utf-8", newline="\n")
    return {"cale": cale.as_posix(), "texte": len(texte), "litere": sum(len(t["text"]) for t in texte),
            "sha256": hashlib.sha256(continut.encode("utf-8")).hexdigest(),
            "surse": [{k: v for k, v in t.items() if k != "text"} for t in texte]}


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Examenul neutru: texte create după 12 octombrie 2026.")
    parser.add_argument("--descarca", action="store_true", help="descarcă și scrie cele trei seturi (o singură dată)")
    parser.add_argument("--dosar", default="date/neutru")
    args = parser.parse_args(argv)
    if not args.descarca:
        parser.print_help()
        return 1
    dosar = Path(args.dosar)
    surse: dict[str, Any] = {"descarcat": datetime.now(timezone.utc).isoformat(timespec="seconds"), "de_la": DE_LA,
                             "samanta": SAMANTA, "seturi": {}}
    for nume, fa in (("wikipedia_ro_nou", lambda: set_wikipedia("ro", None)),
                     ("wikipedia_en_nou", lambda: set_wikipedia("en", 200)),
                     ("cod_python_nou", lambda: set_cod())):
        texte = fa()
        seturi = [(nume, texte)]
        if nume.startswith("wikipedia"):  # aceleași articole, în aceeași ordine, fără cele făcute de roboți
            seturi.append((f"{nume}_oameni", [t for t in texte if not t["robot"]]))
        for n, lista in seturi:
            surse["seturi"][n] = scrie_set(dosar, n, lista)
            s = surse["seturi"][n]
            roboti = sum(len(t["text"]) for t in lista if t.get("robot"))
            print(f"{n}: {s['texte']} texte, {s['litere']:,} litere ({roboti / max(1, s['litere']):.0%} de la roboți)",
                  flush=True)
    (dosar / "surse.json").write_text(json.dumps(surse, ensure_ascii=False, indent=1), encoding="utf-8")
    (dosar / "seturi.json").write_text(json.dumps({n: s["cale"] for n, s in surse["seturi"].items()}, indent=1),
                                       encoding="utf-8")
    print(f"Atribuirile: {dosar / 'surse.json'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
