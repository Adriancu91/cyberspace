"""S2: măsurarea problemelor de română din perechi (fără motor: o funcție de verificare scrisă aici)."""

from unelte import masoara_romana as mr


def _verifica(text):
    probleme = []
    if "fata frumos" in text:
        probleme.append({"tip": "acord_subst_adj", "certitudine": "sigura", "propozitie": text, "mesaj": "acord"})
    if "sapte" in text:
        probleme.append({"tip": "ortografie", "certitudine": "probabila", "propozitie": text, "sugestie": "șapte"})
    return {"probleme": probleme}


def test_numara_perechile_cu_probleme_pe_grupe_si_sare_engleza():
    perechi = [
        {"fel": "text", "limba": "ro", "text": "A fost odată o fata frumos.", "raspuns": "Are sapte ani."},
        {"fel": "text", "limba": "ro", "text": "A fost odată o fata frumos.", "raspuns": "Da."},
        {"fel": "conversatie", "limba": "ro", "intrebare": "Salut!", "raspuns": "Salut!"},
        {"fel": "zi", "limba": "en", "raspuns": "fata frumos sapte"},
    ]
    vazute = []
    r = mr.masoara(perechi, lambda t: (vazute.append(t), _verifica(t))[1])
    assert r["romana"] == 3 and r["engleza_nemasurate"] == 1 and r["cu_probleme"] == 2
    assert r["pe_grupe"] == {"acord": 2, "diacritice": 1}
    assert r["pe_certitudine"] == {"sigura": 2, "probabila": 1}
    assert r["cu_probleme_fara_necunoscute"] == 2
    assert vazute.count("A fost odată o fata frumos.") == 1  # textul repetat se verifică o singură dată


def test_exemplele_alese_sunt_aceleasi_cu_aceeasi_samanta():
    probleme = [{"i": i} for i in range(100)]
    assert mr.alese(probleme, 30, 1020) == mr.alese(probleme, 30, 1020)
    assert len(mr.alese(probleme[:5], 30, 1020)) == 5
