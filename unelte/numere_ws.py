"""Text cu numere pentru amestecul workstation-ului: calcule, date, prețuri, măsuri, ordine, numere în propoziții.

De ce: tokenizer-ul nou are numerele 0–999 ca simboluri întregi, iar modelul trebuie să le vadă în multe feluri de
text, nu în câteva tipare repetate. Tot ce scrie e adevărat (calculele, zilele săptămânii, transformările de măsuri,
numerele scrise în litere), în română și în engleză. Textul e împărțit în bucăți mici, despărțite de „<|endoftext|>”,
fiecare cu rânduri de mai multe feluri. Aceeași sămânță dă același text.

    from unelte.numere_ws import text_numere
    text = text_numere(1_000_000)
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Callable

SEPARATOR = "<|endoftext|>"

# --- numere în litere ---------------------------------------------------------------------------------------------

_UNITATI_RO = ["zero", "unu", "doi", "trei", "patru", "cinci", "șase", "șapte", "opt", "nouă", "zece", "unsprezece",
               "doisprezece", "treisprezece", "paisprezece", "cincisprezece", "șaisprezece", "șaptesprezece",
               "optsprezece", "nouăsprezece"]
_ZECI_RO = ["", "", "douăzeci", "treizeci", "patruzeci", "cincizeci", "șaizeci", "șaptezeci", "optzeci", "nouăzeci"]
_SUTE_RO = ["", "o sută", "două sute", "trei sute", "patru sute", "cinci sute", "șase sute", "șapte sute", "opt sute",
            "nouă sute"]
_UNITATI_EN = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
               "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_ZECI_EN = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
LUNI_RO = ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie", "august", "septembrie", "octombrie",
           "noiembrie", "decembrie"]
LUNI_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"]
ZILE_RO = ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "duminică"]
ZILE_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ORDINALE_RO = ["primul", "al doilea", "al treilea", "al patrulea", "al cincilea", "al șaselea", "al șaptelea",
               "al optulea", "al nouălea", "al zecelea"]


def in_litere_ro(n: int) -> str:
    """0–999 în română, forma de numărat: 21 = „douăzeci și unu”, 345 = „trei sute patruzeci și cinci”."""
    if not 0 <= n <= 999:
        raise ValueError("doar 0–999")
    sute, rest = divmod(n, 100)
    if rest < 20:
        coada = _UNITATI_RO[rest] if rest or not sute else ""
    else:
        zeci, unitati = divmod(rest, 10)
        coada = _ZECI_RO[zeci] + (f" și {_UNITATI_RO[unitati]}" if unitati else "")
    return " ".join(p for p in (_SUTE_RO[sute], coada) if p)


def in_litere_en(n: int) -> str:
    """0–999 în engleză: 21 = „twenty-one”, 345 = „three hundred forty-five”."""
    if not 0 <= n <= 999:
        raise ValueError("doar 0–999")
    sute, rest = divmod(n, 100)
    if rest < 20:
        coada = _UNITATI_EN[rest] if rest or not sute else ""
    else:
        zeci, unitati = divmod(rest, 10)
        coada = _ZECI_EN[zeci] + (f"-{_UNITATI_EN[unitati]}" if unitati else "")
    return " ".join(p for p in (f"{_UNITATI_EN[sute]} hundred" if sute else "", coada) if p)


def ordinal_en(n: int) -> str:
    """1st, 2nd, 3rd, 4th, 11th, 12th, 13th, 21st, 112th."""
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def cu_de(n: int, substantiv: str) -> str:
    """„5 mere”, „20 de mere”, „101 mere”, „120 de mere”: „de” de la 20 în sus, în afară de cele terminate în 01–19."""
    return f"{n} de {substantiv}" if n >= 20 and not 1 <= n % 100 <= 19 else f"{n} {substantiv}"


def mii_ro(n: int) -> str:
    return f"{n:,}".replace(",", ".")


# --- felurile de rânduri ---------------------------------------------------------------------------------------------

LUCRURI = [("apples", "mere"), ("books", "cărți"), ("cats", "pisici"), ("stars", "stele"), ("days", "zile"),
           ("trees", "copaci"), ("birds", "păsări"), ("cars", "mașini"), ("houses", "case"), ("flowers", "flori"),
           ("pencils", "creioane"), ("chairs", "scaune"), ("eggs", "ouă"), ("coins", "monede"), ("pages", "pagini"),
           ("boxes", "cutii"), ("steps", "trepte"), ("windows", "ferestre"), ("stones", "pietre"), ("letters", "scrisori")]
NUME = ["Ana", "Mihai", "Ioana", "Andrei", "Maria", "Tom", "Lily", "Sam", "Mia", "Ben", "Elena", "Radu", "Sara", "Max"]
PRODUSE = [("a loaf of bread", "o pâine"), ("a notebook", "un caiet"), ("a ticket", "un bilet"), ("a toy", "o jucărie"),
           ("a coffee", "o cafea"), ("a pen", "un pix"), ("a book", "o carte"), ("a ball", "o minge")]


def _calcule(r: random.Random) -> str:
    a, b, c = r.randint(0, 999), r.randint(0, 999), r.randint(2, 12)
    fel = r.randrange(16)
    if fel == 0:
        return f"{a} + {b} = {a + b}"
    if fel == 1:
        a, b = max(a, b), min(a, b)
        return f"{a} - {b} = {a - b}"
    if fel == 2:
        a, b = r.randint(0, 99), r.randint(0, 99)
        return f"{a} {r.choice(['*', 'x', '×'])} {b} = {a * b}"
    if fel == 3:
        b = r.randint(1, 99)
        return f"{a * b} {r.choice(['/', ':', '÷'])} {b} = {a}"
    if fel == 4:
        return f"{a} + {b} + {c} = {a + b + c}"
    if fel == 5:
        a, b = r.randint(1, 99), r.randint(1, 99)
        return f"({a} + {b}) * {c} = {(a + b) * c}, dar {a} + {b} * {c} = {a + b * c}"
    if fel == 6:
        procent, intreg = r.choice([10, 20, 25, 50, 75]), r.choice([20, 40, 60, 80, 100, 120, 200, 360, 480, 800])
        return (f"{procent}% din {intreg} = {procent * intreg // 100}" if r.random() < 0.5
                else f"{procent}% of {intreg} is {procent * intreg // 100}")
    if fel == 7:
        b = r.randint(2, 19)
        return f"{a} = {b} * {a // b} + {a % b}; {a} // {b} = {a // b}; {a} % {b} = {a % b}"
    if fel == 8:
        a = r.randint(0, 31)
        return f"{a}² = {a * a}" if r.random() < 0.5 else f"{a} ** 2 == {a * a}"
    if fel == 9:
        return f"x = {a}\ny = {b}\nprint(x + y)  # {a + b}\nprint(x * 2)  # {a * 2}"
    if fel == 10:
        a = r.randint(0, 499)
        return (f"Dublul lui {a} este {a * 2}. Jumătatea lui {a * 2} este {a}." if r.random() < 0.5
                else f"Double {a} is {a * 2}. Half of {a * 2} is {a}.")
    if fel == 11:
        a, b = r.randint(1, 12), r.randint(1, 12)
        return (f"{a} ori {b} fac {a * b}" if r.random() < 0.5 else f"{a} times {b} is {a * b}")
    if fel == 12:
        return f"{a} < {a + b + 1}, {a + b + 1} > {a}, {a} == {a}, {a} != {a + c}, {min(a, b)} <= {max(a, b)}"
    if fel == 13:
        valori = [r.randint(0, 99) for _ in range(r.randint(3, 6))]
        return f"sum({valori}) = {sum(valori)}; max = {max(valori)}; min = {min(valori)}; len = {len(valori)}"
    if fel == 14:
        a, b = max(a, b), min(a, b)
        return (f"Diferența dintre {a} și {b} este {a - b}, iar suma lor este {a + b}." if r.random() < 0.5
                else f"The difference between {a} and {b} is {a - b}, and their sum is {a + b}.")
    return f"{a} + {b} = {b} + {a} = {a + b}; {a} + 0 = {a}; {a} * 1 = {a}; {a} * 0 = 0"


def _date(r: random.Random) -> str:
    zi = date(1900, 1, 1) + timedelta(days=r.randint(0, 51_000))  # 1900–2039
    fel = r.randrange(8)
    if fel == 0:
        return f"{zi.day} {LUNI_RO[zi.month - 1]} {zi.year} a fost într-o zi de {ZILE_RO[zi.weekday()]}."
    if fel == 1:
        return f"{LUNI_EN[zi.month - 1]} {zi.day}, {zi.year} was a {ZILE_EN[zi.weekday()]}."
    if fel == 2:
        return f"{zi.day:02d}.{zi.month:02d}.{zi.year} = {zi.isoformat()} = {zi.day} {LUNI_RO[zi.month - 1]} {zi.year}"
    if fel == 3:
        peste = r.randint(1, 60)
        dupa = zi + timedelta(days=peste)
        return (f"La {peste} zile după {zi.day} {LUNI_RO[zi.month - 1]} {zi.year} este {dupa.day} "
                f"{LUNI_RO[dupa.month - 1]} {dupa.year}.")
    if fel == 4:
        an2 = zi.year + r.randint(1, 80)
        return (f"Din {zi.year} până în {an2} au trecut {an2 - zi.year} ani." if r.random() < 0.5
                else f"From {zi.year} to {an2} is {an2 - zi.year} years.")
    if fel == 5:
        ore, minute, plus = r.randint(0, 23), r.randint(0, 59), r.randint(1, 180)
        total = (ore * 60 + minute + plus) % (24 * 60)
        return f"{ore:02d}:{minute:02d} + {plus} min = {total // 60:02d}:{total % 60:02d}"
    if fel == 6:
        luna = r.randint(1, 12)
        zile = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][luna - 1]
        return (f"Luna {LUNI_RO[luna - 1]} este luna {luna} din an și are {zile} zile"
                + (" (29 în anii bisecți)." if luna == 2 else "."))
    varsta = r.randint(1, 99)
    return (f"{r.choice(NUME)} s-a născut în {zi.year}. În {zi.year + varsta} avea {varsta} ani." if r.random() < 0.5
            else f"{r.choice(NUME)} was born in {zi.year}. In {zi.year + varsta} they were {varsta} years old.")


def _preturi(r: random.Random) -> str:
    lei, bani, bucati = r.randint(1, 199), r.choice([0, 0, 50, 99, 25, 75, 10]), r.randint(2, 12)
    en, ro = r.choice(PRODUSE)
    fel = r.randrange(6)
    total_bani = (lei * 100 + bani) * bucati
    if fel == 0:
        return (f"{ro.capitalize()} costă {lei},{bani:02d} lei. {bucati} bucăți costă "
                f"{total_bani // 100},{total_bani % 100:02d} lei.")
    if fel == 1:
        return f"{en.capitalize()} costs ${lei}.{bani:02d}. {bucati} of them cost ${total_bani // 100}.{total_bani % 100:02d}."
    if fel == 2:
        platit = (lei // 50 + 1) * 50
        return f"Am plătit cu {platit} lei pentru ceva de {lei} lei și am primit rest {platit - lei} lei."
    if fel == 3:
        reducere = r.choice([10, 20, 25, 50])
        pret = r.choice([20, 40, 60, 80, 100, 120, 200, 400])
        return (f"Preț: {pret} lei. Reducere {reducere}%: {pret * reducere // 100} lei. Preț nou: "
                f"{pret - pret * reducere // 100} lei.")
    if fel == 4:
        a, b, c = r.randint(1, 99), r.randint(1, 99), r.randint(1, 99)
        return f"{a} lei + {b} lei + {c} lei = {a + b + c} lei; {a} € + {b} € = {a + b} €; {a} RON"
    return (f"{r.choice(NUME)} are {lei} lei și cheltuiește {min(lei, bucati * 3)} lei. Îi rămân "
            f"{lei - min(lei, bucati * 3)} lei.")


def _masuri(r: random.Random) -> str:
    a, b = r.randint(1, 999), r.randint(1, 99)
    fel = r.randrange(9)
    if fel == 0:
        return f"{a} km = {mii_ro(a * 1000)} m; {b} m = {b * 100} cm; {b} cm = {b * 10} mm"
    if fel == 1:
        return f"{a} kg = {mii_ro(a * 1000)} g; {b} kg {a} g = {mii_ro(b * 1000 + a)} g"
    if fel == 2:
        return f"{b} l = {mii_ro(b * 1000)} ml; {a * 10} ml = {a // 100},{a % 100:02d} l"
    if fel == 3:
        return f"{b} ore = {b * 60} minute = {mii_ro(b * 3600)} secunde; {a} minute = {a // 60} h {a % 60} min"
    if fel == 4:
        return f"{b} hours = {b * 60} minutes; {a} minutes = {a // 60} h {a % 60} min; {b} weeks = {b * 7} days"
    if fel == 5:
        lat, lung = r.randint(1, 60), r.randint(1, 60)
        return (f"Un dreptunghi de {lat} m pe {lung} m are aria {lat * lung} m² și perimetrul {2 * (lat + lung)} m."
                if r.random() < 0.5 else
                f"A {lat} m by {lung} m rectangle has an area of {lat * lung} m² and a perimeter of {2 * (lat + lung)} m.")
    if fel == 6:
        viteza, ore = r.choice([4, 5, 12, 20, 50, 60, 80, 90, 100, 120]), r.randint(1, 9)
        return (f"Cu {viteza} km/h, în {ore} ore se parcurg {viteza * ore} km." if r.random() < 0.5
                else f"At {viteza} km/h, you travel {viteza * ore} km in {ore} hours.")
    if fel == 7:
        t1, t2 = r.randint(-20, 35), r.randint(-20, 35)
        return f"Dimineața erau {t1} °C, iar la prânz {t2} °C: o diferență de {abs(t2 - t1)} grade."
    return f"{a} cm = {a // 100} m {a % 100} cm; {a} g; {b} t = {mii_ro(b * 1000)} kg"


def _ordine(r: random.Random) -> str:
    fel = r.randrange(9)
    valori = r.sample(range(0, 1000), r.randint(4, 8))
    if fel == 0:
        return f"{valori} sortat crescător: {sorted(valori)}"
    if fel == 1:
        return f"sorted({valori}, reverse=True) == {sorted(valori, reverse=True)}"
    if fel == 2:
        return f"Cel mai mare dintre {', '.join(map(str, valori))} este {max(valori)}, iar cel mai mic este {min(valori)}."
    if fel == 3:
        start, pas = r.randint(0, 200), r.randint(1, 25)
        sir = [start + pas * k for k in range(r.randint(5, 10))]
        return f"{', '.join(map(str, sir))}, ... (din {pas} în {pas}); urmează {sir[-1] + pas}"
    if fel == 4:
        n = r.randint(1, 998)
        return (f"Înainte de {n} vine {n - 1}, iar după {n} vine {n + 1}." if r.random() < 0.5
                else f"{n - 1} comes before {n}, and {n + 1} comes after {n}.")
    if fel == 5:
        copii = r.sample(NUME, 4)
        return ("La cursă: " + ", ".join(f"{ORDINALE_RO[k]} {nume}" for k, nume in enumerate(copii)) + ". "
                + f"{copii[0]} a fost pe locul 1, iar {copii[3]} pe locul 4.")
    if fel == 6:
        n = r.randint(1, 130)
        return f"{ordinal_en(n)}, {ordinal_en(n + 1)}, {ordinal_en(n + 2)}; the {ordinal_en(n)} comes before the {ordinal_en(n + 1)}"
    if fel == 7:
        n = r.randint(0, 999)
        return (f"{n} este un număr {'par' if n % 2 == 0 else 'impar'}; {n + 1} este {'par' if n % 2 else 'impar'}."
                if r.random() < 0.5 else
                f"{n} is {'even' if n % 2 == 0 else 'odd'}; {n + 1} is {'even' if n % 2 else 'odd'}.")
    start = r.randint(1, 990)
    return " ".join(str(k) for k in range(start, start + r.randint(5, 12)))


def _propozitii(r: random.Random) -> str:
    a, b = r.randint(2, 999), r.randint(2, 999)
    en, ro = r.choice(LUCRURI)
    nume = r.choice(NUME)
    fel = r.randrange(12)
    if fel == 0:
        return f"{a} = {in_litere_ro(a)} = {in_litere_en(a)}"
    if fel == 1:
        return f"{in_litere_ro(a).capitalize()} se scrie {a}. {in_litere_en(b).capitalize()} is written {b}."
    if fel == 2:
        return f"{nume} are {cu_de(a, ro)} și mai primește {cu_de(b, ro)}. Acum are {cu_de(a + b, ro)}."
    if fel == 3:
        return f"{nume} has {a} {en} and gets {b} more. Now {nume} has {a + b} {en}."
    if fel == 4:
        a, b = max(a, b) + 2, min(a, b)  # rămân cel puțin 2: fără „1 mere”
        return f"Erau {cu_de(a, ro)}. Au dispărut {cu_de(b, ro)}. Au rămas {cu_de(a - b, ro)}."
    if fel == 5:
        randuri, pe_rand = r.randint(2, 30), r.randint(2, 30)
        return (f"Sunt {cu_de(randuri, 'rânduri')} cu câte {cu_de(pe_rand, ro)}: în total {cu_de(randuri * pe_rand, ro)}."
                if r.random() < 0.5 else
                f"There are {randuri} rows of {pe_rand} {en}: {randuri * pe_rand} {en} in all.")
    if fel == 6:
        mare = r.randint(1000, 99_999_999)
        return f"Orașul are {mii_ro(mare)} locuitori. The city has {mare:,} people. Fără separatori: {mare}."
    if fel == 7:
        etaj, etaje = r.randint(1, 40), r.randint(41, 120)
        return f"Blocul are {cu_de(etaje, 'etaje')}. {nume} stă la etajul {etaj}, cu {etaje - etaj} etaje sub ultimul."
    if fel == 8:
        pagini, citite = r.randint(50, 900), r.randint(1, 49)
        return (f"Cartea are {cu_de(pagini, 'pagini')}. După {cu_de(citite, 'pagini')} citite, mai rămân "
                f"{cu_de(pagini - citite, 'pagini')}.")
    if fel == 9:
        copii, fiecare = r.randint(2, 12), r.randint(1, 20)
        return (f"{cu_de(copii * fiecare, ro).capitalize()} se împart la {copii} copii: fiecare primește {fiecare}."
                if r.random() < 0.5 else
                f"{copii * fiecare} {en} are shared by {copii} children: each one gets {fiecare}.")
    if fel == 10:
        return f"Numărul {a} are cifrele {', '.join(str(a))}; suma cifrelor este {sum(int(c) for c in str(a))}."
    return f"{a} rotunjit la zeci este {(a + 5) // 10 * 10}; la sute este {(a + 50) // 100 * 100}."


FELURI: list[tuple[str, Callable[[random.Random], str], float]] = [
    ("calcule", _calcule, 0.30), ("date", _date, 0.14), ("preturi", _preturi, 0.12), ("masuri", _masuri, 0.14),
    ("ordine", _ordine, 0.14), ("propozitii", _propozitii, 0.16),
]


def text_numere(octeti: int, samanta: int = 0) -> str:
    """Cel puțin `octeti` de text cu numere, în bucăți de 6–30 de rânduri amestecate, despărțite de „<|endoftext|>”."""
    r = random.Random(samanta)
    functii, greutati = [f for _, f, _ in FELURI], [g for _, _, g in FELURI]
    parti: list[str] = []
    marime = 0
    while marime < octeti:
        randuri = [r.choices(functii, greutati)[0](r) for _ in range(r.randint(6, 30))]
        bucata = "\n".join(randuri) + f"\n{SEPARATOR}\n"
        parti.append(bucata)
        marime += len(bucata.encode("utf-8"))
    return "".join(parti)
