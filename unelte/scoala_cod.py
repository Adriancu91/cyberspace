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

**v0.3** (config/scoala_cod_v03.toml, în lucru/cod_v03/), pe lângă v0.2:
- **nivelul 0 = numerele 0–99 împreună** (intern „0n”), apoi cuvintele (0w). La amândouă, codul e doar valoarea sau
  print(valoarea);
- **linia D primește exact cât B**, cu repetări când nu mai sunt sarcini văzute noi;
- **la fiecare regresie, biblioteca se curăță** (lecția SANDBOX-7): soluțiile care, mutate pe sarcinile nevăzute de
  aceeași formă, pică, ies în respinse/ (module/cod/curatare.py);
- **oprirea singură la `[buget] oprire_la`** (18:30), cu îngheț, ca placa să fie liberă la 19:00;
- **raportul** se scrie singur la sfârșitul pilotului.

**v0.2** (config/scoala_cod_v02.toml, în lucru/cod_v02/):
- **poveștile rămân în lecții:** 70% din fiecare lot vine din textul de antrenare al poveștilor. Biții pe octet pe
  povești se măsoară la fiecare îngheț; peste 0,46 e regresie;
- **pregătirea** se oprește la o pierdere pe abecedar de ~0,5 sau la un număr fix de pași;
- **treptele 0a, 0b, 1a, 1b:** numere de o cifră, apoi de două cifre. 0a are seturi mici: doar 8 numere de o cifră nu
  sunt în abecedar;
- **linia D (control):** în fiecare rundă primește tot atâtea soluții corecte câte reușite noi a avut B în aceeași
  rundă. Soluțiile vin de la unealtă (sarcini văzute alese la întâmplare, cu soluția noastră), nu descoperite de D.

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
from module.cod.examen_cod import (Sarcina, Seturi, adauga_sacru, citeste_sacru, genereaza_sacru, judeca,  # noqa: E402
                                   seturi)
from module.cod.mediu import (Abecedar, Episod, citeste_abecedar, incercarea, schelet, text_cu_regula,  # noqa: E402
                              text_fata)
from unelte.ingheata_cod import exista, ingheata, scrie_in_jurnal  # noqa: E402
from module.cod import curatare  # noqa: E402

SECTIUNI = ("scoala", "mediu", "sandbox", "examen", "runda", "pregatire", "temperatura", "buget", "regresie", "paznic",
            "pilot")
REGULI = ("scurta", "lunga", "fara")
LINII = ("A", "B", "D")
DESCRIERE_REGULA = {"scurta": "regula scurtată", "lunga": "regula lungă (preambulul)", "fara": "fără regulă"}


def procent(x: float | None) -> str:
    return "—" if x is None else f"{x:.0%}"


def rotunjit(x: float | None) -> float | None:
    return None if x is None else round(x, 3)


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
    linii = cfg["pilot"]["linii"]
    if not set(linii) <= set(LINII):
        raise ValueError(f"[pilot] linii: doar {', '.join(LINII)}")
    if "D" in linii and ("B" not in linii or linii.index("B") > linii.index("D")):
        raise ValueError("[pilot] linii: linia D cere linia B înaintea ei (primește câte soluții a găsit B)")
    if not 0 <= (cfg.get("povesti") or {}).get("fractie", 0) < 1:
        raise ValueError("[povesti] fractie: între 0 și 1")
    if cfg["runda"]["incercari"] % cfg["runda"]["sarcini"]:
        raise ValueError("[runda] incercari trebuie să se împartă exact la sarcini (ex. 100 = 20 × 5)")
    if cfg["mediu"]["regula"] not in REGULI:
        raise ValueError(f"[mediu] regula: una din {', '.join(REGULI)}")
    return cfg


def regulile(mediu: dict[str, Any], abecedar: Abecedar) -> tuple[str, str]:
    """(regula din fața modelului la test, regula din textul de pregătire și antrenare), după `[mediu] regula`:
    - „scurta”: regula scurtată, cuvânt cu cuvânt, în ambele (varianta 3);
    - „lunga”: preambulul abecedarului în ambele (varianta 1);
    - „fara”: nimic la test, preambulul în antrenare (varianta 2)."""
    scurta = mediu.get("regula_scurta", "").replace("\r\n", "\n").strip("\n") + "\n"
    return {"scurta": (scurta, scurta), "lunga": (abecedar.preambul, abecedar.preambul),
            "fara": ("", abecedar.preambul)}[mediu["regula"]]


# --- biblioteca unei linii --------------------------------------------------------------------------------------------

def scoase_la_curatare(cod: Path, linie: str, nume: str = "biblioteca") -> set[tuple[str, str]]:
    """(sarcina, codul) scoase din biblioteca `nume` a liniei la curățări (respinse/curatare_<linie>.jsonl)."""
    fisier = cod / "respinse" / f"curatare_{linie}.jsonl"
    if not fisier.exists():
        return set()
    randuri = [json.loads(r) for r in fisier.read_text(encoding="utf-8").splitlines() if r.strip()]
    return {(r["test"], r["cod"]) for r in randuri if r.get("biblioteca") == nume}


