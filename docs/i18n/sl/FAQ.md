> To je strojno podprt prevod. Merodajna je angleška različica.

# Fontes: vprašanja in odgovori

## Kaj je Fontes?

Brezplačen odprtokodni strežnik MCP (Apache 2.0). Vsaki aplikaciji, ki uporablja Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI in druge), omogoča, da v živo išče sodne
odločbe in predpise na spletnih straneh sodišč in državnih organov v več kot 120 jurisdikcijah
in mednarodnih sodiščih (124 adapterjev). Vsak rezultat navaja svoj vir in vsebuje povezavo do
izvirnika.

## Ali so besedila uradna?

Večinoma, vendar ne vedno.

- Večino virov upravlja sodišče, ministrstvo ali uradni list.
- Nekatera prečiščena besedila objavlja država, vendar so izrecno neuradna: verodostojen je samo
  uradni list.
- Nekaj virov sploh ni spletnih strani državnih organov (na primer LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes vsakemu odgovoru, ki izvira iz enega od teh virov, doda opombo »Unofficial source«.
Preden kar koli navajate, preverite uradno objavo. Tabela pokritosti v
[README](README.md#pokritost) in `list_jurisdictions` navajata vir za vsako jurisdikcijo.

## Katere jurisdikcije pokriva in kako dobro?

124 adapterjev: 108 držav članic OZN, Hongkong, Kosovo, Palestina, Tajvan, sodišča DIFC in 11
mednarodnih sodišč in organov (na primer Evropsko sodišče za človekove pravice, EU, Meddržavno
sodišče in WTO).

Pokritost se zelo razlikuje. Po strogem pravilu (precedenčne odločbe najvišjega splošnega
sodišča ali ustava in temeljni zakoni, dosegljivi v celoti) se 72 od 124 šteje za pokrite.
[COVERAGE.md](COVERAGE.md) za vsako jurisdikcijo navaja, kaj Fontes doseže, česa ne in zakaj.

## Ali potrebujem ključ API?

Za skoraj vsako jurisdikcijo ne. Nekateri viri potrebujejo brezplačen ključ: glejte
[KEYS.md](KEYS.md).

- **Francija:** da. Francija je izklopljena, dokler ne nastavite `WLM_FR_PISTE_CLIENT_ID` in
  `WLM_FR_PISTE_CLIENT_SECRET`. Dobite ju z brezplačnim računom PISTE (piste.gouv.fr) z
  aplikacijo, naročeno na Judilibre in Légifrance.
- **Združene države Amerike:** neobvezno. Iskanje sodne prakse deluje brez ključa, vendar
  skupni demo ključ dovoli le približno 10 iskanj na dan na naslov IP. Brezplačen ključ
  api.data.gov v `WLM_US_GOVINFO_KEY` to omejitev zviša.

Nastavite jih kot spremenljivke okolja za strežnik Fontes v nastavitvah MCP svoje aplikacije.
Ko bo namestitveni program izšel, jih bo zahteval po namestitvi, njegov zaganjalnik
**Add or change keys** pa jih pozneje spremeni.

Ločeno od tega nekaj virov v svojih pogojih navaja, da avtomatiziran dostop zahteva dovoljenje
izdajatelja. Označeni so z OFF in ostanejo izklopljeni. Ključ tega ne spremeni; to spremeni le
dovoljenje izdajatelja (takrat nastavite `WLM_PERMITTED=<codes>`).

## Kaj zapusti moj računalnik?

Vaša iskanja gredo samo viru, ki ga preiskujete. Fontes ne vodi zbirke podatkov in ne potrebuje
uporabniškega računa.

Poleg virov Fontes enkrat na dan vpraša PyPI, ali obstaja novejša različica (izklopite z
`FONTES_NO_UPDATE_CHECK=1`). Števci uporabe so izklopljeni, razen če jih vklopite, prijava
napake pa se pošlje šele, ko jo vidite in potrdite. Vaša aplikacija AI vidi vaš pogovor po
lastnih pogojih.

Vse podrobnosti: [PRIVACY.md](PRIVACY.md).

## Ali je to pravni nasvet?

Ne. Fontes je raziskovalno orodje. Najde besedila; ne pove vam, kaj pomenijo za vašo zadevo,
njegova uporaba pa z nikomer ne vzpostavi razmerja med odvetnikom in stranko. Aplikacija AI
lahko besedilo napačno prebere, zato preberite celotno odločbo ali določbo, preden se nanjo
zanesete. Za nasvet se obrnite na odvetnika, ki je usposobljen tam, kjer se vaše vprašanje
postavlja.

## Kdo ga vzdržuje? Bo še naprej deloval?

Ena oseba: Yüce Karapazar. Za orodjem Fontes ne stoji podjetje, ni pogodbe o podpori in ni
zaveze glede ravni storitev. Pravne storitve se ne zagotavljajo.

Viri se preverijo enkrat na dan, rezultati pa so objavljeni na
[strani stanja](https://ykarapazar.github.io/fontes/status/?lang=sl). Spletne strani sodišč in
državnih organov se spreminjajo brez obvestila, zato lahko vir kadar koli preneha delovati. Ni
zagotovila, da bo kateri koli vir ali sam Fontes še naprej deloval. Fontes se zagotavlja »tak,
kot je«, brez jamstva (razdelka 7 in 8 [LICENSE](../../../LICENSE)).

## Besedilo je napačno ali zastarelo ali pa vir ne deluje. Kako to prijavim?

- Odprite prijavo težave (issue) z obrazcem "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Navedite jurisdikcijo, kaj ste
  vprašali, kaj ste dobili in uradno stran, ki prikazuje pravilno besedilo.
- Ali pa svojo aplikacijo AI prosite, naj »prijavi napako v orodju Fontes« (ali zaženite
  `fontes report-bug`). Prijavo vidite, preden se kar koli pošlje.
- Ali pa pišite na fontesmcp@proton.me.

V prijavo ne vpisujte podatkov o strankah ali zaupnih dejstev.

**Če upravljate enega od virov** in je kaj narobe (vaši pogoji, vaš robots.txt, vaše omejitve
števila zahtev), pišite na fontesmcp@proton.me. Vir bo popravljen ali izklopljen.

## V čem se Fontes razlikuje od gostovanih orodij za pravno raziskovanje?

- **Deluje v vašem računalniku.** Ni strežnika Fontes in ni uporabniškega računa. To pomeni
  tudi, da deluje le v aplikacijah, ki lahko zaženejo lokalni strežnik MCP (Claude Desktop,
  Codex, Cursor, VS Code in podobne), ne pa v izključno spletnih aplikacijah, ki sprejemajo le
  gostovane povezovalnike.
- **Nima zbirke podatkov.** Vsako iskanje gre v živo na spletno stran ali API izdajatelja, zato
  so rezultati tako ažurni kot vir, kakovost iskanja pa je kakovost samega vira. Ni semantičnega
  iskanja po urejenem indeksu.
- **Ne določa omejitve uporabe.** Fontes nima mesečne omejitve klicev. Svoje zahteve do vsake
  spletne strani razporeja, nekateri viri pa omejujejo, kako hitro ali kako pogosto jih je
  mogoče poizvedovati.
- **Je odprtokoden.** Preberete lahko vsak adapter in natančno vidite, od kod izvira vsako
  besedilo.
- **Za njim ne stoji ponudnik.** Ni pogodbe, službe za podporo ali zaveze glede razpoložljivosti
  (glejte »Kdo ga vzdržuje?«).

## S katerimi aplikacijami in sistemi deluje?

Z vsako aplikacijo MCP, ki lahko zažene lokalni (stdio) strežnik, na primer Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio in
Cline. Fontes deluje v sistemih macOS, Windows in Linux, povsod, kjer deluje uv (Python 3.13+).
Še ni na PyPI; ko bo, bo večina aplikacij potrebovala en ukaz ali en vnos v konfiguraciji,
Claude Desktop pa sprejme datoteko `.mcpb`, ki jo dvakrat kliknete. Namestitveni program z enim
klikom za Mac in Windows je v pripravi. Naenkrat nastavi Claude Desktop, Codex, Claude Code,
Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio in Cline. Koraki za vsako aplikacijo:
[INSTALL.md](INSTALL.md).

## Ali lahko prispevam kodo?

Trenutno ne. Prijave težav, prijave virov in zahteve za jurisdikcije so dobrodošle. Glejte
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
