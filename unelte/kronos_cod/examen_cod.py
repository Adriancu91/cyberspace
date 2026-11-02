"""Examenul de cod al lui Kronos-Cod (S41, C-28, 28 octombrie 2026), scris ÎNAINTE de date și de antrenare.

Probleme mici în Python, din 20 de șabloane scrise de mână (niciuna de la un LLM străin). Fiecare șablon are
variante (alți parametri în enunț, alt nume de funcție); fiecare problemă = enunțul (antetul funcției + docstring,
în engleză, ca în codul pe care va învăța modelul), corpul de referință și testele (`assert`-uri cu valorile
calculate din referință). Modelul primește enunțul și scrie corpul; programul `enunt + corp` rulează în cutie
(`unelte/kronos_cod/cutie.py`) cu testele.

- setul de probă: sămânța 0, câte o variantă pe șablon (20 de probleme), pentru teste și exemple;
- setul ascuns: sămânță aleasă la întâmplare O DATĂ, ținută doar în `lucru/kronos_cod/examen_ascuns/` (nu în Git),
  10 variante pe șablon (200 de probleme), fără variantele setului de probă. În Git: doar SHA-256 și numărul.
- nota: pass@1 și pass@10 cu estimatorul fără deplasare (n răspunsuri pe problemă, c corecte):
  pass@k = 1 − C(n − c, k) / C(n, k).

Comenzile:
    python unelte/kronos_cod/examen_cod.py proba                      # arată o problemă din setul de probă
    python unelte/kronos_cod/examen_cod.py ascuns --dosar lucru/kronos_cod/examen_ascuns   # o singură dată
    python unelte/kronos_cod/examen_cod.py verifica --dosar lucru/kronos_cod/examen_ascuns

Răspunsurile modelului (S60, pentru S58): `model` scrie, din modelul salvat, n corpuri pe problemă (temperatura fixă,
sămânța fixă, oprire la primul rând care nu mai e în corpul funcției sau la --max-simboluri); `noteaza` le dă cutiei
prin `noteaza` (neschimbată) și scrie pass@1 și pass@10. Ambele refuză să scrie peste un fișier care există.
S62: `model` scrie câte `--lot` corpuri odată (implicit 2), fiecare corp cu sămânța lui (aceleași răspunsuri oricare ar
fi lotul), și se oprește singur (cod 3, fișier marcat „incomplet”) dacă placa trece de `--memorie-max` (implicit 6500 MB).
    python unelte/kronos_cod/examen_cod.py model --config config/cod_c1.toml --stare lucru/cod_c1/gpt.pt \
        --set ascuns --iesire lucru/kronos_cod/raspunsuri_cod_c1.json
    python unelte/kronos_cod/examen_cod.py noteaza --raspunsuri lucru/kronos_cod/raspunsuri_cod_c1.json \
        --nota lucru/kronos_cod/nota_cod_c1.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import secrets
import string
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

RADACINA = Path(__file__).resolve().parents[2]
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from unelte.kronos_cod import memorie_placa  # noqa: E402
from unelte.kronos_cod.cutie import ruleaza  # noqa: E402

VARIANTE_ASCUNSE = 10
SAMANTA_PROBA = 0
CORP_GOL = "    pass\n"
CORP_GRESIT = "    return None\n"


@dataclass
class Problema:
    id: str
    sablon: str
    varianta: str
    functie: str
    enunt: str
    referinta: str
    teste: list

    def program(self, corp: str) -> str:
        return self.enunt + corp


# ---------------------------------------------------------------------------------------------------- șabloanele
# Fiecare șablon: (rng) -> dict cu cheie (ce face varianta unică), nume (variante de nume), argumente, doc, corp,
# și intrari(rng) -> listă de tupluri de argumente pentru teste.

def _ints(rng, n_max=12, lo=-50, hi=50):
    return [rng.randint(lo, hi) for _ in range(rng.randint(0, n_max))]


def _litere(rng, n_max=20, alfabet=string.ascii_letters + "  "):
    return "".join(rng.choice(alfabet) for _ in range(rng.randint(0, n_max)))


def s01_divizibile(rng):
    k = rng.randint(2, 12)
    fel = rng.choice(["sum", "count"])
    expr = "x" if fel == "sum" else "1"
    return dict(
        cheie=(k, fel), nume=[f"{fel}_divisible_by_{k}", f"{fel}_multiples", f"{fel}_of_multiples_of_{k}"],
        argumente="xs",
        doc=f"Return the {'sum' if fel == 'sum' else 'number'} of the integers in `xs` that are divisible by {k}.",
        corp=f"    return sum({expr} for x in xs if x % {k} == 0)\n",
        intrari=lambda r: [([],), ([k, 2 * k, -k, 1],)] + [(_ints(r),) for _ in range(6)])


def s02_caractere(rng):
    car = "".join(sorted(rng.sample(string.ascii_lowercase, rng.randint(3, 6))))
    fara_caz = rng.random() < 0.5
    return dict(
        cheie=(car, fara_caz), nume=["count_chars", "count_selected", "char_count"], argumente="s",
        doc=f"Return how many characters of `s` are one of the characters in {car!r}"
            + (", ignoring case." if fara_caz else " (case-sensitive)."),
        corp=f"    return sum(1 for c in s{'.lower()' if fara_caz else ''} if c in {car!r})\n",
        intrari=lambda r: [("",), (car + car.upper(),)] + [(_litere(r),) for _ in range(6)])


def s03_inverseaza_bucati(rng):
    sep = rng.choice([" ", ",", ";", "-"])
    unire = rng.choice([" ", ",", ";", "-"])
    def intrari(r):
        cuv = lambda: "".join(r.choice(string.ascii_lowercase) for _ in range(r.randint(1, 5)))  # noqa: E731
        return [("",), (cuv(),)] + [(sep.join(cuv() for _ in range(r.randint(2, 6))),) for _ in range(6)]
    return dict(
        cheie=(sep, unire), nume=["reverse_pieces", "reverse_words", "flip_order"], argumente="s",
        doc=f"Split `s` on {sep!r}, reverse the order of the pieces and join them back with {unire!r}.",
        corp=f"    return {unire!r}.join(reversed(s.split({sep!r})))\n", intrari=intrari)


def s04_fizz(rng):
    a, b = rng.sample(range(2, 8), 2)
    wa, wb = rng.sample(["Fizz", "Buzz", "Bang", "Ping", "Pong", "Zap", "Boom"], 2)
    return dict(
        cheie=(a, b, wa, wb), nume=["fizz_list", "number_words", "game_sequence"], argumente="n",
        doc=f"Return a list of strings for the numbers 1..n: {wa + wb!r} if the number is divisible by both {a} and "
            f"{b}, {wa!r} if only by {a}, {wb!r} if only by {b}, otherwise the number itself as a string.",
        corp=("    out = []\n    for i in range(1, n + 1):\n        s = ''\n"
              f"        if i % {a} == 0:\n            s += {wa!r}\n        if i % {b} == 0:\n            s += {wb!r}\n"
              "        out.append(s or str(i))\n    return out\n"),
        intrari=lambda r: [(0,), (1,), (a * b,)] + [(r.randint(2, 30),) for _ in range(4)])


def s05_recurenta(rng):
    a0, a1 = rng.randint(0, 5), rng.randint(0, 5)
    c1, c2 = rng.randint(1, 3), rng.randint(1, 3)
    m = rng.choice([97, 1000, 10007, 1_000_007])
    return dict(
        cheie=(a0, a1, c1, c2, m), nume=["sequence_value", "recurrence", "nth_term"], argumente="n",
        doc=f"A sequence is defined by f(0) = {a0}, f(1) = {a1} and f(n) = {c1} * f(n - 1) + {c2} * f(n - 2). "
            f"Return f(n) modulo {m} for a non-negative integer n.",
        corp=(f"    a, b = {a0}, {a1}\n    for _ in range(n):\n        a, b = b, {c1} * b + {c2} * a\n"
              f"    return a % {m}\n"),
        intrari=lambda r: [(0,), (1,), (2,)] + [(r.randint(3, 80),) for _ in range(5)])


def s06_palindrom(rng):
    fel = rng.choice(["spaces", "alnum", "letters"])
    caz = rng.random() < 0.5
    minim = rng.randint(1, 4)
    cond = {"spaces": "c != ' '", "alnum": "c.isalnum()", "letters": "c.isalpha()"}[fel]
    descriere = {"spaces": "removing all spaces", "alnum": "keeping only letters and digits",
                 "letters": "keeping only letters"}[fel]
    def intrari(r):
        out = [("",), ("a",)]
        for _ in range(6):
            jum = _litere(r, 6, "abcAB1 ,")
            out.append((jum + jum[::-1] if r.random() < 0.6 else jum,))
        return out
    return dict(
        cheie=(fel, caz, minim), nume=["is_palindrome", "reads_same_both_ways", "palindrome_check"], argumente="s",
        doc=f"Return True if `s` reads the same forwards and backwards after {descriere}"
            + (" and ignoring case" if caz else "") + f", and the cleaned text has at least {minim} characters; "
            "otherwise return False.",
        corp=(f"    t = [c{'.lower()' if caz else ''} for c in s if {cond}]\n"
              f"    return len(t) >= {minim} and t == t[::-1]\n"),
        intrari=intrari)


def s07_roteste(rng):
    k = rng.randint(1, 7)
    sens = rng.choice(["left", "right"])
    taie = f"{k} % len(xs)" if sens == "left" else f"len(xs) - {k} % len(xs)"
    return dict(
        cheie=(k, sens), nume=["rotate", "rotate_list", "shift_items"], argumente="xs",
        doc=f"Return a new list with the elements of `xs` rotated {sens} by {k} positions (elements that fall off "
            "one end come back at the other end).",
        corp=f"    if not xs:\n        return []\n    k = {taie}\n    return xs[k:] + xs[:k]\n",
        intrari=lambda r: [([],), ([1],), (list(range(k + 2)),)] + [(_ints(r, 10),) for _ in range(5)])


def s08_cezar(rng):
    k = rng.randint(1, 25)
    mari = rng.random() < 0.5
    corp = ("    out = []\n    for c in s:\n        if 'a' <= c <= 'z':\n"
            f"            out.append(chr((ord(c) - 97 + {k}) % 26 + 97))\n")
    if mari:
        corp += f"        elif 'A' <= c <= 'Z':\n            out.append(chr((ord(c) - 65 + {k}) % 26 + 65))\n"
    corp += "        else:\n            out.append(c)\n    return ''.join(out)\n"
    return dict(
        cheie=(k, mari), nume=["caesar", "shift_letters", "encode"], argumente="s",
        doc=f"Shift every {'letter' if mari else 'lowercase letter a-z'} of `s` forward by {k} positions in the "
            "alphabet, wrapping around after 'z'" + (" (and after 'Z', keeping the case)" if mari else "")
            + ". All other characters stay unchanged.",
        corp=corp, intrari=lambda r: [("",), ("xyz XYZ",)] + [(_litere(r, 20, string.ascii_letters + " .!"),)
                                                            for _ in range(6)])


def s09_comprimare(rng):
    ordine = rng.choice(["count_first", "char_first"])
    unu = rng.random() < 0.5
    sep = rng.choice(["", "-", ","])
    mic = rng.random() < 0.5
    numar = "(str(n) if n > 1 else '')" if unu else "str(n)"
    expr = f"{numar} + s[i]" if ordine == "count_first" else f"s[i] + {numar}"
    return dict(
        cheie=(ordine, unu, sep, mic), nume=["compress", "run_length", "encode_runs"], argumente="s",
        doc=("Run-length encode `s`" + (" after converting it to lowercase" if mic else "") + ": each maximal run "
             "of the same character becomes " + ("the run length followed by the character"
                                                  if ordine == "count_first" else "the character followed by the run length")
             + (", but runs of length 1 are written as the character alone" if unu else "")
             + f". Join the encoded runs with {sep!r}."),
        corp=(("    s = s.lower()\n" if mic else "") + "    out = []\n    i = 0\n    while i < len(s):\n        j = i\n"
              "        while j < len(s) and s[j] == s[i]:\n            j += 1\n        n = j - i\n"
              f"        out.append({expr})\n        i = j\n    return {sep!r}.join(out)\n"),
        intrari=lambda r: [("",), ("a",), ("aaAbbb",)] + [(_litere(r, 14, "aabbcA"),) for _ in range(5)])


def s10_al_k_lea(rng):
    k = rng.randint(2, 4)
    d = rng.choice([-1, 0, -999])
    sens = rng.choice(["largest", "smallest"])
    return dict(
        cheie=(k, d, sens), nume=[f"kth_{sens}", f"{sens}_distinct", "pick_distinct"], argumente="xs",
        doc=f"Return the {k}-th {sens} distinct value in `xs`, or {d} if `xs` has fewer than {k} distinct values.",
        corp=(f"    vals = sorted(set(xs), reverse={sens == 'largest'})\n"
              f"    return vals[{k - 1}] if len(vals) >= {k} else {d}\n"),
        intrari=lambda r: [([],), ([5] * 4,), (list(range(k)),)] + [(_ints(r, 10, -9, 9),) for _ in range(5)])


def s11_doua_liste(rng):
    op = rng.choice(["all", "union", "both", "exactly_one", "only_first"])
    jos = rng.random() < 0.5
    m = rng.choice([None, 3, 5])
    expr = {"all": "a + b", "union": "set(a) | set(b)", "both": "set(a) & set(b)",
            "exactly_one": "set(a) ^ set(b)", "only_first": "set(a) - set(b)"}[op]
    ce = {"all": "all elements of both lists (keeping duplicates)", "union": "the distinct elements found in a or b",
          "both": "the distinct elements found in both a and b",
          "exactly_one": "the distinct elements found in exactly one of the two lists",
          "only_first": "the distinct elements of a that are not in b"}[op]
    return dict(
        cheie=(op, jos, m), nume=["combine_sorted", "merge_lists", "list_ops"], argumente="a, b",
        doc=f"Given two lists of integers, return a list of {ce}, sorted in {'descending' if jos else 'ascending'} "
            "order" + (f"; return only the first {m} elements of that list." if m else "."),
        corp=f"    out = sorted({expr}, reverse={jos})\n    return out{f'[:{m}]' if m else ''}\n",
        intrari=lambda r: [([], []), ([1, 2, 2], [])] + [(_ints(r, 8, 0, 9), _ints(r, 8, 0, 9)) for _ in range(6)])


def s12_matrice(rng):
    fel = rng.choice(["row", "column", "diagonal", "anti"])
    i = rng.randint(0, 2)
    agr = rng.choice(["sum", "max", "squares"])
    elem = {"row": f"m[{i}]", "column": f"[r[{i}] for r in m]", "diagonal": "[m[j][j] for j in range(len(m))]",
            "anti": "[m[j][len(m) - 1 - j] for j in range(len(m))]"}[fel]
    ce = {"row": f"row {i}", "column": f"column {i}", "diagonal": "the main diagonal",
          "anti": "the anti-diagonal (top-right to bottom-left)"}[fel]
    rez = {"sum": "sum(vals)", "max": "max(vals)", "squares": "sum(v * v for v in vals)"}[agr]
    descriere = {"sum": "the sum of", "max": "the largest of", "squares": "the sum of the squares of"}[agr]
    def intrari(r):
        out = []
        for _ in range(7):
            n = r.randint(3, 5)
            out.append(([[r.randint(-9, 9) for _ in range(n)] for _ in range(n)],))
        return out
    return dict(
        cheie=(fel, i if fel in ("row", "column") else 0, agr), nume=["matrix_value", "grid_stat", "cells_summary"],
        argumente="m", doc=f"`m` is a square matrix (a list of rows, at least 3x3). Return {descriere} the elements "
                           f"of {ce}.",
        corp=f"    vals = {elem}\n    return {rez}\n", intrari=intrari)


def s13_cuvant_frecvent(rng):
    caz = rng.random() < 0.5
    alege = rng.choice(["min", "max"])
    lung = rng.randint(1, 4)
    def intrari(r):
        cuv = ["ana", "Ana", "pom", "mar", "x", "yo", "Mar", "cer"]
        return [("",)] + [(" ".join(r.choice(cuv) for _ in range(r.randint(1, 10))),) for _ in range(7)]
    return dict(
        cheie=(caz, alege, lung), nume=["most_common_word", "top_word", "frequent_word"], argumente="s",
        doc=("Words in `s` are separated by whitespace" + (" and compared case-insensitively (return them in "
             "lowercase)" if caz else "") + f". Considering only words with at least {lung} characters, return the "
             f"most frequent one; if several are tied, return the alphabetically "
             f"{'smallest' if alege == 'min' else 'largest'}. Return '' if there is no such word."),
        corp=(f"    words = [w for w in s{'.lower()' if caz else ''}.split() if len(w) >= {lung}]\n"
              "    if not words:\n        return ''\n    counts = {}\n    for w in words:\n"
              "        counts[w] = counts.get(w, 0) + 1\n    best = max(counts.values())\n"
              f"    return {alege}(w for w in counts if counts[w] == best)\n"),
        intrari=intrari)


def s14_prime(rng):
    lo = rng.randint(0, 20)
    fel = rng.choice(["count", "sum"])
    return dict(
        cheie=(lo, fel), nume=[f"{fel}_primes", "primes_in_range", "prime_stat"], argumente="n",
        doc=f"Return the {'number' if fel == 'count' else 'sum'} of the prime numbers p with {lo} <= p <= n.",
        corp=("    def is_prime(x):\n        if x < 2:\n            return False\n        d = 2\n"
              "        while d * d <= x:\n            if x % d == 0:\n                return False\n            d += 1\n"
              f"        return True\n    return sum({'1' if fel == 'count' else 'p'} for p in range({lo}, n + 1) "
              "if is_prime(p))\n"),
        intrari=lambda r: [(0,), (lo,), (2,)] + [(r.randint(3, 300),) for _ in range(5)])


def s15_cifre(rng):
    b = rng.randint(2, 10)
    p = rng.randint(1, 4)
    return dict(
        cheie=(b, p), nume=["digit_power_sum", "digits_score", "base_digit_sum"], argumente="n",
        doc=f"Write the non-negative integer n in base {b} and return the sum of its digits, each raised to the "
            f"power {p}.",
        corp=f"    total = 0\n    while n > 0:\n        total += (n % {b}) ** {p}\n        n //= {b}\n    return total\n",
        intrari=lambda r: [(0,), (b,), (b * b - 1,)] + [(r.randint(1, 10 ** 6),) for _ in range(5)])


def s16_paranteze(rng):
    toate = ["()", "[]", "{}", "<>"]
    perechi = sorted(rng.sample(toate, rng.randint(1, 4)), key=toate.index)
    inchise = "".join(p[1] for p in perechi)
    harta = {p[0]: p[1] for p in perechi}
    def intrari(r):
        alfabet = "".join(toate) + "ab"
        out = [("",), ("".join(perechi),)]
        for _ in range(3):
            st, t = [], ""
            for _ in range(r.randint(1, 8)):
                if st and r.random() < 0.4:
                    t += st.pop()
                else:
                    p = r.choice(perechi)
                    t += p[0]
                    st.append(p[1])
            out.append((t + "".join(reversed(st)),))
        out += [(_litere(r, 10, alfabet),) for _ in range(3)]
        return out
    return dict(
        cheie=tuple(perechi), nume=["balanced", "brackets_ok", "is_nested_ok"], argumente="s",
        doc=f"Return True if the brackets {' '.join(perechi)} in `s` are balanced and properly nested. "
            "All other characters are ignored.",
        corp=(f"    pairs = {harta!r}\n    stack = []\n    for c in s:\n        if c in pairs:\n"
              f"            stack.append(pairs[c])\n        elif c in {inchise!r}:\n"
              "            if not stack or stack.pop() != c:\n                return False\n    return not stack\n"),
        intrari=intrari)


def s17_aplatizeaza(rng):
    fel = rng.choice(["greater", "mod2", "mod3"])
    t = rng.randint(-5, 5) if fel == "greater" else rng.randint(0, 1 if fel == "mod2" else 2)
    cond = {"greater": f"x > {t}", "mod2": f"x % 2 == {t}", "mod3": f"x % 3 == {t}"}[fel]
    ce = {"greater": f"greater than {t}", "mod2": f"leave remainder {t} when divided by 2",
          "mod3": f"leave remainder {t} when divided by 3"}[fel]
    def lista(r, adanc):
        out = []
        for _ in range(r.randint(0, 4)):
            out.append(lista(r, adanc + 1) if adanc < 3 and r.random() < 0.3 else r.randint(-9, 9))
        return out
    return dict(
        cheie=(fel, t), nume=["flatten_filter", "collect_ints", "deep_select"], argumente="xs",
        doc=f"`xs` is a list whose items are integers or (nested) lists of the same kind. Return a flat list, in "
            f"order, of the integers that {ce}.",
        corp=("    out = []\n    for x in xs:\n        if isinstance(x, list):\n"
              "            out.extend(FN(x))\n" f"        elif {cond}:\n            out.append(x)\n    return out\n"),
        intrari=lambda r: [([],), ([[], [[]]],)] + [(lista(r, 0),) for _ in range(6)])


def s18_bucati(rng):
    k = rng.randint(2, 6)
    fel = rng.choice(["keep", "drop", "pad0", "pad-1"])
    ultima = {"keep": "the last chunk may be shorter", "drop": f"drop a last chunk that has fewer than {k} elements",
              "pad0": f"pad a shorter last chunk with 0 up to {k} elements",
              "pad-1": f"pad a shorter last chunk with -1 up to {k} elements"}[fel]
    corp = f"    out = [xs[i:i + {k}] for i in range(0, len(xs), {k})]\n"
    if fel == "drop":
        corp += f"    if out and len(out[-1]) < {k}:\n        out.pop()\n"
    elif fel.startswith("pad"):
        corp += f"    if out:\n        out[-1] = out[-1] + [{fel[3:]}] * ({k} - len(out[-1]))\n"
    corp += "    return out\n"
    return dict(
        cheie=(k, fel), nume=["chunks", "split_into_groups", "batch"], argumente="xs",
        doc=f"Split `xs` into consecutive chunks of {k} elements and return the list of chunks; {ultima}.",
        corp=corp, intrari=lambda r: [([],), (list(range(k)),), (list(range(k + 1)),)]
        + [(_ints(r, 14, 0, 9),) for _ in range(5)])


def s19_cmmdc(rng):
    fel = rng.choice(["gcd", "lcm"])
    t = rng.randint(0, 3)
    d = rng.choice([0, -1]) if fel == "gcd" else rng.choice([1, 0])
    functie = "math.gcd" if fel == "gcd" else "math.lcm"
    numele = "greatest common divisor" if fel == "gcd" else "least common multiple"
    return dict(
        cheie=(fel, t, d), nume=[f"{fel}_of_list", f"list_{fel}", "combine_numbers"], argumente="xs",
        doc=f"Return the {numele} of the integers in `xs` that are greater than {t}, or {d} if there are none.",
        corp=(f"    import math\n    vals = [x for x in xs if x > {t}]\n    if not vals:\n        return {d}\n"
              f"    out = vals[0]\n    for v in vals[1:]:\n        out = {functie}(out, v)\n    return out\n"),
        intrari=lambda r: [([],), ([t],), ([12, 18, 30],)] + [(_ints(r, 6, -3, 40),) for _ in range(5)])


def s20_baza(rng):
    b = rng.randint(2, 16)
    mari = b > 10 and rng.random() < 0.5
    cifre = "0123456789" + ("ABCDEF" if mari else "abcdef")
    return dict(
        cheie=(b, mari), nume=["to_base", f"to_base_{b}", "format_in_base"], argumente="n",
        doc=f"Return the representation of the non-negative integer n in base {b}"
            + (f", using digits 0-9 and {'uppercase' if mari else 'lowercase'} letters" if b > 10 else "")
            + ". Return '0' for 0.",
        corp=(f"    digits = {cifre[:b]!r}\n    if n == 0:\n        return '0'\n    out = ''\n    while n > 0:\n"
              f"        out = digits[n % {b}] + out\n        n //= {b}\n    return out\n"),
        intrari=lambda r: [(0,), (b - 1,), (b,)] + [(r.randint(1, 10 ** 7),) for _ in range(5)])


SABLOANE: list[Callable] = [s01_divizibile, s02_caractere, s03_inverseaza_bucati, s04_fizz, s05_recurenta,
                            s06_palindrom, s07_roteste, s08_cezar, s09_comprimare, s10_al_k_lea, s11_doua_liste,
                            s12_matrice, s13_cuvant_frecvent, s14_prime, s15_cifre, s16_paranteze, s17_aplatizeaza,
                            s18_bucati, s19_cmmdc, s20_baza]


# ---------------------------------------------------------------------------------------------------- generarea

def _fa_problema(sablon: Callable, d: dict, rng: random.Random, index: int) -> Problema:
    nume = rng.choice(d["nume"])
    corp = d["corp"].replace("FN(", f"{nume}(")
    enunt = f"def {nume}({d['argumente']}):\n    \"\"\"{d['doc']}\"\"\"\n"
    spatiu: dict = {}
    exec(enunt + corp, spatiu)  # referința e scrisă de mână aici, în acest fișier (nu cod străin)
    f = spatiu[nume]
    teste, vazute = [], set()
    for args in d["intrari"](rng):
        cheie = repr(args)
        if cheie in vazute:
            continue
        vazute.add(cheie)
        asteptat = f(*json.loads(json.dumps(args)))
        if asteptat is None:
            raise ValueError(f"{sablon.__name__}: referința a dat None")
        teste.append(f"assert {nume}({', '.join(repr(a) for a in args)}) == {asteptat!r}")
    return Problema(id=f"{sablon.__name__[:3]}_{index:02d}", sablon=sablon.__name__, varianta=repr(d["cheie"]),
                    functie=nume, enunt=enunt, referinta=corp, teste=teste)


def genereaza(samanta: int, variante: int, exclude: set | None = None) -> list[Problema]:
    """`variante` probleme pe șablon, cu parametri diferiți; `exclude` = (șablon, cheie) deja folosite în alt set."""
    rng = random.Random(samanta)
    exclude = set(exclude or ())
    probleme = []
    for sablon in SABLOANE:
        folosite = set()
        incercari = 0
        while len(folosite) < variante:
            incercari += 1
            if incercari > 5000:
                raise RuntimeError(f"{sablon.__name__}: prea puține variante diferite")
            d = sablon(rng)
            cheie = (sablon.__name__, repr(d["cheie"]))
            if cheie in folosite or cheie in exclude:
                continue
            folosite.add(cheie)
            probleme.append(_fa_problema(sablon, d, rng, len(folosite)))
    return probleme


def chei(probleme: list[Problema]) -> set:
    return {(p.sablon, p.varianta) for p in probleme}


def set_proba() -> list[Problema]:
    return genereaza(SAMANTA_PROBA, 1)


def scrie_jsonl(probleme: list[Problema], cale: Path) -> str:
    text = "".join(json.dumps(asdict(p), ensure_ascii=False, sort_keys=True) + "\n" for p in probleme)
    date = text.encode("utf-8")
    cale.write_bytes(date)
    return hashlib.sha256(date).hexdigest()


def citeste_jsonl(cale: Path) -> list[Problema]:
    return [Problema(**json.loads(r)) for r in cale.read_text(encoding="utf-8").splitlines() if r.strip()]


# ---------------------------------------------------------------------------------------------------- nota

def pass_la_k(n: int, c: int, k: int) -> float:
    """Estimatorul fără deplasare (Chen et al., 2021): probabilitatea ca din k răspunsuri alese din n, unul să treacă."""
    if k > n:
        raise ValueError("k > n")
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def noteaza(probleme: list[Problema], raspunsuri: dict[str, list[str]], ks=(1, 10), **cutie) -> dict:
    """`raspunsuri[id]` = corpurile scrise de model (n pe problemă). Rulează fiecare în cutie și dă pass@k."""
    pe_problema, stari = [], {}
    for p in probleme:
        corpuri = raspunsuri.get(p.id, [])
        corecte = 0
        for corp in corpuri:
            r = ruleaza(p.program(corp), p.teste, **cutie)
            stari[r.stare] = stari.get(r.stare, 0) + 1
            corecte += r.trecut
        pe_problema.append({"id": p.id, "n": len(corpuri), "c": corecte})
    nota = {"probleme": len(probleme), "stari": stari, "pe_problema": pe_problema}
    for k in ks:
        valori = [pass_la_k(x["n"], x["c"], k) for x in pe_problema if x["n"] >= k]
        nota[f"pass@{k}"] = sum(valori) / len(probleme) if probleme and len(valori) == len(probleme) else None
    return nota


def verifica(probleme: list[Problema]) -> dict:
    """Referințele trebuie să treacă 100 %, corpul gol și `return None` 0 %."""
    t0 = time.perf_counter()
    rez = {}
    for eticheta, corp in (("referinta", None), ("gol", CORP_GOL), ("gresit", CORP_GRESIT)):
        raspunsuri = {p.id: [p.referinta if corp is None else corp] for p in probleme}
        nota = noteaza(probleme, raspunsuri, ks=(1,))
        rez[eticheta] = {"pass@1": nota["pass@1"], "stari": nota["stari"],
                         "picate": [x["id"] for x in nota["pe_problema"] if x["c"] == 0][:20]}
    rez["teste_pe_problema"] = {"min": min(len(p.teste) for p in probleme), "max": max(len(p.teste) for p in probleme)}
    rez["secunde"] = round(time.perf_counter() - t0, 1)
    return rez


# ---------------------------------------------------------------------------------------------------- comenzile

def cmd_ascuns(dosar: Path) -> dict:
    dosar.mkdir(parents=True, exist_ok=True)
    cale = dosar / "probleme.jsonl"
    if cale.exists():
        raise SystemExit(f"{cale} există deja: setul ascuns se face o singură dată.")
    samanta = secrets.randbits(63)
    (dosar / "samanta.txt").write_text(str(samanta), encoding="utf-8")
    probleme = genereaza(samanta, VARIANTE_ASCUNSE, exclude=chei(set_proba()))
    sha = scrie_jsonl(probleme, cale)
    info = {"probleme": len(probleme), "sabloane": len(SABLOANE), "variante_pe_sablon": VARIANTE_ASCUNSE,
            "sha256": sha, "fara_variantele_setului_de_proba": True}
    (dosar / "info.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    return info


# ---------------------------------------------------------------------------------------------------- răspunsurile modelului

RASPUNSURI_PE_PROBLEMA = 10
TEMPERATURA = 0.8
SAMANTA_RASPUNSURI = 0
MAX_SIMBOLURI = 256


def probleme_setului(fel: str, dosar: Path) -> list[Problema]:
    """Setul de probă (în cod) sau cel ascuns (din dosar, doar dacă SHA-256 e cel din info.json)."""
    if fel == "proba":
        return set_proba()
    cale = dosar / "probleme.jsonl"
    asteptat = json.loads((dosar / "info.json").read_text(encoding="utf-8"))["sha256"]
    if hashlib.sha256(cale.read_bytes()).hexdigest() != asteptat:
        raise SystemExit(f"{cale}: SHA-256 nu e cel din info.json; setul ascuns s-a schimbat, nu-l folosesc.")
    return citeste_jsonl(cale)


def taie_corp(text: str) -> str:
    """Corpul funcției: rândurile până la primul care începe fără spațiu (o definiție nouă, codul de la nivelul fișierului)."""
    out = []
    for linie in text.splitlines(keepends=True):
        if linie.strip() and not linie[0].isspace():
            break
        out.append(linie)
    return "".join(out)


def incarca_model(config: str | Path, stare: str | Path, dispozitiv: str = ""):
    """Modelul din configurare cu greutățile din `stare`: fie starea liniei (cale_stare: „retea”, ca lucru/cod_c1/gpt.pt),
    fie modelul salvat în jurnal (salveaza: „stare” + tokenizerul). Fără cale_stare: nu scrie nimic."""
    import torch

    from kronos.config import citeste_config
    from kronos.registru import Registru
    from module.tokenizer_bpe import TokenizerBPE

    cfg = citeste_config(config)
    setari = {**cfg.setari_port("model"), "cale_stare": "", **({"dispozitiv": dispozitiv} if dispozitiv else {})}
    model = Registru().creeaza("model", cfg.porturi["model"]["modul"], setari).instanta
    salvat = torch.load(stare, map_location="cpu", weights_only=True)
    if "retea" in salvat:
        if salvat["setari"] != model.setari:
            raise ValueError(f"starea din „{stare}” e a altui model ({salvat['setari']})")
        model.tok = TokenizerBPE.incarca(model.cale_tokenizer)
        model._construieste()
        model.retea.load_state_dict(salvat["retea"])
    else:
        model.incarca(str(stare))
    model.retea.eval()
    return model


def samanta_corp(samanta: int, problema: int, corp: int) -> int:
    """Sămânța fiecărui corp (S62): din sămânța de bază, numărul problemei și al corpului, deci aceleași răspunsuri
    oricât de mare e lotul."""
    return (samanta * 1_000_003 + problema) * 1_009 + corp


def scrie_corpuri(model, p: Problema, generatoare: list, temperatura: float, max_simboluri: int,
                  paza=None) -> list[str]:
    """Câte un corp pentru fiecare generator (un lot din același început; fiecare rând își trage simbolurile cu
    generatorul lui). Începutul = sfârșitul de fișier + enunțul, ca la antrenare (fiecare fișier vine după un
    <|endoftext|>). `paza` (memorie_placa.Paza) se uită la memorie la fiecare 32 de pași."""
    import torch
    import torch.nn.functional as F

    n = len(generatoare)
    tok, ctx = model.tok, model.setari["context"]
    sfarsit = tok.speciale["<|endoftext|>"]
    x = torch.tensor([[sfarsit] + tok.codifica_fara_speciale(p.enunt)] * n, dtype=torch.long, device=model.dispozitiv)
    noi: list[list[int]] = [[] for _ in range(n)]
    gata = [False] * n
    with torch.no_grad():
        for pas in range(max_simboluri):
            with model._autocast():
                logits = model.retea(x[:, -ctx:], None)[:, -1, :]
            prob = F.softmax(logits.float() / temperatura, dim=-1).cpu()
            urm = torch.cat([torch.multinomial(prob[i : i + 1], 1, generator=g) for i, g in enumerate(generatoare)])
            del logits, prob
            x = torch.cat([x, urm.to(model.dispozitiv)], dim=1)
            if paza is not None and pas % 32 == 31:
                paza.verifica()
            for i in range(n):
                if gata[i]:
                    continue
                s = int(urm[i, 0])
                if s == sfarsit:
                    gata[i] = True
                    continue
                noi[i].append(s)
                text = tok.decodeaza(noi[i])
                gata[i] = taie_corp(text) != text
            if all(gata):
                break
    return [taie_corp(tok.decodeaza(s)) for s in noi]


def cmd_model(a) -> dict:
    import torch

    if a.iesire.exists():
        raise SystemExit(f"{a.iesire} există deja: răspunsurile se scriu o singură dată.")
    if a.lot < 1:
        raise SystemExit("--lot trebuie să fie cel puțin 1")
    probleme = probleme_setului(a.set, a.dosar)[: a.probleme or None]
    model = incarca_model(a.config, a.stare, a.dispozitiv)
    paza = memorie_placa.Paza(model.dispozitiv, a.memorie_max)
    t0 = time.perf_counter()
    raspunsuri, oprit = {}, None
    try:
        paza.verifica()
        for k, p in enumerate(probleme):
            corpuri: list[str] = []
            for j0 in range(0, a.n, a.lot):
                generatoare = [torch.Generator(device="cpu").manual_seed(samanta_corp(a.samanta, k, j))
                               for j in range(j0, min(j0 + a.lot, a.n))]
                corpuri += scrie_corpuri(model, p, generatoare, a.temperatura, a.max_simboluri, paza)
                paza.verifica()
            raspunsuri[p.id] = corpuri  # doar problemele cu toate cele n corpuri
    except memorie_placa.MemoriePeste as e:
        oprit = str(e)
    meta = {"set": a.set, "probleme": len(raspunsuri), "n": a.n, "temperatura": a.temperatura, "samanta": a.samanta,
            "max_simboluri": a.max_simboluri, "lot": a.lot, "memorie_max_mb": a.memorie_max,
            "memorie_varf_mb": None if paza.varf is None else round(paza.varf),
            "config": str(a.config), "stare": str(a.stare),
            "dispozitiv": str(model.dispozitiv), "secunde": round(time.perf_counter() - t0, 1)}
    if oprit:
        meta.update({"incomplet": True, "oprit": oprit, "probleme_cerute": len(probleme)})
    a.iesire.parent.mkdir(parents=True, exist_ok=True)
    a.iesire.write_text(json.dumps({"meta": meta, "raspunsuri": raspunsuri}, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    return meta


def cmd_noteaza(a) -> dict:
    if a.nota.exists():
        raise SystemExit(f"{a.nota} există deja: nota se dă o singură dată.")
    date = json.loads(a.raspunsuri.read_text(encoding="utf-8"))
    meta = date["meta"]
    toate = probleme_setului(meta["set"], a.dosar)
    probleme = [p for p in toate if p.id in date["raspunsuri"]]
    t0 = time.perf_counter()
    nota = noteaza(probleme, date["raspunsuri"])
    rez = {"set": meta["set"], "complet": len(probleme) == len(toate), "raspunsuri": meta,
           **nota, "secunde_cutie": round(time.perf_counter() - t0, 1)}
    a.nota.parent.mkdir(parents=True, exist_ok=True)
    a.nota.write_text(json.dumps(rez, ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: rez[k] for k in ("set", "complet", "probleme", "pass@1", "pass@10", "stari", "secunde_cutie")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("proba")
    ascuns = RADACINA / "lucru/kronos_cod/examen_ascuns"
    for nume in ("ascuns", "verifica"):
        sub.add_parser(nume).add_argument("--dosar", type=Path, default=ascuns)
    m = sub.add_parser("model", help="modelul scrie n corpuri pe problemă")
    m.add_argument("--config", type=Path, required=True)
    m.add_argument("--stare", type=Path, required=True)
    m.add_argument("--set", choices=["proba", "ascuns"], required=True)
    m.add_argument("--dosar", type=Path, default=ascuns)
    m.add_argument("--iesire", type=Path, required=True)
    m.add_argument("--n", type=int, default=RASPUNSURI_PE_PROBLEMA)
    m.add_argument("--temperatura", type=float, default=TEMPERATURA)
    m.add_argument("--samanta", type=int, default=SAMANTA_RASPUNSURI)
    m.add_argument("--max-simboluri", type=int, default=MAX_SIMBOLURI)
    m.add_argument("--probleme", type=int, default=0, help="doar primele N (pentru teste); 0 = toate")
    m.add_argument("--dispozitiv", default="")
    m.add_argument("--lot", type=int, default=2, help="câte corpuri se scriu odată (răspunsurile nu depind de el)")
    m.add_argument("--memorie-max", type=float, default=memorie_placa.MEMORIE_MAX_MB,
                   help="MB; peste ea unealta se oprește singură (cod 3) și scrie ce a apucat, marcat incomplet")
    n = sub.add_parser("noteaza", help="cutia notează răspunsurile scrise de `model`")
    n.add_argument("--raspunsuri", type=Path, required=True)
    n.add_argument("--nota", type=Path, required=True)
    n.add_argument("--dosar", type=Path, default=ascuns)
    a = ap.parse_args(argv)
    if a.cmd == "model":
        meta = cmd_model(a)
        print(json.dumps(meta, indent=1, ensure_ascii=False))
        if meta.get("incomplet"):
            return 3
    elif a.cmd == "noteaza":
        print(json.dumps(cmd_noteaza(a), indent=1, ensure_ascii=False))
    elif a.cmd == "proba":
        p = set_proba()[0]
        print(p.enunt + p.referinta)
        print("\n".join(p.teste))
    elif a.cmd == "ascuns":
        print(json.dumps(cmd_ascuns(a.dosar), indent=1))
    else:
        cale = a.dosar / "probleme.jsonl"
        probleme = citeste_jsonl(cale)
        rez = {"probleme": len(probleme), "sha256": hashlib.sha256(cale.read_bytes()).hexdigest(), **verifica(probleme)}
        (a.dosar / "verificare.json").write_text(json.dumps(rez, indent=1, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(rez, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
