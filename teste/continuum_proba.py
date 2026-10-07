"""CONTINUUM fără placă video: module de probă și un proiect mic pe disc, ca bucla să poată fi încercată întreagă în
câteva secunde.

Proiectul mic conține:
- configurări (CONTINUUM și Kronos);
- jurnalul Kronos;
- hrana;
- unelte de probă. Ele doar scriu fișe, cum ar face uneltele adevărate, fără antrenare și fără profesor.

Testele intră în dosarul temporar (monkeypatch.chdir), deci totul, inclusiv lucru/STOP, rămâne acolo.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from module.continuum.observa import Senzori

RADACINA = Path(__file__).resolve().parent.parent


# --- module de probă -------------------------------------------------------------------------------------------------

class ModulSanatos:
    MANIFEST = {"nume": "modul_sanatos", "port": "model", "versiune": "1.0", "versiune_contract": 1}

    @classmethod
    def sanatate(cls) -> dict[str, Any]:
        return {"stare": "ok"}

    @staticmethod
    def semnale() -> list[dict[str, Any]]:
        return [{"ce": "am terminat o oră"}]


class ModulCareCade:
    """sanatate() aruncă o eroare cât timp cade = True: testele îl strică și îl repară în timpul rulării."""
    MANIFEST = {"nume": "modul_care_cade", "port": "profesor", "versiune": "1.0", "versiune_contract": 1}
    cade = False

    @classmethod
    def sanatate(cls) -> dict[str, Any]:
        if cls.cade:
            raise RuntimeError("placa a dispărut")
        return {"stare": "ok"}


class ModulDegradat:
    MANIFEST = {"nume": "modul_degradat", "port": "profesor", "versiune": "1.0", "versiune_contract": 1}

    @classmethod
    def sanatate(cls) -> dict[str, Any]:
        return {"stare": "degradat", "detalii": "merge încet"}


class ModulFaraManifest:
    pass


MODULE_IMPLICITE = {"model": "teste.continuum_proba:ModulSanatos", "examene": "teste.continuum_proba:ModulSanatos",
                    "profesor": "teste.continuum_proba:ModulCareCade"}


# --- configurările ---------------------------------------------------------------------------------------------------

CONFIG_CONTINUUM = """
[continuum]
director_lucru = "lucru"
redescopera_la_cicluri = @REDESCOPERA@
jurnal_max_mb = 20
ordinea_nevoilor = ["masoara", "continua", "dezvolta"]

[guvernator]
fereastra_invatare = "22:00-07:00"
fereastra_intretinere = "07:00-22:00"
minute_fara_om = 10
temperatura_max = 85
memorie_video_libera_min_mb = 4500
procese_grele = ["python"]

[guvernator.pauza_minute]
REPAUS = 0
"ÎNTREȚINERE" = 0
"ÎNVĂȚARE" = 0

[invatare]
incredere_initiala = 0.5
pas_incredere = 0.1

[module]
@MODULE@

[linii]
configurari = ["config/laptop_antrenare_lunga*.toml", "config/laptop_fapte*.toml"]

[capacitati.povesti]
metrica = "val_bpb"
mai_mare_e_mai_bine = false
prag_zgomot = 0.02
module = ["model"]

[capacitati.fapte]
metrica = "fapte_corecte"
mai_mare_e_mai_bine = true
prag_zgomot = 3
maxim = 150
module = ["examene"]
unealta = { linie = "examen_fapte", scor = "corecte_doar_cuvantul_din_fapt" }
masurare = ["{python}", "unelte/examen_fapte.py", "--experiment", "{experiment}"]

[capacitati.sens]
metrica = "nota_profesor"
mai_mare_e_mai_bine = true
prag_zgomot = 0.3
maxim = 10
module = ["profesor"]
unealta = { linie = "examen_profesor", scor = "nota_medie" }
masurare = ["{python}", "unelte/examen_profesor.py", "--experiment", "{experiment}"]

[hrana.fapte]
dosar = "date/fapte"
minima_povesti = 5000
comanda = ["{python}", "unelte/genereaza_fapte.py", "--povesti", "{tinta_povesti}"]
adaos_povesti = 2000
timeout_ore = 0.05

