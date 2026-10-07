"""Examenele elevului din afara examenului oficial (Faza 3): examenul de fapte (cel vechi și cel nou, reformulat) și
nota profesorului pe povești nevăzute. Nu e un modul de port, ci o bibliotecă: o folosesc uneltele (unelte/examen_fapte.py, unelte/examen_profesor.py,
unelte/test_profesor.py) și GPT-ul însuși, cu setarea examene_suplimentare, ca să dea prin dupa_examen criteriile
suplimentare ale deciziei (regula 4). Examenul oficial (val_bpb) nu se atinge.

Examenul de fapte: pentru fiecare din cele 50 de fapte ale profesorului, 3 propoziții cu un gol la capăt (faptul însuși;
spus de mama; învățat de Lily). Elevul completează fără întâmplare (completeaza). Corect = primul cuvânt (după un
„the/a/an”) e printre cele acceptate; numărăm și doar cu cuvântul din fapt, fără sinonime.
Examenul de fapte nou (7 octombrie 2026, unelte/examen_fapte_nou.py): pentru aceleași 50 de fapte, câte 3 propoziții
REFORMULATE de profesor (alt subiect, altă construcție), cu același cuvânt-răspuns la capăt, în date/fapte/examen_nou.json.
Niciuna și niciun fragment de 5 cuvinte din ele nu apare în poveștile cu fapte sau în TinyStories: le poate ști doar
cine a înțeles faptul, nu cine a memorat propozițiile din antrenare. Scorul principal: fapte_noi (doar cu cuvântul din fapt).
Nota profesorului: elevul pornește din prima propoziție a unor povești din validarea R2 (alese mereu la fel) și scrie cam
cât povestea originală; profesorul notează fără întâmplare.
"""

from __future__ import annotations

import json
import random
import re
import statistics
from pathlib import Path
from typing import Any

from module.profesor_qwen import SUBIECTE

SEPARATOR = "<|endoftext|>"

# --- examenul de fapte ----------------------------------------------------------------------------------------

# subiect → (începutul propoziției, până la gol; răspunsurile acceptate). Primul răspuns e cuvântul din fapt.
INTREBARI: dict[str, tuple[str, tuple[str, ...]]] = {
    "snow": ("Water freezes into", ("ice",)),
    "birds": ("Birds have", ("feathers",)),
    "the Sun": ("The Sun is a", ("star",)),
    "plants": ("Plants need water and sunlight to", ("grow",)),
    "the Moon": ("The Moon goes around the", ("earth",)),
    "bees": ("Bees make", ("honey",)),
    "fish": ("Fish breathe through their", ("gills",)),
    "rain": ("Rain falls from", ("clouds",)),
    "spiders": ("Spiders have eight", ("legs",)),
    "frogs": ("Frogs start their lives as", ("tadpoles",)),
    "butterflies": ("A caterpillar changes into a", ("butterfly",)),
    "cows": ("Cows give", ("milk",)),
    "teeth": ("Brushing your teeth helps keep them", ("healthy", "clean")),
    "rainbows": ("A rainbow can appear when sunlight shines through", ("raindrops", "rain")),
    "autumn": ("Many trees lose their leaves in", ("autumn", "fall")),
    "the sea": ("Sea water is", ("salty",)),
    "magnets": ("Magnets pull things made of", ("iron", "metal")),
    "the heart": ("The heart pumps", ("blood",)),
    "bats": ("Bats are mammals that can", ("fly",)),
    "penguins": ("Penguins are birds that cannot", ("fly",)),
    "volcanoes": ("Hot melted rock called", ("lava",)),
    "shadows": ("A shadow forms when something blocks the", ("light", "sun", "sunlight")),
    "boiling water": ("Water boils when it gets very", ("hot",)),
    "owls": ("Many owls hunt at", ("night",)),
    "camels": ("Camels can go a long time without drinking", ("water",)),
    "elephants": ("Elephants use their", ("trunks",)),
    "stars": ("Stars are very", ("far",)),
    "wind": ("Wind is moving", ("air",)),
    "ants": ("Ants live and work together in big groups called", ("colonies", "colony")),
    "seeds": ("A big tree can grow from a small", ("seed",)),
    "snakes": ("Snakes have no", ("legs",)),
    "whales": ("Whales breathe air through a", ("blowhole",)),
    "ice cream": ("Ice cream melts when it gets", ("warm", "hot")),
    "night": ("It gets dark at night because our side of the Earth turns away from the", ("sun",)),
    "sleep": ("Our bodies need sleep to stay", ("healthy",)),
    "bread": ("Bread is made from", ("flour", "wheat")),
    "chickens": ("Hens lay", ("eggs",)),
    "turtles": ("A turtle carries its", ("shell",)),
    "thunderstorms": ("We see lightning before we hear the", ("thunder",)),
    "mountains": ("At the top of a high mountain, it is usually", ("colder", "cold")),
    "dogs": ("Dogs have a very good sense of", ("smell",)),
    "cats": ("Cats can see well when there is little", ("light",)),
    "apples": ("Apples grow on", ("trees",)),
    "the Earth": ("The Earth goes around the", ("sun",)),
    "squirrels": ("Squirrels hide", ("nuts", "acorns")),
    "bears": ("Some bears sleep through most of the", ("winter",)),
    "carrots": ("Carrots grow under the", ("ground", "soil", "dirt")),
    "clouds": ("Clouds are made of tiny drops of", ("water",)),
    "sand": ("Sand is made of tiny pieces of", ("rock", "stone", "shells")),
    "washing hands": ("Washing your hands with soap helps wash away", ("germs",)),
}
CADRE = ("{p} ___.", 'Mom said, "{p} ___."', "Lily learned that {pm} ___.")
ARTICOLE = ("the", "a", "an")


