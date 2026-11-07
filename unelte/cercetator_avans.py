"""Cercetătorul cu model trimis în avans (S91, C-85 pasul 4 partea a, aprobat de Adrian 6 nov 2026).

Ideea: o încercare pe modelul mare costă o oră pe placă. Așa că rețetele se încearcă întâi pe un model MIC, „trimis
în avans”, iar pe cel mare merge doar câștigătorul. Unealta asta face partea de pe modelul mic și scrie propunerea
pentru cel mare. Propunerea NU se rulează: o pornește cineva separat (o sarcină cu pre-înregistrare).

Ce face, cu `--porneste`:
  1. Citește `--config-mic` și `--config-mare` (doar citite, nu se schimbă).
  2. Verifică ÎNAINTE de orice antrenare că setările pe care le poate schimba cercetătorul modelului mic au sens pe
     cel mare: nu sunt de mărimea modelului (n_straturi, n_emb...) și există în aceeași secțiune din configurarea mare.
     Altfel refuză, cu un mesaj clar.
  3. Rulează platforma Kronos (Orchestrator, cu Registru și Jurnal) pe configurarea mică, cu `--incercari N`
     experimente (punctul de plecare + N − 1 propuneri ale cercetătorului din `--config-mic`) și
     `--minute-pe-incercare M` (bugetul de antrenare al fiecărui experiment). TOT ce scrie platforma (jurnalul mic,
     amprentele, modelele păstrate, cache-ul) merge în `<iesire>/`, nu în `lucru/`. Amprentele examenelor aprobate se
     copiază din dosarul de lucru al configurării mici, ca un examen schimbat să fie refuzat și aici.
  4. Scrie `<iesire>/clasament.json` + `clasament.md`: fiecare rețetă, scorul, timpul, decizia și amprenta modelului
     de pornire (SHA-256 al fișierului din `cale_stare`, sau „de la zero”).
  5. Scrie `<iesire>/propunere_mare.toml` = configurarea mare cu DOAR setările câștigătorului schimbate (restul
     fișierului e copiat literă cu literă) și `<iesire>/propunere_mare.diff`.

Implicit e `--proba`: arată ce ar face și verifică setările, fără să antreneze și fără să scrie nimic.

Comenzi:
  python -X utf8 unelte/cercetator_avans.py --config-mic config/avans_proba_mic.toml \
      --config-mare config/avans_proba_mare.toml --incercari 5 --minute-pe-incercare 1 --iesire lucru/avans/demo
  (același, cu --porneste: rulează; --procesor = fără placă, CUDA_VISIBLE_DEVICES=-1)

Nu importă nimic din module/: modulele vin doar prin configurare și registru (regula nucleului).
"""

from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import json
import math
import os
import re
import shutil
import sys
import time
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.config import Config, citeste_config  # noqa: E402

# Setări care țin de mărimea sau de identitatea modelului: un câștig al lor pe modelul mic nu spune nimic despre cel
# mare (sau l-ar schimba în alt model). Se refuză.
SETARI_INTERZISE = frozenset({
    "n_straturi", "n_capete", "n_emb", "context", "vocab", "vocabular", "tokenizer", "cale_tokenizer", "cale_stare",
    "director_cache", "categorii_memorie", "n_emb_memorie", "adancime_memorie", "memorie",
})

FARA_PORNIRE = "de la zero (fără model de pornire)"


class Refuz(Exception):
    """Ceva nu are sens sau nu e voie; mesajul spune exact ce."""


# --------------------------------------------------------------------------- verificări


def _sha256(cale: Path) -> str:
    h = hashlib.sha256()
    with cale.open("rb") as f:
        for bucata in iter(lambda: f.read(1 << 20), b""):
            h.update(bucata)
    return h.hexdigest()


def _spatiu_cercetator(config: Config) -> dict[str, dict[str, list[Any]]]:
    spatiu = config.setari_port("cercetator").get("spatiu")
    return spatiu if isinstance(spatiu, dict) else {}


