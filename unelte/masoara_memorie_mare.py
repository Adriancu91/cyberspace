"""S86 (C-85 pasul 2, aprobat de Adrian 6 nov 2026): memoria plăcii la Kronos de 24 de straturi, Muon față de AdamW.

Fiecare variantă rulează într-un proces nou (`unul`), urmărit de procesul părinte (`toate`) cu nvidia-smi: peste 7.000 MB
sau la 83 °C copilul e oprit. În copil, modelul e construit exact ca în `antrenare_recalcul.py` (recalculul activărilor pe
straturi, plafonul PyTorch 5.800 MB) din config/conv_w2_mare_24f.toml, cu `cale_stare` mutată pe o COPIE a lui
lucru/w2_mare/gpt_24.pt în lucru/memorie_mare/<varianta>/ (originalul doar citit). O „oră” scurtă = ca în orchestrator:
  1. antrenare: model nou din starea copiei, `pasi_optimizator` pași de optimizator (pasi_max = pași × adunare_loturi);
  2. validare: examenul (`ExamenBpb().examineaza`, doar chemat) + `dupa_examen` (salvează starea în COPIE și
     rulează examenele suplimentare, ca la sfârșitul unei ore adevărate);
  3. testul rapid al orei următoare: model nou, `antreneaza(date, 2)` + `biti_pentru` pe 500 de caractere.
Înainte și după fiecare fază: memory_allocated, memory_reserved, nvidia-smi; în fază: vârfurile PyTorch și nvidia-smi.
`--goleste`: după fiecare test rapid `del` + `gc.collect()` + `torch.cuda.empty_cache()`. Nimic în jurnal, niciun model
păstrat în afara copiilor din lucru/memorie_mare/.

    python unelte/masoara_memorie_mare.py toate
    python unelte/masoara_memorie_mare.py unul --varianta a --repetari 3

S87: `ore` rulează (b) Muon lot 4 × 24 în ordinea din kronos/orchestrator.py (test rapid → antrenare → validare, cu
model_test ținut), 3 ore, fără golire / cu gc la începutul orei / cu `del model_test` → lucru/memorie_ore/s87.json.

    python unelte/masoara_memorie_mare.py ore
    python unelte/masoara_memorie_mare.py unul --varianta b --repetari 3 --ordine orchestrator --golire gc --iesire …
"""

from __future__ import annotations

import argparse
import gc
import json
import shutil
import subprocess
import sys
import threading
import time
import tomllib
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

CONFIG = RADACINA / "config" / "conv_w2_mare_24f.toml"
SURSA = RADACINA / "lucru" / "w2_mare" / "gpt_24.pt"
DOSAR = RADACINA / "lucru" / "memorie_mare"
PRAG_MB = 6700
OPRIRE_MB = 7000
TEMPERATURA_MAX = 83
CARACTERE_TEST_RAPID = 500  # ca în kronos/orchestrator.py
CRESTERE_MB = 100  # „memoria crește de la o oră la alta”: alocatul după testul rapid urcă cu peste atât

VARIANTE: dict[str, dict[str, Any]] = {
    "a": {"optimizator": "adamw", "lot": 4, "adunare_loturi": 24},
    "b": {"optimizator": "muon", "lot": 4, "adunare_loturi": 24},
    "c": {"optimizator": "muon", "lot": 6, "adunare_loturi": 16},
    "d": {"optimizator": "muon", "lot": 12, "adunare_loturi": 8},
}


def nvidia_smi() -> tuple[int, int] | None:
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,temperature.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=30)
        m, t = (int(x) for x in r.stdout.strip().splitlines()[0].split(","))
        return m, t
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        return None


def setari_model(varianta: str, cale_stare: Path, pasi_optimizator: int) -> dict[str, Any]:
    """Setările modelului din config/conv_w2_mare_24f.toml, cu varianta, copia stării și pasi_max."""
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    setari = dict(config["porturi"]["model"]["setari"])
    setari.update(VARIANTE[varianta])
    setari["cale_stare"] = str(cale_stare)
    setari["pasi_max"] = pasi_optimizator * setari["adunare_loturi"]
    return setari


def setari_date() -> dict[str, Any]:
    return dict(tomllib.loads(CONFIG.read_text(encoding="utf-8"))["porturi"]["date"]["setari"])


def creste(alocat_dupa_test: list[float], prag: float = CRESTERE_MB) -> bool:
    """Memoria ținută crește de la o „oră” la alta dacă alocatul după ultimul test rapid e peste primul cu > prag MB."""
    return len(alocat_dupa_test) >= 2 and alocat_dupa_test[-1] - alocat_dupa_test[0] > prag


