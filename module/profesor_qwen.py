"""Profesorul (Faza 3, pasul 1): un model de limbaj mare, local, care scrie povești cu un fapt adevărat și le notează.

Modelul: Qwen3-4B-Instruct-2507 (Qwen, licență Apache 2.0), de pe Hugging Face (Qwen/Qwen3-4B-Instruct-2507), cuantizat
la încărcare în 4 biți (NF4, bitsandbytes) prin transformers: ~3 GB de memorie video, sub limita de 5,5 GB.
- De ce transformers în 4 biți și nu GGUF prin llama-cpp-python: pe Windows, llama-cpp-python nu are pe PyPI variante
  gata făcute, doar codul sursă, de compilat cu Visual Studio, CMake și setul de unelte CUDA, pe care laptopul nu le are
  (variantele gata făcute cu CUDA stau pe un site separat al proiectului, nu pe PyPI). transformers, accelerate și
  bitsandbytes vin gata făcute din PyPI și folosesc PyTorch-ul cu CUDA pe care îl avem deja.
- De ce Qwen3-4B și nu Qwen2.5-3B-Instruct (cerut la început): Qwen2.5-3B are licența „qwen-research”, nu Apache 2.0.

Ce face:
- genereaza(subiect, stil): o poveste scurtă în engleză simplă, ca în TinyStories, cu un fapt adevărat despre lume. Pentru
  cele 50 de subiecte din SUBIECTE, faptul e scris de noi (ca să fie sigur adevărat); pentru alt subiect, îl alege
  profesorul. Stilul: unul din STILURI (simplu, dialog, morala) sau scris liber, în engleză.
- noteaza(poveste): {"nota": 1–10, "motiv": un rând} pentru coerență, sens și gramatică; fără întâmplare, deci aceeași
  poveste primește mereu aceeași notă.
- genereaza_exercitii(tema, numar): contractul portului „profesor”: numar povești pe tema dată, ca {subiect, stil, fapt,
  poveste}.
Pentru viteză, genereaza_mai_multe și noteaza_mai_multe lucrează pe loturi (setarea lot). Modelul mare se încarcă abia la
prima folosire și stă pe placa video până la elibereaza().
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

MODEL_IMPLICIT = "Qwen/Qwen3-4B-Instruct-2507"

# 50 de subiecte, fiecare cu un fapt adevărat și simplu despre lume (în engleză, ca poveștile).
SUBIECTE: list[tuple[str, str]] = [
    ("snow", "Water freezes into ice when it is very cold."),
    ("birds", "Birds have feathers."),
    ("the Sun", "The Sun is a star."),
    ("plants", "Plants need water and sunlight to grow."),
    ("the Moon", "The Moon goes around the Earth."),
    ("bees", "Bees make honey from the nectar of flowers."),
    ("fish", "Fish breathe through their gills."),
    ("rain", "Rain falls from clouds."),
    ("spiders", "Spiders have eight legs."),
    ("frogs", "Frogs start their lives as tadpoles in the water."),
    ("butterflies", "A caterpillar changes into a butterfly."),
    ("cows", "Cows give milk."),
    ("teeth", "Brushing your teeth helps keep them healthy."),
    ("rainbows", "A rainbow can appear when sunlight shines through raindrops."),
    ("autumn", "Many trees lose their leaves in autumn."),
    ("the sea", "Sea water is salty."),
    ("magnets", "Magnets pull things made of iron."),
    ("the heart", "The heart pumps blood around the body."),
    ("bats", "Bats are mammals that can fly."),
    ("penguins", "Penguins are birds that cannot fly, but they swim very well."),
    ("volcanoes", "Hot melted rock called lava comes out of volcanoes."),
    ("shadows", "A shadow forms when something blocks the light."),
    ("boiling water", "Water boils when it gets very hot."),
    ("owls", "Many owls hunt at night."),
    ("camels", "Camels can go a long time without drinking water."),
    ("elephants", "Elephants use their trunks to drink water and to pick things up."),
    ("stars", "Stars are very far away from the Earth."),
    ("wind", "Wind is moving air."),
    ("ants", "Ants live and work together in big groups called colonies."),
    ("seeds", "A big tree can grow from a small seed."),
    ("snakes", "Snakes have no legs."),
    ("whales", "Whales breathe air through a blowhole on top of their heads."),
    ("ice cream", "Ice cream melts when it gets warm."),
    ("night", "It gets dark at night because our side of the Earth turns away from the Sun."),
    ("sleep", "Our bodies need sleep to stay healthy."),
    ("bread", "Bread is made from flour."),
    ("chickens", "Hens lay eggs."),
    ("turtles", "A turtle carries its shell with it everywhere."),
    ("thunderstorms", "We see lightning before we hear the thunder."),
    ("mountains", "It is usually colder at the top of a high mountain."),
    ("dogs", "Dogs have a very good sense of smell."),
    ("cats", "Cats can see well when there is little light."),
    ("apples", "Apples grow on trees."),
    ("the Earth", "The Earth goes around the Sun once every year."),
    ("squirrels", "Squirrels hide nuts to eat in the winter."),
    ("bears", "Some bears sleep through most of the winter."),
    ("carrots", "Carrots grow under the ground."),
    ("clouds", "Clouds are made of tiny drops of water."),
    ("sand", "Sand is made of tiny pieces of rock and shells."),
    ("washing hands", "Washing your hands with soap helps wash away germs."),
]
FAPTE = dict(SUBIECTE)
STILURI = {
    "simplu": "simple and calm, told by a narrator",
    "dialog": "with a short conversation between the characters, using quotation marks",
    "morala": "ending with a short, clear lesson",
    "problema": "where a small problem is solved by the end",
    "intrebare": "where a child asks a question and a grown-up answers it",
    "prieteni": "about two friends who help each other",
    "seara": "as a calm bedtime story",
    "amuzant": "funny, with a silly surprise",
}
# Personajul principal, ca poveștile despre același fapt să nu semene între ele.
PERSONAJE = (
    "a little girl", "a little boy", "a curious puppy", "a small kitten", "a grandma and her grandson",
    "two best friends", "a mom and her daughter", "a dad and his son",
)
SISTEM_POVESTE = (
    "You write short stories for small children, in the style of the TinyStories dataset: very simple English that a "
    "3-year-old understands, short sentences, and a clear beginning, middle and end."
)
SISTEM_NOTA = "You are a strict but fair teacher who grades very short children's stories."
_NOTA = re.compile(r"GRADE\s*:\s*(\d+)", re.IGNORECASE)
_MOTIV = re.compile(r"REASON\s*:\s*(.+)", re.IGNORECASE)


def cerere_poveste(subiect: str, stil: str = "simplu", personaj: str | None = None) -> list[dict[str, str]]:
    """Mesajele pentru o poveste: subiectul, stilul (din STILURI sau scris liber), personajul principal (dacă e dat) și
    faptul adevărat de pus în ea."""
    fapt = FAPTE.get(subiect)
    if fapt:
        cerinta = ("The story must include this true fact about the world exactly once (do not repeat it anywhere, not "
                   "even at the end), said simply and correctly as a natural part of the story (for example, a "
                   f'character learns it): "{fapt}" Do not add other facts that are not true.')
    else:
        cerinta = (f"The story must include one true, simple fact about {subiect} that a child can learn, said once, "
                   "as a natural part of the story. Make sure the fact is correct.")
    return [
        {"role": "system", "content": SISTEM_POVESTE},
        {"role": "user", "content": f"Write a short story (about 150 words) about {subiect}. "
                                    f"Style: {STILURI.get(stil, stil)}. "
                                    + (f"The main character is {personaj}. " if personaj else "")
                                    + f"{cerinta} Write it as one to three normal paragraphs, not one sentence per "
                                    "line. Write only the story, with no title."},
    ]


def cerere_nota(poveste: str) -> list[dict[str, str]]:
    """Mesajele pentru notă: criteriile (coerență, sens, gramatică), câteva repere ale scării și forma răspunsului."""
    return [
        {"role": "system", "content": SISTEM_NOTA},
        {"role": "user", "content": (
            "Grade this story from 1 to 10 for coherence (do the events follow each other and fit together?), sense "
            "(does every sentence make sense?) and grammar (correct simple English).\n"
            "10 = perfect: clear, sensible, no mistakes.\n"
            "7 = good, with one or two small mistakes.\n"
            "4 = several sentences do not make sense or do not fit together.\n"
            "1 = mostly nonsense.\n\n"
            f'Story:\n"""\n{poveste.strip()}\n"""\n\n'
            "Answer in exactly two lines:\nGRADE: <a whole number from 1 to 10>\nREASON: <one short sentence>"
        )},
    ]


def citeste_nota(raspuns: str) -> dict[str, Any]:
    """Nota (1–10) și motivul din răspunsul profesorului; nota e None dacă răspunsul nu are forma cerută."""
    nota, motiv = _NOTA.search(raspuns), _MOTIV.search(raspuns)
    return {
        "nota": min(10, max(1, int(nota.group(1)))) if nota else None,
        "motiv": motiv.group(1).strip() if motiv else raspuns.strip(),
    }


def e_descarcat(model: str = MODEL_IMPLICIT) -> bool:
    """E modelul întreg în cache-ul local Hugging Face (fără să descarce nimic)?"""
    try:
        from huggingface_hub import try_to_load_from_cache
    except ImportError:
        return False
    index = try_to_load_from_cache(model, "model.safetensors.index.json")
    if not isinstance(index, str):
        return False
    with open(index, encoding="utf-8") as f:
        bucati = set(json.load(f)["weight_map"].values())
    fisiere = {"config.json", "tokenizer.json", "tokenizer_config.json", *bucati}
    return all(isinstance(try_to_load_from_cache(model, nume), str) for nume in fisiere)


class ProfesorQwen:
    MANIFEST = {
        "nume": "profesor_qwen",
        "port": "profesor",
        "versiune": "0.1.0",
        "versiune_contract": 1,
        "resurse": {"gpu": True, "memorie_gpu_mb": 4500, "disc_mb": 8100},
        "permisiuni": ["internet", "citire_fisier"],
    }

    def __init__(
        self,
        model: str = MODEL_IMPLICIT,
        lot: int = 8,
        max_simboluri: int = 350,
        max_simboluri_nota: int = 60,
        temperatura: float = 0.7,
        samanta: int = 0,
        doar_local: bool = False,
    ) -> None:
        if lot < 1 or max_simboluri < 1 or max_simboluri_nota < 1 or temperatura <= 0:
            raise ValueError("lot, max_simboluri, max_simboluri_nota și temperatura trebuie să fie pozitive")
        self.model = model
        self.lot = lot
        self.max_simboluri = max_simboluri
        self.max_simboluri_nota = max_simboluri_nota
        self.temperatura = temperatura
        self.samanta = samanta
        self.doar_local = doar_local  # True: nu descarcă nimic (ex. în teste)
        self._tok: Any = None
        self._llm: Any = None
        self._loturi = 0
        self.simboluri_generate = 0
        self.secunde = 0.0

    # --- modelul mare -------------------------------------------------------------

    def pregateste(self) -> None:
        """Încarcă modelul mare pe placa video (o singură dată; altfel se încarcă singur la prima folosire)."""
        if self._llm is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        cuantizare = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                                        bnb_4bit_compute_dtype=torch.bfloat16)
        self._tok = AutoTokenizer.from_pretrained(self.model, padding_side="left", local_files_only=self.doar_local)
        self._llm = AutoModelForCausalLM.from_pretrained(self.model, quantization_config=cuantizare, device_map={"": 0},
                                                         dtype=torch.bfloat16, local_files_only=self.doar_local)
        self._llm.eval()

    def _raspunsuri(self, conversatii: list[list[dict[str, str]]], max_simboluri: int, cu_intamplare: bool) -> list[str]:
        """Un lot de conversații → răspunsurile profesorului. Singurul loc care atinge modelul mare."""
        import torch

        self.pregateste()
        # enable_thinking=False: Qwen3-8B (15 octombrie 2026) ar scrie altfel întâi un „<think>…”; șablonul lui
        # Qwen3-4B-Instruct-2507 nu-l folosește, deci pentru el nu se schimbă nimic.
        texte = [self._tok.apply_chat_template(c, tokenize=False, add_generation_prompt=True, enable_thinking=False)
                 for c in conversatii]
        intrare = self._tok(texte, return_tensors="pt", padding=True).to(self._llm.device)
        if cu_intamplare:  # aceeași sămânță și aceleași cereri = aceleași povești
            torch.manual_seed(self.samanta * 100_003 + self._loturi)
            setari = {"do_sample": True, "temperature": self.temperatura, "top_p": 0.8, "top_k": 20}
        else:
            setari = {"do_sample": False, "temperature": None, "top_p": None, "top_k": None}
        self._loturi += 1
        start = time.perf_counter()
        with torch.no_grad():
            iesire = self._llm.generate(**intrare, max_new_tokens=max_simboluri, pad_token_id=self._tok.pad_token_id,
                                        **setari)
        self.secunde += time.perf_counter() - start
        noi = iesire[:, intrare["input_ids"].shape[1]:]
        self.simboluri_generate += int((noi != self._tok.pad_token_id).sum())
        raspunsuri = [t.strip() for t in self._tok.batch_decode(noi, skip_special_tokens=True)]
        # Loturile au lungimi diferite, iar PyTorch păstrează memoria eliberată pentru refolosire: fără asta, memoria
        # rezervată crește de la un lot la altul (într-o rulare de ore a ajuns la 5,9 GB, peste limita de 5,5 GB).
        del iesire, noi, intrare
        torch.cuda.empty_cache()
        return raspunsuri

    # --- ce face profesorul ---------------------------------------------------------

    def genereaza_mai_multe(self, cereri: list[tuple[str, ...]]) -> list[str]:
        """Câte o poveste pentru fiecare (subiect, stil) sau (subiect, stil, personaj), pe loturi."""
        povesti: list[str] = []
        for i in range(0, len(cereri), self.lot):
            lot = [cerere_poveste(*cerere) for cerere in cereri[i : i + self.lot]]
            povesti += self._raspunsuri(lot, self.max_simboluri, cu_intamplare=True)
        return povesti

    def raspunde_mai_multe(self, conversatii: list[list[dict[str, str]]], max_simboluri: int,
                           cu_intamplare: bool = True) -> list[str]:
        """Răspunsurile la conversații gata făcute (ex. propozițiile examenului de fapte nou), pe loturi."""
        raspunsuri: list[str] = []
        for i in range(0, len(conversatii), self.lot):
            raspunsuri += self._raspunsuri(conversatii[i : i + self.lot], max_simboluri, cu_intamplare)
        return raspunsuri

    def genereaza(self, subiect: str, stil: str = "simplu") -> str:
        """O poveste scurtă în engleză simplă, cu un fapt adevărat despre lume."""
        return self.genereaza_mai_multe([(subiect, stil)])[0]

    def noteaza_mai_multe(self, povesti: list[str]) -> list[dict[str, Any]]:
        """Câte o notă (1–10) și un rând de motivare pentru fiecare poveste, pe loturi, fără întâmplare."""
        note: list[dict[str, Any]] = []
        for i in range(0, len(povesti), self.lot):
            lot = [cerere_nota(p) for p in povesti[i : i + self.lot]]
            note += [citeste_nota(r) for r in self._raspunsuri(lot, self.max_simboluri_nota, cu_intamplare=False)]
        return note

    def noteaza(self, poveste: str) -> dict[str, Any]:
        """{"nota": 1–10, "motiv": un rând} pentru coerență, sens și gramatică."""
        return self.noteaza_mai_multe([poveste])[0]

    def genereaza_exercitii(self, tema: str, numar: int) -> list[dict[str, str]]:
        """Contractul portului „profesor”: numar povești pe tema dată, prin stilurile pe rând."""
        stiluri = list(STILURI)
        cereri = [(tema, stiluri[k % len(stiluri)]) for k in range(numar)]
        return [{"subiect": tema, "stil": stil, "fapt": FAPTE.get(tema, ""), "poveste": poveste}
                for (_, stil), poveste in zip(cereri, self.genereaza_mai_multe(cereri))]

    # --- măsurători -----------------------------------------------------------------

    def statistici(self) -> dict[str, float]:
        return {"simboluri_generate": self.simboluri_generate, "secunde": round(self.secunde, 1),
                "simboluri_pe_secunda": round(self.simboluri_generate / self.secunde, 1) if self.secunde else 0.0}

    @staticmethod
    def memorie_video_mb() -> dict[str, int]:
        import torch

        if not torch.cuda.is_available():
            return {}
        return {"rezervata": round(torch.cuda.max_memory_reserved() / 2**20),
                "folosita": round(torch.cuda.max_memory_allocated() / 2**20)}

    def elibereaza(self) -> None:
        """Scoate modelul mare de pe placa video."""
        self._llm = None
        self._tok = None
        import gc

        import torch

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
