"""Schema bazei lingvistice (SQLite) și migrările ei.

Principiul: fiecare lucru are tabela lui și nu se confundă cu altul.
  - `lexeme`      = unități de dicționar (lemă + categorie + număr de omonim), cu identificator stabil;
  - `forme`       = forme de suprafață (cuvinte așa cum apar în text), legate de un lexem și de trăsături;
  - `forme_provenienta` = de unde știm forma (sursa, regula, frecvența) — o formă poate avea mai multe dovezi;
  - `trasaturi`   = inventarul trăsăturilor morfologice (cheie = valoare), ca să nu apară valori inventate;
  - `concepte`    = concepte (synseturi) — un înțeles, independent de cuvânt;
  - `sensuri`     = legătura lexem ↔ concept (sensul unui cuvânt), cu definiția lui;
  - `relatii_semantice`  = relații între concepte / sensuri / lexeme (hiperonim, antonim, parte–întreg…);
  - `relatii_sintactice` = inventarul relațiilor de dependență (nsubj, obj, amod…) cu descrieri;
  - `reguli`      = regulile explicite (morfologie, acord, sintaxă, dezambiguizare), cu statut și justificare;
  - `exemple` + `exemple_cuvinte` = propoziții adnotate (corpus), cu setul din care fac parte;
  - `contexte`    = contexte de conversație furnizate motorului (opțional);
  - `ortografie`  = cuvinte cunoscute doar ortografic (din dicționarul ortografic, fără lemă/categorie);
  - `surse`       = proveniența și licențele;
  - `validari`    = rezultatele rulărilor de test / validare / acoperire.

Migrările sunt numerotate; `baza.Baza` aplică doar ce lipsește și ține evidența în `migratii`.
"""

from __future__ import annotations

VERSIUNE_SCHEMA = 2

# Categoriile gramaticale folosite în toată baza (UPOS, Universal Dependencies) + marcaje proprii.
CATEGORII = {
    "NOUN": "substantiv comun", "PROPN": "substantiv propriu", "VERB": "verb", "AUX": "verb auxiliar",
    "ADJ": "adjectiv", "ADV": "adverb", "PRON": "pronume", "DET": "determinant (articol, adjectiv pronominal)",
    "NUM": "numeral", "ADP": "prepoziție", "CCONJ": "conjuncție coordonatoare", "SCONJ": "conjuncție subordonatoare",
    "PART": "particulă (a, să, nu…)", "INTJ": "interjecție", "PUNCT": "punctuație", "SYM": "simbol",
    "X": "altceva / necunoscut", "ABBR": "abreviere (categorie necunoscută)",
}

STATUTE_FORME = {
    "atestat": "forma apare explicit într-o sursă (corpus adnotat, tabel de flexiune, intrare de dicționar)",
    "generat": "forma a fost produsă de o regulă (afix Hunspell sau paradigmă proprie), fără confirmare independentă",
    "validat": "forma e confirmată de cel puțin două surse independente (de ex. generată + atestată)",
    "ipoteza": "forma a fost propusă de analizator pentru un cuvânt necunoscut; nu e în bază",
}

STATUTE_LEXEME = {
    "importat": "lexemul vine direct dintr-o sursă (lemă + categorie)",
    "derivat": "lema a fost derivată prin regulă dintr-o intrare de sursă (de ex. infinitivul din forma de persoana I)",
    "confirmat": "lexemul apare în cel puțin două surse independente",
}

