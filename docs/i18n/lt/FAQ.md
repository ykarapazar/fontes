> Tai vertimas, parengtas padedant mašininiam vertimui. Autentiška yra versija anglų kalba.

# Fontes: klausimai ir atsakymai

## Kas yra Fontes?

Nemokamas atvirojo kodo MCP serveris (Apache 2.0). Jis leidžia bet kuriai programai, palaikančiai
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI ir kitoms), tiesiogiai ieškoti
teismų sprendimų ir teisės aktų teismų ir valstybės institucijų svetainėse 120+ jurisdikcijų ir
tarptautinių teismų (124 adapteriai). Kiekvienas rezultatas nurodo savo šaltinį ir pateikia
nuorodą į originalą.

## Ar tekstai oficialūs?

Dažniausiai taip, bet ne visada.

- Daugumą šaltinių administruoja teismas, ministerija arba oficialusis leidinys.
- Kai kuriuos suvestinės redakcijos tekstus skelbia vyriausybė, tačiau jie yra aiškiai
  neoficialūs: autentiškas tik oficialusis leidinys.
- Keli šaltiniai apskritai nėra valstybinės svetainės (pavyzdžiui, LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes prie kiekvieno atsakymo, gauto iš vieno iš šių šaltinių, prideda pastabą „Unofficial
source“. Prieš ką nors cituodami, patikrinkite oficialųjį leidinį. Aprėpties lentelė
[README](README.md#aprėptis) ir `list_jurisdictions` nurodo kiekvienos jurisdikcijos šaltinį.

## Kurias jurisdikcijas aprėpia ir kaip gerai?

124 adapteriai: 108 JT valstybės narės, Honkongas, Kosovas, Palestina, Taivanas, DIFC Courts ir
11 tarptautinių teismų ir institucijų (pavyzdžiui, Europos Žmogaus Teisių Teismas, ES,
Tarptautinis Teisingumo Teismas ir PPO).

Aprėptis labai skiriasi. Pagal griežtą taisyklę (aukščiausiojo bendrosios kompetencijos teismo
precedentai arba konstitucija ir pagrindiniai įstatymai, pasiekti visa apimtimi) aprėptomis
laikomos 72 iš 124. [COVERAGE.md](../../COVERAGE.md) kiekvienai jurisdikcijai nurodo, ką Fontes
pasiekia, ko nepasiekia ir kodėl.

## Ar man reikia API rakto?

Beveik visoms jurisdikcijoms – ne. Kai kuriems šaltiniams reikia nemokamo rakto: žr.
[KEYS.md](KEYS.md).

- **Prancūzija:** taip. Prancūzija išjungta, kol nenustatote `WLM_FR_PISTE_CLIENT_ID` ir
  `WLM_FR_PISTE_CLIENT_SECRET`. Juos gausite iš nemokamos PISTE paskyros (piste.gouv.fr) su
  programa, užsiprenumeravusia Judilibre ir Légifrance.
- **Jungtinės Valstijos:** neprivaloma. Teismų praktikos paieška veikia be rakto, tačiau bendras
  demonstracinis raktas leidžia tik apie 10 paieškų per dieną vienam IP adresui. Nemokamas
  api.data.gov raktas kintamajame `WLM_US_GOVINFO_KEY` šią ribą padidina.

Nustatykite juos kaip Fontes serverio aplinkos kintamuosius savo programos MCP nustatymuose. Kai
bus išleista diegimo programa, ji jų paklaus po diegimo, o jos paleidiklis **Add or change keys**
leis juos pakeisti vėliau.

Atskirai: kelių šaltinių sąlygose nurodyta, kad automatizuotai prieigai reikia leidėjo leidimo.
Jie pažymėti OFF ir lieka išjungti. Raktas to nepakeičia; tai pakeičia tik leidėjo leidimas
(tada nustatykite `WLM_PERMITTED=<codes>`).

## Kas palieka mano kompiuterį?

Jūsų paieškos siunčiamos tik į ieškomą šaltinį. Fontes nesaugo duomenų bazės ir jam nereikia
paskyros.

Be šaltinių, Fontes kartą per dieną paklausia PyPI, ar yra naujesnė versija (išjungiama nustačius
`FONTES_NO_UPDATE_CHECK=1`). Naudojimo skaičiai išjungti, nebent juos įjungsite, o klaidos
ataskaita išsiunčiama tik jums ją pamačius ir patvirtinus. Jūsų DI programa mato jūsų pokalbį
pagal savo sąlygas.

Visa informacija: [PRIVACY.md](PRIVACY.md).

## Ar tai teisinė konsultacija?

Ne. Fontes yra tyrimų įrankis. Jis randa tekstus; jis nepasako, ką jie reiškia jūsų bylai, o jo
naudojimas nesukuria advokato ir kliento santykių su niekuo. DI programa gali klaidingai
perskaityti tekstą, todėl prieš remdamiesi perskaitykite visą sprendimą ar nuostatą. Dėl
konsultacijos kreipkitės į advokatą, turintį kvalifikaciją toje vietoje, kur kyla jūsų
klausimas.

## Kas jį prižiūri? Ar jis toliau veiks?

Vienas žmogus: Yüce Karapazar. Už Fontes nėra jokios įmonės, jokios palaikymo sutarties ir jokio
paslaugų lygio pažado. Teisinės paslaugos neteikiamos.

Šaltiniai tikrinami kartą per dieną, o rezultatai skelbiami
[būsenos puslapyje](https://ykarapazar.github.io/fontes/status/?lang=lt). Teismų ir valstybės
institucijų svetainės keičiasi be įspėjimo, todėl šaltinis gali sugesti bet kada. Nėra jokios
garantijos, kad kuris nors šaltinis ar pats Fontes toliau veiks. Fontes teikiamas „tokia, kokia
yra“ („as is“), be garantijų ([LICENSE](../../../LICENSE) 7 ir 8 skirsniai).

## Tekstas klaidingas, pasenęs arba šaltinis neveikia. Kaip apie tai pranešti?

- Atidarykite pranešimą (issue) su forma „Broken or wrong source“:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Nurodykite, kuri jurisdikcija, ko
  klausėte, ką gavote ir oficialų puslapį, kuriame matyti teisingas tekstas.
- Arba paprašykite savo DI programos „pranešti apie Fontes klaidą“ (arba paleiskite
  `fontes report-bug`). Ataskaitą pamatysite, prieš ką nors išsiunčiant.
- Arba rašykite fontesmcp@proton.me.

Neįtraukite į ataskaitą klientų duomenų ar konfidencialių faktų.

**Jei administruojate vieną iš šaltinių** ir kas nors negerai (jūsų sąlygos, robots.txt, užklausų
ribos), rašykite fontesmcp@proton.me. Šaltinis bus pataisytas arba išjungtas.

## Kuo Fontes skiriasi nuo debesyje veikiančių teisinių tyrimų įrankių?

- **Jis veikia jūsų kompiuteryje.** Nėra Fontes serverio ir paskyros. Tai taip pat reiškia, kad
  jis veikia tik programose, galinčiose paleisti vietinį MCP serverį (Claude Desktop, Codex,
  Cursor, VS Code ir panašiose), o ne vien žiniatinklio programose, priimančiose tik debesyje
  veikiančias jungtis.
- **Jis neturi duomenų bazės.** Kiekviena paieška tiesiogiai siunčiama į paties leidėjo svetainę
  ar API, todėl rezultatai tokie pat aktualūs kaip šaltinis, o paieškos kokybė yra paties
  šaltinio. Nėra semantinės paieškos atrinktame indekse.
- **Jis nenustato naudojimo ribos.** Fontes neturi mėnesinės iškvietimų ribos. Jis išdėsto savo
  užklausas kiekvienai svetainei laike, o kai kurie šaltiniai riboja, kaip greitai ar kaip dažnai
  galima jų užklausti.
- **Jis atvirojo kodo.** Galite perskaityti kiekvieną adapterį ir tiksliai matyti, iš kur
  gaunamas kiekvienas tekstas.
- **Už jo nėra tiekėjo.** Nėra sutarties, pagalbos tarnybos ar veikimo laiko pažado (žr. „Kas jį
  prižiūri?“).

## Su kokiomis programomis ir sistemomis jis veikia?

Su bet kuria MCP programa, galinčia paleisti vietinį (stdio) serverį, pavyzdžiui, Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio ir
Cline. Fontes veikia macOS, Windows ir Linux sistemose, visur, kur veikia uv (Python 3.13+). Jo
dar nėra PyPI; kai jis ten atsiras, daugumai programų reikės vienos komandos arba vieno
konfigūracijos įrašo, o Claude Desktop priima dukart spustelėjamą `.mcpb` failą. Diegimo
programa vienu spustelėjimu, skirta Mac ir Windows, netrukus bus išleista. Ji vienu kartu
nustato Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio
ir Cline. Kiekvienos programos veiksmai: [INSTALL.md](INSTALL.md).

## Ar galiu prisidėti kodu?

Šiuo metu ne. Pranešimai (issues), pranešimai apie šaltinius ir jurisdikcijų prašymai laukiami.
Žr. [CONTRIBUTING.md](../../../CONTRIBUTING.md).