def intrebarea(cadru: str, inceput: str) -> tuple[str, str]:
    """(propoziția cu gol, textul pe care îl primește elevul: tot ce e înainte de gol)."""
    propozitie = cadru.format(p=inceput, pm=inceput[0].lower() + inceput[1:])
    return propozitie, propozitie.split(" ___")[0]


def _singular(cuvant: str) -> str:
    return cuvant[:-1] if cuvant.endswith("s") and len(cuvant) > 3 else cuvant


def raspunsul(completare: str) -> str:
    """Primul cuvânt al completării, cu litere mici, după un „the/a/an” de la început (dacă e)."""
    cuvinte = re.findall(r"[A-Za-z]+", completare)
    if len(cuvinte) > 1 and cuvinte[0].lower() in ARTICOLE:
        cuvinte = cuvinte[1:]
    return cuvinte[0].lower() if cuvinte else ""


def e_corect(completare: str, acceptate: tuple[str, ...]) -> bool:
    raspuns = raspunsul(completare)
    return bool(raspuns) and any(_singular(raspuns) == _singular(a) for a in acceptate)


def examineaza_fapte(model: Any) -> list[dict[str, Any]]:
    """Cele 150 de întrebări (50 de fapte × 3 propoziții), cu completarea elevului și dacă e corectă."""
    max_simboluri = 4 if getattr(model, "tokenizer", "") == "bpe" else 16  # pe litere: un cuvânt are mai multe semne
    rezultate = []
    for subiect, fapt in SUBIECTE:
        inceput, acceptate = INTREBARI[subiect]
        for k, cadru in enumerate(CADRE, start=1):
            propozitie, text = intrebarea(cadru, inceput)
            completare = model.completeaza(text, max_simboluri)
            rezultate.append({"subiect": subiect, "fapt": fapt, "propozitie": k, "intrebare": propozitie,
                              "completare": completare, "raspuns": raspunsul(completare),
                              "acceptate": list(acceptate), "corect": e_corect(completare, acceptate),
                              "corect_cuvantul_din_fapt": e_corect(completare, acceptate[:1])})
    return rezultate


def scor_fapte(rezultate: list[dict[str, Any]]) -> dict[str, int]:
    """Numerele examenului de fapte: corecte doar cu cuvântul din fapt, cu sinonime, și câte fapte au măcar unul corect."""
    return {
        "fapte_corecte": sum(r["corect_cuvantul_din_fapt"] for r in rezultate),
        "fapte_corecte_cu_sinonime": sum(r["corect"] for r in rezultate),
        "fapte_stiute": sum(1 for s, _ in SUBIECTE if any(r["corect"] for r in rezultate if r["subiect"] == s)),
    }


# --- examenul de fapte nou: propoziții reformulate, care nu apar în textele de antrenare ------------------------

CALE_EXAMEN_NOU = "date/fapte/examen_nou.json"


def cuvinte(text: str) -> list[str]:
    """Cuvintele unui text, cu litere mici și fără semne (apostroful din interior rămâne: „bird's”)."""
    return re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)*", text.lower().replace("’", "'").replace("‘", "'"))


def citeste_examen_nou(cale: str | Path = CALE_EXAMEN_NOU) -> list[dict[str, Any]]:
    """Întrebările examenului nou: subiect, fapt, propoziție (cu „___” la capăt), răspuns (cuvântul din fapt), acceptate."""
    return json.loads(Path(cale).read_text(encoding="utf-8"))["intrebari"]