[nevoi.masoara]
nivel = "ÎNTREȚINERE"
timeout_minute = 2

[nevoi.continua]
nivel = "ÎNVĂȚARE"
capacitate = "povesti"
castig_minim = 0.005
configurari = ["config/laptop_antrenare_lunga*.toml"]
timeout_ore = 0.05

[nevoi.dezvolta]
nivel = "ÎNTREȚINERE"
configurari = ["config/laptop_fapte*.toml"]
timeout_ore = 0.05

[comenzi]
antrenare = ["{python}", "unelte/antrenare_lunga.py", "--config", "{config}", "--ore", "{ore}", "--porneste-din", "{ultimul_model}"]
"""

CONFIG_KRONOS = """
[platforma]
nume = "@LINIE@"
director_lucru = "lucru"
buget_antrenare_secunde = @BUGET@
experimente = @ORE@

[porturi.model]
modul = "module.model_ngram:ModelNgram"
setari = { n_straturi = @STRATURI@, n_capete = 8, n_emb = 512, context = 256@MODEL@ }

[porturi.date]
modul = "module.date_mostra:DateMostra"
setari = { director = "date/tinystories_tot"@DATE@ }

[porturi.examen]
modul = "module.examen_bpb:ExamenBpb"

[porturi.cercetator]
modul = "module.cercetator_aleator:CercetatorAleator"

[porturi.profesor]
modul = "module.jucarii:ProfesorGol"

[porturi.rulare]
modul = "module.rulare_locala:RulareLocala"

[porturi.stocare]
modul = "module.stocare_disc:StocareDisc"

[porturi.interfata]
modul = "module.interfata_consola:InterfataConsola"

[porturi.traducere]
modul = "module.jucarii:TraducereIdentitate"

