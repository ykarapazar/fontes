> Ovo je mašinski potpomognut prevod. Merodavna je verzija na engleskom.

# Obaveštenje o privatnosti za Fontes

Fontes radi na vašem računaru. Vaše pretrage i dokumenti koje otvarate ostaju između vašeg
računara, zvaničnih izvora koje pretražujete i AI aplikacije koju koristite (prema uslovima te
aplikacije). Sam Fontes programerima projekta Fontes **podrazumevano ne šalje ništa**.

## Šta može da napusti vaš računar, i kada

**1. Provera ažuriranja (podrazumevano uključena).** Jednom dnevno Fontes pita PyPI, javni
indeks Python paketa, koja je verzija najnovija. Zahtev ne sadrži ništa o vama ili vašem radu;
PyPI vidi vašu IP adresu, kao i pri svakom preuzimanju. Da biste je isključili, podesite
`FONTES_NO_UPDATE_CHECK=1` (obaveštenje u aplikaciji) i `FONTES_NO_AUTO_UPDATE=1` (automatska
ažuriranja instalacionog programa).

**2. Brojevi korišćenja (isključeni, osim ako ih ne uključite).** Ako date pristanak (opt-in),
jednom dnevno Fontes šalje:

- verziju programa Fontes i porodicu vašeg operativnog sistema (macOS, Windows, Linux);
- po danima, koliko je puta svaki alat korišćen za svaki kod jurisdikcije, na primer
  "2026-11-10, nl, search_caselaw, 12".

To je cela poruka. Ona nikada ne sadrži vaše pretrage, identifikatore dokumenata ili predmeta,
tekst dokumenata, vaše ime, nalog niti bilo kakav identifikator za vas ili vaš računar.
Brojevi čekaju na vašem računaru (u keš fascikli programa Fontes, `stats.json`) dok ne budu
poslati; ako slanje ne uspe, čekaju do sledećeg dana.

- **Pristanak (opt-in)**: odgovorite "d" kada instalacioni program pita, ili podesite
  `FONTES_STATS=1` za Fontes server.
- **Odustajanje (opt-out)**: ponovo pokrenite instalacioni program i pritisnite Enter na tom
  pitanju, ili uklonite `FONTES_STATS`. Brisanjem `stats.json` odbacuje se sve što još nije
  poslato.

**3. Prijave grešaka (samo kada ih pošaljete).** Kada zatražite prijavu (`fontes report-bug`,
ili zamolite svoju AI aplikaciju da prijavi grešku u programu Fontes), Fontes vam prvo prikazuje
celu prijavu i šalje je samo ako potvrdite. Ona sadrži verziju programa Fontes, porodicu vašeg
operativnog sistema, kod jurisdikcije, naziv alata i poruku o grešci poslednjeg neuspelog poziva
alata (sa uklonjenim rečima pretrage i identifikatorima), kao i napomenu ako je napišete. Ne
unosite podatke o klijentima u napomenu. Radi toga Fontes čuva poslednju grešku na vašem
računaru (`last-error.json` u svojoj keš fascikli, zamenjuje se svaki put); ona se nikada ne
šalje sama.

## Gde se šalje i koliko dugo se čuva

Brojevi korišćenja i prijave grešaka šalju se na mali server kojim upravlja programer projekta
Fontes (`relay.kinetra.fit`). On ne čuva IP adrese: one se koriste samo u memoriji, kratko, da
bi se zaustavilo preplavljivanje zahtevima (flood), a veb server za njega ne vodi dnevnik pristupa.
Brojevi se sabiraju u dnevne zbirove; pojedinačna slanja se ne čuvaju. Zbirovi se čuvaju do
2 godine, prijave grešaka do 1 godine, a zatim se brišu. Ništa se ne prodaje niti deli.

Ako taj server nije dostupan, ništa se ne šalje: brojevi ostaju na vašem računaru, a prijave
grešaka vas umesto toga upućuju na sistem za praćenje problema (issue tracker).

## Ko je odgovoran i na osnovu čega

Rukovalac podacima za brojeve korišćenja i prijave grešaka je Yüce Karapazar, programer
projekta Fontes. Kontakt: fontesmcp@proton.me.

Pravni osnov je vaš pristanak (član 6(1)(a) UK GDPR i EU GDPR). Brojevi korišćenja šalju se samo
ako date pristanak (opt-in), a prijava greške tek kada je potvrdite. Pristanak možete povući u
bilo kom trenutku tako što ćete odustati na način opisan iznad; to ne utiče na ono što je ranije
poslato.

## Kontakt

Pitanja ili zahtevi: pišite na fontesmcp@proton.me ili otvorite issue na
<https://github.com/ykarapazar/fontes/issues>.
