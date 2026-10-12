"""Antrenează tokenizer-ul workstation-ului: BPE pe octeți, 16.384 de simboluri, regulile „ws” (module/tokenizer_bpe.py).

Planul e în docs/MUTARE_workstation.md, secțiunea 5. Învață dintr-un amestec, măsurat în octeți:
~45% engleză simplă (TinyStories), ~35% română, ~15% cod Python, ~5% numere și calcule scrise în text.
Învață doar din textele de ANTRENARE (date/ws/curat/*/antrenare.txt și date/tinystories_tot/antrenare.txt); validarea
fiecărei surse e folosită doar la verificările de la final.

Cum se face amestecul: din fiecare sursă se numără bucățile unui eșantion (felii luate de peste tot din fișier), în
paralel, iar numărătorile se înmulțesc astfel încât fiecare categorie să aibă partea ei din total. Apoi, ca un cuvânt
să rămână întreg și fără spațiu în față (după ghilimele sau paranteze), forma fără spațiu primește FARA_SPATIU din
aparițiile formei cu spațiu.

    python unelte/antreneaza_tokenizer_ws.py                      # → date/ws/bpe_16384.json
    python unelte/antreneaza_tokenizer_ws.py --verifica           # doar verificările, pe tokenizer-ul deja făcut
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.tokenizer_bpe import TokenizerBPE, antreneaza_din_frecvente, frecvente_bucati  # noqa: E402

CURAT = Path("date/ws/curat")
# categoria → (partea din amestec, {sursa: partea ei din categorie})
AMESTEC: dict[str, tuple[float, dict[str, float]]] = {
    "engleza_simpla": (0.45, {"date/tinystories_tot/antrenare.txt": 1.0}),
    "romana": (0.35, {"wikipedia_ro": 0.30, "fineweb2_ro": 0.30, "fabule_ro": 0.20, "wikisource_ro": 0.10,
                      "europarl_en_ro": 0.08, "tatoeba_en_ro": 0.02}),
    "cod": (0.15, {"cod_stack": 0.90, "cod_instruct": 0.10}),
    "numere": (0.05, {"numere": 1.0}),
}
ESANTION_MO = 400.0   # cel mult atâția megaocteți numărați din fiecare sursă
NUMERE_OCTETI = 260_000_000  # cât text cu numere se generează (5% din amestecul de antrenare de ~5 GB)
FELIE = 8 << 20       # o felie de numărat (8 MB)
FARA_SPATIU = 0.30    # cât din aparițiile lui „ cuvânt” primește forma „cuvânt” (ales pe 12 octombrie: 0,1 rupe „moon”)
FRECVENTA_MINIMA = 2.0


def text_numere(octeti: int, samanta: int = 0) -> str:
    """Numere și calcule scrise în text, în engleză și română: adunări, scăderi, înmulțiri, liste, prețuri, ore, ani,
    numere mari cu grupe de trei cifre. Calculele sunt corecte."""
    r = random.Random(samanta)
    lucruri = [("apples", "mere"), ("books", "cărți"), ("cats", "pisici"), ("stars", "stele"), ("days", "zile"),
               ("children", "copii"), ("trees", "copaci"), ("birds", "păsări")]
    randuri: list[str] = []
    marime = 0
    while marime < octeti:
        a, b = r.randint(0, 999), r.randint(0, 999)
        en, ro = r.choice(lucruri)
        fel = r.randrange(14)
        if fel == 0:
            rand = f"{a} + {b} = {a + b}"
        elif fel == 1:
            a, b = max(a, b), min(a, b)
            rand = f"{a} - {b} = {a - b}"
        elif fel == 2:
            a, b = r.randint(0, 99), r.randint(0, 99)
            rand = f"{a} * {b} = {a * b}"
        elif fel == 3:
            b = r.randint(1, 99)
            rand = f"{a * b} / {b} = {a}"
        elif fel == 4:
            rand = f"x = {a}\ny = {b}\nprint(x + y)  # {a + b}"
        elif fel == 5:
            rand = f"There are {a} {en} and {b} more {en}. Now there are {a + b} {en}."
        elif fel == 6:
            rand = f"Sunt {a} {ro} și încă {b} {ro}. Acum sunt {a + b} {ro}."
        elif fel == 7:
            start, pas = r.randint(0, 50), r.randint(1, 12)
            rand = ", ".join(str(start + pas * k) for k in range(r.randint(4, 10)))
        elif fel == 8:
            rand = f"{r.randint(1, 500)}.{r.randint(0, 99):02d} lei, {r.randint(1, 500)},{r.randint(0, 99):02d} kg, {r.randint(1, 100)}%"
        elif fel == 9:
            rand = f"{r.randint(0, 23):02d}:{r.randint(0, 59):02d}, {r.randint(1, 28)}.{r.randint(1, 12):02d}.{r.randint(1900, 2030)}"
        elif fel == 10:
            mare = r.randint(1000, 99_999_999)
            rand = f"{mare} = {mare:,} = " + f"{mare:,}".replace(",", ".")
        elif fel == 11:
            rand = f"({a} + {b}) * 2 = {(a + b) * 2}; [{a}, {b}, {a + b}]; f({a}) = {a * 2}"
        elif fel == 12:
            rand = f"In {r.randint(1500, 2026)}, {a} {en} cost {b} coins. În {r.randint(1500, 2026)} erau {a} {ro}."
        else:
            rand = f"{a} < {a + b + 1}, {a + b + 1} > {b}, {a} == {a}, {a} != {a + 1}"
        randuri.append(rand)
        marime += len(rand.encode("utf-8")) + 1
    return "\n".join(randuri) + "\n"


def scrie_numere(fisier: Path) -> None:
    """Textul cu numere, generat o singură dată (aceeași sămânță, deci același text); refăcut dacă e prea mic."""
    if not fisier.exists() or fisier.stat().st_size < NUMERE_OCTETI:
        fisier.parent.mkdir(parents=True, exist_ok=True)
        fisier.write_text(text_numere(NUMERE_OCTETI), encoding="utf-8", newline="\n")


def cale_sursa(sursa: str) -> Path:
    return Path(sursa) if sursa.endswith(".txt") else CURAT / sursa / "antrenare.txt"


def felii(cale: Path, megaocteti: float) -> list[tuple[str, int, int]]:
    """Felii de câte FELIE octeți, la distanțe egale prin tot fișierul, până la `megaocteti` în total."""
    marime = cale.stat().st_size
    cate = max(1, min(int(megaocteti * 1e6 // FELIE) or 1, -(-marime // FELIE)))
    pas = marime / cate
    return [(str(cale), int(k * pas), min(FELIE, marime - int(k * pas))) for k in range(cate)]


def numara_felia(felie: tuple[str, int, int]) -> tuple[Counter[str], int]:
    cale, start, cat = felie
    with open(cale, "rb") as f:
        f.seek(start)
        octeti = f.read(cat)
    # o felie începe și se termină la un sfârșit de rând, ca să nu taie o literă sau un cuvânt
    inceput = 0 if start == 0 else octeti.find(b"\n") + 1
    sfarsit = octeti.rfind(b"\n") + 1 or len(octeti)
    text = octeti[inceput:sfarsit].decode("utf-8", errors="ignore")
    return frecvente_bucati(text, reguli="ws"), len(text.encode("utf-8"))


def numara_amestecul(procese: int) -> tuple[dict[str, float], dict[str, Any]]:
    """Tabelul bucată → apariții (înmulțite cu partea fiecărei categorii) și ce a intrat în el."""
    (CURAT / "numere").mkdir(parents=True, exist_ok=True)
    fisier_numere = CURAT / "numere" / "antrenare.txt"
    scrie_numere(fisier_numere)
    frecvente: dict[str, float] = {}
    info: dict[str, Any] = {}
    with ProcessPoolExecutor(procese) as grup:
        for categorie, (parte, surse) in AMESTEC.items():
            pe_surse: dict[str, tuple[Counter[str], int]] = {}
            for sursa in surse:
                cale = cale_sursa(sursa)
                if not cale.exists():
                    print(f"   {sursa}: lipsește, o sar", flush=True)
                    continue
                numarate: Counter[str] = Counter()
                octeti = 0
                for c, n in grup.map(numara_felia, felii(cale, ESANTION_MO)):
                    numarate.update(c)
                    octeti += n
                pe_surse[sursa] = (numarate, octeti)
                print(f"   {categorie} / {sursa}: {octeti / 1e6:,.0f} MB numărați, {len(numarate):,} bucăți diferite", flush=True)
            parti = sum(surse[s] for s in pe_surse)
            for sursa, (numarate, octeti) in pe_surse.items():
                # fiecare octet numărat din sursă cântărește cât partea sursei în amestec: părțile ies în octeți
                greutate = parte * surse[sursa] / parti / octeti * 1e9
                for bucata, n in numarate.items():
                    frecvente[bucata] = frecvente.get(bucata, 0.0) + n * greutate
                info[sursa] = {"categorie": categorie, "parte_din_amestec": round(parte * surse[sursa] / parti, 4),
                               "megaocteti_numarati": round(octeti / 1e6, 1)}
    return frecvente, info


def cu_forma_fara_spatiu(frecvente: dict[str, float], parte: float = FARA_SPATIU) -> dict[str, float]:
    rezultat = dict(frecvente)
    for bucata, n in frecvente.items():
        if len(bucata) > 2 and bucata[0] == " " and bucata[1:].isalpha():
            rezultat[bucata[1:]] = rezultat.get(bucata[1:], 0.0) + n * parte
    return {b: n for b, n in rezultat.items() if n >= FRECVENTA_MINIMA}


def cuvinte_dese(cale: Path, cate: int, octeti: int = 30_000_000) -> list[str]:
    """Cele mai dese `cate` cuvinte (cu cel puțin 3 litere) din începutul unui text."""
    with cale.open("rb") as f:
        text = f.read(octeti).decode("utf-8", errors="ignore")
    numarate = Counter(b[1:] for b in frecvente_bucati(text, reguli="ws").elements() if b[0] == " " and len(b) > 3 and b[1:].isalpha())
    return [c for c, _ in numarate.most_common(cate)]


def acoperire(tok: TokenizerBPE, cuvinte: list[str]) -> dict[str, Any]:
    """Din cuvintele date: câte sunt o singură bucată cu spațiu în față și câte fără spațiu (după ghilimele)."""
    cu = sum(len(tok.codifica(" " + c)) == 1 for c in cuvinte)
    fara = sum(len(tok.codifica(c)) == 1 for c in cuvinte)
    fara_2 = sum(len(tok.codifica(c)) <= 2 for c in cuvinte)
    return {"cuvinte": len(cuvinte), "o_bucata_cu_spatiu": cu, "o_bucata_fara_spatiu": fara,
            "cel_mult_2_bucati_fara_spatiu": fara_2}


def bucati(tok: TokenizerBPE, text: str) -> list[str]:
    return [tok.octeti(s).decode("utf-8", errors="replace") for s in tok.codifica(text)]


def verifica(cale: Path, cale_vechi: Path, iesire: Path | None) -> int:
    """Verificările cerute (12 octombrie 2026), cu exemple; pe validare, nu pe textele din care a învățat."""
    nou, vechi = TokenizerBPE.incarca(cale), TokenizerBPE.incarca(cale_vechi)
    r: dict[str, Any] = {"tokenizer": cale.as_posix(), "simboluri": nou.marime, "exemple": {}, "surse": {}}
    exemple = ['46', 'x = 46', '37 + 58 = 95', '1234', '19053815', '"moon"', 'The word is "moon".', '(moon)', "print(moon)",
               'He said, "Look at the moon!"', "Pisica doarme pe covor, iar câinele aleargă prin grădină.",
               'def aduna(a, b):\n    return a + b', "Ştefan şi Ţuţu"]
    for text in exemple:
        r["exemple"][text] = {"nou": bucati(nou, text), "vechi": bucati(vechi, text)}
    numere_intregi = all(len(nou.codifica(str(k))) == 1 for k in range(1000))
    moon = bucati(nou, '"moon"')
    r["verificari"] = {
        "46_e_o_bucata": bucati(nou, "46") == ["46"],
        "numerele_0_999_sunt_o_bucata": numere_intregi,
        "1234_e_123_si_4": bucati(nou, "1234") == ["123", "4"],
        "moon_intre_ghilimele_bucati": moon, "moon_intre_ghilimele_numar": len(moon),
        "cuvantul_moon_fara_spatiu_bucati": bucati(nou, "moon"),
    }
    for sursa in ["wikipedia_ro", "wikisource_ro", "fineweb2_ro", "fabule_ro", "europarl_en_ro", "tatoeba_en_ro",
                  "cod_instruct", "cod_stack", "date/tinystories_r2/validare.txt"]:
        fisier = Path(sursa) if sursa.endswith(".txt") else CURAT / sursa / "validare.txt"
        if not fisier.exists():
            continue
        with fisier.open("rb") as f:
            octeti = f.read(2_000_000)
        text = octeti[: octeti.rfind(b"\n") + 1].decode("utf-8", errors="ignore")
        cod_nou, cod_vechi = nou.codifica(text), vechi.codifica(text)
        r["surse"][sursa] = {
            "octeti": len(text.encode("utf-8")), "bucati_nou": len(cod_nou), "bucati_vechi": len(cod_vechi),
            "mai_putine_cu_procent": round(100 * (1 - len(cod_nou) / len(cod_vechi)), 1),
            "octeti_pe_bucata_nou": round(len(text.encode("utf-8")) / len(cod_nou), 2),
            "octeti_pe_bucata_vechi": round(len(text.encode("utf-8")) / len(cod_vechi), 2),
            "se_rescrie_exact": nou.decodeaza(cod_nou) == text,
        }
    romana = [s for s in ("wikipedia_ro", "wikisource_ro", "fineweb2_ro", "fabule_ro") if s in r["surse"]]
    if romana:
        a = sum(r["surse"][s]["bucati_nou"] for s in romana)
        b = sum(r["surse"][s]["bucati_vechi"] for s in romana)
        r["verificari"]["romana_mai_putine_bucati_procent"] = round(100 * (1 - a / b), 1)
        r["verificari"]["romana_cel_putin_30_la_suta"] = a <= 0.7 * b
    r["verificari"]["toate_se_rescriu_exact"] = all(s["se_rescrie_exact"] for s in r["surse"].values())
    r["acoperire"] = {}
    for nume, sursa in (("engleza_simpla_cele_mai_dese_2000", "date/tinystories_tot/antrenare.txt"),
                        ("romana_cele_mai_dese_2000", "wikipedia_ro")):
        if cale_sursa(sursa).exists():
            r["acoperire"][nume] = acoperire(nou, cuvinte_dese(cale_sursa(sursa), 2000))
    text = json.dumps(r, ensure_ascii=False, indent=1)
    print(text)
    if iesire:
        iesire.parent.mkdir(parents=True, exist_ok=True)
        iesire.write_text(text, encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Antrenează tokenizer-ul workstation-ului (regulile „ws”).")
    parser.add_argument("--marime", type=int, default=16384)
    parser.add_argument("--destinatie", default="date/ws/bpe_16384.json")
    parser.add_argument("--vechi", default="date/tinystories/bpe_4096.json", help="tokenizer-ul cu care se compară")
    parser.add_argument("--procese", type=int, default=16)
    parser.add_argument("--fara-spatiu", type=float, default=FARA_SPATIU,
                        help="cât din aparițiile lui „ cuvânt” primește forma fără spațiu „cuvânt”")
    parser.add_argument("--verifica", action="store_true", help="doar verificările, pe tokenizer-ul deja făcut")
    parser.add_argument("--iesire-verificare", default="lucru/tokenizer_ws_verificare.json")
    args = parser.parse_args(argv)
    destinatie = Path(args.destinatie)
    if not args.verifica:
        start = time.perf_counter()
        print("Număr bucățile amestecului...", flush=True)
        frecvente, info = numara_amestecul(args.procese)
        numarat = time.perf_counter() - start
        de_invatat = cu_forma_fara_spatiu(frecvente, args.fara_spatiu)
        print(f"Numărat în {numarat:.0f} s: {len(frecvente):,} bucăți diferite; învăț din {len(de_invatat):,} "
              f"(cele cu cel puțin {FRECVENTA_MINIMA:g} apariții, cu formele fără spațiu). Învăț {args.marime:,} simboluri...",
              flush=True)
        tok = antreneaza_din_frecvente(de_invatat, args.marime, reguli="ws")
        tok.salveaza(destinatie, {
            "facut": time.strftime("%Y-%m-%d %H:%M"), "reguli": "ws", "amestec": info, "fara_spatiu": args.fara_spatiu,
            "frecventa_minima": FRECVENTA_MINIMA, "esantion_mo_pe_sursa": ESANTION_MO,
            "secunde_numarat": round(numarat), "secunde_invatat": round(time.perf_counter() - start - numarat),
        })
        print(f"Gata în {(time.perf_counter() - start) / 60:.1f} minute: {destinatie} ({tok.marime:,} simboluri), "
              f"sha256 {hashlib.sha256(destinatie.read_bytes()).hexdigest()[:16]}…", flush=True)
    return verifica(destinatie, Path(args.vechi), Path(args.iesire_verificare) if args.iesire_verificare else None)


if __name__ == "__main__":
    raise SystemExit(main())
