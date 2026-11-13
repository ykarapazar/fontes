> Iyi ni inyandiko yahinduwe hifashishijwe imashini. Inyandiko y'Icyongereza ni yo ifite agaciro.

# Fontes: ibibazo n'ibisubizo

## Fontes ni iki?

Ni seriveri MCP y'ubuntu ifite kode ifunguye (Apache 2.0). Ituma porogaramu iyo ari yo yose ivuga Model
Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI n'izindi) ishakisha ibyemezo by'inkiko
n'amategeko ako kanya ku mbuga z'inkiko n'iza Leta, mu mafasi y'ubutabera arenga 120 no mu nkiko
mpuzamahanga (adapter 124). Buri gisubizo kivuga inkomoko yacyo kandi gifite ihuza rijya ku nyandiko
y'umwimerere.

## Inyandiko ni iza Leta?

Akenshi yego, ariko si buri gihe.

- Inkomoko nyinshi zicungwa n'urukiko, minisiteri cyangwa igazeti ya Leta.
- Inyandiko zimwe zivuguruye zitangazwa na Leta, ariko zivuga ku mugaragaro ko atari iza Leta zemewe:
  igazeti ya Leta ni yo yonyine yemewe.
- Inkomoko zimwe si imbuga za Leta na gato (urugero LexiVox, LawPhil, Maqam, Wikisource).

Fontes yongera itangazo "Inkomoko itari iya Leta" kuri buri gisubizo kivuye kuri imwe muri izo nkomoko.
Mbere yo kuvuga (cite) ikintu icyo ari cyo cyose, genzura inyandiko yatangajwe na Leta. Imbonerahamwe
y'ibyo igeraho iri muri [README](README.md#ibyo-igeraho) na `list_jurisdictions` bivuga inkomoko ya buri
fasi y'ubutabera.

## Igera ku yahe mafasi y'ubutabera, kandi ku rugero rungana iki?

Adapter 124: ibihugu 108 binyamuryango bya Loni, Hong Kong, Kosovo, Palesitina, Taiwan, Inkiko za DIFC
n'inkiko n'inzego mpuzamahanga 11 (nk'Urukiko rw'u Burayi rw'Uburenganzira bwa Muntu, Umuryango w'u
Burayi, ICJ na WTO).

Ibyo igeraho biratandukanye cyane. Hakurikijwe igipimo gikomeye (imanza zibanziriza z'urukiko rukuru
rusanzwe, cyangwa Itegeko Nshinga n'amategeko y'ibanze, bigerwaho byuzuye), 72 muri 124 zibarwa ko
zigerwaho. [COVERAGE.md](../../COVERAGE.md) (mu Cyongereza) ivuga, kuri buri fasi y'ubutabera, ibyo Fontes
igeraho, ibyo itageraho, n'impamvu.

## Nkeneye urufunguzo rwa API?

Ku mafasi y'ubutabera hafi ya yose, oya. Inkomoko zimwe zikenera urufunguzo rw'ubuntu: reba
[KEYS.md](KEYS.md).

- **U Bufaransa:** yego. U Bufaransa burafunze kugeza ushyizeho `WLM_FR_PISTE_CLIENT_ID` na
  `WLM_FR_PISTE_CLIENT_SECRET`. Biva kuri konti ya PISTE y'ubuntu (piste.gouv.fr) na porogaramu
  yiyandikishije kuri Judilibre na Légifrance.
- **Leta Zunze Ubumwe za Amerika:** si itegeko. Gushakisha imanza bikora nta rufunguzo, ariko urufunguzo
  rwa demo rusangiwe rwemera gusa ishakisha rigera ku 10 ku munsi kuri buri aderesi IP. Urufunguzo
  rw'ubuntu rwa api.data.gov muri `WLM_US_GOVINFO_KEY` ruzamura uwo mubare ntarengwa.

Zishyireho nk'environment variables za seriveri ya Fontes mu igenamiterere rya MCP rya porogaramu yawe.
Porogaramu yo gushyiraho nisohoka, izazigusaba nyuma yo gushyiraho, kandi **Ongeraho cyangwa uhindure
imfunguzo** yayo izazihindura nyuma.

Uretse ibyo, inkomoko zimwe zivuga mu mabwiriza yazo ko kwinjira mu buryo bwikora bisaba uruhushya
rw'uyitangaza. Zanditseho OFF kandi zikomeza gufunga. Urufunguzo ntiruhindura ibyo; uruhushya
rw'uyitangaza ni rwo rwonyine rubihindura (hanyuma ushyireho `WLM_PERMITTED=<codes>`).

## Ni iki kiva kuri mudasobwa yanjye?

Ibyo ushakisha bijya gusa ku nkomoko irimo gushakishwamo. Fontes ntibika ububiko bw'amakuru kandi
ntikenera konti.

Uretse inkomoko, Fontes ibaza PyPI rimwe ku munsi niba hari verisiyo nshya (bihagarike ukoresheje
`FONTES_NO_UPDATE_CHECK=1`). Imibare y'ikoreshwa irafunze keretse uyifunguye, kandi raporo y'ikosa
yoherezwa gusa umaze kuyibona no kuyemeza. Porogaramu yawe ya AI ibona ikiganiro cyawe hakurikijwe
amabwiriza yayo bwite.

