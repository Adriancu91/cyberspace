"""Raportul buclei de auto-îmbunătățire (config/laptop_bucla.toml): tabelul experimentelor, cel mai bun scor și ce
direcții au ajutat.

Citește jurnalul (doar citire) pentru linia din configurare și scrie raportul în Markdown.
Cum se citește: cu continuare, o rețetă cu o arhitectură deja încercată (aceleași straturi, lățime, capete și context)
pornește din cea mai bună stare a acelei arhitecturi, deci are în spate mai multe minute de antrenare; o arhitectură nouă
pornește de la zero și are doar 5 minute. Câștigul unei schimbări de lot sau de rată se amestecă așa cu antrenamentul în
plus. De aceea tabelul arată și minutele din spate, iar la direcții sunt două comparații curate, separate: rețetele
pornite de la zero (toate cu exact 5 minute) între ele, și continuările care au pornit din aceeași stare.

    python unelte/raport_bucla.py                                   # pe ecran
    python unelte/raport_bucla.py --iesire lucru/bucla/raport.md    # și în fișier
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.config import citeste_config  # noqa: E402
from kronos.jurnal import Jurnal  # noqa: E402

SCOR = "val_bpb"
NUME = {"n_straturi": "straturi", "n_emb": "lățime", "context": "context", "lot": "lot", "rata_invatare": "rata"}
SCHIMBARE = re.compile(r"^(lista|strângere în jurul locului \d+ \(#(\d+), scor [\d.]+\)): \w+\.(\w+): (\S+) → (\S+)$")


def nr(x: Any, zecimale: int = 4, semn: bool = False) -> str:
    """Număr cu virgulă, ca în restul README-ului (1,2345); „–” dacă lipsește."""
    if not isinstance(x, (int, float)) or isinstance(x, bool):
        return "–"
    return f"{x:{'+' if semn else ''}.{zecimale}f}".replace(".", ",")


def mii(n: Any) -> str:
    """Număr întreg cu punct la mii, ca în restul README-ului (23.368); „–” dacă lipsește."""
    return f"{n:,}".replace(",", ".") if isinstance(n, int) and not isinstance(n, bool) else "–"


def de(n: int) -> str:
    """„21 de experimente”, dar „7 experimente”."""
    return "de " if n >= 20 and (n % 100 == 0 or n % 100 >= 20) else ""


def _valoare(text: str) -> Any:
    for tip in (int, float):
        try:
            return tip(text)
        except ValueError:
            pass
    return text


def _val(setare: str | None, v: Any) -> str:
    if setare == "rata_invatare" and isinstance(v, float):
        return f"{v:.6f}".rstrip("0").replace(".", ",")
    return str(v)


def schimbarea(fisa: dict[str, Any]) -> dict[str, Any]:
    """Din descrierea propunerii: faza (pornire, lista, strângere), setarea schimbată, valoarea veche și cea nouă."""
    descriere = fisa.get("propunere", {}).get("descriere", "")
    potrivire = SCHIMBARE.match(descriere)
    if potrivire is None:
        faza = "pornire" if descriere.startswith("punct de plecare") else "altceva"
        return {"faza": faza, "setare": None, "veche": None, "noua": None, "baza": None}
    faza, baza, setare, veche, noua = potrivire.groups()
    return {"faza": "lista" if faza == "lista" else "strângere", "setare": setare, "veche": _valoare(veche),
            "noua": _valoare(noua), "baza": int(baza) if baza else None}


def rand(fisa: dict[str, Any]) -> dict[str, Any]:
    """Ce arată raportul despre un experiment."""
    model = (fisa.get("setari") or {}).get("model", {})
    statistici = fisa.get("statistici_antrenare") or {}
    continuare = (fisa.get("dupa_examen") or {}).get("continuare") or {}
    scor = (fisa.get("scoruri") or {}).get(SCOR)
    return {
        "id": fisa["id"],
        **schimbarea(fisa),
        "reteta": {k: model.get(k) for k in (*NUME, "n_capete")},
        "parametri": statistici.get("parametri"),
        "continuat": statistici.get("continuat"),
        "scor_la_pornire": statistici.get("scor_la_pornire"),
        "minute_total": statistici.get("minute_total"),
        "pasi": statistici.get("pasi"),
        "pasi_total": statistici.get("pasi_total"),
        "memorie_mb": statistici.get("memorie_rezervata_mb"),
        "scor": scor if isinstance(scor, (int, float)) else None,
        "castig": fisa.get("castig"),
        "decizie": fisa.get("decizie"),
        "motiv": fisa.get("motiv"),
        "stare_salvata": continuare.get("salvat"),
        "inceput": fisa.get("inceput"),
        "durata": fisa.get("durata_totala_secunde"),
    }


def randuri_din(fise: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rândurile raportului, plus câștigul față de rețeta de bază a cercetătorului (lista: cea mai bună de atunci;
    strângere: rețeta din jurul căreia a căutat) și, la continuări, față de starea din care a pornit modelul."""
    randuri = [rand(f) for f in fise]
    scor_id = {r["id"]: r["scor"] for r in randuri}
    for r in randuri:
        r["fata_de_baza"] = None
        if r["scor"] is not None:
            if r["faza"] == "lista":
                r["fata_de_baza"] = r["castig"]
            elif r["faza"] == "strângere" and scor_id.get(r["baza"]) is not None:
                r["fata_de_baza"] = scor_id[r["baza"]] - r["scor"]
        r["fata_de_stare"] = (
            r["scor_la_pornire"] - r["scor"]
            if r["continuat"] and r["scor_la_pornire"] is not None and r["scor"] is not None
            else None
        )
    return randuri


