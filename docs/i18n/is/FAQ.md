> Þetta er vélstudd þýðing. Enska útgáfan gildir.

# Fontes: spurningar og svör

## Hvað er Fontes?

Ókeypis MCP-þjónn með opnum hugbúnaði (Apache 2.0). Hann gerir hvaða forriti sem talar Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI og fleirum) kleift að leita í dómum og
löggjöf í rauntíma á vefsíðum dómstóla og stjórnvalda í 125 lögsögum og alþjóðlegum
dómstólum, auk 91 lands til viðbótar úr skrá Lexifina (sjá hér að neðan). Hver niðurstaða nefnir heimild sína og tengir á frumritið.

## Eru textarnir opinberir?

Að mestu leyti, en ekki alltaf.

- Flestum heimildum er haldið úti af dómstóli, ráðuneyti eða opinberu birtingarriti.
- Sumir uppfærðir textar eru birtir af stjórnvöldum en eru beinlínis óopinberir: aðeins
  opinbera birtingarritið er gilt.
- Nokkrar heimildir eru alls ekki vefsíður stjórnvalda (til dæmis LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes bætir tilkynningunni „Óopinber heimild“ við hvert svar sem kemur frá einni af þessum. Áður en
þú vitnar í eitthvað, athugaðu opinberu birtinguna. Umfangstaflan í
[README](README.md#umfang) og `list_jurisdictions` nefna heimildina fyrir hverja lögsögu.

## Hvaða lögsögur nær það til, og hversu vel?

125 millistykki: 108 aðildarríki SÞ, Hong Kong, Kosovo, Palestína, Taívan, DIFC Courts, ríkisdómstólar Bandaríkjanna og
11 alþjóðlegir dómstólar og stofnanir (svo sem Mannréttindadómstóll Evrópu, ESB,
Alþjóðadómstóllinn (ICJ) og WTO).

Umfangið er mjög mismunandi. Samkvæmt strangri reglu (fordæmi æðsta almenna dómstólsins, eða
stjórnarskráin og helstu lög, sem náð er til að fullu) teljast 72 af 125 falla undir.
[COVERAGE.md](../../COVERAGE.md) tilgreinir fyrir hverja lögsögu hvað Fontes nær til, hvað ekki,
og hvers vegna.

## Þarf ég API-lykil?

Fyrir nánast allar lögsögur, nei. Sumar heimildir þurfa ókeypis lykil: sjá [KEYS.md](KEYS.md).

- **Frakkland:** já. Frakkland er óvirkt þar til þú stillir `WLM_FR_PISTE_CLIENT_ID` og
  `WLM_FR_PISTE_CLIENT_SECRET`. Þetta fæst með ókeypis PISTE-aðgangi (piste.gouv.fr) með
  forriti sem er áskrifandi að Judilibre og Légifrance.
- **Bandaríkin:** valkvætt. Leit í dómaframkvæmd virkar án lykils, en sameiginlegi kynningarlykillinn
  leyfir aðeins um 10 leitir á dag á hverja IP-tölu. Ókeypis api.data.gov-lykill í
  `WLM_US_GOVINFO_KEY` hækkar það.
- **Ríkisdómstólar Bandaríkjanna:** já. Dómaframkvæmd ríkjanna (`us-states`) er óvirk þar til þú stillir `WLM_US_COURTLISTENER_KEY` á þitt eigið ókeypis CourtListener API-tákn. CourtListener er rekið af sjálfseignarstofnuninni Free Law Project; það er ekki opinber heimild og hvert svar segir til um það.

Stilltu þetta sem umhverfisbreytur fyrir Fontes-þjóninn í MCP-stillingum forritsins. Uppsetningarforritin spyrja um þær eftir uppsetningu, og ræsirinn **Add or change keys**
breytir þeim síðar.

Að auki segja nokkrar heimildir í skilmálum sínum að sjálfvirkur aðgangur krefjist leyfis
útgefandans. Þær eru merktar OFF og haldast óvirkar. Lykill breytir því ekki; aðeins
leyfi útgefandans gerir það (stilltu þá `WLM_PERMITTED=<codes>`).

## Hvaðan koma fyrri útgáfur og aukalöndin?

Frá [Lexifina](https://github.com/lexifina/global-law), sem geymir lög um það bil 200 landa sem git-sögu: hver breyting er færsla dagsett þeim degi sem hún tók gildi. Fontes les hana í gegnum ókeypis hýsta þjón Lexifina. Tvö verkfæri nota hana: `get_law_on_date` (ákvæði eins og það var í gildi á dagsetningu, líka í fortíðinni, ásamt lögunum sem breyttu því síðast) og `get_law_history` (sérhver lög sem breyttu ákvæði, eða breytingin orð fyrir orð milli tveggja dagsetninga). Fontes les einnig 91 land og landsvæði til viðbótar á þennan hátt, aðeins fyrir löggjöf (til dæmis Suður-Afríku, Kenía, Mexíkó, Nýja-Sjáland, Rússland, Suður-Kóreu, Belgíu, Litháen, Úkraínu, Malasíu, Taíland og Sádi-Arabíu). Þau eru aðskilin frá 125 lögsögunum með opinberri umfjöllun í rauntíma, og umfang eftir landi er mjög misjafnt (landsskrá Kenía geymir 9 lög). Lög Indlands koma einnig úr skrá Lexifina, því skilmálar India Code banna sjálfvirkan aðgang; dómar Hæstaréttar Indlands eru í rauntíma.

Lexifina er ekki opinber útgefandi og skrá hennar er ekki í rauntíma: Lexifina athugar hvert land öðru hverju, og eigin skýrsla hennar frá 2026-11-26 taldi 338 af 383 landsbundnum lagaheildum ekki athugaðar síðustu 7 daga. Hvert svar nefnir Lexifina sem heimild, tengir á síðu opinbera útgefandans og segir hversu langt skráin nær.

Lexifina telur að opinberir lagatextar séu ekki verndaðir af höfundarrétti, og því afritar hún í sumum löndum vefsíður, en skilmálum eða robots.txt þeirra fylgir Fontes sjálft. Fontes virðir enn robots.txt og skilmála fyrir allt sem það sækir sjálft; það sem kemur í gegnum Lexifina fylgir eigin mati Lexifina, skráð fyrir hvert land í geymslum hennar. Sumir útgefendur takmarka notkun (útgefandi Kenía: CC BY-NC). Leitarorð þín, tilvitnanir og dagsetningar fara til netþjóns Lexifina fyrir þetta. Stilltu `WLM_LEXIFINA=0` til að slökkva á því. Ókeypis þjónninn leyfir 60 köll á mínútu og 10.000 á dag á hverja IP-tölu; enginn lykill né aðgangur. Fontes er ekki tengt Lexifina.

## Hvað fer frá tölvunni minni?

Leitir þínar fara aðeins til heimildarinnar sem leitað er í (fyrir verkfæri og lönd Lexifina er það netþjónn Lexifina). Fontes heldur engan gagnagrunn og þarf engan
aðgang.

Auk heimildanna spyr Fontes PyPI einu sinni á dag hvort nýrri útgáfa sé til (slökkt
með `FONTES_NO_UPDATE_CHECK=1`). Notkunartölur eru óvirkar nema þú kveikir á þeim, og villuskýrsla
er aðeins send eftir að þú hefur séð hana og staðfest. Gervigreindarforritið þitt sér samtalið þitt samkvæmt
eigin skilmálum.

Allar upplýsingar: [PRIVACY.md](PRIVACY.md).

## Er þetta lögfræðiráðgjöf?

Nei. Fontes er tæki til heimildaleitar. Það finnur texta; það segir þér ekki hvað þeir þýða fyrir þitt
mál, og notkun þess stofnar ekki til sambands lögmanns og skjólstæðings við neinn. Gervigreindarforritið getur
mislesið texta, svo lestu allan dóminn eða ákvæðið áður en þú treystir á það. Til að fá ráðgjöf, spyrðu
lögmann sem hefur réttindi þar sem spurningin þín vaknar.

## Hver heldur því við? Mun það halda áfram að virka?

Einn maður: Yüce Karapazar. Það er ekkert fyrirtæki á bak við Fontes, enginn þjónustusamningur og ekkert
loforð um þjónustustig. Engin lögfræðiþjónusta er í boði.

Heimildirnar eru athugaðar einu sinni á dag og niðurstöðurnar birtar á
[stöðusíðunni](https://ykarapazar.github.io/fontes/status/?lang=is). Vefsíður dómstóla og stjórnvalda
breytast án fyrirvara, svo heimild getur bilað hvenær sem er. Engin trygging er fyrir því að nokkur heimild,
eða Fontes sjálft, haldi áfram að virka. Fontes er látið í té „eins og það er“, án ábyrgðar (kaflar 7
og 8 í [LICENSE](../../../LICENSE)).

## Texti er rangur eða úreltur, eða heimild virkar ekki. Hvernig tilkynni ég það?

- Stofnaðu issue með eyðublaðinu „Broken or wrong source“:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Segðu hvaða lögsögu, hvað þú
  spurðir um, hvað þú fékkst og hvaða opinbera síða sýnir rétta textann.
- Eða biddu gervigreindarforritið þitt að „tilkynna villu í Fontes“ (eða keyrðu `fontes report-bug`). Þú sérð skýrsluna áður en
  nokkuð er sent.
- Eða sendu tölvupóst á fontesmcp@proton.me.

Ekki setja upplýsingar um skjólstæðinga eða trúnaðarupplýsingar í skýrslu.

**Ef þú rekur eina af heimildunum** og eitthvað er rangt (skilmálar þínir, robots.txt, takmarkanir þínar
á beiðnum), sendu tölvupóst á fontesmcp@proton.me. Heimildin verður leiðrétt eða gerð óvirk.

## Hvernig er Fontes frábrugðið hýstum tækjum til lögfræðilegrar heimildaleitar?

- **Það keyrir á tölvunni þinni.** Það er enginn Fontes-þjónn og enginn aðgangur. Það þýðir líka að það
  virkar aðeins í forritum sem geta ræst staðbundinn MCP-þjón (Claude Desktop, Codex, Cursor, VS Code
  og svipuðum), ekki í hreinum vefforritum sem taka aðeins við hýstum tengingum (hosted connectors).
- **Það hefur engan gagnagrunn.** Hver leit fer í rauntíma á eigin vefsíðu eða API útgefandans, svo
  niðurstöðurnar eru jafn nýjar og heimildin, og leitargæðin eru heimildarinnar sjálfrar. Það er engin
  merkingarleit (semantic search) í sérvalinni skrá.
- **Það setur engin notkunarmörk.** Fontes hefur ekkert mánaðarlegt hámark á köll. Það dreifir beiðnum sínum til hverrar
  vefsíðu, og sumar heimildir takmarka hversu hratt eða hversu oft má senda þeim fyrirspurnir.
- **Það er opinn hugbúnaður.** Þú getur lesið hvert millistykki og séð nákvæmlega hvaðan hver texti kemur.
- **Enginn söluaðili stendur að baki því.** Enginn samningur, engin þjónustuborð og ekkert loforð um uppitíma (sjá „Hver
  heldur því við?“).

## Með hvaða forritum og kerfum virkar það?

Hvaða MCP-forriti sem getur keyrt staðbundinn þjón (stdio), til dæmis Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio og Cline. Fontes
keyrir á macOS, Windows og Linux, alls staðar þar sem uv keyrir (Python 3.13+). Á Mac eða Windows-tölvu setur uppsetningarforrit með einum smelli upp
Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio og Cline í
einu. Skref fyrir hvert forrit: [INSTALL.md](INSTALL.md).

## Get ég lagt til kóða?

Ekki eins og er. Issues, tilkynningar um heimildir og óskir um lögsögur eru vel þegnar. Sjá
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
