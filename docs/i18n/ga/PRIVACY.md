> Aistriúchán é seo a rinneadh le cúnamh ó mheaisín. Is é an leagan Béarla an leagan údarásach.

# Fógra príobháideachta Fontes

Ritheann Fontes ar do ríomhaire. Fanann do chuardaigh agus na doiciméid a osclaíonn tú idir do
ríomhaire, na foinsí oifigiúla a chuardaíonn tú, agus an aip IS a úsáideann tú (faoi théarmaí na
haipe sin féin). Ní sheolann Fontes féin **aon rud de réir réamhshocraithe** chuig forbróirí Fontes.

## Cad is féidir a fhágáil do ríomhaire, agus cathain

**1. Seiceáil nuashonruithe (ar siúl de réir réamhshocraithe).** Uair sa lá fiafraíonn Fontes de
PyPI, innéacs poiblí na bpacáistí Python, cén leagan is nuaí. Níl aon rud fút ná faoi d'obair san
iarratas; feiceann PyPI do sheoladh IP, mar a tharlaíonn le haon íoslódáil. Chun é a mhúchadh,
socraigh `FONTES_NO_UPDATE_CHECK=1` (an fógra san aip) agus `FONTES_NO_AUTO_UPDATE=1`
(nuashonruithe uathoibríocha an tsuiteálaí).

**2. Comhairimh úsáide (múchta mura gcasann tú air iad).** Má roghnaíonn tú páirt a ghlacadh, uair
sa lá seolann Fontes:

- leagan Fontes agus teaghlach do chórais oibriúcháin (macOS, Windows, Linux);
- in aghaidh an lae, cé mhéad uair a úsáideadh gach uirlis do gach cód dlínse, mar shampla
  "2026-11-10, nl, search_caselaw, 12".

Sin í an teachtaireacht iomlán. Ní bhíonn iontu riamh do chuardaigh, aitheantóirí doiciméad nó
cásanna, téacs doiciméad, d'ainm, cuntas, ná aon aitheantóir duitse nó do do ríomhaire. Fanann na
comhairimh ar do ríomhaire (i bhfillteán taisce Fontes, `stats.json`) go dtí go seoltar iad; má
theipeann ar an seoladh fanann siad go dtí an lá dár gcionn.

- **Páirt a ghlacadh (opt in)**: freagair "y" nuair a fhiafraíonn an suiteálaí, nó socraigh
  `FONTES_STATS=1` don fhreastalaí Fontes.
- **Tarraingt siar (opt out)**: rith an suiteálaí arís agus brúigh Enter ag an gceist sin, nó bain
  `FONTES_STATS`. Má scriosann tú `stats.json` caitear amach aon rud nár seoladh fós.

**3. Tuairiscí ar fhabhtanna (ach amháin nuair a sheolann tú ceann).** Nuair a iarrann tú ceann
(`fontes report-bug`, nó iarr ar d'aip IS fabht in Fontes a thuairisciú), taispeánann Fontes an
tuairisc iomlán duit ar dtús agus ní sheolann sé í ach má dheimhníonn tú. Tá inti leagan Fontes,
teaghlach do chórais oibriúcháin, cód dlínse, ainm uirlise agus teachtaireacht earráide an ghlao
uirlise teipthe is déanaí (agus d'fhocail chuardaigh agus aitheantóirí bainte amach), agus nóta má
scríobhann tú ceann. Ná cuir sonraí cliant sa nóta. Chun tacú leis seo, coinníonn Fontes an earráid
is déanaí ar do ríomhaire (`last-error.json` ina fhillteán taisce, a chuirtear ina áit gach uair);
ní sheoltar riamh léi féin í.

## Cá dtéann sé agus cá fhad a choinnítear é

Téann comhairimh úsáide agus tuairiscí ar fhabhtanna chuig freastalaí beag a ritheann forbróir
Fontes (`relay.kinetra.fit`). Ní stórálann sé aon seoltaí IP: ní úsáidtear iad ach sa chuimhne, go
hachomair, chun tuilte a stopadh, agus ní choinníonn an freastalaí gréasáin aon loga rochtana dó.
Cuirtear comhairimh le hiomláin laethúla; ní choinnítear aighneachtaí aonair. Coinnítear iomláin
suas le 2 bhliain, tuairiscí ar fhabhtanna suas le bliain amháin, agus scriostar ansin iad. Ní
dhíoltar ná ní roinntear aon rud.

Mura féidir teacht ar an bhfreastalaí sin, ní sheoltar aon rud: fanann comhairimh ar do ríomhaire
agus treoraíonn tuairiscí ar fhabhtanna chuig an rianaire ceisteanna (issue tracker) thú ina ionad.

## Cé atá freagrach, agus ar cén bonn

An rialaitheoir sonraí do chomhairimh úsáide agus tuairiscí ar fhabhtanna ná Yüce Karapazar,
forbróir Fontes. Teagmháil: fontesmcp@proton.me.

Is é an bonn dleathach do thoiliú (Airteagal 6(1)(a) de GDPR na RA agus GDPR an AE). Ní sheoltar
comhairimh úsáide ach má roghnaíonn tú páirt a ghlacadh, agus ní sheoltar tuairisc ar fhabht ach tar
éis duit í a dheimhniú. Is féidir leat do thoiliú a tharraingt siar am ar bith trí tharraingt siar
mar a thuairiscítear thuas; ní théann sé seo i bhfeidhm ar an méid a seoladh roimhe sin.

## Teagmháil

Ceisteanna nó iarratais: seol ríomhphost chuig fontesmcp@proton.me, nó oscail ceist (issue) ag
<https://github.com/ykarapazar/fontes/issues>.