class Urmaritor:
    """Citește nvidia-smi la 0,5 s în fir separat și ține vârful pe faza curentă."""

    def __init__(self, citeste: Any = nvidia_smi, pas: float = 0.5) -> None:
        self.citeste, self.pas = citeste, pas
        self.faza = ""
        self.varfuri: dict[str, int] = {}
        self.temperatura_max = 0
        self._gata = threading.Event()
        self._fir = threading.Thread(target=self._bucla, daemon=True)

    def porneste(self) -> None:
        self._fir.start()

    def opreste(self) -> None:
        self._gata.set()
        self._fir.join(timeout=60)

    def citeste_acum(self) -> int | None:
        c = self.citeste()
        if c:
            self._noteaza(c)
            return c[0]
        return None

    def _noteaza(self, c: tuple[int, int]) -> None:
        if self.faza:
            self.varfuri[self.faza] = max(self.varfuri.get(self.faza, 0), c[0])
        self.temperatura_max = max(self.temperatura_max, c[1])

    def _bucla(self) -> None:
        while not self._gata.is_set():
            c = self.citeste()
            if c:
                self._noteaza(c)
            self._gata.wait(self.pas)


def _mb(x: float) -> int:
    return round(x / 2**20)


def ruleaza_unul(varianta: str, repetari: int, pasi_optimizator: int, goleste: bool, iesire: Path,
                 memorie_max_mb: int) -> dict[str, Any]:
    """În procesul acesta, pe placă: `repetari` „ore” scurte pentru varianta dată. Scrie iesire după fiecare fază."""
    import torch

    from module.date_amestec import DateAmestec
    from module.examen_bpb import ExamenBpb
    from module.model_muon import ModelGPTConversatieMuon
    from unelte import antrenare_recalcul

    fractie = antrenare_recalcul.plafon_placa(memorie_max_mb)
    antrenare_recalcul.instaleaza()
    dosar = iesire.parent
    dosar.mkdir(parents=True, exist_ok=True)
    copie = dosar / "gpt.pt"
    shutil.copyfile(SURSA, copie)
    setari = setari_model(varianta, copie, pasi_optimizator)
    date = DateAmestec(**setari_date())
    mostra = date.text_validare()[:CARACTERE_TEST_RAPID]
    urm = Urmaritor()
    urm.porneste()
    rezultat: dict[str, Any] = {"varianta": varianta, **VARIANTE[varianta], "pasi_optimizator": pasi_optimizator,
                                "pasi_max": setari["pasi_max"], "repetari": repetari, "goleste": goleste,
                                "plafon_pytorch_mb": memorie_max_mb, "fractie": fractie, "ore": [], "terminat": False}
    if varianta != "a":
        from module.model_muon import MuonCuAdamW
        import inspect
        rezultat["setari_muon"] = {"rata_muon": setari.get("rata_muon", 0.02),
                                   "scadere_muon": setari.get("scadere_muon", 0.0),
                                   **{k: v.default for k, v in inspect.signature(MuonCuAdamW.__init__).parameters.items()
                                      if k in ("momentum", "nesterov", "pasi_ns", "weight_decay")}}

    def scrie() -> None:
        rezultat["temperatura_max"] = urm.temperatura_max
        iesire.write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")

    def faza(ora: dict[str, Any], nume: str, f: Any) -> Any:
        torch.cuda.synchronize()
        inainte = {"alocat_mb": _mb(torch.cuda.memory_allocated()), "rezervat_mb": _mb(torch.cuda.memory_reserved()),
                   "nvidia_smi_mb": urm.citeste_acum()}
        torch.cuda.reset_peak_memory_stats()
        urm.faza = f"{ora['ora']}_{nume}"
        t0 = time.perf_counter()
        valoare = f()
        torch.cuda.synchronize()
        secunde = time.perf_counter() - t0
        dupa = {"alocat_mb": _mb(torch.cuda.memory_allocated()), "rezervat_mb": _mb(torch.cuda.memory_reserved()),
                "nvidia_smi_mb": urm.citeste_acum()}
        ora[nume] = {"inainte": inainte, "dupa": dupa, "secunde": round(secunde, 1),
                     "varf_alocat_mb": _mb(torch.cuda.max_memory_allocated()),
                     "varf_rezervat_mb": _mb(torch.cuda.max_memory_reserved()),
                     "varf_nvidia_smi_mb": urm.varfuri.get(urm.faza, 0)}
        urm.faza = ""
        scrie()
        return valoare

    try:
        for i in range(1, repetari + 1):
            ora: dict[str, Any] = {"ora": i}
            rezultat["ore"].append(ora)
            model = ModelGPTConversatieMuon(**setari)
            stat = faza(ora, "antrenare", lambda: model.antreneaza(date, 3600.0))
            ora["antrenare"].update(pasi=stat["pasi"], pasi_optimizator=stat.get("pasi_optimizator"),
                                    pasi_pe_secunda=round(stat["pasi"] / max(stat["secunde_bucla"], 1e-9), 2),
                                    pierdere=stat.get("pierdere_finala", stat.get("pierdere")))

            def valideaza() -> float:
                scoruri = ExamenBpb().examineaza(model, date)
                v = scoruri[ExamenBpb.scor_principal]
                model.dupa_examen({"scor": v})
                return v

            ora["validare_biti"] = faza(ora, "validare", valideaza)
            model_test = ModelGPTConversatieMuon(**setari)

            def test_rapid() -> float:
                model_test.antreneaza(date, 2.0)
                return model_test.biti_pentru(mostra)

            ora["test_rapid_biti"] = faza(ora, "test_rapid", test_rapid)
            if goleste:
                del model, model_test
                gc.collect()
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                ora["dupa_golire"] = {"alocat_mb": _mb(torch.cuda.memory_allocated()),
                                      "rezervat_mb": _mb(torch.cuda.memory_reserved()),
                                      "nvidia_smi_mb": urm.citeste_acum()}
            scrie()
        rezultat["terminat"] = True
    except torch.cuda.OutOfMemoryError as e:
        rezultat["eroare"] = f"out of memory: {str(e).splitlines()[0]}"
    finally:
        alocat = [o["test_rapid"]["dupa"]["alocat_mb"] for o in rezultat["ore"] if "test_rapid" in o]
        rezultat["alocat_dupa_test_rapid_mb"] = alocat
        rezultat["memoria_creste"] = creste(alocat)
        urm.opreste()
        scrie()
    return rezultat


