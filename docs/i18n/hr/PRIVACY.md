> Ovo je strojno potpomognut prijevod. Mjerodavna je engleska verzija.

# Obavijest o privatnosti za Fontes

Fontes radi na vašem računalu. Vaša pretraživanja i dokumenti koje otvarate ostaju između vašeg
računala, izvora koje pretražujete (službenih, a uz njih CourtListener i Lexifina tamo gdje ih upotrebljavate, vidi niže) i AI aplikacije koju upotrebljavate (prema vlastitim
uvjetima te aplikacije). Sam Fontes razvojnim programerima projekta Fontes **prema zadanim
postavkama ne šalje ništa**.

## Što može napustiti vaše računalo i kada

**1. Provjera ažuriranja (zadano uključena).** Jednom dnevno Fontes pita PyPI, javni indeks
Python paketa, koja je inačica najnovija. Zahtjev ne sadrži ništa o vama ni o vašem radu; PyPI
vidi vašu IP adresu, kao i pri svakom preuzimanju. Da biste je isključili, postavite
`FONTES_NO_UPDATE_CHECK=1` (obavijest u aplikaciji) i `FONTES_NO_AUTO_UPDATE=1` (automatska
ažuriranja instalacijskog programa).

**2. Brojevi korištenja (isključeni ako ih sami ne uključite).** Ako pristanete (opt-in), Fontes
jednom dnevno šalje:

- inačicu programa Fontes i obitelj vašeg operacijskog sustava (macOS, Windows, Linux);
- po danu, koliko je puta svaki alat upotrijebljen za svaki kôd jurisdikcije, na primjer
  „2026-11-10, nl, search_caselaw, 12”.

To je cijela poruka. Nikada ne sadrži vaša pretraživanja, identifikatore dokumenata ili
predmeta, tekst dokumenata, vaše ime, korisnički račun ni bilo kakav identifikator vas ili vašeg
računala. Brojevi čekaju na vašem računalu (u mapi predmemorije programa Fontes, `stats.json`)
dok ne budu poslani; ako slanje ne uspije, čekaju sljedeći dan.

- **Pristanak (opt-in)**: odgovorite „y” kada vas instalacijski program pita ili postavite
  `FONTES_STATS=1` za Fontes poslužitelj.
- **Odustajanje (opt-out)**: ponovno pokrenite instalacijski program i na tom pitanju pritisnite
  Enter ili uklonite `FONTES_STATS`. Brisanjem datoteke `stats.json` odbacuje se sve što još nije
  poslano.

**3. Prijave pogrešaka (samo kada je sami pošaljete).** Kada je zatražite (`fontes report-bug`
ili zamolite svoju AI aplikaciju da prijavi pogrešku u programu Fontes), Fontes vam najprije
prikaže cijelu prijavu i šalje je samo ako potvrdite. Sadrži inačicu programa Fontes, obitelj
vašeg operacijskog sustava, kôd jurisdikcije, naziv alata i poruku o pogrešci posljednjeg
neuspjelog poziva alata (bez vaših pojmova za pretraživanje i identifikatora) te napomenu ako je
napišete. U napomenu ne upisujte podatke o klijentima. Kako bi to bilo moguće, Fontes čuva
posljednju pogrešku na vašem računalu (`last-error.json` u svojoj mapi predmemorije, svaki put
se zamjenjuje); ona se nikada ne šalje sama.

**4. Lexifina (zadano uključena).** `get_law_on_date`, `get_law_history`, 91 država i indijski akti čitaju se kroz Lexifinin zapis zakona, pa tako idu na Lexifinu, uz službene stranice ili umjesto njih. Vaši pojmovi za pretraživanje, citati i datumi idu na Lexifinin besplatni poslužitelj, `global-law.lexifina.com`, koji vodi Lexifina, a ne razvojni programeri projekta Fontes. Lexifina dokumentira da njezin poslužitelj bilježi koji je alat pozvan i koliko je trajao, nikada što je traženo; Fontes to ne može provjeriti, a primjenjuju se Lexifinini vlastiti uvjeti. Lexifina vidi vašu IP adresu, kao i svaki web-poslužitelj. Da biste to potpuno isključili, postavite `WLM_LEXIFINA=0`; ta dva alata i te države tada prestaju raditi i ništa se tamo ne šalje.

## Kamo podaci idu i koliko se dugo čuvaju

Brojevi korištenja i prijave pogrešaka šalju se na mali poslužitelj kojim upravlja razvojni
programer projekta Fontes (`relay.kinetra.fit`). On ne pohranjuje IP adrese: upotrebljavaju se
samo u memoriji, kratko, radi sprječavanja preopterećenja, a web-poslužitelj za njega ne vodi
zapisnik pristupa. Brojevi se zbrajaju u dnevne ukupne iznose; pojedinačne pošiljke se ne čuvaju.
Ukupni iznosi čuvaju se do 2 godine, prijave pogrešaka do 1 godine, a zatim se brišu. Ništa se ne
prodaje niti dijeli.

Ako taj poslužitelj nije dostupan, ništa se ne šalje: brojevi ostaju na vašem računalu, a
prijave pogrešaka vas umjesto toga upućuju na sustav za praćenje problema (issue tracker).

## Tko je odgovoran i na kojoj osnovi

Voditelj obrade za brojeve korištenja i prijave pogrešaka je Yüce Karapazar, razvojni programer
projekta Fontes. Kontakt: fontesmcp@proton.me.

Pravna osnova je vaša privola (članak 6. stavak 1. točka (a) UK GDPR-a i GDPR-a EU-a). Brojevi
korištenja šalju se samo ako pristanete (opt-in), a prijava pogreške tek nakon što je potvrdite.
Privolu možete povući u bilo kojem trenutku tako da odustanete na gore opisani način; to ne utječe
na ono što je poslano ranije.

## Kontakt

Pitanja ili zahtjevi: pišite na fontesmcp@proton.me ili otvorite prijavu problema (issue) na
<https://github.com/ykarapazar/fontes/issues>.
