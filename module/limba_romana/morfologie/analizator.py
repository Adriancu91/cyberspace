"""Analiza morfologică a unui cuvânt: toate analizele cunoscute din bază + ipoteze pentru cuvintele necunoscute.

Rezultatul e o listă de `Analiza` (una pe fiecare pereche lexem–trăsături), fiecare cu:
  - `incredere`: „baza” (forma e în bază), „fara_diacritice” (potrivire pe forma fără diacritice), „ipoteza”
    (lemă găsită, formă dedusă prin regulă), „necunoscut” (nimic în bază; categoria e doar ghicită din terminație);
  - `dovezi`: textul explicațiilor (proveniența formelor, frecvența în corpus, regula folosită).
Ambiguitatea se păstrează: dezambiguizarea se face mai târziu, din context (sintaxa/dezambiguizare.py).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..baza import Baza, canonic_trasaturi, desparte_trasaturi
from ..text import are_diacritice, fara_diacritice, normalizeaza

RE_NUMAR = re.compile(r"^\d+(?:[.,]\d+)*(?:%|‰)?$")
RE_ROMAN = re.compile(r"^(?=[MDCLXVI])M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")
RE_PUNCT = re.compile(r"^[^\w\s]+$")

# terminații → (categorie, trăsături) pentru cuvinte necunoscute (doar ipoteze slabe, ordonate de la lung la scurt)
TERMINATII: list[tuple[str, str, str]] = [
    ("urilor", "NOUN", "Case=Dat,Gen|Definite=Def|Gender=Fem|Number=Plur"), ("urile", "NOUN", "Case=Acc,Nom|Definite=Def|Gender=Fem|Number=Plur"),
    ("ilor", "NOUN", "Case=Dat,Gen|Definite=Def|Number=Plur"), ("elor", "NOUN", "Case=Dat,Gen|Definite=Def|Gender=Fem|Number=Plur"),
    ("ului", "NOUN", "Case=Dat,Gen|Definite=Def|Gender=Masc|Number=Sing"), ("ele", "NOUN", "Case=Acc,Nom|Definite=Def|Gender=Fem|Number=Plur"),
    ("uri", "NOUN", "Definite=Ind|Gender=Fem|Number=Plur"), ("ul", "NOUN", "Case=Acc,Nom|Definite=Def|Gender=Masc|Number=Sing"),
    ("ează", "VERB", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin"), ("ește", "VERB", "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin"),
    ("ând", "VERB", "VerbForm=Ger"), ("ind", "VERB", "VerbForm=Ger"), ("ează", "VERB", "Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin"),
    ("eam", "VERB", "Mood=Ind|Number=Sing|Person=1|Tense=Imp|VerbForm=Fin"), ("eau", "VERB", "Mood=Ind|Number=Plur|Person=3|Tense=Imp|VerbForm=Fin"),
    ("ăm", "VERB", "Mood=Ind|Number=Plur|Person=1|Tense=Pres|VerbForm=Fin"), ("ați", "VERB", "Mood=Ind|Number=Plur|Person=2|Tense=Pres|VerbForm=Fin"),
    ("mente", "ADV", ""), ("ește", "ADV", ""),
]


@dataclass
class Analiza:
    forma: str
    lema: str
    lexem_id: str | None
    pos: str
    trasaturi: dict[str, str]
    incredere: str                       # baza | fara_diacritice | ipoteza | necunoscut | special
    statut: str = ""                     # statutul formei în bază (atestat/generat/validat) sau gol
    gen_lexem: str | None = None
    multicuvant: bool = False
    frecventa: int = 0                   # aparițiile în corpus (UD) cu această analiză
    dovezi: list[str] = field(default_factory=list)
    atribute: dict = field(default_factory=dict)

    def tr(self, cheie: str, implicit: str | None = None) -> str | None:
        return self.trasaturi.get(cheie, implicit)

    def ca_dict(self) -> dict:
        return {"forma": self.forma, "lema": self.lema, "lexem_id": self.lexem_id, "pos": self.pos, "trasaturi": dict(self.trasaturi),
                "incredere": self.incredere, "statut": self.statut, "gen_lexem": self.gen_lexem, "frecventa": self.frecventa, "dovezi": list(self.dovezi),
                "atribute": {k: v for k, v in self.atribute.items() if k in ("registru", "etimologie", "tip")}}


class Analizator:
    def __init__(self, baza: Baza):
        self.baza = baza
        self._cache: dict[str, list[Analiza]] = {}

    def analizeaza(self, text: str, tip: str = "cuvant") -> list[Analiza]:
        """Toate analizele pentru un token. `tip` vine de la tokenizator (numar, punct, abrev, cuvant, clitic)."""
        if tip == "numar" or RE_NUMAR.match(text):
            numar = "Plur" if text.endswith(("%", "‰")) else "Sing"
            return [Analiza(text, text, None, "NUM", {"NumForm": "Digit", "NumType": "Card", "Number": numar}, "special", dovezi=["număr scris cu cifre"])]
        if tip == "punct" or RE_PUNCT.match(text):
            return [Analiza(text, text, None, "PUNCT", {}, "special", dovezi=["punctuație"])]
        if tip == "ora":
            return [Analiza(text, text, None, "NUM", {"NumForm": "Digit"}, "special", dovezi=["oră"])]
        cheie = text
        if cheie in self._cache:
            return self._cache[cheie]
        rez = self._din_baza(text)
        if not rez and RE_ROMAN.match(text) and len(text) <= 6:
            rez = [Analiza(text, text, None, "NUM", {"NumForm": "Roman", "NumType": "Card"}, "special", dovezi=["numeral roman"])]
        if not rez and tip == "abrev":
            rez = [Analiza(text, text, None, "ABBR", {"Abbr": "Yes"}, "special", dovezi=["abreviere cu punct"])]
        if not rez:
            rez = self._ipoteze(text)
        self._cache[cheie] = rez
        return rez

    def _din_baza(self, text: str) -> list[Analiza]:
        randuri = self.baza.cauta_forma(text, si_fara_diacritice=True)
        rez: list[Analiza] = []
        vazute: dict[tuple[str, str], Analiza] = {}
        for r in randuri:
            tr = {k: v for k, v in desparte_trasaturi(r["trasaturi"]).items() if k != "ExtPos"}
            if r["gen"] and r["pos"] in ("NOUN", "PROPN") and "Gender" not in tr and tr.get("Number"):
                tr["Gender"] = {"Neut": "Masc" if tr["Number"] == "Sing" else "Fem"}.get(r["gen"], r["gen"])
            frecv = sum(p["frecventa"] for p in r["provenienta"] if p["sursa_id"] == "ud_rrt")
            surse = sorted({p["sursa_id"] for p in r["provenienta"]})
            dovezi = [f"în bază ({r['statut']}): " + ", ".join(surse)]
            if frecv:
                dovezi.append(f"în corpusul UD RRT: {frecv} apariții cu această analiză")
            reguli = sorted({p["origine"] for p in r["provenienta"] if p["origine"].startswith("regula")})
            if reguli:
                dovezi.append("generată de: " + ", ".join(reguli[:3]))
            incredere = "baza" if r["potrivire"] == "exacta" else "fara_diacritice"
            if incredere == "fara_diacritice":
                dovezi.append("potrivire fără diacritice (textul nu avea diacritice sau forma e altfel scrisă)")
            a = Analiza(r["forma"], r["lema"], r["lexem_id"], r["pos"], tr, incredere, r["statut"], r["gen"], bool(r["multicuvant"]), frecv, dovezi, r["atribute"])
            cheie = (r["lexem_id"], canonic_trasaturi(tr))
            if cheie in vazute:   # același lexem și aceleași trăsături (rânduri care difereau doar prin ExtPos): contopim dovezile
                vazute[cheie].frecventa += frecv
                if r["statut"] == "validat":
                    vazute[cheie].statut = "validat"
                continue
            vazute[cheie] = a
            rez.append(a)
        # un cuvânt cu majusculă necunoscut altfel decât ca nume propriu rămâne și ipoteză de nume propriu
        if text[:1].isupper() and not any(a.pos == "PROPN" for a in rez):
            pass
        return rez

    def _ipoteze(self, text: str) -> list[Analiza]:
        norm = normalizeaza(text)
        rez: list[Analiza] = []
        orto = self.baza.cunoscut_ortografic(text)
        if orto:
            rez.append(Analiza(text, text, None, "X", {}, "ipoteza", dovezi=["cuvânt cunoscut doar ortografic (dicționarul Hunspell), fără lemă/categorie"]))
        # cu majusculă inițială: nume propriu probabil (nu e în bază)
        if text[:1].isupper() and len(text) > 1 and not text.isupper():
            rez.append(Analiza(text, text, None, "PROPN", {}, "ipoteza", dovezi=["majusculă inițială; nu e în bază ca nume propriu"]))
        if text.isupper() and len(text) >= 2:
            rez.append(Analiza(text, text, None, "PROPN", {"Abbr": "Yes"}, "ipoteza", dovezi=["scris cu majuscule: siglă/abreviere"]))
        # lemă cunoscută + terminație regulată (de ex. substantiv fără gen în bază)
        rez.extend(self._din_terminatii(text, norm))
        if not rez:
            rez.append(Analiza(text, text, None, "X", {}, "necunoscut", dovezi=["cuvânt necunoscut: nu e în nicio sursă și nu se potrivește cu nicio regulă"]))
        return rez

    def _din_terminatii(self, text: str, norm: str) -> list[Analiza]:
        rez: list[Analiza] = []
        vazute: set[tuple[str, str, str]] = set()
        for term, pos, tr in TERMINATII:
            if not norm.endswith(term) or len(norm) - len(term) < 2:
                continue
            radacina = norm[: -len(term)]
            # căutăm o lemă care să înceapă cu rădăcina (substantiv: lema = rădăcina sau rădăcina + ă/e/u)
            candidati = []
            if pos == "NOUN":
                candidati = [radacina, radacina + "ă", radacina + "e", radacina + "u", radacina + "ie"]
            elif pos == "VERB":
                candidati = [radacina + "a", radacina + "i", radacina + "e", radacina + "ea", radacina[:-1] + "a" if term.startswith("e") else radacina + "a"]
            elif pos == "ADV":
                candidati = []
            gasit = False
            for c in candidati:
                for lx in self.baza.cauta_lema(c, pos):
                    cheie = (lx["id"], tr, pos)
                    if cheie in vazute:
                        continue
                    vazute.add(cheie)
                    gasit = True
                    rez.append(Analiza(text, lx["lema"], lx["id"], pos, desparte_trasaturi(tr), "ipoteza", "", lx["gen"],
                                       dovezi=[f"formă dedusă: lema „{lx['lema']}” există în bază, terminația „-{term}” sugerează {tr or pos}; forma nu e în bază"]))
            if not gasit and pos in ("NOUN", "VERB", "ADV"):
                cheie = ("", tr, pos)
                if cheie not in vazute:
                    vazute.add(cheie)
                    rez.append(Analiza(text, "?", None, pos, desparte_trasaturi(tr), "necunoscut",
                                       dovezi=[f"cuvânt necunoscut; terminația „-{term}” sugerează {pos} ({tr or 'fără trăsături'})"]))
        return rez