MIGRATII: dict[int, str] = {
    1: """
    CREATE TABLE IF NOT EXISTS migratii (
        versiune INTEGER PRIMARY KEY,
        aplicata TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS surse (
        id TEXT PRIMARY KEY,
        nume TEXT NOT NULL,
        url TEXT,
        versiune TEXT,
        data_descarcarii TEXT,
        licenta TEXT NOT NULL,
        atribuire TEXT,
        obligatii TEXT,
        fisiere TEXT,
        transformari TEXT,
        limitari TEXT
    );
    CREATE TABLE IF NOT EXISTS lexeme (
        id TEXT PRIMARY KEY,
        lema TEXT NOT NULL,
        lema_norm TEXT NOT NULL,
        pos TEXT NOT NULL,
        omonim INTEGER NOT NULL DEFAULT 0,
        gen TEXT,
        clasa TEXT,
        multicuvant INTEGER NOT NULL DEFAULT 0,
        statut TEXT NOT NULL,
        sursa_id TEXT NOT NULL REFERENCES surse(id),
        atribute TEXT
    );
    CREATE INDEX IF NOT EXISTS ix_lexeme_lema ON lexeme(lema_norm);
    CREATE INDEX IF NOT EXISTS ix_lexeme_lema_pos ON lexeme(lema_norm, pos);
    CREATE TABLE IF NOT EXISTS lexeme_surse (
        lexem_id TEXT NOT NULL REFERENCES lexeme(id),
        sursa_id TEXT NOT NULL REFERENCES surse(id),
        detalii TEXT,
        PRIMARY KEY (lexem_id, sursa_id)
    );
    CREATE TABLE IF NOT EXISTS trasaturi (
        cheie TEXT NOT NULL,
        valoare TEXT NOT NULL,
        descriere TEXT,
        PRIMARY KEY (cheie, valoare)
    );
    CREATE TABLE IF NOT EXISTS forme (
        id INTEGER PRIMARY KEY,
        forma TEXT NOT NULL,
        forma_norm TEXT NOT NULL,
        forma_plata TEXT NOT NULL,
        lexem_id TEXT NOT NULL REFERENCES lexeme(id),
        trasaturi TEXT NOT NULL DEFAULT '',
        statut TEXT NOT NULL,
        UNIQUE (forma, lexem_id, trasaturi)
    );
    CREATE INDEX IF NOT EXISTS ix_forme_norm ON forme(forma_norm);
    CREATE INDEX IF NOT EXISTS ix_forme_plata ON forme(forma_plata);
    CREATE INDEX IF NOT EXISTS ix_forme_lexem ON forme(lexem_id);
    CREATE TABLE IF NOT EXISTS forme_provenienta (
        forma_id INTEGER NOT NULL REFERENCES forme(id),
        sursa_id TEXT NOT NULL REFERENCES surse(id),
        origine TEXT NOT NULL,
        detalii TEXT,
        frecventa INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (forma_id, sursa_id, origine)
    );
    CREATE TABLE IF NOT EXISTS concepte (
        id TEXT PRIMARY KEY,
        pos TEXT NOT NULL,
        definitie TEXT,
        ili TEXT,
        sursa_id TEXT NOT NULL REFERENCES surse(id),
        atribute TEXT
    );
    CREATE TABLE IF NOT EXISTS sensuri (
        id TEXT PRIMARY KEY,
        lexem_id TEXT NOT NULL REFERENCES lexeme(id),
        concept_id TEXT REFERENCES concepte(id),
        definitie TEXT,
        nr INTEGER NOT NULL DEFAULT 1,
        etichete TEXT,
        sursa_id TEXT NOT NULL REFERENCES surse(id),
        statut TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_sensuri_lexem ON sensuri(lexem_id);
    CREATE INDEX IF NOT EXISTS ix_sensuri_concept ON sensuri(concept_id);
    CREATE TABLE IF NOT EXISTS relatii_semantice (
        id INTEGER PRIMARY KEY,
        tip TEXT NOT NULL,
        nivel TEXT NOT NULL,
        de_la TEXT NOT NULL,
        la TEXT NOT NULL,
        sursa_id TEXT NOT NULL REFERENCES surse(id),
        detalii TEXT,
        UNIQUE (tip, nivel, de_la, la)
    );
    CREATE INDEX IF NOT EXISTS ix_relsem_de_la ON relatii_semantice(de_la, tip);
    CREATE INDEX IF NOT EXISTS ix_relsem_la ON relatii_semantice(la, tip);
    CREATE TABLE IF NOT EXISTS relatii_sintactice (
        tip TEXT PRIMARY KEY,
        descriere TEXT,
        frecventa INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS reguli (
        id TEXT PRIMARY KEY,
        tip TEXT NOT NULL,
        nume TEXT NOT NULL,
        descriere TEXT,
        definitie TEXT,
        justificare TEXT,
        statut TEXT NOT NULL,
        versiune TEXT
    );
    CREATE TABLE IF NOT EXISTS exemple (
        id TEXT PRIMARY KEY,
        text TEXT NOT NULL,
        sursa_id TEXT NOT NULL REFERENCES surse(id),
        set_ TEXT NOT NULL,
        gen TEXT,
        doc TEXT,
        cuvinte TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS exemple_cuvinte (
        exemplu_id TEXT NOT NULL REFERENCES exemple(id),
        idx INTEGER NOT NULL,
        forma TEXT NOT NULL,
        forma_norm TEXT NOT NULL,
        lema_norm TEXT NOT NULL,
        upos TEXT NOT NULL,
        xpos TEXT,
        trasaturi TEXT NOT NULL DEFAULT '',
        cap INTEGER NOT NULL,
        rel TEXT NOT NULL,
        PRIMARY KEY (exemplu_id, idx)
    );
    CREATE INDEX IF NOT EXISTS ix_excuv_forma ON exemple_cuvinte(forma_norm);
    CREATE INDEX IF NOT EXISTS ix_excuv_lema ON exemple_cuvinte(lema_norm);
    CREATE TABLE IF NOT EXISTS contexte (
        id TEXT PRIMARY KEY,
        tip TEXT NOT NULL,
        continut TEXT NOT NULL,
        creat TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS validari (
        id INTEGER PRIMARY KEY,
        nume TEXT NOT NULL,
        data TEXT NOT NULL,
        versiune_motor TEXT NOT NULL,
        rezultat TEXT NOT NULL
    );
    """,
    2: """
    CREATE TABLE IF NOT EXISTS ortografie (
        forma TEXT PRIMARY KEY,
        forma_norm TEXT NOT NULL,
        sursa_id TEXT NOT NULL REFERENCES surse(id),
        detalii TEXT
    );
    CREATE INDEX IF NOT EXISTS ix_ortografie_norm ON ortografie(forma_norm);
    """,
}

