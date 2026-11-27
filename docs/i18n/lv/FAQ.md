> Šis ir tulkojums, kas sagatavots ar mašīntulkošanas palīdzību. Noteicošā ir angļu valodas versija.

# Fontes: jautājumi un atbildes

## Kas ir Fontes?

Bezmaksas atvērtā koda MCP serveris (Apache 2.0). Tas ļauj jebkurai lietotnei, kas izmanto
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI un citām), tiešsaistē meklēt
tiesu nolēmumus un tiesību aktus tiesu un valsts iestāžu tīmekļa vietnēs 125 jurisdikcijās un starptautiskajās tiesās, kā arī
vēl 91 valstī caur Lexifina ierakstu (skatiet tālāk). Katrs rezultāts nosauc savu avotu un
sniedz saiti uz oriģinālu.

## Vai teksti ir oficiāli?

Lielākoties, bet ne vienmēr.

- Lielāko daļu avotu uztur tiesa, ministrija vai oficiālais izdevums.
- Dažus konsolidētos tekstus publicē valdība, taču tie ir skaidri norādīti kā neoficiāli:
  autentisks ir tikai oficiālais izdevums.
- Daži avoti vispār nav valsts iestāžu vietnes (piemēram, LexiVox, LawPhil, Maqam,
  Wikisource).

