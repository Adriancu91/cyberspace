"""Antrenarea lungă, peste noapte (după bucla cinstită): rețeta câștigătoare, cu continuare, câte un experiment Kronos
pe oră.

Configurarea: config/laptop_antrenare_lunga.toml (rețeta; starea în lucru/antrenare_lunga/gpt.pt). Fiecare oră e un
experiment Kronos: o oră de antrenare din starea de la finalul orei dinainte, apoi examenul oficial și salvarea stării.
Rata de învățare scade singură pe toată durata plănuită (durata_scaderii_secunde din configurare: 8 ore), nu pe fiecare
oră: încălzire în primii 100 de pași, apoi cosinus până la 10%.
Înainte de fiecare oră: pauză și răcire (până la --racire grade); paznicul verifică temperatura, memoria video și
butonul de oprire. Se poate relua: orele făcute se citesc din jurnal. Cât rulează, Windows nu intră în somn.

    python unelte/antrenare_lunga.py --ore 8
    python unelte/antrenare_lunga.py --raport      # doar tabelul și povestea, din orele făcute

Cu --porneste-din <nr. experiment>, prima oră nu pornește de la zero, ci din modelul salvat de Kronos la acel experiment
(greutățile lui): optimizatorul și numărătoarea pașilor pornesc din nou, deci rata repornește (încălzire scurtă, apoi
scădere pe toată durata plănuită). Ce făcuse modelul înainte (ore, pași, text văzut, scor) se ține minte în pornire.json,
lângă stare, și intră în totaluri. Cu --compara-cu <nr. experiment>, povestea de la final se scrie, din același început,
și de modelul acelui experiment, ca să se vadă diferența. Cu --alaturi-de <linie>, la fiecare oră apare și scorul altei
antrenări lungi din aceeași oră, cu diferența, iar la final un verdict cu pragul --prag-alaturi (implicit 0,02: zgomotul
dintre semințe).

Rezultatul: pe ecran și în lucru/<linia>/rezultat.json: scorul pe ore, pașii și textul văzut (în total și de câte ori a
trecut prin tot textul de antrenare), o poveste scrisă de modelul de la final (din starea salvată, dacă Kronos n-a salvat
separat ultima oră, fiind sub pragul de zgomot).

Din 8 octombrie 2026:
- **Retenția R** = faptele noi ale orei ÷ faptele noi la plecare (ale modelului din --porneste-din), la fiecare oră, pe
  ecran, în tabel și în rezultat.json. E doar raportată, nu e criteriu.
- **Prima oră nu mai e păstrată din oficiu:** kronos o judecă cu regula 4 față de modelul de pornire (porneste_din),
  până la primul experiment păstrat al liniei.
- **Hrana e implicită (lecția 6a):** o configurare care nu pomenește deloc `hrana` primește HRANA_IMPLICITA, 5% bucăți
  din poveștile cu fapte în fiecare lot (fișele din jurnal o înregistrează). Fără hrană: `hrana = ""` în configurare.
- **Criteriile sunt implicite (ca în configurarea 7):** o configurare fără niciun [criterii] primește CRITERII_IMPLICITE
  (val_bpb rămâne principalul, cu prag_zgomot, implicit 0,005; fapte_noi nu scad cu peste 10; nota nu scade cu peste
  1,0), doar pentru examenele date la fiecare oră. Fără criterii: un [criterii] gol în configurare.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.cai import gaseste_model  # noqa: E402
from kronos.config import citeste_config  # noqa: E402
from kronos.jurnal import Jurnal  # noqa: E402
from kronos.registru import Registru  # noqa: E402
from unelte.compara_plasa_adaptiva import ruleaza  # noqa: E402

LITERE_PE_SIMBOL = 4.0  # măsurat pe TinyStories, cu tokenizerul BPE de 4.096 de simboluri
# Criteriile din afara examenului oficial (examene_suplimentare), ca coloane: (nume, titlu, lățime).
COLOANE_CRITERII = (("fapte_corecte", "fapte", 5), ("nota_profesor", "nota prof.", 10))
ZECIMALE_CRITERII = (0, 2)
# Examenul de fapte nou (7 octombrie 2026, unelte/examen_fapte_nou.py): coloana lui apare doar când a fost măsurat.
COLOANE_NOI = (("fapte_noi", "fapte noi", 9),)
ZECIMALE_NOI = (0,)
ARHITECTURA = ("n_straturi", "n_capete", "n_emb", "context")
# Din 8 octombrie 2026 (lecția 6a: fără hrană, faptele se uită în prima oră; cu 5% hrană, rămân, cu un cost de ~0,002 la
# val_bpb): hrana implicită a oricărei antrenări lungi care nu pomenește `hrana` în setările modelului.
HRANA_IMPLICITA = {"hrana": "date/fapte/povesti.txt", "fractie_hrana": 0.05}


# Din 8 octombrie 2026 (ca în configurarea 7; pragul notei 1,0, fiindcă 0,5 a respins #261 din zgomot): criteriul →
# (regula, examenul de la oră de care are nevoie). val_bpb rămâne principalul, cu prag_zgomot.
CRITERII_IMPLICITE = {"fapte_noi": ({"mai_mare_e_mai_bine": True, "prag": 10.0}, "fapte_noi"),
                      "nota_profesor": ({"mai_mare_e_mai_bine": True, "prag": 1.0}, "profesor")}
PRAG_ZGOMOT_IMPLICIT = 0.005


def cu_criterii_implicite(config: Any, brut: dict[str, Any]) -> list[str]:
    """Criteriile implicite, dacă fișierul n-are deloc [criterii] (un [criterii] gol = fără criterii), doar pentru
    examenele date la fiecare oră; și prag_zgomot 0,005, dacă fișierul nu-l spune. Întoarce criteriile puse."""
    if "prag_zgomot" not in (brut.get("platforma") or {}):
        config.prag_zgomot = PRAG_ZGOMOT_IMPLICIT
    if "criterii" in brut:
        return []
    examene = config.setari_port("model").get("examene_suplimentare") or []
    puse = [nume for nume, (_, examen) in CRITERII_IMPLICITE.items() if examen in examene]
    config.criterii = {nume: dict(CRITERII_IMPLICITE[nume][0]) for nume in puse}
    return puse


def cu_hrana_implicita(config: Any) -> bool:
    """Pune HRANA_IMPLICITA în setările modelului, dacă ele nu pomenesc `hrana` (nici goală). True dacă a pus-o."""
    setari = config.porturi["model"].setdefault("setari", {})
    if "hrana" in setari or setari.get("memorie"):  # hrana nu merge (încă) cu memoria ierarhică
        return False
    setari.update(HRANA_IMPLICITA)
    return True


def tine_treaz(da: bool) -> None:
    """Windows: cât rulează, laptopul nu intră în somn (cererea se anulează oricum când procesul se termină)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        es_continuous, es_system_required = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(es_continuous | (es_system_required if da else 0))
    except (AttributeError, OSError):
        pass


