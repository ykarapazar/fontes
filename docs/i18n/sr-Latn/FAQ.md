> Ovo je mašinski potpomognut prevod. Merodavna je verzija na engleskom.

# Fontes: pitanja i odgovori

## Šta je Fontes?

Besplatan MCP server otvorenog koda (Apache 2.0). Omogućava svakoj aplikaciji koja podržava
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI i drugima) da pretražuje
sudske odluke i propise uživo na sajtovima sudova i državnih organa u 125 jurisdikcija i
međunarodnih sudova, uz još 91 državu preko Lexifinog zapisa (pogledajte dalje). Svaki rezultat
navodi svoj izvor i sadrži vezu ka originalu.

## Da li su tekstovi zvanični?

Uglavnom jesu, ali ne uvek.

- Većinom izvora upravlja sud, ministarstvo ili službeni glasnik.
- Neke prečišćene tekstove objavljuje država, ali su izričito nezvanični: autentičan je samo
  službeni glasnik.
- Nekoliko izvora uopšte nisu državni sajtovi (na primer LexiVox, LawPhil, Maqam, Wikisource).

Fontes dodaje obaveštenje "Unofficial source" svakom odgovoru koji potiče iz nekog od njih. Pre
nego što bilo šta citirate, proverite u zvaničnoj publikaciji. Tabela pokrivenosti u
[README](README.md#pokrivenost) i `list_jurisdictions` navode izvor za svaku jurisdikciju.

## Koje jurisdikcije obuhvata i koliko dobro?

125 adaptera: 108 država članica UN, Hongkong, Kosovo, Palestina, Tajvan, sudovi DIFC, sudovi američkih saveznih država i 11
međunarodnih sudova i tela (kao što su Evropski sud za ljudska prava, EU, Međunarodni sud
pravde i STO).

Pokrivenost se veoma razlikuje. Prema strogom pravilu (praksa najvišeg suda opšte nadležnosti,
ili ustav i osnovni zakoni, obuhvaćeni u potpunosti) 72 od 125 smatraju se pokrivenim.
[COVERAGE.md](../../COVERAGE.md) za svaku jurisdikciju navodi šta Fontes obuhvata, šta ne i
zašto.

## Da li mi je potreban API ključ?

Za skoro svaku jurisdikciju — ne. Nekim izvorima je potreban besplatan ključ: pogledajte
[KEYS.md](KEYS.md).

- **Francuska:** da. Francuska je isključena dok ne podesite `WLM_FR_PISTE_CLIENT_ID` i
  `WLM_FR_PISTE_CLIENT_SECRET`. Oni se dobijaju iz besplatnog PISTE naloga (piste.gouv.fr) sa
  aplikacijom pretplaćenom na Judilibre i Légifrance.
- **Sjedinjene Države:** opciono. Pretraga sudske prakse radi bez ključa, ali zajednički demo
  ključ dozvoljava samo oko 10 pretraga dnevno po IP adresi. Besplatan api.data.gov ključ u
  `WLM_US_GOVINFO_KEY` povećava tu granicu.
- **Sudovi američkih saveznih država:** da. Sudska praksa saveznih država (`us-states`) je isključena dok u `WLM_US_COURTLISTENER_KEY` ne podesite svoj besplatan CourtListener API token. CourtListener vodi neprofitna organizacija Free Law Project; nije zvaničan izvor, a svaki odgovor to navodi.

Podesite ih kao promenljive okruženja za Fontes server u MCP podešavanjima svoje aplikacije. Instalacioni
programi ih traže nakon instalacije, a njihov pokretač **Add or change keys** menja ih kasnije.

Odvojeno od toga, nekoliko izvora u svojim uslovima navodi da je za automatizovan pristup
potrebna dozvola izdavača. Oni su označeni sa OFF i ostaju isključeni. Ključ to ne menja; menja
to samo dozvola izdavača (tada podesite `WLM_PERMITTED=<codes>`).

## Odakle dolaze prošle verzije i dodatne države?

[Lexifina](https://github.com/lexifina/global-law) čuva zakone oko 200 država kao istoriju git-a: svaka promena je commit datiran danom kada je stupila na snagu. Fontes ih čita preko Lexifinog besplatnog hostovanog servera. Dva alata to koriste: `get_law_on_date` (odredba onakva kakva važi na neki datum, i u prošlosti, uz zakon koji ju je poslednji put menjao) i `get_law_history` (svaki zakon koji je menjao odredbu, ili promena reč po reč između dva datuma). Fontes na taj način čita i još 91 državu i teritoriju, samo za propise (na primer Južna Afrika, Kenija, Meksiko, Novi Zeland, Rusija, Južna Koreja, Belgija, Litvanija, Ukrajina, Malezija, Tajland i Saudijska Arabija). One su odvojene od 125 izvora sa aktivnom zvaničnom pokrivenošću, a pokrivenost po državi znatno varira (nacionalni zapis Kenije sadrži 9 zakona). Zakoni Indije takođe dolaze iz Lexifinog zapisa, jer uslovi sajta India Code zabranjuju automatizovan pristup; njene odluke Vrhovnog suda su uživo.

Lexifina nije zvanični izdavač, a njen zapis nije uživo: Lexifina s vremena na vreme proverava svaku državu, a njen sopstveni izveštaj od 2026-11-26 navodi da 338 od 383 nacionalna korpusa prava nije provereno u poslednjih 7 dana. Svaki njen odgovor navodi Lexifinu kao izvor, povezuje stranicu zvaničnog izdavača i kaže koliko zapis seže.

Lexifina smatra da zvanični pravni tekstovi nisu zaštićeni autorskim pravom, pa u nekim državama kopira sajtove čije uslove ili robots.txt Fontes poštuje. Fontes ih i dalje poštuje za sve što preuzima direktno; ono što stiže preko Lexifine prati Lexifinino sopstveno pravno mišljenje, zabeleženo za svaku državu u njenim repozitorijumima. Neki ograničavaju upotrebu (izdavač Kenije: CC BY-NC). Vaše reči za pretragu, citati i datumi za ove alate i države idu na Lexifinin server. Postavite `WLM_LEXIFINA=0` da ga isključite. Besplatan server dozvoljava 60 poziva u minuti i 10.000 dnevno po internet adresi; bez ključa i naloga. Fontes nije povezan sa Lexifinom.

## Šta napušta moj računar?

Vaše pretrage idu samo izvoru koji se pretražuje (za Lexifinine alate i države, to je Lexifinin server). Fontes ne vodi bazu podataka i nije mu potreban nalog.

Osim izvorima, Fontes se jednom dnevno obraća PyPI-ju da proveri da li postoji novija verzija
(isključuje se sa `FONTES_NO_UPDATE_CHECK=1`). Brojevi korišćenja su isključeni osim ako ih ne
uključite, a prijava greške šalje se tek kada je vidite i potvrdite. Vaša AI aplikacija vidi vaš
razgovor prema svojim uslovima.

Svi detalji: [PRIVACY.md](PRIVACY.md).

## Da li je ovo pravni savet?

Ne. Fontes je alat za istraživanje. On pronalazi tekstove; ne kaže vam šta oni znače za vaš
slučaj, i njegovo korišćenje ne stvara odnos advokat–klijent ni sa kim. AI aplikacija može
pogrešno da pročita tekst, pa pročitajte celu odluku ili odredbu pre nego što se na nju
oslonite. Za savet se obratite pravniku ovlašćenom tamo gde vaše pitanje nastaje.

## Ko ga održava? Da li će nastaviti da radi?

Jedna osoba: Yüce Karapazar. Iza programa Fontes ne stoji kompanija, nema ugovora o podršci
niti obećanja o nivou usluge. Pravne usluge se ne pružaju.

Izvori se proveravaju jednom dnevno, a rezultati se objavljuju na
[stranici statusa](https://ykarapazar.github.io/fontes/status/?lang=sr-Latn). Sajtovi sudova i
državnih organa menjaju se bez najave, pa izvor može prestati da radi u bilo kom trenutku. Nema
garancije da će bilo koji izvor, ili sam Fontes, nastaviti da radi. Fontes se pruža „takav
kakav jeste“, bez garancije (odeljci 7 i 8 [LICENSE](../../../LICENSE)).

## Tekst je pogrešan, zastareo ili izvor ne radi. Kako da to prijavim?

- Otvorite issue preko obrasca "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Navedite jurisdikciju, šta ste
  pitali, šta ste dobili i zvaničnu stranicu koja prikazuje ispravan tekst.
- Ili zamolite svoju AI aplikaciju da „prijavi grešku u programu Fontes“ (ili pokrenite
  `fontes report-bug`). Prijavu vidite pre nego što se bilo šta pošalje.
- Ili pišite na fontesmcp@proton.me.

Ne unosite u prijavu podatke o klijentima niti poverljive činjenice.

**Ako upravljate nekim od izvora** i nešto nije u redu (vaši uslovi, vaš robots.txt, vaša
ograničenja broja zahteva), pišite na fontesmcp@proton.me. Izvor će biti ispravljen ili isključen.

## Po čemu se Fontes razlikuje od hostovanih alata za pravna istraživanja?

- **Radi na vašem računaru.** Nema Fontes servera ni naloga. To takođe znači da radi samo u
  aplikacijama koje mogu da pokrenu lokalni MCP server (Claude Desktop, Codex, Cursor, VS Code
  i slične), a ne u isključivo veb aplikacijama koje prihvataju samo hostovane konektore.
- **Nema bazu podataka.** Svaka pretraga ide uživo na sopstveni sajt ili API izdavača, pa su
  rezultati ažurni koliko i izvor, a kvalitet pretrage je kvalitet samog izvora. Nema
  semantičke pretrage nad uređenim indeksom.
- **Ne postavlja ograničenje korišćenja.** Fontes nema mesečno ograničenje broja poziva. On
  raspoređuje svoje zahteve svakom sajtu, a neki izvori ograničavaju koliko brzo ili koliko
  često mogu da se pretražuju.
- **Otvorenog je koda.** Možete pročitati svaki adapter i tačno videti odakle potiče svaki
  tekst.
- **Iza njega ne stoji dobavljač.** Nema ugovora, službe podrške niti obećanja o neprekidnom radu
  (pogledajte „Ko ga održava?“).

## S kojim aplikacijama i sistemima radi?

Sa svakom MCP aplikacijom koja može da pokrene lokalni (stdio) server, na primer Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio i
Cline. Fontes radi na macOS-u, Windows-u i Linux-u, svuda gde radi uv (Python 3.13+). Na Mac-u ili na Windows PC-u instalacioni program na jedan klik podešava Claude Desktop,
Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio i Cline odjednom.
Koraci za svaku aplikaciju: [INSTALL.md](INSTALL.md).

## Mogu li da doprinesem kodom?

Trenutno ne. Issues, prijave o izvorima i zahtevi za jurisdikcije su dobrodošli. Pogledajte
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
