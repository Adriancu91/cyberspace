"""S64: „mai multe încercări ajută?” — pe setul de PROBĂ (20 de probleme), starea lucru/cod_c1/gpt.pt (doar citită):
(a) 200 de corpuri pe problemă la T = 0,8, apoi noteaza; (b) la fel la T = 0,4 (cu --n 100 dacă (a) a scris > 70 min).
--lot 2 --memorie-max 6500; nvidia-smi la 5 s în placa.csv; plasa: > 6.900 MB sau > 82 °C oprește pasul în curs.
Seturile ascunse nu se deschid. Pre-înregistrarea: docs/preinregistrari/2026-11-02_cod_pass_k_mare.md."""
import json
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

RAD = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAD))
from unelte.urmareste_placa import citeste  # noqa: E402

PY = str(RAD / ".venv" / "Scripts" / "python.exe")
CFG = "config/cod_c1_init002.toml"
STARE = "lucru/cod_c1/gpt.pt"
IES = "lucru/kronos_cod/s64"
DOS = RAD / "lucru" / "cascada" / "S64"
JURNAL = DOS / "s64.json"
CSV = DOS / "placa.csv"
PRAG_A_SECUNDE = 70 * 60


def model(temp, n, nume):
    return [PY, "-X", "utf8", "unelte/kronos_cod/examen_cod.py", "model", "--config", CFG, "--stare", STARE,
            "--set", "proba", "--n", str(n), "--temperatura", temp, "--samanta", "0", "--lot", "2",
            "--memorie-max", "6500", "--iesire", f"{IES}/{nume}.json"]


def noteaza(nume):
    return [PY, "-X", "utf8", "unelte/kronos_cod/examen_cod.py", "noteaza", "--raspunsuri", f"{IES}/{nume}.json",
            "--nota", f"{IES}/nota_{nume}.json"]


masuratori = []
stop = threading.Event()
curent = {"proc": None, "plasa": None, "cu_plasa": False}


def urmareste():
    with CSV.open("a", encoding="utf-8") as f:
        if CSV.stat().st_size == 0:
            f.write("ora,temperatura,memorie_mb,incarcare_procent\n")
        while not stop.is_set():
            m = citeste()
            if m:
                masuratori.append((time.time(), m[0], m[1]))
                f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S},{m[0]},{m[1]},{m[2]}\n")
                f.flush()
                p = curent["proc"]
                if curent["cu_plasa"] and p is not None and p.poll() is None and (m[1] > 6900 or m[0] > 82):
                    curent["plasa"] = f"plasa: {m[1]} MB, {m[0]} °C"
                    p.terminate()
            stop.wait(5)


def ruleaza(jurnal, nume, cu_plasa, cmd):
    t0 = time.time()
    print(f"=== {nume} ({datetime.now():%H:%M:%S}): {' '.join(cmd)}", flush=True)
    curent["plasa"] = None
    curent["cu_plasa"] = cu_plasa
    curent["proc"] = subprocess.Popen(cmd, cwd=RAD)
    cod = curent["proc"].wait()
    t1 = time.time()
    fer = [m for m in masuratori if t0 <= m[0] <= t1 + 1]
    jurnal["pasi"].append({"pas": nume, "cod": cod, "secunde": round(t1 - t0, 1), "plasa": curent["plasa"],
                           "nvidia_smi_memorie_max_mb": max((m[2] for m in fer), default=None),
                           "nvidia_smi_temperatura_max": max((m[1] for m in fer), default=None),
                           "citiri": len(fer)})
    JURNAL.write_text(json.dumps(jurnal, ensure_ascii=False, indent=1), encoding="utf-8")
    return cod, t1 - t0


def main():
    if JURNAL.exists() or (RAD / IES).exists():
        print("S64 a rulat deja (s64.json sau lucru/kronos_cod/s64 există): nu se repetă.")
        return 2
    if not (RAD / STARE).exists():
        print(f"{STARE} lipsește. Nu pornesc.")
        return 4
    (RAD / IES).mkdir(parents=True)
    threading.Thread(target=urmareste, daemon=True).start()
    jurnal = {"pornit": f"{datetime.now():%Y-%m-%d %H:%M:%S}", "pasi": []}
    cod_final = 0
    cod, sec_a = ruleaza(jurnal, "a_raspunsuri_t08", True, model("0.8", 200, "t08"))
    if cod == 0:
        cod, _ = ruleaza(jurnal, "a_nota_t08", False, noteaza("t08"))
    if cod == 0:
        n_b = 200 if sec_a <= PRAG_A_SECUNDE else 100
        jurnal["n_b"] = n_b
        cod, _ = ruleaza(jurnal, "b_raspunsuri_t04", True, model("0.4", n_b, "t04"))
    if cod == 0:
        cod, _ = ruleaza(jurnal, "b_nota_t04", False, noteaza("t04"))
    if cod != 0:
        print(f"Un pas a picat (cod {cod}); nu încerc altceva.", flush=True)
        cod_final = cod
    jurnal["terminat"] = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
    JURNAL.write_text(json.dumps(jurnal, ensure_ascii=False, indent=1), encoding="utf-8")
    time.sleep(6)
    stop.set()
    return cod_final


if __name__ == "__main__":
    sys.exit(main())
