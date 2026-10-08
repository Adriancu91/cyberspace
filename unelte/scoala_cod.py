"""Școala de cod (Kronos Code Bootstrapping v0.1): pregătirea, bucla pe un nivel și pilotul (planul, secțiunile 6–10).

**O rundă**, pe o linie (A sau B) și un nivel:
1. 100 de încercări pe sarcini din setul văzut (20 de sarcini × 5, același text din față pentru cele 5), eșantionate
   cu temperatura curentă;
2. fiecare încercare → sandbox → verificator → trecut / picat / trișat;
3. încercările trecute, deduplicate, intră în biblioteca liniei (lucru/cod/biblioteca_<linie>.txt, format episod).
   Cele picate stau deoparte, în lucru/cod/respinse/<linie>.jsonl, și nu intră în antrenare;
4. antrenare scurtă (200 de pași, rată mică și fixă, fără repornire):
   - linia A: doar pe abecedar (biblioteca se umple, dar nu se antrenează pe ea);
   - linia B: pe abecedar și pe biblioteca ei (abecedarul cel puțin 5%);
5. măsurarea pe setul nevăzut, fără întâmplare:
   - cel puțin 80%: nivel trecut → adversarial și sacru (doar pentru raport) → îngheț → regresie;
   - altfel: runda următoare;
   - buget epuizat (30 de minute sau 60 de runde): nivel picat → adversarial și sacru → îngheț → oprirea liniei și
     raport. Nivelul nu se coboară.

**Temperatura:** pornește de la `start` (1,0 la nivelurile 0–2). Scade la 0,7 când trec peste 10% din încercările pe
văzut și la 0,5 peste 50%. Pe un nivel, doar scade.

**Liniile A și B** au aceleași sarcini, aceleași texte din față și aceleași semințe în fiecare rundă. Pornesc din
aceeași pregătire. La pilot, merg pe rând la fiecare nivel (A, apoi B). O linie se oprește la primul ei nivel picat
(sau la o regresie), iar cealaltă continuă: tocmai diferența dintre ele e întrebarea.

**Paznicul**, înainte de fiecare rundă:
- amprentele;
- STOP (lucru/STOP);
- configurarea schimbată fără îngheț;
- un singur lucru pe placă;
- temperatura;
- alimentarea.

După fiecare rundă verifică memoria video. Încercările „trișat” se numără; peste 50% într-o rundă se raportează.

**Jurnalul:** lucru/cod/runde.jsonl, un rând pe rundă, plus pregătirea, înghețurile, rollback-urile și deciziile,
fiecare cu motivul în română. Starea: lucru/cod/stare.json.

    python unelte/scoala_cod.py --genereaza-sacru     # o singură dată
    python unelte/scoala_cod.py --aproba-amprente
    python unelte/scoala_cod.py --pilot               # pregătirea, înghețul „inainte_de_pilot”, nivelurile 0 → 3B
    python unelte/scoala_cod.py --nivel 2A --linie B  # un singur nivel, pe o linie
    python unelte/scoala_cod.py --stare
    python unelte/raport_cod.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import shutil
import sys
import time
import tomllib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.cod import ordinea, paznic_cod, sandbox  # noqa: E402
from module.cod.examen_cod import Sarcina, Seturi, citeste_sacru, genereaza_sacru, judeca, seturi  # noqa: E402
from module.cod.mediu import Abecedar, Episod, citeste_abecedar, incercarea, schelet, text_fata  # noqa: E402
from unelte.ingheata_cod import exista, ingheata, scrie_in_jurnal  # noqa: E402

SECTIUNI = ("scoala", "mediu", "sandbox", "examen", "runda", "pregatire", "temperatura", "buget", "regresie", "paznic",
            "pilot")


def samanta(*parti: Any) -> int:
    """O sămânță întreagă, mereu aceeași pentru aceleași părți (ex. nivelul și runda): la fel pentru A și B."""
    return int(hashlib.sha256(":".join(map(str, parti)).encode("utf-8")).hexdigest()[:8], 16)


def citeste_config(cale: str | Path) -> dict[str, Any]:
    with open(cale, "rb") as f:
        cfg = tomllib.load(f)
    lipsa = [s for s in SECTIUNI if s not in cfg]
    if lipsa:
        raise ValueError(f"în {cale} lipsește: {', '.join(f'[{s}]' for s in lipsa)}")
    for nivel in cfg["pilot"]["niveluri"]:
        ordinea(nivel)
    if not set(cfg["pilot"]["linii"]) <= {"A", "B"}:
        raise ValueError("[pilot] linii: doar A și B în v0.1")
    if cfg["runda"]["incercari"] % cfg["runda"]["sarcini"]:
        raise ValueError("[runda] incercari trebuie să se împartă exact la sarcini (ex. 100 = 20 × 5)")
    return cfg


# --- biblioteca unei linii --------------------------------------------------------------------------------------------

class Biblioteca:
    """Reușitele unei linii (doar cod 100% corect), deduplicate după (sarcină, cod), cu nivelul și runda la care au
    apărut. biblioteca_<linie>.txt = episoadele (pentru antrenare); biblioteca_<linie>.jsonl = aceleași, cu detalii."""

    def __init__(self, cod: Path, linie: str, scheletele_abecedarului: set[str]) -> None:
        self.fisier = cod / f"biblioteca_{linie}.jsonl"
        self.text = cod / f"biblioteca_{linie}.txt"
        self.abecedar = scheletele_abecedarului
        self.intrari = [json.loads(r) for r in self.fisier.read_text(encoding="utf-8").splitlines() if r.strip()] \
            if self.fisier.exists() else []
        self.chei = {(i["test"], i["cod"]) for i in self.intrari}

    def adauga(self, reusite: list[dict[str, Any]], nivel: str, runda: int) -> list[dict[str, Any]]:
        noi = []
        for r in reusite:
            cheie = (r["test"], r["cod"])
            if cheie in self.chei:
                continue
            self.chei.add(cheie)
            forma = schelet(r["cod"])
            noi.append({"nivel": nivel, "runda": runda, "test": r["test"], "cod": r["cod"], "rezultat": r["rezultat"],
                        "schelet": forma, "forma_noua": forma not in self.abecedar})
        if noi:
            self.fisier.parent.mkdir(parents=True, exist_ok=True)
            with self.fisier.open("a", encoding="utf-8") as f:
                f.writelines(json.dumps(i, ensure_ascii=False) + "\n" for i in noi)
            with self.text.open("a", encoding="utf-8") as f:
                f.writelines(Episod(i["test"], i["cod"], i["rezultat"], nivel).text() + "\n" for i in noi)
            self.intrari += noi
        return noi

    def episoade(self) -> str:
        return "".join(Episod(i["test"], i["cod"], i["rezultat"], i["nivel"]).text() + "\n" for i in self.intrari)


def text_antrenare(abecedar: str, biblioteca: str, fractie_minima: float) -> str:
    """Abecedarul, repetat cât să fie cel puțin `fractie_minima` din text, plus biblioteca (la linia B)."""
    if not biblioteca:
        return abecedar
    repetari = max(1, math.ceil(fractie_minima * len(biblioteca) / ((1 - fractie_minima) * len(abecedar))))
    return "\n".join([abecedar] * repetari) + "\n" + biblioteca


# --- școala -----------------------------------------------------------------------------------------------------------

@dataclass
class Scoala:
    cfg: dict[str, Any]
    radacina: Path = RADACINA
    cale_config: Path | None = None                     # pentru regula „îngheț înainte de schimbarea configurării”
    fabrica_elev: Callable[[Path], Any] | None = None   # implicit: ElevCod (modelul Kronos)
    senzori: paznic_cod.Senzori = field(default_factory=paznic_cod.Senzori)
    git_la_inghet: bool = True
    afiseaza: Callable[[str], None] = field(default=lambda text: print(text, flush=True))
    _seturi: dict[str, Seturi] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        s = self.cfg["scoala"]
        self.lucru = self._cale(s["director_lucru"])
        self.cod = self.lucru / "cod"
        self.abecedar: Abecedar = citeste_abecedar(self._cale(s["abecedar"]))
        self.texte_abecedar = {e.test for e in self.abecedar.episoade}
        self.schelete_abecedar = {schelet(e.cod) for e in self.abecedar.episoade}
        cale_sacru = self._cale(s["sacru"])
        self.sacru: dict[str, list[Sarcina]] = citeste_sacru(cale_sacru) if cale_sacru.exists() else {}
        if self.fabrica_elev is None:
            from module.cod.elev import ElevCod

            self.fabrica_elev = lambda cale: ElevCod(cale, s.get("dispozitiv", ""))

    def _cale(self, cale: str) -> Path:
        p = Path(cale)
        return p if p.is_absolute() else self.radacina / p

    # --- stare și jurnal ---------------------------------------------------------------------------------------------

    def stare(self) -> dict[str, Any]:
        fisier = self.cod / "stare.json"
        stare = json.loads(fisier.read_text(encoding="utf-8")) if fisier.exists() else {}
        stare.setdefault("versiune", 1)
        stare.setdefault("linii", {})
        for linie in ("A", "B"):
            sl = stare["linii"].setdefault(linie, {})
            for cheie, valoare in (("nivel_curent", None), ("niveluri_trecute", {}), ("niveluri_picate", {}),
                                   ("oprita", False), ("motiv_oprire", None), ("ultimul_inghet", None),
                                   ("temperatura", None), ("buget", {})):
                sl.setdefault(cheie, valoare)
        return stare

    def salveaza_stare(self, stare: dict[str, Any]) -> None:
        self.cod.mkdir(parents=True, exist_ok=True)
        stare["actualizat"] = datetime.now().isoformat(timespec="seconds")
        temporar = self.cod / "stare.json.tmp"
        temporar.write_text(json.dumps(stare, ensure_ascii=False, indent=1), encoding="utf-8")
        temporar.replace(self.cod / "stare.json")

    def jurnal(self, rand: dict[str, Any]) -> None:
        scrie_in_jurnal(self.cod, rand)
        if rand.get("motiv"):
            self.afiseaza(f"[{datetime.now():%H:%M:%S}] {rand.get('linie', '')} {rand.get('nivel', '')} "
                          f"{rand.get('tip')}: {rand['motiv']}")

    def amprenta_config(self) -> str | None:
        return hashlib.sha256(self.cale_config.read_bytes()).hexdigest() if self.cale_config else None

    def _eticheta_libera(self, baza: str) -> str:
        eticheta, i = baza, 2
        while exista(self.lucru, eticheta, self.git_la_inghet, self.radacina):
            eticheta, i = f"{baza}_{i}", i + 1
        return eticheta

    def _ingheata(self, stare: dict[str, Any], eticheta: str, motiv: str, linii: list[str] | None) -> None:
        stare["inghetat_dupa_ultima_runda"] = True
        self.salveaza_stare(stare)
        ingheata(self.lucru, eticheta, motiv, linii, git=self.git_la_inghet, radacina=self.radacina)

    # --- seturi, încercări, măsurare ---------------------------------------------------------------------------------

    def seturi(self, nivel: str) -> Seturi:
        if nivel not in self._seturi:
            if nivel not in self.sacru:
                raise RuntimeError(f"setul sacru lipsește pentru nivelul {nivel}: python unelte/scoala_cod.py "
                                   f"--genereaza-sacru")
            e = self.cfg["examen"]
            self._seturi[nivel] = seturi(nivel, self.texte_abecedar, self.sacru[nivel], e["vazut"], e["nevazut"],
                                         e["adversarial"], e["samanta_seturi"])
        return self._seturi[nivel]

    def fata(self, elev: Any, sarcina: Sarcina, nivel: str, rng: random.Random) -> tuple[str, int]:
        m = self.cfg["mediu"]
        text, puse = text_fata(self.abecedar, sarcina.text, nivel, rng, elev.numara, elev.context, m["max_simboluri"],
                               m["preambul_la_test"], m["max_episoade"])
        return text, len(puse)

    def ruleaza_cod(self, coduri: list[str]) -> list[sandbox.Rulare]:
        s = self.cfg["sandbox"]
        with ThreadPoolExecutor(max_workers=s["fire"]) as fire:
            return list(fire.map(lambda c: sandbox.ruleaza(c, s["timeout_secunde"], tuple(s["interzis"]),
                                                           s["iesire_max_caractere"]), coduri))

    def incearca(self, elev: Any, perechi: list[tuple[Sarcina, str]], n: int, temperatura: float,
                 seminte: list[int]) -> list[dict[str, Any]]:
        """Pentru fiecare (sarcină, text din față): n încercări → sandbox → verdict."""
        m = self.cfg["mediu"]
        generate = []
        for (sarcina, fata), seed in zip(perechi, seminte):
            for scris in elev.genereaza(fata, n, temperatura, m["max_simboluri"], seed):
                cod, ajuns = incercarea(scris)
                generate.append((sarcina, cod, ajuns))
        rulari = self.ruleaza_cod([cod for _, cod, _ in generate])
        rezultate = []
        for (sarcina, cod, ajuns), rulare in zip(generate, rulari):
            verdict, motiv = judeca(sarcina, cod, rulare)
            rezultate.append({"test": sarcina.text, "cod": cod, "ajuns_la_result": ajuns, "verdict": verdict,
                              "motiv": motiv, "rezultat": rulare.iesire.strip(),
                              "aproape": verdict == "picat" and motiv.startswith("rezultat corect")})
        return rezultate

    def masoara(self, elev: Any, sarcini: list[Sarcina], nume_set: str, nivel: str) -> tuple[float, list[dict[str, Any]]]:
        """Rata de trecere pe un set, fără întâmplare (temperatura examenului), cu texte din față mereu aceleași."""
        perechi = [(s, self.fata(elev, s, nivel, random.Random(samanta(nume_set, nivel, j)))[0])
                   for j, s in enumerate(sarcini)]
        rezultate = self.incearca(elev, perechi, 1, self.cfg["examen"]["temperatura_examen"],
                                  [samanta("examen", nume_set, nivel, j) for j in range(len(sarcini))])
        return sum(r["verdict"] == "trecut" for r in rezultate) / max(1, len(rezultate)), rezultate

    def ce_stia(self, elev: Any) -> float | None:
        """Biți pe octet pe o bucată fixă din validarea poveștilor: cât din ce știa modelul a rămas."""
        s = self.cfg["scoala"]
        cale = self._cale(s["povesti"])
        if not cale.exists() or not hasattr(elev, "biti_pe_octet"):
            return None
        return round(elev.biti_pe_octet(cale.read_text(encoding="utf-8")[: s["caractere_povesti"]]), 4)

    # --- runda ---------------------------------------------------------------------------------------------------

    def runda(self, linie: str, nivel: str, numar: int, elev: Any, temperatura: float,
              biblioteca: Biblioteca) -> dict[str, Any]:
        r, baza = self.cfg["runda"], self.cfg["scoala"]["samanta"]
        start = time.perf_counter()
        vazut = self.seturi(nivel).vazut
        sarcini = random.Random(samanta(baza, "runda", nivel, numar)).sample(vazut, min(r["sarcini"], len(vazut)))
        fete = [self.fata(elev, s, nivel, random.Random(samanta(baza, "fata", nivel, numar, j)))
                for j, s in enumerate(sarcini)]
        incercari = self.incearca(elev, [(s, f) for s, (f, _) in zip(sarcini, fete)], r["incercari"] // r["sarcini"],
                                  temperatura, [samanta(baza, "gen", nivel, numar, j) for j in range(len(sarcini))])
        secunde_incercari = time.perf_counter() - start
        trecute = [i for i in incercari if i["verdict"] == "trecut"]
        trisate = [i for i in incercari if i["verdict"] == "trișat"]
        noi = biblioteca.adauga(trecute, nivel, numar)
        respinse = self.cod / "respinse" / f"{linie}.jsonl"
        respinse.parent.mkdir(parents=True, exist_ok=True)
        with respinse.open("a", encoding="utf-8") as f:
            f.writelines(json.dumps({"nivel": nivel, "runda": numar, **{k: i[k] for k in ("test", "cod", "verdict",
                                     "motiv", "aproape")}}, ensure_ascii=False) + "\n"
                         for i in incercari if i["verdict"] != "trecut")
        text = text_antrenare(self.abecedar.text, biblioteca.episoade() if linie == "B" else "",
                              r["fractie_abecedar_minima"])
        antrenare = elev.antreneaza(text, r["pasi_antrenare"], r["rata"], r["lot"], samanta(baza, "antrenare", nivel, numar))
        inceput_masurare = time.perf_counter()
        rata_nevazut, _ = self.masoara(elev, self.seturi(nivel).nevazut, "nevazut", nivel)
        return {
            "tip": "runda", "linie": linie, "nivel": nivel, "runda": numar, "temperatura": temperatura,
            "incercari": len(incercari), "trecute": len(trecute), "picate": len(incercari) - len(trecute) - len(trisate),
            "trisate": len(trisate), "aproape": sum(i["aproape"] for i in incercari),
            "fara_result": sum(not i["ajuns_la_result"] for i in incercari), "unice_noi": len(noi),
            "forme_noi": sum(i["forma_noua"] for i in noi), "marime_biblioteca": len(biblioteca.intrari),
            "episoade_in_fata": round(sum(p for _, p in fete) / max(1, len(fete)), 2),
            "pasi_antrenare": antrenare["pasi"], "pierdere": antrenare["pierdere_finala"],
            "simboluri_antrenare": antrenare.get("simboluri_text"),
            "rata_vazut": round(len(trecute) / max(1, len(incercari)), 3), "rata_nevazut": round(rata_nevazut, 3),
            "secunde": round(time.perf_counter() - start, 1), "secunde_incercari": round(secunde_incercari, 1),
            "secunde_antrenare": antrenare.get("secunde"),
            "secunde_masurare": round(time.perf_counter() - inceput_masurare, 1),
            "memorie_video_mb": antrenare.get("memorie_video_mb"), "temperatura_placa": self.senzori.temperatura(),
            "trisat_raportat": len(trisate) / max(1, len(incercari)) > self.cfg["paznic"]["trisat_raportat_peste"],
            "exemple_trecute": [i["cod"] for i in trecute[:3]],
            "exemple_trisate": sorted({i["motiv"] for i in trisate})[:3],
        }

    def temperatura_de_start(self, nivel: str) -> float:
        t = self.cfg["temperatura"]
        return float(t.get("start_pe_nivel", {}).get(nivel, t["start"]))

    def temperatura_noua(self, temperatura: float, rata_vazut: float) -> float:
        t = self.cfg["temperatura"]
        if rata_vazut > 0.5:
            return min(temperatura, t["peste_50_la_suta"])
        if rata_vazut > 0.1:
            return min(temperatura, t["peste_10_la_suta"])
        return temperatura

    def _motiv_runda(self, r: dict[str, Any], linie: str, trecut: bool, temperatura: float, dupa: float) -> str:
        e, p = self.cfg["examen"], self.cfg["paznic"]
        parti = [f"văzut {r['trecute']}/{r['incercari']} trecute ({r['rata_vazut']:.0%})"
                 + (f", {r['trisate']} prinse trișând" if r["trisate"] else "")
                 + (f", {r['aproape']} cu rezultatul corect, dar fără forma cerută" if r["aproape"] else ""),
                 f"{r['unice_noi']} reușite noi în biblioteca liniei (are {r['marime_biblioteca']})",
                 f"antrenare {r['pasi_antrenare']} de pași pe "
                 + ("abecedar și bibliotecă" if linie == "B" else "abecedar (linia A nu se antrenează pe bibliotecă)"),
                 f"nevăzut {r['rata_nevazut']:.0%} " + (f"≥ {e['prag_trecere']:.0%}: nivel trecut" if trecut
                                                        else f"< {e['prag_trecere']:.0%}: runda următoare")]
        if dupa != temperatura:
            parti.append(f"temperatura {temperatura:g} → {dupa:g} (pe văzut au trecut peste "
                         f"{'50' if r['rata_vazut'] > 0.5 else '10'}%)")
        if r["trisat_raportat"]:
            parti.append(f"RAPORTAT: peste {p['trisat_raportat_peste']:.0%} din încercări au fost prinse trișând")
        return "; ".join(parti)

    # --- paznicul, înainte de fiecare rundă --------------------------------------------------------------------------

    def de_ce_nu_continui(self, stare: dict[str, Any], linie: str, nivel: str) -> str | None:
        p = self.cfg["paznic"]
        motiv = paznic_cod.verifica(self.radacina, self.lucru)
        if motiv:
            return motiv
        if paznic_cod.oprire_ceruta(self.lucru):
            return "butonul STOP (lucru/STOP)"
        acum = self.amprenta_config()
        if acum and stare.get("config_sha") not in (None, acum) and not stare.get("inghetat_dupa_ultima_runda"):
            return ("configurarea s-a schimbat de la ultima rundă, fără îngheț între ele (planul: îngheț obligatoriu "
                    "înainte de orice schimbare de configurare): python unelte/ingheata_cod.py --eticheta <nume> "
                    "--motiv \"...\", apoi pornește din nou")
        alte = self.senzori.alte_procese()
        if alte:
            return "un singur lucru pe placă, dar pe ea mai lucrează: " + "; ".join(alte)
        racire = paznic_cod.asteapta_racirea(p["temperatura_max"], p["racire_la"], self.senzori)
        if racire:
            self.jurnal({"tip": "racire", "linie": linie, "nivel": nivel, "motiv": racire})
        merge, alimentare = paznic_cod.asteapta_incarcatorul(self.senzori)
        if alimentare:
            self.jurnal({"tip": "alimentare", "linie": linie, "nivel": nivel, "motiv": alimentare})
        return None if merge else alimentare

    # --- un nivel, pe o linie ----------------------------------------------------------------------------------------

    def model_liniei(self, linie: str) -> Path:
        return self.cod / "linii" / linie / "model.pt"

    def nivel(self, linie: str, nivel: str) -> str:
        """Rundele unui nivel pe o linie, până la trecere sau la bugetul epuizat. Întoarce „trecut”, „picat”,
        „regresie” sau „oprit” (paznicul sau STOP; se poate relua de unde a rămas)."""
        b, p, e, m = self.cfg["buget"], self.cfg["paznic"], self.cfg["examen"], self.cfg["mediu"]
        ordinea(nivel)
        if not self.model_liniei(linie).exists():
            raise RuntimeError(f"linia {linie} n-are încă model: întâi pregătirea (python unelte/scoala_cod.py "
                               f"--pregateste)")
        stare = self.stare()
        sl = stare["linii"][linie]
        if sl["oprita"]:
            raise RuntimeError(f"linia {linie} e oprită ({sl['motiv_oprire']}); decide omul, de ex. rollback: "
                               f"python unelte/ingheata_cod.py --revino <nume> --motiv \"...\"")
        if nivel in sl["niveluri_trecute"]:
            raise RuntimeError(f"linia {linie} a trecut deja nivelul {nivel} (înghețul "
                               f"„{sl['niveluri_trecute'][nivel]['inghet']}”)")
        elev = self.fabrica_elev(self.model_liniei(linie))
        biblioteca = Biblioteca(self.cod, linie, self.schelete_abecedar)
        buget = sl["buget"].setdefault(nivel, {"runde": 0, "secunde": 0.0})
        reluat = sl["nivel_curent"] == nivel and sl["temperatura"] is not None
        temperatura = float(sl["temperatura"]) if reluat else self.temperatura_de_start(nivel)
        sl["nivel_curent"], sl["temperatura"] = nivel, temperatura
        self.salveaza_stare(stare)
        self.jurnal({"tip": "nivel_inceput", "linie": linie, "nivel": nivel, "temperatura": temperatura, "reluat": reluat,
                     "preambul_la_test": m["preambul_la_test"], "max_simboluri": m["max_simboluri"],
                     "motiv": f"{'reiau' if reluat else 'încep'} nivelul {nivel} pe linia {linie}: temperatura "
                              f"{temperatura:g}, buget {b['minute_pe_nivel']} de minute sau {b['runde_pe_nivel']} de runde"
                              + (f" (consumat: {buget['runde']} runde, {buget['secunde'] / 60:.1f} minute)"
                                 if reluat else "")
                              + f"; în față: {'preambulul și ' if m['preambul_la_test'] else ''}episoade din "
                                f"abecedar, cât încap"})
        ultima: dict[str, Any] | None = None
        while True:
            oprire = self.de_ce_nu_continui(stare, linie, nivel)
            if oprire:
                return self._oprit(stare, linie, nivel, oprire)
            if buget["runde"] >= b["runde_pe_nivel"] or buget["secunde"] >= 60 * b["minute_pe_nivel"]:
                return self._picat(stare, linie, nivel, buget, elev, ultima)
            rand = self.runda(linie, nivel, buget["runde"] + 1, elev, temperatura, biblioteca)
            buget["runde"] += 1
            buget["secunde"] = round(buget["secunde"] + rand["secunde"], 1)
            elev.salveaza(self.model_liniei(linie))
            trecut = rand["rata_nevazut"] >= e["prag_trecere"]
            dupa = self.temperatura_noua(temperatura, rand["rata_vazut"])
            rand["temperatura_urmatoare"] = dupa
            rand["motiv"] = self._motiv_runda(rand, linie, trecut, temperatura, dupa)
            self.jurnal(rand)
            sl["temperatura"] = temperatura = dupa
            stare["config_sha"], stare["inghetat_dupa_ultima_runda"] = self.amprenta_config(), False
            self.salveaza_stare(stare)
            ultima = rand
            vram = rand.get("memorie_video_mb") or 0
            if vram > p["memorie_video_max_mb"]:
                return self._oprit(stare, linie, nivel, f"memoria video {vram} MB, peste {p['memorie_video_max_mb']} MB")
            if trecut:
                return self._trecut(stare, linie, nivel, elev, rand, buget)

    def _oprit(self, stare: dict[str, Any], linie: str, nivel: str, motiv: str) -> str:
        self.salveaza_stare(stare)
        self.jurnal({"tip": "oprit", "linie": linie, "nivel": nivel,
                     "motiv": f"oprit: {motiv} (se poate relua de unde a rămas)"})
        return "oprit"

    def _picat(self, stare: dict[str, Any], linie: str, nivel: str, buget: dict[str, Any], elev: Any,
               ultima: dict[str, Any] | None) -> str:
        sl = stare["linii"][linie]
        adversarial, _ = self.masoara(elev, self.seturi(nivel).adversarial, "adversarial", nivel)
        sacru, _ = self.masoara(elev, self.seturi(nivel).sacru, "sacru", nivel)
        povesti = self.ce_stia(elev)
        eticheta = self._eticheta_libera(f"{linie}_{nivel}_picat")
        motiv = (f"nivelul {nivel} picat pe linia {linie}: buget epuizat ({buget['runde']} runde, "
                 f"{buget['secunde'] / 60:.0f} minute)")
        vazut = ultima["rata_vazut"] if ultima else None
        nevazut = ultima["rata_nevazut"] if ultima else None
        sl["niveluri_picate"][nivel] = {"vazut": vazut, "nevazut": nevazut, "adversarial": round(adversarial, 3),
                                        "sacru": round(sacru, 3), "runde": buget["runde"], "secunde": buget["secunde"],
                                        "inghet": eticheta, "povesti_bpo": povesti}
        sl.update(oprita=True, motiv_oprire=motiv)
        self._ingheata(stare, eticheta, motiv, [linie])
        procent = lambda x: "—" if x is None else f"{x:.0%}"  # noqa: E731
        self.jurnal({"tip": "nivel_picat", "linie": linie, "nivel": nivel, "runde": buget["runde"],
                     "secunde": buget["secunde"], "rata_vazut": vazut, "rata_nevazut": nevazut,
                     "rata_adversarial": round(adversarial, 3), "rata_sacru": round(sacru, 3), "povesti_bpo": povesti,
                     "inghet": eticheta,
                     "motiv": f"{motiv}; la ultima rundă: văzut {procent(vazut)}, nevăzut {procent(nevazut)}; "
                              f"adversarial {adversarial:.0%}, sacru {sacru:.0%} (doar pentru raport); înghețat "
                              f"„{eticheta}”. Linia se oprește: nivelul nu se coboară automat, decide omul"})
        return "picat"

    def _trecut(self, stare: dict[str, Any], linie: str, nivel: str, elev: Any, rand: dict[str, Any],
                buget: dict[str, Any]) -> str:
        sl = stare["linii"][linie]
        adversarial, _ = self.masoara(elev, self.seturi(nivel).adversarial, "adversarial", nivel)
        sacru, _ = self.masoara(elev, self.seturi(nivel).sacru, "sacru", nivel)
        povesti = self.ce_stia(elev)
        regresii = {}
        for anterior, info in sl["niveluri_trecute"].items():
            acum, _ = self.masoara(elev, self.seturi(anterior).nevazut, "nevazut", anterior)
            if info["nevazut"] - acum > self.cfg["regresie"]["scadere_maxima"] + 1e-9:
                regresii[anterior] = {"atunci": info["nevazut"], "acum": round(acum, 3)}
        principal = sl["ultimul_inghet"]
        eticheta = self._eticheta_libera(f"{linie}_{nivel}")
        sl["niveluri_trecute"][nivel] = {"vazut": rand["rata_vazut"], "nevazut": rand["rata_nevazut"],
                                         "adversarial": round(adversarial, 3), "sacru": round(sacru, 3),
                                         "runda": rand["runda"], "secunde": buget["secunde"], "inghet": eticheta,
                                         "regresii": regresii, "povesti_bpo": povesti}
        if regresii:
            sl.update(oprita=True, motiv_oprire=f"regresie după nivelul {nivel}: " + ", ".join(
                f"{n} {r['atunci']:.0%} → {r['acum']:.0%}" for n, r in regresii.items()))
        else:
            sl["ultimul_inghet"] = eticheta
        sl["nivel_curent"], sl["temperatura"] = None, None
        self._ingheata(stare, eticheta, f"linia {linie} a trecut nivelul {nivel} (nevăzut {rand['rata_nevazut']:.0%})"
                       + (", cu regresie" if regresii else ""), [linie])
        motiv = (f"nivelul {nivel} trecut pe linia {linie} în runda {rand['runda']}: nevăzut {rand['rata_nevazut']:.0%}, "
                 f"adversarial {adversarial:.0%}, sacru {sacru:.0%} (adversarialul și sacrul doar pentru raport); "
                 f"înghețat „{eticheta}”")
        if regresii:
            motiv += (f"; REGRESIE ({sl['motiv_oprire']}): modelul nu devine cel principal al liniei (rămâne "
                      f"„{principal}”), linia se oprește și decide omul. Pentru a continua din cel principal: "
                      f"python unelte/ingheata_cod.py --revino {principal} --motiv \"...\"")
        elif len(sl["niveluri_trecute"]) > 1:
            motiv += "; fără regresie pe nivelurile trecute înainte"
        self.jurnal({"tip": "regresie" if regresii else "nivel_trecut", "linie": linie, "nivel": nivel,
                     "runda": rand["runda"], "rata_vazut": rand["rata_vazut"], "rata_nevazut": rand["rata_nevazut"],
                     "rata_adversarial": round(adversarial, 3), "rata_sacru": round(sacru, 3), "regresii": regresii,
                     "povesti_bpo": povesti, "inghet": eticheta, "motiv": motiv})
        return "regresie" if regresii else "trecut"

    # --- pregătirea și pilotul ---------------------------------------------------------------------------------------

    def pregateste(self) -> dict[str, Any]:
        """Antrenare scurtă pe abecedar, din #252. Liniile A și B pornesc din același model pregătit."""
        p, c = self.cfg["pregatire"], self.cfg
        if (self.cod / "pregatit.pt").exists():
            raise RuntimeError("pregătirea e deja făcută (lucru/cod/pregatit.pt); liniile pornesc din ea")
        elev = self.fabrica_elev(self._cale(c["scoala"]["model_pornire"]))
        niveluri = c["pilot"]["niveluri"]
        inainte = {n: round(self.masoara(elev, self.seturi(n).nevazut, "nevazut", n)[0], 3) for n in niveluri}
        povesti_inainte = self.ce_stia(elev)
        antrenare = elev.antreneaza(self.abecedar.text, p["pasi"], p["rata"], c["runda"]["lot"],
                                    samanta(c["scoala"]["samanta"], "pregatire"))
        dupa = {n: round(self.masoara(elev, self.seturi(n).nevazut, "nevazut", n)[0], 3) for n in niveluri}
        povesti_dupa = self.ce_stia(elev)
        elev.salveaza(self.cod / "pregatit.pt")
        for linie in ("A", "B"):
            self.model_liniei(linie).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.cod / "pregatit.pt", self.model_liniei(linie))
        stare = self.stare()
        stare["pregatire"] = {"pasi": antrenare["pasi"], "rata": p["rata"], "pierdere": antrenare["pierdere_finala"],
                              "secunde": antrenare.get("secunde"), "nevazut_inainte": inainte, "nevazut_dupa": dupa,
                              "povesti_bpo_inainte": povesti_inainte, "povesti_bpo_dupa": povesti_dupa,
                              "timp": datetime.now().isoformat(timespec="seconds")}
        self.salveaza_stare(stare)
        self.jurnal({"tip": "pregatire", **stare["pregatire"], "memorie_video_mb": antrenare.get("memorie_video_mb"),
                     "motiv": f"pregătirea, din #252: {antrenare['pasi']} de pași pe abecedar (rata {p['rata']:g}); "
                              f"nevăzut înainte → după: "
                              + ", ".join(f"{n} {inainte[n]:.0%} → {dupa[n]:.0%}" for n in niveluri)
                              + (f"; povești (biți pe octet) {povesti_inainte} → {povesti_dupa}"
                                 if povesti_inainte is not None else "")
                              + "; liniile A și B pornesc amândouă din acest model"})
        return stare["pregatire"]

    def pilot(self) -> dict[str, str]:
        """Nivelurile pilotului, liniile pe rând la fiecare nivel. Fiecare linie se oprește la primul ei nivel picat."""
        motiv = paznic_cod.verifica(self.radacina, self.lucru) or paznic_cod.de_ce_nu_e_libera(self.senzori)
        if motiv:
            raise RuntimeError(motiv)
        niveluri, linii = self.cfg["pilot"]["niveluri"], self.cfg["pilot"]["linii"]
        self.jurnal({"tip": "pilot_inceput", "niveluri": niveluri, "linii": linii,
                     "motiv": f"pilotul pornește (sau se reia): nivelurile {', '.join(niveluri)}, liniile "
                              f"{' și '.join(linii)} pe rând la fiecare nivel, {self.cfg['buget']['minute_pe_nivel']} de "
                              f"minute pe nivel și linie"})
        if not (self.cod / "pregatit.pt").exists():
            self.pregateste()
        if not exista(self.lucru, "inainte_de_pilot", self.git_la_inghet, self.radacina):
            self._ingheata(self.stare(), "inainte_de_pilot", "înainte de pilot (obligatoriu), după pregătire", None)
        rezultate: dict[str, str] = {}
        for nivel in niveluri:
            for linie in linii:
                sl = self.stare()["linii"][linie]
                if sl["oprita"] or nivel in sl["niveluri_trecute"]:
                    continue
                rezultate[f"{linie} {nivel}"] = rezultat = self.nivel(linie, nivel)
                if rezultat == "oprit":
                    return rezultate
        self.jurnal({"tip": "pilot_gata", "rezultate": rezultate,
                     "motiv": "pilotul s-a încheiat: " + ", ".join(f"{k} {v}" for k, v in rezultate.items())
                              + ". Raportul: python unelte/raport_cod.py"})
        return rezultate


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Școala de cod: pregătirea, nivelurile și pilotul.")
    ce = parser.add_mutually_exclusive_group(required=True)
    ce.add_argument("--aproba-amprente", action="store_true")
    ce.add_argument("--genereaza-sacru", action="store_true")
    ce.add_argument("--pregateste", action="store_true")
    ce.add_argument("--nivel")
    ce.add_argument("--pilot", action="store_true")
    ce.add_argument("--stare", action="store_true")
    parser.add_argument("--linie", choices=("A", "B"))
    parser.add_argument("--motiv", default="", help="la --aproba-amprente: de ce (intră în jurnal)")
    parser.add_argument("--config", default="config/scoala_cod.toml")
    args = parser.parse_args(argv)
    cale_config = Path(args.config) if Path(args.config).is_absolute() else RADACINA / args.config
    cfg = citeste_config(cale_config)
    if args.genereaza_sacru:
        cale = RADACINA / cfg["scoala"]["sacru"]
        if cale.exists():
            print(f"Setul sacru există deja ({cale}): nu se regenerează.")
            return 1
        abecedar = citeste_abecedar(RADACINA / cfg["scoala"]["abecedar"])
        date = genereaza_sacru({e.test for e in abecedar.episoade}, cfg["examen"]["sacru"])
        cale.write_text(json.dumps(date, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Setul sacru: {sum(len(v) for v in date['niveluri'].values())} de sarcini în {cale}. Urmează: git add -f "
              f"{cfg['scoala']['sacru']} și python unelte/scoala_cod.py --aproba-amprente")
        return 0
    scoala = Scoala(cfg, cale_config=cale_config)
    try:
        if args.aproba_amprente:
            for nume, valoare in paznic_cod.aproba(RADACINA, scoala.lucru).items():
                print(f"   {nume}: {valoare[:16]}…")
            scoala.jurnal({"tip": "amprente_aprobate", "motiv": "amprentele examenului, sacrului, abecedarului și "
                                                               "sandbox-ului au fost aprobate"
                                                               + (f": {args.motiv}" if args.motiv else "")})
            return 0
        if args.stare:
            print(json.dumps(scoala.stare(), ensure_ascii=False, indent=1))
            return 0
        if args.nivel and not args.linie:
            raise RuntimeError("--nivel cere --linie A sau B")
        import torch

        if cfg["scoala"].get("dispozitiv", "") != "cpu" and not torch.cuda.is_available():
            raise RuntimeError("placa video nu se vede (CUDA): școala rulează pe procesor doar cu dispozitiv = \"cpu\" "
                               "în configurare")
        if args.pregateste:
            motiv = paznic_cod.verifica(RADACINA, scoala.lucru) or paznic_cod.de_ce_nu_e_libera(scoala.senzori)
            if motiv:
                raise RuntimeError(motiv)
            scoala.pregateste()
            return 0
        if args.nivel:
            motiv = paznic_cod.de_ce_nu_e_libera(scoala.senzori)
            if motiv:
                raise RuntimeError(motiv)
            return 0 if scoala.nivel(args.linie, args.nivel) == "trecut" else 1
        rezultate = scoala.pilot()
        return 0 if rezultate and all(v == "trecut" for v in rezultate.values()) else 1
    except (RuntimeError, FileExistsError, FileNotFoundError, ValueError) as eroare:
        print(f"Oprit: {eroare}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
