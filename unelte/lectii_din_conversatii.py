"""S118 pasul 2 (C-126 B, 17 nov 2026): lecțiile din conversațiile cu Adrian.

Citește baza interfeței (`lucru/interfata/conversatii.db`, în afara Git) și strânge DOAR răspunsurile:
    - marcate 👍 (nota 1) fără corectură  → lecția e răspunsul modelului, așa cum a fost dat;
    - corectate („răspunsul corect ar fi…”), oricare ar fi nota → lecția e corectura lui Adrian.
👎 fără corectură și rândurile fără notă și fără corectură se ignoră (nu știm care e răspunsul bun).

Forma fiecărei lecții = forma perechilor de antrenare de la S116 (`unelte/conversatie_chat.py`): „Întrebare: …⏎Răspuns:”
fără text în față pentru fila „Chat”; „Text: …⏎Întrebare: …⏎Răspuns:” (cu câmpul „text”) pentru fila „Întreabă din text”.

Fără dubluri: o lecție pe întrebare (aceeași întrebare, cu același paragraf, scrisă cu alte spații sau litere mari/mici,
e tot una); dacă aceeași întrebare are mai multe aprecieri, corectura bate 👍, iar între două de același fel câștigă cea
mai nouă.

20 % deoparte, ca examen al lecțiilor: alegerea se face după amprenta întrebării (SHA-256), nu la întâmplare, ca o lecție
să rămână mereu de aceeași parte când se adaugă lecții noi (altfel examenul s-ar scurge în antrenare de la o rulare la
alta).

Ieșirea (totul în `lucru/lectii/`, ignorat de Git — conversațiile lui Adrian nu ajung în Git, hub sau rapoarte):
    lectii.jsonl          lecțiile de antrenare (80 %)
    examen_lectii.jsonl   lecțiile ținute deoparte (20 %)
    info.json             doar numere (câte apreciate, câte lecții, câte deoparte, câte ignorate și de ce)
Fișierele se refac de fiecare dată din bază (rularea e repetabilă: aceeași bază → aceleași fișiere).

    python unelte/lectii_din_conversatii.py                 # baza implicită, dosarul implicit
    python unelte/lectii_din_conversatii.py --baza X.db --dosar lucru/lectii_proba
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

BAZA = "lucru/interfata/conversatii.db"
DOSAR = "lucru/lectii"
LECTII = "lectii.jsonl"
EXAMEN = "examen_lectii.jsonl"
INFO = "info.json"
PROCENT_DEOPARTE = 20


def norm(s: str | None) -> str:
    """Textul fără spațiile în plus și cu litere mici: „ Câți  ani?” și „câți ani?” sunt aceeași întrebare."""
    return " ".join((s or "").split()).casefold()


def cheie(intrebare: str, paragraf: str) -> str:
    """Amprenta întrebării (cu paragraful, la „din text”): după ea se scot dublurile și se alege partea deoparte."""
    return hashlib.sha256(f"{norm(paragraf)}\n{norm(intrebare)}".encode("utf-8")).hexdigest()


def e_deoparte(amprenta: str, procent: int = PROCENT_DEOPARTE) -> bool:
    return int(amprenta[:8], 16) % 100 < procent


def lectie_din(rand: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    """Din rândul întors de `Catalog.apreciate()` face o lecție, sau întoarce (None, motivul)."""
    from module.model_conversatie import intrebarea

    intrebare = " ".join((rand.get("intrebare") or "").split())
    paragraf = (rand.get("paragraf") or "").strip()
    corectura = (rand.get("corectura") or "").strip()
    nota = rand.get("nota")
    if not intrebare:
        return None, "fara_intrebare"
    if corectura:
        raspuns, tip = corectura, "corectat"
    elif nota == 1:
        raspuns, tip = (rand.get("raspuns") or "").strip(), "apreciat"
        if not raspuns:
            return None, "raspuns_gol"
    elif nota == -1:
        return None, "nu_fara_corectura"
    else:
        return None, "fara_nota"
    fila = rand.get("fila") or "chat"
    amprenta = cheie(intrebare, paragraf if fila == "text" else "")
    lectie: dict[str, Any] = {"fel": f"lectie_{fila}", "tip": tip,
                              "prompt": intrebarea(intrebare, paragraf if fila == "text" else ""),
                              "intrebare": intrebare, "raspuns": raspuns, "cheie": [], "subiect": "",
                              "id": f"lectie_{amprenta[:16]}"}
    if fila == "text":
        lectie["text"] = paragraf
    return lectie | {"_creata": rand.get("creata") or ""}, tip


def strange(apreciate: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], Counter]:
    """Lecțiile, fără dubluri (o lecție pe întrebare), în ordinea amprentei; plus numărătoarea motivelor."""
    numere: Counter = Counter()
    alese: dict[str, dict[str, Any]] = {}
    for rand in apreciate:
        lectie, motiv = lectie_din(rand)
        numere[motiv] += 1
        if lectie is None:
            continue
        vechi = alese.get(lectie["id"])
        if vechi is not None:
            numere["dubluri"] += 1
            rang_nou = (lectie["tip"] == "corectat", lectie["_creata"])
            rang_vechi = (vechi["tip"] == "corectat", vechi["_creata"])
            if rang_nou <= rang_vechi:
                continue
        alese[lectie["id"]] = lectie
    lectii = [{k: v for k, v in l.items() if k != "_creata"} for _, l in sorted(alese.items())]
    return lectii, numere


def imparte(lectii: list[dict[str, Any]], procent: int = PROCENT_DEOPARTE
            ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    antrenare, deoparte = [], []
    for l in lectii:
        (deoparte if e_deoparte(l["id"][len("lectie_"):], procent) else antrenare).append(l)
    return antrenare, deoparte


def _scrie_jsonl(cale: Path, randuri: list[dict[str, Any]]) -> None:
    cale.write_bytes("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in randuri).encode("utf-8"))


def ruleaza(baza: Path, dosar: Path, procent: int = PROCENT_DEOPARTE) -> dict[str, Any]:
    from module.interfata.catalog import Catalog

    if not baza.exists():
        raise FileNotFoundError(f"Baza interfeței nu există: {baza}")
    apreciate = Catalog(baza).apreciate()
    lectii, numere = strange(apreciate)
    antrenare, deoparte = imparte(lectii, procent)
    dosar.mkdir(parents=True, exist_ok=True)
    _scrie_jsonl(dosar / LECTII, antrenare)
    _scrie_jsonl(dosar / EXAMEN, deoparte)
    info = {
        "apreciate": len(apreciate),
        "lectii": len(lectii),
        "antrenare": len(antrenare),
        "deoparte": len(deoparte),
        "procent_deoparte": procent,
        "corectate": sum(l["tip"] == "corectat" for l in lectii),
        "apreciate_fara_corectura": sum(l["tip"] == "apreciat" for l in lectii),
        "din_chat": sum(l["fel"] == "lectie_chat" for l in lectii),
        "din_text": sum(l["fel"] == "lectie_text" for l in lectii),
        "ignorate": {k: v for k, v in sorted(numere.items()) if k not in ("corectat", "apreciat")},
    }
    (dosar / INFO).write_bytes(json.dumps(info, ensure_ascii=False, indent=1).encode("utf-8"))
    return info


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Strânge lecțiile (👍 și corecturile) din conversațiile din interfață.")
    p.add_argument("--baza", default=BAZA, help=f"baza interfeței (implicit {BAZA})")
    p.add_argument("--dosar", default=DOSAR, help=f"unde scrie lecțiile (implicit {DOSAR})")
    args = p.parse_args(argv)
    baza = Path(args.baza) if Path(args.baza).is_absolute() else RADACINA / args.baza
    dosar = Path(args.dosar) if Path(args.dosar).is_absolute() else RADACINA / args.dosar
    try:
        info = ruleaza(baza, dosar)
    except FileNotFoundError as e:
        print(e)
        return 2
    # doar numere pe ecran, niciodată textul conversațiilor
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
