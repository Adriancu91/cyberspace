"""Orchestratorul: conduce fiecare experiment prin aceleași opt stări.

propus → verificat → aplicat → testat_rapid → antrenat → examinat → decis → inregistrat

Orice eșec duce direct la „anulat”, iar fișa ajunge oricum în jurnal.

Regula 4 (nou ≠ mai bun), doar cu [criterii] în configurare: pe lângă scorul principal al examenului, modelul dă prin
dupa_examen „criterii” suplimentare (numere cu nume, ex. fapte_corecte, nota_profesor), înainte de decizie. Un experiment
e păstrat doar dacă scorul principal e mai bun ȘI niciun criteriu nu a scăzut mai mult decât pragul lui față de cel mai
bun experiment păstrat; altfel e „respins”, cu motivul „a pierdut <criteriu>”. Fără [criterii], totul e ca înainte.

Criteriul principal (principal = true la un criteriu, cel mult unul): atunci el hotărăște. Păstrat = principalul e mai
bun cu peste pragul lui ȘI niciun alt criteriu, inclusiv scorul examenului (pragul lui e prag_zgomot), nu scade peste
pragul lui. Referința e cel mai bun experiment păstrat după criteriul principal. Fără „principal”, totul e ca înainte.

Pornirea dintr-un model păstrat (config.porneste_din, ex. --porneste-din la antrenarea lungă): până la primul experiment
păstrat al liniei, referința regulii 4 (scorul examenului și criteriile) e fișa acelui model. Fără ea, primul experiment
al liniei e păstrat din oficiu, ca înainte. Rețeta liniei rămâne cea din configurare.
"""

from __future__ import annotations

import copy
import math
import time
from datetime import datetime, timezone
from typing import Any, Callable

from .config import Config, EroareConfig
from .contracte import PORTURI, Propunere
from .jurnal import Jurnal
from .paznic import Paznic
from .registru import EroareModul, Registru

CARACTERE_TEST_RAPID = 500