Ibisobanuro byose: [PRIVACY.md](PRIVACY.md).

## Iyi ni inama mu by'amategeko?

Oya. Fontes ni igikoresho cy'ubushakashatsi. Izana inyandiko; ntikubwira icyo zisobanuye ku kibazo cyawe,
kandi kuyikoresha ntibitera umubano w'umunyamategeko n'umukiliya n'uwo ari we wese. Porogaramu ya AI
ishobora gusoma inyandiko nabi, bityo soma icyemezo cyose cyangwa ingingo yose mbere yo kuyishingiraho.
Ku nama, baza umunyamategeko wemewe aho ikibazo cyawe kiri.

## Ni nde uyicunga? Izakomeza gukora?

Umuntu umwe: Yüce Karapazar. Nta sosiyete iri inyuma ya Fontes, nta masezerano y'ubufasha, kandi nta
masezerano y'urwego rwa serivisi. Nta serivisi z'amategeko zitangwa.

Inkomoko zigenzurwa rimwe ku munsi, kandi ibisubizo bitangazwa ku
[rupapuro rw'uko inkomoko zihagaze](https://ykarapazar.github.io/fontes/status/?lang=rw). Imbuga z'inkiko
n'iza Leta zihinduka nta nteguza, bityo inkomoko ishobora gupfa igihe icyo ari cyo cyose. Nta garanti ko
inkomoko iyo ari yo yose, cyangwa Fontes ubwayo, izakomeza gukora. Fontes itangwa "uko iri" ("as is"),
nta garanti (ibice bya 7 n'8 bya [LICENSE](../../../LICENSE)).

## Inyandiko ni mbi, ntigezweho, cyangwa inkomoko yarapfuye. Nabimenyekanisha nte?

- Fungura issue ukoresheje ifishi "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Vuga ifasi y'ubutabera, icyo wabajije, icyo
  wabonye, n'urupapuro rwa Leta rugaragaza inyandiko nyayo.
- Cyangwa usabe porogaramu yawe ya AI "gutangaza ikosa rya Fontes" (cyangwa ukore `fontes report-bug`).
  Ubona raporo mbere y'uko hagira ikintu cyoherezwa.
- Cyangwa wandikire fontesmcp@proton.me.

Ntugashyire amakuru y'abakiliya cyangwa ibintu by'ibanga muri raporo.

**Niba ari wowe ucunga imwe mu nkomoko** kandi hari ikitari cyo (amabwiriza yawe, robots.txt yawe,
umubare ntarengwa w'ibisabwa), andikira fontesmcp@proton.me. Inkomoko izakosorwa cyangwa ifungwe.

## Fontes itandukaniye he n'ibikoresho by'ubushakashatsi mu mategeko biri kuri seriveri z'abandi?

- **Ikorera kuri mudasobwa yawe.** Nta seriveri ya Fontes kandi nta konti. Ibyo binasobanura ko ikora
  gusa muri porogaramu zishobora gutangiza seriveri MCP iri kuri mudasobwa (Claude Desktop, Codex, Cursor,
  VS Code n'izisa na zo), si muri porogaramu ziri kuri internet gusa zemera connectors ziri kuri seriveri
  gusa.
- **Nta bubiko bw'amakuru igira.** Buri shakisha rijya ako kanya ku rubuga cyangwa API by'utangaza ubwe,
  bityo ibisubizo bigezweho nk'uko inkomoko igezweho, kandi ubwiza bw'ishakisha ni ubw'inkomoko. Nta
  shakisha rishingiye ku busobanuro (semantic search) mu ishakiro ryateguwe.
- **Ntishyiraho umubare ntarengwa w'ikoreshwa.** Fontes nta mubare ntarengwa w'ihamagara ku kwezi igira.
  Itandukanya ubusabe yohereza kuri buri rubuga, kandi inkomoko zimwe zigabanya umuvuduko cyangwa inshuro
  zishobora kubazwa.
- **Ifite kode ifunguye.** Ushobora gusoma buri adapter ukabona neza aho buri nyandiko ituruka.
- **Nta mucuruzi uri inyuma yayo.** Nta masezerano, nta biro by'ubufasha, nta sezerano ry'uko izahora
  iboneka (reba "Ni nde uyicunga?").

## Ikora na porogaramu na sisitemu izihe?

Porogaramu iyo ari yo yose ya MCP ishobora gukoresha seriveri iri kuri mudasobwa (stdio), urugero Claude
Desktop, Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio na
Cline. Fontes ikora kuri macOS, Windows na Linux, aho uv ikora hose (Python 3.13+). Porogaramu yo gushyiraho
ukanze rimwe ya Mac na Windows iri hafi. Ishyiraho Claude Desktop, Codex, Claude Code, Cursor, VS Code,
Windsurf, Gemini CLI, Zed, LM Studio na Cline icyarimwe. Intambwe kuri buri porogaramu:
[INSTALL.md](INSTALL.md).

## Nshobora gutanga umusanzu wa kode?

Ubu oya. Issues, raporo ku nkomoko n'ibyifuzo by'amafasi y'ubutabera mashya birakirwa neza. Reba
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
