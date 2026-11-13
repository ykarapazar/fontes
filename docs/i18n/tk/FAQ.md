> Bu terjime maşynyň kömegi bilen taýýarlandy. Iňlis dilindäki görnüşi esasy hasaplanýar.

# Fontes: soraglar we jogaplar

## Fontes näme?

Mugt, açyk çeşme kodly MCP serweri (Apache 2.0). Ol Model Context Protocol bilen işleýän
islendik programma (Claude, Codex, Cursor, VS Code, Gemini CLI we beýlekiler) 120-den gowrak
ýurisdiksiýada we halkara kazyýetlerinde (124 adapter) kazyýet çözgütlerini we kanunçylygy
kazyýet we döwlet saýtlarynda göni gözlemäge mümkinçilik berýär. Her netije öz çeşmesini
atlandyrýar we asyl nusga salgylanýar.

## Tekstler resmimi?

Köplenç hawa, ýöne hemişe däl.

- Çeşmeleriň köpüsini kazyýet, ministrlik ýa-da resmi býulleten dolandyrýar.
- Ähli üýtgetmeler girizilen käbir tekstleri hökümet çap edýär, ýöne olar aç-açan resmi däl:
  diňe resmi býulleten hakyky hasaplanýar.
- Birnäçe çeşme asla döwlet saýty däl (meselem, LexiVox, LawPhil, Maqam, Wikisource).

