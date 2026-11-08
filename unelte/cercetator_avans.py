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

Modul relativ (`--relativ`, S92, 8 nov 2026): pentru setările cu scară (`rata_invatare`, `incalzire_pasi`, plus cele
date cu `--scara`), valorile din spațiul cercetătorului mic se citesc ca FACTORI față de rețetă. Pe modelul mic se încearcă
valoarea mică × factor; propunerea pentru cel mare = valoarea MARE × factorul câștigător (rata la 3 cifre semnificative,
încălzirea la întreg). Setările fără scară (ex. `optimizator`) se mută ca valori, ca fără `--relativ`. Tot în modul
relativ, modelul de pornire din `cale_stare` (dacă e în afara dosarului de ieșire) devine `stare_de_pornire`: fiecare
încercare pornește din ACELAȘI fișier, care nu se scrie niciodată; starea de după încercare merge în `<iesire>/stare/`.
Fără `--relativ`, totul ca înainte.

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

# Setările cu scară: în modul relativ, valorile din spațiul cercetătorului sunt factori față de rețetă.
SETARI_CU_SCARA = ("rata_invatare", "incalzire_pasi")


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


# --------------------------------------------------------------------------- modul relativ (S92)


def _numar(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def aplica_factor(baza: Any, factor: float) -> Any:
    """Valoarea `baza` × `factor`, rotunjită: un întreg rămâne întreg (cel puțin 1), un număr cu virgulă la 3 cifre."""
    v = baza * factor
    if isinstance(baza, int):
        return max(1, int(math.floor(v + 0.5)))
    return float(f"{v:.3g}")


def setari_relative(config_mic: Config, config_mare: Config,
                    scara: tuple[str, ...] = SETARI_CU_SCARA) -> dict[tuple[str, str], dict[str, Any]]:
    """Pentru fiecare setare cu scară din spațiul cercetătorului mic: factorii, valoarea mică, valoarea mare și harta
    valoare mică → factor. Refuză un factor ≤ 0 (sau care nu e număr) și o setare fără valoare numerică pe vreun model."""
    rezultat: dict[tuple[str, str], dict[str, Any]] = {}
    for port, setari in _spatiu_cercetator(config_mic).items():
        for cheie, factori in setari.items():
            if cheie not in scara:
                continue
            for f in factori:
                if not _numar(f) or f <= 0:
                    raise Refuz(f"factorul {f!r} din spațiul „{port}.{cheie}” nu e un număr pozitiv: în modul relativ "
                                "valorile din spațiu sunt factori (ex. 0,5; 2; 4)")
            mic = config_mic.setari_port(port).get(cheie)
            mare = config_mare.setari_port(port).get(cheie)
            for ce, v, cfg in (("mică", mic, config_mic), ("mare", mare, config_mare)):
                if not _numar(v) or v <= 0:
                    raise Refuz(f"setarea „{port}.{cheie}” n-are o valoare numerică pozitivă în configurarea {ce} "
                                f"{cfg.cale_fisier} (are {v!r}): nu am la ce aplica factorul")
            harta: dict[Any, float] = {mic: 1.0}
            for f in factori:
                v = aplica_factor(mic, float(f))
                if v in harta and harta[v] != float(f):
                    raise Refuz(f"„{port}.{cheie}”: factorii {harta[v]} și {f} dau aceeași valoare mică {v} după "
                                "rotunjire")
                harta[v] = float(f)
            rezultat[(port, cheie)] = {"factori": [float(f) for f in factori], "mic": mic, "mare": mare, "harta": harta}
    return rezultat


def spatiu_absolut(spatiu: dict[str, dict[str, list[Any]]],
                   relative: dict[tuple[str, str], dict[str, Any]]) -> dict[str, dict[str, list[Any]]]:
    """Spațiul pentru cercetătorul de pe modelul mic: factorii înlocuiți cu valorile mici (restul neschimbat)."""
    out = copy.deepcopy(spatiu)
    for (port, cheie), r in relative.items():
        out[port][cheie] = [aplica_factor(r["mic"], f) for f in r["factori"]]
    return out


def info_relativ(setari: dict[str, dict[str, Any]],
                 relative: dict[tuple[str, str], dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Pentru o rețetă de pe modelul mic: factorul și valoarea pe fiecare model, la fiecare setare cu scară."""
    out = {}
    for (port, cheie), r in relative.items():
        mic = (setari or {}).get(port, {}).get(cheie, r["mic"])
        factor = r["harta"].get(mic, mic / r["mic"])
        out[f"{port}.{cheie}"] = {"factor": factor, "mic": mic, "mare": aplica_factor(r["mare"], factor)}
    return out


def schimbari_mari(schimbari: dict[str, dict[str, Any]], setari: dict[str, dict[str, Any]],
                   relative: dict[tuple[str, str], dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Schimbările câștigătorului mutate pe modelul mare: setările cu scară = valoarea mare × factor; restul ca valori."""
    info = info_relativ(setari, relative)
    out: dict[str, dict[str, Any]] = {}
    for port, valori in schimbari.items():
        for cheie, v in valori.items():
            out.setdefault(port, {})[cheie] = info[f"{port}.{cheie}"]["mare"] if (port, cheie) in relative else v
    return out


def pregateste_relativ(config_mic: Config, iesire: Path, relative: dict[tuple[str, str], dict[str, Any]]) -> Config:
    """Copia configurării mici pentru modul relativ: spațiul în valori mici și modelul de pornire doar citit
    (`stare_de_pornire`), cu starea de după fiecare încercare în `<iesire>/stare/`."""
    noua = copy.deepcopy(config_mic)
    cerc = noua.porturi["cercetator"]
    cerc["setari"] = {**cerc.get("setari", {}), "spatiu": spatiu_absolut(_spatiu_cercetator(config_mic), relative)}
    model = dict(noua.porturi["model"].get("setari", {}))
    cale = model.get("cale_stare")
    if cale and not _sub(Path(cale), iesire) and not model.get("stare_de_pornire"):
        model["stare_de_pornire"] = str(cale)
        model["cale_stare"] = str((iesire / "stare" / Path(cale).name).resolve())
        noua.porturi["model"]["setari"] = model
    return noua


def retete_proba(config: Config, incercari: int) -> list[dict[str, Any]]:
    """Rețetele pe care le-ar încerca cercetătorul (prin registru, nu din module/), dacă niciuna nu e păstrată: punctul
    de plecare + încercari − 1 propuneri. O rețetă păstrată schimbă baza celor de după (le combină)."""
    from kronos.registru import Registru

    cerc = Registru().creeaza("cercetator", config.porturi["cercetator"]["modul"],
                              config.setari_port("cercetator")).instanta
    porturi = config.paznic.get("porturi_modificabile", ["model"])
    baza = {p: copy.deepcopy(config.setari_port(p)) for p in porturi}
    retete = [{"descriere": "punct de plecare", "setari": copy.deepcopy(baza)}]
    istoric: list[dict[str, Any]] = [{"setari": copy.deepcopy(baza)}]
    for _ in range(max(0, incercari - 1)):
        p = cerc.propune(copy.deepcopy(istoric), copy.deepcopy(baza))
        if not p.modificari:
            break
        setari = copy.deepcopy(baza)
        for port, valori in p.modificari.items():
            setari.setdefault(port, {}).update(valori)
        retete.append({"descriere": p.descriere, "setari": setari})
        istoric.append({"setari": setari})
    return retete


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
              mai_mic_e_mai_bun: bool,
              relative: dict[tuple[str, str], dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    randuri = []
    for f in fise:
        s = (f.get("scoruri") or {}).get(scor)
        valid = isinstance(s, (int, float)) and not isinstance(s, bool) and math.isfinite(s)
        extra = {"relativ": info_relativ(f.get("setari") or {}, relative)} if relative else {}
        randuri.append({
            **extra,
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
        if x.get("relativ"):
            sch += " — " + "; ".join(f"{k}: ×{v['factor']:g} (mic {v['mic']}, mare {v['mare']})"
                                     for k, v in x["relativ"].items())
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
            orchestrator_cls: Any = None, relativ: bool = False,
            scara: tuple[str, ...] = SETARI_CU_SCARA) -> dict[str, Any]:
    from kronos.orchestrator import Orchestrator

    orchestrator_cls = orchestrator_cls or Orchestrator
    iesire = iesire.resolve()
    if (iesire / "clasament.json").exists():
        raise Refuz(f"{iesire / 'clasament.json'} există deja: nu scriu peste o rulare veche (alege alt --iesire)")
    verifica_spatiu(config_mic, config_mare)
    pornire = amprenta_pornire(config_mic)
    relative = setari_relative(config_mic, config_mare, scara) if relativ else {}
    if relativ:
        de_rulat = pregateste_relativ(config_mic, iesire, relative)
        sursa = de_rulat.setari_port("model").get("stare_de_pornire")
        if sursa and not Path(sursa).exists():
            raise Refuz(f"modelul de pornire {sursa} nu există: nu pornesc de la zero pe tăcute")
    else:
        de_rulat = config_mic
    rulare = pregateste_config_mic(de_rulat, iesire, minute)
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
    randuri = clasament(fise, baza, scor, mai_mic, relative)
    castigator = next((x for x in randuri if x["scor"] is not None), None)
    if castigator is None:
        raise Refuz("nicio încercare n-a dat un scor valid: nu am ce propune")
    schimbari = (schimbari_mari(castigator["schimbari"], castigator["setari"], relative) if relativ
                 else castigator["schimbari"])
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
    if relativ:
        rezultat["relativ"] = {f"{p}.{k}": {kk: vv for kk, vv in r.items() if kk != "harta"}
                               for (p, k), r in relative.items()}
        rezultat["propunere"]["schimbari_pe_mic"] = castigator["schimbari"]
    (iesire / "clasament.json").write_text(json.dumps(rezultat, ensure_ascii=False, indent=2, default=str),
                                           encoding="utf-8")
    (iesire / "clasament.md").write_text(_md(rezultat), encoding="utf-8")
    return rezultat


def proba(config_mic: Config, config_mare: Config, incercari: int, minute: float, iesire: Path,
          relativ: bool = False, scara: tuple[str, ...] = SETARI_CU_SCARA) -> str:
    """Ce ar face, fără să antreneze și fără să scrie nimic."""
    perechi = verifica_spatiu(config_mic, config_mare)
    pornire = amprenta_pornire(config_mic)
    spatiu = _spatiu_cercetator(config_mic)
    if relativ:
        relative = setari_relative(config_mic, config_mare, scara)
        de_rulat = pregateste_relativ(config_mic, iesire.resolve(), relative)
        rulare = pregateste_config_mic(de_rulat, iesire.resolve(), minute)
        return _proba_relativ(config_mic, config_mare, de_rulat, rulare, relative, incercari, minute, iesire, pornire)
    rulare = pregateste_config_mic(config_mic, iesire.resolve(), minute)
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


def _proba_relativ(config_mic: Config, config_mare: Config, de_rulat: Config, rulare: Config,
                   relative: dict[tuple[str, str], dict[str, Any]], incercari: int, minute: float, iesire: Path,
                   pornire: dict[str, Any]) -> str:
    model = de_rulat.setari_port("model")
    sursa = model.get("stare_de_pornire")
    retete = retete_proba(de_rulat, incercari)
    linii = [
        "PROBA în modul RELATIV (nimic antrenat, nimic scris). Cu --porneste aș face:",
        f"  modelul mic: {config_mic.cale_fisier} ({config_mic.porturi['model']['modul']}), linia {config_mic.nume}",
        f"  cercetătorul: {config_mic.porturi['cercetator']['modul']}",
        "  setări cu scară (factori față de rețetă):",
    ]
    for (p, k), r in relative.items():
        linii.append(f"    {p}.{k}: mic {r['mic']}, mare {r['mare']}; factori {r['factori']} → pe mic "
                     f"{[aplica_factor(r['mic'], f) for f in r['factori']]}, pe mare "
                     f"{[aplica_factor(r['mare'], f) for f in r['factori']]}")
    linii += [
        f"  modelul de pornire: {pornire['descriere']}"
        + (f" (SHA-256 {pornire['sha256']})" if pornire.get("sha256") else ""),
        f"  fiecare încercare pornește din: {sursa or model.get('cale_stare') or 'zero'}"
        + (" (doar citit: stare_de_pornire)" if sursa else "")
        + (f"; starea de după încercare → {model.get('cale_stare')}" if sursa else ""),
        f"  încercări: {incercari}, {minute:g} min antrenare fiecare → cel puțin ~{incercari * minute:g} min",
        f"  rețetele (dacă niciuna nu e păstrată; una păstrată devine baza celor de după):",
    ]
    for i, r in enumerate(retete, start=1):
        info = info_relativ(r["setari"], relative)
        linii.append(f"    {i}. {r['descriere']}: " + "; ".join(
            f"{k} ×{v['factor']:g} (mic {v['mic']}, mare {v['mare']})" for k, v in info.items()))
    linii += [
        f"  scriu doar în: {iesire.resolve()} (jurnalul mic în {rulare.director_lucru})",
        f"  propunerea pentru: {config_mare.cale_fisier} → {iesire / 'propunere_mare.toml'} (valoarea mare × factorul "
        "câștigător; NU o rulez)",
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
    ap.add_argument("--relativ", action="store_true",
                    help="spațiul setărilor cu scară = factori față de rețetă (mic × factor pe mic, mare × factor pe mare)")
    ap.add_argument("--scara", nargs="*", default=[],
                    help=f"setări cu scară în plus față de {', '.join(SETARI_CU_SCARA)} (doar cu --relativ)")
    a = ap.parse_args(argv)
    scara = SETARI_CU_SCARA + tuple(s for s in a.scara if s not in SETARI_CU_SCARA)
    if a.procesor:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    try:
        if a.incercari < 1:
            raise Refuz("--incercari trebuie să fie cel puțin 1")
        if not (a.minute_pe_incercare > 0):
            raise Refuz("--minute-pe-incercare trebuie să fie pozitiv")
        mic, mare = citeste_config(a.config_mic), citeste_config(a.config_mare)
        iesire = Path(a.iesire)
        if a.scara and not a.relativ:
            raise Refuz("--scara are sens doar cu --relativ")
        if not a.porneste:
            print(proba(mic, mare, a.incercari, a.minute_pe_incercare, iesire, a.relativ, scara))
            return 0
        r = ruleaza(mic, mare, a.incercari, a.minute_pe_incercare, iesire, relativ=a.relativ, scara=scara)
    except Refuz as e:
        print(f"REFUZ: {e}", file=sys.stderr)
        return 2
    print(_md(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