def ore_din_jurnal(fise: list[dict[str, Any]], scor_principal: str) -> list[dict[str, Any]]:
    """Câte un rând pe oră (experimentele reușite ale liniei, în ordine), cu textul văzut adunat de la început."""
    ore: list[dict[str, Any]] = []
    simboluri_total = 0
    for fisa in fise:
        if fisa.get("decizie") not in ("pastrat", "respins"):
            continue
        model = fisa["setari"]["model"]
        s = fisa.get("statistici_antrenare") or {}
        simboluri = s["pasi"] * model["lot"] * model["context"]
        simboluri_total += simboluri
        ore.append({
            "ora": len(ore) + 1, "experiment": fisa["id"], "scor": fisa["scoruri"][scor_principal], "pasi": s["pasi"],
            "pasi_total": s.get("pasi_total"), "minute_total": s.get("minute_total"), "simboluri": simboluri,
            "simboluri_total": simboluri_total,
            "treceri_prin_text": simboluri_total / s["simboluri_antrenare"] if s.get("simboluri_antrenare") else None,
            "rata_la_final": s.get("rata_la_final"), "memorie_rezervata_mb": s.get("memorie_rezervata_mb"),
            "decizie": fisa["decizie"], "model_salvat": fisa.get("model_salvat"), "criterii": criterii_din(fisa),
        })
    return ore


def criterii_din(fisa: dict[str, Any]) -> dict[str, float]:
    """Criteriile suplimentare ale orei (examene_suplimentare): cu [criterii], în fișă; fără, în răspunsul dupa_examen."""
    criterii = fisa.get("criterii") or (fisa.get("dupa_examen") or {}).get("criterii") or {}
    return {k: v for k, v in criterii.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}