class Orchestrator:
    def __init__(
        self,
        config: Config,
        registru: Registru | None = None,
        asteapta: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self.registru = registru or Registru()
        self.asteapta = asteapta
        self.jurnal = Jurnal(config.director_lucru)
        self.paznic = Paznic(config.paznic, config.director_lucru)

        for port in PORTURI:
            self.registru.pune(port, config.porturi[port]["modul"], config.setari_port(port))

        self.date = self.registru.ia("date")
        self.examen = self.registru.ia("examen")
        self.cercetator = self.registru.ia("cercetator")
        self.rulare = self.registru.ia("rulare")
        self.stocare = self.registru.ia("stocare")
        self.interfata = self.registru.ia("interfata")
        self.memorie = self.registru.ia("memorie")

        # Pornim de la cea mai bună rețetă păstrată (reluare de unde am rămas).
        self.setari_curente: dict[str, dict[str, Any]] = {
            p: config.setari_port(p) for p in self.paznic.porturi_modificabile
        }
        self.cel_mai_bun = self.jurnal.cel_mai_bun(
            config.nume, self.examen.scor_principal, self.examen.mai_mic_e_mai_bun
        )
        principal = config.criteriu_principal()
        if principal is not None:  # cu un criteriu principal, referința e cel mai bun experiment păstrat după el
            self.cel_mai_bun = self._cel_mai_bun_dupa(principal) or self.cel_mai_bun
        if self.cel_mai_bun is not None:
            self.setari_curente = copy.deepcopy(self.cel_mai_bun["setari"])
        # O linie care pornește dintr-un model păstrat: până la primul ei experiment păstrat, el e referința.
        self.pornire: dict[str, Any] | None = None
        if self.cel_mai_bun is None and config.porneste_din is not None:
            self.pornire = self._fisa_de_pornire(config.porneste_din)
            self.cel_mai_bun = self.pornire

    # ------------------------------------------------------------------

    def ruleaza(self, numar_experimente: int | None = None) -> list[dict[str, Any]]:
        numar = self.config.experimente if numar_experimente is None else numar_experimente
        self.interfata.anunta(
            "start",
            {
                "configurare": self.config.nume,
                "experimente": numar,
                "module": self.registru.descriere(),
                "cel_mai_bun_scor": self._scor(self.cel_mai_bun),
            },
        )
        fise: list[dict[str, Any]] = []
        if self._opreste():
            numar = 0
        elif self.cel_mai_bun is None or self.cel_mai_bun is self.pornire:
            fise.append(self.experiment(Propunere("punct de plecare (setările din configurare)")))

        for i in range(numar):
            # înainte de primul experiment am verificat deja mai sus
            if (i > 0 or fise) and self._opreste():
                break
            propunere = self.cercetator.propune(
                self.jurnal.istoric(self.config.nume), copy.deepcopy(self.setari_curente)
            )
            if not propunere.modificari:
                self.interfata.anunta("gata", {"motiv": propunere.descriere})
                break
            fise.append(self.experiment(propunere))

        self.interfata.anunta(
            "final",
            {
                "experimente_rulate": len(fise),
                "pastrate": sum(1 for f in fise if f["decizie"] == "pastrat"),
                "cel_mai_bun_scor": self._scor(self.cel_mai_bun),
                "setari_castigatoare": self.setari_curente,
            },
        )
        return fise

    def _opreste(self) -> bool:
        if self.paznic.oprire_ceruta():
            self.interfata.anunta("oprit", {"motiv": f"există fișierul {self.paznic.fisier_stop}"})
            return True
        for _ in range(self.paznic.incercari_racire):
            motiv = self.paznic.prea_cald()
            if motiv is None:
                return False
            self.interfata.anunta("racire", {"motiv": motiv, "pauza_secunde": self.paznic.pauza_racire_secunde})
            self.asteapta(self.paznic.pauza_racire_secunde)
        motiv = self.paznic.prea_cald()
        if motiv is not None:
            self.interfata.anunta("oprit", {"motiv": motiv + " (nu s-a răcit)"})
            return True
        return False

    def _fisa_de_pornire(self, id_experiment: int) -> dict[str, Any]:
        """Fișa modelului păstrat din care pornește linia (config.porneste_din)."""
        fisa = next((f for f in self.jurnal.istoric() if f.get("id") == id_experiment), None)
        if fisa is None or fisa.get("decizie") != "pastrat" or not isinstance(self._scor(fisa), (int, float)):
            raise EroareConfig(f"porneste_din = {id_experiment}: în jurnal nu e un experiment păstrat cu scorul "
                               f"„{self.examen.scor_principal}”")
        return fisa

    def _scor(self, fisa: dict[str, Any] | None) -> float | None:
        if fisa is None:
            return None
        return fisa.get("scoruri", {}).get(self.examen.scor_principal)

    # ------------------------------------------------------------------

    def experiment(self, propunere: Propunere) -> dict[str, Any]:
        fisa: dict[str, Any] = {
            "id": self.jurnal.urmatorul_id(),
            "linie": self.config.nume,
            "inceput": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "propunere": {"descriere": propunere.descriere, "modificari": propunere.modificari},
            "module": self.registru.descriere(),
            "stari": [],
            "decizie": None,
        }
        start = time.perf_counter()

        def stare(nume: str) -> None:
            fisa["stari"].append(nume)
            self.interfata.anunta("stare", {"id": fisa["id"], "stare": nume})

        def anuleaza(motiv: str) -> dict[str, Any]:
            fisa["decizie"] = "anulat"
            fisa["motiv"] = motiv
            stare("anulat")
            return self._inregistreaza(fisa, start, stare)

        stare("propus")

        # 2. Verificat
        motiv = self.paznic.verifica_propunere(propunere)
        if motiv is None:
            motiv = self.paznic.verifica_examen(self.examen)
        if motiv:
            return anuleaza(motiv)
        stare("verificat")

        # 3. Aplicat
        setari_noi = copy.deepcopy(self.setari_curente)
        for port, modificari in propunere.modificari.items():
            setari_noi.setdefault(port, {}).update(modificari)
        fisa["setari"] = setari_noi
        try:
            date = self._fa("date", setari_noi) if "date" in propunere.modificari else self.date
            model_test = self._fa("model", setari_noi)
        except EroareModul as e:
            return anuleaza(str(e))
        stare("aplicat")

        # 4. Test rapid: prinde greșelile ieftin, înainte de antrenarea lungă
        mostra = date.text_validare()[:CARACTERE_TEST_RAPID]

        def test_rapid() -> float:
            model_test.antreneaza(date, min(2.0, self.config.buget_antrenare_secunde))
            return model_test.biti_pentru(mostra)

        r = self.rulare.executa(test_rapid, self.paznic.timp_test_secunde)
        if not r.reusit:
            return anuleaza(f"testul rapid a eșuat: {r.eroare}")
        if not isinstance(r.valoare, (int, float)) or not math.isfinite(r.valoare):
            return anuleaza(f"testul rapid a dat un rezultat invalid: {r.valoare!r}")
        stare("testat_rapid")

        # 5. Antrenat (model nou, de la 0, cu bugetul complet)
        model = self._fa("model", setari_noi)
        r = self.rulare.executa(
            lambda: model.antreneaza(date, self.config.buget_antrenare_secunde),
            self.paznic.timp_max_secunde,
        )
        fisa["consum"] = {
            "durata_antrenare_secunde": round(r.durata_secunde, 2),
            "memorie_gpu_max_mb": r.memorie_gpu_max_mb,
        }
        if not r.reusit:
            return anuleaza(f"antrenarea a eșuat: {r.eroare}")
        fisa["statistici_antrenare"] = r.valoare
        motiv = self.paznic.verifica_consum(r)
        if motiv:
            return anuleaza(motiv)
        stare("antrenat")

        # 6. Examinat
        r = self.rulare.executa(lambda: self.examen.examineaza(model, date), self.paznic.timp_max_secunde)
        if not r.reusit:
            return anuleaza(f"examenul a eșuat: {r.eroare}")
        scoruri = r.valoare
        fisa["scoruri"] = scoruri
        scor = scoruri.get(self.examen.scor_principal) if isinstance(scoruri, dict) else None
        if not isinstance(scor, (int, float)) or not math.isfinite(scor):
            return anuleaza(f"scorul „{self.examen.scor_principal}” lipsește sau nu e valid: {scor!r}")
        stare("examinat")

        # 7. Decis
        anterior = self._scor(self.cel_mai_bun)
        if self.pornire is not None and self.cel_mai_bun is self.pornire:
            fisa["fata_de_pornire"] = self.pornire["id"]  # primul experiment păstrat al liniei încă nu există
        if anterior is None:
            castig = None
            mai_bun = True
        else:
            castig = (anterior - scor) if self.examen.mai_mic_e_mai_bun else (scor - anterior)
            mai_bun = castig > self.config.prag_zgomot
        fisa["scor_anterior"] = anterior
        fisa["castig"] = castig
        pierdut = None
        if self.config.criterii:
            # Regula 4: criteriile suplimentare vin de la model, prin dupa_examen, ÎNAINTE de decizie (modelul primește
            # decizia pe care ar lua-o scorul principal singur). Doar numere.
            self._dupa_examen(model, fisa, scor, anterior, castig, "pastrat" if mai_bun else "respins")
            fisa["criterii"] = self._criterii(fisa.get("dupa_examen"))
            lipsa = [nume for nume in self.config.criterii if nume not in fisa["criterii"]]
            if lipsa:
                fisa["criterii_lipsa"] = lipsa
            principal = self.config.criteriu_principal()
            if principal is not None:
                pierdut = self._decizie_principal(principal, fisa, scor, anterior, castig)
                mai_bun = pierdut is None
            elif mai_bun:
                pierdut = self._criteriu_pierdut(fisa["criterii"])
                mai_bun = pierdut is None
        if mai_bun:
            fisa["decizie"] = "pastrat"
            try:
                fisa["model_salvat"] = model.salveaza(self.stocare.cale_pentru(f"modele/experiment_{fisa['id']}"))
            except Exception as e:  # noqa: BLE001 - salvarea nu trebuie să piardă experimentul
                fisa["eroare_salvare"] = f"{type(e).__name__}: {e}"
            self.setari_curente = setari_noi
            self.cel_mai_bun = fisa
        else:
            fisa["decizie"] = "respins"
            fisa["motiv"] = pierdut or (
                f"câștig {castig:+.4f} sub pragul de zgomot {self.config.prag_zgomot}"
                if castig is not None and castig > 0
                else "scorul nu e mai bun"
            )

        # 8. După examen: un model care învață între experimente (are `dupa_examen`) primește
        #    rezultatul DOAR ca numere (scor, câștig, decizie), niciodată textul de examen.
        #    (Cu [criterii], dupa_examen a fost deja chemat mai sus, înainte de decizie.)
        if not self.config.criterii:
            self._dupa_examen(model, fisa, scor, anterior, castig, fisa["decizie"])
        stare("decis")
        return self._inregistreaza(fisa, start, stare)

    @staticmethod
    def _dupa_examen(model: Any, fisa: dict[str, Any], scor: float, anterior: float | None, castig: float | None,
                     decizie: str) -> None:
        if hasattr(model, "dupa_examen"):
            try:
                fisa["dupa_examen"] = model.dupa_examen(
                    {"id": fisa["id"], "scor": scor, "scor_anterior": anterior, "castig": castig, "decizie": decizie}
                )
            except Exception as e:  # noqa: BLE001 - o eroare aici nu strică experimentul deja examinat
                fisa["eroare_dupa_examen"] = f"{type(e).__name__}: {e}"

    @staticmethod
    def _criterii(raspuns: Any) -> dict[str, float]:
        """Criteriile din răspunsul modelului (dupa_examen → {"criterii": {nume: număr}}): doar numere finite."""
        criterii = raspuns.get("criterii") if isinstance(raspuns, dict) else None
        if not isinstance(criterii, dict):
            return {}
        return {str(nume): valoare for nume, valoare in criterii.items()
                if isinstance(valoare, (int, float)) and not isinstance(valoare, bool) and math.isfinite(valoare)}

    def _criteriu_pierdut(self, criterii: dict[str, float]) -> str | None:
        """Motivul respingerii, dacă un criteriu a scăzut mai mult decât pragul lui față de cel mai bun experiment
        păstrat; None dacă niciunul. Un criteriu pe care nu-l au amândouă nu se poate compara și nu oprește nimic."""
        if self.cel_mai_bun is None:
            return None
        referinta = self.cel_mai_bun.get("criterii") or self._criterii(self.cel_mai_bun.get("dupa_examen"))
        for nume, regula in self.config.criterii.items():
            if nume not in criterii or nume not in referinta:
                continue
            acum, atunci = criterii[nume], referinta[nume]
            scadere = (atunci - acum) if regula["mai_mare_e_mai_bine"] else (acum - atunci)
            if scadere > regula["prag"]:
                return (f"a pierdut {nume}: {acum:g} față de {atunci:g} la #{self.cel_mai_bun['id']} "
                        f"(a scăzut cu {scadere:g}, pragul e {regula['prag']:g})")
        return None

    def _cel_mai_bun_dupa(self, principal: str) -> dict[str, Any] | None:
        """Cel mai bun experiment PĂSTRAT al liniei după criteriul principal (din criteriile din fișe)."""
        pastrate = [f for f in self.jurnal.istoric(self.config.nume)
                    if f.get("decizie") == "pastrat" and principal in (f.get("criterii") or {})]
        if not pastrate:
            return None
        alege = max if self.config.criterii[principal]["mai_mare_e_mai_bine"] else min
        return alege(pastrate, key=lambda f: f["criterii"][principal])

    def _decizie_principal(self, principal: str, fisa: dict[str, Any], scor: float, anterior: float | None,
                           castig: float | None) -> str | None:
        """Cu un criteriu principal: motivul respingerii, sau None (păstrat). Păstrat = principalul e mai bun cu peste
        pragul lui față de cel mai bun experiment păstrat ȘI niciun alt criteriu, inclusiv scorul examenului (pragul
        lui e prag_zgomot), nu scade peste pragul lui. Primul experiment al liniei e păstrat, ca înainte."""
        if self.cel_mai_bun is None:
            return None
        regula = self.config.criterii[principal]
        referinta = self.cel_mai_bun.get("criterii") or self._criterii(self.cel_mai_bun.get("dupa_examen"))
        id_referinta = self.cel_mai_bun["id"]
        if principal not in fisa["criterii"] or principal not in referinta:
            return f"criteriul principal {principal} nu se poate compara cu #{id_referinta} (lipsește)"
        acum, atunci = fisa["criterii"][principal], referinta[principal]
        fisa["castig_principal"] = (acum - atunci) if regula["mai_mare_e_mai_bine"] else (atunci - acum)
        if fisa["castig_principal"] <= regula["prag"]:
            return (f"criteriul principal {principal}: {acum:g} față de {atunci:g} la #{id_referinta} "
                    f"(câștig {fisa['castig_principal']:+g}, trebuie peste {regula['prag']:g})")
        if castig is not None and -castig > self.config.prag_zgomot:
            return (f"a pierdut {self.examen.scor_principal}: {scor:g} față de {anterior:g} la #{id_referinta} "
                    f"(a scăzut cu {-castig:g}, pragul e {self.config.prag_zgomot:g})")
        return self._criteriu_pierdut(fisa["criterii"])

    def _fa(self, port: str, setari: dict[str, dict[str, Any]]) -> Any:
        """Creează un modul nou (model sau date) cu setările date.

        Modulele care știu să folosească memoria (au `conecteaza_memorie`) o primesc imediat.
        """
        instanta = self.registru.creeaza(port, self.config.porturi[port]["modul"], setari.get(port, {})).instanta
        if hasattr(instanta, "conecteaza_memorie"):
            instanta.conecteaza_memorie(self.memorie)
        return instanta

    def _inregistreaza(self, fisa: dict[str, Any], start: float, stare: Callable[[str], None]) -> dict[str, Any]:
        fisa["durata_totala_secunde"] = round(time.perf_counter() - start, 2)
        stare("inregistrat")
        self.jurnal.adauga(fisa)
        self.interfata.anunta(
            "experiment",
            {
                "id": fisa["id"],
                "propunere": fisa["propunere"]["descriere"],
                "decizie": fisa["decizie"],
                "scor": (fisa.get("scoruri") or {}).get(self.examen.scor_principal),
                "motiv": fisa.get("motiv"),
            },
        )
        return fisa
