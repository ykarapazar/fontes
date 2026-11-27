> See on masinabil tehtud tõlge. Autoriteetne on ingliskeelne versioon.

# Fontes: küsimused ja vastused

## Mis on Fontes?

Tasuta avatud lähtekoodiga MCP-server (Apache 2.0). See võimaldab igal Model Context
Protocoli toetaval rakendusel (Claude, Codex, Cursor, VS Code, Gemini CLI ja teised) otsida kohtulahendeid ja
õigusakte reaalajas kohtute ja valitsuste veebisaitidelt 125 jurisdiktsioonis ja rahvusvahelistes kohtutes,
lisaks 91 veel riiki Lexifina registri kaudu (vt allpool). Iga tulemus nimetab oma allika ja lingib originaalile.

## Kas tekstid on ametlikud?

Enamasti, kuid mitte alati.

- Enamikku allikaid haldab kohus, ministeerium või ametlik väljaanne.
- Mõned terviktekstid avaldab valitsus, kuid need on sõnaselgelt mitteametlikud: autentne on ainult
  ametlik väljaanne.
- Mõned allikad ei ole üldse valitsuse saidid (näiteks LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes lisab teate „Mitteametlik allikas“ igale vastusele, mis pärineb mõnest neist. Enne
kui millelegi viitate, kontrollige ametlikku väljaannet. Katvuse tabel
[README-s](README.md#katvus) ja `list_jurisdictions` nimetavad iga jurisdiktsiooni allika.

## Milliseid jurisdiktsioone see katab ja kui hästi?

125 adapterit: 108 ÜRO liikmesriiki, Hongkong, Kosovo, Palestiina, Taiwan, DIFC Courts, USA osariikide kohtud ja 11 rahvusvahelist kohut ja organit (näiteks Euroopa Inimõiguste Kohus, EL,
Rahvusvaheline Kohus (ICJ) ja WTO).

Katvus erineb palju. Range reegli järgi (kõrgeima üldkohtu pretsedendid või
põhiseadus ja peamised seadused, täielikult kättesaadavad) loetakse kaetuks 72 jurisdiktsiooni 125-st.
[COVERAGE.md](../../COVERAGE.md) loetleb iga jurisdiktsiooni kohta, mida Fontes kätte saab, mida mitte,
ja miks.

## Kas ma vajan API-võtit?

Peaaegu iga jurisdiktsiooni puhul mitte. Mõni allikas vajab tasuta võtit: vt [KEYS.md](KEYS.md).

- **Prantsusmaa:** jah. Prantsusmaa on välja lülitatud, kuni määrate `WLM_FR_PISTE_CLIENT_ID` ja
  `WLM_FR_PISTE_CLIENT_SECRET`. Need saate tasuta PISTE kontolt (piste.gouv.fr), millel on
  Judilibre ja Légifrance'i tellinud rakendus.
- **Ameerika Ühendriigid:** valikuline. Kohtupraktika otsing töötab ilma võtmeta, kuid jagatud demovõti
  lubab ainult umbes 10 otsingut päevas IP-aadressi kohta. Tasuta api.data.gov võti muutujas
  `WLM_US_GOVINFO_KEY` tõstab seda piiri.
- **USA osariikide kohtud:** jah. Osariikide kohtupraktika (`us-states`) on välja lülitatud, kuni seate `WLM_US_COURTLISTENER_KEY` oma tasuta CourtListeneri API-tunnuseks. CourtListenerit haldab mittetulundusorganisatsioon Free Law Project; see ei ole ametlik allikas ja iga vastus ütleb seda.

Määrake need Fontese serveri keskkonnamuutujatena oma rakenduse MCP-seadetes. Paigaldajad
küsivad neid pärast paigaldamist ja nende käivitaja **Add or change keys** muudab neid hiljem.

Eraldi märgivad mõned allikad oma tingimustes, et automatiseeritud juurdepääs nõuab avaldaja
luba. Need on märgitud OFF ja jäävad välja lülitatuks. Võti seda ei muuda; seda muudab ainult
avaldaja luba (siis määrake `WLM_PERMITTED=<codes>`).

## Kust tulevad varasemad versioonid ja lisariigid?

[Lexifina](https://github.com/lexifina/global-law) hoiab umbes 200 riigi õigust git-ajaloona: iga muudatus on commit, mis on dateeritud päeval, mil see jõustus. Fontes loeb seda Lexifina tasuta serveri kaudu. Kahte tööriista kasutatakse selleks: `get_law_on_date` (säte sellisena, nagu see kehtis kuupäeval, ka minevikus, koos seadusega, mis seda viimati muutis) ja `get_law_history` (iga seadus, mis sätet muutis, või sõnasõnaline muudatus kahe kuupäeva vahel). Fontes loeb selle kaudu veel 91 riiki ja territooriumi, ainult õigusakte (näiteks Lõuna-Aafrika, Keenia, Mehhiko, Uus-Meremaa, Venemaa, Lõuna-Korea, Belgia, Leedu, Ukraina, Malaisia, Tai ja Saudi Araabia). Need on eraldi 125 adapterist, millel on reaalajas ametlik katvus, ja katvus riigiti varieerub palju (Keenia riiklik register sisaldab 9 akti). India aktid tulevad samuti Lexifina registrist, sest India Code'i tingimused keelavad automatiseeritud juurdepääsu; selle Ülemkohtu otsused on reaalajas.

Lexifina ei ole ametlik avaldaja ja tema register ei ole reaalajas: Lexifina kontrollib iga riiki aeg-ajalt, ning tema enda 2026-11-26 aruanne luges 383 riigi õigusallikast 338 viimase 7 päeva jooksul kontrollimata. Iga vastus nimetab Lexifinat allikana, lingib ametliku avaldaja lehe ja ütleb, kui kaugele register ulatub.

Lexifina seisukoha järgi ei ole ametlikud õigustekstid autoriõigusega kaitstud, seetõttu kopeerib ta mõnes riigis saite, mille tingimusi või robots.txt Fontes ise austab. Fontes austab neid kõige puhul, mida ta ise alla laeb; Lexifina kaudu tulev järgib Lexifina enda hinnangut, mis on iga riigi kohta kirjas tema hoidlates. Mõned piiravad kasutust (Keenia avaldaja: CC BY-NC). Teie otsingusõnad, viited ja kuupäevad lähevad nende puhul Lexifina serverisse. Selle väljalülitamiseks seadke `WLM_LEXIFINA=0`. Tasuta server lubab 60 päringut minutis ja 10 000 päevas internetiaadressi kohta; võtit ega kontot pole vaja. Fontes ei ole Lexifinaga seotud.

## Mis minu arvutist lahkub?

Teie otsingud lähevad ainult otsitavale allikale (Lexifina tööriistade ja riikide puhul on see Lexifina server). Fontes ei pea andmebaasi ega vaja
kontot.

Lisaks allikatele küsib Fontes kord päevas PyPI-lt, kas on olemas uuem versioon (välja lülitatav
seadega `FONTES_NO_UPDATE_CHECK=1`). Kasutuskordade arvud on väljas, kui te neid sisse ei lülita, ja veateade
saadetakse alles siis, kui olete seda näinud ja kinnitanud. Teie tehisintellekti rakendus näeb teie vestlust oma
tingimuste alusel.

Kõik üksikasjad: [PRIVACY.md](PRIVACY.md).

## Kas see on õigusnõu?

Ei. Fontes on uurimistööriist. See leiab tekste; see ei ütle teile, mida need teie
asjas tähendavad, ja selle kasutamine ei loo kellegagi advokaadi ja kliendi suhet. Tehisintellekti rakendus võib
teksti valesti lugeda, seega lugege kogu lahendit või sätet, enne kui sellele tuginete. Nõu saamiseks pöörduge
juristi poole, kellel on kvalifikatsioon seal, kus teie küsimus tekib.

## Kes seda haldab? Kas see jätkab töötamist?

Üks inimene: Yüce Karapazar. Fontese taga ei ole ettevõtet, tugilepingut ega
teenustaseme lubadust. Õigusteenuseid ei osutata.

Allikaid kontrollitakse kord päevas ja tulemused avaldatakse
[seisundilehel](https://ykarapazar.github.io/fontes/status/?lang=et). Kohtute ja valitsuste veebisaidid
muutuvad ette teatamata, seega võib allikas igal ajal katki minna. Puudub garantii, et ükski allikas
või Fontes ise jätkab töötamist. Fontes antakse „nagu on“, ilma garantiita ([LICENSE](../../../LICENSE)-faili jaotised 7
ja 8).

## Tekst on vale või aegunud või allikas ei tööta. Kuidas sellest teatada?

- Avage issue vormiga „Broken or wrong source“:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Märkige, milline jurisdiktsioon, mida te
  küsisite, mida saite ja milline ametlik leht näitab õiget teksti.
- Või paluge oma tehisintellekti rakendusel „teatada Fontese veast“ (või käivitage `fontes report-bug`). Näete teadet enne,
  kui midagi saadetakse.
- Või kirjutage aadressile fontesmcp@proton.me.

Ärge lisage teatesse kliendi andmeid ega konfidentsiaalseid asjaolusid.

**Kui haldate mõnda allikat** ja midagi on valesti (teie tingimused, teie robots.txt, teie päringupiirangud),
kirjutage aadressile fontesmcp@proton.me. Allikas parandatakse või lülitatakse välja.

## Mille poolest erineb Fontes veebipõhistest õigusalase uurimistöö tööriistadest?

- **See töötab teie arvutis.** Fontese serverit ega kontot ei ole. See tähendab ka, et see
  töötab ainult rakendustes, mis suudavad käivitada kohalikku MCP-serverit (Claude Desktop, Codex, Cursor, VS Code
  ja sarnased), mitte ainult veebipõhistes rakendustes, mis aktsepteerivad ainult serveripõhiseid konnektoreid (hosted connectors).
- **Sellel pole andmebaasi.** Iga otsing läheb reaalajas avaldaja enda veebisaidile või API-sse, nii et
  tulemused on sama ajakohased kui allikas ja otsingu kvaliteet on allika enda oma. Kureeritud indeksis
  semantilist otsingut ei ole.
- **See ei sea kasutuspiirangut.** Fontesel ei ole igakuist päringute ülempiiri. See hajutab oma päringuid igale
  veebisaidile ja mõned allikad piiravad, kui kiiresti või kui sageli neilt päringuid teha saab.
- **See on avatud lähtekoodiga.** Saate lugeda iga adapterit ja näha täpselt, kust iga tekst pärineb.
- **Selle taga ei ole tarnijat.** Ei lepingut, kasutajatuge ega tööaja lubadust (vt „Kes
  seda haldab?“).

## Milliste rakenduste ja süsteemidega see töötab?

Iga MCP-rakendusega, mis suudab käivitada kohalikku (stdio) serverit, näiteks Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio ja Cline. Fontes
töötab macOS-is, Windowsis ja Linuxis, kõikjal, kus töötab uv (Python 3.13+). Macis või Windowsi arvutis
seadistab ühe klõpsuga paigaldaja korraga Claude Desktopi, Codexi, Claude Code'i, Cursori, VS Code'i, Windsurfi, Gemini CLI, Zedi, LM Studio ja
Cline'i. Sammud iga rakenduse jaoks: [INSTALL.md](INSTALL.md).

## Kas ma saan koodi panustada?

Praegu mitte. Issue'd, allikateated ja jurisdiktsioonisoovid on teretulnud. Vt
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
