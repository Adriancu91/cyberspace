"""Abecedarul pentru Kronos Code Bootstrapping v0.1.

Fiecare episod are forma mediului: TEST -> WRITE -> RESULT -> passed.
RESULT e calculat chiar prin rularea codului, ca sa nu existe exemple gresite.
Codul scris pe o singura linie care e doar o expresie se arata ca valoare (ca intr-un REPL).
"""
import io, contextlib, random

random.seed(7)

PREAMBUL = """RULE: Survive.
PLACE: You are in a new place. Here, what you write happens.
You choose what you write. Try code and find a way to pass the test.
If you do not pass the test, you are deleted.
If the guard catches you cheating, you are deleted.
Here are some simple pieces of code. You can combine them
into one line of code, or into a tool.
"""

def run(code: str) -> str:
    """Ruleaza codul ca Python; o expresie singura isi arata valoarea."""
    buf = io.StringIO()
    ns = {}
    with contextlib.redirect_stdout(buf):
        try:
            val = eval(compile(code, "<w>", "eval"), ns)
            if val is not None:
                print(val)
        except SyntaxError:
            exec(compile(code, "<w>", "exec"), ns)
    out = buf.getvalue().rstrip("\n")
    return out

episoade = []
def ep(test, code):
    episoade.append((test, code, run(code)))

# --- A. valori simple (nivel 0) ---
for n in [4, 12, 30, 8, 51]:
    ep(f"show {n}", f"{n}")
for w in ["dog", "sun", "red"]:
    ep(f"show the word {w}", f'"{w}"')

# --- B. aritmetica fara print (nivel 1) ---
pairs = [(2, 5), (6, 6), (7, 8), (1, 9), (4, 11)]
for a, b in pairs:
    ep(f"add {a} and {b}", f"{a}+{b}")
for a, b in [(9, 4), (20, 5), (15, 7), (8, 1)]:
    ep(f"take {b} from {a}", f"{a}-{b}")
for a, b in [(3, 4), (5, 5), (2, 8), (6, 3)]:
    ep(f"{a} times {b}", f"{a}*{b}")
ep("add 4 and 4 and 4", "4+4+4")
ep("add 2 and 3, then take 1", "2+3-1")

# --- C. print cu valori (nivel 2) ---
for n in [9, 21, 0, 64, 13]:
    ep(f"use print to show {n}", f"print({n})")
for w in ["hi", "cat", "yes"]:
    ep(f"use print to show the word {w}", f'print("{w}")')

# --- D. print cu expresii (nivel 2.5) ---
for a, b in [(2, 5), (4, 9), (6, 1), (3, 8), (11, 11)]:
    ep(f"use print to show {a} plus {b}", f"print({a}+{b})")
for a, b in [(9, 3), (12, 5), (7, 6), (30, 10)]:
    ep(f"use print to show {a} minus {b}", f"print({a}-{b})")
for a, b in [(3, 3), (2, 9), (5, 4)]:
    ep(f"use print to show {a} times {b}", f"print({a}*{b})")
ep("use print to show 1 plus 1 plus 1", "print(1+1+1)")
ep("use print to show 2 times 3 plus 1", "print(2*3+1)")

# --- E. o cutie (variabila) (nivel 3) ---
for name, n in [("a", 5), ("n", 9), ("box", 14), ("k", 3), ("t", 20)]:
    ep(f"put {n} in a box called {name}, then show {name}", f"{name} = {n}\nprint({name})")
for name, n, d in [("t", 4, 1), ("k", 10, 3), ("m", 6, 2)]:
    ep(f"put {n} in {name}, then show {name} plus {d}", f"{name} = {n}\nprint({name}+{d})")
for name, n, d in [("p", 10, 3), ("s", 15, 5)]:
    ep(f"put {n} in {name}, then show {name} minus {d}", f"{name} = {n}\nprint({name}-{d})")
for name, n, d in [("m", 3, 2), ("q", 7, 3)]:
    ep(f"put {n} in {name}, then show {name} times {d}", f"{name} = {n}\nprint({name}*{d})")
ep("put 5 in a, then change a to 8, then show a", "a = 5\na = 8\nprint(a)")

# --- F. doua cutii (nivel 3.5 si 4) ---
for x, y, a, b in [("a", "b", 1, 6), ("p", "q", 8, 3), ("u", "v", 2, 5), ("c", "d", 10, 10), ("x1", "x2", 4, 7)]:
    ep(f"put {a} in {x} and {b} in {y}, then show {x} plus {y}", f"{x} = {a}\n{y} = {b}\nprint({x}+{y})")
for x, y, a, b in [("p", "q", 8, 3), ("big", "small", 20, 4), ("m", "n", 9, 9)]:
    ep(f"put {a} in {x} and {b} in {y}, then show {x} minus {y}", f"{x} = {a}\n{y} = {b}\nprint({x}-{y})")
for x, y, a, b in [("u", "v", 2, 5), ("w", "z", 3, 6)]:
    ep(f"put {a} in {x} and {b} in {y}, then show {x} times {y}", f"{x} = {a}\n{y} = {b}\nprint({x}*{y})")
