> Lii ab tekki la bu masin dimbali. Mbind mu Àngale mi moo am sañ-sañ.

# Fontes: laaj ak tontu

## Lan mooy Fontes?

Ab serwëer MCP bu ñu joxe ci neen te seen kood ubbiku na (Apache 2.0). Dafay may bépp aplikasioŋ bu mën
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI ak yeneen) wut ci saa si àtte yi
àttekaay yi def ak yoon yi ci sit internet yu àttekaay yi ak yu Nguur gi, ci lu ëpp 120 juridiction ak
àttekaay yu adduna (124 adaptatëer). Bépp njeexital dafay tudd cosaanam te am lëkkalekaay bu jëm ci mbind
mu njëkk mi.

## Ndax mbind yi yu Nguur gi lañu?

Li ëpp ci yoon waaw, waaye du saa su ne.

- Li ëpp ci cosaan yi, ab àttekaay, ab ministeer walla ab Journal officiel moo leen yor.
- Am na ay mbind yu ñu yeesal (textes consolidés) yu Nguur gi siiwal, waaye wax nañu ci lu leer ne duñu yu
  Nguur gi: Journal officiel bi rekk moo dëggu.
- Am na ay cosaan yu dul situ Nguur gi sax (misaal LexiVox, LawPhil, Maqam, Wikisource).