Fontes şolaryň birinden gelýän her jogaba “Unofficial source” duýduryşyny goşýar. Bir zatdan
sitata getirmezden öň resmi neşiri barlaň. [README](README.md#gerim) faýlyndaky gerim tablisasy
we `list_jurisdictions` her ýurisdiksiýa üçin çeşmäni atlandyrýar.

## Ol haýsy ýurisdiksiýalary we näderejede gowy öz içine alýar?

124 adapter: BMG-niň 108 agza döwleti, Gonkong, Kosowo, Palestina, Taýwan, DIFC Courts we
11 halkara kazyýeti we edarasy (meselem, Adam hukuklary boýunça Ýewropa kazyýeti, ÝB, Halkara
kazyýeti (ICJ) we BSG).

Gerim ep-esli tapawutlanýar. Berk düzgün boýunça (iň ýokary umumy kazyýetiň presedentleri
ýa-da konstitusiýa we esasy kanunlar doly ýetilýän bolsa) 124-den 72-si öz içine alnan
hasaplanýar. [COVERAGE.md](../../COVERAGE.md) her ýurisdiksiýa üçin Fontes-iň nämä ýetýändigini,
nämä ýetmeýändigini we näme üçindigini görkezýär.

## Maňa API açary gerekmi?

Ýurisdiksiýalaryň hemmesi diýen ýaly üçin gerek däl. Käbir çeşmelere mugt açar gerek:
[KEYS.md](KEYS.md) serediň.

- **Fransiýa:** hawa. `WLM_FR_PISTE_CLIENT_ID` we `WLM_FR_PISTE_CLIENT_SECRET` goýýançaňyz
  Fransiýa öçük. Olar Judilibre we Légifrance hyzmatlaryna ýazylan programmasy bolan mugt
  PISTE hasabyndan (piste.gouv.fr) alynýar.
- **Amerikanyň Birleşen Ştatlary:** islege bagly. Kazyýet tejribesi boýunça gözleg açarsyz
  işleýär, ýöne umumy demo açar bir IP salgy üçin günde takmynan 10 gözlege rugsat berýär.
  `WLM_US_GOVINFO_KEY` içindäki mugt api.data.gov açary bu çägi ýokarlandyrýar.

Bulary programmaňyzyň MCP sazlamalarynda Fontes serweri üçin gurşaw üýtgeýänleri hökmünde
goýuň. Gurnaýjy çykandan soň, ol gurnalandan soň olary sorar, onuň **Add or change keys**
işlediji faýly bolsa olary soňra üýtgeder.

Mundan aýratynlykda, birnäçe çeşme öz şertlerinde awtomatik giriş üçin neşir edijiniň
rugsadynyň gerekdigini aýdýar. Olar OFF diýlip bellenen we öçük galýar. Açar muny
üýtgetmeýär; diňe neşir edijiniň rugsady üýtgedýär (şonda `WLM_PERMITTED=<codes>` goýuň).

## Kompýuterimden näme çykýar?

Gözlegleriňiz diňe gözlenýän çeşmä gidýär. Fontes maglumat bazasyny saklamaýar we hasap
ýazgysyny talap etmeýär.

Çeşmelerden başga, Fontes günde bir gezek PyPI-dan täze wersiýanyň bardygyny soraýar (ony
`FONTES_NO_UPDATE_CHECK=1` bilen öçüriň). Ulanyş sanlary siz açmasaňyz öçük, ýalňyşlyk
hasabaty bolsa diňe siz ony görüp tassyklanyňyzdan soň iberilýär. AI programmaňyz
söhbetdeşligiňizi öz şertlerine laýyklykda görýär.

Doly jikme-jiklikler: [PRIVACY.md](PRIVACY.md).

## Bu hukuk maslahatymy?

Ýok. Fontes barlag guraly. Ol tekstleri tapýar; olaryň siziň işiňiz üçin nämäni aňladýandygyny
aýtmaýar we ony ulanmak hiç kim bilen aklawçy-müşderi gatnaşygyny döretmeýär. AI programmasy
teksti nädogry okap biler, şonuň üçin daýanmazdan öň kazyýet çözgüdini ýa-da maddany doly
okaň. Maslahat üçin soragyňyz ýüze çykan ýerde hünär derejesi bolan aklawça ýüz tutuň.

## Ony kim goldaýar? Ol işlemegini dowam etdirermi?

Bir adam: Yüce Karapazar. Fontes-iň aňyrsynda kompaniýa, goldaw şertnamasy we hyzmat
derejesi boýunça wada ýok. Hiç hili hukuk hyzmatlary hödürlenmeýär.

Çeşmeler günde bir gezek barlanýar we netijeler
[ýagdaý sahypasynda](https://ykarapazar.github.io/fontes/status/?lang=tk) çap edilýär. Kazyýet
we döwlet saýtlary duýduryşsyz üýtgeýär, şonuň üçin çeşme islendik wagt işlemän biler. Haýsydyr
bir çeşmäniň ýa-da Fontes-iň özüniň işlemegini dowam etdirjekdigine kepillik ýok. Fontes
“bolşy ýaly” (“as is”), kepilliksiz berilýär ([LICENSE](../../../LICENSE) faýlynyň 7-nji we
8-nji bölümleri).

## Tekst nädogry, köne ýa-da çeşme işlemeýär. Bu barada nädip habar bermeli?

- “Broken or wrong source” görnüşi bilen issue açyň:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Haýsy ýurisdiksiýadygyny, näme
  soranyňyzy, näme alanyňyzy we dogry teksti görkezýän resmi sahypany ýazyň.
- Ýa-da AI programmaňyzdan “Fontes ýalňyşlygy barada habar ber” diýip haýyş ediň (ýa-da
  `fontes report-bug` işlediň). Bir zat iberilmezden öň hasabaty görýärsiňiz.
- Ýa-da fontesmcp@proton.me salgysyna ýazyň.

Hasabata müşderi maglumatlaryny ýa-da gizlin faktlary goşmaň.

**Eger siz çeşmeleriň birini dolandyrýan bolsaňyz** we bir zat nädogry bolsa (ulanyş
şertleriňiz, robots.txt, haýyş çäkleriňiz), fontesmcp@proton.me salgysyna ýazyň. Çeşme
düzediler ýa-da öçüriler.

## Fontes hostingdäki hukuk barlag gurallaryndan nämesi bilen tapawutlanýar?

- **Ol siziň kompýuteriňizde işleýär.** Fontes serweri we hasap ýazgysy ýok. Bu, şeýle hem, onuň
  diňe ýerli MCP serweri işe girizip bilýän programmalarda (Claude Desktop, Codex, Cursor,
  VS Code we şuňa meňzeşler) işleýändigini, diňe hostingdäki birikdirijileri kabul edýän diňe
  web programmalarynda işlemeýändigini aňladýar.
- **Onuň maglumat bazasy ýok.** Her gözleg göni neşir edijiniň öz saýtyna ýa-da API-sine
  gidýär, şonuň üçin netijeler çeşme näçe täze bolsa, şonça täze, gözlegiň hili bolsa çeşmäniň
  öz hili. Saýlanyp düzülen indeks boýunça semantik gözleg ýok.
- **Ol ulanyş çägini goýmaýar.** Fontes-de aýlyk çagyryş çägi ýok. Ol her saýta haýyşlaryny
  aralyk bilen iberýär, käbir çeşmeler bolsa olara näçe çalt ýa-da näçe ýygy haýyş iberip
  bolýandygyny çäklendirýär.
- **Ol açyk çeşme kodly.** Her adaptery okap, her tekstiň takyk nireden gelýändigini görüp
  bilersiňiz.
- **Onuň aňyrsynda üpjün ediji ýok.** Şertnama, goldaw gullugy ýa-da işleýiş wagty boýunça
  wada ýok (“Ony kim goldaýar?” serediň).

## Ol haýsy programmalar we ulgamlar bilen işleýär?

Ýerli (stdio) serweri işledip bilýän islendik MCP programmasy, meselem, Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio we
Cline. Fontes macOS, Windows we Linux-da, uv işleýän islendik ýerde (Python 3.13+) işleýär.
Mac we Windows üçin bir basyşda gurnaýjy ýakynda çykar. Ol Claude Desktop, Codex,
Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio we Cline programmalaryny
birbada sazlaýar. Her programma üçin ädimler: [INSTALL.md](INSTALL.md).

## Kod bilen goşant goşup bilerinmi?

Häzirlikçe ýok. Issue-lar, çeşmeler barada habarlar we ýurisdiksiýa boýunça haýyşlar hoş
kabul edilýär. [CONTRIBUTING.md](../../../CONTRIBUTING.md) serediň.