def _memorie(torch: Any, urm: Urmaritor) -> dict[str, Any]:
    torch.cuda.synchronize()
    return {"alocat_mb": _mb(torch.cuda.memory_allocated()), "rezervat_mb": _mb(torch.cuda.memory_reserved()),
            "nvidia_smi_mb": urm.citeste_acum()}


def _goleste(torch: Any) -> None:
    gc.collect()
    torch.cuda.empty_cache()


def ruleaza_orchestrator(varianta: str, repetari: int, pasi_optimizator: int, golire: str, iesire: Path,
                         memorie_max_mb: int) -> dict[str, Any]:
    """S87: „orele” în ordinea din kronos/orchestrator.py (liniile ~191–231, doar citit): model_test → test rapid →
    model → antrenare → validare (examen + dupa_examen), cu model_test încă ținut. O oră e o funcție: la ieșirea din ea
    variabilele locale se eliberează singure, ca la ieșirea din experimentul orchestratorului; nimic nu se șterge explicit.
    golire: „nimic”; „gc” = gc.collect() + empty_cache() la începutul fiecărei ore; „del” = ca „gc”, plus
    `del model_test` + gc.collect() + empty_cache() înainte de construirea lui model (doar ca informație)."""
    import torch

    from module.date_amestec import DateAmestec
    from module.examen_bpb import ExamenBpb
    from module.model_muon import ModelGPTConversatieMuon
    from unelte import antrenare_recalcul

    fractie = antrenare_recalcul.plafon_placa(memorie_max_mb)
    antrenare_recalcul.instaleaza()
    dosar = iesire.parent
    dosar.mkdir(parents=True, exist_ok=True)
    copie = dosar / "gpt.pt"
    shutil.copyfile(SURSA, copie)
    setari = setari_model(varianta, copie, pasi_optimizator)
    date = DateAmestec(**setari_date())
    mostra = date.text_validare()[:CARACTERE_TEST_RAPID]
    urm = Urmaritor()
    urm.porneste()
    rezultat: dict[str, Any] = {"varianta": varianta, **VARIANTE[varianta], "ordine": "orchestrator", "golire": golire,
                                "pasi_optimizator": pasi_optimizator, "pasi_max": setari["pasi_max"],
                                "repetari": repetari, "plafon_pytorch_mb": memorie_max_mb, "fractie": fractie,
                                "ore": [], "terminat": False}

    def scrie() -> None:
        rezultat["temperatura_max"] = urm.temperatura_max
        iesire.write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")

    def faza(ora: dict[str, Any], nume: str, f: Any) -> Any:
        inainte = _memorie(torch, urm)
        torch.cuda.reset_peak_memory_stats()
        urm.faza = f"{ora['ora']}_{nume}"
        t0 = time.perf_counter()
        valoare = f()
        torch.cuda.synchronize()
        secunde = time.perf_counter() - t0
        ora[nume] = {"inainte": inainte, "dupa": _memorie(torch, urm), "secunde": round(secunde, 1),
                     "varf_alocat_mb": _mb(torch.cuda.max_memory_allocated()),
                     "varf_rezervat_mb": _mb(torch.cuda.max_memory_reserved()),
                     "varf_nvidia_smi_mb": urm.varfuri.get(urm.faza, 0)}
        urm.faza = ""
        scrie()
        return valoare

    def o_ora(ora: dict[str, Any]) -> None:
        ora["inceput"] = _memorie(torch, urm)
        if golire in ("gc", "del"):
            _goleste(torch)
            ora["inceput_dupa_golire"] = _memorie(torch, urm)
        scrie()
        model_test = ModelGPTConversatieMuon(**setari)

        def test_rapid() -> float:
            model_test.antreneaza(date, 2.0)
            return model_test.biti_pentru(mostra)

        ora["test_rapid_biti"] = faza(ora, "test_rapid", test_rapid)
        if golire == "del":
            del model_test
            _goleste(torch)
            ora["dupa_del_model_test"] = _memorie(torch, urm)
        model = ModelGPTConversatieMuon(**setari)
        stat = faza(ora, "antrenare", lambda: model.antreneaza(date, 3600.0))
        ora["antrenare"].update(pasi=stat["pasi"], pasi_optimizator=stat.get("pasi_optimizator"),
                                pasi_pe_secunda=round(stat["pasi"] / max(stat["secunde_bucla"], 1e-9), 2),
                                pierdere=stat.get("pierdere_finala", stat.get("pierdere")))

        def valideaza() -> float:
            scoruri = ExamenBpb().examineaza(model, date)
            v = scoruri[ExamenBpb.scor_principal]
            model.dupa_examen({"scor": v})
            return v

        ora["validare_biti"] = faza(ora, "validare", valideaza)

    try:
        for i in range(1, repetari + 1):
            ora: dict[str, Any] = {"ora": i}
            rezultat["ore"].append(ora)
            o_ora(ora)
            scrie()
        rezultat["dupa_ultima_ora"] = _memorie(torch, urm)
        rezultat["terminat"] = True
    except torch.cuda.OutOfMemoryError as e:
        ora_c = rezultat["ore"][-1] if rezultat["ore"] else {}
        fazele = [f for f in ("test_rapid", "antrenare", "validare") if f in ora_c]
        rezultat["eroare"] = f"out of memory: {str(e).splitlines()[0]}"
        rezultat["eroare_la"] = {"ora": ora_c.get("ora"), "dupa_faza": fazele[-1] if fazele else "început"}
    finally:
        rezultat["alocat_inceput_ora_mb"] = alocat_inceput(rezultat["ore"])
        urm.opreste()
        scrie()
    return rezultat


