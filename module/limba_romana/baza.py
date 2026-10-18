"""Baza lingvistică: stocare SQLite, migrări, integritate, export/import.

Doar biblioteca standard (sqlite3). Toate scrierile trec pe aici, ca să rămână valabile regulile:
  - orice rând are sursă (`sursa_id`) înregistrată în `surse`;
  - trăsăturile se scriu canonic (`canonic_trasaturi`): chei sortate, „Cheie=Valoare|Cheie=Valoare”;
  - formele au una sau mai multe proveniențe; statutul formei se recalculează din proveniențe.
"""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

from . import schema
from .text import fara_diacritice, normalizeaza

CALE_IMPLICITA = Path(__file__).resolve().parent / "_baza" / "limba_romana.sqlite"


def canonic_trasaturi(trasaturi: dict[str, str] | str | None) -> str:
    """„Number=Sing|Case=Acc,Nom” → „Case=Acc,Nom|Number=Sing” (chei sortate, fără dubluri)."""
    if not trasaturi or trasaturi == "_":
        return ""
    if isinstance(trasaturi, str):
        perechi = dict(p.split("=", 1) for p in trasaturi.split("|") if "=" in p)
    else:
        perechi = dict(trasaturi)
    return "|".join(f"{k}={perechi[k]}" for k in sorted(perechi))


def desparte_trasaturi(sir: str) -> dict[str, str]:
    return dict(p.split("=", 1) for p in sir.split("|") if "=" in p) if sir else {}


