"""Registrul regulilor explicite de sintaxă, acord și dezambiguizare (numele, descrierea, statutul).

Regulile sunt implementate în cod (acord.py, dependente.py, ../dezambiguizare.py); aici sunt descrise ca să poată fi
listate (`motor.reguli()`), citate în explicații și numărate în raportul de acoperire. Statutul „evaluata” înseamnă că
regula are teste în `teste/` și e verificată pe corpus; „implementata” — are doar teste unitare.
"""

from __future__ import annotations

from ..baza import Baza
from ..identificatori import id_regula

REGULI_ACORD = [
    ("subst_adj", "Adjectivul se acordă cu substantivul în gen, număr și caz (fata frumoasă, fetei frumoase, băieții frumoși).", "evaluata"),
    ("subst_det", "Determinantul (articol nehotărât, demonstrativ, posesiv, nehotărât) se acordă cu substantivul în gen, număr și caz (acest băiat, această fată, unui om, unei femei).", "evaluata"),
    ("articol_hotarat_unic", "Într-un grup nominal articolul hotărât apare o singură dată: pe substantiv (băiatul frumos) sau pe adjectivul antepus (frumosul băiat), nu pe amândouă.", "evaluata"),
    ("al_a_ai_ale", "Articolul posesiv-genitival al/a/ai/ale se acordă în gen și număr cu obiectul posedat (cartea elevului / o carte a elevului / cărțile ale … ✗), nu cu posesorul.", "evaluata"),
    ("subiect_predicat", "Predicatul se acordă cu subiectul în persoană și număr (copiii merg, copilul merge, eu merg); subiectul multiplu cere pluralul.", "evaluata"),
    ("numeral_de", "De la 20 în sus, numeralul cardinal se leagă de substantiv prin „de” (douăzeci de copii, 100 de lei); sub 20 fără „de” (19 copii); 101–119 fără „de” (o sută cinci copii).", "evaluata"),
    ("doi_doua", "Numeralele doi/două, doisprezece/douăsprezece, 21–22… se acordă în gen cu substantivul (doi băieți, două fete).", "evaluata"),
    ("nume_predicativ", "Numele predicativ adjectival se acordă cu subiectul (fata este frumoasă, copiii sunt obosiți).", "implementata"),
    ("participiu_pasiv", "Participiul din diateza pasivă se acordă cu subiectul (cartea a fost citită, cărțile au fost citite).", "implementata"),
]

REGULI_SINTAXA = [
    ("grup_nominal", "Grupul nominal: [DET/NUM]* [ADJ antepus]* SUBST [ADJ postpus]* [DET postpus] [al/a/ai/ale + GENITIV | GENITIV]; adjectivele postpuse intră în grup doar dacă se acordă.", "evaluata"),
    ("grup_verbal", "Grupul verbal: [nu] [clitice] [AUX] [să] VERB; perfect compus = am/ai/a/am/ați/au + participiu; viitor = voi/vei/va/vom/veți/vor + infinitiv; condițional = aș/ai/ar/am/ați/ar + infinitiv; conjunctiv = să + formă finită; pasiv = a fi + participiu acordat.", "evaluata"),
    ("subiect", "Subiectul: grupul nominal în nominativ fără prepoziție, cel mai apropiat de predicat (înainte sau după el); pronumele personal accentuat în nominativ; la persoanele I și II subiectul e opțional (subînțeles).", "evaluata"),
    ("complement_direct", "Complementul direct: grupul nominal fără prepoziție de după verbul tranzitiv sau cu „pe” (persoane / nume proprii); cliticele de acuzativ (îl, o, îi, le, mă, te, ne, vă).", "evaluata"),
    ("complement_indirect", "Complementul indirect: grupul nominal în dativ sau cliticele de dativ (îi, le, îmi, îți, ne, vă, își).", "implementata"),
    ("complement_prepozitional", "Prepoziția cere cazul: acuzativ (majoritatea), genitiv (asupra, contra, împotriva, deasupra…), dativ (datorită, grație, mulțumită, conform, potrivit).", "evaluata"),
    ("negatie", "Negația: „nu” înaintea verbului (și a cliticelor/auxiliarelor); dubla negație cu nimeni/nimic/niciun/niciodată cere „nu”.", "implementata"),
    ("interogatie", "Interogația: semnul „?”, cuvinte interogative (cine, ce, care, unde, când, cum, cât, de ce, oare) sau inversiune.", "implementata"),
    ("imperativ", "Imperativul: forma de imperativ (vino!, plecați!), cu clitice postpuse (spune-mi!), negativul cu „nu” + infinitiv la singular (nu pleca!).", "implementata"),
    ("coordonare", "Coordonarea: și/sau/ori/dar/iar/însă/ci/nici leagă elemente de același fel; un subiect coordonat e plural.", "evaluata"),
    ("subordonare", "Subordonarea: că/să/dacă/deși/fiindcă… + propoziție; relativele cu care/ce/cine/cât; locuțiunile conjuncționale.", "implementata"),
    ("topica", "Topica: ordinea obișnuită S–V–O, dar subiectul poate sta după verb (vine mama) și complementul înaintea lui (pe Ion l-am văzut); analiza păstrează ambele atașări când nu poate decide.", "implementata"),
    ("clitice", "Pronumele clitice stau înaintea verbului (îl văd, l-am văzut) sau după imperativ/gerunziu (văzându-l, vezi-l); se desprind cu cratimă.", "evaluata"),
    ("impersonal", "Construcțiile impersonale: se + verb la persoana a III-a sg (se spune), trebuie să, e bine să.", "implementata"),
    ("diateza", "Diateza: activă; pasivă = a fi + participiu (+ de/de către); reflexivă/pronominală = clitic reflexiv (se, își).", "implementata"),
    ("punctuatie", "Punctuația cu efect structural: punct/semnul întrebării/exclamării închid propoziția; virgula separă apoziții, vocative, coordonări și subordonate antepuse.", "implementata"),
    ("elipsa", "Elipsa: propozițiile fără verb (răspunsuri scurte, titluri) se analizează ca grup nominal / adverbial fără predicat, cu nota „fără predicat”.", "implementata"),
]

