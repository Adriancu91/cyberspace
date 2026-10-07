"""Bucla CONTINUUM: leagă cele 8 etape, cu același buton STOP ca Kronos și cu modul --simuleaza.

    python -m module.continuum.bucla --config config/continuum.toml --simuleaza   # doar spune ce ar alege
    python -m module.continuum.bucla --config config/continuum.toml --simuleaza --pauza-minute 15   # o zi, la 15 min
    python -m module.continuum.bucla --config config/continuum.toml               # pornește și experimentele
    python -m module.continuum.bucla --config config/continuum.toml --jurnal      # ultimele cicluri, pe scurt
    python -m module.continuum.bucla --config config/continuum.toml --simuleaza --ca-la 23:00   # ce ar alege la noapte

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
from datetime import date, datetime
from datetime import time as Ora
from pathlib import Path
from typing import Any, Callable

import module.continuum.observa as senzori_reali
from kronos.paznic import Paznic
from module.continuum import NECONCLUDENT, REPAUS, SUCCES, EroareContinuum, citeste_config, ro_scurt, stabilitate
from module.continuum import stare as memorie_continuum
from module.continuum.actioneaza import actioneaza, text_comanda
from module.continuum.alege import alege
from module.continuum.evalueaza import evalueaza
from module.continuum.invata import dupa_confirmare, invata
from module.continuum.masoara import masoara
from module.continuum.nevoi import nevoi
from module.continuum.observa import Senzori, descopera_module, observa

MESAJ_STOP = ("Oprit: butonul STOP (lucru/STOP) e apăsat. Ca să pornească din nou: "
              "python -m kronos porneste --config config/proba.toml, apoi pornește din nou CONTINUUM.")


def pe_scurt(rand: dict[str, Any]) -> str:
    """Ciclul într-o propoziție sau două, în română: ce a văzut, ce a ales și de ce."""
    if rand.get("ca_la"):
        return f"[ca la {rand['ca_la']}, fără om] " + pe_scurt({k: v for k, v in rand.items() if k != "ca_la"})
    if rand.get("oprit"):
        return MESAJ_STOP
    if rand.get("eroare"):
        return (f"Ciclul s-a încheiat la etapa {rand['eroare']['etapa']}: {rand['eroare']['mesaj']}. "
                f"Urmează ciclul următor.")
    text = f"{rand['nivel']}: {rand['de_ce_nivelul']}."
    for schimbare in rand.get("candidati", []):
        text += f" Candidat: {schimbare}."
    if rand.get("nevoie"):
        text += f" Aleg {rand['nevoie']}: {rand['motiv']}."
        if rand.get("simulat"):
            return text + f" [simulat] Aș {'scrie' if rand.get('fel') == 'raport' else 'porni'}: {rand['actiune']}."
        if rand.get("fel") == "raport":
            return text + f" Am scris: {rand['actiune']} ({(rand.get('rezultat') or {}).get('raport')})."
        return text + f" Am pornit: {rand['actiune']}. Verdict: {rand.get('verdict')} ({rand.get('motiv_verdict')})."
    if rand["nivel"] == REPAUS and rand.get("nevoi"):
        return text + " Nevoi în așteptare: " + ", ".join(n["nevoie"] for n in rand["nevoi"]) + "."
    if rand.get("sarite"):
        return text + " Nu pornesc nimic: " + "; ".join(f"{s['nevoie']} — {s['de_ce_nu']}" for s in rand["sarite"]) + "."
    return text + " Nicio nevoie acum."


class Bucla:
    def __init__(self, cale_config: str | Path, simuleaza: bool = False, senzori: Senzori | None = None,
                 dormi: Callable[[float], None] | None = None, iesire: Callable[[str], None] = print,
                 pauza_minute: float | None = None, ca_la: str | None = None, director_stare: str | Path | None = None) -> None:
        self.cale_config = cale_config
        self.config = citeste_config(cale_config)
        self.simuleaza = simuleaza
        self.senzori = senzori or Senzori()
        self.director = Path(director_stare) if director_stare else self.config["continuum"]["director_lucru"] / "continuum"
        self.paznic = Paznic({}, self.config["continuum"]["director_lucru"])  # același STOP ca Kronos
        self.memorie = memorie_continuum.incarca(self.director)
        self.module: dict[str, Any] = {}
        self.problema_config: str | None = None
        self.cicluri_facute = 0
        self.dormi = dormi or self.asteapta
        self.iesire = iesire
        self.pauza_minute = pauza_minute  # dacă e dată: aceeași pauză după orice nivel (ex. o zi simulată, la 15 minute)
        self.ca_la = ca_la  # doar simulat: ciclurile se fac „ca la” ora asta, fără om la laptop (se scrie în jurnal)

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
        if self.ca_la:
            rand["ca_la"] = self.ca_la
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
                inainte = evalueaza(observat, self.config, self.memorie)
                stabilitate.initializeaza(self.memorie, inainte, rand["timp"])  # linia de bază: de dinaintea acțiunii
                rand.update(nivel=inainte.nivel, de_ce_nivelul=inainte.motiv_nivel, organism=inainte.rezumat())
                etapa = "nevoi"
                lista = nevoi(inainte, self.config, self.memorie)
                rand["nevoi"] = [{"nevoie": n.cheie, "motiv": n.motiv} for n in lista]
                etapa = "alege"
                alegere = alege(lista, inainte, self.config, self.memorie, numar)
                rand["sarite"] = alegere.sarite
                if alegere.plan:
                    rand.update(nevoie=alegere.nevoie.cheie, motiv=alegere.nevoie.motiv, actiune=alegere.plan.descriere,
                                comenzi=[text_comanda(c) for c in alegere.plan.comenzi], fel=alegere.plan.fel)
                if alegere.plan and self.paznic.oprire_ceruta():
                    rand["oprit"] = True
                else:
                    etapa = "actioneaza"
                    rezultat = actioneaza(alegere.plan, self.simuleaza, self.director, numar) if alegere.plan else None
                    pe_bune = bool(rezultat) and not rezultat["simulat"]
                    if pe_bune:
                        rand["rezultat"] = rezultat
                        if alegere.nevoie.tip != "repara":  # anti-buclă: răcirea (fără „repara”)
                            self.memorie["racire"][alegere.nevoie.cheie] = numar + self.config["anti_bucla"]["racire_cicluri"]
                        if alegere.plan.fel == "raport":
                            self.memorie["rapoarte"].append({"cheie": alegere.plan.detalii["cheie"], "tip": "repara",
                                                             "capacitate": alegere.nevoie.capacitate, "deschis": True,
                                                             "ciclu": numar, "timp": rand["timp"], "fisier": rezultat["raport"]})
                    etapa = "masoara"
                    dupa, fise = None, observat.fise
                    if pe_bune and alegere.plan.fel != "raport":
                        observat_dupa = observa(self.config, self.module, self.senzori)
                        fise = observat_dupa.fise
                        dupa = evalueaza(observat_dupa, self.config, self.memorie)
                    masurare = masoara(alegere, inainte, dupa, rezultat, fise, self.memorie, self.config)
                    candidati_noi: list[str] = []
                    if masurare.get("candidat") and dupa is not None:
                        candidati_noi = self._confirma_imediat(masurare, alegere, inainte, dupa, fise, rand["timp"])
                    if alegere.plan and not self.simuleaza:
                        rand.update({k: v for k, v in masurare.items() if k != "motiv"}, motiv_verdict=masurare["motiv"])
                    etapa = "invata"
                    self.memorie = invata(self.memorie, alegere, masurare, self.config, numar, rand["timp"])
                    etapa = "stare"
                    rand["candidati"] = candidati_noi + self._stabilitate(dupa or inainte, fise, rand["timp"])
                    self._rapoarte_strategii(numar, rand)
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

    def _confirma_imediat(self, masurare: dict[str, Any], alegere: Any, inainte: Any, dupa: Any,
                          fise: list[dict[str, Any]], timp: str) -> list[str]:
        """Scorul nou al unei antrenări e un candidat (față de linia de bază, sau doar față de modelul de pornire). Dacă
        o a doua măsurătoare îl confirmă deja (ex. două ore păstrate), ÎNVAȚĂ mută încrederea acum; altfel, strategia
        așteaptă confirmarea. Un SUCCES SCUMP nu așteaptă nimic: încrederea lui nu urcă oricum."""
        tinta, experiment = masurare["candidat"]["capacitate"], masurare["candidat"]["experiment"]
        noi = stabilitate.adauga_candidati(self.memorie, dupa, timp, fise, self.config, de_la_id=inainte.ultimul_id)
        intrare = stabilitate.cauta(self.memorie, tinta, experiment, muta_baza=True)
        if intrare is None and masurare["verdict"] == SUCCES:
            intrare = stabilitate.adauga_succes(self.memorie, dupa, tinta, inainte.capacitati[tinta].curent,
                                                masurare.get("model_inainte"), timp)
            noi.append(intrare)
        stabilitate.actualizeaza(self.memorie, fise, self.config, timp)
        if intrare is None:
            return [k["motiv"] for k in noi]
        # Una dintre orele noi confirmată (ex. ora 7, de ora 8) ajunge: acțiunea a ajutat cu adevărat.
        confirmate = [k["experiment"] for k in noi if k["capacitate"] == tinta and k["stare"] == stabilitate.CONFIRMAT]
        confirmata = confirmate or None
        masurare["candidat"]["stare"] = stabilitate.CONFIRMAT if confirmata else intrare["stare"]
        if confirmata is None and intrare["stare"] == stabilitate.NECONFIRMAT:
            masurare.update(verdict=NECONCLUDENT, motiv=f"{masurare['motiv']}; {intrare['motiv']}")
        elif masurare["verdict"] == SUCCES:
            masurare["confirmat"] = confirmata is not None or intrare["stare"] == stabilitate.CONFIRMAT
            if confirmata is not None:
                baza = self.memorie["capacitati"][tinta]
                ore = (f"ora #{confirmate[0]} e confirmată" if len(confirmate) == 1 else
                       f"orele {', '.join(f'#{e}' for e in confirmate)} sunt confirmate" if len(confirmate) <= 3 else
                       f"orele #{confirmate[0]} … #{confirmate[-1]} ({len(confirmate)}) sunt confirmate")
                masurare["motiv"] += (f"; {ore} de orele păstrate de după: linia de bază e acum "
                                      f"{ro_scurt(baza['linie_de_baza'])} (#{baza['experiment_baza']})")
            elif intrare["stare"] == stabilitate.CANDIDAT:
                intrare.update(strategie=alegere.plan.strategie, castig_pe_ora=masurare.get("castig_pe_ora"))
                masurare["motiv"] += "; e un candidat: încrederea urcă după a doua măsurătoare"
        return [k["motiv"] for k in noi]

    def _stabilitate(self, stare: Any, fise: list[dict[str, Any]], timp: str) -> list[str]:
        """Linia de bază: inițializată o dată din jurnal, apoi mutată doar prin candidați confirmați."""
        stabilitate.initializeaza(self.memorie, stare, timp)
        noi = stabilitate.adauga_candidati(self.memorie, stare, timp)
        schimbate = stabilitate.actualizeaza(self.memorie, fise, self.config, timp,
                                             aplica=dupa_confirmare(self.memorie, self.config))
        return [k["motiv"] for k in noi + schimbate]

    def _rapoarte_strategii(self, numar: int, rand: dict[str, Any]) -> None:
        """Strategiile blocate (prea multe eșecuri la rând): raport către om, o singură dată."""
        while self.memorie["de_raportat"]:
            de_raportat = self.memorie["de_raportat"].pop(0)
            fisier = self.director / "rapoarte" / f"ciclu_{numar:05d}_blocata_{de_raportat['strategie'].replace(':', '_')}.md"
            fisier.parent.mkdir(parents=True, exist_ok=True)
            fisier.write_text(
                f"# CONTINUUM: strategia {de_raportat['strategie']} e blocată\n\n"
                f"- A eșuat de {de_raportat['esecuri_la_rand']} ori la rând (limita: "
                f"{self.config['anti_bucla']['max_esecuri']}).\n- Ultimul motiv: {de_raportat['ultimul_motiv']}\n\n"
                f"CONTINUUM n-o mai alege până nu decide omul (de ex. o configurare nouă sau ștergerea blocării din "
                f"stare.json).\n", encoding="utf-8")
            self.memorie["rapoarte"].append({"cheie": f"blocata:{de_raportat['strategie']}", "tip": "strategie_blocata",
                                             "ciclu": numar, "timp": de_raportat["timp"], "fisier": fisier.as_posix()})
            rand.setdefault("rapoarte", []).append(fisier.as_posix())

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
            pauza = self.pauza_minute
            if pauza is None:
                pauza = self.config["guvernator"]["pauza_minute"][rand.get("nivel") or REPAUS]
            self.dormi(60 * pauza)
        return 0


def main(argv: list[str] | None = None) -> int:
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8")  # diacriticele și pe Windows
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(prog="python -m module.continuum.bucla",
                                     description="CONTINUUM v1: decide ce face Kronos când nimeni nu-i spune.")
    parser.add_argument("--config", default="config/continuum.toml")
    parser.add_argument("--simuleaza", action="store_true", help="nu pornește nimic: doar scrie ce ar alege și de ce")
    parser.add_argument("--cicluri", type=int, default=None, help="câte cicluri (implicit: până la STOP)")
    parser.add_argument("--pauza-minute", type=float, default=None,
                        help="aceeași pauză între cicluri, pe orice nivel (implicit: cea din configurare, pe nivel)")
    parser.add_argument("--ca-la", default=None, metavar="HH:MM",
                        help="doar cu --simuleaza: un ciclu ca și cum ar fi ora asta și omul ar fi plecat de la laptop "
                             "(ex. ce ar alege la noapte); placa rămâne cea adevărată")
    parser.add_argument("--placa-libera", action="store_true",
                        help="doar cu --simuleaza: ca și cum placa ar fi liberă (ex. ce ar alege după antrenarea de acum)")
    parser.add_argument("--stare", default=None, metavar="DOSAR",
                        help="alt dosar pentru stare.json și cicluri.jsonl (implicit: lucru/continuum)")
    parser.add_argument("--jurnal", type=int, nargs="?", const=20, default=None, metavar="N",
                        help="nu rula: arată ultimele N cicluri (implicit 20), pe scurt")
    args = parser.parse_args(argv)
    try:
        config = citeste_config(args.config)
    except EroareContinuum as e:
        print(f"Eroare: {e}", file=sys.stderr)
        return 1
    director = Path(args.stare) if args.stare else config["continuum"]["director_lucru"] / "continuum"
    if args.jurnal is not None:
        randuri = memorie_continuum.citeste_cicluri(director, args.jurnal)
        if not randuri:
            print(f"Încă niciun ciclu în {(director / 'cicluri.jsonl').as_posix()}.")
        for rand in randuri:
            print(f"#{rand.get('ciclu')}  {str(rand.get('timp', ''))[:16].replace('T', ' ')}  {rand.get('pe_scurt', '')}")
        return 0
    if args.pauza_minute is not None and args.pauza_minute < 0:
        print("Eroare: --pauza-minute nu poate fi negativ.", file=sys.stderr)
        return 1
    senzori, cicluri = None, args.cicluri
    if args.placa_libera and not args.simuleaza:
        print("Eroare: --placa-libera merge doar cu --simuleaza.", file=sys.stderr)
        return 1
    if args.ca_la:
        try:
            ora = Ora.fromisoformat(args.ca_la)
        except ValueError:
            print("Eroare: --ca-la e de forma 23:00.", file=sys.stderr)
            return 1
        if not args.simuleaza:
            print("Eroare: --ca-la merge doar cu --simuleaza (nu pornește nimic „ca la” altă oră).", file=sys.stderr)
            return 1
        senzori = Senzori(acum=lambda: datetime.combine(date.today(), ora), placa=senzori_reali.citeste_placa,
                          om=lambda: {"stare": "ok", "minute_de_la_ultima_atingere": 60.0, "presupus": True})
        cicluri = 1 if cicluri is None else cicluri
    if args.placa_libera:
        placa_reala = (senzori.placa if senzori else senzori_reali.citeste_placa)

        def placa_libera() -> dict[str, Any]:
            placa = dict(placa_reala())
            if placa.get("stare") == "ok":
                placa.update(procese=[], memorie_libera_mb=placa["memorie_totala_mb"], presupus_liber=True)
            return placa

        senzori = Senzori(acum=senzori.acum if senzori else datetime.now, placa=placa_libera,
                          om=senzori.om if senzori else senzori_reali.citeste_omul)
        cicluri = 1 if cicluri is None else cicluri
    bucla = Bucla(args.config, simuleaza=args.simuleaza, pauza_minute=args.pauza_minute, senzori=senzori,
                  ca_la=f"{ora:%H:%M}" if args.ca_la else None, director_stare=args.stare)
    if bucla.paznic.oprire_ceruta():
        print(MESAJ_STOP)
        return 1
    print(f"CONTINUUM v1{' în modul simulat: nu pornește nimic, doar spune ce ar alege' if args.simuleaza else ''}. "
          f"Ciclurile se scriu în {(director / 'cicluri.jsonl').as_posix()}.\n"
          f"Oprire: python -m kronos opreste --config config/proba.toml (același STOP ca Kronos).", flush=True)
    try:
        return bucla.ruleaza(cicluri)
    except KeyboardInterrupt:
        print("\nOprit cu Ctrl+C.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
