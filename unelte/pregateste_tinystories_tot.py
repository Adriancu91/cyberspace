"""TinyStories întreg (~2,2 GB, licență CDLA-Sharing-1.0), cu același examen ca R2: pregătirea, o singură dată.

1. Descarcă tot fișierul oficial de antrenare (TinyStoriesV2-GPT4-train.txt) și pregătește dosarul din configurare
   (date/tinystories_tot/): antrenarea = tot fișierul, fără poveștile care apar identic în validarea R2; validarea =
   copia exactă a validării R2 (date/tinystories_r2/validare.txt), deci scorurile rămân comparabile cu cele de până acum.
2. Împarte textul de antrenare în simboluri o singură dată, pe bucăți (tăiate între povești, deci aceleași simboluri), și
   le ține minte în director_cache (lucru/cache), sub amprenta pe care o caută modelul: antrenarea le găsește gata.
Setările vin din configurarea antrenării: portul date și tokenizerul modelului.

    python unelte/pregateste_tinystories_tot.py
    python unelte/pregateste_tinystories_tot.py --config config/laptop_antrenare_lunga_2.toml
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from kronos.config import citeste_config  # noqa: E402
from kronos.registru import Registru  # noqa: E402
from module.model_continuu import cale_simboluri, simboluri_din_cache  # noqa: E402
from module.tokenizer_bpe import TokenizerBPE  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="TinyStories întreg, cu validarea R2: datele și simbolurile, o singură dată.")
    parser.add_argument("--config", default="config/laptop_antrenare_lunga_2.toml")
    args = parser.parse_args(argv)
    config = citeste_config(args.config)
    setari_date, model = config.setari_port("date"), config.setari_port("model")
    inceput = time.perf_counter()

    date = Registru().creeaza("date", config.porturi["date"]["modul"], setari_date).instanta  # descarcă și pregătește
    info = date.info
    sursa = Path(setari_date["validare_din"]) / "validare.txt"
    copie = Path(setari_date["director"]) / "validare.txt"
    if copie.read_bytes() != sursa.read_bytes():
        print(f"Validarea din „{copie}” nu e identică cu „{sursa}”: examenul n-ar mai fi același. Mă opresc.", flush=True)
        return 1
    print(f"Date: {info['povesti_antrenare']:,} de povești de antrenare ({info['octeti_antrenare'] / 1e6:,.1f} MB); "
          f"scoase pentru că apar identic în validarea R2: {info.get('scoase_ca_in_validare', 0):,}; validarea = copia "
          f"exactă a validării R2 ({info['povesti_validare']:,} de povești, {info['octeti_validare'] / 1e6:.1f} MB).",
          flush=True)

    tok = TokenizerBPE.incarca(model["cale_tokenizer"])
    text = date.text_antrenare()
    fisier = cale_simboluri(text, model["director_cache"], model["cale_tokenizer"])
    exista = fisier.exists()
    inceput_simboluri = time.perf_counter()
    simboluri = simboluri_din_cache(tok, text, model["director_cache"], model["cale_tokenizer"])
    secunde = time.perf_counter() - inceput_simboluri
    print(f"Simboluri: {len(simboluri):,} ({len(text) / len(simboluri):.2f} litere pe simbol), "
          f"{len(simboluri) * simboluri.element_size() / 1e9:.2f} GB în memorie; "
          f"{'erau deja' if exista else f'împărțite acum, în {secunde:.0f} s'} în {fisier}.", flush=True)
    print(f"Gata în {(time.perf_counter() - inceput) / 60:.1f} minute.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
