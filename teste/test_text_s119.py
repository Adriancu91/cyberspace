"""S119: unealta pentru textul românesc nou (curățare, dubluri, scurgeri) pe date mici, făcute aici."""

from __future__ import annotations

import gzip
import json
import random

import pytest

pa = pytest.importorskip("pyarrow")
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
