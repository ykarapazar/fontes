> Šis ir tulkojums, kas sagatavots ar mašīntulkošanas palīdzību. Noteicošā ir angļu valodas versija.

# Fontes privātuma paziņojums

Fontes darbojas jūsu datorā. Jūsu meklējumi un atvērtie dokumenti paliek starp jūsu datoru,
avotiem, kurus meklējat (oficiālajiem, kā arī CourtListener un Lexifina, ja tos izmantojat, skatiet tālāk), un jūsu izmantoto MI lietotni (saskaņā ar šīs lietotnes
noteikumiem). Pats Fontes pēc noklusējuma Fontes izstrādātājiem **neko nesūta**.

## Kas var atstāt jūsu datoru un kad

**1. Atjauninājumu pārbaude (pēc noklusējuma ieslēgta).** Reizi dienā Fontes jautā PyPI –
publiskajam Python pakotņu katalogam –, kura versija ir jaunākā. Pieprasījumā nav nekā par jums
vai jūsu darbu; PyPI redz jūsu IP adresi, tāpat kā jebkuras lejupielādes laikā. Lai to
izslēgtu, iestatiet `FONTES_NO_UPDATE_CHECK=1` (paziņojums lietotnē) un `FONTES_NO_AUTO_UPDATE=1`
(instalētāja automātiskie atjauninājumi).

**2. Lietojuma skaitļi (izslēgti, ja vien tos neieslēdzat).** Ja piekrītat (opt-in), Fontes
reizi dienā nosūta:

- Fontes versiju un jūsu operētājsistēmas saimi (macOS, Windows, Linux);
- par katru dienu – cik reizes katrs rīks izmantots katram jurisdikcijas kodam, piemēram,
  “2026-11-10, nl, search_caselaw, 12”.

Tas ir viss ziņojums. Tajā nekad nav jūsu meklējumu, dokumentu vai lietu identifikatoru,
dokumentu teksta, jūsu vārda, konta vai jebkāda jūsu vai jūsu datora identifikatora. Skaitļi
gaida jūsu datorā (Fontes kešatmiņas mapē, `stats.json`), līdz tiek nosūtīti; ja nosūtīšana
neizdodas, tie gaida nākamo dienu.

- **Piekrist (opt-in)**: atbildiet “y”, kad instalētājs jautā, vai iestatiet `FONTES_STATS=1`
  Fontes serverim.
- **Atteikties (opt-out)**: vēlreiz palaidiet instalētāju un pie šī jautājuma nospiediet Enter
  vai noņemiet `FONTES_STATS`. Izdzēšot `stats.json`, tiek atmests viss, kas vēl nav nosūtīts.

**3. Kļūdu ziņojumi (tikai tad, kad jūs tādu nosūtāt).** Kad to pieprasāt (`fontes report-bug`
vai lūdzat savai MI lietotnei ziņot par Fontes kļūdu), Fontes vispirms parāda jums visu
ziņojumu un nosūta to tikai tad, ja apstiprināt. Tajā ir Fontes versija, jūsu operētājsistēmas
saime, pēdējā neizdevušās rīka izsaukuma jurisdikcijas kods, rīka nosaukums un kļūdas
paziņojums (ar izņemtiem jūsu meklēšanas vārdiem un identifikatoriem), kā arī piezīme, ja to
uzrakstāt. Neievietojiet piezīmē klientu datus. Lai to nodrošinātu, Fontes jūsu datorā glabā
pēdējo kļūdu (`last-error.json` savā kešatmiņas mapē, katru reizi aizstāta); tā nekad netiek
nosūtīta atsevišķi.

**4. Lexifina (pēc noklusējuma ieslēgts).** `get_law_on_date`, `get_law_history`, 91 valsts un Indijas akti tiek lasīti caur Lexifina tiesību aktu ierakstu, tādēļ tie nonāk Lexifina gan papildus oficiālajai vietnei, gan tās vietā. Jūsu meklēšanas vārdi, citāti un datumi tiek sūtīti uz Lexifina bezmaksas serveri `global-law.lexifina.com`, ko vada Lexifina, nevis Fontes izstrādātāji. Lexifina dokumentē, ka tās serveris reģistrē, kurš rīks tika izsaukts un cik ilgi tas prasīja, bet nekad – ko jautāja; Fontes to nevar pārbaudīt, un piemērojami ir Lexifina paša noteikumi. Lexifina redz jūsu IP adresi, kā jebkurš tīmekļa serveris. Lai to pilnībā izslēgtu, iestatiet `WLM_LEXIFINA=0`; tad minētie divi rīki un valstis pārstāj darboties un nekas netiek sūtīts uz turieni.

## Kur tas nonāk un cik ilgi tiek glabāts

Lietojuma skaitļi un kļūdu ziņojumi nonāk nelielā serverī, ko uztur Fontes izstrādātājs
(`relay.kinetra.fit`). Tas neglabā IP adreses: tās tiek izmantotas tikai atmiņā, īslaicīgi, lai
apturētu pieprasījumu plūdus, un tīmekļa serveris tam neuztur piekļuves žurnālu. Skaitļi tiek
saskaitīti dienas kopsummās; atsevišķi iesniegumi netiek glabāti. Kopsummas tiek glabātas līdz
2 gadiem, kļūdu ziņojumi – līdz 1 gadam, pēc tam tiek dzēsti. Nekas netiek pārdots vai nodots
citiem.

Ja šis serveris nav sasniedzams, nekas netiek nosūtīts: skaitļi paliek jūsu datorā, un kļūdu
ziņojumi tā vietā novirza jūs uz problēmu izsekotāju (issue tracker).

## Kas ir atbildīgs un uz kāda pamata

Lietojuma skaitļu un kļūdu ziņojumu datu pārzinis ir Yüce Karapazar, Fontes izstrādātājs.
Kontakti: fontesmcp@proton.me.

Tiesiskais pamats ir jūsu piekrišana (AK VDAR un ES VDAR 6. panta 1. punkta a) apakšpunkts).
Lietojuma skaitļi tiek nosūtīti tikai tad, ja piekrītat, un kļūdas ziņojums – tikai pēc tam, kad
to apstiprināt. Piekrišanu varat jebkurā laikā atsaukt, atsakoties, kā aprakstīts iepriekš; tas
neietekmē to, kas nosūtīts iepriekš.

## Kontakti

Jautājumi vai pieprasījumi: rakstiet uz fontesmcp@proton.me vai atveriet problēmu (issue) vietnē
<https://github.com/ykarapazar/fontes/issues>.
