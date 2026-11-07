"""S83b (C-82): modelul în uz e #513 — căile implicite ale modulelor de inferență și ale bancului/reglajului CCM."""

import inspect
import tomllib
from pathlib import Path

from module.calcul import banc, reglaj
from module.inferenta_ccm import InferentaCCM
from module.inferenta_kgr1 import InferentaKGR1

RADACINA = Path(__file__).resolve().parents[1]
KGR_IN_UZ = "lucru/export/kronos_513_q8_0.kgr"


def _implicit(cls: type, nume: str) -> str:
    return inspect.signature(cls.__init__).parameters[nume].default


def test_modulele_de_inferenta_pornesc_implicit_pe_513():
    assert _implicit(InferentaKGR1, "cale") == KGR_IN_UZ
    assert _implicit(InferentaCCM, "cale") == KGR_IN_UZ


def test_bancul_si_reglajul_au_implicit_513():
    for modul in (banc, reglaj):
        text = Path(modul.__file__).read_text(encoding="utf-8")
        assert f'default="{KGR_IN_UZ}"' in text
        assert 'default="lucru/export/kronos_477_q8_0.kgr"' not in text


def test_manifestele_nu_s_au_schimbat():
    assert InferentaKGR1.MANIFEST["versiune"] == "0.1.0"
    assert InferentaCCM.MANIFEST["versiune"] == "0.2.0"


def test_configurarea_punctelor_de_salvare_are_513_in_uz():
    c = tomllib.loads((RADACINA / "config/puncte_salvare.toml").read_text(encoding="utf-8"))
    assert c["model_in_uz"] == 513