def acum() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Baza:
    """Legătura cu fișierul SQLite. Se folosește ca `with Baza(cale) as b:` sau direct."""

    def __init__(self, cale: str | Path | None = None, doar_citire: bool = False):
        self.cale = Path(cale) if cale else CALE_IMPLICITA
        self.doar_citire = doar_citire
        if doar_citire:
            self.con = sqlite3.connect(f"file:{self.cale}?mode=ro", uri=True)
        else:
            self.cale.parent.mkdir(parents=True, exist_ok=True)
            self.con = sqlite3.connect(self.cale)
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys = ON")
        self.con.execute("PRAGMA journal_mode = WAL" if not doar_citire else "PRAGMA query_only = ON")
        self.con.execute("PRAGMA synchronous = NORMAL")
        if not doar_citire:
            self.migreaza()

    # ---- ciclu de viață ------------------------------------------------------------------------------
    def __enter__(self) -> "Baza":
        return self

    def __exit__(self, *_: Any) -> None:
        self.inchide()

    def inchide(self) -> None:
        self.con.commit()
        self.con.close()

    def migreaza(self) -> list[int]:
        """Aplică migrările care lipsesc, în ordine. Întoarce versiunile aplicate acum."""
        self.con.executescript(schema.MIGRATII[1].split("CREATE TABLE IF NOT EXISTS surse")[0])  # tabela migratii
        aplicate = {r[0] for r in self.con.execute("SELECT versiune FROM migratii")}
        noi = []
        for versiune in sorted(schema.MIGRATII):
            if versiune in aplicate:
                continue
            self.con.executescript(schema.MIGRATII[versiune])
            self.con.execute("INSERT OR IGNORE INTO migratii(versiune, aplicata) VALUES (?, ?)", (versiune, acum()))
            noi.append(versiune)
        self.con.commit()
        return noi

    def versiune_schema(self) -> int:
        r = self.con.execute("SELECT MAX(versiune) FROM migratii").fetchone()
        return int(r[0] or 0)

    # ---- scriere ----------------------------------------------------------------------------------------
    def adauga_sursa(self, id: str, nume: str, licenta: str, url: str = "", versiune: str = "", atribuire: str = "",
                     obligatii: str = "", fisiere: list[str] | None = None, transformari: str = "", limitari: str = "",
                     data_descarcarii: str = "") -> None:
        self.con.execute(
            "INSERT OR REPLACE INTO surse(id, nume, url, versiune, data_descarcarii, licenta, atribuire, obligatii, fisiere, transformari, limitari)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (id, nume, url, versiune, data_descarcarii, licenta, atribuire, obligatii, json.dumps(fisiere or [], ensure_ascii=False), transformari, limitari),
        )

    def adauga_lexem(self, id: str, lema: str, pos: str, omonim: int, statut: str, sursa_id: str, gen: str | None = None,
                     clasa: str | None = None, multicuvant: bool = False, atribute: dict | None = None, detalii_sursa: str = "") -> bool:
        """Întoarce True dacă lexemul e nou; dacă există deja, îi adaugă doar sursa (și completează genul/clasa lipsă)."""
        exista = self.con.execute("SELECT gen, clasa, atribute FROM lexeme WHERE id = ?", (id,)).fetchone()
        if exista is None:
            self.con.execute(
                "INSERT INTO lexeme(id, lema, lema_norm, pos, omonim, gen, clasa, multicuvant, statut, sursa_id, atribute) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (id, lema, normalizeaza(lema), pos, omonim, gen, clasa, int(multicuvant), statut, sursa_id, json.dumps(atribute or {}, ensure_ascii=False)),
            )
            nou = True
        else:
            nou = False
            gen_nou = exista["gen"] or gen
            clasa_noua = exista["clasa"] or clasa
            atr = json.loads(exista["atribute"] or "{}")
            if atribute:
                for k, v in atribute.items():
                    atr.setdefault(k, v)
            self.con.execute("UPDATE lexeme SET gen = ?, clasa = ?, atribute = ?, statut = CASE WHEN statut = 'confirmat' THEN statut ELSE 'confirmat' END WHERE id = ?",
                             (gen_nou, clasa_noua, json.dumps(atr, ensure_ascii=False), id))
        self.con.execute("INSERT OR IGNORE INTO lexeme_surse(lexem_id, sursa_id, detalii) VALUES (?,?,?)", (id, sursa_id, detalii_sursa))
        return nou

    def adauga_forma(self, forma: str, lexem_id: str, trasaturi: dict[str, str] | str | None, statut: str, sursa_id: str,
                     origine: str, detalii: str = "", frecventa: int = 0) -> int:
        """Adaugă o formă (sau o proveniență nouă pentru una existentă). Întoarce id-ul formei."""
        tr = canonic_trasaturi(trasaturi)
        r = self.con.execute("SELECT id, statut FROM forme WHERE forma = ? AND lexem_id = ? AND trasaturi = ?", (forma, lexem_id, tr)).fetchone()
        if r is None:
            cur = self.con.execute(
                "INSERT INTO forme(forma, forma_norm, forma_plata, lexem_id, trasaturi, statut) VALUES (?,?,?,?,?,?)",
                (forma, normalizeaza(forma), fara_diacritice(forma), lexem_id, tr, statut),
            )
            forma_id = int(cur.lastrowid)
        else:
            forma_id = int(r["id"])
        self.con.execute(
            "INSERT INTO forme_provenienta(forma_id, sursa_id, origine, detalii, frecventa) VALUES (?,?,?,?,?)"
            " ON CONFLICT(forma_id, sursa_id, origine) DO UPDATE SET frecventa = frecventa + excluded.frecventa",
            (forma_id, sursa_id, origine, detalii, frecventa),
        )
        return forma_id

    def adauga_forme_in_bloc(self, randuri: Iterable[tuple[str, str, str, str, str, str, str, int]]) -> int:
        """Varianta rapidă pentru importuri mari: (forma, lexem_id, trasaturi_canonice, statut, sursa_id, origine, detalii, frecventa).
        Formele noi se inserează; proveniențele se adaugă/cumulează. Întoarce numărul de forme noi."""
        noi = 0
        for forma, lexem_id, tr, statut, sursa_id, origine, detalii, frecventa in randuri:
            cur = self.con.execute(
                "INSERT OR IGNORE INTO forme(forma, forma_norm, forma_plata, lexem_id, trasaturi, statut) VALUES (?,?,?,?,?,?)",
                (forma, normalizeaza(forma), fara_diacritice(forma), lexem_id, tr, statut),
            )
            if cur.rowcount:
                noi += 1
                forma_id = cur.lastrowid
            else:
                forma_id = self.con.execute("SELECT id FROM forme WHERE forma = ? AND lexem_id = ? AND trasaturi = ?", (forma, lexem_id, tr)).fetchone()[0]
            self.con.execute(
                "INSERT INTO forme_provenienta(forma_id, sursa_id, origine, detalii, frecventa) VALUES (?,?,?,?,?)"
                " ON CONFLICT(forma_id, sursa_id, origine) DO UPDATE SET frecventa = frecventa + excluded.frecventa",
                (forma_id, sursa_id, origine, detalii, frecventa),
            )
        return noi

    def adauga_concept(self, id: str, pos: str, definitie: str | None, sursa_id: str, ili: str | None = None, atribute: dict | None = None) -> None:
        self.con.execute("INSERT OR REPLACE INTO concepte(id, pos, definitie, ili, sursa_id, atribute) VALUES (?,?,?,?,?,?)",
                         (id, pos, definitie, ili, sursa_id, json.dumps(atribute or {}, ensure_ascii=False)))

    def adauga_sens(self, id: str, lexem_id: str, concept_id: str | None, definitie: str | None, nr: int, sursa_id: str,
                    statut: str = "importat", etichete: list[str] | None = None) -> None:
        self.con.execute("INSERT OR REPLACE INTO sensuri(id, lexem_id, concept_id, definitie, nr, etichete, sursa_id, statut) VALUES (?,?,?,?,?,?,?,?)",
                         (id, lexem_id, concept_id, definitie, nr, json.dumps(etichete or [], ensure_ascii=False), sursa_id, statut))

    def adauga_relatie_semantica(self, tip: str, nivel: str, de_la: str, la: str, sursa_id: str, detalii: str = "") -> None:
        self.con.execute("INSERT OR IGNORE INTO relatii_semantice(tip, nivel, de_la, la, sursa_id, detalii) VALUES (?,?,?,?,?,?)",
                         (tip, nivel, de_la, la, sursa_id, detalii))

    def adauga_regula(self, id: str, tip: str, nume: str, descriere: str, definitie: dict | str | None, justificare: str, statut: str, versiune: str = "1") -> None:
        self.con.execute("INSERT OR REPLACE INTO reguli(id, tip, nume, descriere, definitie, justificare, statut, versiune) VALUES (?,?,?,?,?,?,?,?)",
                         (id, tip, nume, descriere, json.dumps(definitie, ensure_ascii=False) if not isinstance(definitie, str) else definitie, justificare, statut, versiune))

    def adauga_exemplu(self, id: str, text: str, sursa_id: str, set_: str, cuvinte: list[dict], gen: str = "", doc: str = "") -> None:
        self.con.execute("INSERT OR REPLACE INTO exemple(id, text, sursa_id, set_, gen, doc, cuvinte) VALUES (?,?,?,?,?,?,?)",
                         (id, text, sursa_id, set_, gen, doc, json.dumps(cuvinte, ensure_ascii=False)))
        self.con.execute("DELETE FROM exemple_cuvinte WHERE exemplu_id = ?", (id,))
        self.con.executemany(
            "INSERT INTO exemple_cuvinte(exemplu_id, idx, forma, forma_norm, lema_norm, upos, xpos, trasaturi, cap, rel) VALUES (?,?,?,?,?,?,?,?,?,?)",
            [(id, c["idx"], c["forma"], normalizeaza(c["forma"]), normalizeaza(c.get("lema", "")), c["upos"], c.get("xpos"),
              canonic_trasaturi(c.get("trasaturi")), c["cap"], c["rel"]) for c in cuvinte],
        )

    def adauga_validare(self, nume: str, versiune_motor: str, rezultat: dict) -> int:
        cur = self.con.execute("INSERT INTO validari(nume, data, versiune_motor, rezultat) VALUES (?,?,?,?)",
                               (nume, acum(), versiune_motor, json.dumps(rezultat, ensure_ascii=False)))
        return int(cur.lastrowid)

    def seteaza_trasaturi(self, inventar: Iterable[tuple[str, str, str]]) -> None:
        self.con.executemany("INSERT OR REPLACE INTO trasaturi(cheie, valoare, descriere) VALUES (?,?,?)", list(inventar))

    def seteaza_relatii_sintactice(self, inventar: Iterable[tuple[str, str, int]]) -> None:
        self.con.executemany("INSERT OR REPLACE INTO relatii_sintactice(tip, descriere, frecventa) VALUES (?,?,?)", list(inventar))

    def commit(self) -> None:
        self.con.commit()

    def adauga_ortografie(self, forme: Iterable[tuple[str, str, str]]) -> None:
        """(formă, sursa_id, detalii) — cuvinte cunoscute doar ortografic."""
        self.con.executemany("INSERT OR IGNORE INTO ortografie(forma, forma_norm, sursa_id, detalii) VALUES (?,?,?,?)",
                             [(f, normalizeaza(f), s, d) for f, s, d in forme])

    def cunoscut_ortografic(self, forma: str) -> list[dict]:
        return [dict(r) for r in self.con.execute("SELECT * FROM ortografie WHERE forma_norm = ?", (normalizeaza(forma),))]

    def fuzioneaza_forme_fara_trasaturi(self) -> dict[str, int]:
        """O formă generată de o regulă FĂRĂ trăsături (de ex. din Hunspell) e aceeași formă cu rândul care are
        trăsături pentru același lexem (de ex. din Wiktionary). Mutăm proveniențele pe rândul cu trăsături (pe toate,
        dacă forma e sincretică) și ștergem rândul gol, ca statutul „validat” să aibă sens."""
        mutate = sterse = 0
        goale = self.con.execute(
            "SELECT f.id, f.forma, f.lexem_id FROM forme f WHERE f.trasaturi = '' AND EXISTS ("
            "SELECT 1 FROM forme g WHERE g.forma = f.forma AND g.lexem_id = f.lexem_id AND g.trasaturi <> '')").fetchall()
        for r in goale:
            tinte = [x[0] for x in self.con.execute("SELECT id FROM forme WHERE forma = ? AND lexem_id = ? AND trasaturi <> ''", (r["forma"], r["lexem_id"]))]
            prov = self.con.execute("SELECT sursa_id, origine, detalii, frecventa FROM forme_provenienta WHERE forma_id = ?", (r["id"],)).fetchall()
            for t in tinte:
                for p in prov:
                    self.con.execute(
                        "INSERT INTO forme_provenienta(forma_id, sursa_id, origine, detalii, frecventa) VALUES (?,?,?,?,?)"
                        " ON CONFLICT(forma_id, sursa_id, origine) DO UPDATE SET frecventa = MAX(frecventa, excluded.frecventa)",
                        (t, p["sursa_id"], p["origine"], (p["detalii"] + "; " if p["detalii"] else "") + "mutat de pe rândul fără trăsături", p["frecventa"]))
                    mutate += 1
            self.con.execute("DELETE FROM forme_provenienta WHERE forma_id = ?", (r["id"],))
            self.con.execute("DELETE FROM forme WHERE id = ?", (r["id"],))
            sterse += 1
        self.con.commit()
        return {"proveniente_mutate": mutate, "randuri_sterse": sterse}

    # ---- statutul formelor --------------------------------------------------------------------------------
    def recalculeaza_statut_forme(self) -> dict[str, int]:
        """Statutul unei forme vine din proveniențele ei:
        - `validat`: cel puțin două surse independente, sau o sursă care o atestă + o regulă care o generează;
        - `atestat`: cel puțin o proveniență de tip atestare (corpus, tabel de flexiune, intrare explicită);
        - `generat`: doar reguli (afixe Hunspell / paradigme proprii)."""
        self.con.execute("""
            WITH p AS (
                SELECT forma_id,
                       COUNT(DISTINCT sursa_id) AS surse,
                       SUM(CASE WHEN origine LIKE 'atestare%' THEN 1 ELSE 0 END) AS atestari,
                       SUM(CASE WHEN origine LIKE 'regula%' THEN 1 ELSE 0 END) AS reguli
                FROM forme_provenienta GROUP BY forma_id)
            UPDATE forme SET statut = (
                SELECT CASE WHEN p.surse >= 2 THEN 'validat'
                            WHEN p.atestari > 0 THEN 'atestat'
                            ELSE 'generat' END FROM p WHERE p.forma_id = forme.id)
        """)
        rez = {r[0]: r[1] for r in self.con.execute("SELECT statut, COUNT(*) FROM forme GROUP BY statut")}
        self.con.commit()
        return rez

    # ---- citire ----------------------------------------------------------------------------------------
    def surse(self) -> list[dict]:
        return [dict(r) for r in self.con.execute("SELECT * FROM surse ORDER BY id")]

    def cauta_forma(self, forma: str, si_fara_diacritice: bool = True) -> list[dict]:
        """Toate analizele cunoscute pentru o formă: lexem + trăsături + proveniențe. Potrivirea fără diacritice e marcată."""
        norm = normalizeaza(forma)
        randuri = self._forme_dupa_coloana("forma_norm", norm)
        for r in randuri:
            r["potrivire"] = "exacta"
        if not randuri and si_fara_diacritice:
            randuri = self._forme_dupa_coloana("forma_plata", fara_diacritice(forma))
            for r in randuri:
                r["potrivire"] = "fara_diacritice"
        return randuri

    def _forme_dupa_coloana(self, coloana: str, valoare: str) -> list[dict]:
        sql = f"""
            SELECT f.id AS forma_id, f.forma, f.trasaturi, f.statut, l.id AS lexem_id, l.lema, l.pos, l.omonim, l.gen, l.clasa, l.multicuvant, l.atribute
            FROM forme f JOIN lexeme l ON l.id = f.lexem_id WHERE f.{coloana} = ? ORDER BY l.pos, l.lema, f.trasaturi"""
        rezultat = []
        for r in self.con.execute(sql, (valoare,)):
            d = dict(r)
            d["atribute"] = json.loads(d["atribute"] or "{}")
            d["provenienta"] = [dict(p) for p in self.con.execute(
                "SELECT sursa_id, origine, detalii, frecventa FROM forme_provenienta WHERE forma_id = ? ORDER BY sursa_id, origine", (r["forma_id"],))]
            rezultat.append(d)
        return rezultat

    def cauta_lema(self, lema: str, pos: str | None = None) -> list[dict]:
        norm = normalizeaza(lema)
        if pos:
            randuri = self.con.execute("SELECT * FROM lexeme WHERE lema_norm = ? AND pos = ? ORDER BY omonim", (norm, pos))
        else:
            randuri = self.con.execute("SELECT * FROM lexeme WHERE lema_norm = ? ORDER BY pos, omonim", (norm,))
        rezultat = []
        for r in randuri:
            d = dict(r)
            d["atribute"] = json.loads(d["atribute"] or "{}")
            d["surse"] = [dict(s) for s in self.con.execute("SELECT sursa_id, detalii FROM lexeme_surse WHERE lexem_id = ?", (r["id"],))]
            rezultat.append(d)
        return rezultat

    def lexem(self, lexem_id: str) -> dict | None:
        r = self.con.execute("SELECT * FROM lexeme WHERE id = ?", (lexem_id,)).fetchone()
        if r is None:
            return None
        d = dict(r)
        d["atribute"] = json.loads(d["atribute"] or "{}")
        return d

    def forme_lexem(self, lexem_id: str) -> list[dict]:
        rezultat = []
        for r in self.con.execute("SELECT id, forma, trasaturi, statut FROM forme WHERE lexem_id = ? ORDER BY trasaturi, forma", (lexem_id,)):
            d = dict(r)
            d["provenienta"] = [dict(p) for p in self.con.execute(
                "SELECT sursa_id, origine, detalii, frecventa FROM forme_provenienta WHERE forma_id = ? ORDER BY sursa_id", (r["id"],))]
            rezultat.append(d)
        return rezultat

    def sensuri_lexem(self, lexem_id: str) -> list[dict]:
        rezultat = []
        for r in self.con.execute(
                "SELECT s.*, c.definitie AS definitie_concept, c.ili FROM sensuri s LEFT JOIN concepte c ON c.id = s.concept_id WHERE s.lexem_id = ? ORDER BY s.sursa_id, s.nr", (lexem_id,)):
            d = dict(r)
            d["etichete"] = json.loads(d["etichete"] or "[]")
            rezultat.append(d)
        return rezultat

    def concept(self, concept_id: str) -> dict | None:
        r = self.con.execute("SELECT * FROM concepte WHERE id = ?", (concept_id,)).fetchone()
        if r is None:
            return None
        d = dict(r)
        d["atribute"] = json.loads(d["atribute"] or "{}")
        d["lexeme"] = [dict(x) for x in self.con.execute(
            "SELECT l.id AS lexem_id, l.lema, l.pos, s.id AS sens_id FROM sensuri s JOIN lexeme l ON l.id = s.lexem_id WHERE s.concept_id = ? ORDER BY l.lema", (concept_id,))]
        return d

    def relatii(self, de_la: str, tip: str | None = None, directie: str = "iesire") -> list[dict]:
        col, alt = ("de_la", "la") if directie == "iesire" else ("la", "de_la")
        if tip:
            q = self.con.execute(f"SELECT tip, nivel, {alt} AS celalalt, sursa_id, detalii FROM relatii_semantice WHERE {col} = ? AND tip = ?", (de_la, tip))
        else:
            q = self.con.execute(f"SELECT tip, nivel, {alt} AS celalalt, sursa_id, detalii FROM relatii_semantice WHERE {col} = ?", (de_la,))
        return [dict(r) for r in q]

    def lant(self, concept_id: str, tip: str = "hypernym", maxim: int = 30) -> list[str]:
        """Urcă pe relația `tip` (de ex. hiperonim) până la rădăcină; se oprește la cicluri."""
        lant, vazute, curent = [], {concept_id}, concept_id
        for _ in range(maxim):
            urm = [r["celalalt"] for r in self.relatii(curent, tip)]
            if not urm:
                break
            urm.sort()
            curent = urm[0]
            if curent in vazute:
                break
            vazute.add(curent)
            lant.append(curent)
        return lant

    def exemple_cu(self, lema: str | None = None, forma: str | None = None, limita: int = 10, set_: str | None = None) -> list[dict]:
        cond, par = [], []
        if lema:
            cond.append("c.lema_norm = ?"); par.append(normalizeaza(lema))
        if forma:
            cond.append("c.forma_norm = ?"); par.append(normalizeaza(forma))
        if set_:
            cond.append("e.set_ = ?"); par.append(set_)
        unde = " AND ".join(cond) if cond else "1=1"
        q = self.con.execute(f"SELECT DISTINCT e.id, e.text, e.set_, e.gen, e.sursa_id FROM exemple e JOIN exemple_cuvinte c ON c.exemplu_id = e.id WHERE {unde} ORDER BY e.id LIMIT ?", (*par, limita))
        return [dict(r) for r in q]

    def exemplu(self, id: str) -> dict | None:
        r = self.con.execute("SELECT * FROM exemple WHERE id = ?", (id,)).fetchone()
        if r is None:
            return None
        d = dict(r)
        d["cuvinte"] = json.loads(d["cuvinte"])
        return d

    def reguli(self, tip: str | None = None) -> list[dict]:
        q = self.con.execute("SELECT * FROM reguli WHERE tip = ? ORDER BY id", (tip,)) if tip else self.con.execute("SELECT * FROM reguli ORDER BY id")
        return [dict(r) for r in q]

    def statistici(self) -> dict[str, Any]:
        s: dict[str, Any] = {"cale": str(self.cale), "versiune_schema": self.versiune_schema()}
        for t in ("surse", "lexeme", "forme", "forme_provenienta", "concepte", "sensuri", "relatii_semantice", "relatii_sintactice", "reguli", "exemple", "exemple_cuvinte", "trasaturi", "validari", "ortografie"):
            s[t] = self.con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        s["lexeme_pe_categorie"] = {r[0]: r[1] for r in self.con.execute("SELECT pos, COUNT(*) FROM lexeme GROUP BY pos ORDER BY 2 DESC")}
        s["forme_pe_statut"] = {r[0]: r[1] for r in self.con.execute("SELECT statut, COUNT(*) FROM forme GROUP BY statut")}
        s["lexeme_pe_sursa"] = {r[0]: r[1] for r in self.con.execute("SELECT sursa_id, COUNT(*) FROM lexeme_surse GROUP BY sursa_id")}
        s["forme_pe_sursa"] = {r[0]: r[1] for r in self.con.execute("SELECT sursa_id, COUNT(DISTINCT forma_id) FROM forme_provenienta GROUP BY sursa_id")}
        s["exemple_pe_set"] = {r[0]: r[1] for r in self.con.execute("SELECT set_, COUNT(*) FROM exemple GROUP BY set_")}
        s["relatii_semantice_pe_tip"] = {r[0]: r[1] for r in self.con.execute("SELECT tip, COUNT(*) FROM relatii_semantice GROUP BY tip ORDER BY 2 DESC")}
        return s

    # ---- integritate --------------------------------------------------------------------------------------
    def verifica_integritate(self, maxim_exemple: int = 5) -> dict[str, Any]:
        """Rulează toate verificările din schema.VERIFICARI_INTEGRITATE + detectarea ciclurilor în ierarhii.
        Întoarce {nume: {probleme: n, exemple: [...]}} și `ok` (True dacă nimic nu a ieșit)."""
        raport: dict[str, Any] = {"verificari": {}, "ok": True}
        for nume, sql in schema.VERIFICARI_INTEGRITATE:
            randuri = self.con.execute(sql).fetchall()
            raport["verificari"][nume] = {"probleme": len(randuri), "exemple": [tuple(r) for r in randuri[:maxim_exemple]]}
            if randuri:
                raport["ok"] = False
        # ciclurile din ierarhiile semantice sunt erori ale SURSEI (le raportăm ca avertismente, nu ca defect structural al bazei)
        cicluri = self.detecteaza_cicluri(schema.RELATII_FARA_CICLURI)
        raport["avertismente"] = {"cicluri în ierarhii (hypernym, mero_*) — provin din sursă": {"probleme": len(cicluri), "exemple": cicluri[:maxim_exemple]}}
        sqlite_ok = self.con.execute("PRAGMA integrity_check").fetchone()[0]
        raport["verificari"]["sqlite integrity_check"] = {"probleme": 0 if sqlite_ok == "ok" else 1, "exemple": [] if sqlite_ok == "ok" else [sqlite_ok]}
        fk = self.con.execute("PRAGMA foreign_key_check").fetchall()
        raport["verificari"]["chei străine (sqlite)"] = {"probleme": len(fk), "exemple": [tuple(r) for r in fk[:maxim_exemple]]}
        if sqlite_ok != "ok" or fk:
            raport["ok"] = False
        return raport

    def detecteaza_cicluri(self, tipuri: tuple[str, ...]) -> list[list[str]]:
        """Găsește cicluri în graful relațiilor date (fiecare tip separat). Întoarce lista ciclurilor (liste de id-uri)."""
        cicluri: list[list[str]] = []
        for tip in tipuri:
            graf: dict[str, list[str]] = defaultdict(list)
            for r in self.con.execute("SELECT de_la, la FROM relatii_semantice WHERE tip = ?", (tip,)):
                graf[r[0]].append(r[1])
            # Kahn: nodurile rămase după eliminarea celor fără intrări sunt într-un ciclu
            grad: dict[str, int] = defaultdict(int)
            for a, bs in graf.items():
                grad.setdefault(a, 0)
                for b in bs:
                    grad[b] += 1
            coada = deque([n for n, g in grad.items() if g == 0])
            while coada:
                n = coada.popleft()
                for b in graf.get(n, []):
                    grad[b] -= 1
                    if grad[b] == 0:
                        coada.append(b)
            ramase = {n for n, g in grad.items() if g > 0}
            while ramase:
                start = min(ramase)
                drum, vazute, curent = [start], {start}, start
                while True:
                    urm = [b for b in graf.get(curent, []) if b in ramase]
                    if not urm:
                        break
                    curent = min(urm)
                    if curent in vazute:
                        drum.append(curent)
                        break
                    vazute.add(curent)
                    drum.append(curent)
                cicluri.append([tip] + drum)
                ramase -= vazute
        return cicluri

    # ---- export / import -------------------------------------------------------------------------------------
    TABELE_EXPORT = ("surse", "lexeme", "lexeme_surse", "trasaturi", "forme", "forme_provenienta", "concepte", "sensuri",
                     "relatii_semantice", "relatii_sintactice", "reguli", "exemple", "exemple_cuvinte", "contexte", "validari", "ortografie")

    def exporta(self, director: str | Path, doar_sursa: str | None = None) -> dict[str, int]:
        """Scrie câte un fișier JSONL pe tabelă (rânduri în ordine deterministă). `doar_sursa` filtrează rândurile cu `sursa_id`."""
        director = Path(director)
        director.mkdir(parents=True, exist_ok=True)
        numar: dict[str, int] = {}
        for t in self.TABELE_EXPORT:
            coloane = [r[1] for r in self.con.execute(f"PRAGMA table_info({t})")]
            cond = ""
            if doar_sursa and "sursa_id" in coloane:
                cond = f" WHERE sursa_id = '{doar_sursa}'"
            ordine = ", ".join(coloane[:3])
            with open(director / f"{t}.jsonl", "w", encoding="utf8") as f:
                n = 0
                for r in self.con.execute(f"SELECT * FROM {t}{cond} ORDER BY {ordine}"):
                    f.write(json.dumps(dict(r), ensure_ascii=False) + "\n")
                    n += 1
            numar[t] = n
        (director / "export.json").write_text(json.dumps({"data": acum(), "versiune_schema": self.versiune_schema(), "randuri": numar, "doar_sursa": doar_sursa}, ensure_ascii=False, indent=2), "utf8")
        return numar

    def importa(self, director: str | Path) -> dict[str, int]:
        """Citește fișierele JSONL scrise de `exporta` (în ordinea tabelelor, ca să respecte cheile străine)."""
        director = Path(director)
        numar: dict[str, int] = {}
        for t in self.TABELE_EXPORT:
            cale = director / f"{t}.jsonl"
            if not cale.exists():
                continue
            coloane = [r[1] for r in self.con.execute(f"PRAGMA table_info({t})")]
            n = 0
            with open(cale, encoding="utf8") as f:
                lot = []
                for linie in f:
                    d = json.loads(linie)
                    lot.append(tuple(d.get(c) for c in coloane))
                    n += 1
                    if len(lot) >= 5000:
                        self.con.executemany(f"INSERT OR REPLACE INTO {t}({', '.join(coloane)}) VALUES ({', '.join('?' for _ in coloane)})", lot)
                        lot = []
                if lot:
                    self.con.executemany(f"INSERT OR REPLACE INTO {t}({', '.join(coloane)}) VALUES ({', '.join('?' for _ in coloane)})", lot)
            numar[t] = n
        self.con.commit()
        return numar

    def iter_lexeme(self) -> Iterator[dict]:
        for r in self.con.execute("SELECT * FROM lexeme ORDER BY id"):
            yield dict(r)