def masuratori_examene(jurnal: Any, experiment: int) -> dict[str, float]:
    """Ultimele măsurători din afara examenului oficial pentru modelul experimentului dat (unelte/examen_fapte.py și
    unelte/examen_profesor.py), ca punct de plecare al unei antrenări care pornește din el."""
    rezultat: dict[str, float] = {}
    for linie, cheie, nume in (("examen_fapte", "corecte_doar_cuvantul_din_fapt", "fapte_corecte"),
                               ("examen_fapte_nou", "fapte_noi", "fapte_noi"),
                               ("examen_profesor", "nota_medie", "nota_profesor")):
        fise = [f for f in jurnal.istoric(linie)
                if ((f.get("module") or {}).get("elev") or {}).get("experiment") == experiment
                and isinstance((f.get("scoruri") or {}).get(cheie), (int, float))]
        if fise:
            rezultat[nume] = fise[-1]["scoruri"][cheie]
    return rezultat


def punct_de_plecare(jurnal: Any, inainte: dict[str, Any] | None) -> dict[str, Any] | None:
    """Scorurile modelului din care pornește linia: scorul oficial, criteriile din fișa lui (examenele de la oră) și,
    peste ele, măsurătorile uneltelor de examen (mai noi). None fără --porneste-din."""
    if not inainte:
        return None
    fisa = next((f for f in jurnal.istoric() if f.get("id") == inainte["experiment"]), {})
    return {"scor": inainte["scor"], **criterii_din(fisa), **masuratori_examene(jurnal, inainte["experiment"])}


def retentia(criterii: dict[str, Any], pornire: dict[str, Any] | None) -> float | None:
    """R = faptele noi acum ÷ faptele noi la plecare (doar raportat, nu e criteriu); None dacă lipsește una."""
    acum, la_plecare = criterii.get("fapte_noi"), (pornire or {}).get("fapte_noi")
    if not isinstance(acum, (int, float)) or not isinstance(la_plecare, (int, float)) or la_plecare <= 0:
        return None
    return round(acum / la_plecare, 3)


def coloanele(ore: list[dict[str, Any]], pornire: dict[str, Any] | None) -> list[tuple[str, str, int, int]]:
    """Coloanele criteriilor (nume, titlu, lățime, zecimale): faptele și nota mereu; fapte_noi doar dacă e măsurat."""
    puncte = [o["criterii"] for o in ore] + ([pornire] if pornire else [])
    vechi = [(n, t, l, z) for (n, t, l), z in zip(COLOANE_CRITERII, ZECIMALE_CRITERII)]
    noi = [(n, t, l, z) for (n, t, l), z in zip(COLOANE_NOI, ZECIMALE_NOI) if any(n in p for p in puncte)]
    return vechi[:1] + noi + vechi[1:]


def corelatii(ore: list[dict[str, Any]], pornire: dict[str, Any] | None) -> dict[str, float | None]:
    """Legătura (Pearson) dintre val_bpb și fiecare criteriu, pe ore (cu punctul de plecare): −1 = când val_bpb scade,
    criteriul urcă mereu; 0 = nicio legătură. None dacă sunt mai puțin de 3 puncte sau criteriul nu se schimbă."""
    puncte = ([{"scor": pornire["scor"], "criterii": pornire}] if pornire else []) + ore
    rezultat: dict[str, float | None] = {}
    for nume, _, _, _ in coloanele(ore, pornire):
        perechi = [(p["scor"], p["criterii"][nume]) for p in puncte if nume in p["criterii"]]
        try:
            rezultat[nume] = round(statistics.correlation(*zip(*perechi)), 2) if len(perechi) >= 3 else None
        except statistics.StatisticsError:
            rezultat[nume] = None
    return rezultat


def _celula(valoare: Any, latime: int, zecimale: int) -> str:
    return f"{valoare:>{latime}.{zecimale}f}" if isinstance(valoare, (int, float)) else f"{'–':>{latime}}"