def examineaza_fapte_noi(model: Any, cale: str | Path = CALE_EXAMEN_NOU) -> list[dict[str, Any]]:
    """Cele 150 de propoziții reformulate, cu completarea elevului (fără întâmplare) și dacă e corectă."""
    max_simboluri = 4 if getattr(model, "tokenizer", "") == "bpe" else 16
    rezultate = []
    for intrebare in citeste_examen_nou(cale):
        completare = model.completeaza(intrebare["propozitie"].split(" ___")[0], max_simboluri)
        rezultate.append({"subiect": intrebare["subiect"], "fapt": intrebare["fapt"], "intrebare": intrebare["propozitie"],
                          "completare": completare, "raspuns": raspunsul(completare),
                          "acceptate": list(intrebare["acceptate"]),
                          "corect": e_corect(completare, tuple(intrebare["acceptate"])),
                          "corect_cuvantul_din_fapt": e_corect(completare, (intrebare["raspuns"],))})
    return rezultate


def scor_fapte_noi(rezultate: list[dict[str, Any]]) -> dict[str, int]:
    """Numerele examenului nou, ca la cel vechi: doar cu cuvântul din fapt (fapte_noi), cu sinonime, fapte știute."""
    return {
        "fapte_noi": sum(r["corect_cuvantul_din_fapt"] for r in rezultate),
        "fapte_noi_cu_sinonime": sum(r["corect"] for r in rezultate),
        "fapte_noi_stiute": len({r["subiect"] for r in rezultate if r["corect"]}),
    }


# --- nota profesorului pe povești nevăzute ---------------------------------------------------------------------


def alege_povesti(text: str, numar: int, samanta: int = 0) -> list[str]:
    """`numar` povești din validare, alese la întâmplare (aceeași sămânță = aceleași povești), în ordinea din text."""
    povesti = [p.strip() for p in text.split(SEPARATOR) if p.strip()]
    return [povesti[i] for i in sorted(random.Random(samanta).sample(range(len(povesti)), numar))]


def prima_propozitie(poveste: str) -> str:
    """Începutul dat elevului: prima propoziție (până la primul . ! ?), sau primele 8 cuvinte dacă nu are."""
    gasit = re.match(r"\s*(.+?[.!?][\"”']?)(?=\s|$)", poveste, re.S)
    return gasit.group(1) if gasit else " ".join(poveste.split()[:8])


def taie_la_propozitie(text: str) -> str:
    """Povestea elevului până la primul sfârșit de poveste și, dacă e tăiată la mijloc, până la ultima propoziție întreagă
    (ca nota să nu fie trasă în jos doar de lungimea la care s-a oprit scrisul)."""
    text = text.split(SEPARATOR)[0].strip()
    if re.search(r"[.!?][\"”']?$", text):
        return text
    capete = list(re.finditer(r"[.!?][\"”']?(?=\s|$)", text))
    return text[: capete[-1].end()] if capete else text


def povesti_elevului(elev: Any, originale: list[str]) -> list[dict[str, str]]:
    """Elevul pornește din prima propoziție a fiecărei povești originale și scrie cam cât ea (între 200 și 1.000 de
    litere); povestea lui se taie la ultima propoziție întreagă."""
    povesti = []
    for original in originale:
        inceput = prima_propozitie(original)
        lungime = max(200, min(1000, len(original) - len(inceput)))
        povesti.append({"inceput": inceput, "poveste": taie_la_propozitie(inceput + elev.genereaza(inceput, lungime))})
    return povesti


def distributie(note: list[int | None]) -> dict[str, int]:
    numarate: dict[int, int] = {}
    for n in note:
        if n is not None:
            numarate[n] = numarate.get(n, 0) + 1
    return {str(n): numarate.get(n, 0) for n in range(1, 11)}


def medie(note: list[int | None]) -> float | None:
    valide = [n for n in note if n is not None]
    return round(statistics.mean(valide), 2) if valide else None


def nota_profesorului(elev: Any, validare: str, numar: int = 20, lot: int = 8, profesor: Any = None) -> dict[str, Any]:
    """Elevul scrie cele `numar` povești, iar profesorul le notează (fără întâmplare): poveștile, notele și media. Un
    profesor dat se folosește așa cum e; altfel se încarcă unul și se eliberează la final."""
    from module.profesor_qwen import ProfesorQwen

    originale = alege_povesti(Path(validare).read_text(encoding="utf-8"), numar)
    povesti = povesti_elevului(elev, originale)
    profesorul = profesor if profesor is not None else ProfesorQwen(lot=lot)
    note = profesorul.noteaza_mai_multe([p["poveste"] for p in povesti])
    if profesor is None:
        profesorul.elibereaza()
    return {"povesti": povesti, "note": note, "nota_medie": medie([n["nota"] for n in note])}