def alocat_inceput(ore: list[dict[str, Any]]) -> list[int]:
    """Alocatul PyTorch la începutul fiecărei ore, după golirea de început a variantei (dacă are), ca intră în oră."""
    return [(o.get("inceput_dupa_golire") or o["inceput"])["alocat_mb"] for o in ore if "inceput" in o]


def crestere_ora3(r: dict[str, Any]) -> int | None:
    """memory_allocated la începutul orei 3 minus la începutul orei 1 (None dacă ora 3 n-a început)."""
    a = r.get("alocat_inceput_ora_mb") or alocat_inceput(r.get("ore", []))
    return a[2] - a[0] if len(a) >= 3 else None


def varf_nvidia(r: dict[str, Any]) -> int:
    """Cel mai mare nvidia-smi văzut: de părinte (la 0,5 s) sau de copil, pe faze."""
    copil = [f.get("varf_nvidia_smi_mb", 0) for o in r.get("ore", []) for f in o.values() if isinstance(f, dict)]
    return max([r.get("nvidia_smi_varf_parinte_mb", 0), *copil])


def a_cazut(r: dict[str, Any]) -> bool:
    """Out of memory, cod ≠ 0, oprit de paza părintelui sau peste 6.700 MB nvidia-smi."""
    return bool(r.get("eroare")) or r.get("cod", 0) != 0 or bool(r.get("oprit_de_paza")) or varf_nvidia(r) > PRAG_MB