[porturi.memorie]
modul = "module.jucarii:MemorieGoala"
"""


def config_continuum(radacina: Path, module: dict[str, str] | None = None, redescopera: int = 1,
                     inlocuiri: dict[str, str] | None = None) -> Path:
    module = MODULE_IMPLICITE if module is None else module
    text = CONFIG_CONTINUUM.replace("@REDESCOPERA@", str(redescopera)).replace(
        "@MODULE@", "\n".join(f'{nume} = "{cale}"' for nume, cale in module.items()))
    for vechi, nou in (inlocuiri or {}).items():
        assert vechi in text, vechi
        text = text.replace(vechi, nou)
    cale = radacina / "config" / "continuum.toml"
    cale.parent.mkdir(parents=True, exist_ok=True)
    cale.write_text(text, encoding="utf-8")
    return cale


def config_kronos(radacina: Path, fisier: str, linie: str, ore: int = 8, straturi: int = 10, model: str = "",
                  date: str = "", buget: int = 3600) -> Path:
    cale = radacina / "config" / fisier
    cale.parent.mkdir(parents=True, exist_ok=True)
    text = CONFIG_KRONOS
    for vechi, nou in (("@LINIE@", linie), ("@ORE@", str(ore)), ("@STRATURI@", str(straturi)), ("@MODEL@", model),
                       ("@DATE@", date), ("@BUGET@", str(buget))):
        text = text.replace(vechi, nou)
    cale.write_text(text, encoding="utf-8")
    return cale


# --- jurnalul Kronos și hrana ------------------------------------------------------------------------------------------

def fisa(id: int, linie: str, val_bpb: float, decizie: str = "pastrat", criterii: dict[str, Any] | None = None,
         straturi: int = 10, inceput: str = "2026-10-06T20:00:00+00:00", samanta: int | None = None,
         durata: float | None = None) -> dict[str, Any]:
    """O oră Kronos. `samanta` intră în setările modelului (perechi de semințe, pentru zgomotul învățat); `durata` e
    durata_totala_secunde (bugetul zilnic de ore pe placă)."""
    f: dict[str, Any] = {"id": id, "linie": linie, "inceput": inceput, "decizie": decizie, "scoruri": {"val_bpb": val_bpb},
                         "setari": {"model": {"n_straturi": straturi, "n_capete": 8, "n_emb": 512, "context": 256}}}
    if samanta is not None:
        f["setari"]["model"]["samanta"] = samanta
    if durata is not None:
        f["durata_totala_secunde"] = durata
    if decizie == "pastrat":
        f["model_salvat"] = f"lucru/stocare/modele/experiment_{id}.pt"
    if criterii:
        f["dupa_examen"] = {"criterii": criterii}
    return f


def fisa_unealta(id: int, linie: str, experiment: int, scoruri: dict[str, Any]) -> dict[str, Any]:
    return {"id": id, "linie": linie, "decizie": "masurat", "module": {"elev": {"experiment": experiment}},
            "scoruri": scoruri}


def scrie_jurnal(radacina: Path, fise: list[dict[str, Any]]) -> Path:
    cale = radacina / "lucru" / "jurnal" / "experimente.jsonl"
    cale.parent.mkdir(parents=True, exist_ok=True)
    with cale.open("a", encoding="utf-8") as f:
        for x in fise:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    return cale


SCORURI_NOAPTEA_3 = [0.5762, 0.5501, 0.5285, 0.5102, 0.4941, 0.4771, 0.4636, 0.4567]


def noaptea_3(radacina: Path, masurat: bool = True) -> None:
    """Ca a treia antrenare lungă: 8 ore păstrate (#1–#8), val_bpb încă scade; ultimul model măsurat cu uneltele
    (#9: 41 de fapte din 150, #10: nota 4,7)."""
    config_kronos(radacina, "laptop_antrenare_lunga_3.toml", "antrenare_lunga_3")
    fise = [fisa(i, "antrenare_lunga_3", s) for i, s in enumerate(SCORURI_NOAPTEA_3, start=1)]
    if masurat:
        fise += [fisa_unealta(9, "examen_fapte", 8, {"corecte_doar_cuvantul_din_fapt": 41, "corecte": 50}),
                 fisa_unealta(10, "examen_profesor", 8, {"nota_medie": 4.7})]
    scrie_jurnal(radacina, fise)


def scrie_hrana(radacina: Path, povesti: int = 7520, scrise: int = 9000,
                schimbata: datetime = datetime(2026, 10, 6, 12, 0)) -> Path:
    dosar = radacina / "date" / "fapte"
    dosar.mkdir(parents=True, exist_ok=True)
    (dosar / "povesti.txt").write_text("Birds have feathers.\n<|endoftext|>\nWater freezes when it is cold.",
                                       encoding="utf-8")
    (dosar / "info.json").write_text(json.dumps({"scrise": scrise, "ramase": povesti}), encoding="utf-8")
    for f in dosar.iterdir():
        os.utime(f, (schimbata.timestamp(), schimbata.timestamp()))
    return dosar


# --- unelte de probă (doar scriu fișe, ca uneltele adevărate) ---------------------------------------------------------

UNEALTA_EXAMEN = """
import sys
sys.path.insert(0, @RADACINA@)
from kronos.jurnal import Jurnal
experiment = int(sys.argv[sys.argv.index("--experiment") + 1])
jurnal = Jurnal("lucru")
jurnal.adauga({"id": jurnal.urmatorul_id(), "linie": @LINIE@, "decizie": "masurat",
               "module": {"elev": {"experiment": experiment}}, "scoruri": {@CHEIE@: @VALOARE@}})
"""

UNEALTA_ANTRENARE = """
import json, sys
sys.path.insert(0, @RADACINA@)
from kronos.config import citeste_config
from kronos.jurnal import Jurnal
argumente = sys.argv[1:]
config = citeste_config(argumente[argumente.index("--config") + 1])
ore = int(argumente[argumente.index("--ore") + 1])
jurnal = Jurnal("lucru")
facute = sum(1 for f in jurnal.istoric(config.nume) if f.get("decizie") in ("pastrat", "respins"))
for ora in range(facute + 1, ore + 1):
    jurnal.adauga({"id": jurnal.urmatorul_id(), "linie": config.nume, "inceput": "2099-01-01T00:00:00+00:00",
                   "decizie": "pastrat", "scoruri": {"val_bpb": @VAL_BPB@ + @PAS_VAL_BPB@ * ora},
                   "setari": {"model": config.setari_port("model")}, "model_salvat": "lucru/stocare/ora_%d.pt" % ora,
                   "dupa_examen": {"criterii": {"fapte_corecte": @FAPTE@ + @PAS_FAPTE@ * ora, "nota_profesor": 4.7}}})
(jurnal.director / "argumente.json").write_text(json.dumps(argumente), encoding="utf-8")
"""

UNEALTA_HRANA = """
import json, sys
from pathlib import Path
tinta = int(sys.argv[sys.argv.index("--povesti") + 1])
info = Path("date/fapte/info.json")
date = json.loads(info.read_text(encoding="utf-8"))
date["ramase"] += tinta - date["scrise"]
date["scrise"] = tinta
info.write_text(json.dumps(date), encoding="utf-8")
"""


def scrie_unelte(radacina: Path, val_bpb: float = 0.4567, pas_val_bpb: float = -0.004, fapte: int = 41,
                 pas_fapte: int = 2, fapte_examen: int = 33) -> None:
    """Uneltele de probă, în radacina/unelte/: examenele scriu o fișă (examenul de fapte dă `fapte_examen`); antrenarea
    scrie orele care lipsesc (val_bpb și faptele se schimbă cu pasul dat la fiecare oră); hrana adaugă povești în
    info.json."""
    unelte = radacina / "unelte"
    unelte.mkdir(parents=True, exist_ok=True)
    radacina_text = repr(str(RADACINA))
    (unelte / "examen_fapte.py").write_text(UNEALTA_EXAMEN.replace("@RADACINA@", radacina_text).replace(
        "@LINIE@", '"examen_fapte"').replace("@CHEIE@", '"corecte_doar_cuvantul_din_fapt"').replace(
        "@VALOARE@", str(fapte_examen)),
        encoding="utf-8")
    (unelte / "examen_profesor.py").write_text(UNEALTA_EXAMEN.replace("@RADACINA@", radacina_text).replace(
        "@LINIE@", '"examen_profesor"').replace("@CHEIE@", '"nota_medie"').replace("@VALOARE@", "5.1"), encoding="utf-8")
    text = UNEALTA_ANTRENARE
    for vechi, nou in (("@RADACINA@", radacina_text), ("@VAL_BPB@", repr(val_bpb)), ("@PAS_VAL_BPB@", repr(pas_val_bpb)),
                       ("@FAPTE@", str(fapte)), ("@PAS_FAPTE@", str(pas_fapte))):
        text = text.replace(vechi, nou)
    (unelte / "antrenare_lunga.py").write_text(text, encoding="utf-8")
    (unelte / "genereaza_fapte.py").write_text(UNEALTA_HRANA, encoding="utf-8")


# --- semnalele din afara fișierelor ---------------------------------------------------------------------------------

class Lume:
    """Ora, placa și omul, de probă; testele le schimbă în timpul rulării."""

    def __init__(self, ora: str = "23:30", libera_mb: float = 5800, temperatura: float = 50,
                 procese: list[dict[str, Any]] | None = None, om_minute: float | None = 60.0,
                 placa_citita: bool = True) -> None:
        self.ora, self.libera_mb, self.temperatura = ora, libera_mb, temperatura
        self.procese = procese or []
        self.om_minute, self.placa_citita = om_minute, placa_citita

    def timp(self) -> datetime:
        ore, minute = (int(x) for x in self.ora.split(":"))
        return datetime(2026, 10, 7, ore, minute)

    def placa(self) -> dict[str, Any]:
        if not self.placa_citita:
            return {"stare": "indisponibil", "eroare": "nvidia-smi nu există"}
        return {"stare": "ok", "temperatura": self.temperatura, "memorie_folosita_mb": 6144 - self.libera_mb,
                "memorie_totala_mb": 6144, "memorie_libera_mb": self.libera_mb, "procese": self.procese}

    def om(self) -> dict[str, Any]:
        if self.om_minute is None:
            return {"stare": "indisponibil", "eroare": "proces fără ecran"}
        return {"stare": "ok", "minute_de_la_ultima_atingere": self.om_minute}

    def senzori(self) -> Senzori:
        return Senzori(acum=self.timp, placa=self.placa, om=self.om)