def _reteta(r: dict[str, Any]) -> str:
    t = r["reteta"]
    return f"{t['n_straturi']}×{t['n_emb']} · c{t['context']} · lot {t['lot']} · {_val('rata_invatare', t['rata_invatare'])}"


def _schimbare(r: dict[str, Any]) -> str:
    if r["setare"] not in NUME:
        return "–"
    return f"{NUME[r['setare']]}: {_val(r['setare'], r['veche'])} → {_val(r['setare'], r['noua'])}"


def _pornire(r: dict[str, Any]) -> str:
    if r["continuat"]:
        return f"din starea cu {nr(r['scor_la_pornire'])}" if r["scor_la_pornire"] is not None else "continuă"
    return "de la zero" if r["continuat"] is False else "–"


def _decizia(r: dict[str, Any]) -> str:
    if r["decizie"] == "pastrat":
        return "**păstrat**"
    if r["decizie"] == "anulat":
        return f"anulat ({r['motiv']})" if r["motiv"] else "anulat"
    return r["decizie"] or "–"


def _parametri(r: dict[str, Any]) -> str:
    return f"{nr(r['parametri'] / 1e6, 1)} M" if isinstance(r["parametri"], (int, float)) else "–"


def _pasi(r: dict[str, Any]) -> str:
    """Pașii experimentului și câte simboluri a văzut în ei (pași × lot × context)."""
    t = r["reteta"]
    if not all(isinstance(x, int) for x in (r["pasi"], t["lot"], t["context"])):
        return mii(r["pasi"])
    return f"{mii(r['pasi'])} ({nr(r['pasi'] * t['lot'] * t['context'] / 1e6, 1)} M)"


