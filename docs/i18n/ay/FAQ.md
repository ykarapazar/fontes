> Aka jaqukipäwix mäkina yanapt'ampiw luratawa. Inglés arun qillqatawa chiqapax (autoritativo).

# Fontes: jiskt'äwinaka, jaysäwinaka

## Kunas Fontes?

Mä inaki, código abierto MCP servidorawa (Apache 2.0). Model Context Protocol arsuri kuna
aplicacionarus (Claude, Codex, Cursor, VS Code, Gemini CLI, yaqhanakasa) taripañ utanakan
taripäwinakap, kamachinaksa taripañ uta, gobierno web sitionakan jichhpach thaqañapatak
yanapt'i, 120 jurisdiccionat juk'amp, markanak taypin taripañ utanakansa (124 adaptador).
Sapa jaysäwix jalsupan sutip siwa, originalaruw mayachata.

## Qillqatanakax oficialati?

Jilpachax jïsa, ukampis janiw sapakutikiti.

- Jilpach jalsunakax mä taripañ uta, mä ministerio jan ukax mä oficial gaceta ukaw
  irnaqayi.
- Yaqhip consolidado qillqatanakax mä gobiernow uñt'ayi, ukampis qhanpach jan oficialawa:
  oficial gacetakiw auténtico.
- Mä qhawqha jalsunakax janiw gobierno sitiokiti (amtañataki LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes ukax aka jalsunakat juti uka taqi jaysäwinakaruw "Jan oficial jalsu" yatiyäw uchi.
Kuns citkasa, oficial uñt'ayäw uñakipam. [README](README.md#purinipa) ukan purinipa tabla,
`list_jurisdictions` ukanakaw sapa jurisdiccionan jalsup siwa.

## Kawkïr jurisdiccionanakarus puri, kunjamas?

124 adaptador: ONU ukan 108 markanakapa, Hong Kong, Kosovo, Palestina, Taiwán, DIFC Courts,
ukat 11 markanak taypin taripañ utanaka, organonaka (amtañataki Tribunal Europeo de
Derechos Humanos, Unión Europea, CIJ, OMC).

Purinipax wali mayj mayjawa. Mä ch'ama kamachimpi (jach'a general taripañ utan
precedentenakapa, jan ukax constitución, nayrïr leyenakasa, taqpach purita), 124 taypit 72
ukakiw purita sasin jakhthapisi. [COVERAGE.md](COVERAGE.md) ukax sapa jurisdiccionataki
Fontes kunaru puri, kunar jan puri, kunatsa uk siqichi.

## Mä API llaveti wakisitu?

Niya taqi jurisdiccionanakatakix janiwa. Yaqhip jalsunakax inaki llaveniw wakisi:
[KEYS.md](KEYS.md) uñjam.

- **Francia:** jïsa. Francia ukax jiwt'atawa `WLM_FR_PISTE_CLIENT_ID`,
  `WLM_FR_PISTE_CLIENT_SECRET` uchañamkama. Ukanakax mä inaki PISTE cuenta (piste.gouv.fr)
  ukat jutapxi, Judilibre, Légifrance ukanakar suscribita mä aplicacionani.
- **Estados Unidos:** ajlliñataki. Jurisprudencia thaqañax jan llavempiw irnaqi, ukampis
  chikat apnaqat demo llavex sapa uru sapa IP direccionatak niya 10 thaqäwinakak jaytayi.
  `WLM_US_GOVINFO_KEY` ukan mä inaki api.data.gov llavex juk'amptayi.

Aka variables de entorno ukham aplicacionaman MCP configuracionapan Fontes servidoratak
uchañam. Instaladoranakax instalasaxa ukanak mayipxi, **Add or change keys**
qalltayirix qhipat mayjt'ayi.

Yaqha tuqitxa, mä qhawqha jalsunakax condicionanakapan automatizado mantañax uñt'ayirin
permisop munasi sapxi. OFF ukham uñacht'ayatawa, jiwt'atakiw qhiparapxi. Mä llavex janiw
uk mayjt'aykiti; uñt'ayirin permisopakiw mayjt'ayi (ukat `WLM_PERMITTED=<codes>` uchañam).

## Kunas computadorajat mistu?

Thaqäwinakamax thaqkta uka jalsurukiw sari. Fontes ukax janiw base de datos imkiti,
janirakiw cuenta munkiti.

Jalsunakat sipana, Fontes ukax sapa uru mä kuti PyPI ukar machaq versión utjiti sasaw
jiskt'i (`FONTES_NO_UPDATE_CHECK=1` ukamp jiwt'ayam). Apnaqat jakhunakax jiwt'atawa juma
naktaykäta ukhakama, mä pantjat yatiyäwisti uñjasin chiqapar sasma ukhakiw apayasi. IA
aplicacionamax aruskipäwim pachpa condicionanakaparjam uñji.

Taqpach yatiyäwi: [PRIVACY.md](PRIVACY.md).

