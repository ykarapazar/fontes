> Toto je strojovo podporovaný preklad. Rozhodujúce je anglické znenie.

# Informácie o ochrane súkromia Fontes

Fontes beží vo vašom počítači. Vaše vyhľadávania a dokumenty, ktoré otvoríte, zostávajú medzi
vaším počítačom, zdrojmi, ktoré prehľadávate (oficiálnymi, plus CourtListener a Lexifina tam, kde ich používate;
pozri nižšie), a AI aplikáciou, ktorú používate (podľa
vlastných podmienok tejto aplikácie). Samotný Fontes vývojárom Fontes **predvolene neodosiela
nič**.

## Čo môže opustiť váš počítač a kedy

**1. Kontrola aktualizácií (predvolene zapnutá).** Raz denne sa Fontes opýta PyPI, verejného
registra balíkov Pythonu, ktorá verzia je najnovšia. Požiadavka neobsahuje nič o vás ani o vašej
práci; PyPI vidí vašu IP adresu ako pri každom sťahovaní. Ak ju chcete vypnúť, nastavte
`FONTES_NO_UPDATE_CHECK=1` (upozornenie v aplikácii) a `FONTES_NO_AUTO_UPDATE=1` (automatické
aktualizácie inštalátora).

**2. Počty použití (vypnuté, pokiaľ ich nezapnete).** Ak s tým súhlasíte (opt-in), Fontes raz
denne odošle:

- verziu Fontes a rodinu vášho operačného systému (macOS, Windows, Linux);
- za každý deň, koľkokrát sa každý nástroj použil pre každý kód jurisdikcie, napríklad
  „2026-11-10, nl, search_caselaw, 12“.

To je celá správa. Nikdy neobsahuje vaše vyhľadávania, identifikátory dokumentov alebo vecí, text
dokumentov, vaše meno, účet ani žiadny identifikátor vás alebo vášho počítača. Počty čakajú vo
vašom počítači (v priečinku vyrovnávacej pamäte Fontes, `stats.json`), kým sa neodošlú; ak
odoslanie zlyhá, čakajú do ďalšieho dňa.

- **Prihlásenie (opt-in)**: odpovedzte „a“, keď sa inštalátor opýta, alebo nastavte
  `FONTES_STATS=1` pre server Fontes.
- **Odhlásenie (opt-out)**: spustite inštalátor znova a pri tejto otázke stlačte Enter, alebo
  odstráňte `FONTES_STATS`. Vymazaním `stats.json` zahodíte všetko, čo ešte nebolo odoslané.

**3. Hlásenia chýb (iba keď nejaké odošlete).** Keď o ne požiadate (`fontes report-bug` alebo
požiadate svoju AI aplikáciu, aby nahlásila chybu vo Fontes), Fontes vám najprv ukáže celé
hlásenie a odošle ho iba vtedy, ak to potvrdíte. Obsahuje verziu Fontes, rodinu vášho
operačného systému, pri poslednom neúspešnom volaní nástroja kód jurisdikcie, názov nástroja a
chybové hlásenie (s odstránenými slovami vášho vyhľadávania a identifikátormi) a poznámku, ak
nejakú napíšete. Do poznámky neuvádzajte údaje o klientoch. Na tento účel Fontes uchováva
poslednú chybu vo vašom počítači (`last-error.json` v priečinku vyrovnávacej pamäte, zakaždým
nahradený); nikdy sa neodosiela samostatne.

**4. Lexifina (predvolene zapnuté).** `get_law_on_date`, `get_law_history`, 91 krajín a indické zákony sa čítajú zo záznamu práva Lexifina, takže idú k Lexifine rovnako ako na oficiálnu stránku, alebo namiesto nej. Vaše hľadané slová, citácie a dátumy smerujú
na bezplatný server Lexifiny, `global-law.lexifina.com`, ktorý prevádzkuje Lexifina, nie vývojári
Fontes. Lexifina dokumentuje, že jej server zaznamenáva, ktorý nástroj bol volaný a ako dlho trval,
nikdy nie to, čo sa pýtalo; Fontes to nedokáže overiť a platia podmienky samotnej Lexifiny. Lexifina
vidí vašu IP adresu, ako každý webový server. Ak chcete Lexifinu úplne vypnúť, nastavte
`WLM_LEXIFINA=0`; tieto dva nástroje a krajiny potom prestanú fungovať a nič sa tam neodošle.

## Kam to smeruje a ako dlho sa to uchováva

Počty použití a hlásenia chýb smerujú na malý server prevádzkovaný vývojárom Fontes
(`relay.kinetra.fit`). Neukladá žiadne IP adresy: používajú sa iba v pamäti, krátko, na
zastavenie zahltenia, a webový server preň nevedie žiadny prístupový záznam (access log). Počty
sa sčítavajú do denných súhrnov; jednotlivé podania sa neuchovávajú. Súhrny sa uchovávajú
najviac 2 roky, hlásenia chýb najviac 1 rok, potom sa vymažú. Nič sa nepredáva ani
nesprístupňuje ďalej.

Ak tento server nie je dostupný, nič sa neodošle: počty zostanú vo vašom počítači a hlásenia
chýb vás namiesto toho odkážu na systém evidencie problémov (issue tracker).

## Kto zodpovedá a na akom právnom základe

Prevádzkovateľom pre počty použití a hlásenia chýb je Yüce Karapazar, vývojár Fontes. Kontakt:
fontesmcp@proton.me.

Právnym základom je váš súhlas (článok 6 ods. 1 písm. a) UK GDPR a GDPR EÚ). Počty použití sa
odosielajú iba vtedy, ak s tým súhlasíte (opt-in), a hlásenie chyby až po tom, čo ho potvrdíte.
Súhlas môžete kedykoľvek odvolať odhlásením, ako je opísané vyššie; nemá to vplyv na to, čo bolo
odoslané predtým.

## Kontakt

Otázky alebo žiadosti: napíšte na fontesmcp@proton.me alebo otvorte issue na
<https://github.com/ykarapazar/fontes/issues>.