def verdicte_s87(variante: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Pragurile pre-înregistrării memorie_ore (scrise de supraveghetor în coadă la S87)."""
    o, g, d = variante.get("b_orch", {}), variante.get("b_orch_gc", {}), variante.get("b_orch_del", {})
    c_o, c_g = crestere_ora3(o), crestere_ora3(g)
    p1 = (c_o is not None and c_o >= 300) or a_cazut(o) or not o.get("terminat")
    p2 = (bool(g.get("terminat")) and not a_cazut(g) and varf_nvidia(g) <= 6600 and c_g is not None and c_g < 100)
    return {"P1_memoria_creste": "DA" if p1 else "NU", "P2_golirea_ajuta": "DA" if p2 else "NU",
            "crestere_b_orch_mb": c_o, "crestere_b_orch_gc_mb": c_g, "crestere_b_orch_del_mb": crestere_ora3(d),
            "varf_nvidia_b_orch_mb": varf_nvidia(o), "varf_nvidia_b_orch_gc_mb": varf_nvidia(g),
            "varf_nvidia_b_orch_del_mb": varf_nvidia(d), "b_orch_del_trece": bool(d.get("terminat")) and not a_cazut(d)}


DOSAR_ORE = RADACINA / "lucru" / "memorie_ore"
PLAN_S87 = [("b_orch", "nimic"), ("b_orch_gc", "gc"), ("b_orch_del", "del")]


def _sha(cale: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with cale.open("rb") as f:
        for bucata in iter(lambda: f.read(1 << 24), b""):
            h.update(bucata)
    return h.hexdigest()


def ore(pasi_optimizator: int, memorie_max_mb: int, repetari: int = 3) -> dict[str, Any]:
    iesire = DOSAR_ORE / "s87.json"
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja: măsurarea S87 s-a făcut, nu se reface.")
    DOSAR_ORE.mkdir(parents=True, exist_ok=True)
    rezultat: dict[str, Any] = {"pornit": time.strftime("%Y-%m-%dT%H:%M:%S"), "pasi_optimizator": pasi_optimizator,
                                "repetari": repetari, "sha_gpt_24_inainte": _sha(SURSA) if SURSA.exists() else None,
                                "variante": {}}
    for eticheta, golire in PLAN_S87:
        rezultat["variante"][eticheta] = in_proces_nou("b", repetari, pasi_optimizator, False, eticheta,
                                                       memorie_max_mb, dosar=DOSAR_ORE, golire=golire)
        (DOSAR_ORE / "s87_partial.json").write_text(json.dumps(rezultat, ensure_ascii=False, indent=1),
                                                    encoding="utf-8")
    rezultat["verdicte"] = verdicte_s87(rezultat["variante"])
    rezultat["sha_gpt_24_dupa"] = _sha(SURSA) if SURSA.exists() else None
    rezultat["terminat"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    iesire.write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(rezultat["verdicte"], ensure_ascii=False), flush=True)
    return rezultat


def in_proces_nou(varianta: str, repetari: int, pasi_optimizator: int, goleste: bool, eticheta: str,
                  memorie_max_mb: int, pas_urmarire: float = 0.5, dosar: Path | None = None,
                  golire: str | None = None) -> dict[str, Any]:
    """`unul` într-un proces nou; peste 7.000 MB sau la 83 °C îl oprește. Întoarce rezultatul copilului + paza.
    Cu `golire` (S87): ordinea orchestratorului, cu golirea dată."""
    dosar = (dosar or DOSAR) / eticheta
    dosar.mkdir(parents=True, exist_ok=True)
    iesire = dosar / "rezultat.json"
    comanda = [sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "unul", "--varianta", varianta,
               "--repetari", str(repetari), "--pasi-optimizator", str(pasi_optimizator), "--iesire", str(iesire),
               "--memorie-max-mb", str(memorie_max_mb)] + (["--goleste"] if goleste else [])
    if golire is not None:
        comanda += ["--ordine", "orchestrator", "--golire", golire]
    print(f"== {eticheta}: {' '.join(comanda[3:])}", flush=True)
    p = subprocess.Popen(comanda, cwd=RADACINA)
    varf = {"mb": 0, "c": 0, "oprit": ""}

    def urmareste() -> None:
        while p.poll() is None:
            c = nvidia_smi()
            if c:
                varf["mb"], varf["c"] = max(varf["mb"], c[0]), max(varf["c"], c[1])
                if c[0] > OPRIRE_MB or c[1] >= TEMPERATURA_MAX:
                    varf["oprit"] = f"{c[0]} MB, {c[1]} °C"
                    p.kill()
            time.sleep(pas_urmarire)

    fir = threading.Thread(target=urmareste, daemon=True)
    t0 = time.perf_counter()
    fir.start()
    cod = p.wait()
    fir.join()
    r: dict[str, Any] = json.loads(iesire.read_text(encoding="utf-8")) if iesire.exists() else {}
    r.update(eticheta=eticheta, cod=cod, secunde_proces=round(time.perf_counter() - t0, 1),
             nvidia_smi_varf_parinte_mb=varf["mb"], temperatura_max_parinte=varf["c"],
             peste_prag=varf["mb"] > PRAG_MB or bool(r.get("eroare")) or cod != 0)
    if varf["oprit"]:
        r["oprit_de_paza"] = varf["oprit"]
    print(f"   cod {cod}, vârf nvidia-smi {varf['mb']} MB, {varf['c']} °C, {r['secunde_proces']} s", flush=True)
    return r


def toate(pasi_optimizator: int, memorie_max_mb: int) -> dict[str, Any]:
    iesire = DOSAR / "s86.json"
    if iesire.exists():
        raise SystemExit(f"{iesire} există deja: măsurarea S86 s-a făcut, nu se reface.")
    DOSAR.mkdir(parents=True, exist_ok=True)
    rezultat: dict[str, Any] = {"pornit": time.strftime("%Y-%m-%dT%H:%M:%S"), "pasi_optimizator": pasi_optimizator,
                                "prag_mb": PRAG_MB, "variante": {}}
    plan = [("a", 3, False, "a"), ("b", 1, False, "b"), ("c", 1, False, "c"), ("d", 1, False, "d")]
    for varianta, repetari, goleste, eticheta in plan:
        rezultat["variante"][eticheta] = in_proces_nou(varianta, repetari, pasi_optimizator, goleste, eticheta,
                                                       memorie_max_mb)
        (DOSAR / "s86_partial.json").write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")
    if rezultat["variante"]["a"].get("memoria_creste") or rezultat["variante"]["a"].get("eroare"):
        rezultat["variante"]["a_golit"] = in_proces_nou("a", 3, pasi_optimizator, True, "a_golit", memorie_max_mb)
    rezultat["terminat"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    iesire.write_text(json.dumps(rezultat, ensure_ascii=False, indent=1), encoding="utf-8")
    return rezultat


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="comanda", required=True)
    t = sub.add_parser("toate")
    t.add_argument("--pasi-optimizator", type=int, default=50)
    t.add_argument("--memorie-max-mb", type=int, default=5800)
    u = sub.add_parser("unul")
    u.add_argument("--varianta", choices=sorted(VARIANTE), required=True)
    u.add_argument("--repetari", type=int, default=1)
    u.add_argument("--pasi-optimizator", type=int, default=50)
    u.add_argument("--goleste", action="store_true")
    u.add_argument("--iesire", type=Path, required=True)
    u.add_argument("--memorie-max-mb", type=int, default=5800)
    u.add_argument("--ordine", choices=["s86", "orchestrator"], default="s86")
    u.add_argument("--golire", choices=["nimic", "gc", "del"], default="nimic")
    o = sub.add_parser("ore", help="S87: b_orch, b_orch_gc, b_orch_del → lucru/memorie_ore/s87.json")
    o.add_argument("--pasi-optimizator", type=int, default=50)
    o.add_argument("--memorie-max-mb", type=int, default=5800)
    o.add_argument("--repetari", type=int, default=3)
    a = p.parse_args(argv)
    if a.comanda == "toate":
        toate(a.pasi_optimizator, a.memorie_max_mb)
        return 0
    if a.comanda == "ore":
        ore(a.pasi_optimizator, a.memorie_max_mb, a.repetari)
        return 0
    if a.ordine == "orchestrator":
        r = ruleaza_orchestrator(a.varianta, a.repetari, a.pasi_optimizator, a.golire, a.iesire, a.memorie_max_mb)
        return 0 if r.get("terminat") else 1
    r = ruleaza_unul(a.varianta, a.repetari, a.pasi_optimizator, a.goleste, a.iesire, a.memorie_max_mb)
    return 0 if r.get("terminat") else 1


if __name__ == "__main__":
    raise SystemExit(main())
