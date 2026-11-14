> Kayqa makinap yanapasqan t'ikrasqam. Inglés simipi qillqasqam chaninchasqa kaq (autoritativo).

# Fontes: tapukuykuna, kutichiykunapas

## Imataq Fontes?

Mana qullqiyuq, kichasqa pukyuyuq (open source) MCP servidormi (Apache 2.0). Model Context
Protocol nisqata rimaq mayqin aplicacióntapas (Claude, Codex, Cursor, VS Code, Gemini CLI,
hukkunatapas) taripana wasikunap taripayninkunata, kamachiykunatapas taripana wasikunap,
gobiernop web sitionkunapi kawsaqta maskachin, 120+ jurisdicciónkunapi, suyukuna pura taripana
wasikunapipas (124 adaptadorkuna). Sapa kutichiymi pukyunta sutinchan, originalmantaq t'inkin.

## Qillqakunaqa oficialchu?

Astawanqa ari, ichaqa manam sapa kutichu.

- Achka pukyukunataqa huk taripana wasi, huk ministerio utaq huk oficial gacetam purichin.
- Wakin consolidado qillqakunataqa huk gobiernom uyarichin, ichaqa sut'inta mana oficialmi:
  oficial gacetallam chiqap (auténtica).
- Wakin pisi pukyukunaqa manapunim gobiernop sitionkunachu (kayhina: LexiVox, LawPhil, Maqam,
  Wikisource).

