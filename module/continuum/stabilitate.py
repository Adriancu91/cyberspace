"""Stabilitate pe două niveluri (v1, punctul 3): un scor mai bun devine „candidat”. Linia de bază, și încrederea
strategiei care l-a adus, se mută doar după o a doua măsurătoare independentă care îl confirmă.

- **Candidații** stau în coadă, în stare.json („candidati”), fiecare cu motivul, de când e și ce a decis-o. Sunt două
  feluri:
  - **linia de bază:** ultimul model păstrat e mai bun decât linia de bază confirmată, cu peste prag. La confirmare,
    linia de bază se mută (și încrederea strategiei care l-a adus, dacă e una);
  - **succes:** o antrenare pornită de CONTINUUM a ieșit mai bună decât modelul de la care a pornit, dar nu și decât
    linia de bază. La confirmare, se mută doar încrederea strategiei.
- **Măsurătoare independentă:** aceeași capacitate, fie pe același model, a doua oară (ex. examenul de la oră și
  unealta de examen, sau unealta de două ori), fie pe un model păstrat MAI NOU de pe aceeași linie.
- **Confirmare:** cel puțin [stabilitate] confirmari măsurători independente sunt și ele mai bune decât referința
  (linia de bază veche, sau modelul de pornire) cu peste prag. Linia de bază nouă e cea mai slabă dintre ele și
  candidat (prudent), și doar dacă e mai bună decât linia de bază de acum: linia de bază nu coboară niciodată.
- **După o antrenare pornită de CONTINUUM,** toate orele păstrate noi intră în coadă, în ordine (nu doar ultima): așa,
  ora 7 e confirmată de ora 8.
- **Infirmare:** o măsurătoare independentă care NU e mai bună face candidatul „neconfirmat”, dacă nu sunt destule
  confirmări.
- **La început,** linia de bază a fiecărei capacități e cea mai bună valoare păstrată din jurnal, de dinaintea
  acțiunii: e trecută în memorie ca „inițializată din jurnal” și de acolo se mută doar prin confirmare.
"""

from __future__ import annotations

from typing import Any, Callable

from module.continuum import peste, ro_scurt
from module.continuum.evalueaza import StareaOrganismului
from module.continuum.masuratori import masuratori_unelte, valoare
from module.continuum.zgomot import masuratori_pe_experiment

CANDIDAT, CONFIRMAT, NECONFIRMAT = "candidat", "confirmat", "neconfirmat"
ASTEPT = "aștept o a doua măsurătoare"


def initializeaza(memorie: dict[str, Any], stare: StareaOrganismului, timp: str) -> None:
    """Linia de bază a capacităților care n-au încă una în memorie: cea mai bună din jurnal (o singură dată)."""
    for nume, c in stare.capacitati.items():
        m = memorie["capacitati"].setdefault(nume, {})
        if not m.get("baza_confirmata") and c.linie_de_baza is not None:
            m.update(linie_de_baza=c.linie_de_baza, experiment_baza=c.experiment_baza, baza_confirmata=True,
                     sursa_bazei="inițializată din jurnal (cel mai bun experiment păstrat)", baza_de_la=timp)


def _candidat(nume: str, model: dict[str, Any], valoare_noua: float, referinta: float, experiment_referinta: Any,
              prag: float, castig: float, muta_baza: bool, timp: str) -> dict[str, Any]:
    fata_de = (f"peste linia de bază {ro_scurt(referinta)} (#{experiment_referinta})" if muta_baza else
               f"peste modelul de pornire #{experiment_referinta} ({ro_scurt(referinta)})")
    return {"capacitate": nume, "experiment": model.get("experiment"), "linie": model.get("linie"),
            "valoare": valoare_noua, "referinta": referinta, "experiment_referinta": experiment_referinta, "prag": prag,
            "muta_baza": muta_baza, "stare": CANDIDAT, "de_la": timp,
            "motiv": (f"{nume} = {ro_scurt(valoare_noua)} pe #{model.get('experiment')}, {fata_de} cu "
                      f"{ro_scurt(castig)}, mai mult decât pragul {ro_scurt(prag)}; {ASTEPT}")}


def adauga_candidati(memorie: dict[str, Any], stare: StareaOrganismului, timp: str,
                     fise: list[dict[str, Any]] | None = None, config: dict[str, Any] | None = None,
                     de_la_id: int | None = None) -> list[dict[str, Any]]:
    """Scorurile mai bune decât linia de bază cu peste prag intră în coadă (o dată): pe ultimul model păstrat, sau, cu
    `de_la_id` (după o acțiune), pe fiecare model păstrat nou, în ordine."""
    if de_la_id is None or fise is None or config is None:
        modele = [(stare.ultimul_model, {n: c.curent for n, c in stare.capacitati.items()})] if stare.ultimul_model else []
    else:
        unelte, pe_id = masuratori_unelte(fise, config), {f.get("id"): f for f in fise}
        modele = [(m, {n: valoare(pe_id[m["experiment"]], config["capacitati"][n], unelte) for n in stare.capacitati})
                  for m in stare.modele if m["experiment"] > de_la_id and m["experiment"] in pe_id]
    noi = []
    for model, valori in modele:
        for nume, c in stare.capacitati.items():
            v = valori.get(nume)
            if v is None or c.linie_de_baza is None or not peste(c.castig(v, c.linie_de_baza), c.prag_zgomot):
                continue
            if cauta(memorie, nume, model.get("experiment"), muta_baza=True) is not None:
                continue
            candidat = _candidat(nume, model, v, c.linie_de_baza, c.experiment_baza, c.prag_zgomot,
                                 c.castig(v, c.linie_de_baza), True, timp)
            memorie["candidati"].append(candidat)
            noi.append(candidat)
    return noi


