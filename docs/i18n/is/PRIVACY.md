> Þetta er vélstudd þýðing. Enska útgáfan gildir.

# Persónuverndartilkynning Fontes

Fontes keyrir á tölvunni þinni. Leitir þínar og skjölin sem þú opnar haldast
á milli tölvunnar þinnar, heimildanna sem þú leitar í (opinberu heimildanna, auk CourtListener og Lexifina þar sem þú notar þær, sjá hér að neðan) og gervigreindarforritsins sem þú notar (samkvæmt
eigin skilmálum þess forrits). Fontes sjálft sendir forriturum Fontes **sjálfgefið
ekkert**.

## Hvað getur farið frá tölvunni þinni, og hvenær

**1. Uppfærsluathugun (virk sjálfgefið).** Einu sinni á dag spyr Fontes PyPI, almennu
Python-pakkaskrána, hver nýjasta útgáfan sé. Beiðnin ber ekkert um þig eða vinnu þína;
PyPI sér IP-töluna þína, eins og við hvert niðurhal. Til að slökkva á þessu skaltu stilla `FONTES_NO_UPDATE_CHECK=1`
(tilkynningin í forritinu) og `FONTES_NO_AUTO_UPDATE=1` (sjálfvirkar uppfærslur uppsetningarforritsins).

**2. Notkunartölur (óvirkar nema þú kveikir á þeim).** Ef þú samþykkir (opt-in) sendir Fontes einu sinni á dag:

- útgáfu Fontes og tegund stýrikerfisins þíns (macOS, Windows, Linux);
- fyrir hvern dag, hversu oft hvert verkfæri var notað fyrir hvern lögsögukóða, til dæmis
  „2026-11-10, nl, search_caselaw, 12“.

Það eru öll skilaboðin. Þau innihalda aldrei leitir þínar, auðkenni skjala eða mála, texta skjala,
nafn þitt, aðgang eða neitt auðkenni fyrir þig eða tölvuna þína. Tölurnar bíða á tölvunni þinni
(í skyndiminnismöppu Fontes, `stats.json`) þar til þær eru sendar; ef sending mistekst bíða þær til
næsta dags.

- **Samþykkja (opt in)**: svaraðu „j“ þegar uppsetningarforritið spyr, eða stilltu `FONTES_STATS=1` fyrir Fontes-þjóninn.
- **Afþakka (opt out)**: keyrðu uppsetningarforritið aftur og ýttu á Enter við þeirri spurningu, eða fjarlægðu
  `FONTES_STATS`. Ef þú eyðir `stats.json` fargast allt sem ekki hefur enn verið sent.

**3. Villuskýrslur (aðeins þegar þú sendir slíka).** Þegar þú biður um skýrslu (`fontes report-bug`, eða biður
gervigreindarforritið þitt að tilkynna villu í Fontes) sýnir Fontes þér fyrst alla skýrsluna og sendir hana aðeins ef
þú staðfestir. Hún inniheldur útgáfu Fontes, tegund stýrikerfisins þíns, lögsögukóðann, heiti verkfærisins og
villuboðin úr síðasta misheppnaða verkfærakallinu (með leitarorðum þínum og auðkennum fjarlægðum), og
athugasemd ef þú skrifar hana. Ekki setja upplýsingar um skjólstæðinga í athugasemdina. Til að styðja þetta geymir Fontes
síðustu villuna á tölvunni þinni (`last-error.json` í skyndiminnismöppu þess, skipt út í hvert skipti);
hún er aldrei send ein og sér.

**4. Lexifina (virk sjálfgefið).** `get_law_on_date`, `get_law_history`, 91 landið og lög Indlands sem lesin eru í gegnum skrá Lexifina um lögin fara til Lexifina, auk eða í stað opinberrar vefsíðu. Leitarorð þín, tilvitnanir og dagsetningar fara til ókeypis netþjóns Lexifina, `global-law.lexifina.com`, sem Lexifina rekur, ekki forritarar Fontes. Lexifina skjalfestir að netþjónn þess skrái hvaða verkfæri var kallað og hversu langan tíma það tók, aldrei hvað var spurt; Fontes getur ekki staðfest það, og skilmálar Lexifina gilda. Lexifina sér IP-tölu þína, eins og hver vefþjónn. Til að slökkva alveg á Lexifina skaltu stilla `WLM_LEXIFINA=0`; þessi tvö verkfæri og löndin hætta þá að virka og ekkert er sent þangað.

## Hvert þetta fer og hversu lengi það er geymt

Notkunartölur og villuskýrslur fara á lítinn þjón sem forritari Fontes rekur
(`relay.kinetra.fit`). Hann geymir engar IP-tölur: þær eru aðeins notaðar í minni, stutta stund, til að
stöðva flóð beiðna, og vefþjónninn heldur engan aðgangsannál fyrir hann. Tölur eru lagðar saman í daglegar
heildartölur; einstakar sendingar eru ekki geymdar. Heildartölur eru geymdar í allt að 2 ár, villuskýrslur í allt að
1 ár, og síðan eytt. Ekkert er selt eða deilt.

Ef ekki næst samband við þjóninn er ekkert sent: tölur haldast á tölvunni þinni og villuskýrslur
vísa þér í staðinn á villurakningarkerfið (issue tracker).

## Hver ber ábyrgð, og á hvaða grundvelli

Ábyrgðaraðili notkunartalna og villuskýrslna er Yüce Karapazar, forritari
Fontes. Samband: fontesmcp@proton.me.

Lagagrundvöllurinn er samþykki þitt (a-liður 1. mgr. 6. gr. UK GDPR og almennu persónuverndarreglugerðar ESB, GDPR). Notkunartölur
eru aðeins sendar ef þú samþykkir (opt-in), og villuskýrsla aðeins eftir að þú hefur staðfest hana. Þú getur hvenær sem er dregið
samþykki þitt til baka með því að afþakka eins og lýst er hér að ofan; það hefur ekki áhrif á það sem var sent
áður.

## Samband

Spurningar eða beiðnir: sendu tölvupóst á fontesmcp@proton.me, eða stofnaðu issue á
<https://github.com/ykarapazar/fontes/issues>.