# Ce verificăm la integritate: (nume, interogare care întoarce rândurile PROBLEMĂ; corect = 0 rânduri)
VERIFICARI_INTEGRITATE: list[tuple[str, str]] = [
    ("lexeme cu sursă necunoscută", "SELECT l.id FROM lexeme l LEFT JOIN surse s ON s.id = l.sursa_id WHERE s.id IS NULL"),
    ("lexeme cu categorie din afara inventarului",
     "SELECT id, pos FROM lexeme WHERE pos NOT IN (" + ",".join(f"'{c}'" for c in CATEGORII) + ")"),
    ("forme fără lexem", "SELECT f.id FROM forme f LEFT JOIN lexeme l ON l.id = f.lexem_id WHERE l.id IS NULL"),
    ("forme fără nicio proveniență",
     "SELECT f.id FROM forme f LEFT JOIN forme_provenienta p ON p.forma_id = f.id WHERE p.forma_id IS NULL"),
    ("proveniențe fără formă",
     "SELECT p.forma_id FROM forme_provenienta p LEFT JOIN forme f ON f.id = p.forma_id WHERE f.id IS NULL"),
    ("sensuri fără lexem", "SELECT s.id FROM sensuri s LEFT JOIN lexeme l ON l.id = s.lexem_id WHERE l.id IS NULL"),
    ("sensuri cu concept lipsă",
     "SELECT s.id FROM sensuri s LEFT JOIN concepte c ON c.id = s.concept_id WHERE s.concept_id IS NOT NULL AND c.id IS NULL"),
    ("relații semantice între concepte cu capăt lipsă",
     "SELECT r.id FROM relatii_semantice r LEFT JOIN concepte a ON a.id = r.de_la LEFT JOIN concepte b ON b.id = r.la "
     "WHERE r.nivel = 'concept' AND (a.id IS NULL OR b.id IS NULL)"),
    ("relații semantice între sensuri cu capăt lipsă",
     "SELECT r.id FROM relatii_semantice r LEFT JOIN sensuri a ON a.id = r.de_la LEFT JOIN sensuri b ON b.id = r.la "
     "WHERE r.nivel = 'sens' AND (a.id IS NULL OR b.id IS NULL)"),
    ("relații semantice între lexeme cu capăt lipsă",
     "SELECT r.id FROM relatii_semantice r LEFT JOIN lexeme a ON a.id = r.de_la LEFT JOIN lexeme b ON b.id = r.la "
     "WHERE r.nivel = 'lexem' AND (a.id IS NULL OR b.id IS NULL)"),
    ("exemple cu cuvinte lipsă",
     "SELECT e.id FROM exemple e LEFT JOIN exemple_cuvinte c ON c.exemplu_id = e.id WHERE c.exemplu_id IS NULL"),
    ("cuvinte din exemple cu cap în afara propoziției",
     "SELECT c.exemplu_id, c.idx FROM exemple_cuvinte c WHERE c.cap < 0 OR c.cap > (SELECT MAX(idx) FROM exemple_cuvinte d WHERE d.exemplu_id = c.exemplu_id)"),
    ("relații de dependență din exemple care lipsesc din inventar",
     "SELECT DISTINCT c.rel FROM exemple_cuvinte c LEFT JOIN relatii_sintactice r ON r.tip = c.rel WHERE r.tip IS NULL"),
]

# Relațiile semantice în care un ciclu e interzis (ierarhii): se verifică la integritate.
RELATII_FARA_CICLURI = ("hypernym", "instance_hypernym", "mero_part", "mero_member", "mero_substance")