def verifica_setare(port: str, cheie: str, config_mare: Config, interzise: frozenset[str] = SETARI_INTERZISE) -> None:
    """Refuză o setare care nu are sens pe modelul mare."""
    if cheie in interzise:
        raise Refuz(f"setarea „{port}.{cheie}” ține de mărimea/identitatea modelului: un câștig pe modelul mic nu se "
                    f"poate muta pe cel mare. Scoate-o din spațiul cercetătorului din configurarea mică.")
    if port not in config_mare.porturi:
        raise Refuz(f"portul „{port}” nu există în configurarea mare {config_mare.cale_fisier}")
    if cheie not in config_mare.setari_port(port):
        raise Refuz(f"setarea „{port}.{cheie}” nu există în configurarea mare {config_mare.cale_fisier} "
                    f"(acolo modulul e {config_mare.porturi[port]['modul']}): nu are sens pe modelul mare.")


def verifica_spatiu(config_mic: Config, config_mare: Config) -> list[tuple[str, str]]:
    """Toate setările pe care le poate schimba cercetătorul mic; refuză dacă vreuna nu are sens pe cel mare."""
    spatiu = _spatiu_cercetator(config_mic)
    if not spatiu:
        raise Refuz(f"cercetătorul din {config_mic.cale_fisier} nu are „spatiu = {{port: {{setare: [valori]}}}}”: "
                    "nu pot verifica dinainte ce va schimba")
    perechi = [(port, cheie) for port, setari in spatiu.items() for cheie in setari]
    for port, cheie in perechi:
        verifica_setare(port, cheie, config_mare)
    return perechi


def amprenta_pornire(config_mic: Config) -> dict[str, Any]:
    cale = config_mic.setari_port("model").get("cale_stare")
    if not cale:
        return {"cale": None, "sha256": None, "descriere": FARA_PORNIRE}
    fisier = Path(cale)
    if not fisier.exists():
        return {"cale": str(cale), "sha256": None, "descriere": FARA_PORNIRE + f" — {cale} nu există încă"}
    return {"cale": str(cale), "sha256": _sha256(fisier), "octeti": fisier.stat().st_size,
            "descriere": f"{cale}"}


def _sub(cale: Path, dosar: Path) -> bool:
    cale, dosar = cale.resolve(), dosar.resolve()
    return cale == dosar or dosar in cale.parents


def pregateste_config_mic(config_mic: Config, iesire: Path, minute: float) -> Config:
    """Copia configurării mici cu tot ce se scrie mutat în `iesire` și bugetul de M minute pe încercare."""
    buget = minute * 60.0
    timp_max = float(config_mic.paznic.get("timp_max_secunde", 600))
    if buget > timp_max:
        raise Refuz(f"--minute-pe-incercare {minute:g} = {buget:.0f} s, dar paznicul din {config_mic.cale_fisier} "
                    f"oprește orice antrenare peste timp_max_secunde = {timp_max:.0f} s")
    cale_stare = config_mic.setari_port("model").get("cale_stare")
    if cale_stare and not _sub(Path(cale_stare), iesire):
        raise Refuz(f"modelul mic are cale_stare = {cale_stare}, în afara dosarului de ieșire {iesire}: încercările "
                    "ar putea scrie peste el. Copiază întâi modelul de pornire în dosarul de ieșire și pune "
                    "cale_stare acolo (o configurare nouă avans_*).")
    if config_mic.porneste_din is not None:
        raise Refuz("configurarea mică are porneste_din: jurnalul mic din dosarul de ieșire nu are acel experiment")
    noua = copy.deepcopy(config_mic)
    noua.director_lucru = (iesire / "kronos_lucru").resolve()
    noua.buget_antrenare_secunde = buget
    if "stocare" in noua.porturi:
        noua.porturi["stocare"].setdefault("setari", {})
        noua.porturi["stocare"]["setari"] = {**noua.porturi["stocare"].get("setari", {}),
                                             "director": str((iesire / "stocare").resolve())}
    model = noua.porturi["model"].setdefault("setari", {})
    if "director_cache" in model:
        noua.porturi["model"]["setari"] = {**model, "director_cache": str((iesire / "cache").resolve())}
    return noua


# --------------------------------------------------------------------------- propunerea pentru modelul mare

_VALOARE = r'"(?:[^"\\]|\\.)*"|\'[^\']*\'|[^,}\s#\]]+'


