> Tai vertimas, parengtas padedant mašininiam vertimui. Autentiška yra versija anglų kalba.

# Fontes privatumo pranešimas

Fontes veikia jūsų kompiuteryje. Jūsų paieškos ir atidaryti dokumentai lieka tarp jūsų
kompiuterio, šaltinių, kuriuose ieškote (oficialių, taip pat CourtListener ir Lexifina, kai jais naudojatės; žr. toliau), ir jūsų naudojamos DI programos (pagal tos
programos sąlygas). Pats Fontes pagal numatytuosius nustatymus Fontes kūrėjams **nieko
nesiunčia**.

## Kas gali palikti jūsų kompiuterį ir kada

**1. Atnaujinimų patikra (pagal numatytuosius nustatymus įjungta).** Kartą per dieną Fontes
paklausia PyPI – viešojo Python paketų katalogo, – kuri versija yra naujausia. Užklausoje nėra
nieko apie jus ar jūsų darbą; PyPI mato jūsų IP adresą, kaip ir atsisiunčiant bet ką. Norėdami
tai išjungti, nustatykite `FONTES_NO_UPDATE_CHECK=1` (pranešimas programoje) ir
`FONTES_NO_AUTO_UPDATE=1` (diegimo programos automatiniai atnaujinimai).

**2. Naudojimo skaičiai (išjungti, nebent juos įjungsite).** Jei sutinkate (opt-in), kartą per
dieną Fontes siunčia:

- Fontes versiją ir jūsų operacinės sistemos šeimą (macOS, Windows, Linux);
- kiekvienai dienai – kiek kartų kiekvienas įrankis buvo naudotas kiekvienam jurisdikcijos
  kodui, pavyzdžiui, „2026-11-10, nl, search_caselaw, 12“.

Tai visas pranešimas. Jame niekada nėra jūsų paieškų, dokumentų ar bylų identifikatorių,
dokumentų teksto, jūsų vardo, paskyros ar kokio nors jūsų ar jūsų kompiuterio identifikatoriaus.
Skaičiai laukia jūsų kompiuteryje (Fontes talpyklos aplanke, `stats.json`), kol bus išsiųsti; jei
išsiųsti nepavyksta, jie laukia kitos dienos.

- **Sutikti (opt-in)**: atsakykite „y“, kai diegimo programa paklaus, arba nustatykite
  `FONTES_STATS=1` Fontes serveriui.
- **Atsisakyti (opt-out)**: dar kartą paleiskite diegimo programą ir prie šio klausimo
  paspauskite Enter arba pašalinkite `FONTES_STATS`. Ištrynus `stats.json`, panaikinama viskas,
  kas dar neišsiųsta.

**3. Klaidų ataskaitos (tik kai patys išsiunčiate).** Kai jos paprašote (`fontes report-bug` arba
paprašote savo DI programos pranešti apie Fontes klaidą), Fontes pirmiausia parodo jums visą
ataskaitą ir išsiunčia ją tik jums patvirtinus. Joje yra Fontes versija, jūsų operacinės
sistemos šeima, paskutinio nepavykusio įrankio iškvietimo jurisdikcijos kodas, įrankio
pavadinimas ir klaidos pranešimas (pašalinus jūsų paieškos žodžius ir identifikatorius), taip pat
pastaba, jei ją parašote. Nerašykite pastaboje klientų duomenų. Tam palaikyti Fontes jūsų
kompiuteryje saugo paskutinę klaidą (`last-error.json` savo talpyklos aplanke, kaskart
pakeičiamą); ji niekada nesiunčiama atskirai.

**4. Lexifina (įjungta pagal numatytuosius nustatymus).** `get_law_on_date`, `get_law_history`, 91 šalis ir Indijos aktai skaitomi per Lexifina teisės duomenų rinkinį, todėl jie siunčiami į Lexifina kartu su oficialia svetaine arba vietoj jos. Jūsų paieškos žodžiai,
citatos ir datos siunčiami į Lexifina nemokamą serverį `global-law.lexifina.com`, kurį valdo Lexifina, o ne
Fontes kūrėjai. Lexifina dokumentuoja, kad jos serveris registruoja, kuris įrankis buvo iškviestas ir kiek
laiko tai užtruko, bet niekada – ko buvo klausiama; Fontes to patikrinti negali, taikomos pačios Lexifina
sąlygos. Lexifina mato jūsų IP adresą, kaip ir bet kuris interneto serveris. Norėdami visiškai išjungti
Lexifina, nustatykite `WLM_LEXIFINA=0`; tuomet tie du įrankiai ir šalys nustoja veikti ir niekas į ją
nesiunčiama.

## Kur tai siunčiama ir kiek laiko saugoma

Naudojimo skaičiai ir klaidų ataskaitos siunčiami į nedidelį serverį, kurį valdo Fontes kūrėjas
(`relay.kinetra.fit`). Jis nesaugo IP adresų: jie naudojami tik atmintyje, trumpai, siekiant
sustabdyti užklausų antplūdžius, o žiniatinklio serveris jam nesaugo prieigos žurnalo. Skaičiai
sudedami į dienos sumas; atskiri pateikimai nesaugomi. Sumos saugomos iki 2 metų, klaidų
ataskaitos – iki 1 metų, tada ištrinamos. Niekas neparduodama ir niekam neperduodama.

Jei to serverio pasiekti nepavyksta, niekas nesiunčiama: skaičiai lieka jūsų kompiuteryje, o
klaidų ataskaitos vietoj to nukreipia jus į problemų sekimo sistemą (issue tracker).

## Kas atsakingas ir kokiu pagrindu

Naudojimo skaičių ir klaidų ataskaitų duomenų valdytojas yra Yüce Karapazar, Fontes kūrėjas.
Kontaktai: fontesmcp@proton.me.

Teisinis pagrindas yra jūsų sutikimas (JK BDAR ir ES BDAR 6 straipsnio 1 dalies a punktas).
Naudojimo skaičiai siunčiami tik jums sutikus, o klaidos ataskaita – tik jums ją patvirtinus.
Sutikimą galite bet kada atšaukti, atsisakydami, kaip aprašyta aukščiau; tai neturi įtakos
tam, kas buvo išsiųsta anksčiau.

## Kontaktai

Klausimai ar prašymai: rašykite fontesmcp@proton.me arba atidarykite pranešimą (issue) adresu
<https://github.com/ykarapazar/fontes/issues>.