def tabel(randuri: list[dict[str, Any]]) -> list[str]:
    linii = [
        "| # | Faza | Schimbarea | Rețeta (straturi×lățime · context · lot · rata) | Parametri | Pornire "
        "| Pași (simboluri văzute) | Minute în spate | val_bpb | Câștig | Decizie |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in randuri:
        linii.append(
            f"| {r['id']} | {r['faza']} | {_schimbare(r)} | {_reteta(r)} | {_parametri(r)} | {_pornire(r)} "
            f"| {_pasi(r)} | {nr(r['minute_total'], 0)} | {nr(r['scor'])} | {nr(r['castig'], semn=True)} | {_decizia(r)} |"
        )
    return linii


def cel_mai_bun(randuri: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Ca la Kronos: cel mai bun dintre experimentele păstrate."""
    pastrate = [r for r in randuri if r["decizie"] == "pastrat" and r["scor"] is not None]
    return min(pastrate, key=lambda r: r["scor"]) if pastrate else None


def pe_setari(randuri: list[dict[str, Any]], prag: float) -> list[str]:
    """Pentru fiecare setare și sens: câte încercări, câte de la zero, câte păstrate, câte mai bune decât baza."""
    grupe: dict[tuple[str, bool], list[dict[str, Any]]] = defaultdict(list)
    for r in randuri:
        v, n = r["veche"], r["noua"]
        if r["setare"] in NUME and isinstance(v, (int, float)) and isinstance(n, (int, float)) and v != n:
            grupe[(r["setare"], n > v)].append(r)
    linii = [
        "| Schimbarea | Încercări | Din ele, de la zero | Păstrate | Mai bune decât baza (peste prag) "
        "| Cel mai bun câștig față de bază |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for setare in NUME:
        for sus in (True, False):
            g = grupe.get((setare, sus))
            if not g:
                continue
            pastrate = [f"#{r['id']}" for r in g if r["decizie"] == "pastrat"]
            cu_castig = [r for r in g if isinstance(r["fata_de_baza"], (int, float))]
            cel = max(cu_castig, key=lambda r: r["fata_de_baza"], default=None)
            linii.append(
                f"| {NUME[setare]} {'↑' if sus else '↓'} | {len(g)} | {sum(1 for r in g if r['continuat'] is False)} "
                f"| {len(pastrate)}{' (' + ', '.join(pastrate) + ')' if pastrate else ''} "
                f"| {sum(1 for r in cu_castig if r['fata_de_baza'] > prag)} "
                f"| {nr(cel['fata_de_baza'], semn=True) + ' (#' + str(cel['id']) + ': ' + _schimbare(cel) + ')' if cel else '–'} |"
            )
    return linii


def de_la_zero(randuri: list[dict[str, Any]]) -> list[str]:
    """Comparația curată 1: rețetele pornite de la zero au toate exact 5 minute de antrenare."""
    zero = sorted((r for r in randuri if r["continuat"] is False and r["scor"] is not None), key=lambda r: r["scor"])
    linii = ["| Loc | # | Rețeta | Parametri | Pași în 5 minute (simboluri văzute) | val_bpb |",
             "| --- | --- | --- | --- | --- | --- |"]
    for loc, r in enumerate(zero, start=1):
        linii.append(f"| {loc} | {r['id']} | {_reteta(r)} | {_parametri(r)} | {_pasi(r)} | {nr(r['scor'])} |")
    return linii


def din_aceeasi_stare(randuri: list[dict[str, Any]]) -> list[str]:
    """Comparația curată 2: continuările care au pornit din aceeași stare (aceeași arhitectură, același punct)."""
    grupe: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in randuri:
        if r["continuat"] and r["scor"] is not None and r["scor_la_pornire"] is not None:
            t = r["reteta"]
            grupe[(t["n_straturi"], t["n_emb"], t["n_capete"], t["context"], r["scor_la_pornire"])].append(r)
    linii = []
    for (straturi, emb, _, context, start), g in grupe.items():
        if len(g) < 2:
            continue
        variante = "; ".join(
            f"#{r['id']} lot {r['reteta']['lot']}, rata {_val('rata_invatare', r['reteta']['rata_invatare'])} → "
            f"{nr(r['scor'])} ({nr(r['fata_de_stare'], semn=True)})"
            for r in sorted(g, key=lambda r: r["scor"])
        )
        linii.append(f"- {straturi}×{emb} · c{context}, din starea cu {nr(start)}: {variante}")
    return linii or ["- (nicio stare din care să fi pornit mai multe continuări)"]


def _ore(randuri: list[dict[str, Any]]) -> float | None:
    try:
        start = datetime.fromisoformat(randuri[0]["inceput"])
        final = datetime.fromisoformat(randuri[-1]["inceput"]) + timedelta(seconds=randuri[-1]["durata"] or 0)
    except (TypeError, ValueError):
        return None
    return (final - start).total_seconds() / 3600


def raport(fise: list[dict[str, Any]], linie: str, prag: float = 0.005) -> str:
    randuri = randuri_din(fise)
    if not randuri:
        return f"Jurnalul nu are încă experimente pe linia „{linie}”."
    bun = cel_mai_bun(randuri)
    pastrate = [r for r in randuri if r["decizie"] == "pastrat"]
    strangere = next((r["id"] for r in randuri if r["faza"] == "strângere"), None)
    ore = _ore(randuri)
    memorie = [r["memorie_mb"] for r in randuri if isinstance(r["memorie_mb"], (int, float))]
    n = len(randuri)
    linii = [
        f"## Bucla de auto-îmbunătățire: „{linie}”",
        "",
        f"- {n} {de(n)}experimente{' în ' + nr(ore, 1) + ' ore' if ore is not None else ''}; "
        f"{len(pastrate)} păstrate; "
        + (f"lista s-a epuizat înainte de #{strangere}, de acolo a urmat strângerea în jurul celor mai bune 3."
           if strangere else "lista nu s-a epuizat (n-a ajuns la strângere)."),
    ]
    schimbari = [r for r in randuri if r["faza"] != "pornire" and r["scor"] is not None]
    for nume, din_stare in (("continuări (din starea arhitecturii lor)", True), ("rețete pornite de la zero", False)):
        g = [r for r in schimbari if bool(r["continuat"]) == din_stare]
        if g:
            linii.append(f"- Păstrate, dintre {nume}: {sum(1 for r in g if r['decizie'] == 'pastrat')} din {len(g)}.")
    if bun is not None:
        primul = randuri[0]
        linii.append(
            f"- Cel mai bun scor: **{nr(bun['scor'])}** val_bpb (#{bun['id']}: {_reteta(bun)}, {_parametri(bun)}; "
            f"{nr(bun['minute_total'], 0)} minute de antrenare în spate, {mii(bun['pasi_total'])} pași)"
            + (f", față de {nr(primul['scor'])} la punctul de plecare (#{primul['id']}): "
               f"{nr(bun['scor'] - primul['scor'], semn=True)}." if primul["scor"] is not None and primul is not bun else ".")
        )
    if memorie:
        linii.append(f"- Memoria video rezervată, cel mai mult: {mii(max(memorie))} MB.")
    linii += ["", "### Experimentele", "", *tabel(randuri), "",
              "„Câștig” = cât de mult e mai bun decât cea mai bună rețetă de atunci (pozitiv = mai bun); Kronos păstrează "
              f"doar peste pragul de zgomot ({nr(prag, 3)}).", "",
              "### Drumul (rețetele păstrate, în ordine)", ""]
    for r in pastrate:
        linii.append(f"- #{r['id']} ({r['faza']}): {_schimbare(r)} → {nr(r['scor'])}; {_pornire(r)}, "
                     f"{nr(r['minute_total'], 0)} minute în spate")
    linii += ["", f"### Pe setări (amestecat cu minutele în plus de la continuare; prag {nr(prag, 3)})", "",
              *pe_setari(randuri, prag), "",
              "### Comparația curată 1: rețetele pornite de la zero (toate cu exact 5 minute)", "", *de_la_zero(randuri), "",
              "### Comparația curată 2: continuări pornite din aceeași stare", "", *din_aceeasi_stare(randuri)]
    return "\n".join(linii) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default="config/laptop_bucla.toml")
    parser.add_argument("--iesire", default="", help="scrie raportul și în acest fișier (Markdown)")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    config = citeste_config(args.config)
    text = raport(Jurnal(config.director_lucru).istoric(config.nume), config.nume, config.prag_zgomot)
    print(text)
    if args.iesire:
        Path(args.iesire).parent.mkdir(parents=True, exist_ok=True)
        Path(args.iesire).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