class Biblioteca:
    """Reușitele unei linii (doar cod 100% corect), deduplicate după (sarcină, cod), cu nivelul și runda la care au
    apărut. biblioteca_<linie>.txt = episoadele (pentru antrenare); biblioteca_<linie>.jsonl = aceleași, cu detalii."""

    def __init__(self, cod: Path, linie: str, scheletele_abecedarului: set[str], nume: str = "biblioteca") -> None:
        self.fisier = cod / f"{nume}_{linie}.jsonl"
        self.text = cod / f"{nume}_{linie}.txt"
        self.abecedar = scheletele_abecedarului
        self.intrari = [json.loads(r) for r in self.fisier.read_text(encoding="utf-8").splitlines() if r.strip()] \
            if self.fisier.exists() else []
        self.chei = {(i["test"], i["cod"]) for i in self.intrari}
        scoase = scoase_la_curatare(cod, linie, nume)  # rămân scoase și după un rollback la un îngheț mai vechi
        if any((i["test"], i["cod"]) in scoase for i in self.intrari):
            self.scoate([i for i in self.intrari if (i["test"], i["cod"]) in scoase])

    def adauga(self, reusite: list[dict[str, Any]], nivel: str, runda: int, repetari: bool = False) -> list[dict[str, Any]]:
        """Reușitele noi. Cu `repetari` (biblioteca uneltei la linia D, v0.3), și cele care există deja: D primește exact
        cât B, chiar dacă n-au mai rămas sarcini văzute noi."""
        noi = []
        for r in reusite:
            cheie = (r["test"], r["cod"])
            if cheie in self.chei and not repetari:
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

    def scoate(self, de_scos: list[dict[str, Any]]) -> None:
        """Scoate intrările date (curățarea): fișierele bibliotecii se rescriu fără ele, scrise întâi alături."""
        scoase = {id(i) for i in de_scos}
        self.intrari = [i for i in self.intrari if id(i) not in scoase]
        self.chei = {(i["test"], i["cod"]) for i in self.intrari}
        for fisier, text in ((self.fisier, "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in self.intrari)),
                             (self.text, self.episoade())):
            temporar = fisier.with_name(fisier.name + ".tmp")
            temporar.write_text(text, encoding="utf-8")
            temporar.replace(fisier)


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
    _povesti: Any = field(default=None, repr=False)
    ceas: Callable[[], datetime] = field(default=datetime.now, repr=False)

    def __post_init__(self) -> None:
        s = self.cfg["scoala"]
        self.lucru = self._cale(s["director_lucru"])
        self.dosar = s.get("dosar", "cod")          # v0.2: cod_v02 (v0.1 rămâne neatins în lucru/cod)
        self.cod = self.lucru / self.dosar
        self.prefix = s.get("prefix_inghet", "")   # v0.2: v02_ (tag-urile Git sunt comune tuturor versiunilor)
        self.abecedar: Abecedar = citeste_abecedar(self._cale(s["abecedar"]))
        self.regula_test, regula_antrenare = regulile(self.cfg["mediu"], self.abecedar)
        self.text_abecedar = text_cu_regula(self.abecedar, regula_antrenare)  # pregătirea și antrenarea
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
        for linie in LINII:
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
        while exista(self.lucru, eticheta, self.git_la_inghet, self.radacina, self.dosar):
            eticheta, i = f"{baza}_{i}", i + 1
        return eticheta

    def _ingheata(self, stare: dict[str, Any], eticheta: str, motiv: str, linii: list[str] | None) -> None:
        stare["inghetat_dupa_ultima_runda"] = True
        self.salveaza_stare(stare)
        ingheata(self.lucru, eticheta, motiv, linii, git=self.git_la_inghet, radacina=self.radacina, dosar=self.dosar)

    # --- seturi, încercări, măsurare ---------------------------------------------------------------------------------

    def seturi(self, nivel: str) -> Seturi:
        if nivel not in self._seturi:
            if nivel not in self.sacru:
                raise RuntimeError(f"setul sacru lipsește pentru nivelul {nivel}: python unelte/scoala_cod.py "
                                   f"--genereaza-sacru")
            e = self.cfg["examen"]
            m = e.get("marimi", {}).get(nivel, {})  # 0a: doar 8 numere de o cifră, deci seturi mici
            self._seturi[nivel] = seturi(nivel, self.texte_abecedar, self.sacru[nivel], m.get("vazut", e["vazut"]),
                                         m.get("nevazut", e["nevazut"]), m.get("adversarial", e["adversarial"]),
                                         e["samanta_seturi"])
        return self._seturi[nivel]

    def fata(self, elev: Any, sarcina: Sarcina, nivel: str, rng: random.Random) -> tuple[str, int]:
        """Textul din fața modelului, cu exact `[mediu] episoade` exemple: dacă nu încap, școala se oprește, nu dă
        testul cu mai puține exemple fără să spună."""
        m = self.cfg["mediu"]
        text, puse = text_fata(self.abecedar, sarcina.text, nivel, rng, elev.numara, elev.context, m["max_simboluri"],
                               self.regula_test, m["episoade"])
        if len(puse) < m["episoade"]:
            raise RuntimeError(f"în fața modelului încap doar {len(puse)} exemple din {m['episoade']} la „{sarcina.text}” "
                               f"(nivelul {nivel}); varianta textului din față trebuie schimbată de om")
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

    def masoara_sacru(self, elev: Any, nivel: str) -> float | None:
        """Setul sacru, doar la îngheț, pentru raport. None la un nivel fără set sacru (0a: toate cele 8 sarcini ale lui
        sunt deja în văzut și nevăzut)."""
        sarcini = self.seturi(nivel).sacru
        return self.masoara(elev, sarcini, "sacru", nivel)[0] if sarcini else None

    def ce_stia(self, elev: Any) -> float | None:
        """Biți pe octet pe o bucată fixă din validarea poveștilor: cât din ce știa modelul a rămas."""
        s = self.cfg["scoala"]
        cale = self._cale(s["povesti"])
        if not cale.exists() or not hasattr(elev, "biti_pe_octet"):
            return None
        return round(elev.biti_pe_octet(cale.read_text(encoding="utf-8")[: s["caractere_povesti"]]), 4)

    def povesti_antrenare(self, elev: Any) -> Any:
        """Simbolurile textului de antrenare al poveștilor (v0.2), citite o singură dată. Vin din memoria lui Kronos
        (director_cache, doar citire), dacă sunt acolo; altfel se împart cu tokenizer-ul elevului, doar la texte mici, ca
        în teste. Fără [povesti] sau cu fractie = 0: None (v0.1)."""
        pv = self.cfg.get("povesti") or {}
        if not pv.get("fractie"):
            return None
        if self._povesti is None:
            import torch

            text = self._cale(pv["text_antrenare"]).read_text(encoding="utf-8")
            if pv.get("director_cache"):
                from module.model_continuu import cale_simboluri

                tokenizer = self._cale(pv["tokenizer"])
                if hasattr(elev, "tokenizer_ca") and not elev.tokenizer_ca(tokenizer):
                    raise RuntimeError(f"tokenizer-ul elevului nu e {tokenizer}: simbolurile poveștilor n-ar fi ale lui")
                fisier = cale_simboluri(text, str(self._cale(pv["director_cache"])), str(tokenizer))
                if not fisier.exists():
                    raise RuntimeError(f"simbolurile poveștilor lipsesc din memoria lui Kronos ({fisier})")
                self._povesti = torch.load(fisier, weights_only=True)
            else:
                self._povesti = torch.tensor(elev.simboluri(text), dtype=torch.int32)
        return self._povesti

    def _antreneaza(self, elev: Any, text: str, pasi: int, rata: float, seed: int) -> dict[str, Any]:
        """Antrenarea școlii: textul școlii, plus poveștile (v0.2: 70% din fiecare lot), dacă sunt în configurare."""
        povesti = self.povesti_antrenare(elev)
        # v0.4: lotul trecut pe bucăți (micro_lot), doar dacă e în configurare: același lot, mai puțină memorie video
        bucati = {"micro_lot": self.cfg["runda"]["micro_lot"]} if self.cfg["runda"].get("micro_lot") else {}
        if povesti is None:
            return elev.antreneaza(text, pasi, rata, self.cfg["runda"]["lot"], seed, **bucati)
        return elev.antreneaza(text, pasi, rata, self.cfg["runda"]["lot"], seed, povesti=povesti,
                               fractie_povesti=self.cfg["povesti"]["fractie"], **bucati)

    def de_la_unealta(self, nivel: str, numar: int, unealta: Biblioteca) -> tuple[list[dict[str, Any]], int]:
        """Linia D: tot atâtea soluții corecte câte reușite noi a avut linia B în aceeași rundă a nivelului, date de
        unealtă. Sarcinile sunt alese la întâmplare din setul văzut (aceeași sămânță pe rundă), cu soluția noastră și
        rezultatul ei. Întoarce (adăugate, câte a găsit B); mai puține adăugate = n-au mai rămas sarcini văzute noi."""
        b = Biblioteca(self.cod, "B", self.schelete_abecedar)
        cate = sum(1 for i in b.intrari if i["nivel"] == nivel and i["runda"] == numar)
        if not cate:
            return [], 0
        vazut = list(self.seturi(nivel).vazut)
        random.Random(samanta(self.cfg["scoala"]["samanta"], "unealta", nivel, numar)).shuffle(vazut)
        alese = [s for s in vazut if (s.text, s.solutie) not in unealta.chei][:cate]
        repetari = bool(self.cfg["runda"].get("d_exact_cat_b"))
        if repetari and len(alese) < cate:  # v0.3: n-au mai rămas sarcini văzute noi, deci se repetă
            alese += [vazut[i % len(vazut)] for i in range(cate - len(alese))]
        noi = unealta.adauga([{"test": s.text, "cod": s.solutie, "rezultat": s.asteptat} for s in alese], nivel, numar,
                             repetari=repetari)
        return noi, cate

    # --- runda ---------------------------------------------------------------------------------------------------

    def runda(self, linie: str, nivel: str, numar: int, elev: Any, temperatura: float,
              biblioteca: Biblioteca, unealta: Biblioteca | None = None) -> dict[str, Any]:
        r, baza = self.cfg["runda"], self.cfg["scoala"]["samanta"]
        start = time.perf_counter()
        vazut = self.seturi(nivel).vazut
        sarcini = random.Random(samanta(baza, "runda", nivel, numar)).sample(vazut, min(r["sarcini"], len(vazut)))
        fete = [self.fata(elev, s, nivel, random.Random(samanta(baza, "fata", nivel, numar, j)))
                for j, s in enumerate(sarcini)]
        incercari = self.incearca(elev, [(s, f) for s, (f, _) in zip(sarcini, fete)], r["incercari"] // len(sarcini),
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
        de_la_unealta, cerute = [], 0
        if linie == "D" and unealta is not None:  # soluții date, nu descoperite: câte a găsit B în runda asta
            de_la_unealta, cerute = self.de_la_unealta(nivel, numar, unealta)
        lectii = biblioteca.episoade() if linie == "B" else unealta.episoade() if linie == "D" and unealta else ""
        text = text_antrenare(self.text_abecedar, lectii, r["fractie_abecedar_minima"])
        antrenare = self._antreneaza(elev, text, r["pasi_antrenare"], r["rata"], samanta(baza, "antrenare", nivel, numar))
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
            "simboluri_antrenare": antrenare.get("simboluri_text"), "ferestre_povesti": antrenare.get("ferestre_povesti", 0),
            "ferestre": antrenare.get("ferestre"),
            **({"de_la_unealta": len(de_la_unealta), "cerute_de_la_unealta": cerute,
                "marime_unealta": len(unealta.intrari)} if linie == "D" and unealta is not None else {}),
            "rata_vazut": round(len(trecute) / max(1, len(incercari)), 3), "rata_nevazut": round(rata_nevazut, 3),
            "secunde": round(time.perf_counter() - start, 1), "secunde_incercari": round(secunde_incercari, 1),
            "secunde_antrenare": antrenare.get("secunde"),
            "secunde_masurare": round(time.perf_counter() - inceput_masurare, 1),
            "memorie_video_mb": antrenare.get("memorie_video_mb"), "temperatura_placa": self.senzori.temperatura(),
            "placa": self.senzori.placa(),
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
                 + ("abecedar și bibliotecă" if linie == "B" else
                    f"abecedar și soluțiile uneltei ({r.get('de_la_unealta', 0)} noi, cât a găsit B în runda asta: "
                    f"{r.get('cerute_de_la_unealta', 0)}; are {r.get('marime_unealta', 0)})" if linie == "D" else
                    f"abecedar (linia {linie} nu se antrenează pe propriile reușite)")
                 + (f", cu {r['ferestre_povesti'] / r['ferestre']:.0%} povești" if r.get("ferestre_povesti") else ""),
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
        comun = self.cfg["buget"].get("stop_comun")
        if comun and (self.radacina / comun).exists():  # planul joi–sâmbătă: STOP-ul comun oprește tot, și școala
            return f"butonul STOP comun ({comun})"
        if self.dupa_ora_de_oprire():
            return (f"ora de oprire ({self.cfg['buget']['oprire_la']}): nicio rundă nouă după ea, ca placa să fie "
                    f"liberă pentru noapte (19:00)")
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
        unealta = Biblioteca(self.cod, linie, self.schelete_abecedar, "biblioteca_unealta") if linie == "D" else None
        buget = sl["buget"].setdefault(nivel, {"runde": 0, "secunde": 0.0})
        reluat = sl["nivel_curent"] == nivel and sl["temperatura"] is not None
        temperatura = float(sl["temperatura"]) if reluat else self.temperatura_de_start(nivel)
        sl["nivel_curent"], sl["temperatura"] = nivel, temperatura
        self.salveaza_stare(stare)
        self.jurnal({"tip": "nivel_inceput", "linie": linie, "nivel": nivel, "temperatura": temperatura, "reluat": reluat,
                     "regula": m["regula"], "episoade": m["episoade"], "max_simboluri": m["max_simboluri"],
                     "motiv": f"{'reiau' if reluat else 'încep'} nivelul {nivel} pe linia {linie}: temperatura "
                              f"{temperatura:g}, buget {b['minute_pe_nivel']} de minute sau {b['runde_pe_nivel']} de runde"
                              + (f" (consumat: {buget['runde']} runde, {buget['secunde'] / 60:.1f} minute)"
                                 if reluat else "")
                              + f"; în față: {DESCRIERE_REGULA[m['regula']]} + {m['episoade']} exemple din abecedar "
                                f"+ sarcina"})
        ultima: dict[str, Any] | None = None
        while True:
            oprire = self.de_ce_nu_continui(stare, linie, nivel)
            if oprire:
                return self._oprit(stare, linie, nivel, oprire)
            if buget["runde"] >= b["runde_pe_nivel"] or buget["secunde"] >= 60 * b["minute_pe_nivel"]:
                return self._picat(stare, linie, nivel, buget, elev, ultima)
            rand = self.runda(linie, nivel, buget["runde"] + 1, elev, temperatura, biblioteca, unealta)
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

    def dupa_ora_de_oprire(self) -> bool:
        """v0.3: după `[buget] oprire_la` (ex. „18:30”), școala nu mai începe nicio rundă."""
        ora = self.cfg["buget"].get("oprire_la")
        return bool(ora) and self.ceas().time() >= datetime.strptime(ora, "%H:%M").time()

    def _oprit(self, stare: dict[str, Any], linie: str, nivel: str, motiv: str) -> str:
        if motiv.startswith("ora de oprire"):  # raport parțial: starea liniei se îngheață, ca dimineața să se poată relua
            self._ingheata(stare, self._eticheta_libera(f"{self.prefix}{linie}_{nivel}_oprit"),
                           f"oprit la {self.cfg['buget']['oprire_la']}, în mijlocul nivelului {nivel}", [linie])
        self.salveaza_stare(stare)
        self.jurnal({"tip": "oprit", "linie": linie, "nivel": nivel,
                     "motiv": f"oprit: {motiv} (se poate relua de unde a rămas)"})
        return "oprit"

    def _picat(self, stare: dict[str, Any], linie: str, nivel: str, buget: dict[str, Any], elev: Any,
               ultima: dict[str, Any] | None) -> str:
        sl = stare["linii"][linie]
        adversarial, _ = self.masoara(elev, self.seturi(nivel).adversarial, "adversarial", nivel)
        sacru = self.masoara_sacru(elev, nivel)
        povesti = self.ce_stia(elev)
        peste = self.povesti_peste_prag(povesti)
        eticheta = self._eticheta_libera(f"{self.prefix}{linie}_{nivel}_picat")
        motiv = (f"nivelul {nivel} picat pe linia {linie}: buget epuizat ({buget['runde']} runde, "
                 f"{buget['secunde'] / 60:.0f} minute)")
        vazut = ultima["rata_vazut"] if ultima else None
        nevazut = ultima["rata_nevazut"] if ultima else None
        sl["niveluri_picate"][nivel] = {"vazut": vazut, "nevazut": nevazut, "adversarial": round(adversarial, 3),
                                        "sacru": rotunjit(sacru), "runde": buget["runde"], "secunde": buget["secunde"],
                                        "inghet": eticheta, "povesti_bpo": povesti, "regresie_povesti": peste}
        sl.update(oprita=True, motiv_oprire=motiv)
        self._ingheata(stare, eticheta, motiv, [linie])
        self.jurnal({"tip": "nivel_picat", "linie": linie, "nivel": nivel, "runde": buget["runde"],
                     "secunde": buget["secunde"], "rata_vazut": vazut, "rata_nevazut": nevazut,
                     "rata_adversarial": round(adversarial, 3), "rata_sacru": rotunjit(sacru), "povesti_bpo": povesti,
                     "inghet": eticheta,
                     "motiv": f"{motiv}; la ultima rundă: văzut {procent(vazut)}, nevăzut {procent(nevazut)}; "
                              f"adversarial {adversarial:.0%}, sacru {procent(sacru)} (doar pentru raport); povești "
                              f"{povesti} biți pe octet" + (" (PESTE PRAG: regresie)" if peste else "")
                              + f"; înghețat „{eticheta}”. Linia se oprește: nivelul nu se coboară automat, decide omul"})
        return "picat"

    def _trecut(self, stare: dict[str, Any], linie: str, nivel: str, elev: Any, rand: dict[str, Any],
                buget: dict[str, Any]) -> str:
        sl = stare["linii"][linie]
        adversarial, _ = self.masoara(elev, self.seturi(nivel).adversarial, "adversarial", nivel)
        sacru = self.masoara_sacru(elev, nivel)
        povesti = self.ce_stia(elev)
        regresii = {}
        g = self.cfg["regresie"]
        for anterior, info in sl["niveluri_trecute"].items():
            nevazut_anterior = self.seturi(anterior).nevazut
            acum, _ = self.masoara(elev, nevazut_anterior, "nevazut", anterior)
            pierdute = round((info["nevazut"] - acum) * len(nevazut_anterior))  # pe seturi mici, o sarcină = 25 de puncte
            if info["nevazut"] - acum > g["scadere_maxima"] + 1e-9 and pierdute >= g.get("sarcini_minime", 1):
                regresii[anterior] = {"atunci": info["nevazut"], "acum": round(acum, 3)}
        peste = self.povesti_peste_prag(povesti)
        principal = sl["ultimul_inghet"]
        eticheta = self._eticheta_libera(f"{self.prefix}{linie}_{nivel}")
        sl["niveluri_trecute"][nivel] = {"vazut": rand["rata_vazut"], "nevazut": rand["rata_nevazut"],
                                         "adversarial": round(adversarial, 3), "sacru": rotunjit(sacru),
                                         "runda": rand["runda"], "secunde": buget["secunde"], "inghet": eticheta,
                                         "regresii": regresii, "povesti_bpo": povesti, "regresie_povesti": peste}
        if regresii:  # lecția SANDBOX-7: biblioteca liniei se curăță după corectitudine
            self.curata_biblioteca(linie, nivel)
        if regresii or peste:
            sl.update(oprita=True, motiv_oprire=f"regresie după nivelul {nivel}: " + ", ".join(
                [f"{n} {r['atunci']:.0%} → {r['acum']:.0%}" for n, r in regresii.items()]
                + ([f"povești {povesti} biți pe octet, peste pragul de {self.cfg['povesti']['prag_regresie']}"]
                   if peste else [])))
        else:
            sl["ultimul_inghet"] = eticheta
        sl["nivel_curent"], sl["temperatura"] = None, None
        self._ingheata(stare, eticheta, f"linia {linie} a trecut nivelul {nivel} (nevăzut {rand['rata_nevazut']:.0%})"
                       + (", cu regresie" if regresii or peste else ""), [linie])
        motiv = (f"nivelul {nivel} trecut pe linia {linie} în runda {rand['runda']}: nevăzut {rand['rata_nevazut']:.0%}, "
                 f"adversarial {adversarial:.0%}, sacru {procent(sacru)} (adversarialul și sacrul doar pentru raport); "
                 + (f"povești {povesti} biți pe octet; " if povesti is not None else "") + f"înghețat „{eticheta}”")
        if regresii or peste:
            motiv += (f"; REGRESIE ({sl['motiv_oprire']}): modelul nu devine cel principal al liniei (rămâne "
                      f"„{principal}”), linia se oprește și decide omul. Pentru a continua din cel principal: "
                      f"python unelte/ingheata_cod.py --revino {principal} --motiv \"...\"")
        elif len(sl["niveluri_trecute"]) > 1:
            motiv += "; fără regresie pe nivelurile trecute înainte"
        self.jurnal({"tip": "regresie" if regresii or peste else "nivel_trecut", "linie": linie, "nivel": nivel,
                     "runda": rand["runda"], "rata_vazut": rand["rata_vazut"], "rata_nevazut": rand["rata_nevazut"],
                     "rata_adversarial": round(adversarial, 3), "rata_sacru": rotunjit(sacru), "regresii": regresii,
                     "povesti_bpo": povesti, "inghet": eticheta, "motiv": motiv})
        return "regresie" if regresii or peste else "trecut"

    def curata_biblioteca(self, linie: str, la_nivelul: str) -> list[dict[str, Any]]:
        """La o regresie: fiecare soluție din bibliotecile liniei (reușitele ei; la D și cele de la unealtă), mutată pe
        sarcinile nevăzute de aceeași formă ale nivelului ei. Cele care pică ies în respinse/, cu motivul."""
        scoase: list[dict[str, Any]] = []
        nume = ["biblioteca"] + (["biblioteca_unealta"] if linie == "D" else [])
        for n in nume:
            biblioteca = Biblioteca(self.cod, linie, self.schelete_abecedar, n)
            de_scos = []
            for nivel in dict.fromkeys(i["nivel"] for i in biblioteca.intrari):
                ale_nivelului = [i for i in biblioteca.intrari if i["nivel"] == nivel]
                de_scos += curatare.verifica(ale_nivelului, self.seturi(nivel).nevazut, self.ruleaza_cod)
            if de_scos:
                # separat de încercările picate (respinse/<linie>.jsonl), ca statisticile raportului să rămână curate;
                # scrise înainte de scoatere: dacă procesul cade între ele, încărcarea bibliotecii le scoate oricum
                respinse = self.cod / "respinse" / f"curatare_{linie}.jsonl"
                respinse.parent.mkdir(parents=True, exist_ok=True)
                with respinse.open("a", encoding="utf-8") as f:
                    f.writelines(json.dumps({"nivel": i["nivel"], "runda": i["runda"], "test": i["test"], "cod": i["cod"],
                                             "biblioteca": n, "la_regresia_dupa": la_nivelul, "motiv": motiv},
                                            ensure_ascii=False) + "\n" for i, motiv in de_scos)
                biblioteca.scoate([i for i, _ in de_scos])
            scoase += [{"biblioteca": n, "nivel": i["nivel"], "test": i["test"], "cod": i["cod"], "motiv": m}
                       for i, m in de_scos]
        self.jurnal({"tip": "curatare", "linie": linie, "nivel": la_nivelul, "scoase": len(scoase),
                     "exemple": scoase[:5],
                     "motiv": f"regresie după nivelul {la_nivelul}: biblioteca liniei {linie} curățată după corectitudine "
                              f"(fiecare soluție, mutată pe sarcinile nevăzute de aceeași formă ale nivelului ei): "
                              f"{len(scoase)} soluții scoase, în respinse/curatare_{linie}.jsonl"})
        return scoase

    def scrie_raportul(self) -> None:
        """Raportul (unelte/raport_cod.py), în lucru/<dosar>/raport.md: la sfârșitul pilotului sau la oprire (parțial)."""
        try:
            from unelte.raport_cod import raport

            (self.cod / "raport.md").write_text(raport(self.cod), encoding="utf-8")
        except Exception as e:  # noqa: BLE001 - raportul nu oprește școala
            self.jurnal({"tip": "eroare_raport", "motiv": f"raportul n-a putut fi scris: {type(e).__name__}: {e}"})

    def povesti_peste_prag(self, povesti: float | None) -> bool:
        """v0.2: biții pe octet pe povești peste prag (0,46: lecția 6a, în oglindă) = regresie."""
        prag = (self.cfg.get("povesti") or {}).get("prag_regresie")
        return prag is not None and povesti is not None and povesti > prag

    # --- pregătirea și pilotul ---------------------------------------------------------------------------------------

    def pregateste(self) -> dict[str, Any]:
        """Antrenare scurtă pe abecedar, din #252. Toate liniile pornesc din același model pregătit. Cu
        `pierdere_tinta` (v0.2), se oprește când pierderea pe abecedar ajunge la ținta (~0,5, nu pe de rost), măsurată la
        fiecare `verifica_la` pași, sau la `pasi`."""
        p, c = self.cfg["pregatire"], self.cfg
        if (self.cod / "pregatit.pt").exists():
            raise RuntimeError(f"pregătirea e deja făcută (lucru/{self.dosar}/pregatit.pt); liniile pornesc din ea")
        elev = self.fabrica_elev(self._cale(c["scoala"]["model_pornire"]))
        niveluri = c["pilot"]["niveluri"]
        inainte = {n: round(self.masoara(elev, self.seturi(n).nevazut, "nevazut", n)[0], 3) for n in niveluri}
        povesti_inainte = self.ce_stia(elev)
        tinta = p.get("pierdere_tinta")
        pierderi: list[tuple[int, float]] = []
        if tinta is None:  # v0.1: toți pașii odată
            antrenare = self._antreneaza(elev, self.text_abecedar, p["pasi"], p["rata"],
                                         samanta(c["scoala"]["samanta"], "pregatire"))
            pasi_facuti = p["pasi"]
        else:
            pierderi.append((0, round(elev.pierdere_pe(self.text_abecedar), 4)))
            pasi_facuti, antrenare = 0, {}
            while pasi_facuti < p["pasi"] and pierderi[-1][1] > tinta:
                bucata = min(p.get("verifica_la", 10), p["pasi"] - pasi_facuti)
                antrenare = self._antreneaza(elev, self.text_abecedar, bucata, p["rata"],
                                             samanta(c["scoala"]["samanta"], "pregatire", pasi_facuti))
                pasi_facuti += bucata
                pierderi.append((pasi_facuti, round(elev.pierdere_pe(self.text_abecedar), 4)))
        dupa = {n: round(self.masoara(elev, self.seturi(n).nevazut, "nevazut", n)[0], 3) for n in niveluri}
        povesti_dupa = self.ce_stia(elev)
        elev.salveaza(self.cod / "pregatit.pt")
        for linie in c["pilot"]["linii"]:
            self.model_liniei(linie).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.cod / "pregatit.pt", self.model_liniei(linie))
        stare = self.stare()
        stare["pregatire"] = {"pasi": pasi_facuti, "rata": p["rata"], "pierdere": antrenare.get("pierdere_finala"),
                              "secunde": antrenare.get("secunde"), "nevazut_inainte": inainte, "nevazut_dupa": dupa,
                              "povesti_bpo_inainte": povesti_inainte, "povesti_bpo_dupa": povesti_dupa,
                              "pierdere_abecedar": pierderi, "pierdere_tinta": tinta,
                              "fractie_povesti": (c.get("povesti") or {}).get("fractie", 0),
                              "regresie_povesti": self.povesti_peste_prag(povesti_dupa),
                              "timp": datetime.now().isoformat(timespec="seconds")}
        self.salveaza_stare(stare)
        self.jurnal({"tip": "pregatire", **stare["pregatire"], "memorie_video_mb": antrenare.get("memorie_video_mb"),
                     "regula": c["mediu"]["regula"],
                     "motiv": f"pregătirea, din #252: {pasi_facuti} de pași pe abecedar, cu "
                              f"{DESCRIERE_REGULA[c['mediu']['regula']].replace('fără regulă', 'regula lungă')} "
                              f"deasupra exemplelor (rata {p['rata']:g}); "
                              f"nevăzut înainte → după: "
                              + ", ".join(f"{n} {inainte[n]:.0%} → {dupa[n]:.0%}" for n in niveluri)
                              + (f"; pierderea pe abecedar {pierderi[0][1]} → {pierderi[-1][1]} "
                                 + ("(ținta " + str(tinta) + " atinsă)" if pierderi[-1][1] <= tinta
                                    else f"(ținta {tinta} neatinsă în {pasi_facuti} de pași)") if pierderi else "")
                              + (f"; {stare['pregatire']['fractie_povesti']:.0%} povești în fiecare lot"
                                 if stare["pregatire"]["fractie_povesti"] else "")
                              + (f"; povești (biți pe octet) {povesti_inainte} → {povesti_dupa}"
                                 if povesti_inainte is not None else "")
                              + ("; PESTE PRAG: regresie pe povești" if stare["pregatire"]["regresie_povesti"] else "")
                              + f"; liniile {', '.join(c['pilot']['linii'])} pornesc toate din acest model"})
        return stare["pregatire"]

    def pilot(self) -> dict[str, str]:
        """Nivelurile pilotului, liniile pe rând la fiecare nivel. Fiecare linie se oprește la primul ei nivel picat."""
        motiv = paznic_cod.verifica(self.radacina, self.lucru) or paznic_cod.de_ce_nu_e_libera(self.senzori)
        if motiv:
            raise RuntimeError(motiv)
        if self.dupa_ora_de_oprire():  # v0.3: după 18:30 nu pornește nimic, nici pregătirea
            raise RuntimeError(f"e după ora de oprire ({self.cfg['buget']['oprire_la']}): placa e a nopții; pilotul se "
                               f"pornește a doua zi")
        niveluri, linii = self.cfg["pilot"]["niveluri"], self.cfg["pilot"]["linii"]
        self.jurnal({"tip": "pilot_inceput", "niveluri": niveluri, "linii": linii,
                     "versiune": self.cfg["scoala"].get("versiune", "v0.1"), "dosar": self.dosar,
                     "fractie_povesti": (self.cfg.get("povesti") or {}).get("fractie", 0),
                     "motiv": f"pilotul {self.cfg['scoala'].get('versiune', 'v0.1')} pornește (sau se reia), din "
                              f"{self.cfg['scoala']['model_pornire']}: nivelurile {', '.join(niveluri)}, liniile "
                              f"{' și '.join(linii)} pe rând la fiecare nivel, {self.cfg['buget']['minute_pe_nivel']} de "
                              f"minute pe nivel și linie"})
        if not (self.cod / "pregatit.pt").exists():
            self.pregateste()
        if self.stare().get("pregatire", {}).get("regresie_povesti"):
            self.jurnal({"tip": "oprit", "motiv": "oprit: pregătirea a dus poveștile peste prag (regresie); liniile nu "
                                                  "pornesc, decide omul"})
            return {"pregatire": "regresie"}
        eticheta = f"{self.prefix}inainte_de_pilot"
        if not exista(self.lucru, eticheta, self.git_la_inghet, self.radacina, self.dosar):
            self._ingheata(self.stare(), eticheta, "înainte de pilot (obligatoriu), după pregătire", None)
        rezultate: dict[str, str] = {}
        for nivel in niveluri:
            for linie in linii:
                sl = self.stare()["linii"][linie]
                if sl["oprita"] or nivel in sl["niveluri_trecute"]:
                    continue
                rezultate[f"{linie} {nivel}"] = rezultat = self.nivel(linie, nivel)
                if rezultat == "oprit":
                    self.scrie_raportul()
                    return rezultate
        self.scrie_raportul()
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
    if args.nivel and not args.linie:  # o comandă greșită nu e o oprire a școlii: nu intră în jurnal
        print("Oprit: --nivel cere --linie A sau B")
        return 1
    cale_config = Path(args.config) if Path(args.config).is_absolute() else RADACINA / args.config
    cfg = citeste_config(cale_config)
    if args.genereaza_sacru:  # o singură dată pe nivel: nivelurile care există nu se regenerează niciodată
        cale = RADACINA / cfg["scoala"]["sacru"]
        e = cfg["examen"]
        texte = {ep.test for ep in citeste_abecedar(RADACINA / cfg["scoala"]["abecedar"]).episoade}
        marimi = {n: m["sacru"] for n, m in e.get("marimi", {}).items() if "sacru" in m}
        niveluri = tuple(cfg["pilot"]["niveluri"])
        if cale.exists():
            date = json.loads(cale.read_text(encoding="utf-8"))
            adaugate = adauga_sacru(date, texte, niveluri, e["sacru"], e.get("samanta_sacru", "sacru-v0.1"), marimi)
            if not adaugate:
                print(f"Setul sacru există deja pentru toate nivelurile ({cale}): nu se regenerează.")
                return 1
        else:
            date = genereaza_sacru(texte, e["sacru"], e.get("samanta_sacru", "sacru-v0.1"), niveluri, marimi)
            adaugate = list(niveluri)
        cale.write_text(json.dumps(date, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Setul sacru: nivelurile {', '.join(adaugate)} ("
              + ", ".join(f"{n}: {len(date['niveluri'][n])}" for n in adaugate) + f" sarcini) în {cale}. Urmează: "
              f"git add -f {cfg['scoala']['sacru']} și python unelte/scoala_cod.py --aproba-amprente")
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
        if args.pilot or args.nivel or args.pregateste:
            scoala.jurnal({"tip": "oprit", "motiv": f"oprit: {eroare}"})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