## Akax asesoramiento jurídicoti?

Janiwa. Fontes ukax thaqañ irnaqañawa. Qillqatanak jikxati; janiw casomatak kuns sañ
munapxi uk siskiti, apnaqañasti janiw khitimpis abogado–cliente relación luratkiti. IA
aplicacionax mä qillqat pantjasaw liyt'aspa, ukatwa taqpach taripäwi jan ukax disposición
liyt'am janïr confiaskasa. Asesoramiento munasax jiskt'äwimax utjki uka chiqan
irnaqañatak yatiqat mä abogador jiskt'am.

## Khitis uñji? Irnaqaskakiniti?

Mä jaqi: Yüce Karapazar. Fontes qhipan janiw mä empresa utjkiti, janiw soporte contrato
ni nivel de servicio arsüwis utjkiti. Janiw servicios jurídicos churaskiti.

Jalsunakax sapa uru mä kuti uñakipata, uñakipäwinakasti
[jalsunakan kunjamäkipa laphina](https://ykarapazar.github.io/fontes/status/?lang=ay)
uñt'ayata. Taripañ uta, gobierno web sitionakax jan yatiyasaw mayjt'apxi, ukatwa mä jalsux
kuna pachas p'akjasispa. Janiw garantía utjkiti kuna jalsus, ni Fontes pachpas
irnaqaskakiniwa sasa. Fontes ukax "kunjamäki ukhamaw" (as is) churata, jan garantíani
([LICENSE](../../../LICENSE) ukan 7, 8 seccionanakapa).

## Mä qillqatax pantjatawa, nayrawa jan ukax mä jalsux p'akjatawa. Kunjams yatiyä?

- "Broken or wrong source" formulariompi mä issue jist'aram:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Kawkïr jurisdicción, kuns
  jiskt'ta, kuns katuqta, chiqap qillqat uñacht'ayir oficial laphi sim.
- Jan ukax IA aplicacionamar "report a Fontes bug" mayim (jan ukax `fontes report-bug`
  irnaqayam). Janïr kunas apayaskipanx yatiyäw uñjtaxa.
- Jan ukax fontesmcp@proton.me ukar qillqt'am.

Mä yatiyäwin clientenakam tuqit yatiyäwinaka jan ukax confidencial kunanaks jan uchamti.

**Maya aka jalsunak irnaqaykäta** ukat kunas jan walïchi (condicionanakama, robots.txt
ukama, rate limit ukanakama), fontesmcp@proton.me ukar qillqt'am. Jalsux askichatäniwa jan
ukax jiwt'ayatäniwa.

## Fontes kunjamas alojado derecho thaqañ irnaqañanakat mayja?

- **Computadoramanw irnaqi.** Janiw Fontes servidor ni cuenta utjkiti. Ukax mä local MCP
  servidor qalltayañ puedki uka aplicacionanakankak irnaqi sañ muniraki (Claude Desktop, Codex,
  Cursor, VS Code, ukham yaqhanakasa), janiw alojado conectoranakak katuqir web
  aplicacionanakankiti.
- **Janiw base de datos utjkiti.** Sapa thaqäwix uñt'ayirin pachpa web sitiopar jan ukax
  APIpar jichhpach sari, ukatwa jaysäwinakax jalsux jichhäki ukham jichhäpxi, thaqañan
  sumapasti jalsun pachpaw. Janiw mä ajllit índice patxan semántica thaqäwi utjkiti.
- **Janiw apnaqañ límite uchkiti.** Fontes ukax janiw phaxsin jawsañ límite utjkiti. Sapa
  web sitior mayiwinakap jayarst'ayi, yaqhip jalsunakasti qhawqa jank'akis jan ukax qhawqa
  kutis jiskt'asispa uk jark'apxi.
- **Código abiertowa.** Sapa adaptador liyt'asmawa, sapa qillqatax kawkits juti uk chiqapar
  uñjasma.
- **Janiw qhipan mä aljiri utjkiti.** Janiw contrato, soporte mesa ni irnaqaskakiniwa sasin
  arsüwi utjkiti ("Khitis uñji?" uñjam).

## Kawkïr aplicacionanakampi, sistemanakampis irnaqi?

Mä local (stdio) servidor irnaqayañ puedki uka kuna MCP aplicacionasa, amtañataki Claude
Desktop, Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM
Studio, Cline. Fontes ukax macOS, Windows, Linux ukanakan irnaqi, uv irnaqki uka kawkinsa
(Python 3.13+). Mac jan ukax Windows PC ukanxa, mä click instaladorax Claude Desktop, Codex,
Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio, Cline ukanak mä kutik
wakicht'i. Sapa aplicacionatak lurawinaka: [INSTALL.md](INSTALL.md).

## Código churirista?

Jichhax janiwa. Issue, jalsu yatiyäwinaka, jurisdicción mayiwinakas katuqatawa.
[CONTRIBUTING.md](../../../CONTRIBUTING.md) uñjam.