Fontesqa kaykunamanta hamuq sapa kutichiymanmi "Unofficial source" willakuyta yapan. Manaraq
imatapas citachkaspa, oficial uyarichiyta qhaway. [README](README.md#chayasqan) nisqapi
chayasqan tabla, `list_jurisdictions` nisqapas sapa jurisdicciónpa pukyunta sutinchanku.

## Mayqin jurisdicciónkunatataq chayan, hayk'a allintataq?

124 adaptadorkuna: ONUp 108 suyu kamachiqninkuna, Hong Kong, Kosovo, Palestina, Taiwán, DIFC
taripana wasikuna, 11 suyukuna pura taripana wasikuna, entidadkunapas (kayhina: Derechos
Humanos Corte Europea, Unión Europea, ICJ, OMC).

Chayasqanqa ancham hukniray. Huk sinchi kamachiypi (aswan hatun general taripana wasip
precedentenkuna, utaq constitución, primario leykunapas, llapanta chayasqa), 124 kaqmanta 72
chayasqa hina yupakun. [COVERAGE.md](COVERAGE.md) nisqam sapa jurisdicciónpaq willan imata
Fontes chayan, imata mana chayanchu, imaraykutaq.

## API llavetachu necesitani?

Yaqa llapan jurisdicciónkunapaq, manam. Wakin pukyukunaqa mana qullqiyuq llavetam necesitan:
[KEYS.md](KEYS.md) qhaway.

- **Francia:** ari. Franciaqa wañusqam `WLM_FR_PISTE_CLIENT_ID`,
  `WLM_FR_PISTE_CLIENT_SECRET` nisqakunata churanaykikama. Kaykunaqa mana qullqiyuq PISTE
  cuentamantam hamun (piste.gouv.fr), Judilibre, Légifrance nisqakunaman suscribisqa
  aplicacionwan.
- **Estados Unidos:** akllanapaq. Jurisprudencia maskayqa mana llaveyuqpas llamk'anmi, ichaqa
  rakinakusqa demo llaveqa sapa IP direcciónpaq p'unchawpi 10 maskaykunallatam yaqa
  saqin. `WLM_US_GOVINFO_KEY` nisqapi mana qullqiyuq api.data.gov llavem chayta wichachin.

Kaykunataqa aplicacionniykip MCP configuracionninpi Fontes servidorpaq variables de entorno
hina churay. Instalador lluqsiptinña, instalasqa qhipa chaykunata mañasunki, **Add or change
keys** qallarichiqnintaq qhipaman tikran.

Hukmanta, wakin pisi pukyukunaqa condicionninkunapi ninku automatizado yaykuyqa
uyarichiqpa permisonta necesitasqanta. OFF nisqawan qillqasqam kanku, wañusqataq qhipakunku.
Huk llaveqa manam chayta tikranchu; uyarichiqpa permisonllam tikran (chaymanta
`WLM_PERMITTED=<codes>` nisqata churay).

## Imataq computadoraymanta lluqsin?

Maskasqaykikunaqa maskasqa pukyullamanmi rinku. Fontesqa manam base de datosta waqaychanchu,
manataq cuentata necesitanchu.

Pukyukunamanta hawa, Fontesqa p'unchawpi huk kutita PyPI nisqata aswan musuq versión kasqanta
tapun (`FONTES_NO_UPDATE_CHECK=1` nisqawan wañuchiy). Llamk'achiy yupaykunaqa wañusqam qam
hap'ichinaykikama, pantay willakuytaq rikusqayki, ari nisqayki qhipallam kachakun. IA
aplicacionniykiqa rimanakuyniykitam rikun kikin condicionninkunaman hina.

Llapan sut'inchaykuna: [PRIVACY.md](PRIVACY.md).

## Kayqa asesoramiento jurídicochu?

Manam. Fontesqa maskana llamk'anam. Qillqakunatam tarin; manam willasunkichu casoykipaq ima
niyta munasqankuta, llamk'achiytaq manam pipas abogado–cliente kaqninta ruwanchu. IA
aplicacionqa huk qillqata pantaspa ñawinchanmanmi, chayrayku manaraq confiakuchkaspa llapan
taripayta utaq disposiciónta ñawinchay. Asesoramientopaqqa, tapukuyniyki paqarimusqan
cheqaspi calificado abogadota tapuy.

## Pitaq waqaychan? Llamk'achkanqachu?

Huk runalla: Yüce Karapazar. Fontespa qhipanpiqa manam empresa kanchu, manam yanapakuy
contrato kanchu, manataq servicio nivel prometekuy kanchu. Manam servicios jurídicos
qukunchu.

Pukyukunaqa p'unchawpi huk kutitam qhawasqa kanku, kutichiykunataq
[imayna kasqan raphipi](https://ykarapazar.github.io/fontes/status/?lang=qu) uyarichisqa.
Taripana wasikunap, gobiernop web sitionkunaqa mana willaspam tikrakunku, chayrayku huk
pukyuqa mayqin pachapipas p'akikunmanmi. Manam garantía kanchu mayqin pukyupas, nitaq Fontes
kikinpas, llamk'achkananpaq. Fontesqa "kasqanman hina" (as is) qusqam, mana garantíayuq
([LICENSE](../../../LICENSE) nisqap 7, 8 kaq seccionninkuna).

## Huk qillqa pantasqam, mana musuqchasqachu, utaq huk pukyu p'akisqam. Imaynatataq willayman?

- "Broken or wrong source" formulariowan huk issueta kichay:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Niy mayqin jurisdicción, imata
  tapurqanki, imata chaskirqanki, allin qillqata rikuchiq oficial raphitapas.
- Utaq IA aplicacionniykita "Fontesmanta huk pantayta willay" nispa mañay (utaq
  `fontes report-bug` nisqata purichiy). Manaraq imapas kachakuchkaptinmi willakuyta rikunki.
- Utaq fontesmcp@proton.me nisqaman qillqay.

Ama huk willakuypi clientekunap datonkunata utaq pakasqa (confidencial) hechokunata churaychu.

**Pukyukunamanta hukninta purichinki chayqa** imapas mana allin kaptin (condicionniyki,
robots.txt nisqayki, rate limit nisqayki), fontesmcp@proton.me nisqaman qillqay. Pukyuqa
allichasqam kanqa utaq wañuchisqam.

## Imapitaq Fontes huk alojado (hosted) derecho maskana llamk'anakunamanta hukniray?

- **Computadoraykipim purin.** Manam Fontes servidor kanchu, manataq cuenta. Chaymi niyta
  munan local MCP servidorta qallarichiyta atiq aplicacionkunallapim llamk'an (Claude Desktop,
  Codex, Cursor, VS Code, chay hinakunapi), manam alojado conectorkunallata chaskiq web
  aplicacionkunallapichu.
- **Manam base de datosniyuqchu.** Sapa maskaymi uyarichiqpa kikin web sitionman utaq APInman
  kawsaqta rin, chayrayku kutichiykunaqa pukyu hina musuqmi, maskaypa allin kayninpas pukyup
  kikinmi. Manam akllasqa índice patapi semántico maskay kanchu.
- **Manam llamk'achiy limiteta churanchu.** Fontesqa manam killapi waqyay limiteyuqchu. Sapa
  web sitioman mañakuyninkunata t'aqan, wakin pukyukunataq hayk'a utqaylla utaq hayk'a kuti
  tapusqa kanankuta limitanku.
- **Open sourcem.** Sapa adaptadorta ñawinchayta atinki, sapa qillqa maymanta hamusqantapas
  sut'inta rikunki.
- **Manam vendedor qhipanpi kanchu.** Mana contrato, mana yanapakuy mesa, mana uptime
  prometekuy ("Pitaq waqaychan?" qhaway).

## Mayqin aplicacionkunawan, sistemakunawantaq llamk'an?

Local (stdio) servidorta purichiyta atiq mayqin MCP aplicacionpas, kayhina: Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio,
Cline. Fontesqa macOS, Windows, Linux nisqakunapim purin, uv purisqan maypipas (Python 3.13+).
Macpiqa huk clickllawan instaladormi Claude Desktop, Codex, Claude Code, Cursor, VS Code,
Windsurf, Gemini CLI, Zed, LM Studio, Cline nisqakunata huk kutillapi churan; Windowspaq
instaladormi hamuchkan. Sapa aplicacionpaq ruraykuna: [INSTALL.md](INSTALL.md).

## Codigota yapayta atiymanchu?

Kunanqa manam. Issuekuna, pukyukunamanta willakuykuna, jurisdicción mañakuykunapas allinmi
chaskisqa. [CONTRIBUTING.md](../../../CONTRIBUTING.md) qhaway.
