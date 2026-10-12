"""Școala de cod v0.4, pasul 0: vocabularul, cu tokenizer-ul nou al workstation-ului (date/ws/bpe_16384.json).

Reface, fără model și fără placă video, „împărțirea în simboluri” a tot ce vede școala: abecedarul, setul sacru și
seturile de examen ale fiecărui nivel. Fișierele cu amprentă (abecedarul, setul sacru, generatorul de teste,
sandbox-ul) NU se schimbă: se schimbă doar felul în care tokenizer-ul le taie.

Ce verifică:
1. Abecedarul trece prin tokenizer și iese identic; câte simboluri are (tot, pe episod, regula scurtă), față de
   tokenizer-ul vechi.
2. La fiecare nivel al pilotului și la fiecare set (văzut, nevăzut, adversarial, sacru), textul din fața modelului
   încape în context cu numărul cerut de exemple și cu loc pentru ce scrie modelul.
3. **Problema veche: cuvintele între ghilimele.** Pentru fiecare cuvânt al examenelor: în câte bucăți e în sarcină
   („show the word moon”: cu spațiu în față) și în câte în răspuns (`"moon"`: fără spațiu, între ghilimele), și dacă
   bucățile din răspuns sunt aceleași cu cele din sarcină (atunci modelul poate copia, bucată cu bucată, ce vede).
   Același lucru pentru o sarcină care ar arăta cuvântul gata pus între ghilimele (`show the word "moon"`): asta ar
   cere schimbarea generatorului de teste, deci aprobarea lui Adrian; aici doar se măsoară.
4. Numerele: în sarcină („show 46”) și în răspuns („46”) sunt aceeași bucată.

    python unelte/vocabular_cod_ws.py                                   # cu config/scoala_cod_v04.toml
    python unelte/vocabular_cod_ws.py --iesire lucru/cod_v04/vocabular_ws.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import tomllib
from pathlib import Path
from typing import Any

RADACINA = Path(__file__).resolve().parent.parent
if str(RADACINA) not in sys.path:
    sys.path.insert(0, str(RADACINA))

from module.cod import examen_cod  # noqa: E402
from module.cod.mediu import citeste_abecedar, text_cu_regula, text_fata  # noqa: E402
from module.tokenizer_bpe import TokenizerBPE  # noqa: E402


def bucati(tok: TokenizerBPE, text: str) -> list[str]:
    return [tok.octeti(s).decode("utf-8", errors="replace") for s in tok.codifica(text)]


def cuvant_in_sarcina_si_raspuns(tok: TokenizerBPE, cuvant: str, sarcina: str) -> dict[str, Any]:
    """Cum e tăiat cuvântul în sarcina dată (un text cu {w}) și în răspunsul `"cuvânt"`. „se_copiaza” = bucățile
    cuvântului din răspuns apar, în aceeași ordine, și în sarcină: modelul are de unde să le ia."""
    in_sarcina = tok.codifica(sarcina.replace("{w}", cuvant))
    fara = tok.codifica(sarcina.replace("{w}", ""))
    in_raspuns = tok.codifica(f'"{cuvant}"')
    ghilimea = tok.codifica('"')
    miez = in_raspuns[len(ghilimea): len(in_raspuns) - len(ghilimea)] if (
        in_raspuns[: len(ghilimea)] == ghilimea and in_raspuns[-len(ghilimea):] == ghilimea) else in_raspuns
    se_copiaza = any(in_sarcina[i: i + len(miez)] == miez for i in range(len(in_sarcina) - len(miez) + 1))
    return {"bucati_raspuns": len(in_raspuns), "bucati_cuvant_in_raspuns": len(miez),
            "bucati_in_plus_in_sarcina": len(in_sarcina) - len(fara), "se_copiaza": se_copiaza}


def cuvintele(tok: TokenizerBPE, cuvinte: tuple[str, ...]) -> dict[str, Any]:
    """Rezumatul pentru o listă de cuvinte, cu sarcina de acum și cu sarcina care arată cuvântul între ghilimele."""
    acum = [cuvant_in_sarcina_si_raspuns(tok, w, "show the word {w}") for w in cuvinte]
    ghilimele = [cuvant_in_sarcina_si_raspuns(tok, w, 'show the word "{w}"') for w in cuvinte]
    n = len(cuvinte)
    return {
        "cuvinte": n,
        "cuvantul_din_raspuns_o_bucata": sum(r["bucati_cuvant_in_raspuns"] == 1 for r in acum),
        "cuvantul_din_raspuns_cel_mult_2": sum(r["bucati_cuvant_in_raspuns"] <= 2 for r in acum),
        "raspunsul_intreg_bucati_in_medie": round(sum(r["bucati_raspuns"] for r in acum) / n, 2),
        "se_copiaza_cu_sarcina_de_acum": sum(r["se_copiaza"] for r in acum),
        "se_copiaza_cu_sarcina_cu_ghilimele": sum(r["se_copiaza"] for r in ghilimele),
        "rupte_in_raspuns": [w for w, r in zip(cuvinte, acum) if r["bucati_cuvant_in_raspuns"] > 1][:40],
    }


def numerele(tok: TokenizerBPE) -> dict[str, Any]:
    def la_fel(n: int) -> bool:
        raspuns = tok.codifica(str(n))
        sarcina = tok.codifica(f"show {n}")
        return any(sarcina[i: i + len(raspuns)] == raspuns for i in range(len(sarcina) - len(raspuns) + 1))

    return {"0_99_o_bucata": sum(len(tok.codifica(str(n))) == 1 for n in range(100)),
            "0_99_se_copiaza": sum(la_fel(n) for n in range(100)),
            "100_999_o_bucata": sum(len(tok.codifica(str(n))) == 1 for n in range(100, 1000)),
            "100_999_se_copiaza": sum(la_fel(n) for n in range(100, 1000))}


def incape(tok: TokenizerBPE, cfg: dict[str, Any], context: int) -> dict[str, Any]:
    """La fiecare nivel al pilotului: câte exemple încap în fața fiecărei sarcini și cât ocupă cel mai lung text."""
    s, m, e = cfg["scoala"], cfg["mediu"], cfg["examen"]
    abecedar = citeste_abecedar(RADACINA / s["abecedar"])
    sacru = examen_cod.citeste_sacru(RADACINA / s["sacru"])
    regula = m["regula_scurta"].strip("\n") + "\n" if m["regula"] == "scurta" else (
        abecedar.preambul if m["regula"] == "lunga" else "")
    texte_abecedar = {ep.test for ep in abecedar.episoade}

    def numara(text: str) -> int:
        return len(tok.codifica(text))

    rezultat: dict[str, Any] = {}
    for nivel in cfg["pilot"]["niveluri"]:
        marimi = {**{k: e[k] for k in ("vazut", "nevazut", "adversarial")}, **(e.get("marimi", {}).get(nivel, {}))}
        seturi = examen_cod.seturi(nivel, texte_abecedar, sacru.get(nivel, []), marimi["vazut"], marimi["nevazut"],
                                   marimi["adversarial"], e["samanta_seturi"])
        rng = random.Random(f"vocabular:{nivel}")
        exemple_minime, cel_mai_lung, sarcini, se_copiaza = m["episoade"], 0, 0, 0
        for nume in examen_cod.SETURI:
            for sarcina in getattr(seturi, nume):
                text, puse = text_fata(abecedar, sarcina.text, nivel, rng, numara, context, m["max_simboluri"], regula,
                                       m["episoade"])
                exemple_minime = min(exemple_minime, len(puse))
                cel_mai_lung = max(cel_mai_lung, numara(text) + m["max_simboluri"])
                sarcini += 1
                raspuns, in_fata = tok.codifica(sarcina.solutie.strip('"')), tok.codifica(sarcina.text)
                se_copiaza += any(in_fata[i: i + len(raspuns)] == raspuns for i in range(len(in_fata) - len(raspuns) + 1))
                cel_mai_lunga_solutie = numara(sarcina.solutie + "\nRESULT:")
                if cel_mai_lunga_solutie > m["max_simboluri"]:
                    rezultat.setdefault("solutii_care_nu_incap", []).append(sarcina.text)
        rezultat[nivel] = {"sarcini": sarcini, "exemple_minime": exemple_minime, "cel_mai_lung_text_cu_raspuns": cel_mai_lung,
                           "context": context, "sacre": len(seturi.sacru)}
        if nivel in ("0n", "0w", "0q"):  # nivelurile unde răspunsul e chiar valoarea din sarcină
            rezultat[nivel]["raspunsul_se_poate_copia_din_sarcina"] = se_copiaza
    return rezultat


def verifica(cfg: dict[str, Any], cale_nou: Path, cale_vechi: Path, context: int) -> dict[str, Any]:
    nou, vechi = TokenizerBPE.incarca(cale_nou), TokenizerBPE.incarca(cale_vechi)
    abecedar = citeste_abecedar(RADACINA / cfg["scoala"]["abecedar"])
    regula = cfg["mediu"]["regula_scurta"].strip("\n") + "\n"
    r: dict[str, Any] = {"tokenizer_nou": cale_nou.as_posix(), "tokenizer_vechi": cale_vechi.as_posix(), "context": context}
    r["abecedar"] = {}
    for nume, tok in (("nou", nou), ("vechi", vechi)):
        episoade = [len(tok.codifica(ep.text())) for ep in abecedar.episoade]
        r["abecedar"][nume] = {
            "iese_identic": tok.decodeaza(tok.codifica(abecedar.text)) == abecedar.text,
            "simboluri": len(tok.codifica(abecedar.text)), "episoade": len(episoade),
            "simboluri_pe_episod": round(sum(episoade) / len(episoade), 1), "cel_mai_lung_episod": max(episoade),
            "regula_scurta_cu_examples": len(tok.codifica(regula + "\nEXAMPLES:\n\n")),
            "textul_de_pregatire": len(tok.codifica(text_cu_regula(abecedar, regula))),
        }
    liste = {"0w_scurte": examen_cod.CUVINTE_0W, "0w_lungi_adversarial": examen_cod.CUVINTE_LUNGI_0W}
    r["cuvinte"] = {nume: {"nou": cuvintele(nou, lista), "vechi": cuvintele(vechi, lista)} for nume, lista in liste.items()}
    r["numere"] = {"nou": numerele(nou), "vechi": numerele(vechi)}
    r["incape"] = incape(nou, cfg, context)
    r["exemple"] = {text: {"nou": bucati(nou, text), "vechi": bucati(vechi, text)} for text in (
        'TEST: show the word moon\nWRITE:\n"moon"\nRESULT:\nmoon\npassed\n', 'show the word "moon"', "show 46",
        'TEST: put 7 in a box called x and show it\nWRITE:\nx = 7\nprint(x)\n', 'print("elephant")')}
    return r


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Școala de cod v0.4: vocabularul, cu tokenizer-ul nou.")
    parser.add_argument("--config", default="config/scoala_cod_v04.toml")
    parser.add_argument("--vechi", default="../cyberspace/date/tinystories/bpe_4096.json")
    parser.add_argument("--context", type=int, default=512, help="contextul modelului de pornire (W2: 512)")
    parser.add_argument("--iesire", default="lucru/cod_v04/vocabular_ws.json")
    args = parser.parse_args(argv)
    with open(RADACINA / args.config, "rb") as f:
        cfg = tomllib.load(f)
    r = verifica(cfg, (RADACINA / cfg["povesti"]["tokenizer"]).resolve(), (RADACINA / args.vechi).resolve(), args.context)
    iesire = RADACINA / args.iesire
    iesire.parent.mkdir(parents=True, exist_ok=True)
    iesire.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    a = r["abecedar"]
    print("=== Școala de cod v0.4, vocabularul cu tokenizer-ul nou ===")
    print(f"Abecedarul iese identic: {a['nou']['iese_identic']}. Simboluri: {a['nou']['simboluri']} (vechi: "
          f"{a['vechi']['simboluri']}); pe episod {a['nou']['simboluri_pe_episod']} (vechi: "
          f"{a['vechi']['simboluri_pe_episod']}); regula scurtă {a['nou']['regula_scurta_cu_examples']} (vechi: "
          f"{a['vechi']['regula_scurta_cu_examples']}).")
    for nume, c in r["cuvinte"].items():
        n, v = c["nou"], c["vechi"]
        print(f"Cuvintele {nume} ({n['cuvinte']}): cuvântul din răspuns e o singură bucată la "
              f"{n['cuvantul_din_raspuns_o_bucata']} (vechi: {v['cuvantul_din_raspuns_o_bucata']}); se pot copia din "
              f"sarcina de acum la {n['se_copiaza_cu_sarcina_de_acum']} (vechi: {v['se_copiaza_cu_sarcina_de_acum']}); cu "
              f"sarcina cu ghilimele la {n['se_copiaza_cu_sarcina_cu_ghilimele']} (vechi: "
              f"{v['se_copiaza_cu_sarcina_cu_ghilimele']}).")
    print(f"Numerele: {json.dumps(r['numere'], ensure_ascii=False)}")
    for nivel, i in r["incape"].items():
        if isinstance(i, dict):
            print(f"Nivelul {nivel}: {i['sarcini']} sarcini, cel puțin {i['exemple_minime']} exemple în față, cel mai lung "
                  f"text cu răspuns {i['cel_mai_lung_text_cu_raspuns']} din {i['context']}."
                  + (f" Răspunsul se poate copia din sarcină la {i['raspunsul_se_poate_copia_din_sarcina']}."
                     if "raspunsul_se_poate_copia_din_sarcina" in i else "")
                  + (" FĂRĂ set sacru încă." if not i["sacre"] else ""))
    print(f"Toate cifrele: {iesire}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
