> Ko ñembohasa ojejapo máquina pytyvõ reheve. Pe inglés ñe'ẽme oĩva ha'e pe autoritativo.

# Fontes: porandu ha mbohovái

## Mba'épa Fontes?

Peteĩ servidor MCP reigua ha código abierto (Apache 2.0). Oheja oimeraẽ aplicación oñe'ẽva
Model Context Protocol-pe (Claude, Codex, Cursor, VS Code, Gemini CLI ha ambue) oheka
tribunalkuéra sentencia ha léikuéra ko'ag̃aite tribunal ha gobierno sitio web-pe, 120
jurisdicción ári ha tribunal internacional-pe (124 adaptador). Opaite mbohovái he'i
hypykue ha ojoaju pe original rehe.

## Umi jehaipy ha'épa oficial?

Hetavévape, ha katu ndaha'éi akóinte.

- Hetavéva ypykue omboguata peteĩ tribunal, peteĩ ministerio térã peteĩ diario oficial.
- Oĩ jehaipy consolidado peteĩ gobierno omosarambíva ha katu he'i hesakã porã ndaha'eiha
  oficial: diario oficial añoite ha'e auténtico.
- Mbovymi ypykue ndaha'éi mba'eveichagua gobierno sitio (techapyrãramo LexiVox, LawPhil,
  Maqam, Wikisource).

