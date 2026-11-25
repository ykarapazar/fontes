> Aistriúchán é seo a rinneadh le cúnamh ó mheaisín. Is é an leagan Béarla an leagan údarásach.

# Fontes: ceisteanna agus freagraí

## Cad é Fontes?

Freastalaí MCP saor in aisce, foinse oscailte (Apache 2.0). Ligeann sé d'aon aip a labhraíonn an
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI agus aipeanna eile) breithiúnais
chúirte agus reachtaíocht a chuardach beo ar shuíomhanna gréasáin cúirteanna agus rialtais in 120+
dlínse agus cúirt idirnáisiúnta (124 oiriúnaitheoir). Ainmníonn gach toradh a fhoinse agus tá nasc
chuig an mbunleagan ann.

## An bhfuil na téacsanna oifigiúil?

Den chuid is mó, ach ní i gcónaí.

- Ritheann cúirt, aireacht nó iris oifigiúil formhór na bhfoinsí.
- Foilsíonn rialtas roinnt téacsanna comhdhlúite ach tá siad neamhoifigiúil go sainráite: níl ach
  an iris oifigiúil barántúil.
- Ní suíomhanna rialtais ar chor ar bith iad roinnt bheag foinsí (mar shampla LexiVox, LawPhil,
  Maqam, Wikisource).

