"""S96 (C-85 pasul 5): unelte/date_bucati.py — bucățile scrise din cache, cititorul pe rând, verificarea și proba de
identitate (același șir de simboluri, octet cu octet)."""

import hashlib
import json

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from module.model_continuu import cale_simboluri  # noqa: E402
from unelte import date_bucati as db  # noqa: E402


def _sursa(tmp_path, n=103, tip=torch.int16):
    t = torch.arange(n, dtype=tip) * 7 % 16384
    cale = tmp_path / "simboluri.pt"
    torch.save(t, cale)
    return cale, t


def _sha(t):
    return hashlib.sha256(t.numpy().tobytes()).hexdigest()


def test_scrie_citeste_identic(tmp_path):
    sursa, t = _sursa(tmp_path)
    tok = tmp_path / "tok.json"
    tok.write_text("{}", encoding="utf-8")
    dosar = tmp_path / "bucati"
    index = db.scrie(sursa, dosar, 10, tok, 0.0)
    assert len(index["bucati"]) == 11 and index["bucati"][-1]["simboluri"] == 3
    assert index["simboluri_total"] == 103 and not index["partial"] and index["tip"] == "int16"
    assert index["tokenizer"]["sha256"] == hashlib.sha256(b"{}").hexdigest()
    assert index["sha256_tot"] == _sha(t)
    cititor = db.CititorBucati(dosar)
    assert len(cititor) == 103
    lipit = np.concatenate([np.asarray(a) for a in cititor])
    assert np.array_equal(lipit, t.numpy())
    rez = db.citeste(dosar)
    assert rez["simboluri"] == 103 and rez["sha256_tot"] == _sha(t)


def test_int32(tmp_path):
    sursa, t = _sursa(tmp_path, n=25, tip=torch.int32)
    index = db.scrie(sursa, tmp_path / "b", 8, None, 0.0)
    assert index["tip"] == "int32" and index["sha256_tot"] == _sha(t)
    assert np.array_equal(np.concatenate(list(db.CititorBucati(tmp_path / "b"))), t.numpy())


def test_refuza_a_doua_oara(tmp_path):
    sursa, _ = _sursa(tmp_path)
    db.scrie(sursa, tmp_path / "b", 50, None, 0.0)
    with pytest.raises(FileExistsError):
        db.scrie(sursa, tmp_path / "b", 50, None, 0.0)


def test_verifica_prinde_stricaciunea(tmp_path):
    sursa, _ = _sursa(tmp_path)
    dosar = tmp_path / "b"
    db.scrie(sursa, dosar, 20, None, 0.0)
    assert db.verifica(dosar)["ok"]
    f = dosar / "bucata_00002.bin"
    octeti = bytearray(f.read_bytes())
    octeti[0] ^= 1
    f.write_bytes(bytes(octeti))
    rez = db.verifica(dosar)
    assert not rez["ok"] and {g["fisier"] for g in rez["gresite"]} == {"bucata_00002.bin", "(tot șirul)"}
    assert db.main(["verifica", "--dosar", str(dosar)]) == 1


def test_partial_cand_nu_e_loc(tmp_path):
    sursa, _ = _sursa(tmp_path)
    index = db.scrie(sursa, tmp_path / "b", 10, None, 10**9)
    assert index["partial"] and index["bucati"] == [] and "nota_partial" in index


def test_identitate_cap_coada(tmp_path):
    """Comanda întreagă prin main (procese noi pentru încărcare și cititor), cu --config pe un text mic."""
    sursa, t = _sursa(tmp_path)
    dosar = tmp_path / "b"
    assert db.main(["scrie", "--sursa", str(sursa), "--iesire", str(dosar), "--marime", "16",
                    "--minim-liber-gb", "0"]) == 0
    text = tmp_path / "antrenare.txt"
    text.write_bytes(b"un text mic\r\ncu doua randuri\r\n")
    tok = tmp_path / "tok.json"
    tok.write_text("{}", encoding="utf-8")
    cache = tmp_path / "cache"
    cache.mkdir()
    torch.save(t, cale_simboluri(text.read_text(encoding="utf-8"), str(cache), str(tok)))
    config = tmp_path / "c.toml"
    config.write_text(
        "[porturi.date]\nsetari = { cale_antrenare = %s, cale_validare = %s }\n"
        "[porturi.model]\nsetari = { director_cache = %s, cale_tokenizer = %s }\n"
        % tuple(json.dumps(str(x)) for x in (text, text, cache, tok)), encoding="utf-8")
    iesire = tmp_path / "id.json"
    assert db.main(["identitate", "--sursa", str(sursa), "--dosar", str(dosar), "--config", str(config),
                    "--iesire", str(iesire)]) == 0
    rez = json.loads(iesire.read_text(encoding="utf-8"))
    assert rez["identic"] and rez["acum"]["sha256_tot"] == _sha(t) == rez["cititor"]["sha256_tot"]
    assert rez["pornire_linie"]["simboluri"] == 103 and rez["pornire_linie"]["text_caractere"] == 28  # \r\n → \n, ca read_text
    with pytest.raises(FileExistsError):
        db.main(["identitate", "--sursa", str(sursa), "--dosar", str(dosar), "--iesire", str(iesire)])
