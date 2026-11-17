"""S119: unealta pentru textul românesc nou (curățare, dubluri, scurgeri) pe date mici, făcute aici."""

from __future__ import annotations

import gzip
import json
import random

import numpy as np
import pytest

pa =pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")

from unelte import text_s119  # noqa: E402


def _cuvinte(seed: int, n: int = 120) -> str:
    rng = random.Random(seed)
    silabe = ["ma", "re", "pa", "dru", "ce", "ta", "lu", "mi", "nos", "ver", "de", "că", "să", "ții", "în", "ro"]
    return " ".join("".join(rng.choice(silabe) for _ in range(rng.randint(2, 4))) for _ in range(n)) + "."


def _parchet(cale, texte):
    cale.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table({"text": texte, "minhash_cluster_size": [1] * len(texte)}), cale, row_group_size=3)


def test_curata_scoate_dublurile_si_scurgerile(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    vechi_text = _cuvinte(1)
    examen = _cuvinte(2)
    bun1, bun2, bun3 = _cuvinte(3), _cuvinte(4), _cuvinte(5)
    aproape = vechi_text[:-1] + " și încă puțin."   # aproape identic cu textul vechi
    scurs = _cuvinte(6) + " " + examen[:200]          # are 200 de litere din examen
    vechi = tmp_path / "vechi.txt"
    vechi.write_text(f"{vechi_text}\n<|endoftext|>\n", encoding="utf-8")
    _parchet(tmp_path / "fw" / "data" / "a.parquet",
             [bun1, vechi_text.upper(), aproape, scurs, bun2, bun2, "scurt", bun3])
    (tmp_path / "oa").mkdir()
    with gzip.open(tmp_path / "oa" / "m.jsonl.gz", "wt", encoding="utf-8") as f:
        for d in [{"message_tree_id": "t1", "lang": "ro", "text": "Bună ziua, ce mai faci astăzi, prietene drag?"},
                  {"message_tree_id": "t1", "lang": "ro", "text": "Bine.", "synthetic": True},
                  {"message_tree_id": "t2", "lang": "en", "text": "Hello there, how are you doing today, friend?"}]:
            f.write(json.dumps(d) + "\n")
    de_ferit = {"examen": [examen]}
    info = text_s119.curata(tmp_path / "out", procese=2, limita_gb=1.0, minim_liber_gb=0.0,
                            brut_fineweb=tmp_path / "fw", brut_oasst=tmp_path / "oa", vechi=[str(vechi)],
                            de_ferit=de_ferit, lucru=tmp_path / "lucru", spune=lambda *a, **k: None)
    fw = info["surse"]["fineweb2_ro_s119"]
    assert fw["citite"] == 8
    assert fw["prea_scurte"] == 1
    assert fw["dubluri_identice_vechi"] == 1
    assert fw["dubluri_identice_noi"] == 1
    assert fw["dubluri_aproape_vechi"] == 1
    assert fw["scurgeri"] == 1 and fw["scurgeri_pe_sursa"] == {"examen": 1}
    assert fw["texte_antrenare"] + fw["texte_validare"] == 3
    oa = info["surse"]["oasst2_ro"]
    assert oa["mesaje_ro"] == 2 and oa["mesaje_ro_aruncate"] == 1 and oa["arbori_doar_ro"] == 1
    scris = (tmp_path / "out" / "antrenare.txt").read_text(encoding="utf-8")
    assert examen[:200] not in scris and vechi_text not in scris
    assert not list((tmp_path / "lucru").glob("*.npy"))
    v = text_s119.verifica(tmp_path / "out", procese=1, de_ferit=de_ferit, lucru=tmp_path / "lucru",
                           spune=lambda *a, **k: None)
    assert v["curat"]
    with pytest.raises(FileExistsError):
        text_s119.curata(tmp_path / "out", procese=1, brut_fineweb=tmp_path / "fw", brut_oasst=tmp_path / "oa",
                         vechi=[str(vechi)], de_ferit=de_ferit, lucru=tmp_path / "lucru")


SF = "<|endoftext|>"
SUBSOL = "Urmareste-ne si pe Facebook, abonare gratuita."  # 46 de litere: singur, sub 50


def _sfarsit_cu_separator():
    """Un text care se termină cu un subsol scurt; o „validare” care are același subsol + separator. Bucata comună de
    50 de litere există DOAR dacă te uiți și la separatorul de la capăt."""
    text = _cuvinte(11) + " ZZZ " + SUBSOL
    validare = _cuvinte(12) + " QQQ " + SUBSOL + "\n" + SF + "\n" + _cuvinte(13)
    return text, {"validare_site": [validare]}


def test_sfarsit_de_text_cu_separator_e_prins_de_ambele_cautari():
    from unelte.hrana_fineweb_rest import CAPAT, amprente_de_ferit, cauta_in_bloc
    from unelte.scurgeri_examen import amprente, coduri

    text, de_ferit = _sfarsit_cu_separator()
    ferit, ferit_sursa, _ = amprente_de_ferit(de_ferit, text_s119.LUNGIME)
    # Înainte (doar rând nou + text): nu se vedea.
    vechi = amprente(coduri("\n" + text), text_s119.LUNGIME)
    assert not text_s119._in(ferit, vechi).any()
    # Prima căutare, reparată:
    r = text_s119.judeca_texte([(text, 300)], ferit, ferit_sursa, np.zeros(0, dtype=np.uint64))[0]
    assert r["scurgeri"] == [0] and "\n<|" in r["bucata_scursa"]  # bucata trece peste capătul textului
    # A doua căutare (ca `trece`), cu textul urmat de altul:
    bloc = (text + "\n").encode() + CAPAT + (_cuvinte(14) + "\n").encode() + CAPAT
    a_doua = cauta_in_bloc(bloc, text_s119.LUNGIME, ferit, ferit_sursa)
    assert a_doua["indici_scoase"] == [0]


def test_scoate_lista_si_verifica_fara_ea(tmp_path):
    import hashlib

    text, de_ferit = _sfarsit_cu_separator()
    bune = [_cuvinte(20), _cuvinte(21), _cuvinte(22)]
    toate = [bune[0], text, bune[1], bune[2]]
    iesire = tmp_path / "out"
    iesire.mkdir()
    continut = "".join(f"{t}\n{SF}\n" for t in toate).encode("utf-8")
    (iesire / "antrenare.txt").write_bytes(continut)
    (iesire / "info.json").write_text(json.dumps({
        "surse": {"x": {"texte_antrenare": 4}}, "sha256_antrenare": hashlib.sha256(continut).hexdigest(),
        "verificare": {"curat": False, "texte_cu_bucati_comune": 1}}), encoding="utf-8")
    liniste = {"spune": lambda *a, **k: None}
    v0 = text_s119.verifica(iesire, procese=1, de_ferit=de_ferit, lucru=tmp_path / "l", **liniste)
    assert not v0["curat"] and v0["texte_cu_bucati_comune"] == 1
    s = text_s119.scoate(iesire, procese=2, de_ferit=de_ferit, lucru=tmp_path / "l", octeti_pe_bloc=300, **liniste)
    assert s["texte"] == 1 and s["amandoua"] == 1 and s["pe_sursa"] == {"validare_site": 1}
    a, b = s["portiuni"][0]
    assert continut[a:b] == f"{text}\n{SF}\n".encode("utf-8")
    assert (iesire / "antrenare.txt").read_bytes() == continut  # nimic rescris
    v = text_s119.verifica(iesire, procese=1, de_ferit=de_ferit, lucru=tmp_path / "l", **liniste)
    assert v["curat"] and v["texte"] == 3 and v["texte_sarite"] == 1
    info = json.loads((iesire / "info.json").read_text(encoding="utf-8"))
    assert len(info["verificari_vechi"]) == 2  # cea veche (necurată) și v0 rămân scrise
    with pytest.raises(FileExistsError):
        text_s119.scoate(iesire, procese=1, de_ferit=de_ferit, lucru=tmp_path / "l")
