> Ky është një përkthim i ndihmuar nga makina. Versioni në anglisht është ai që vlen.

# Njoftimi i privatësisë i Fontes

Fontes funksionon në kompjuterin tuaj. Kërkimet tuaja dhe dokumentet që hapni mbeten mes
kompjuterit tuaj, burimeve zyrtare ku kërkoni dhe aplikacionit të AI-së që përdorni (sipas kushteve
të vetë atij aplikacioni). Vetë Fontes nuk u dërgon zhvilluesve të Fontes **asgjë si parazgjedhje**.

## Çfarë mund të dalë nga kompjuteri juaj, dhe kur

**1. Kontrolli i përditësimeve (aktiv si parazgjedhje).** Një herë në ditë Fontes pyet PyPI-në,
indeksin publik të paketave Python, se cili është versioni më i ri. Kërkesa nuk mban asgjë për ju
ose punën tuaj; PyPI sheh adresën tuaj IP, si në çdo shkarkim. Për ta çaktivizuar, vendosni
`FONTES_NO_UPDATE_CHECK=1` (njoftimi brenda aplikacionit) dhe `FONTES_NO_AUTO_UPDATE=1`
(përditësimet automatike të instaluesit).

**2. Numërimet e përdorimit (joaktive, përveç nëse i aktivizoni).** Nëse jepni pëlqimin (opt-in),
një herë në ditë Fontes dërgon:

- versionin e Fontes dhe familjen e sistemit tuaj operativ (macOS, Windows, Linux);
- për çdo ditë, sa herë u përdor secili mjet për secilin kod juridiksioni, për shembull
  "2026-11-10, nl, search_caselaw, 12".

Ky është i gjithë mesazhi. Nuk përfshin kurrë kërkimet tuaja, identifikuesit e dokumenteve ose të
çështjeve, tekstin e dokumenteve, emrin tuaj, një llogari, ose ndonjë identifikues për ju ose
kompjuterin tuaj. Numërimet presin në kompjuterin tuaj (në dosjen cache të Fontes, `stats.json`)
derisa të dërgohen; nëse dërgimi dështon, presin deri të nesërmen.

- **Pëlqimi (opt-in)**: përgjigjuni "p" kur instaluesi pyet, ose vendosni `FONTES_STATS=1` për
  serverin Fontes.
- **Tërheqja (opt-out)**: ekzekutoni sërish instaluesin dhe shtypni Enter te ajo pyetje, ose hiqni
  `FONTES_STATS`. Fshirja e `stats.json` hedh poshtë çdo gjë që nuk është dërguar ende.

**3. Raportet e gabimeve (vetëm kur dërgoni një të tillë).** Kur kërkoni një (`fontes report-bug`,
ose i kërkoni aplikacionit tuaj të AI-së të raportojë një gabim të Fontes), Fontes ju tregon së
pari raportin e plotë dhe e dërgon vetëm nëse e konfirmoni. Ai përmban versionin e Fontes,
familjen e sistemit tuaj operativ, kodin e juridiksionit, emrin e mjetit dhe mesazhin e gabimit të
thirrjes së fundit të dështuar të një mjeti (me fjalët tuaja të kërkimit dhe identifikuesit të
hequr), dhe një shënim nëse shkruani një të tillë. Mos vendosni të dhëna të klientëve në shënim. Për
këtë qëllim, Fontes ruan gabimin e fundit në kompjuterin tuaj (`last-error.json` në dosjen e tij
cache, që zëvendësohet çdo herë); ai nuk dërgohet kurrë më vete.

## Ku shkon dhe sa kohë ruhet

Numërimet e përdorimit dhe raportet e gabimeve shkojnë në një server të vogël që drejtohet nga
zhvilluesi i Fontes (`relay.kinetra.fit`). Ai nuk ruan adresa IP: ato përdoren vetëm në memorie,
për pak kohë, për të ndaluar vërshimet, dhe serveri web nuk mban regjistër aksesi për të. Numërimet
mblidhen në totale ditore; dërgesat e veçanta nuk ruhen. Totalet ruhen deri në 2 vjet, raportet e
gabimeve deri në 1 vit, pastaj fshihen. Asgjë nuk shitet dhe nuk ndahet me të tjerë.

Nëse ai server nuk mund të arrihet, nuk dërgohet asgjë: numërimet mbeten në kompjuterin tuaj dhe
raportet e gabimeve ju drejtojnë në vend të kësaj te gjurmuesi i problemeve (issue tracker).

## Kush është përgjegjës, dhe mbi çfarë baze

Kontrolluesi i të dhënave për numërimet e përdorimit dhe raportet e gabimeve është Yüce Karapazar,
zhvilluesi i Fontes. Kontakt: fontesmcp@proton.me.

Baza ligjore është pëlqimi juaj (neni 6(1)(a) i UK GDPR dhe i GDPR të BE-së). Numërimet e
përdorimit dërgohen vetëm nëse jepni pëlqimin, dhe një raport gabimi vetëm pasi ta konfirmoni. Mund
ta tërhiqni pëlqimin në çdo kohë duke e refuzuar siç përshkruhet më sipër; kjo nuk ndikon në atë që
është dërguar më parë.

## Kontakti

Pyetje ose kërkesa: shkruani te fontesmcp@proton.me, ose hapni një issue te
<https://github.com/ykarapazar/fontes/issues>.
