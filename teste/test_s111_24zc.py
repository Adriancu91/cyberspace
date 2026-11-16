"""S111 (C-119 E3, 16 nov 2026): config/conv_w2_mare_24zc.toml diferă de conv_w2_mare_24z2.toml doar prin ce cere coada."""

from __future__ import annotations

import tomllib
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent


def _config(nume: str) -> dict:
    return tomllib.loads((RADACINA / "config" / nume).read_text(encoding="utf-8"))


def test_24zc_difera_de_24z2_doar_prin_ce_cere_sarcina():
    z, c = _config("conv_w2_mare_24z2.toml"), _config("conv_w2_mare_24zc.toml")
    sz, sc = z["porturi"]["model"]["setari"], c["porturi"]["model"]["setari"]
    diferite = {k for k in sz.keys() | sc.keys() if sz.get(k) != sc.get(k)}
    assert diferite == {"cale_stare", "fractie_conversatie", "fractie_hrana", "optimizator", "rata_invatare",
                        "incalzire_pasi", "durata_scaderii_secunde"}
    assert sc["cale_stare"] == "lucru/w2_mare_24zc/gpt.pt"
    assert sc["fractie_conversatie"] == 0.45 and sc["fractie_hrana"] == 0.30
    assert sc["optimizator"] == "adamw" and sc["rata_invatare"] == 0.00001
    assert sc["incalzire_pasi"] == 1000 and sc["durata_scaderii_secunde"] == 25200
    assert sc["racire_finala"] == 0.25 and sc["lot"] == 6 and sc["adunare_loturi"] == 16
    assert sc["hrana"] == sz["hrana"]
    assert c["platforma"]["nume"] == "w2_mare_24zc"
    # restul configurării (platforma în afară de nume, paznicul, celelalte porturi) e identic
    zp, cp = dict(z["platforma"]), dict(c["platforma"])
    zp.pop("nume"), cp.pop("nume")
    assert zp == cp and z["paznic"] == c["paznic"]
    for port in z["porturi"]:
        if port != "model":
            assert z["porturi"][port] == c["porturi"][port], port
    assert z["porturi"]["model"]["modul"] == c["porturi"]["model"]["modul"]