def valoare_toml(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if not math.isfinite(v):
            raise Refuz(f"valoarea {v} nu se poate scrie în TOML")
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    raise Refuz(f"valoarea {v!r} ({type(v).__name__}) nu se poate pune în propunere (doar numere, text, adevărat/fals)")


def inlocuieste_setare(text: str, port: str, cheie: str, valoare: Any) -> str:
    """Schimbă DOAR valoarea `cheie` din setările portului; restul textului rămâne literă cu literă."""
    linii = text.splitlines(keepends=True)
    sectiune = None
    potriviri: list[tuple[int, re.Match[str]]] = []
    for i, linie in enumerate(linii):
        antet = re.match(r"^\s*\[([^\[\]]+)\]\s*(#.*)?$", linie)
        if antet:
            sectiune = antet.group(1).strip()
            continue
        if sectiune == f"porturi.{port}" and re.match(r"^\s*setari\s*=\s*\{", linie):
            m = re.search(rf"(?<![\w.]){re.escape(cheie)}\s*=\s*({_VALOARE})", linie)
        elif sectiune == f"porturi.{port}.setari":
            m = re.match(rf"^\s*{re.escape(cheie)}\s*=\s*({_VALOARE})", linie)
        else:
            m = None
        if m:
            potriviri.append((i, m))
    if len(potriviri) != 1:
        raise Refuz(f"nu găsesc exact o dată „{cheie} = …” în setările portului {port} din configurarea mare "
                    f"(găsit de {len(potriviri)} ori)")
    i, m = potriviri[0]
    linie = linii[i]
    linii[i] = linie[:m.start(1)] + valoare_toml(valoare) + linie[m.end(1):]
    return "".join(linii)


def scrie_propunere(config_mare: Config, schimbari: dict[str, dict[str, Any]], antet: str) -> tuple[str, str]:
    """Textul configurării mari cu doar `schimbari` aplicate (+ un antet de comentarii) și diff-ul față de original."""
    original = Path(config_mare.cale_fisier).read_text(encoding="utf-8")
    text = original
    for port, setari in schimbari.items():
        for cheie, valoare in setari.items():
            verifica_setare(port, cheie, config_mare)
            text = inlocuieste_setare(text, port, cheie, valoare)
    text = "".join(f"# {r}\n" if r else "#\n" for r in antet.splitlines()) + text
    # Verificarea: citit înapoi, fișierul diferă de cel mare DOAR prin aceste setări.
    asteptat = tomllib.loads(original)
    for port, setari in schimbari.items():
        asteptat["porturi"][port]["setari"].update(setari)
    if tomllib.loads(text) != asteptat:
        raise Refuz("propunerea scrisă nu iese identică cu configurarea mare + schimbările (nu o scriu)")
    diff = "".join(difflib.unified_diff(original.splitlines(keepends=True), text.splitlines(keepends=True),
                                        fromfile=str(config_mare.cale_fisier), tofile="propunere_mare.toml"))
    return text, diff


# --------------------------------------------------------------------------- clasamentul


def _cheie(setari: Any) -> str:
    return json.dumps(setari, sort_keys=True, ensure_ascii=False)


def schimbari_fata_de(setari: dict[str, dict[str, Any]], baza: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for port, valori in (setari or {}).items():
        for cheie, v in valori.items():
            if baza.get(port, {}).get(cheie, object()) != v:
                out.setdefault(port, {})[cheie] = v
    return out


def clasament(fise: list[dict[str, Any]], baza: dict[str, dict[str, Any]], scor: str,
              mai_mic_e_mai_bun: bool) -> list[dict[str, Any]]:
    randuri = []
    for f in fise:
        s = (f.get("scoruri") or {}).get(scor)
        valid = isinstance(s, (int, float)) and not isinstance(s, bool) and math.isfinite(s)
        randuri.append({
            "id": f.get("id"),
            "propunere": (f.get("propunere") or {}).get("descriere"),
            "schimbari": schimbari_fata_de(f.get("setari") or {}, baza),
            "setari": f.get("setari"),
            "scor": s if valid else None,
            "decizie": f.get("decizie"),
            "motiv": f.get("motiv"),
            "secunde_antrenare": (f.get("consum") or {}).get("durata_antrenare_secunde"),
            "secunde_total": f.get("durata_totala_secunde"),
        })
    chei = [_cheie(r["setari"]) for r in randuri if r["setari"] is not None]
    if len(chei) != len(set(chei)):
        raise Refuz("cercetătorul a repetat o rețetă: clasamentul nu e valid")
    cu_scor = sorted((r for r in randuri if r["scor"] is not None), key=lambda r: r["scor"],
                     reverse=not mai_mic_e_mai_bun)
    fara = [r for r in randuri if r["scor"] is None]
    for loc, r in enumerate(cu_scor, start=1):
        r["loc"] = loc
    for r in fara:
        r["loc"] = None
    return cu_scor + fara


def _md(rezultat: dict[str, Any]) -> str:
    r = rezultat
    linii = [
        f"# Clasament — cercetătorul cu model trimis în avans ({r['scris']})",
        "",
        f"- configurarea mică: `{r['config_mic']}` (linia `{r['linie_mica']}`), examenul `{r['scor']}` "
        f"({'mai mic e mai bun' if r['mai_mic_e_mai_bun'] else 'mai mare e mai bun'})",
        f"- configurarea mare (doar citită): `{r['config_mare']}`",
        f"- încercări: {r['incercari_cerute']} cerute, {r['incercari_facute']} făcute; {r['minute_pe_incercare']:g} min "
        f"antrenare pe încercare; durata totală {r['secunde_total']:.0f} s",
        f"- modelul de pornire: {r['pornire']['descriere']}"
        + (f" (SHA-256 `{r['pornire']['sha256']}`)" if r['pornire'].get('sha256') else ""),
        "",
        "| loc | # | rețeta (schimbări față de configurarea mică) | scor | decizia Kronos | antrenare (s) | total (s) |",
        "|---|---|---|---|---|---|---|",
    ]
    for x in r["clasament"]:
        sch = ", ".join(f"{p}.{k} = {v}" for p, s in x["schimbari"].items() for k, v in s.items()) or "punctul de plecare"
        scor = f"{x['scor']:.4f}" if x["scor"] is not None else "—"
        linii.append(f"| {x['loc'] or '—'} | {x['id']} | {sch} | {scor} | {x['decizie']} | "
                     f"{x['secunde_antrenare'] if x['secunde_antrenare'] is not None else '—'} | {x['secunde_total']} |")
    linii += ["", "## Propunerea pentru modelul mare (NU a fost rulată)", ""]
    p = r["propunere"]
    if p["schimbari"]:
        linii.append("Setările câștigătorului: " + ", ".join(
            f"`{port}.{k} = {v}`" for port, s in p["schimbari"].items() for k, v in s.items()) + ".")
    else:
        linii.append("Câștigătorul e chiar punctul de plecare: nicio schimbare de propus.")
    linii += ["", "```diff", p["diff"].rstrip("\n") or "(fără diferențe)", "```", ""]
    return "\n".join(linii)


# --------------------------------------------------------------------------- rularea


def ruleaza(config_mic: Config, config_mare: Config, incercari: int, minute: float, iesire: Path,
            orchestrator_cls: Any = None) -> dict[str, Any]:
    from kronos.orchestrator import Orchestrator

    orchestrator_cls = orchestrator_cls or Orchestrator
    iesire = iesire.resolve()
    if (iesire / "clasament.json").exists():
        raise Refuz(f"{iesire / 'clasament.json'} există deja: nu scriu peste o rulare veche (alege alt --iesire)")
    verifica_spatiu(config_mic, config_mare)
    rulare = pregateste_config_mic(config_mic, iesire, minute)
    pornire = amprenta_pornire(config_mic)
    iesire.mkdir(parents=True, exist_ok=True)
    rulare.director_lucru.mkdir(parents=True, exist_ok=True)
    amprente = Path(config_mic.director_lucru) / "amprente.json"
    if amprente.exists():  # examenele aprobate rămân aprobate și aici; unul schimbat e refuzat
        shutil.copyfile(amprente, rulare.director_lucru / "amprente.json")

    start = time.perf_counter()
    o = orchestrator_cls(rulare)
    if o.cel_mai_bun is not None:
        raise Refuz(f"jurnalul mic din {rulare.director_lucru} are deja experimente pe linia {rulare.nume}")
    baza = copy.deepcopy(o.setari_curente)
    fise = o.ruleaza(numar_experimente=max(0, incercari - 1))
    secunde = time.perf_counter() - start

    scor, mai_mic = o.examen.scor_principal, bool(o.examen.mai_mic_e_mai_bun)
    randuri = clasament(fise, baza, scor, mai_mic)
    castigator = next((x for x in randuri if x["scor"] is not None), None)
    if castigator is None:
        raise Refuz("nicio încercare n-a dat un scor valid: nu am ce propune")
    schimbari = castigator["schimbari"]
    scris = datetime.now().strftime("%Y-%m-%d %H:%M")
    antet = (f"PROPUNERE scrisă de unelte/cercetator_avans.py la {scris} — NU a fost rulată.\n"
             f"Copie a {config_mare.cale_fisier} cu DOAR setările câștigătorului de pe modelul mic schimbate.\n"
             f"Modelul mic: {config_mic.cale_fisier}, câștigătorul #{castigator['id']}, {scor} = {castigator['scor']:.4f}.\n"
             f"Se pornește doar printr-o sarcină separată, cu pre-înregistrare.")
    text, diff = scrie_propunere(config_mare, schimbari, antet)
    (iesire / "propunere_mare.toml").write_text(text, encoding="utf-8")
    (iesire / "propunere_mare.diff").write_text(diff, encoding="utf-8")

    rezultat = {
        "scris": scris,
        "config_mic": str(config_mic.cale_fisier),
        "config_mare": str(config_mare.cale_fisier),
        "linie_mica": rulare.nume,
        "scor": scor,
        "mai_mic_e_mai_bun": mai_mic,
        "incercari_cerute": incercari,
        "incercari_facute": len(fise),
        "minute_pe_incercare": minute,
        "secunde_total": round(secunde, 1),
        "pornire": pornire,
        "clasament": randuri,
        "castigator": castigator["id"],
        "propunere": {"fisier": "propunere_mare.toml", "schimbari": schimbari, "diff": diff},
    }
    (iesire / "clasament.json").write_text(json.dumps(rezultat, ensure_ascii=False, indent=2, default=str),
                                           encoding="utf-8")
    (iesire / "clasament.md").write_text(_md(rezultat), encoding="utf-8")
    return rezultat


def proba(config_mic: Config, config_mare: Config, incercari: int, minute: float, iesire: Path) -> str:
    """Ce ar face, fără să antreneze și fără să scrie nimic."""
    perechi = verifica_spatiu(config_mic, config_mare)
    rulare = pregateste_config_mic(config_mic, iesire.resolve(), minute)
    pornire = amprenta_pornire(config_mic)
    spatiu = _spatiu_cercetator(config_mic)
    linii = [
        "PROBA (nimic antrenat, nimic scris). Cu --porneste aș face:",
        f"  modelul mic: {config_mic.cale_fisier} ({config_mic.porturi['model']['modul']}), linia {config_mic.nume}",
        f"  cercetătorul: {config_mic.porturi['cercetator']['modul']}",
        f"  setări încercate (toate au sens pe cel mare): "
        + ", ".join(f"{p}.{k} ∈ {spatiu[p][k]}" for p, k in perechi),
        f"  încercări: {incercari} (punctul de plecare + {max(0, incercari - 1)} propuneri), "
        f"{minute:g} min antrenare fiecare → cel puțin ~{incercari * minute:g} min",
        f"  modelul de pornire: {pornire['descriere']}",
        f"  scriu doar în: {iesire.resolve()} (jurnalul mic în {rulare.director_lucru})",
        f"  propunerea pentru: {config_mare.cale_fisier} → {iesire / 'propunere_mare.toml'} (NU o rulez)",
    ]
    return "\n".join(linii)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config-mic", required=True)
    ap.add_argument("--config-mare", required=True)
    ap.add_argument("--incercari", type=int, required=True)
    ap.add_argument("--minute-pe-incercare", type=float, required=True)
    ap.add_argument("--iesire", required=True)
    mod = ap.add_mutually_exclusive_group()
    mod.add_argument("--proba", action="store_true", help="implicit: arată ce ar face, nu antrenează")
    mod.add_argument("--porneste", action="store_true", help="antrenează pe modelul mic și scrie propunerea")
    ap.add_argument("--procesor", action="store_true", help="fără placă (CUDA_VISIBLE_DEVICES=-1)")
    a = ap.parse_args(argv)
    if a.procesor:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    try:
        if a.incercari < 1:
            raise Refuz("--incercari trebuie să fie cel puțin 1")
        if not (a.minute_pe_incercare > 0):
            raise Refuz("--minute-pe-incercare trebuie să fie pozitiv")
        mic, mare = citeste_config(a.config_mic), citeste_config(a.config_mare)
        iesire = Path(a.iesire)
        if not a.porneste:
            print(proba(mic, mare, a.incercari, a.minute_pe_incercare, iesire))
            return 0
        r = ruleaza(mic, mare, a.incercari, a.minute_pe_incercare, iesire)
    except Refuz as e:
        print(f"REFUZ: {e}", file=sys.stderr)
        return 2
    print(_md(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