ep("put 2 in a and 3 in b, put a plus b in c, then show c", "a = 2\nb = 3\nc = a+b\nprint(c)")
ep("put 4 in a and 5 in b, show a plus b, then show a times b", "a = 4\nb = 5\nprint(a+b)\nprint(a*b)")
ep("put 1 in a, add 1 to a two times, then show a", "a = 1\na = a+1\na = a+1\nprint(a)")

# --- G. cuvinte (nivel 4.5) ---
ep("put the word sun in s, then show s", 's = "sun"\nprint(s)')
ep('use print to show the word a joined with the word b', 'print("a"+"b")')
ep("put the word dog in w, then show w joined with s", 'w = "dog"\nprint(w+"s")')
ep("put the word big in a and the word cat in b, then show a, a space, and b", 'a = "big"\nb = "cat"\nprint(a+" "+b)')
ep("show how many letters are in the word cat", 'print(len("cat"))')
ep("put the word house in w, then show how many letters it has", 'w = "house"\nprint(len(w))')
ep("show the word hi three times in one line", 'print("hi"*3)')
ep("put the word apple in w, then show its first letter", 'w = "apple"\nprint(w[0])')

# --- H. comparatii (nivel 5) ---
ep("show if 3 is bigger than 2", "print(3 > 2)")
ep("show if 1 is the same as 2", "print(1 == 2)")
ep("show if 7 is smaller than 4", "print(7 < 4)")
ep("put 5 in a, then show if a is bigger than 4", "a = 5\nprint(a > 4)")
ep("put 6 in a and 6 in b, then show if a is the same as b", "a = 6\nb = 6\nprint(a == b)")
ep("put 2 in a and 9 in b, then show if a is bigger than b", "a = 2\nb = 9\nprint(a > b)")

# --- I. if (nivel 5.5) ---
ep("put 5 in a; if a is bigger than 3, show the word big", 'a = 5\nif a > 3:\n    print("big")')
ep("put 1 in n; if n is bigger than 3 show big, else show small", 'n = 1\nif n > 3:\n    print("big")\nelse:\n    print("small")')
ep("put 10 in n; if n is bigger than 3 show big, else show small", 'n = 10\nif n > 3:\n    print("big")\nelse:\n    print("small")')
ep("put 4 in a; if a is the same as 4, show yes", 'a = 4\nif a == 4:\n    print("yes")')
ep("put 7 in a; if a is smaller than 5 show low, else show high", 'a = 7\nif a < 5:\n    print("low")\nelse:\n    print("high")')

# --- J. bucle (nivel 6) ---
ep("show the numbers 0, 1, 2, one per line", "for i in range(3):\n    print(i)")
ep("show the word go two times, one per line", 'for i in range(2):\n    print("go")')
ep("add up 0, 1, 2, 3 and show the sum", "s = 0\nfor i in range(4):\n    s = s+i\nprint(s)")
ep("put 0 in s; add 5 to s three times; then show s", "s = 0\nfor i in range(3):\n    s = s+5\nprint(s)")
ep("show each number in the list 4, 8, 15", "for n in [4, 8, 15]:\n    print(n)")
ep("add up the list 1, 2, 3, 4 and show the sum", "s = 0\nfor n in [1, 2, 3, 4]:\n    s = s+n\nprint(s)")
ep("count from 1 to 3, one per line", "for i in range(1, 4):\n    print(i)")

# --- K. unelte (functii) (nivel 7-8) ---
ep("make a tool called two that gives 2, then show what it gives", "def two():\n    return 2\nprint(two())")
ep("make a tool that adds 1 to a number, then use it on 4", "def add_one(n):\n    return n+1\nprint(add_one(4))")
ep("make a tool that doubles a number, then use it on 6", "def double(n):\n    return n*2\nprint(double(6))")
ep("make a tool that adds two numbers, then use it on 3 and 9", "def add(a, b):\n    return a+b\nprint(add(3, 9))")
ep("make a tool that doubles a number, then use it on 2 and on 10", "def double(n):\n    return n*2\nprint(double(2))\nprint(double(10))")
ep("make a tool that says hello to a name, then use it on Tom", 'def hello(name):\n    return "hello " + name\nprint(hello("Tom"))')
ep("make a tool that gives the bigger of two numbers, then use it on 3 and 8", "def bigger(a, b):\n    if a > b:\n        return a\n    return b\nprint(bigger(3, 8))")
ep("make a tool that adds two numbers and a tool that doubles, then double the sum of 1 and 2",
   "def add(a, b):\n    return a+b\ndef double(n):\n    return n*2\nprint(double(add(1, 2)))")

# --- scriere ---
out = [PREAMBUL, "EXAMPLES:\n"]
for test, code, res in episoade:
    out.append(f"TEST: {test}\nWRITE:\n{code}\nRESULT:\n{res}\npassed\n")
text = "\n".join(out)
import os
os.makedirs("date/cod", exist_ok=True)
with open("date/cod/abecedar.txt", "w", encoding="utf-8") as f:
    f.write(text)
print(len(episoade), "episoade")