def tabel(ore: list[dict[str, Any]], alaturi: dict[int, float] | None = None,
          pornire: dict[str, Any] | None = None) -> list[str]:
    """Tabelul pe ore; cu alaturi (scorul altei antrenări la aceeași oră), și scorul acela și diferența; cu criterii
    (examene_suplimentare), faptele corecte și nota profesorului; cu pornire, întâi rândul punctului de plecare."""
    coloane = coloanele(ore, pornire)
    cu_criterii = any(nume in o["criterii"] for o in ore for nume, _, _, _ in coloane) or bool(
        pornire and any(nume in pornire for nume, _, _, _ in coloane))
    cu_r = any(retentia(o["criterii"], pornire) is not None for o in ore)
    cap = f"{'ora':>3}  {'val_bpb':>7}"
    if cu_criterii:
        cap += "".join(f"  {titlu:>{latime}}" for _, titlu, latime, _ in coloane)
    cap += f"  {'R':>5}" if cu_r else ""
    cap += f"  {'alături':>7}  {'diferența':>9}" if alaturi is not None else ""
    linii = [cap + f"  {'pași':>7}  {'pași total':>10}  {'text văzut':>10}  {'treceri':>7}  {'rata la final':>13}  "
                   f"{'memorie':>8}"]
    if pornire:
        rand = f"{0:>3}  {pornire['scor']:>7.4f}"
        if cu_criterii:
            rand += "".join(f"  {_celula(pornire.get(nume), latime, zecimale)}" for nume, _, latime, zecimale in coloane)
        rand += f"  {1:>5.2f}" if cu_r else ""
        linii.append(rand + "  (punctul de plecare)")
    for o in ore:
        rand = f"{o['ora']:>3}  {o['scor']:>7.4f}"
        if cu_criterii:
            rand += "".join(f"  {_celula(o['criterii'].get(nume), latime, zecimale)}"
                            for nume, _, latime, zecimale in coloane)
        if cu_r:
            rand += f"  {_celula(retentia(o['criterii'], pornire), 5, 2)}"
        if alaturi is not None:
            ref = alaturi.get(o["ora"])
            rand += f"  {ref:>7.4f}  {o['scor'] - ref:>+9.4f}" if ref is not None else f"  {'–':>7}  {'–':>9}"
        linii.append(rand + f"  {o['pasi']:>7,}  {o['pasi_total'] or 0:>10,}  {o['simboluri_total'] / 1e6:>8.0f} M  "
                            f"{o['treceri_prin_text'] or 0:>7.1f}  {o['rata_la_final'] or 0:>13.6f}  "
                            f"{o['memorie_rezervata_mb'] or 0:>5} MB")
    return linii


def verdict_alaturi(ore: list[dict[str, Any]], alaturi: dict[int, float], linie: str, prag: float) -> str | None:
    """Ultima oră de acum față de aceeași oră a celeilalte antrenări, cu pragul dat (ex. zgomotul dintre semințe)."""
    ultima = ore[-1]
    ref = alaturi.get(ultima["ora"])
    if ref is None:
        return None
    dif = ultima["scor"] - ref
    text = f"la ora {ultima['ora']}: {ultima['scor']:.4f} față de {ref:.4f} („{linie}”), diferența {dif:+.4f}, pragul {prag}"
    if dif < -prag:
        return f"MAI BUN, peste prag: {text}."
    if dif > prag:
        return f"MAI SLAB, peste prag: {text}."
    return f"ÎN ZGOMOT (nu se poate spune care e mai bun): {text}."


def poveste(config: Any, fisa: dict[str, Any], inceput: str, lungime: int) -> str:
    """O poveste scrisă de modelul salvat la experimentul dat (ca python -m kronos scrie)."""
    model = Registru().creeaza("model", config.porturi["model"]["modul"], fisa["setari"]["model"]).instanta
    model.incarca(gaseste_model(fisa["model_salvat"], config.director_lucru))
    return inceput + model.genereaza(inceput, lungime)


def poveste_din_stare(config: Any, fisa: dict[str, Any], cale_stare: Path, inceput: str, lungime: int) -> str:
    """O poveste scrisă de modelul din starea de la final (după ultima oră, chiar dacă Kronos n-a salvat-o separat, fiind
    sub pragul de zgomot): rețeaua și tokenizerul vin din modelul salvat la experimentul dat, greutățile din stare."""
    import torch

    model = Registru().creeaza("model", config.porturi["model"]["modul"], fisa["setari"]["model"]).instanta
    model.incarca(gaseste_model(fisa["model_salvat"], config.director_lucru))
    model.retea.load_state_dict(torch.load(cale_stare, map_location=model.dispozitiv, weights_only=True)["retea"])
    return inceput + model.genereaza(inceput, lungime)


