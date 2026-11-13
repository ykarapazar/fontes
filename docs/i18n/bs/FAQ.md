> Ovo je mašinski potpomognut prijevod. Mjerodavna je verzija na engleskom.

# Fontes: pitanja i odgovori

## Šta je Fontes?

Besplatan MCP server otvorenog koda (Apache 2.0). Omogućava svakoj aplikaciji koja koristi Model
Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI i druge) da pretražuje sudske odluke
i propise uživo na stranicama sudova i državnih organa u više od 120 jurisdikcija i međunarodnih
sudova (124 adaptera). Svaki rezultat navodi svoj izvor i sadrži link na original.

## Jesu li tekstovi zvanični?

Uglavnom jesu, ali ne uvijek.

- Većinu izvora vodi sud, ministarstvo ili službeni glasnik.
- Neke prečišćene tekstove objavljuje država, ali su izričito nezvanični: autentičan je samo
  službeni glasnik.
- Nekoliko izvora uopće nisu stranice državnih organa (na primjer LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes dodaje napomenu „Unofficial source“ svakom odgovoru koji potiče iz nekog od ovih izvora.
Prije nego što bilo šta citirate, provjerite zvaničnu objavu. Tabela pokrivenosti u
[README](README.md#pokrivenost) i `list_jurisdictions` navode izvor za svaku jurisdikciju.

## Koje jurisdikcije obuhvata i koliko dobro?

124 adaptera: 108 država članica UN-a, Hong Kong, Kosovo, Palestina, Tajvan, sudovi DIFC i 11
međunarodnih sudova i tijela (kao što su Evropski sud za ljudska prava, EU, Međunarodni sud
pravde i WTO).

Pokrivenost se znatno razlikuje. Prema strogom pravilu (presedani najvišeg općeg suda ili ustav i
primarni zakoni, dostupni u potpunosti), 72 od 124 smatraju se obuhvaćenim.
[COVERAGE.md](COVERAGE.md) za svaku jurisdikciju navodi šta Fontes doseže, šta ne doseže i zašto.

## Treba li mi API ključ?

Za gotovo svaku jurisdikciju ne treba. Nekim izvorima je potreban besplatan ključ: pogledajte
[KEYS.md](KEYS.md).

- **Francuska:** da. Francuska je isključena dok ne postavite `WLM_FR_PISTE_CLIENT_ID` i
  `WLM_FR_PISTE_CLIENT_SECRET`. Oni se dobijaju iz besplatnog PISTE računa (piste.gouv.fr) s
  aplikacijom pretplaćenom na Judilibre i Légifrance.
- **Sjedinjene Američke Države:** opcionalno. Pretraga sudske prakse radi bez ključa, ali zajednički
  demo ključ dopušta samo oko 10 pretraga dnevno po IP adresi. Besplatan api.data.gov ključ u
  `WLM_US_GOVINFO_KEY` povećava to ograničenje.

Postavite ih kao varijable okruženja za Fontes server u MCP postavkama svoje aplikacije. Kada
instalacijski program bude objavljen, tražit će ih nakon instalacije, a njegov pokretač
**Add or change keys** mijenja ih kasnije.

Odvojeno od toga, nekoliko izvora u svojim uslovima navodi da je za automatizovani pristup
potrebna dozvola izdavača. Oni su označeni sa OFF i ostaju isključeni. Ključ to ne mijenja; to
mijenja samo dozvola izdavača (tada postavite `WLM_PERMITTED=<codes>`).

## Šta napušta moj računar?

Vaše pretrage idu samo izvoru koji se pretražuje. Fontes ne vodi bazu podataka i ne treba mu
korisnički račun.

Pored izvora, Fontes jednom dnevno pita PyPI postoji li novija verzija (isključite to sa
`FONTES_NO_UPDATE_CHECK=1`). Brojevi korištenja su isključeni osim ako ih ne uključite, a prijava
greške šalje se tek nakon što je vidite i potvrdite. Vaša AI aplikacija vidi vaš razgovor prema
vlastitim uslovima.

Svi detalji: [PRIVACY.md](PRIVACY.md).

## Je li ovo pravni savjet?

Nije. Fontes je alat za istraživanje. Pronalazi tekstove; ne govori vam šta oni znače za vaš
slučaj, a njegovo korištenje ne stvara odnos advokata i klijenta ni sa kim. AI aplikacija može
pogrešno pročitati tekst, pa pročitajte cijelu odluku ili odredbu prije nego što se na nju
oslonite. Za savjet se obratite advokatu koji je kvalifikovan tamo gdje se vaše pitanje postavlja.

## Ko ga održava? Hoće li nastaviti raditi?

Jedna osoba: Yüce Karapazar. Iza projekta Fontes ne stoji kompanija, nema ugovora o podršci niti
obećanja o nivou usluge. Ne pružaju se pravne usluge.

Izvori se provjeravaju jednom dnevno, a rezultati se objavljuju na
[stranici stanja](https://ykarapazar.github.io/fontes/status/?lang=bs). Stranice sudova i državnih
organa mijenjaju se bez najave, pa se izvor može pokvariti u bilo kojem trenutku. Nema garancije da
će bilo koji izvor, ili sam Fontes, nastaviti raditi. Fontes se pruža „takav kakav jeste“, bez
garancije (odjeljci 7 i 8 [LICENSE](../../../LICENSE)).

## Tekst je pogrešan ili zastario, ili izvor ne radi. Kako to da prijavim?

- Otvorite prijavu problema (issue) pomoću obrasca "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Navedite koja jurisdikcija, šta ste
  pitali, šta ste dobili i zvaničnu stranicu na kojoj je ispravan tekst.
- Ili zamolite svoju AI aplikaciju da „prijavi grešku u alatu Fontes“ (ili pokrenite
  `fontes report-bug`). Prijavu vidite prije nego što se bilo šta pošalje.
- Ili pišite na fontesmcp@proton.me.

U prijavu ne unosite podatke o klijentima niti povjerljive činjenice.

**Ako vodite neki od izvora** i nešto nije u redu (vaši uslovi, vaš robots.txt, vaša ograničenja
upita), pišite na fontesmcp@proton.me. Izvor će biti ispravljen ili isključen.

## Po čemu se Fontes razlikuje od hostiranih alata za pravno istraživanje?

- **Radi na vašem računaru.** Nema servera projekta Fontes niti korisničkog računa. To također
  znači da radi samo u aplikacijama koje mogu pokrenuti lokalni MCP server (Claude Desktop, Codex,
  Cursor, VS Code i slične), a ne u isključivo web aplikacijama koje prihvataju samo hostirane
  konektore.
- **Nema bazu podataka.** Svaka pretraga ide uživo na vlastitu stranicu ili API izdavača, pa su
  rezultati ažurni koliko i izvor, a kvalitet pretrage je kvalitet samog izvora. Nema semantičke
  pretrage nad uređenim indeksom.
- **Ne postavlja ograničenje korištenja.** Fontes nema mjesečni limit poziva. Raspoređuje svoje
  zahtjeve prema svakoj stranici, a neki izvori ograničavaju koliko brzo ili koliko često im se
  mogu slati upiti.
- **Otvorenog je koda.** Možete pročitati svaki adapter i tačno vidjeti odakle potiče svaki tekst.
- **Iza njega ne stoji dobavljač.** Nema ugovora, službe za podršku niti obećanja o dostupnosti
  (pogledajte „Ko ga održava?“).

## S kojim aplikacijama i sistemima radi?

Sa svakom MCP aplikacijom koja može pokrenuti lokalni (stdio) server, na primjer Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio i Cline.
Fontes radi na macOS-u, Windowsu i Linuxu, svugdje gdje radi uv (Python 3.13+). Instalacijski program jednim klikom za
Mac i Windows je u pripremi. Postavlja Claude Desktop, Codex, Claude Code, Cursor, VS Code,
Windsurf, Gemini CLI, Zed, LM Studio i Cline odjednom. Koraci za svaku aplikaciju:
[INSTALL.md](INSTALL.md).

## Mogu li doprinijeti kodom?

Trenutno ne. Prijave problema, prijave izvora i zahtjevi za jurisdikcije su dobrodošli.
Pogledajte [CONTRIBUTING.md](../../../CONTRIBUTING.md).
