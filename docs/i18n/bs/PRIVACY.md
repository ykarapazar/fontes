> Ovo je mašinski potpomognut prijevod. Mjerodavna je verzija na engleskom.

# Obavještenje o privatnosti za Fontes

Fontes radi na vašem računaru. Vaše pretrage i dokumenti koje otvarate ostaju između vašeg
računara, zvaničnih izvora koje pretražujete i AI aplikacije koju koristite (prema vlastitim
uslovima te aplikacije). Sam Fontes programerima projekta Fontes **zadano ne šalje ništa**.

## Šta može napustiti vaš računar i kada

**1. Provjera ažuriranja (zadano uključena).** Jednom dnevno Fontes pita PyPI, javni indeks
Python paketa, koja je verzija najnovija. Zahtjev ne nosi ništa o vama ili vašem radu; PyPI vidi
vašu IP adresu, kao i pri svakom preuzimanju. Da je isključite, postavite
`FONTES_NO_UPDATE_CHECK=1` (obavještenje u aplikaciji) i `FONTES_NO_AUTO_UPDATE=1` (automatska
ažuriranja instalacijskog programa).

**2. Brojevi korištenja (isključeni osim ako ih ne uključite).** Ako pristanete (opt-in), Fontes
jednom dnevno šalje:

- verziju programa Fontes i porodicu vašeg operativnog sistema (macOS, Windows, Linux);
- po danu, koliko je puta svaki alat korišten za svaki kod jurisdikcije, na primjer
  „2026-11-10, nl, search_caselaw, 12“.

To je cijela poruka. Nikada ne sadrži vaše pretrage, identifikatore dokumenata ili predmeta,
tekst dokumenata, vaše ime, korisnički račun niti ikakav identifikator za vas ili vaš računar.
Brojevi čekaju na vašem računaru (u keš mapi programa Fontes, `stats.json`) dok se ne pošalju;
ako slanje ne uspije, čekaju sljedeći dan.

- **Pristanak (opt-in)**: odgovorite „y“ kada instalacijski program pita ili postavite
  `FONTES_STATS=1` za Fontes server.
- **Odustajanje (opt-out)**: ponovo pokrenite instalacijski program i na tom pitanju pritisnite
  Enter ili uklonite `FONTES_STATS`. Brisanjem `stats.json` odbacuje se sve što još nije poslano.

**3. Prijave grešaka (samo kada je pošaljete).** Kada je zatražite (`fontes report-bug` ili
zamolite svoju AI aplikaciju da prijavi grešku u alatu Fontes), Fontes vam prvo prikaže cijelu
prijavu i šalje je samo ako potvrdite. Sadrži verziju programa Fontes, porodicu vašeg
operativnog sistema, kod jurisdikcije, naziv alata i poruku o grešci posljednjeg neuspješnog
poziva alata (s uklonjenim vašim riječima pretrage i identifikatorima) te napomenu ako je
napišete. Ne unosite podatke o klijentima u napomenu. Da bi ovo bilo moguće, Fontes čuva
posljednju grešku na vašem računaru (`last-error.json` u svojoj keš mapi, zamjenjuje se svaki
put); ona se nikada ne šalje sama.

## Kamo podaci idu i koliko dugo se čuvaju

Brojevi korištenja i prijave grešaka idu na mali server koji vodi programer projekta Fontes
(`relay.kinetra.fit`). On ne pohranjuje IP adrese: koriste se samo u memoriji, kratko, da bi se
spriječilo preplavljivanje, a web server za njega ne vodi dnevnik pristupa. Brojevi se sabiraju u
dnevne zbirove; pojedinačne pošiljke se ne čuvaju. Zbirovi se čuvaju do 2 godine, prijave grešaka
do 1 godine, a zatim se brišu. Ništa se ne prodaje niti dijeli.

Ako se taj server ne može dosegnuti, ništa se ne šalje: brojevi ostaju na vašem računaru, a
prijave grešaka vas umjesto toga upućuju na sistem za praćenje problema (issue tracker).

## Ko je odgovoran i na kojem osnovu

Kontrolor podataka za brojeve korištenja i prijave grešaka je Yüce Karapazar, programer
projekta Fontes. Kontakt: fontesmcp@proton.me.

Pravni osnov je vaš pristanak (član 6. stav 1. tačka (a) UK GDPR-a i GDPR-a EU). Brojevi
korištenja šalju se samo ako pristanete (opt-in), a prijava greške tek nakon što je potvrdite.
Pristanak možete povući u bilo kojem trenutku tako što ćete odustati na gore opisani način; to ne
utiče na ono što je ranije poslano.

## Kontakt

Pitanja ili zahtjevi: pišite na fontesmcp@proton.me ili otvorite prijavu problema (issue) na
<https://github.com/ykarapazar/fontes/issues>.
