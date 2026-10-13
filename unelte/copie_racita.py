"""Copia răcită: „modelul zilei” al unei linii care învață cu rata constantă (13 octombrie 2026, rețeta W2).

La sfârșitul unei nopți, din starea liniei (cale_stare din configurare) se face o COPIE care învață încă --minute (30)
cu rata care scade liniar de la rata liniei la --rata-finala (0,00005). Copia dă toate examenele și e salvată separat
de Kronos; starea liniei NU se atinge (se verifică: aceeași mărime și aceeași oră a fișierului înainte și după), deci
linia continuă noaptea următoare din punctul de dinainte de răcire.

Copia e un experiment Kronos obișnuit (cu paznic, test rapid și examenul oficial), pe o linie de jurnal separată,
„<linia>_racit_<ore>” (ex. ws_w2_racit_010): fiind primul experiment al liniei lui, e păstrat și salvat mereu. Modelul
e module.model_racit:ModelGPTRacit. Examenele:
- la experiment: val_bpb (examenul oficial) și examenele de la oră ale liniei (fapte, fapte noi, nota profesorului);
- după el, pe modelul salvat: setul sacru (unelte/examen_fapte_nou.py --sacru; doar raportat, nicio decizie nu-l
  citește) și româna și codul (unelte/examen_validari_ws.py).
Rezultatul: lucru/<linia>/modelul_zilei.json (ultimul) și un rând în lucru/<linia>/modelele_zilei.jsonl.
Dacă copia pentru ora de acum există deja, nu se mai antrenează: se dau doar examenele care lipsesc.

    python unelte/copie_racita.py --config config/ws_w2.toml
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.config import citeste_config  # noqa: E402
from kronos.jurnal import Jurnal  # noqa: E402
from kronos.registru import Registru  # noqa: E402
from unelte.antrenare_lunga import criterii_din, cu_criterii_implicite, cu_hrana_implicita, ore_din_jurnal  # noqa: E402
from unelte.compara_plasa_adaptiva import ruleaza  # noqa: E402

MODUL_RACIT = "module.model_racit:ModelGPTRacit"
# setările liniei care țin de starea ei și de scăderea ratei: copia are regulile ei
DOAR_ALE_LINIEI = ("cale_stare", "director_stari", "de_la_zero", "stare_de_pornire", "rata_care_scade", "incalzire_pasi",
                   "fractie_rata_finala", "durata_scaderii_secunde")
DOSAR_SACRU, LINIE_VALIDARI = "examen_sacru", "examen_validari_ws"


def linia_copiei(linie: str, ore: int) -> str:
    return f"{linie}_racit_{ore:03d}"


def config_racit(config: Any, minute: float, rata_finala: float) -> Any:
    """Configurarea copiei: același model, aceleași date și examene; pornește din starea liniei (doar citită), învață
    `minute` cu rata care scade liniar la rata_finala și nu scrie nicio stare."""
    setari = config.setari_port("model")
    stare = setari.get("cale_stare")
    if not stare:
        raise ValueError("configurarea n-are cale_stare: nu există o stare a liniei din care să fac copia")
    racit = copy.deepcopy(config)
    racit.porturi["model"] = {"modul": MODUL_RACIT, "setari": {
        **{k: v for k, v in setari.items() if k not in DOAR_ALE_LINIEI}, "stare_de_pornire": stare, "rata_finala": rata_finala}}
    racit.buget_antrenare_secunde = minute * 60
    racit.experimente, racit.porneste_din = 1, None
    return racit


def semn_fisier(cale: Path) -> tuple[int, int]:
    s = cale.stat()
    return s.st_size, s.st_mtime_ns


def copia_facuta(jurnal: Any, linie: str) -> dict[str, Any] | None:
    fise = [f for f in jurnal.istoric(linie) if f.get("decizie") == "pastrat" and f.get("model_salvat")]
    return fise[-1] if fise else None


def sacru_din(director_lucru: Path, experiment: int) -> dict[str, Any] | None:
    fisier = director_lucru / DOSAR_SACRU / "rezultate.jsonl"
    if not fisier.exists():
        return None
    randuri = [json.loads(r) for r in fisier.read_text(encoding="utf-8").splitlines() if r.strip()]
    return next((r for r in reversed(randuri) if r.get("experiment") == experiment), None)


def validari_din(jurnal: Any, experiment: int) -> dict[str, Any] | None:
    fise = [f for f in jurnal.istoric(LINIE_VALIDARI)
            if ((f.get("module") or {}).get("elev") or {}).get("experiment") == experiment]
    return fise[-1].get("scoruri") if fise else None


def examen_separat(comanda: list[str], minute: float) -> str | None:
    """Rulează o unealtă de examen; None dacă a mers, altfel de ce nu (copia rămâne oricum salvată)."""
    try:
        r = subprocess.run(comanda, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=minute * 60, cwd=Path.cwd())
    except subprocess.TimeoutExpired:
        return f"a depășit {minute:g} minute"
    return None if r.returncode == 0 else f"cod {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}"


def rezumat(config: Any, ore: int, fisa: dict[str, Any], scor_principal: str, sacru: dict[str, Any] | None,
            validari: dict[str, Any] | None, erori: dict[str, str], stare_neatinsa: bool) -> dict[str, Any]:
    s = fisa.get("statistici_antrenare") or {}
    return {
        "data": datetime.now().isoformat(timespec="seconds"), "linie": config.nume, "ore": ore,
        "experiment": fisa["id"], "linia_copiei": fisa["linie"], "model_salvat": fisa.get("model_salvat"),
        scor_principal: fisa["scoruri"][scor_principal], **criterii_din(fisa),
        "fapte_sacre": (sacru or {}).get("fapte_sacre"), "intrebari_sacre": (sacru or {}).get("intrebari"),
        "bpb_romana": (validari or {}).get("bpb_romana"), "bpb_cod": (validari or {}).get("bpb_cod"),
        "validari": validari, "pasi_racire": s.get("pasi"), "minute_racire": round((s.get("secunde_bucla") or 0) / 60, 1),
        "rata_la_inceput": s.get("rata_la_inceput"), "rata_la_final": s.get("rata_la_final"),
        "memorie_rezervata_mb": s.get("memorie_rezervata_mb"), "starea_liniei_neatinsa": stare_neatinsa,
        **({"erori": erori} if erori else {}),
    }


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Copia răcită a unei linii cu rata constantă: modelul zilei.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--minute", type=float, default=30, help="cât învață copia, cu rata care scade liniar")
    parser.add_argument("--rata-finala", type=float, default=0.00005)
    parser.add_argument("--racire", type=float, default=70, help="înainte, aștept placa până la atâtea grade")
    parser.add_argument("--fara-sacru", action="store_true")
    parser.add_argument("--fara-validari", action="store_true")
    parser.add_argument("--minute-examen", type=float, default=30, help="cel mult atât pentru fiecare examen separat")
    args = parser.parse_args(argv)

    config = citeste_config(args.config)
    cu_hrana_implicita(config)
    cu_criterii_implicite(config, tomllib.loads(Path(args.config).read_text(encoding="utf-8")))
    examen = Registru().creeaza("examen", config.porturi["examen"]["modul"], config.setari_port("examen")).instanta
    jurnal = Jurnal(config.director_lucru)
    ore = len(ore_din_jurnal(jurnal.istoric(config.nume), examen.scor_principal))
    try:
        racit = config_racit(config, args.minute, args.rata_finala)
    except ValueError as e:
        print(f"Copia răcită nu se poate face: {e}.", flush=True)
        return 1
    stare = Path(racit.setari_port("model")["stare_de_pornire"])
    if ore == 0 or not stare.exists():
        print(f"Copia răcită nu se poate face: linia „{config.nume}” n-are nicio oră făcută sau lipsește {stare}.", flush=True)
        return 1
    linie = linia_copiei(config.nume, ore)
    inainte = semn_fisier(stare)
    fisa = copia_facuta(jurnal, linie)
    if fisa is None:
        rata = config.setari_port("model")["rata_invatare"]
        print(f"Copia răcită după ora {ore} a liniei „{config.nume}”: {args.minute:g} minute, rata {rata:g} → "
              f"{args.rata_finala:g} (liniar), pe linia de jurnal „{linie}”. Starea liniei ({stare}) doar se citește.",
              flush=True)
        rulare = ruleaza(racit, linie, f"copia răcită după ora {ore} a liniei „{config.nume}” ({args.minute:g} min, rata "
                                       f"{rata:g} → {args.rata_finala:g}, liniar): modelul zilei",
                         {"samanta": config.setari_port("model").get("samanta", 0)}, racire=args.racire, cu_fisa=True)
        if rulare is None:
            return 1
        fisa = rulare["fisa"]
        if not fisa.get("model_salvat"):
            print(f"Copia răcită (#{fisa['id']}) n-a fost salvată de Kronos: {fisa.get('motiv') or fisa.get('eroare_salvare')}",
                  flush=True)
            return 1
    else:
        print(f"Copia răcită după ora {ore} există deja (#{fisa['id']}): dau doar examenele care lipsesc.", flush=True)
    neatinsa = semn_fisier(stare) == inainte
    if not neatinsa:
        print(f"ATENȚIE: {stare} s-a schimbat în timpul copiei răcite. Nu trebuia.", flush=True)

    erori: dict[str, str] = {}
    lucru = ["--director-lucru", str(config.director_lucru)]
    if not args.fara_sacru and sacru_din(config.director_lucru, fisa["id"]) is None:
        e = examen_separat([sys.executable, "-X", "utf8", "unelte/examen_fapte_nou.py", "--sacru", "--experiment",
                            str(fisa["id"]), "--doar-local", *lucru], args.minute_examen)
        if e:
            erori["sacru"] = e
    if not args.fara_validari and validari_din(jurnal, fisa["id"]) is None:
        e = examen_separat([sys.executable, "-X", "utf8", "unelte/examen_validari_ws.py", "--experiment", str(fisa["id"]),
                            *lucru], args.minute_examen)
        if e:
            erori["validari"] = e
    r = rezumat(config, ore, fisa, examen.scor_principal, sacru_din(config.director_lucru, fisa["id"]),
                validari_din(jurnal, fisa["id"]), erori, neatinsa)
    dosar = config.director_lucru / config.nume
    dosar.mkdir(parents=True, exist_ok=True)
    (dosar / "modelul_zilei.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    with (dosar / "modelele_zilei.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def cifra(cheie: str, zecimale: int) -> str:
        return f"{r[cheie]:.{zecimale}f}" if isinstance(r.get(cheie), (int, float)) else "–"

    print(f"\n=== Modelul zilei: copia răcită după ora {ore} a liniei „{config.nume}” (#{fisa['id']}) ===")
    print(f"{examen.scor_principal} {cifra(examen.scor_principal, 4)} | fapte {cifra('fapte_corecte', 0)} | fapte noi "
          f"{cifra('fapte_noi', 0)} | sacru {cifra('fapte_sacre', 0)} din {r.get('intrebari_sacre') or '–'} | nota "
          f"{cifra('nota_profesor', 2)} | română {cifra('bpb_romana', 2)} | cod {cifra('bpb_cod', 2)} (biți pe octet)")
    print(f"Răcirea: {r['pasi_racire']} pași în {r['minute_racire']} minute, rata la final {r['rata_la_final']}. "
          f"Starea liniei: {'neatinsă' if neatinsa else 'S-A SCHIMBAT'}. Modelul: {r['model_salvat']}")
    for nume, e in erori.items():
        print(f"Examenul „{nume}” nu s-a putut da: {e}")
    print(f"Salvat în {dosar / 'modelul_zilei.json'}", flush=True)
    return 0 if neatinsa and not erori else 1


if __name__ == "__main__":
    raise SystemExit(main())