Cuireann Fontes fógra "Unofficial source" le gach freagra a thagann ó cheann díobh seo. Sula
ndéanann tú lua ar aon rud, seiceáil an foilseachán oifigiúil. Ainmníonn an tábla clúdaigh sa
[README](README.md#clúdach) agus `list_jurisdictions` an fhoinse do gach dlínse.

## Cé na dlínsí a chlúdaíonn sé, agus cé chomh maith?

124 oiriúnaitheoir: 108 ballstát de chuid na NA, Hong Cong, an Chosaiv, an Phalaistín, an Téaváin,
Cúirteanna DIFC agus 11 chúirt agus chomhlacht idirnáisiúnta (amhail an Chúirt Eorpach um Chearta
an Duine, an AE, an ICJ agus an EDT).

Tá difríocht mhór sa chlúdach. Faoi riail dhian (fasaigh na príomhchúirte ginearálta, nó an
bunreacht agus na príomhachtanna, sroichte go hiomlán), áirítear 72 as an 124 mar chlúdaithe.
Liostaíonn [COVERAGE.md](COVERAGE.md), do gach dlínse, an méid a shroicheann Fontes, an méid nach
sroicheann sé, agus cén fáth.

## An dteastaíonn eochair API uaim?

Do bheagnach gach dlínse, ní theastaíonn. Teastaíonn eochair saor in aisce ó roinnt foinsí: féach
[KEYS.md](KEYS.md).

- **An Fhrainc:** teastaíonn. Tá an Fhrainc múchta go dtí go socraíonn tú
  `WLM_FR_PISTE_CLIENT_ID` agus `WLM_FR_PISTE_CLIENT_SECRET`. Tagann siad seo ó chuntas PISTE saor
  in aisce (piste.gouv.fr) le haip atá liostáilte le Judilibre agus Légifrance.
- **Na Stáit Aontaithe:** roghnach. Oibríonn cuardach cásdlí gan eochair, ach ní cheadaíonn an
  eochair taispeána chomhroinnte ach thart ar 10 gcuardach sa lá in aghaidh an tseolta IP. Ardaíonn
  eochair api.data.gov saor in aisce in `WLM_US_GOVINFO_KEY` é.

Socraigh iad seo mar athróga timpeallachta don fhreastalaí Fontes i socruithe MCP d'aipe. Iarrann na suiteálaithe iad tar éis na suiteála, agus athraíonn a dtosaitheoir
**Add or change keys** iad níos déanaí.

Ar leith uaidh sin, deir roinnt bheag foinsí ina dtéarmaí go dteastaíonn cead an fhoilsitheora le
haghaidh rochtana uathoibrithe. Tá siad marcáilte OFF agus fanann siad múchta. Ní athraíonn eochair
é sin; ní athraíonn ach cead an fhoilsitheora é (ansin socraigh `WLM_PERMITTED=<codes>`).

## Cad a fhágann mo ríomhaire?

Ní théann do chuardaigh ach chuig an bhfoinse atá á cuardach. Ní choinníonn Fontes bunachar
sonraí agus ní theastaíonn cuntas uaidh.

Seachas na foinsí, fiafraíonn Fontes de PyPI uair sa lá an bhfuil leagan níos nuaí ann (múch é le
`FONTES_NO_UPDATE_CHECK=1`). Tá comhairimh úsáide múchta mura gcasann tú air iad, agus ní sheoltar
tuairisc ar fhabht ach tar éis duit í a fheiceáil agus a dheimhniú. Feiceann d'aip IS do chomhrá
faoina téarmaí féin.

Sonraí iomlána: [PRIVACY.md](PRIVACY.md).

## An comhairle dlí é seo?

Ní hea. Uirlis taighde é Fontes. Aimsíonn sé téacsanna; ní insíonn sé duit cad is brí leo do do
chás, agus ní chruthaíonn a úsáid caidreamh dlíodóra agus cliaint le duine ar bith. Is féidir leis
an aip IS téacs a mhíléamh, mar sin léigh an breithiúnas nó an fhoráil iomlán sula mbraitheann tú
air. Le haghaidh comhairle, téigh chuig dlíodóir atá cáilithe san áit a n-eascraíonn do cheist.

## Cé a choinníonn é? An leanfaidh sé ag obair?

Duine amháin: Yüce Karapazar. Níl aon chomhlacht taobh thiar de Fontes, níl aon chonradh tacaíochta
ná gealltanas leibhéal seirbhíse. Ní thairgtear aon seirbhísí dlí.

Seiceáiltear na foinsí uair sa lá agus foilsítear na torthaí ar an
[leathanach stádais](https://ykarapazar.github.io/fontes/status/?lang=ga). Athraíonn suíomhanna
gréasáin cúirteanna agus rialtais gan fógra, mar sin is féidir le foinse briseadh am ar bith. Níl aon
ráthaíocht go leanfaidh aon fhoinse, ná Fontes féin, ag obair. Soláthraítear Fontes "mar atá", gan
bharántas (ailt 7 agus 8 den [LICENSE](../../../LICENSE)).

## Tá téacs mícheart nó as dáta, nó tá foinse briste. Conas a thuairiscím é?

- Oscail ceist (issue) leis an bhfoirm "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Abair cén dlínse, cad a d'fhiafraigh
  tú, cad a fuair tú, agus an leathanach oifigiúil a thaispeánann an téacs ceart.
- Nó iarr ar d'aip IS "fabht in Fontes a thuairisciú" (nó rith `fontes report-bug`). Feiceann tú an
  tuairisc sula seoltar aon rud.
- Nó seol ríomhphost chuig fontesmcp@proton.me.

Ná cuir sonraí cliant ná fíricí rúnda i dtuairisc.

**Má ritheann tú ceann de na foinsí** agus go bhfuil rud éigin mícheart (do théarmaí, do
robots.txt, do theorainneacha ráta), seol ríomhphost chuig fontesmcp@proton.me. Ceartófar an
fhoinse nó múchfar í.

## Cén difríocht atá idir Fontes agus uirlisí taighde dlí óstáilte?

- **Ritheann sé ar do ríomhaire.** Níl aon fhreastalaí Fontes ná cuntas ann. Ciallaíonn sé sin
  freisin nach n-oibríonn sé ach in aipeanna ar féidir leo freastalaí MCP áitiúil a thosú (Claude
  Desktop, Codex, Cursor, VS Code agus a leithéid), ní in aipeanna gréasáin amháin nach nglacann
  ach le nascóirí óstáilte.
- **Níl bunachar sonraí aige.** Téann gach cuardach beo chuig suíomh gréasáin nó API an
  fhoilsitheora féin, mar sin tá na torthaí chomh reatha leis an bhfoinse, agus is é cáilíocht
  cuardaigh na foinse féin cáilíocht an chuardaigh. Níl aon chuardach séimeantach thar innéacs
  coimeádta ann.
- **Ní shocraíonn sé aon teorainn úsáide.** Níl aon uasteorainn mhíosúil glaonna ag Fontes. Spásálann
  sé a chuid iarratas chuig gach suíomh gréasáin, agus cuireann roinnt foinsí teorainn le cé chomh
  tapa nó cé chomh minic is féidir iad a cheistiú.
- **Is foinse oscailte é.** Is féidir leat gach oiriúnaitheoir a léamh agus a fheiceáil go díreach
  cá as a dtagann gach téacs.
- **Níl aon díoltóir taobh thiar de.** Gan chonradh, deasc tacaíochta ná gealltanas aga fónaimh
  (féach "Cé a choinníonn é?").

## Cé na haipeanna agus na córais a n-oibríonn sé leo?

Aon aip MCP ar féidir léi freastalaí áitiúil (stdio) a rith, mar shampla Claude Desktop, Claude
Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio agus Cline.
Ritheann Fontes ar macOS, Windows agus Linux, áit ar bith a ritheann uv (Python 3.13+). Ar Mac nó PC Windows,
socraíonn suiteálaí aon chliceáil Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf,
Gemini CLI, Zed, LM Studio agus Cline in aon iarraidh amháin.
Céimeanna do gach aip: [INSTALL.md](INSTALL.md).

## An féidir liom cód a chur leis?

Ní féidir faoi láthair. Fáiltítear roimh cheisteanna (issues), tuairiscí ar fhoinsí agus iarratais
ar dhlínsí. Féach [CONTRIBUTING.md](../../../CONTRIBUTING.md).