Katrai atbildei, kas nāk no kāda no šiem avotiem, Fontes pievieno paziņojumu “Unofficial
source”. Pirms kaut ko citējat, pārbaudiet oficiālo publikāciju. Pārklājuma tabula
[README](README.md#pārklājums) un `list_jurisdictions` nosauc avotu katrai jurisdikcijai.

## Kuras jurisdikcijas tas aptver un cik labi?

125 adapteri: 108 ANO dalībvalstis, Honkonga, Kosova, Palestīna, Taivāna, DIFC Courts, ASV štatu tiesas un 11 starptautiskās tiesas un institūcijas (piemēram, Eiropas Cilvēktiesību tiesa, ES, Starptautiskā Tiesa un
PTO).

Pārklājums ļoti atšķiras. Pēc stingra kritērija (pilnībā sasniegti augstākās vispārējās
jurisdikcijas tiesas precedenti vai konstitūcija un primārie likumi) 72 no 125 tiek uzskatītas
par aptvertām. [COVERAGE.md](../../COVERAGE.md) katrai jurisdikcijai uzskaita, ko Fontes
sasniedz, ko nesasniedz un kāpēc.

## Vai man vajadzīga API atslēga?

Gandrīz visās jurisdikcijās – nē. Dažiem avotiem vajadzīga bezmaksas atslēga: skatiet
[KEYS.md](KEYS.md).

- **Francija:** jā. Francija ir izslēgta, līdz iestatāt `WLM_FR_PISTE_CLIENT_ID` un
  `WLM_FR_PISTE_CLIENT_SECRET`. Tos iegūst no bezmaksas PISTE konta (piste.gouv.fr) ar
  lietotni, kas abonē Judilibre un Légifrance.
- **Amerikas Savienotās Valstis:** pēc izvēles. Tiesu prakses meklēšana darbojas bez atslēgas,
  taču koplietotā demonstrācijas atslēga ļauj tikai aptuveni 10 meklējumus dienā no vienas IP
  adreses. Bezmaksas api.data.gov atslēga mainīgajā `WLM_US_GOVINFO_KEY` šo ierobežojumu
  palielina.
- **ASV štatu tiesas:** jā. Štatu tiesu prakse (`us-states`) ir izslēgta, līdz iestatāt `WLM_US_COURTLISTENER_KEY` ar savu bezmaksas CourtListener API token. CourtListener uztur bezpeļņas organizācija Free Law Project; tas nav oficiāls avots, un katra atbilde to norāda.

Iestatiet tos kā vides mainīgos Fontes serverim savas lietotnes MCP iestatījumos. Instalētāji
pēc instalēšanas jautā pēc tiem, un to palaidējs **Add or change keys** ļauj tos vēlāk mainīt.

Atsevišķi: daži avoti savos noteikumos norāda, ka automatizētai piekļuvei vajadzīga izdevēja
atļauja. Tie ir atzīmēti kā OFF un paliek izslēgti. Atslēga to nemaina; to maina tikai
izdevēja atļauja (tad iestatiet `WLM_PERMITTED=<codes>`).

## No kurienes nāk iepriekšējās redakcijas un papildu valstis?

No [Lexifina](https://github.com/lexifina/global-law), kas glabā apmēram 200 valstu tiesības kā git vēsturi: katrs grozījums ir commit ar datumu, kad tas stājās spēkā. Fontes to lasa caur Lexifina bezmaksas mitināto serveri. Divi rīki to izmanto: `get_law_on_date` (norma, kāda tā bija spēkā datumā, arī pagātnē, kopā ar likumu, kas to pēdējo reizi grozīja) un `get_law_history` (katrs likums, kas grozīja normu, vai vārdu pa vārdam izmaiņas starp diviem datumiem). Fontes tādā pat veidā lasa arī vēl 91 valsti un teritoriju, tikai tiesību aktiem (piemēram, Dienvidāfrika, Kenija, Meksika, Jaunzēlande, Krievija, Dienvidkoreja, Beļģija, Lietuva, Ukraina, Malaizija, Taizeme un Saūda Arābija). Tās ir atsevišķas no 125 adapteriem ar aktīvu oficiālo pārklājumu, un pārklājums katrā valstī ļoti atšķiras (Kenijas nacionālajā ierakstā ir 9 akti). Indijas akti arī nāk no Lexifina ieraksta, jo India Code noteikumi aizliedz automatizētu piekļuvi; tās Augstākās tiesas spriedumi ir aktīvi.

Lexifina nav oficiālais izdevējs, un tās ieraksts nav aktīvs: Lexifina laiku pa laikam pārbauda katru valsti, un tās pašas 2026-11-26 pārskatā 338 no 383 nacionālajām tiesību aktu struktūrām bija nepārbaudītas pēdējās 7 dienās. Katra atbilde nosauc Lexifina kā avotu, sniedz saiti uz oriģinālā izdevēja lapu un norāda, cik tālu sniedzas ieraksts.

Lexifina uzskata, ka oficiālie juridiskie teksti nav aizsargāti ar autortiesībām, tāpēc dažās valstīs tā kopē vietnes, kuru noteikumus vai robots.txt Fontes pats respektē. Fontes joprojām respektē robots.txt un noteikumus visam, ko pats iegūst; tas, kas nāk caur Lexifina, seko Lexifina pašas juridiskajam vērtējumam, ko tā fiksē katrai valstij savos repozitorijos. Dažus lietojumus ierobežo (piemēram, Kenijas izdevējs: CC BY-NC). Jūsu meklēšanas vārdi, citāti un datumi šiem diviem rīkiem un šīm valstīm tiek sūtīti uz Lexifina serveri. Lai to izslēgtu, iestatiet `WLM_LEXIFINA=0`. Atslēga vai konts nav vajadzīgs; bezmaksas serveris atļauj 60 izsaukumus minūtē un 10 000 dienā uz vienu interneta adresi. Fontes nav saistīts ar Lexifina.

## Kas atstāj manu datoru?

Jūsu meklējumi nonāk tikai avotā, kurā meklējat (Lexifina rīku un valstu gadījumā – Lexifina serverī). Fontes neuztur datubāzi, un tam nav vajadzīgs
konts.

Bez avotiem Fontes reizi dienā jautā PyPI, vai ir jaunāka versija (to var izslēgt ar
`FONTES_NO_UPDATE_CHECK=1`). Lietojuma skaitļi ir izslēgti, ja vien tos neieslēdzat, un kļūdas
ziņojums tiek nosūtīts tikai pēc tam, kad esat to redzējis un apstiprinājis. Jūsu MI lietotne
redz jūsu sarunu saskaņā ar saviem noteikumiem.

Sīkāk: [PRIVACY.md](PRIVACY.md).

## Vai tā ir juridiska konsultācija?

Nē. Fontes ir izpētes rīks. Tas atrod tekstus; tas nesaka, ko tie nozīmē jūsu lietā, un tā
lietošana ne ar vienu nenodibina advokāta un klienta attiecības. MI lietotne var nepareizi
izlasīt tekstu, tāpēc pirms paļaušanās uz to izlasiet pilnu nolēmumu vai normu. Lai saņemtu
konsultāciju, vērsieties pie jurista, kas ir kvalificēts tajā vietā, kur rodas jūsu jautājums.

## Kas to uztur? Vai tas turpinās darboties?

Viens cilvēks: Yüce Karapazar. Aiz Fontes nav uzņēmuma, nav atbalsta līguma un nav pakalpojumu
līmeņa solījuma. Juridiskie pakalpojumi netiek piedāvāti.

Avoti tiek pārbaudīti reizi dienā, un rezultāti tiek publicēti
[statusa lapā](https://ykarapazar.github.io/fontes/status/?lang=lv). Tiesu un valsts iestāžu
tīmekļa vietnes mainās bez brīdinājuma, tāpēc avots var jebkurā brīdī pārstāt darboties. Nav
garantijas, ka kāds avots vai pats Fontes turpinās darboties. Fontes tiek nodrošināts “tāds,
kāds ir” (“as is”), bez garantijām ([LICENSE](../../../LICENSE) 7. un 8. sadaļa).

## Teksts ir nepareizs, novecojis vai avots nedarbojas. Kā par to ziņot?

- Atveriet problēmu (issue) ar veidlapu “Broken or wrong source”:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Norādiet jurisdikciju, ko jautājāt,
  ko saņēmāt, un oficiālo lapu, kurā redzams pareizais teksts.
- Vai lūdziet savai MI lietotnei “ziņot par Fontes kļūdu” (vai palaidiet `fontes report-bug`).
  Jūs redzat ziņojumu, pirms kaut kas tiek nosūtīts.
- Vai rakstiet uz fontesmcp@proton.me.

Neiekļaujiet ziņojumā klientu datus vai konfidenciālus faktus.

**Ja jūs uzturat kādu no avotiem** un kaut kas nav kārtībā (jūsu noteikumi, jūsu robots.txt,
jūsu pieprasījumu ierobežojumi), rakstiet uz fontesmcp@proton.me. Avots tiks salabots vai
izslēgts.

## Ar ko Fontes atšķiras no mākoņā mitinātiem juridiskās izpētes rīkiem?

- **Tas darbojas jūsu datorā.** Nav Fontes servera un nav konta. Tas arī nozīmē, ka tas
  darbojas tikai lietotnēs, kas var palaist lokālu MCP serveri (Claude Desktop, Codex, Cursor,
  VS Code un līdzīgās), nevis tikai tīmekļa lietotnēs, kas pieņem tikai mitinātus savienotājus.
- **Tam nav datubāzes.** Katrs meklējums tiešsaistē nonāk izdevēja paša tīmekļa vietnē vai
  API, tāpēc rezultāti ir tikpat aktuāli kā avots, un meklēšanas kvalitāte ir paša avota
  kvalitāte. Nav semantiskās meklēšanas pa atlasītu indeksu.
- **Tas nenosaka lietojuma ierobežojumu.** Fontes nav mēneša izsaukumu limita. Tas izkliedē
  savus pieprasījumus katrai tīmekļa vietnei, un daži avoti ierobežo, cik ātri vai cik bieži
  tiem var veikt vaicājumus.
- **Tas ir atvērtā koda.** Jūs varat izlasīt katru adapteri un precīzi redzēt, no kurienes nāk
  katrs teksts.
- **Aiz tā nav piegādātāja.** Nav līguma, atbalsta dienesta vai darbspējas solījuma (skatiet
  “Kas to uztur?”).

## Ar kurām lietotnēm un sistēmām tas darbojas?

Ar jebkuru MCP lietotni, kas var palaist lokālu (stdio) serveri, piemēram, Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio un
Cline. Fontes darbojas macOS, Windows un Linux, visur, kur darbojas uv (Python 3.13+). Mac vai Windows datorā
instalētājs ar vienu klikšķi vienā reizē iestata Claude Desktop, Codex, Claude
Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio un Cline. Darbības katrai lietotnei:
[INSTALL.md](INSTALL.md).

## Vai varu sniegt savu ieguldījumu kodā?

Pašlaik nē. Problēmu ziņojumi (issues), ziņojumi par avotiem un jurisdikciju pieprasījumi ir
laipni gaidīti. Skatiet [CONTRIBUTING.md](../../../CONTRIBUTING.md).
