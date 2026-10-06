"""Bucla CONTINUUM: leagă cele 8 etape, cu același buton STOP ca Kronos și cu modul --simuleaza.

    python -m module.continuum.bucla --config config/continuum.toml --simuleaza   # doar spune ce ar alege
    python -m module.continuum.bucla --config config/continuum.toml               # pornește și experimentele
    python -m module.continuum.bucla --config config/continuum.toml --jurnal      # ultimele cicluri, pe scurt

Oprirea: același buton ca la Kronos, fișierul lucru/STOP:
    python -m kronos opreste --config config/proba.toml     (orice configurare cu director_lucru = "lucru")
    python -m kronos porneste --config config/proba.toml    (ca să poată porni din nou)

Un ciclu: OBSERVĂ → EVALUEAZĂ → NEVOI → ALEGE → ACȚIONEAZĂ → MĂSOARĂ → ÎNVAȚĂ → STARE.
- Dacă o etapă cade, ciclul se încheie curat, eroarea intră în jurnal și urmează ciclul următor. Bucla nu cade din
  cauza unei etape.
- STOP-ul se verifică la începutul fiecărui ciclu, înainte de acțiune și în pauza dintre cicluri, la câteva secunde.
- O acțiune pornită (de ex. o antrenare Kronos) vede singură STOP-ul și se oprește după experimentul în curs.
- Configurarea se recitește și modulele se redescoperă la pornire și la fiecare „redescopera_la_cicluri” cicluri.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Callable

from kronos.paznic import Paznic
from module.continuum import REPAUS, EroareContinuum, citeste_config
from module.continuum import stare as memorie_continuum
from module.continuum.actioneaza import actioneaza, text_comanda
from module.continuum.alege import alege
from module.continuum.evalueaza import evalueaza
from module.continuum.invata import invata
from module.continuum.masoara import masoara
from module.continuum.nevoi import nevoi
from module.continuum.observa import Senzori, descopera_module, observa

MESAJ_STOP = ("Oprit: butonul STOP (lucru/STOP) e apăsat. Ca să pornească din nou: "
              "python -m kronos porneste --config config/proba.toml, apoi pornește din nou CONTINUUM.")


def pe_scurt(rand: dict[str, Any]) -> str:
    """Ciclul într-o propoziție sau două, în română: ce a văzut, ce a ales și de ce."""
    if rand.get("oprit"):
        return MESAJ_STOP
    if rand.get("eroare"):
        return (f"Ciclul s-a încheiat la etapa {rand['eroare']['etapa']}: {rand['eroare']['mesaj']}. "
                f"Urmează ciclul următor.")
    text = f"{rand['nivel']}: {rand['de_ce_nivelul']}."
    if rand.get("nevoie"):
        text += f" Aleg {rand['nevoie']}: {rand['motiv']}."
        if rand.get("simulat"):
            return text + f" [simulat] Aș porni: {rand['actiune']}."
        return text + f" Am pornit: {rand['actiune']}. Verdict: {rand.get('verdict')} ({rand.get('motiv_verdict')})."
    if rand["nivel"] == REPAUS and rand.get("nevoi"):
        return text + " Nevoi în așteptare: " + ", ".join(n["nevoie"] for n in rand["nevoi"]) + "."
    if rand.get("sarite"):
        return text + " Nu pornesc nimic: " + "; ".join(f"{s['nevoie']} — {s['de_ce_nu']}" for s in rand["sarite"]) + "."
    return text + " Nicio nevoie acum."


class Bucla:
    def __init__(self, cale_config: str | Path, simuleaza: bool = False, senzori: Senzori | None = None,
                 dormi: Callable[[float], None] | None = None, iesire: Callable[[str], None] = print) -> None:
        self.cale_config = cale_config
        self.config = citeste_config(cale_config)
        self.simuleaza = simuleaza
        self.senzori = senzori or Senzori()
        self.director = self.config["continuum"]["director_lucru"] / "continuum"
        self.paznic = Paznic({}, self.config["continuum"]["director_lucru"])  # același STOP ca Kronos
        self.memorie = memorie_continuum.incarca(self.director)
        self.module: dict[str, Any] = {}
        self.problema_config: str | None = None
        self.cicluri_facute = 0
        self.dormi = dormi or self.asteapta
        self.iesire = iesire

    def asteapta(self, secunde: float) -> None:
        """Pauza dintre cicluri; se termină mai devreme dacă cineva apasă STOP."""
        sfarsit = time.monotonic() + secunde
        while not self.paznic.oprire_ceruta() and (ramas := sfarsit - time.monotonic()) > 0:
            time.sleep(min(5.0, ramas))

    def redescopera(self) -> None:
        """Recitește configurarea (dacă e stricată, merge cu cea de dinainte) și redescoperă modulele."""
        try:
            self.config = citeste_config(self.cale_config)
            self.problema_config = None
        except EroareContinuum as e:
            self.problema_config = f"{e}; merg mai departe cu configurarea de dinainte"
        self.module = descopera_module(self.config)

    def ciclu(self) -> dict[str, Any]:
        numar = self.memorie["ciclu"] + 1
        rand: dict[str, Any] = {"ciclu": numar, "timp": self.senzori.acum().isoformat(timespec="seconds"),
                                "simulat": self.simuleaza}
        probleme = {"configurare": self.problema_config} if self.problema_config else {}
        etapa = "observa"
        try:
            if self.paznic.oprire_ceruta():
                rand["oprit"] = True
            else:
                observat = observa(self.config, self.module, self.senzori)
                rand["timp"] = observat.timp.isoformat(timespec="seconds")
                rand["observat"] = observat.rezumat()
                probleme.update({f"modul:{nume}": f"modulul {nume} e {info.get('stare')}" + (
                    f": {info['eroare']}" if info.get("eroare") else "")
                    for nume, info in observat.module.items() if info.get("stare") != "ok"})
                etapa = "evalueaza"
                inainte = evalueaza(observat, self.config)
                rand.update(nivel=inainte.nivel, de_ce_nivelul=inainte.motiv_nivel, organism=inainte.rezumat())
                etapa = "nevoi"
                lista = nevoi(inainte, self.config)
                rand["nevoi"] = [{"nevoie": n.cheie, "motiv": n.motiv} for n in lista]
                etapa = "alege"
                alegere = alege(lista, inainte, self.config)
                rand["sarite"] = alegere.sarite
                if alegere.plan:
                    rand.update(nevoie=alegere.nevoie.cheie, motiv=alegere.nevoie.motiv, actiune=alegere.plan.descriere,
                                comenzi=[text_comanda(c) for c in alegere.plan.comenzi])
                if alegere.plan and self.paznic.oprire_ceruta():
                    rand["oprit"] = True
                else:
                    etapa = "actioneaza"
                    rezultat = actioneaza(alegere.plan, self.simuleaza, self.director, numar) if alegere.plan else None
                    if rezultat and not rezultat["simulat"]:
                        rand["rezultat"] = rezultat
                    etapa = "masoara"
                    dupa = None
                    if rezultat and not rezultat["simulat"]:
                        dupa = evalueaza(observa(self.config, self.module, self.senzori), self.config)
                    masurare = masoara(alegere, inainte, dupa, rezultat)
                    if alegere.plan and not self.simuleaza:
                        rand.update({k: v for k, v in masurare.items() if k != "motiv"}, motiv_verdict=masurare["motiv"])
                    etapa = "invata"
                    self.memorie = invata(self.memorie, alegere, masurare, self.config, numar, rand["timp"])
                    etapa = "stare"
                    memorie_continuum.actualizeaza_capacitati(self.memorie, dupa or inainte, rand["timp"])
        except Exception as e:  # noqa: BLE001 - o etapă care cade încheie ciclul, nu bucla
            rand["eroare"] = {"etapa": etapa, "mesaj": f"{type(e).__name__}: {e}"}
            probleme[f"etapa:{etapa}"] = rand["eroare"]["mesaj"]
        rand["pe_scurt"] = pe_scurt(rand)
        try:
            self.memorie["ciclu"], self.memorie["actualizat"] = numar, rand["timp"]
            memorie_continuum.actualizeaza_probleme(self.memorie, probleme, rand["timp"])
            memorie_continuum.salveaza(self.director, self.memorie)
            memorie_continuum.scrie_ciclu(self.director, rand, self.config["continuum"]["jurnal_max_mb"])
        except Exception as e:  # noqa: BLE001 - ex. discul plin: bucla merge mai departe
            print(f"Nu pot scrie starea lui CONTINUUM: {type(e).__name__}: {e}", file=sys.stderr)
        return rand

    def ruleaza(self, cicluri: int | None = None) -> int:
        """Ciclu după ciclu, până la STOP (sau până la numărul dat de cicluri)."""
        while cicluri is None or self.cicluri_facute < cicluri:
            if self.cicluri_facute % self.config["continuum"]["redescopera_la_cicluri"] == 0:
                self.redescopera()
            rand = self.ciclu()
            self.cicluri_facute += 1
            self.iesire(f"[{rand['timp'][11:16]}] #{rand['ciclu']} {rand['pe_scurt']}")
            if rand.get("oprit") or (cicluri is not None and self.cicluri_facute >= cicluri):
                break
            self.dormi(60 * self.config["guvernator"]["pauza_minute"][rand.get("nivel") or REPAUS])
        return 0


def main(argv: list[str] | None = None) -> int:
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8")  # diacriticele și pe Windows
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(prog="python -m module.continuum.bucla",
                                     description="CONTINUUM v0: decide ce face Kronos când nimeni nu-i spune.")
    parser.add_argument("--config", default="config/continuum.toml")
    parser.add_argument("--simuleaza", action="store_true", help="nu pornește nimic: doar scrie ce ar alege și de ce")
    parser.add_argument("--cicluri", type=int, default=None, help="câte cicluri (implicit: până la STOP)")
    parser.add_argument("--jurnal", type=int, nargs="?", const=20, default=None, metavar="N",
                        help="nu rula: arată ultimele N cicluri (implicit 20), pe scurt")
    args = parser.parse_args(argv)
    try:
        config = citeste_config(args.config)
    except EroareContinuum as e:
        print(f"Eroare: {e}", file=sys.stderr)
        return 1
    director = config["continuum"]["director_lucru"] / "continuum"
    if args.jurnal is not None:
        randuri = memorie_continuum.citeste_cicluri(director, args.jurnal)
        if not randuri:
            print(f"Încă niciun ciclu în {(director / 'cicluri.jsonl').as_posix()}.")
        for rand in randuri:
            print(f"#{rand.get('ciclu')}  {str(rand.get('timp', ''))[:16].replace('T', ' ')}  {rand.get('pe_scurt', '')}")
        return 0
    bucla = Bucla(args.config, simuleaza=args.simuleaza)
    if bucla.paznic.oprire_ceruta():
        print(MESAJ_STOP)
        return 1
    print(f"CONTINUUM v0{' în modul simulat: nu pornește nimic, doar spune ce ar alege' if args.simuleaza else ''}. "
          f"Ciclurile se scriu în {(director / 'cicluri.jsonl').as_posix()}.\n"
          f"Oprire: python -m kronos opreste --config config/proba.toml (același STOP ca Kronos).", flush=True)
    try:
        return bucla.ruleaza(args.cicluri)
    except KeyboardInterrupt:
        print("\nOprit cu Ctrl+C.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
