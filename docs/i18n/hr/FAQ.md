> Ovo je strojno potpomognut prijevod. Mjerodavna je engleska verzija.

# Fontes: pitanja i odgovori

## Što je Fontes?

Besplatan MCP poslužitelj otvorenog koda (Apache 2.0). Omogućuje svakoj aplikaciji koja
upotrebljava Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI i druge) da
pretražuje sudske odluke i propise uživo na mrežnim stranicama sudova i državnih tijela u 125 jurisdikcija i međunarodnih sudova, plus 91 država kroz Lexifinin zapis (vidi niže). Svaki rezultat navodi svoj izvor i sadrži
poveznicu na izvornik.

## Jesu li tekstovi službeni?

Uglavnom jesu, ali ne uvijek.

- Većinu izvora vodi sud, ministarstvo ili službeni list.
- Neke pročišćene tekstove objavljuje država, ali su izričito neslužbeni: vjerodostojan je samo
  službeni list.
- Nekoliko izvora uopće nisu stranice državnih tijela (na primjer LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes svakom odgovoru koji potječe iz nekog od tih izvora dodaje napomenu „Unofficial source”.
Prije nego što išta citirate, provjerite službenu objavu. Tablica obuhvata u
[README](README.md#obuhvat) i `list_jurisdictions` navode izvor za svaku jurisdikciju.

## Koje jurisdikcije obuhvaća i koliko dobro?

125 adaptera: 108 država članica UN-a, Hong Kong, Kosovo, Palestina, Tajvan, sudovi DIFC-a, sudovi saveznih država SAD-a i 11
međunarodnih sudova i tijela (kao što su Europski sud za ljudska prava, EU, Međunarodni sud i
WTO).

Obuhvat se znatno razlikuje. Prema strogom pravilu (presedani najvišeg suda opće
nadležnosti ili ustav i temeljni zakoni, dosegnuti u cijelosti), 72 od 125 smatraju se
obuhvaćenima. [COVERAGE.md](COVERAGE.md) za svaku jurisdikciju navodi što Fontes doseže, što ne
doseže i zašto.

## Trebam li API ključ?

Za gotovo svaku jurisdikciju ne trebate. Nekim izvorima potreban je besplatan ključ: pogledajte
[KEYS.md](KEYS.md).

- **Francuska:** da. Francuska je isključena dok ne postavite `WLM_FR_PISTE_CLIENT_ID` i
  `WLM_FR_PISTE_CLIENT_SECRET`. Dobivaju se iz besplatnog računa PISTE (piste.gouv.fr) s
  aplikacijom pretplaćenom na Judilibre i Légifrance.
- **Sjedinjene Američke Države:** neobavezno. Pretraživanje sudske prakse radi bez ključa, ali
  zajednički demo ključ dopušta samo oko 10 pretraživanja dnevno po IP adresi. Besplatan ključ
  api.data.gov u `WLM_US_GOVINFO_KEY` povećava to ograničenje.
- **Sudovi saveznih država SAD-a:** da. Sudska praksa saveznih država (`us-states`) isključena je dok ne postavite `WLM_US_COURTLISTENER_KEY` na vlastiti besplatni CourtListener API token. CourtListener vodi neprofitna organizacija Free Law Project; nije službeni izvor, a svaki odgovor to navodi.

Postavite ih kao varijable okruženja za Fontes poslužitelj u MCP postavkama svoje aplikacije.
Instalacijski programi traže ih nakon instalacije, a njihov pokretač
**Add or change keys** mijenja ih kasnije.

Neovisno o tome, nekoliko izvora u svojim uvjetima navodi da je za automatizirani pristup
potrebno dopuštenje izdavača. Oni su označeni s OFF i ostaju isključeni. Ključ to ne mijenja; to
mijenja samo dopuštenje izdavača (tada postavite `WLM_PERMITTED=<codes>`).

## Odakle dolaze prijašnje verzije i dodatne države?

Iz [Lexifine](https://github.com/lexifina/global-law), koja čuva zakone otprilike 200 država kao
povijest git-a: svaka izmjena je commit datiran danom kada je stupila na snagu. Fontes je čita preko
Lexifinina besplatnog hostiranog poslužitelja. Dva alata to koriste: `get_law_on_date` (odredba kakva je
bila na snazi na datum, i u prošlosti, s propisom koji ju je posljednji izmijenio) i `get_law_history`
(svaki zakon koji je izmijenio odredbu ili promjena riječ po riječ između dvaju datuma). Fontes na isti
način čita još 91 državu i teritorij, samo za propise (na primjer Južnu Afriku, Keniju, Meksiko, Novi
Zeland, Rusiju, Južnu Koreju, Belgiju, Litvu, Ukrajinu, Maleziju, Tajland i Saudijsku Arabiju). One su
odvojene od 125 adaptera s uživo službenim obuhvatom, a obuhvat po državi jako varira (nacionalni zapis
Kenije sadrži 9 zakona). Zakoni Indije također dolaze iz Lexifinina zapisa, jer uvjeti India Codea
zabranjuju automatizirani pristup; njezine presude Vrhovnog suda su uživo.

Lexifina nije službeni izdavač, a njezin zapis nije uživo: Lexifina s vremena na vrijeme provjerava svaku
državu, a njezino vlastito izvješće od 2026-11-26 brojilo je 338 od 383 nacionalna pravna izvora kao
neprovjerena u posljednjih 7 dana. Svaki odgovor navodi Lexifinu kao izvor, povezuje stranicu službenog
izdavača i kaže dokle seže zapis.

Lexifina smatra da službeni pravni tekstovi nisu zaštićeni autorskim pravom, pa u nekim državama kopira
stranice čiji uvjeti ili robots.txt Fontes sam poštuje. Fontes i dalje poštuje robots.txt i uvjete za sve
što sam dohvaća; ono što stiže preko Lexifine slijedi Lexifininu vlastitu procjenu, zabilježenu za svaku
državu u njezinim repozitorijima. Nekoliko ih ograničava uporabu (izdavač za Keniju: CC BY-NC). Za ove
alate i države vaši pojmovi za pretraživanje, citati i datumi idu na Lexifinin poslužitelj. Isključite to
s `WLM_LEXIFINA=0`. Nije potreban ključ ni račun; besplatni poslužitelj dopušta 60 poziva u minuti i 10.000
na dan po internetskoj adresi. Fontes nije povezan s Lexifinom.

## Što napušta moje računalo?

Vaša pretraživanja idu samo izvoru koji se pretražuje (za alate i države iz Lexifinina zapisa to je Lexifinin poslužitelj). Fontes ne vodi bazu podataka i ne treba
mu korisnički račun.

Osim izvora, Fontes jednom dnevno pita PyPI postoji li novija inačica (isključite to s
`FONTES_NO_UPDATE_CHECK=1`). Brojevi korištenja isključeni su ako ih sami ne uključite, a prijava
pogreške šalje se tek nakon što je vidite i potvrdite. Vaša AI aplikacija vidi vaš razgovor
prema vlastitim uvjetima.

Sve pojedinosti: [PRIVACY.md](PRIVACY.md).

## Je li ovo pravni savjet?

Nije. Fontes je alat za istraživanje. Pronalazi tekstove; ne govori vam što oni znače za vaš
slučaj, a njegovo korištenje ne stvara odnos odvjetnika i stranke ni s kim. AI aplikacija može
pogrešno pročitati tekst, stoga pročitajte cijelu odluku ili odredbu prije nego što se na nju
oslonite. Za savjet se obratite odvjetniku koji je kvalificiran ondje gdje se vaše pitanje
postavlja.

## Tko ga održava? Hoće li nastaviti raditi?

Jedna osoba: Yüce Karapazar. Iza projekta Fontes ne stoji tvrtka, nema ugovora o podršci ni
obećanja o razini usluge. Ne pružaju se pravne usluge.

Izvori se provjeravaju jednom dnevno, a rezultati se objavljuju na
[stranici stanja](https://ykarapazar.github.io/fontes/status/?lang=hr). Stranice sudova i
državnih tijela mijenjaju se bez najave, pa izvor može prestati raditi u bilo kojem trenutku.
Nema jamstva da će bilo koji izvor, ili sam Fontes, nastaviti raditi. Fontes se pruža „takav
kakav jest”, bez jamstva (odjeljci 7. i 8. [LICENSE](../../../LICENSE)).

## Tekst je pogrešan ili zastario, ili izvor ne radi. Kako to prijaviti?

- Otvorite prijavu problema (issue) pomoću obrasca "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Navedite o kojoj je jurisdikciji
  riječ, što ste pitali, što ste dobili i službenu stranicu na kojoj je ispravan tekst.
- Ili zamolite svoju AI aplikaciju da „prijavi pogrešku u programu Fontes” (ili pokrenite
  `fontes report-bug`). Prijavu vidite prije nego što se išta pošalje.
- Ili pišite na fontesmcp@proton.me.

U prijavu ne upisujte podatke o klijentima ni povjerljive činjenice.

**Ako vodite neki od izvora** i nešto nije u redu (vaši uvjeti, vaš robots.txt, vaša
ograničenja broja upita), pišite na fontesmcp@proton.me. Izvor će biti ispravljen ili isključen.

## Po čemu se Fontes razlikuje od hostiranih alata za pravno istraživanje?

- **Radi na vašem računalu.** Nema poslužitelja projekta Fontes ni korisničkog računa. To
  također znači da radi samo u aplikacijama koje mogu pokrenuti lokalni MCP poslužitelj (Claude
  Desktop, Codex, Cursor, VS Code i slične), a ne u isključivo web-aplikacijama koje prihvaćaju
  samo hostirane konektore.
- **Nema bazu podataka.** Svako pretraživanje ide uživo na vlastitu stranicu ili API izdavača,
  pa su rezultati ažurni koliko i izvor, a kvaliteta pretraživanja jest kvaliteta samog izvora.
  Nema semantičkog pretraživanja nad uređenim indeksom.
- **Ne postavlja ograničenje korištenja.** Fontes nema mjesečno ograničenje poziva. Raspoređuje
  svoje zahtjeve prema svakoj stranici, a neki izvori ograničavaju koliko brzo ili koliko često
  im se mogu slati upiti.
- **Otvorenog je koda.** Možete pročitati svaki adapter i točno vidjeti odakle potječe svaki
  tekst.
- **Iza njega ne stoji dobavljač.** Nema ugovora, službe za podršku ni obećanja o dostupnosti
  (pogledajte „Tko ga održava?”).

## S kojim aplikacijama i sustavima radi?

Sa svakom MCP aplikacijom koja može pokrenuti lokalni (stdio) poslužitelj, na primjer Claude
Desktop, Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio i Cline. Fontes radi na macOS-u, Windowsima i Linuxu, svugdje gdje radi uv
(Python 3.13+). Na Macu ili Windows računalu instalacijski program jednim klikom odjednom postavlja Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio i Cline.
Koraci za svaku aplikaciju: [INSTALL.md](INSTALL.md).

## Mogu li pridonijeti kodom?

Zasad ne. Prijave problema, prijave izvora i zahtjevi za jurisdikcije su dobrodošli. Pogledajte
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
