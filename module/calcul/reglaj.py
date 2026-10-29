"""S48: reglajul CCM — ce variantă și câte fire folosește `inferenta_ccm` pe calculatorul acesta.

Fișierul `lucru/ccm/reglaj-<calculator>.json` (în afara Git) se scrie din măsurarea bancului (S47), nu de mână.
Formatul e descris în docs/CCM_plan.md („Formatul reglajului”). `alege` spune dacă reglajul se poate folosi pentru un
model anume; la ORICE nepotrivire (lipsește, alt calculator, alte nuclee, alt model, variantă necunoscută sau
neacceptată, fire care nu se pot pune) răspunsul e „nu”, cu motivele, iar modulul ia calea referinței (`inferenta_kgr1`).

Folosire:
    python -X utf8 -m module.calcul.reglaj scrie --banc lucru/ccm/s47.json        # → lucru/ccm/reglaj-<calculator>.json
    python -X utf8 -m module.calcul.reglaj verifica --kgr lucru/export/kronos_459_q8_0.kgr
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sys
import time
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parents[2]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.calcul import fire  # noqa: E402

FORMAT = "ccm-reglaj"
VERSIUNE = 1
OPERATII = ("inmultire",)  # ce operații știe reglajul de acum (S47: doar înmulțirea)


def nume_calculator() -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", platform.node().lower()).strip("-") or "necunoscut"


def cale_implicita() -> Path:
    return RADACINA / "lucru" / "ccm" / f"reglaj-{nume_calculator()}.json"


def sha256(cale: str | Path) -> str:
    h = hashlib.sha256()
    with open(cale, "rb") as f:
        for bucata in iter(lambda: f.read(1 << 22), b""):
            h.update(bucata)
    return h.hexdigest()


def din_banc(banc: dict[str, Any], sursa: str, kgr: str | Path | None = None) -> dict[str, Any]:
    """Reglajul din rezultatul `banc toate`: varianta + firele cele mai rapide pe timpul total, doar dacă e acceptată."""
    alesa = banc.get("cea_mai_rapida_pe_total")
    if not alesa:
        raise ValueError("bancul n-a acceptat nicio variantă: nu am ce scrie în reglaj")
    r = next(r for r in banc["rezultate"] if r["varianta"] == alesa["varianta"] and r["fire"] == alesa["fire"])
    if not r["acceptata"]:
        raise ValueError("varianta aleasă nu e acceptată")
    kgr = Path(kgr or banc["kgr"])
    m = r["masurare"]
    return {
        "format": FORMAT, "versiune": VERSIUNE, "calculator": nume_calculator(), "nuclee": os.cpu_count(),
        "scris": time.strftime("%Y-%m-%dT%H:%M"), "sursa_masurarii": sursa,
        "model": {"nume": kgr.name, "sha256": sha256(kgr)},
        "toleranta_logits": banc["toleranta_logits"],
        "operatii": {"inmultire": {
            "varianta": r["varianta"], "fire": r["fire"], "acceptata": True,
            "dif_logits_max": r["verificare_model"]["dif_logits_max"],
            "total_secunde": m["total"]["median"], "simboluri_pe_secunda": m["simboluri_pe_secunda"]["median"],
            "fata_de_referinta_total": r.get("fata_de_referinta_total"),
        }},
    }


def motive_nepotrivire(reglaj: Any, kgr: str | Path) -> list[str]:
    """Gol = reglajul se poate folosi pentru modelul `kgr` pe calculatorul acesta."""
    from module.calcul.variante import VARIANTE

    if not isinstance(reglaj, dict):
        return ["reglajul nu e un obiect JSON"]
    motive = []
    if reglaj.get("format") != FORMAT or reglaj.get("versiune") != VERSIUNE:
        motive.append(f"alt format: {reglaj.get('format')!r} versiunea {reglaj.get('versiune')!r}")
    if reglaj.get("calculator") != nume_calculator():
        motive.append(f"alt calculator: {reglaj.get('calculator')!r} (aici {nume_calculator()!r})")
    if reglaj.get("nuclee") != os.cpu_count():
        motive.append(f"alte nuclee: {reglaj.get('nuclee')!r} (aici {os.cpu_count()})")
    model = reglaj.get("model") if isinstance(reglaj.get("model"), dict) else {}
    if model.get("sha256") != sha256(kgr):
        motive.append(f"alt model: reglajul e pentru {model.get('nume')!r}")
    operatii = reglaj.get("operatii") if isinstance(reglaj.get("operatii"), dict) else {}
    if set(operatii) - set(OPERATII):
        motive.append(f"operații necunoscute: {sorted(set(operatii) - set(OPERATII))}")
    inm = operatii.get("inmultire")
    if not isinstance(inm, dict):
        return motive + ["lipsește operația „inmultire”"]
    if inm.get("varianta") not in VARIANTE:
        motive.append(f"variantă necunoscută: {inm.get('varianta')!r}")
    if inm.get("acceptata") is not True:
        motive.append("varianta nu e acceptată de banc")
    try:
        n = fire.din_text(str(inm.get("fire")))
        if n is not None and not fire.disponibil():
            motive.append("firele nu se pot schimba în procesul acesta")
    except ValueError as e:
        motive.append(str(e))
    return motive


def alege(cale_reglaj: str | Path, kgr: str | Path) -> dict[str, Any]:
    """{"folosit", "varianta", "fire", "motive", "reglaj"}: ce poate folosi modulul pentru `kgr`."""
    rez = {"folosit": False, "varianta": None, "fire": None, "motive": [], "reglaj": str(cale_reglaj)}
    cale_reglaj = Path(cale_reglaj)
    if not cale_reglaj.exists():
        rez["motive"] = [f"fără reglaj: {cale_reglaj.name}"]
        return rez
    try:
        reglaj = json.loads(cale_reglaj.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        rez["motive"] = [f"reglajul nu se poate citi: {e}"]
        return rez
    rez["motive"] = motive_nepotrivire(reglaj, kgr)
    if not rez["motive"]:
        inm = reglaj["operatii"]["inmultire"]
        rez.update(folosit=True, varianta=inm["varianta"], fire=str(inm["fire"]))
    return rez


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="comanda", required=True)
    s = sub.add_parser("scrie")
    s.add_argument("--banc", required=True, help="rezultatul `banc toate` (de ex. lucru/ccm/s47.json)")
    s.add_argument("--kgr", default=None, help="modelul măsurat (implicit cel din banc)")
    s.add_argument("--iesire", default=None)
    s.add_argument("--inlocuieste", action="store_true")
    v = sub.add_parser("verifica")
    v.add_argument("--kgr", default="lucru/export/kronos_459_q8_0.kgr")
    v.add_argument("--reglaj", default=None)
    a = p.parse_args(argv)
    if a.comanda == "scrie":
        iesire = Path(a.iesire) if a.iesire else cale_implicita()
        if iesire.exists() and not a.inlocuieste:
            raise SystemExit(f"{iesire} există deja (--inlocuieste ca să-l rescrii)")
        banc = json.loads(Path(a.banc).read_text(encoding="utf-8"))
        reglaj = din_banc(banc, Path(a.banc).as_posix(), a.kgr)
        iesire.parent.mkdir(parents=True, exist_ok=True)
        iesire.write_bytes(json.dumps(reglaj, ensure_ascii=False, indent=1).encode("utf-8"))
        print(json.dumps({"scris": str(iesire), **reglaj}, ensure_ascii=False, indent=1))
        return 0
    rez = alege(a.reglaj or cale_implicita(), a.kgr)
    print(json.dumps(rez, ensure_ascii=False, indent=1))
    return 0 if rez["folosit"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