def fisa_experimentului(jurnal: Any, id_experiment: int) -> dict[str, Any]:
    fisa = next((f for f in jurnal.istoric() if f["id"] == id_experiment), None)
    if fisa is None or not fisa.get("model_salvat"):
        raise ValueError(f"Experimentul #{id_experiment} nu există în jurnal sau n-are un model salvat de Kronos.")
    return fisa


def stare_de_pornire(config: Any, jurnal: Any, id_experiment: int, scor_principal: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Starea de pornire din modelul salvat de Kronos la experimentul dat: greutățile lui, un optimizator nou și
    numărătoarea de la zero (rata repornește). Plus ce făcuse modelul înainte, pe linia lui, până la acel experiment."""
    import torch

    fisa = fisa_experimentului(jurnal, id_experiment)
    setari = config.setari_port("model")
    model = Registru().creeaza("model", config.porturi["model"]["modul"], {**setari, "dispozitiv": "cpu"}).instanta
    asteptat = {k: setari[k] for k in ARHITECTURA}
    model.incarca(gaseste_model(fisa["model_salvat"], config.director_lucru))
    if {k: model.setari[k] for k in ARHITECTURA} != asteptat:
        raise ValueError(f"Modelul experimentului #{id_experiment} are altă arhitectură ({model.setari}) decât rețeta "
                         f"din configurare ({asteptat}).")
    optimizator = torch.optim.AdamW(model.retea.parameters(), lr=model.rata_invatare, weight_decay=0.1)
    linia = [f for f in jurnal.istoric(fisa["linie"]) if f["id"] <= id_experiment]
    ore = ore_din_jurnal(linia, scor_principal)
    statistici = fisa.get("statistici_antrenare") or {}
    inainte = {
        "experiment": id_experiment, "linie": fisa["linie"], "ore": len(ore), "scor": fisa["scoruri"][scor_principal],
        "pasi": statistici.get("pasi_total", sum(o["pasi"] for o in ore)), "minute": statistici.get("minute_total"),
        "simboluri": ore[-1]["simboluri_total"] if ore else 0,
    }
    stare = {"setari": model.setari, "retea": model.retea.state_dict(), "optimizator": optimizator.state_dict(),
             "pasi_total": 0, "minute": 0.0, "scor": inainte["scor"]}
    return stare, inainte


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Antrenarea lungă: câte un experiment Kronos pe oră, cu continuare.")
    parser.add_argument("--config", default="config/laptop_antrenare_lunga.toml")
    parser.add_argument("--ore", type=int, default=8, help="câte ore de antrenare, în total (cu cele deja făcute)")
    parser.add_argument("--pauza", type=float, default=60, help="pauza dintre ore, în secunde")
    parser.add_argument("--racire", type=float, default=70, help="înainte de fiecare oră, aștept placa până la atâtea grade")
    parser.add_argument("--raport", action="store_true", help="nu antrena; doar tabelul și povestea, din orele făcute")
    parser.add_argument("--inceput", default="Once upon a time", help="începutul poveștii de la final")
    parser.add_argument("--lungime", type=int, default=600, help="câte litere scrie modelul")
    parser.add_argument("--porneste-din", type=int, default=None, help="prima oră pornește din modelul acestui experiment")
    parser.add_argument("--compara-cu", type=int, default=None, help="povestea se scrie și de modelul acestui experiment")
    parser.add_argument("--alaturi-de", default="", help="linia altei antrenări: scorul ei la aceeași oră, alături")
    parser.add_argument("--prag-alaturi", type=float, default=0.02, help="pragul verdictului față de cealaltă antrenare")
    args = parser.parse_args(argv)

    config = citeste_config(args.config)
    hrana_implicita = cu_hrana_implicita(config)
    criterii_implicite = cu_criterii_implicite(config, tomllib.loads(Path(args.config).read_text(encoding="utf-8")))
    examen = Registru().creeaza("examen", config.porturi["examen"]["modul"], config.setari_port("examen")).instanta
    jurnal = Jurnal(config.director_lucru)
    facute = len(ore_din_jurnal(jurnal.istoric(config.nume), examen.scor_principal))
    cale_stare = Path(config.setari_port("model").get("cale_stare") or "fara_stare.pt")
    fisier_pornire = cale_stare.with_name("pornire.json")
    if args.porneste_din is not None and not args.raport and facute == 0 and not cale_stare.exists():
        if not config.setari_port("model").get("cale_stare"):
            print("--porneste-din cere un cale_stare în configurare (acolo se scrie starea de pornire).", flush=True)
            return 1
        from module.model_continuu import salveaza_atomic

        stare, inainte = stare_de_pornire(config, jurnal, args.porneste_din, examen.scor_principal)
        salveaza_atomic(stare, cale_stare)
        fisier_pornire.write_text(json.dumps(inainte, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Pornesc din modelul experimentului #{inainte['experiment']} (linia „{inainte['linie']}”, ora "
              f"{inainte['ore']}, val_bpb {inainte['scor']:.4f}): optimizatorul și rata pornesc din nou. Până la primul "
              f"experiment păstrat al liniei, regula 4 o judecă față de el.", flush=True)
    inainte = json.loads(fisier_pornire.read_text(encoding="utf-8")) if fisier_pornire.exists() else None
    if inainte:  # kronos: până la primul experiment păstrat al liniei, regula 4 o judecă față de modelul de pornire
        config.porneste_din = inainte["experiment"]
    pornire = punct_de_plecare(jurnal, inainte)
    alaturi = ({o["ora"]: o["scor"] for o in ore_din_jurnal(jurnal.istoric(args.alaturi_de), examen.scor_principal)}
               if args.alaturi_de else None)
    if not args.raport and facute < args.ore:
        reteta = config.setari_port("model")
        print(f"Antrenarea lungă: orele {facute + 1}–{args.ore}, rețeta {reteta['n_straturi']}×{reteta['n_emb']}, context "
              f"{reteta['context']}, lot {reteta['lot']}, rata {reteta['rata_invatare']:g} care scade pe "
              f"{reteta.get('durata_scaderii_secunde', 0) / 3600:g} ore (linia „{config.nume}”).", flush=True)
        if config.buget_antrenare_secunde != 3600:
            print(f"   Aici o „oră” e un experiment de {config.buget_antrenare_secunde / 60:g} minute de antrenare "
                  f"(cu examenele după el).", flush=True)
        if reteta.get("hrana"):
            print(f"   Fiecare lot: {reteta.get('fractie_hrana', 0):.0%} bucăți din {reteta['hrana']}, restul din "
                  f"textul de antrenare." + (" Hrana e cea implicită (configurarea n-o pomenește; fără ea: hrana = \"\")."
                                             if hrana_implicita else ""), flush=True)
        if criterii_implicite:
            print(f"   Criteriile sunt cele implicite (configurarea n-are [criterii]; fără criterii: un [criterii] gol): "
                  f"val_bpb principal (prag {config.prag_zgomot:g}), "
                  + ", ".join(f"{n} nu scade cu peste {config.criterii[n]['prag']:g}" for n in criterii_implicite) + ".",
                  flush=True)
        tine_treaz(True)
        try:
            for ora in range(facute + 1, args.ore + 1):
                rulare = ruleaza(
                    config, config.nume, f"antrenare lungă, ora {ora} din {args.ore}", {"samanta": reteta.get("samanta", 0)},
                    pauza=0 if ora == facute + 1 else args.pauza, racire=args.racire, cu_fisa=True,
                )
                if rulare is None:
                    break
                criterii = criterii_din(rulare.pop("fisa"))
                ref = (alaturi or {}).get(ora)
                r = retentia(criterii, pornire)
                print(f"   ora {ora}: val_bpb {rulare['scor']:.4f}"
                      + (f" (alături, „{args.alaturi_de}”: {ref:.4f}, diferența {rulare['scor'] - ref:+.4f})" if ref else "")
                      + (f", fapte {criterii['fapte_corecte']:g}" if "fapte_corecte" in criterii else "")
                      + (f", fapte noi {criterii['fapte_noi']:g}" if "fapte_noi" in criterii else "")
                      + (f" (R {r:.2f})" if r is not None else "")
                      + (f", nota profesorului {criterii['nota_profesor']:g}" if "nota_profesor" in criterii else "")
                      + f", {rulare['pasi']:,} de pași ({rulare['pasi_pe_secunda']} pași/s), la {datetime.now():%H:%M}",
                      flush=True)
        finally:
            tine_treaz(False)

    ore = ore_din_jurnal(jurnal.istoric(config.nume), examen.scor_principal)
    if not ore:
        print("Nicio oră făcută încă.", flush=True)
        return 1
    print("\n=== Antrenarea lungă: scorul pe ore (val_bpb, mai mic = mai bine) ===")
    if alaturi is not None:
        print(f"„alături” = scorul antrenării „{args.alaturi_de}” la aceeași oră; diferența = acum − alături.")
    for o in ore:
        o["retentie"] = retentia(o["criterii"], pornire)
    print("\n".join(tabel(ore, alaturi, pornire)))
    legaturi = corelatii(ore, pornire)
    if any(v is not None for v in legaturi.values()):
        print("\nLegătura cu val_bpb, pe ore (−1: când val_bpb scade, urcă și ea mereu; 0: nicio legătură): "
              + ", ".join(f"{nume} {v:+.2f}" for nume, v in legaturi.items() if v is not None) + ".")
    verdict = verdict_alaturi(ore, alaturi, args.alaturi_de, args.prag_alaturi) if alaturi else None
    if verdict:
        print(f"\nFață de „{args.alaturi_de}”: {verdict}")
    ultima = ore[-1]
    print(f"\nÎn aceste ore: {ultima['pasi_total']:,} de pași, {ultima['simboluri_total'] / 1e6:,.0f} M de simboluri "
          f"văzute (≈ {ultima['simboluri_total'] * LITERE_PE_SIMBOL / 1e9:.1f} miliarde de litere), adică de "
          f"{ultima['treceri_prin_text'] or 0:.1f} ori tot textul de antrenare.")
    total = None
    if inainte:
        total = {"pasi": inainte["pasi"] + ultima["pasi_total"], "simboluri": inainte["simboluri"] + ultima["simboluri_total"]}
        print(f"Cu cele {inainte['ore']} ore de dinainte (până la experimentul #{inainte['experiment']}, linia "
              f"„{inainte['linie']}”): {total['pasi']:,} de pași, {total['simboluri'] / 1e6:,.0f} M de simboluri "
              f"(≈ {total['simboluri'] * LITERE_PE_SIMBOL / 1e9:.1f} miliarde de litere).")
    cu_model = [o for o in ore if o["model_salvat"]]
    text, ora_povestii = None, None
    if cu_model:
        fisa = next(f for f in jurnal.istoric(config.nume) if f["id"] == cu_model[-1]["experiment"])
        if ore[-1]["model_salvat"] or not cale_stare.exists():
            text, ora_povestii = poveste(config, fisa, args.inceput, args.lungime), cu_model[-1]["ora"]
        else:  # ultima oră n-a fost salvată separat (sub pragul de zgomot): povestea o scrie starea de la final
            text, ora_povestii = poveste_din_stare(config, fisa, cale_stare, args.inceput, args.lungime), ore[-1]["ora"]
    elif inainte and cale_stare.exists():
        # Nicio oră păstrată (din 8 octombrie, prima oră se judecă față de modelul de pornire): povestea o scrie starea
        # de la final, cu rețeaua construită după modelul de pornire (aceeași arhitectură, verificată la pornire).
        fisa = fisa_experimentului(jurnal, inainte["experiment"])
        text, ora_povestii = poveste_din_stare(config, fisa, cale_stare, args.inceput, args.lungime), ore[-1]["ora"]
    if text is not None:
        print(f"\nPovestea modelului de după ora {ora_povestii}:\n{text}")
    comparatie = None
    if args.compara_cu is not None:
        comparatie = poveste(config, fisa_experimentului(jurnal, args.compara_cu), args.inceput, args.lungime)
        print(f"\nAceeași poveste, scrisă de modelul experimentului #{args.compara_cu}:\n{comparatie}")
    iesire = config.director_lucru / config.nume / "rezultat.json"
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps({
        "data": datetime.now().isoformat(timespec="seconds"), "linie": config.nume, "reteta": config.setari_port("model"),
        "ore": ore, "litere_pe_simbol": LITERE_PE_SIMBOL, "inainte": inainte, "total": total,
        "alaturi": {"linie": args.alaturi_de, "scoruri": alaturi, "prag": args.prag_alaturi, "verdict": verdict}
        if alaturi is not None else None,
        "pornire": pornire, "corelatii": legaturi,
        "poveste": {"ora": ora_povestii, "inceput": args.inceput, "text": text} if text else None,
        "poveste_comparatie": {"experiment": args.compara_cu, "text": comparatie} if comparatie else None,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSalvat în {iesire}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
