> Ky është një përkthim i ndihmuar nga makina. Versioni në anglisht është ai që vlen.

# Fontes: pyetje dhe përgjigje

## Çfarë është Fontes?

Një server MCP falas dhe me burim të hapur (Apache 2.0). Ai i lejon çdo aplikacioni që flet Model
Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI dhe të tjerë) të kërkojë vendime
gjyqësore dhe legjislacion drejtpërdrejt në faqet e internetit të gjykatave dhe të institucioneve
shtetërore në 125 juridiksione dhe gjykata ndërkombëtare, plus 91 vende të tjera përmes regjistrit të Lexifina (shihni më poshtë). Çdo rezultat
emërton burimin e vet dhe lidhet me origjinalin.

## A janë tekstet zyrtare?

Kryesisht po, por jo gjithmonë.

- Shumica e burimeve drejtohen nga një gjykatë, një ministri ose një fletore zyrtare.
- Disa tekste të konsoliduara publikohen nga një qeveri, por janë shprehimisht jozyrtare: autentike
  është vetëm fletorja zyrtare.
- Disa burime nuk janë fare faqe shtetërore (për shembull LexiVox, LawPhil, Maqam, Wikisource).

Fontes shton njoftimin "Unofficial source" në çdo përgjigje që vjen nga një prej tyre. Para se të
citoni çfarëdo, kontrolloni botimin zyrtar. Tabela e mbulimit në [README](README.md#mbulimi) dhe
`list_jurisdictions` emërtojnë burimin për çdo juridiksion.

## Cilat juridiksione mbulon, dhe sa mirë?

125 adaptues: 108 shtete anëtare të OKB-së, Hong Kongu, Kosova, Palestina, Tajvani, DIFC Courts, gjykatat shtetërore të SHBA-së dhe 11 gjykata dhe organe ndërkombëtare (si Gjykata Evropiane e të Drejtave të Njeriut, BE-ja,
GJND-ja dhe OBT-ja).

Mbulimi ndryshon shumë. Sipas një rregulli të rreptë (precedentët e gjykatës më të lartë të
përgjithshme, ose kushtetuta dhe aktet primare, të arritura plotësisht), 72 nga 125 llogariten si
të mbuluara. [COVERAGE.md](../../COVERAGE.md) liston, për çdo juridiksion, çfarë arrin Fontes, çfarë
nuk arrin dhe pse.

## A më duhet një çelës API?

Për pothuajse çdo juridiksion, jo. Disa burime kërkojnë një çelës falas: shihni [KEYS.md](KEYS.md).

- **Franca:** po. Franca është joaktive derisa të vendosni `WLM_FR_PISTE_CLIENT_ID` dhe
  `WLM_FR_PISTE_CLIENT_SECRET`. Këto vijnë nga një llogari falas PISTE (piste.gouv.fr) me një
  aplikacion të abonuar në Judilibre dhe Légifrance.
- **Shtetet e Bashkuara:** opsional. Kërkimi i praktikës gjyqësore funksionon pa çelës, por çelësi
  demo i përbashkët lejon vetëm rreth 10 kërkime në ditë për adresë IP. Një çelës falas
  api.data.gov në `WLM_US_GOVINFO_KEY` e rrit këtë kufi.
- **Gjykatat shtetërore të SHBA-së:** po. Praktika gjyqësore e shteteve (`us-states`) është joaktive derisa të vendosni `WLM_US_COURTLISTENER_KEY` me token-in tuaj falas API të CourtListener. CourtListener drejtohet nga organizata jofitimprurëse Free Law Project; nuk është burim zyrtar, dhe çdo përgjigje e thotë këtë.

Vendosini këto si variabla mjedisi për serverin Fontes në cilësimet MCP të aplikacionit tuaj. Instaluesit jua kërkojnë pas instalimit, dhe nisësi i tyre **Add or change keys** i
ndryshon më vonë.

Më vete, disa burime thonë në kushtet e tyre se aksesi i automatizuar kërkon lejen e botuesit. Ato
janë të shënuara OFF dhe mbeten joaktive. Një çelës nuk e ndryshon këtë; vetëm leja e botuesit e
ndryshon (atëherë vendosni `WLM_PERMITTED=<codes>`).

## Nga vijnë versionet e mëparshme dhe vendet shtesë?

Nga [Lexifina](https://github.com/lexifina/global-law), që mban ligjin e rreth 200 vendeve si histori git: çdo ndryshim është një commit i datës kur hyri në fuqi. Fontes e lexon përmes serverit falas të pritur të Lexifina. Dy mjete e përdorin atë: `get_law_on_date` (një dispozitë siç ishte në fuqi në një datë, edhe në të kaluarën, me ligjin që e ndryshoi së fundmi) dhe `get_law_history` (çdo ligj që ka ndryshuar një dispozitë, ose ndryshimi fjalë për fjalë midis dy datave). Fontes lexon gjithashtu 91 vende dhe territore të tjera në këtë mënyrë, vetëm për legjislacion (për shembull Afrika e Jugut, Kenia, Meksika, Zelanda e Re, Rusia, Koreja e Jugut, Belgjika, Lituania, Ukraina, Malajzia, Tajlanda dhe Arabia Saudite). Ato janë veçmas nga 125 adaptuesit me mbulim zyrtar live, dhe mbulimi për çdo vend ndryshon shumë (regjistri kombëtar i Kenias mban 9 akte). Aktet e Indisë vijnë gjithashtu nga regjistri i Lexifina, sepse kushtet e India Code ndalojnë aksesin e automatizuar; vendimet e Gjykatës së Lartë të saj janë live.

Lexifina nuk është botuesi zyrtar, dhe regjistri i saj nuk është live: Lexifina e rikontrollon çdo vend herë pas here, dhe raporti i vet më 2026-11-26 numëroi 338 nga 383 organe kombëtare të ligjit si të pakontrolluara në 7 ditët e fundit. Çdo përgjigje emëron Lexifina si burim, lidh faqen e botuesit zyrtar dhe thotë sa shkon regjistri.

Lexifina mendon se tekstet zyrtare ligjore nuk mbrohen nga e drejta e autorit, ndaj në disa vende kopjon faqe, kushtet ose robots.txt e të cilave Fontes vetë i respekton. Fontes i respekton ende ato për gjithçka që merr vetë; ajo që vjen përmes Lexifina ndjek gjykimin e vet ligjor, të regjistruar për çdo vend në depot e tij. Disa e kufizojnë përdorimin (botuesi i Kenias: CC BY-NC). Fjalët tuaja të kërkimit, citimet dhe datat shkojnë për këto te serveri i Lexifina. Vendosni `WLM_LEXIFINA=0` për ta çaktivizuar. Serveri falas lejon 60 thirrje në minutë dhe 10.000 në ditë për çdo adresë interneti; pa çelës dhe pa llogari. Fontes nuk ka lidhje me Lexifina.

## Çfarë del nga kompjuteri im?

Kërkimet tuaja shkojnë vetëm te burimi ku kërkohet (për mjetet dhe vendet e Lexifina, ai është serveri i Lexifina). Fontes nuk mban bazë të dhënash dhe nuk kërkon
llogari.

Përveç burimeve, Fontes pyet PyPI-në një herë në ditë nëse ekziston një version më i ri
(çaktivizohet me `FONTES_NO_UPDATE_CHECK=1`). Numërimet e përdorimit janë joaktive, përveç nëse i
aktivizoni, dhe një raport gabimi dërgohet vetëm pasi ta keni parë dhe konfirmuar. Aplikacioni juaj
i AI-së e sheh bisedën tuaj sipas kushteve të veta.

Të gjitha hollësitë: [PRIVACY.md](PRIVACY.md).

## A është kjo këshillë juridike?

Jo. Fontes është një mjet kërkimi. Ai gjen tekste; nuk ju tregon çfarë kuptimi kanë për çështjen
tuaj, dhe përdorimi i tij nuk krijon marrëdhënie avokat–klient me askënd. Aplikacioni i AI-së mund
ta keqlexojë një tekst, prandaj lexoni vendimin ose dispozitën të plotë para se të mbështeteni tek
ajo. Për këshillë, pyesni një avokat të kualifikuar në vendin ku lind pyetja juaj.

## Kush e mirëmban? A do të vazhdojë të funksionojë?

Një person: Yüce Karapazar. Pas Fontes nuk ka asnjë kompani, asnjë kontratë mbështetjeje dhe asnjë
premtim për nivelin e shërbimit. Nuk ofrohen shërbime juridike.

Burimet kontrollohen një herë në ditë dhe rezultatet publikohen në
[faqen e gjendjes](https://ykarapazar.github.io/fontes/status/?lang=sq). Faqet e internetit të
gjykatave dhe të institucioneve shtetërore ndryshojnë pa njoftim, prandaj një burim mund të prishet
në çdo kohë. Nuk ka asnjë garanci që ndonjë burim, apo vetë Fontes, do të vazhdojë të funksionojë.
Fontes ofrohet "siç është", pa garanci (seksionet 7 dhe 8 të [LICENSE](../../../LICENSE)).

## Një tekst është i gabuar, i vjetëruar, ose një burim nuk funksionon. Si ta raportoj?

- Hapni një issue me formularin "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Tregoni cili juridiksion, çfarë pyetët,
  çfarë morët dhe faqen zyrtare që tregon tekstin e saktë.
- Ose kërkojini aplikacionit tuaj të AI-së të "raportojë një gabim të Fontes" (ose ekzekutoni
  `fontes report-bug`). Ju e shihni raportin para se të dërgohet çfarëdo.
- Ose shkruani te fontesmcp@proton.me.

Mos përfshini të dhëna të klientëve ose fakte konfidenciale në një raport.

**Nëse drejtoni një nga burimet** dhe diçka nuk është në rregull (kushtet tuaja, robots.txt-ja juaj,
kufijtë tuaj të kërkesave), shkruani te fontesmcp@proton.me. Burimi do të rregullohet ose do të
çaktivizohet.

## Si ndryshon Fontes nga mjetet e kërkimit juridik të strehuara në internet?

- **Funksionon në kompjuterin tuaj.** Nuk ka server të Fontes dhe nuk ka llogari. Kjo do të thotë
  gjithashtu se funksionon vetëm në aplikacione që mund të nisin një server MCP lokal (Claude
  Desktop, Codex, Cursor, VS Code dhe të ngjashme), jo në aplikacione vetëm web që pranojnë vetëm
  konektorë të strehuar.
- **Nuk ka bazë të dhënash.** Çdo kërkim shkon drejtpërdrejt në faqen e internetit ose API-në e
  vetë botuesit, prandaj rezultatet janë po aq të përditësuara sa burimi, dhe cilësia e kërkimit
  është ajo e vetë burimit. Nuk ka kërkim semantik mbi një indeks të kuruar.
- **Nuk vendos kufi përdorimi.** Fontes nuk ka kufi mujor thirrjesh. Ai i shpërndan në kohë
  kërkesat e veta te çdo faqe interneti, dhe disa burime kufizojnë sa shpejt ose sa shpesh mund të
  pyeten.
- **Është me burim të hapur.** Mund të lexoni çdo adaptues dhe të shihni saktësisht nga vjen çdo
  tekst.
- **Pas tij nuk ka shitës.** Asnjë kontratë, asnjë shërbim mbështetjeje dhe asnjë premtim
  disponueshmërie (shihni "Kush e mirëmban?").

## Me cilat aplikacione dhe sisteme funksionon?

Me çdo aplikacion MCP që mund të nisë një server lokal (stdio), për shembull Claude Desktop, Claude
Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio dhe Cline.
Fontes funksionon në macOS, Windows dhe Linux, kudo ku funksionon uv (Python 3.13+). Në Mac ose në Windows PC, një
instalues me një klik konfiguron njëherësh Claude Desktop, Codex, Claude Code, Cursor, VS Code,
Windsurf, Gemini CLI, Zed, LM Studio dhe Cline. Hapat për
çdo aplikacion: [INSTALL.md](INSTALL.md).

## A mund të kontribuoj me kod?

Jo për momentin. Issues, raportet për burimet dhe kërkesat për juridiksione janë të mirëpritura.
Shihni [CONTRIBUTING.md](../../../CONTRIBUTING.md).
