"""S118 pasul 3 (C-126 B, 17 nov 2026): Kronos învață din conversațiile cu Adrian — bucla care schimbă modelul din
interfață DOAR dacă trece toate examenele.

Pașii unei rulări (`ruleaza`), fiecare scris în `lucru/invatare_conversatii/<eticheta>/jurnal.json`:
  1. lecțiile: `unelte/lectii_din_conversatii.py` (👍 și corecturile din baza interfeței; 20 % deoparte);
     fără nicio lecție de antrenare SAU fără nicio lecție deoparte → nu antrenează nimic (cod 3, „prea puține lecții”);
  2. modelul din interfață: valorile implicite din `unelte/interfata_ws.ps1` ($Config, $Experiment);
  3. amestecul: perechile de conversație ale rețetei S117 (`lucru/conversatie_chat/antrenare.jsonl`) + lecțiile de
     antrenare, fiecare de cel mult 3 ori, iar toate lecțiile la un loc cel mult 5 % din rânduri (dacă ar fi mai mult,
     se repetă mai puțin, până la o dată); configurarea = copia lui `config/conv_w2_mare_24zch.toml` (S117) cu DOAR
     numele liniei, `cale_stare`, `conversatie`, `durata_scaderii_secunde = 3600` și eticheta (restul: AdamW 1e-5,
     conversație 0,45, hrană 0,30, ca la S117);
  4. antrenarea: `unelte/antrenare_recalcul.py --config <noua> --ore 1 --porneste-din <modelul din interfață>`;
  5. examenele, pe modelul vechi (V) și pe cel nou (N), aceleași întrebări: română curat (`examen_validari_ws.py`),
     R1 (`romana_raspunsuri.py reper`), `examen_conversatie.py --doar-local` pe S15 + S4 + tipuri noi (corect = nota
     profesorului ≥ 7), `examen_chat.py` (a)+(b) și lecțiile ținute deoparte (`lectii`, mai jos);
  6. regula (pre-înregistrată în docs/preinregistrari/2026-11-17_invatare_conversatii.md, aceleași praguri ca S117 față
     de modelul din interfață): română curat N ≤ V + 0,01 ȘI corecte N ≥ V − 10 ȘI R1 N ≥ 90 ȘI chat N ≥ V − 5 ȘI
     lecțiile deoparte N ≥ V. Doar dacă trece TOT: `interfata_ws.ps1` primește noul model (Chat și „din text”) și
     interfața de pe 8787 e repornită; altfel nimic nu se schimbă și jurnalul spune de ce.
Paza plăcii pe fiecare pas: > 7.000 MB sau ≥ 83 °C → pasul e oprit, rularea se oprește (modelul din interfață rămâne).

Lecțiile ținute deoparte (`lectii`): răspunsul modelului ca în fila Chat (fără întâmplare, 80 de bucăți, tăiat la primul
rând nou), „Text: …” în față la cele din fila „din text”; corect = verificatorul de text (`unelte/verificator_text.verifica`,
regula de la S16) față de răspunsul din lecție. Pe ecran și în jurnal doar NUMERE (conversațiile lui Adrian nu ajung în
Git, hub sau rapoarte); răspunsurile întocmai stau în `lucru/` (ignorat de Git).

    python unelte/invata_din_conversatii.py ruleaza                       # bucla întreagă (placa, ~1 h + examenele)
    python unelte/invata_din_conversatii.py pregateste                    # doar pașii 1–3 (procesor), fără antrenare
    python unelte/invata_din_conversatii.py lectii --experiment 651 --iesire lucru/x.json [--dispozitiv cuda]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

DOSAR = "lucru/invatare_conversatii"
CONFIG_BAZA = "config/conv_w2_mare_24zch.toml"
CONVERSATIE_BAZA = "lucru/conversatie_chat/antrenare.jsonl"
INTERFATA_PS1 = "unelte/interfata_ws.ps1"
DOSAR_LECTII = "lucru/lectii"
REPETARI_MAX = 3
PROCENT_LECTII_MAX = 5.0
SECUNDE_ANTRENARE = 3600
SIMBOLURI = 80
NOTA_CORECT = 7
PRAG_ROMANA = 0.01
PRAG_CORECTE = 10
PRAG_R1 = 90
PRAG_CHAT = 5
PRAG_OPRIRE_MB = 7000
PRAG_GRADE = 83
EXAMENE = {"S15": "docs/conversatie/examen_generalizare_mare.json", "S4": "docs/conversatie/examen_generalizare_401.json",
           "TN": "docs/conversatie/examen_tipuri_noi.json"}
EXAMEN_CHAT = "docs/conversatie/examen_chat.json"


# --- piesele mici (testate fără placă) -------------------------------------------------------------------------------

def modelul_din_interfata(text_ps1: str) -> tuple[str, int, int]:
    """(config, experiment, experiment_text) din valorile implicite ale lui interfata_ws.ps1."""
    def valoare(nume: str) -> str:
        m = re.search(rf"\[(?:string|int)\]\${nume}\s*=\s*\"?([^\",\s]+)\"?", text_ps1)
        if m is None:
            raise ValueError(f"interfata_ws.ps1 nu are valoarea implicită ${nume}")
        return m.group(1)
    return valoare("Config"), int(valoare("Experiment")), int(valoare("ExperimentText"))


def schimba_interfata(text_ps1: str, config: str, experiment: int, nota: str) -> str:
    """Textul lui interfata_ws.ps1 cu noul model implicit în ambele file și un rând de istoric deasupra lui param(...)."""
    text = text_ps1
    for nume, val in (("Config", f'"{config}"'), ("Experiment", str(experiment)), ("ExperimentText", str(experiment))):
        text, n = re.subn(rf"(\[(?:string|int)\]\${nume}\s*=\s*)(\"[^\"]*\"|\d+)", lambda m: m.group(1) + val, text)
        if n != 1:
            raise ValueError(f"interfata_ws.ps1: ${nume} apare de {n} ori (aștept o dată)")
    if "\nparam(" not in text:
        raise ValueError("interfata_ws.ps1 nu are param(")
    return text.replace("\nparam(", f"\n# {nota}\nparam(", 1)


def config_noua(text_baza: str, linie: str, conversatie: str, secunde: int, eticheta: str) -> str:
    """Copia configurării de bază cu DOAR: numele liniei, cale_stare, conversatie, durata scăderii și eticheta."""
    inlocuiri = [
        (r'(?m)^nume = "[^"]*"', f'nume = "{linie}"'),
        (r'cale_stare = "[^"]*"', f'cale_stare = "lucru/{linie}/gpt.pt"'),
        (r'conversatie = "[^"]*"', f'conversatie = "{conversatie}"'),
        (r"durata_scaderii_secunde = \d+", f"durata_scaderii_secunde = {secunde}"),
        (r'(?m)^eticheta = "[^"]*"', f'eticheta = "{eticheta}"'),
    ]
    linii = text_baza.split("\n")
    for tipar, nou in inlocuiri:
        n = 0
        for i, rand in enumerate(linii):
            if rand.lstrip().startswith("#"):
                continue  # comentariile (antetul) rămân cum sunt
            linii[i], k = re.subn(tipar, lambda _m, nou=nou: nou, rand)
            n += k
        if n != 1:
            raise ValueError(f"configurarea de bază: „{tipar}” apare de {n} ori (aștept o dată)")
    text = "\n".join(linii)
    antet = (f"# S118 (C-126 B): învățarea din conversațiile cu Adrian, linia {linie}; scrisă de\n"
             f"# unelte/invata_din_conversatii.py din configurarea de bază, cu DOAR numele, cale_stare, conversatie,\n"
             f"# durata scăderii ({secunde} s) și eticheta schimbate.\n")
    return antet + text


def repetari_lectii(n_lectii: int, n_baza: int, repetari_max: int = REPETARI_MAX,
                    procent_max: float = PROCENT_LECTII_MAX) -> int:
    """De câte ori intră fiecare lecție: cel mult `repetari_max`, iar lecțiile la un loc cel mult `procent_max` % din
    rândurile amestecului; dacă nici o dată nu încap sub procent, tot o dată (lecțiile nu se aruncă)."""
    if n_lectii <= 0:
        return 0
    for r in range(repetari_max, 0, -1):
        if 100.0 * r * n_lectii / (n_baza + r * n_lectii) <= procent_max:
            return r
    return 1


def scrie_amestecul(baza: Path, lectii: list[dict[str, Any]], iesire: Path) -> dict[str, Any]:
    """Rândurile bazei, neschimbate, apoi fiecare lecție de `repetari` ori. Întoarce doar numere."""
    n_baza = sum(1 for rand in baza.open("rb") if rand.strip())
    r = repetari_lectii(len(lectii), n_baza)
    iesire.parent.mkdir(parents=True, exist_ok=True)
    with iesire.open("wb") as f:
        with baza.open("rb") as b:
            shutil.copyfileobj(b, f)
        if baza.stat().st_size and not baza.read_bytes()[-1:] == b"\n":
            f.write(b"\n")
        for lectie in lectii:
            rand = {k: v for k, v in lectie.items() if k != "tip"}
            for _ in range(r):
                f.write((json.dumps(rand, ensure_ascii=False) + "\n").encode("utf-8"))
    return {"randuri_baza": n_baza, "lectii": len(lectii), "repetari": r, "randuri_lectii": r * len(lectii),
            "procent_lectii": round(100.0 * r * len(lectii) / max(1, n_baza + r * len(lectii)), 3)}


def citeste_jsonl(cale: Path) -> list[dict[str, Any]]:
    if not cale.exists():
        return []
    return [json.loads(r) for r in cale.read_text(encoding="utf-8").splitlines() if r.strip()]


def taie(text: str) -> str:
    """Ca fila Chat: până la primul rând nou sau la <|endoftext|>."""
    return text.split("<|endoftext|>")[0].strip().split("\n")[0].strip()


def noteaza_lectii(model: Any, lectii: list[dict[str, Any]], simboluri: int = SIMBOLURI) -> dict[str, Any]:
    """Răspunsurile modelului la lecțiile ținute deoparte și câte sunt corecte (verificatorul de text, regula S16)."""
    from module.model_conversatie import intrebarea
    from unelte.verificator_text import verifica

    raspunsuri = []
    for l in lectii:
        prompt = l.get("prompt") or intrebarea(l["intrebare"], l.get("text", ""))
        r = taie(str(model.completeaza(prompt, simboluri)))
        raspunsuri.append({"id": l["id"], "fel": l.get("fel"), "raspuns": r, "corect": bool(verifica(l["raspuns"], r)["corect"])})
    return {"corecte": sum(r["corect"] for r in raspunsuri), "din": len(raspunsuri), "raspunsuri": raspunsuri}


def verdict(v: dict[str, Any], n: dict[str, Any]) -> dict[str, Any]:
    """Regula pre-înregistrată. `v`/`n` = {romana, corecte, r1, chat, lectii} pentru modelul vechi / nou."""
    c = {
        "romana_curat": {"nou": n["romana"], "vechi": v["romana"], "prag": round(v["romana"] + PRAG_ROMANA, 6),
                         "trece": n["romana"] <= v["romana"] + PRAG_ROMANA},
        "corecte_profesor": {"nou": n["corecte"], "vechi": v["corecte"], "prag": v["corecte"] - PRAG_CORECTE,
                             "trece": n["corecte"] >= v["corecte"] - PRAG_CORECTE},
        "R1_instructiuni": {"nou": n["r1"], "prag": PRAG_R1, "trece": n["r1"] is not None and n["r1"] >= PRAG_R1},
        "chat_a_b": {"nou": n["chat"], "vechi": v["chat"], "prag": v["chat"] - PRAG_CHAT,
                     "trece": n["chat"] >= v["chat"] - PRAG_CHAT},
        "lectii_deoparte": {"nou": n["lectii"], "vechi": v["lectii"], "prag": v["lectii"], "trece": n["lectii"] >= v["lectii"]},
    }
    trece = all(x["trece"] for x in c.values())
    return {"conditii": c, "trece": trece,
            "pica": [k for k, x in c.items() if not x["trece"]],
            "verdict": "MODELUL NOU INTRĂ ÎN INTERFAȚĂ" if trece else "rămâne modelul din interfață"}


# --- rularea pe placă -------------------------------------------------------------------------------------------------

def nvidia_smi() -> tuple[int, int] | None:
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,temperature.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=30)
        m, t = (int(x) for x in r.stdout.strip().split(","))
        return m, t
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


class Rulare:
    """O rulare a buclei; `executa(nume, comanda)` e înlocuibil în teste."""

    def __init__(self, dosar: Path, executa: Callable[[str, list[str]], int] | None = None) -> None:
        self.dosar = dosar
        self.jurnal: dict[str, Any] = {"inceput": datetime.now().isoformat(timespec="seconds"), "pasi": []}
        self._executa = executa or self._cu_paza

    def scrie(self) -> None:
        self.dosar.mkdir(parents=True, exist_ok=True)
        (self.dosar / "jurnal.json").write_bytes(json.dumps(self.jurnal, ensure_ascii=False, indent=1).encode("utf-8"))

    def _cu_paza(self, nume: str, comanda: list[str]) -> int:
        proces = subprocess.Popen(comanda, cwd=RADACINA)
        oprit: list[str] = []
        gata = threading.Event()
        varf = {"mb": 0, "grade": 0}

        def paza() -> None:
            while not gata.wait(5):
                citire = nvidia_smi()
                if citire is None:
                    continue
                varf["mb"], varf["grade"] = max(varf["mb"], citire[0]), max(varf["grade"], citire[1])
                if not oprit and (citire[0] > PRAG_OPRIRE_MB or citire[1] >= PRAG_GRADE):
                    oprit.append(f"{citire[0]} MB / {citire[1]} °C")
                    proces.kill()

        fir = threading.Thread(target=paza, daemon=True)
        fir.start()
        cod = proces.wait()
        gata.set()
        fir.join(30)
        self.jurnal["pasi"][-1].update({"placa_varf_mb": varf["mb"], "placa_grade_max": varf["grade"],
                                        "oprit_de_paza": oprit[0] if oprit else None})
        return cod

    def pas(self, nume: str, comanda: list[str]) -> None:
        print(f"\n=== S118 {datetime.now():%H:%M:%S} — {nume}: {' '.join(comanda)}", flush=True)
        self.jurnal["pasi"].append({"pas": nume, "comanda": comanda, "inceput": datetime.now().isoformat(timespec="seconds")})
        cod = self._executa(nume, comanda)
        self.jurnal["pasi"][-1].update({"sfarsit": datetime.now().isoformat(timespec="seconds"), "cod": cod})
        self.scrie()
        if cod != 0:
            self.opreste(f"pasul „{nume}” a ieșit cu codul {cod}")

    def opreste(self, motiv: str, cod: int = 1) -> None:
        self.jurnal.update({"oprit": motiv, "sfarsit": datetime.now().isoformat(timespec="seconds")})
        self.scrie()
        raise SystemExit(cod)


def _cel_mai_nou(dosar: str, tipar: str, dupa: float) -> Path | None:
    fisiere = [p for p in (RADACINA / dosar).glob(tipar) if p.stat().st_mtime >= dupa]
    return max(fisiere, key=lambda p: p.stat().st_mtime) if fisiere else None


def examineaza(rulare: Rulare, model: int, dosar: Path, lectii_deoparte: Path) -> dict[str, Any]:
    """Examenele unui model; întoarce {romana, corecte, r1, chat, lectii} (doar numere)."""
    py = [sys.executable, "-X", "utf8"]
    rez: dict[str, Any] = {}
    t = datetime.now().timestamp() - 1
    rulare.pas(f"validari_{model}", py + ["unelte/examen_validari_ws.py", "--experiment", str(model)])
    f = _cel_mai_nou("lucru/examen_validari_ws", f"experiment_{model}_*.json", t)
    if f is None:
        rulare.opreste(f"validari_{model}: nu găsesc fișierul")
    rez["romana"] = json.loads(f.read_text(encoding="utf-8"))["bpb_romana_curat"]
    r1 = dosar / f"r1_{model}"
    rulare.pas(f"r1_{model}", py + ["unelte/romana_raspunsuri.py", "reper", "--experiment", str(model), "--iesire",
                                    str(r1.relative_to(RADACINA))])
    rez["r1"] = (json.loads((r1 / "nota.json").read_text(encoding="utf-8")).get("instructiuni") or {}).get("R1")
    corecte = 0
    for examen, cale in EXAMENE.items():
        t = datetime.now().timestamp() - 1
        rulare.pas(f"{examen}_{model}", py + ["unelte/examen_conversatie.py", "--experiment", str(model), "--examen", cale,
                                              "--doar-local"])
        f = _cel_mai_nou("lucru/examen_conversatie", f"experiment_{model}_*.json", t)
        if f is None:
            rulare.opreste(f"{examen}_{model}: nu găsesc fișierul")
        corecte += sum(1 for p in json.loads(f.read_text(encoding="utf-8"))["raspunsuri"]
                       if p.get("nota_elev") is not None and p["nota_elev"] >= NOTA_CORECT)
    rez["corecte"] = corecte
    chat = dosar / f"chat_{model}.json"
    rulare.pas(f"chat_{model}", py + ["unelte/examen_chat.py", "--experiment", str(model), "--examen", EXAMEN_CHAT,
                                      "--iesire", str(chat.relative_to(RADACINA)), "--dispozitiv", "cuda"])
    rez["chat"] = json.loads(chat.read_text(encoding="utf-8"))["nota"]["total"]
    lec = dosar / f"lectii_{model}.json"
    rulare.pas(f"lectii_{model}", py + ["unelte/invata_din_conversatii.py", "lectii", "--experiment", str(model),
                                        "--lectii", str(lectii_deoparte), "--iesire", str(lec), "--dispozitiv", "cuda"])
    rez["lectii"] = json.loads(lec.read_text(encoding="utf-8"))["corecte"]
    return rez


def reporneste_interfata() -> int:
    """Oprește procesul care ascultă pe 8787 și pornește interfata_ws.ps1 (cu noile valori implicite)."""
    oprire = ("Get-NetTCPConnection -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue | "
              "ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }")
    subprocess.run(["powershell", "-NoProfile", "-Command", oprire], cwd=RADACINA, timeout=120)
    return subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", INTERFATA_PS1],
                          cwd=RADACINA, timeout=300).returncode


def pregateste(eticheta: str, dosar: Path, config_baza: str = CONFIG_BAZA, conversatie_baza: str = CONVERSATIE_BAZA,
               dosar_lectii: Path | None = None, rulare: Rulare | None = None) -> dict[str, Any]:
    """Pașii 1–3 (procesor): lecțiile, modelul din interfață, amestecul și configurarea. Doar numere în întoarcere."""
    from unelte import lectii_din_conversatii as lc

    dosar_lectii = dosar_lectii or RADACINA / DOSAR_LECTII
    if rulare is None:
        info = lc.ruleaza(RADACINA / lc.BAZA, dosar_lectii)
    else:
        rulare.pas("lectii_din_conversatii", [sys.executable, "-X", "utf8", "unelte/lectii_din_conversatii.py",
                                              "--dosar", str(dosar_lectii)])
        info = json.loads((dosar_lectii / lc.INFO).read_text(encoding="utf-8"))
    config, experiment, _ = modelul_din_interfata((RADACINA / INTERFATA_PS1).read_text(encoding="utf-8"))
    linie = f"w2_lectii_{eticheta}"
    antrenare = citeste_jsonl(dosar_lectii / lc.LECTII)
    rez: dict[str, Any] = {"lectii": info, "interfata": {"config": config, "experiment": experiment}, "linie": linie}
    if not antrenare or not info.get("deoparte"):
        rez["prea_putine"] = True
        return rez
    amestec = dosar / "antrenare.jsonl"
    rez["amestec"] = scrie_amestecul(RADACINA / conversatie_baza, antrenare, amestec)
    cale_config = dosar / f"config_{linie}.toml"
    cale_config.write_text(config_noua((RADACINA / config_baza).read_text(encoding="utf-8"), linie,
                                       amestec.relative_to(RADACINA).as_posix(), SECUNDE_ANTRENARE,
                                       f"S118: lecțiile din conversații ({len(antrenare)}), 1 h din #{experiment}"),
                           encoding="utf-8")
    rez["config"] = cale_config.relative_to(RADACINA).as_posix()
    return rez


def ruleaza(eticheta: str) -> int:
    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului

    dosar = RADACINA / DOSAR / eticheta
    if (dosar / "jurnal.json").exists():
        raise SystemExit(f"{dosar}/jurnal.json există deja — o rulare pe etichetă")
    rulare = Rulare(dosar)
    rulare.scrie()
    prep = pregateste(eticheta, dosar, rulare=rulare)
    rulare.jurnal["pregatire"] = prep
    if prep.get("prea_putine"):
        rulare.opreste("prea puține lecții (trebuie cel puțin una de antrenare și una deoparte); nimic antrenat", cod=3)
    vechi = prep["interfata"]["experiment"]
    rulare.pas("antrenare", [sys.executable, "-X", "utf8", "unelte/antrenare_recalcul.py", "--config", prep["config"],
                             "--ore", "1", "--porneste-din", str(vechi)])
    nou = fisa_modelului(Jurnal(RADACINA / "lucru"), linie=prep["linie"])["id"]
    rulare.jurnal["modele"] = {"vechi": vechi, "nou": nou}
    deoparte = RADACINA / DOSAR_LECTII / "examen_lectii.jsonl"
    rulare.jurnal["examene"] = {"vechi": examineaza(rulare, vechi, dosar, deoparte)}
    rulare.jurnal["examene"]["nou"] = examineaza(rulare, nou, dosar, deoparte)
    rulare.scrie()
    v = verdict(rulare.jurnal["examene"]["vechi"], rulare.jurnal["examene"]["nou"])
    rulare.jurnal["verdict"] = v
    if v["trece"]:
        ps1 = RADACINA / INTERFATA_PS1
        nota = (f"{datetime.now():%d.%m.%Y} (S118, bucla din conversatii, {eticheta}): #{vechi} -> #{nou}, "
                f"a trecut toate examenele. Revenire: -Config {prep['interfata']['config']} -Experiment {vechi} "
                f"-ExperimentText {vechi}")
        ps1.write_text(schimba_interfata(ps1.read_text(encoding="utf-8"), prep["config"], nou, nota), encoding="utf-8")
        rulare.jurnal["interfata_repornita_cod"] = reporneste_interfata()
    rulare.jurnal["sfarsit"] = datetime.now().isoformat(timespec="seconds")
    rulare.scrie()
    print(json.dumps({"verdict": v["verdict"], "pica": v["pica"], "vechi": vechi, "nou": nou}, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Bucla S118: învață din lecțiile din conversații; schimbă modelul doar dacă trece tot.")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("ruleaza")
    r.add_argument("--eticheta", default=f"{datetime.now():%Y%m%d_%H%M}")
    g = sub.add_parser("pregateste")
    g.add_argument("--eticheta", default=f"{datetime.now():%Y%m%d_%H%M}")
    l = sub.add_parser("lectii")
    l.add_argument("--experiment", type=int, required=True)
    l.add_argument("--lectii", default=f"{DOSAR_LECTII}/examen_lectii.jsonl")
    l.add_argument("--iesire", required=True)
    l.add_argument("--dispozitiv", default="cpu")
    a = p.parse_args(argv)
    if a.cmd == "ruleaza":
        return ruleaza(a.eticheta)
    if a.cmd == "pregateste":
        rez = pregateste(a.eticheta, RADACINA / DOSAR / a.eticheta)
        print(json.dumps(rez, ensure_ascii=False, indent=1))
        return 3 if rez.get("prea_putine") else 0
    iesire = Path(a.iesire)
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja")
    from kronos.jurnal import Jurnal
    from unelte.modele_salvate import fisa_modelului, incarca_modelul

    model = incarca_modelul(fisa_modelului(Jurnal(RADACINA / "lucru"), a.experiment), a.dispozitiv)
    nota = noteaza_lectii(model, citeste_jsonl(Path(a.lectii)))
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_bytes(json.dumps({"experiment": a.experiment, **nota}, ensure_ascii=False, indent=1).encode("utf-8"))
    print(json.dumps({"experiment": a.experiment, "corecte": nota["corecte"], "din": nota["din"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