Fontes omoĩ peteĩ marandu "Ypykue ndaha'éiva oficial" opaite mbohovái oúvape peteĩva ko'ãvagui.
Remombe'u mboyve mba'eve, ehecha publicación oficial. Ñemohupyty tabla
[README](README.md#ñemohupyty)-pe ha `list_jurisdictions` he'i ypykue peteĩteĩ
jurisdicción-pe g̃uarã.

## Mba'e jurisdicción-pepa ohupyty, ha mba'eichaitépa?

124 adaptador: 108 tetã ONU miembro, Hong Kong, Kosovo, Palestina, Taiwán, DIFC Courts ha 11
tribunal ha órgano internacional (techapyrãramo Tribunal Europeo de Derechos Humanos, Unión
Europea, CIJ ha OMC).

Ñemohupyty iñambue heta. Peteĩ regla mbarete reheve (tribunal general yvatevéva
precedentekuéra, térã constitución ha léi primaria, ohupytýva opaite), 124-gui 72 oñemohupyty.
[COVERAGE.md](COVERAGE.md) he'i, peteĩteĩ jurisdicción-pe g̃uarã, mba'épa Fontes ohupyty,
mba'épa nahániri, ha mba'érepa.

## Aikotevẽpa peteĩ clave API?

Haimete opaite jurisdicción-pe g̃uarã, nahániri. Oĩ ypykue oikotevẽva peteĩ clave reigua:
ehecha [KEYS.md](KEYS.md).

- **Francia:** héẽ. Francia oĩ mbogue remoĩ peve `WLM_FR_PISTE_CLIENT_ID` ha
  `WLM_FR_PISTE_CLIENT_SECRET`. Ko'ãva ou peteĩ cuenta PISTE reiguágui (piste.gouv.fr) oguerekóva
  peteĩ aplicación oñesuscribíva Judilibre ha Légifrance-pe.
- **Estados Unidos:** reiporavo hag̃ua. Jurisprudencia jeheka oiko clave'ỹre, ha katu demo clave
  ojepurúva oñondive oheja 10 jeheka rupi añoite ára ha ára peteĩteĩ IP dirección-pe g̃uarã.
  Peteĩ clave api.data.gov reigua `WLM_US_GOVINFO_KEY`-pe omboheta.

Emoĩ ko'ãva variable de entorno ramo Fontes servidor-pe g̃uarã nde aplicación configuración
MCP-pe. Instalador osẽ rire, ojeruréta ko'ãva ñemohenda rire, ha iñepyrũha **Add or change keys**
omoambuéta upéi.

Ambue hendápe, mbovymi ypykue he'i hembiapoukapýpe acceso automático oikotevẽha ijára
permiso. Oñemarka OFF ha opyta mbogue. Peteĩ clave nomoambuéi upéva; ijára permiso añoite
omoambue (upéi emoĩ `WLM_PERMITTED=<codes>`).

## Mba'épa osẽ che computadora-gui?

Nde jeheka oho reheka hápe añoite. Fontes ndoñongatúi base de datos ha noikotevẽi cuenta.

Ypykue ndaha'éiva, Fontes oporandu PyPI-pe ára ha ára peteĩ jey oĩpa versión ipyahuvéva
(embogue `FONTES_NO_UPDATE_CHECK=1` reheve). Papapy jeporu rehegua oĩ mbogue nde remyandy
peve, ha jejavy marandu oñemondo rehecha ha remoneĩ rire añoite. Nde aplicación IA ohecha nde
ñemongeta hembiapoukapy ijeheguáicha.

Mba'emimi opaite: [PRIVACY.md](PRIVACY.md).

## Kóva ha'épa asesoramiento jurídico?

Nahániri. Fontes ha'e peteĩ tembiporu jeheka rehegua. Ojuhu jehaipy; nde'iri ndéve mba'épa
he'ise nde caso-pe g̃uarã, ha ojepuru ramo ndojapói avavéndie relación abogado–cliente.
Aplicación IA ikatu omoñe'ẽ vai peteĩ jehaipy, upévare emoñe'ẽ sentencia térã disposición
opaite rejerovia mboyve hese. Asesoramiento-pe g̃uarã, eporandu peteĩ abogado ikatúvape
omba'apo nde porandu oĩháme.

## Máva oñangareko hese? Oikótapa akóinte?

Peteĩ persona: Yüce Karapazar. Ndaipóri empresa Fontes rapykuéri, ndaipóri contrato soporte
rehegua ni promesa nivel de servicio rehegua. Noñeme'ẽi servicio jurídico.

Ypykuekuéra ojehecha ára ha ára peteĩ jey ha umi resultado osẽ
[ypykue rekotee kuatiarogue](https://ykarapazar.github.io/fontes/status/?lang=gn)-pe. Tribunal ha
gobierno sitio web oñemoambue marandu'ỹre, upévare peteĩ ypykue ikatu oñembyai oimeraẽ árape.
Ndaipóri garantía oimeraẽ ypykue, térã Fontes ijehegui, oikótaha akóinte. Fontes oñeme'ẽ
"oĩháicha" (as is), garantía'ỹre ([LICENSE](../../../LICENSE) sección 7 ha 8).

## Peteĩ jehaipy oĩ vai, ndaha'evéi ko'ag̃agua térã peteĩ ypykue oñembyai. Mba'éichapa amomarandu?

- Eipe'a peteĩ issue formulario "Broken or wrong source" reheve:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Ere mba'e jurisdicción, mba'épa
  reporandu, mba'épa rehupyty, ha kuatiarogue oficial ohechaukáva jehaipy hekopete.
- Térã ejerure nde aplicación IA-pe "report a Fontes bug" (térã emboguata `fontes report-bug`).
  Rehecha marandu oñemondo mboyve mba'eve.
- Térã emondo correo fontesmcp@proton.me-pe.

Ani emoĩ nde cliente rehegua marandu térã mba'e kañymby peteĩ marandúpe.

**Remboguatáramo peteĩ ko'ã ypykuégui** ha oĩ mba'e ndoikóiva (nde condicionkuéra, nde
robots.txt, nde límite de velocidad), emondo correo fontesmcp@proton.me-pe. Ypykue
oñemyatyrõta térã oñembogue.

## Mba'épe iñambue Fontes umi tembiporu jeheka jurídico alojado-gui?

- **Oiko nde computadora-pe.** Ndaipóri servidor Fontes ni cuenta. Upéva he'ise avei oiko
  aplicación ikatúva omoñepyrũ peteĩ servidor MCP local-pe añoite (Claude Desktop, Codex, Cursor,
  VS Code ha ambue ojoguáva), ndaha'éi aplicación web añoite oguerohorýva conector alojado
  añoite-pe.
- **Ndoguerekói base de datos.** Peteĩteĩ jeheka oho ko'ag̃aite ijára sitio web térã API
  ijeheguávape, upévare resultado ipyahu ypykue ipyahuháicha, ha jeheka iporã ypykue iporãháicha.
  Ndaipóri jeheka semántica peteĩ índice oñemopotĩva ári.
- **Nomoĩri límite jeporu rehegua.** Fontes ndoguerekói límite ñehenói jasyrupi. Omombyry
  ijerure peteĩteĩ sitio web-pe, ha oĩ ypykue omombytáva mba'eichaite pya'e térã mboy jey
  ikatu ojeporandu chupe.
- **Ha'e código abierto.** Ikatu remoñe'ẽ opaite adaptador ha rehecha moõguipa ou peteĩteĩ
  jehaipy.
- **Ndaipóri vendedor hapykuéri.** Ndaipóri contrato, mesa de soporte ni promesa oikótaha
  (ehecha "Máva oñangareko hese?").

## Mba'e aplicación ha sistema-ndivepa oiko?

Oimeraẽ aplicación MCP ikatúva omboguata peteĩ servidor local (stdio), techapyrãramo Claude
Desktop, Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM
Studio ha Cline. Fontes oiko macOS, Windows ha Linux-pe, oimeraẽ hendápe uv oikohápe (Python
3.13+). Ndaipóri gueteri PyPI-pe; oĩ rire, hetavéva aplicación oikotevẽ peteĩ comando térã
peteĩ entrada configuración-pe, ha Claude Desktop oguerohory peteĩ archivo `.mcpb` mokõi jey
ojejopýva. Peteĩ instalador peteĩ click-pe Mac ha Windows-pe g̃uarã oúma. Omohenda Claude
Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio ha Cline
peteĩ jeýpe. Tembiapo peteĩteĩ aplicación-pe g̃uarã: [INSTALL.md](INSTALL.md).

## Ikatúpa ame'ẽ código?

Ko'ág̃a nahániri. Issue, ypykue marandu ha jurisdicción jerure ojeguerohory. Ehecha
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
