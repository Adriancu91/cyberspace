# Limitările rămase (versiunea 0.1.0, 19 octombrie 2026)

Cifrele vin din raportul de acoperire (`docs/rapoarte/2026-10-19_0230_acoperire_limba_romana.json`) și din evaluarea pe
setul de test UD RRT (729 propoziții nefolosite la construirea lexiconului sau a regulilor).

## Lexicon și morfologie

- **19.724 substantive fără gen** (din 118.246): au venit doar din Hunspell fără clasă de flexiune sau din RoWordNet; nu li se
  generează paradigma. Ca să primească gen trebuie o sursă (Wiktionary nu le are) sau o regulă de ghicire a genului după
  terminație (nu e implementată, ca să nu inventăm).
- **810.766 forme doar generate, neconfirmate** de nicio atestare (din 1.767.669): sunt forme produse de regulile Hunspell sau de
  paradigmele proprii pentru cuvinte fără tabel de flexiune în surse. Nu sunt greșite de regulă, dar nu sunt verificate.
  Motorul le marchează `generat` și le preferă mai puțin la dezambiguizare.
- **22.712 forme în care paradigma proprie e contrazisă de surse** (cele mai multe la genitiv-dativul feminin: `subst_fem_sg_gd_*`
  ≈ 6 %, pluralul ghicit al neutrelor/masculinelor, vocativele în -ule/-o). Regulile nu tratează alternanțele neregulate
  (om → oameni, băiat → băieți) și pluralele cu -uri/-e/-i nedeterminabile; forma corectă rămâne cea atestată.
- **Verbele neregulate** (a fi, a avea, a vrea, a da, a sta, a lua, a bea, a ști, a mânca, a putea…) au formele doar din surse;
  paradigma regulată produce forme false pentru ele, numărate ca „contrazise”. 292 de verbe au grupul de conjugare nedeterminat
  (fără forma de prezent în surse): li se generează ambele variante (-ez / fără -ez etc.), ambele `generat`.
- **3.113 intrări verbale Hunspell** nu au infinitivul confirmat și nu au fost importate (alternanțe vocalice: port → purta).
- **33.110 cuvinte** sunt cunoscute doar ortografic (din Hunspell, fără clasă): motorul le recunoaște ca scrise corect, dar fără
  lemă, categorie sau trăsături; **133 lexeme** au categoria necunoscută (X).
- **Textul fără diacritice** e acceptat (potrivire pe forma „plată”, marcată), dar ambiguitatea crește (sa/să, mult/mulț).
- Registrul (regional, arhaic, învechit, colocvial) e marcat doar pentru 8.006 lexeme (din Wiktionary); Hunspell și RoWordNet
  nu îl dau.
- Gradele de comparație, timpurile compuse și diateza pasivă sunt tratate sintactic (nu ca forme).

## Sintaxă

- Arborele de dependențe e **de bază**: pe setul de test UD, UAS 67,1 %, LAS 58,1 % (tokeni nepunctuație, propoziții cu
  tokenizare identică; 94,8 % din propoziții). Lipsesc: valența verbală (tranzitiv/intranzitiv), coreferința, tratarea
  completă a coordonării și a subordonatelor relative, construcțiile eliptice complexe. Atașarea grupurilor prepoziționale
  rămâne ambiguă și e raportată ca alternativă.
- Categoria (UPOS) e corectă în 93,2 % din tokeni pe setul de test; cele mai frecvente greșeli: participiu verbal citit ca
  adjectiv, adverb ↔ prepoziție (la cuvinte ca „ca”, „după”), substantiv ↔ adjectiv la omografe.
- **Verificarea acordului** e conservatoare și totuși semnalează ~6,6 alarme false la 100 de propoziții din corpus (texte
  juridice, literare, poezie): subiecte postpuse, coordonări ambigue, nume compuse. Pe propozițiile de regresie scrise de mână
  (16 corecte / 9 greșite) nu are alarme false și găsește toate greșelile. Nu detectează: acordul numelui predicativ la
  distanță, acordul participiului pasiv cu subiectul (regulile sunt descrise, cu statut „implementata” fără evaluare pe corpus),
  dezacordurile „posibile” sunt raportate cu certitudine `posibila`.
- Subordonarea, interogația, imperativul, negația, construcțiile impersonale sunt recunoscute la nivel de bază (mărci,
  relații), fără analiză semantică a lor.

## Semantică și dezambiguizare

- Sensurile în română vin din RoWordNet pentru **53.239 lexeme**; alte 74.000 au doar glose în engleză (Wiktionary); **66.368
  lexeme nu au niciun sens documentat**. Nu se inventează definiții.
- Alegerea sensului din context e o metodă de suprapunere lexicală (Lesk) explicabilă; nu există corpus românesc adnotat
  semantic în surse, deci nu e evaluată cantitativ. Fără dovezi, toate sensurile rămân candidate („nedeterminat”).
- Rolurile semantice sunt derivate din relațiile sintactice + animat/inanimat (ierarhia RoWordNet) + prepoziții; fără
  restricții de selecție din surse. Un rol greșit în sintaxă dă un rol greșit în semantică.
- Contextul conversației: infrastructura există (tabela `contexte`, parametrul `context` al lui `analizeaza`), dar contextul nu
  influențează încă analiza.
- RoWordNet conține 1 ciclu în ierarhia hiperonimelor (eroare a sursei), detectat și raportat, nu „reparat”.

## Surse

- Wiktionary (kaikki) e extras automat; unele forme au etichete nerecunoscute de extractor (cazul adjectivelor e dedus din
  structura tabelului) — notat în proveniență.
- UD RRT: lemele sunt automate (README-ul corpusului) — erorile lor intră ca atare, cu proveniență.
- Hunspell: regulile cu prefix (re-, ne-, auto-) și cliticele lipite nu se materializează; tezaurul nu e folosit.
- Niciun inventar de referință al „întregii limbi române” nu există în surse; procentele de acoperire sunt față de surse și
  față de seturile de test, nu față de limbă.

## Ce ar aduce cel mai mult la următoarea etapă

1. ghicirea genului substantivelor după terminație, cu confirmare din corpus (reduce cele 19.724 fără paradigmă);
2. valența verbală (tranzitiv/intranzitiv, prepoziții cerute) extrasă din corpus — îmbunătățește subiectul, obiectul și acordul;
3. o listă de participii adjectivizate din corpus (reduce confuzia participiu/adjectiv);
4. importul UD_Romanian-SiMoNERo (medical) și Nonstandard (română veche), ambele CC BY-SA 4.0, cu același importator;
5. contextul conversațional: anafora pronumelor (el/ea/ei) spre entitățile menționate anterior.