def adauga_succes(memorie: dict[str, Any], stare: StareaOrganismului, capacitate: str, referinta: float,
                  experiment_referinta: Any, timp: str) -> dict[str, Any]:
    """Succesul unei antrenări care nu bate linia de bază: așteaptă și el confirmarea, doar pentru încredere."""
    c, model = stare.capacitati[capacitate], stare.ultimul_model or {}
    gasit = cauta(memorie, capacitate, model.get("experiment"), muta_baza=False)
    if gasit is not None:
        return gasit
    candidat = _candidat(capacitate, model, c.curent, referinta, experiment_referinta, c.prag_zgomot,
                         c.castig(c.curent, referinta), False, timp)
    memorie["candidati"].append(candidat)
    return candidat


def independente(candidat: dict[str, Any], fise: list[dict[str, Any]], cap: dict[str, Any]) -> list[tuple[float, str]]:
    """Celelalte măsurători ale aceleiași capacități: pe același model, a doua oară, și pe modelele păstrate mai noi de
    pe aceeași linie. (valoare, de unde)"""
    pe_model = list(masuratori_pe_experiment(fise, cap).get(candidat["experiment"], []))
    if candidat["valoare"] in pe_model:
        pe_model.remove(candidat["valoare"])  # el însuși nu se confirmă
    rezultat = [(v, f"a doua măsurătoare a modelului #{candidat['experiment']}") for v in pe_model]
    unelte = masuratori_unelte(fise, {"capacitati": {"x": cap}})
    for fisa in sorted(fise, key=lambda f: f.get("id", 0)):
        if fisa.get("linie") == candidat["linie"] and fisa.get("decizie") == "pastrat" \
                and fisa.get("id", 0) > (candidat["experiment"] or 0):
            v = valoare(fisa, cap, unelte)
            if v is not None:
                rezultat.append((v, f"modelul păstrat mai nou #{fisa['id']}"))
    return rezultat


def actualizeaza(memorie: dict[str, Any], fise: list[dict[str, Any]], config: dict[str, Any], timp: str,
                 aplica: Callable[[dict[str, Any]], None] | None = None) -> list[dict[str, Any]]:
    """Confirmă sau infirmă candidații din coadă. `aplica(candidat)` e chemat pentru fiecare confirmare sau infirmare
    a unui candidat care are o strategie în așteptare (ÎNVAȚĂ mută atunci încrederea). Întoarce schimbările."""
    schimbari = []
    for candidat in memorie["candidati"]:
        if candidat["stare"] != CANDIDAT:
            continue
        cap = config["capacitati"].get(candidat["capacitate"])
        if cap is None:
            continue
        mai_mare = cap["mai_mare_e_mai_bine"]
        alte = independente(candidat, fise, cap)
        bune = [(v, de_unde) for v, de_unde in alte
                if peste(v - candidat["referinta"] if mai_mare else candidat["referinta"] - v, candidat["prag"])]
        rele = [(v, de_unde) for v, de_unde in alte if (v, de_unde) not in bune]
        if len(bune) >= config["stabilitate"]["confirmari"]:
            valori = [candidat["valoare"]] + [v for v, _ in bune]
            prudenta = min(valori) if mai_mare else max(valori)  # cea mai slabă dintre ele
            text = f"confirmat de {bune[0][1]} ({ro_scurt(bune[0][0])})"
            m = memorie["capacitati"].setdefault(candidat["capacitate"], {})
            acum = m.get("linie_de_baza")
            mai_buna = acum is None or (peste(prudenta, acum) if mai_mare else peste(acum, prudenta))
            if candidat["muta_baza"] and mai_buna:
                m.update(linie_de_baza=prudenta, experiment_baza=candidat["experiment"], baza_confirmata=True,
                         baza_de_la=timp, sursa_bazei=f"confirmată de {bune[0][1]}")
                text += f"; linia de bază: {ro_scurt(prudenta)}"
            elif candidat["muta_baza"]:
                text += f"; linia de bază rămâne {ro_scurt(acum)} (e deja mai bună)"
            candidat.update(stare=CONFIRMAT, la=timp, confirmat_de=bune[0][1], motiv=candidat["motiv"].replace(ASTEPT, text))
        elif rele:
            candidat.update(stare=NECONFIRMAT, la=timp, infirmat_de=rele[0][1], motiv=candidat["motiv"].replace(
                ASTEPT, f"neconfirmat: {rele[0][1]} are {ro_scurt(rele[0][0])}"))
        else:
            continue
        schimbari.append(candidat)
        if aplica is not None and candidat.get("strategie"):
            aplica(candidat)
    return schimbari


def cauta(memorie: dict[str, Any], capacitate: str, experiment: Any, muta_baza: bool | None = None) -> dict[str, Any] | None:
    return next((k for k in memorie["candidati"] if k["capacitate"] == capacitate and k["experiment"] == experiment
                 and (muta_baza is None or k["muta_baza"] == muta_baza)), None)


def in_asteptare(memorie: dict[str, Any]) -> list[dict[str, Any]]:
    return [k for k in memorie.get("candidati", []) if k["stare"] == CANDIDAT]