Fontes dafay yokk yégle "Cosaan bu dul bu Nguur gi" ci bépp tontu bu jóge ci benn ci cosaan yooyu. Balaa
ngay jukkee ci dara, saytul mbind mu Nguur gi siiwal. Tablo li mu laal ci [README](README.md#li-mu-laal)
ak `list_jurisdictions` dañuy tudd cosaan bi ci juridiction bu nekk.

## Ban juridiction lay laal, te naka lay laale?

124 adaptatëer: 108 réew yu bokk ci Mbootaayu Xeet yi (ONU), Hong Kong, Kosovo, Palestine, Taiwan,
Àttekaay yu DIFC ak 11 àttekaay ak organisme yu adduna (niki Àttekaayu Tugal bu Sañ-sañi Doomu-aadama,
Uniyoŋ Tugal, CIJ ak OMC).

Li mu laal wute na lool. Ci benn sàrt bu tar (àtte yu àttekaay bu gën a kawe ci yoon wu ñépp, walla
ndeyu-àtte bi ak yoon yu mag yi, ñu mën a jot ci lépp), 72 ci 124 lañu lim ni yu mu laal.
[COVERAGE.md](../../COVERAGE.md) (ci Àngale) dafay wax, ci juridiction bu nekk, li Fontes mën a jot, li mu
mënul a jot, ak lu tax.

## Ndax soxla naa caabi API?

Ci lu ëpp ci juridiction yi, déedéet. Am na ay cosaan yu soxla caabi bu ñu joxe ci neen: xoolal
[KEYS.md](KEYS.md).

- **Faraas:** waaw. Faraas dafa fey ba nga def `WLM_FR_PISTE_CLIENT_ID` ak
  `WLM_FR_PISTE_CLIENT_SECRET`. Ñu ngi jóge ci benn kontu PISTE bu ñu joxe ci neen (piste.gouv.fr) ak ab
  aplikasioŋ bu bindu ci Judilibre ak Légifrance.
- **Etaa-Sini:** su la neexee. Wut ci àtte yi dafay dox te amul caabi, waaye caabi demo bi ñuy bokk dafay
  may rekk lu tollu ci 10 gëstu ci bés bi ci adrees IP bu nekk. Caabi api.data.gov bu ñu joxe ci neen ci
  `WLM_US_GOVINFO_KEY` dafay yokk dayo boobu.

Defal leen ni variables d'environnement ngir serwëer Fontes bi ci réglage MCP yu sa aplikasioŋ. Bu
programu samp bi génnee, dina la leen laaj ginnaaw samp bi, te **Yokk walla soppi caabi yi** dafay leen
soppi ginnaaw.

Lu dul loolu, am na ay cosaan yu wax ci seeni sàrt ne duggu ci masin soxla na sañ-sañu ki siiwal. Dañu
leen bind OFF te dañuy des fey. Caabi du ko soppi; sañ-sañu ki siiwal rekk moo koy soppi (ginnaaw loolu,
defal `WLM_PERMITTED=<codes>`).

## Lan mooy génn ci sama ordinatëer?

Say gëstu dañuy dem ci cosaan bi ngay wut rekk. Fontes du denc benn baasu done te soxlaawul kontu.

Lu dul cosaan yi, Fontes dafay laaj PyPI benn yoon ci bés bi ndax am na sumb bu gën a bees (fey ko ak
`FONTES_NO_UPDATE_CHECK=1`). Limu jëfandikoo yi dañu fey lu dul nga taal leen, te yégle njuumte du dem lu
dul ginnaaw bi nga ko gisee te dëggal ko. Sa aplikasioŋ AI dafay gis sa waxtaan ci seeni sàrt ci boppam.

Leeral yépp: [PRIVACY.md](PRIVACY.md).

## Ndax lii ndigal ci yoon la?

Déedéet. Fontes ab jumtukaayu gëstu la. Dafay jële ay mbind; du la wax lan lañuy tekki ci sa mbir, te
jëfandikoo ko du sos diggante layookat ak kiliyaan ak kenn. Aplikasioŋ AI bi mën na jàng ab mbind lu
baaxul, kon jàngal àtte bi walla xaaju yoon bi bépp balaa ngay ko wóolu. Ngir ndigal, laajal ab layookat bu
am sañ-sañ fa sa laaj di jóge.

## Kan moo koy saytu? Ndax dina wéy di dox?

Benn nit: Yüce Karapazar. Amul benn entreprise ci ginnaaw Fontes, amul kontra dimbali, te amul benn dige
ci dayob liggéey. Amul benn liggéeyu yoon bu ñuy joxe.

Dañuy saytu cosaan yi benn yoon ci bés bi, te dañuy siiwal njeexital yi ci
[xëtu mbiru cosaan yi](https://ykarapazar.github.io/fontes/status/?lang=wo). Sit internet yu àttekaay yi
ak yu Nguur gi dañuy soppiku te duñu yégle, kon ab cosaan mën na yàqu saa su ne. Amul garanti ne benn
cosaan, walla Fontes ci boppam, dina wéy di dox. Fontes ni mu mel lañu koy joxe ("as is"), te amul benn
garanti (xaaj 7 ak 8 yu [LICENSE](../../../LICENSE)).

## Ab mbind baaxul, yeesul, walla ab cosaan yàqu na. Naka laay yégle?

- Ubbil ab issue ak formulaire "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Waxal ban juridiction, lan nga laaj, lan nga
  am, ak xët wu Nguur gi wuy won mbind mu baax mi.
- Walla laajal sa aplikasioŋ AI mu "yégle njuumte ci Fontes" (walla doxal `fontes report-bug`). Dinga
  gis yégle bi balaa dara di dem.
- Walla bindal ci fontesmcp@proton.me.

Bul def ci yégle xibaaru kiliyaan walla mbir yu nëbbu.

**Su fekkee yaa yor benn ci cosaan yi** te am na lu baaxul (say sàrt, sa robots.txt, sa dayo laaj),
bindal ci fontesmcp@proton.me. Dinañu defar cosaan bi walla fey ko.

## Lan moo wuute Fontes ak jumtukaayu gëstu yoon yu ñuy dalal ci serwëer yu yeneen nit?

- **Ci sa ordinatëer lay dox.** Amul serwëer Fontes te amul kontu. Loolu dafay tekki itam ne dafay dox
  rekk ci aplikasioŋ yu mën a tàmbali ab serwëer MCP ci ordinatëer bi (Claude Desktop, Codex, Cursor,
  VS Code ak yu ni mel), du ci aplikasioŋ yu nekk ci web rekk te di nangu rekk ay connecteur yu nekk ci
  serwëer.
- **Amul baasu done.** Bépp gëstu dafay dem ci saa si ci sit internet walla API bu ki siiwal ci boppam,
  kon njeexital yi dañuy yees ni cosaan bi yeese, te baaxaayu gëstu bi mooy bu cosaan bi. Amul gëstu bu
  sémantik ci ab index bu ñu tànn.
- **Du teg benn dayo ci jëfandikoo.** Fontes amul dayo woote ci weer wi. Dafay xaajale laaj yi muy yónne
  sit bu nekk, te yenn cosaan dañuy tënk gaawaay walla ñaata yoon lañu leen mën a laaj.
- **Seen kood ubbiku na.** Mën nga jàng adaptatëer bu nekk te gis fu mbind mu nekk jóge.
- **Amul benn jaaykat ci ginnaaw.** Amul kontra, amul biro dimbali, amul dige ci ni muy dox (xoolal "Kan
  moo koy saytu?").

## Ak ban aplikasioŋ ak sistem lay dox?

Bépp aplikasioŋ MCP bu mën a doxal ab serwëer ci ordinatëer bi (stdio), misaal Claude Desktop, Claude
Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio ak Cline. Fontes dafay
dox ci macOS, Windows ak Linux, fépp fu uv di dox (Python 3.13+). Ci Mac, programu samp ci benn klig dafay samp
Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio ak Cline ci benn
yoon; programu samp bu Windows mu ngi ñëw. Tànk yi ci aplikasioŋ bu nekk: [INSTALL.md](INSTALL.md).

## Ndax mën naa yokk ab kood?

Léegi déet. Issue yi, yégle ci cosaan yi ak sàkku juridiction yu bees, ñu ngi leen di teral. Xoolal
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