REGULI_DEZAMBIGUIZARE = [
    ("frecventa_corpus", "Dovadă explicabilă: numărul de apariții ale perechii formă–analiză în corpusul UD RRT (antrenare + dezvoltare). Nu e probabilitate calibrată.", "evaluata"),
    ("statut_forma", "Formele validate (două surse) sunt preferate celor doar atestate; cele doar generate de reguli sunt preferate ipotezelor.", "evaluata"),
    ("dupa_sa", "După „să” urmează un verb la conjunctiv (sau fi/auxiliar); după „a” (particulă) un infinitiv; după am/ai/a/ați/au (auxiliar) un participiu; după voi/vei/va… un infinitiv; după aș/ai/ar un infinitiv.", "evaluata"),
    ("o_ambiguu", "„o”: articol (o fată), pronume clitic (o văd, am văzut-o), auxiliar de viitor popular (o să vină) — ales după vecini.", "evaluata"),
    ("a_ambiguu", "„a”: auxiliar (a venit), particulă de infinitiv (a merge), articol posesiv (a Mariei, a lui), prepoziție (a doua), verb (a avea).", "evaluata"),
    ("acord_vecini", "Determinanții, numeralele și adjectivele preferă analiza care se acordă cu substantivul vecin.", "evaluata"),
    ("subst_vs_verb", "Omonimele substantiv/verb: după determinant, prepoziție sau adjectiv → substantiv; după pronume clitic, „nu”, „să”, auxiliar → verb.", "evaluata"),
    ("majuscula", "Majuscula la început de propoziție nu e dovadă de nume propriu; în interiorul propoziției, da.", "evaluata"),
    ("ambiguitate_pastrata", "Dacă primii doi candidați au scoruri apropiate și nicio regulă decisivă nu i-a despărțit, cuvântul rămâne marcat „ambiguu”, cu toate variantele.", "evaluata"),
    ("sens_din_context", "Sensurile candidate se ordonează după compatibilitatea cu vecinii (concepte RoWordNet înrudite cu cele ale cuvintelor din propoziție); fără dovezi, toate sensurile rămân candidate.", "implementata"),
]


def scrie_in_baza(baza: Baza) -> dict:
    n = 0
    for tip, lista in (("acord", REGULI_ACORD), ("sintaxa", REGULI_SINTAXA), ("dezambiguizare", REGULI_DEZAMBIGUIZARE)):
        for nume, descriere, statut in lista:
            baza.adauga_regula(id_regula(tip, nume), tip, nume, descriere, None, "GALR; convențiile UD RRT; implementare proprie", statut)
            n += 1
    baza.commit()
    return {"reguli": n}
