> Lii ab tekki la bu masin dimbali. Mbind mu Àngale mi moo am sañ-sañ.

# Yégleb sutura bu Fontes

Fontes ci sa ordinatëer lay dox. Say gëstu ak dokimaŋ yi ngay ubbi dañuy des ci diggante sa ordinatëer,
cosaan yi ngay wut (yu Nguur gi, ak CourtListener ak Lexifina su ngay jëfandikoo leen, xoolal ci suuf), ak
aplikasioŋ AI bi ngay jëfandikoo (ci sàrti aplikasioŋ boobu ci boppam).
Fontes ci boppam du yónne defarkati Fontes yi **dara ci njëlbéen**.

## Lan mën a génn ci sa ordinatëer, ak kañ

**1. Saytu yeesal (taal na ci njëlbéen).** Benn yoon ci bés bi, Fontes dafay laaj PyPI, limu pakaasu
Python yu ñépp mën a gis, ban sumb moo gën a bees. Laaj bi amul dara ci yaw walla ci sa liggéey; PyPI dafay
gis sa adrees IP, ni ci bépp yeb. Ngir fey ko, defal `FONTES_NO_UPDATE_CHECK=1` (yégle bi ci biir
aplikasioŋ bi) ak `FONTES_NO_AUTO_UPDATE=1` (yeesal yu boppam yu programu samp bi).

**2. Limu jëfandikoo (fey nañu lu dul nga taal leen).** Su nga nangoo (opt-in), benn yoon ci bés bi
Fontes dafay yónne:

- sumbu Fontes bi ak njabootu sistem bu sa ordinatëer (macOS, Windows, Linux);
- ci bés bu nekk, ñaata yoon lañu jëfandikoo jumtukaay bu nekk ci kood juridiction bu nekk, misaal
  "2026-11-10, nl, search_caselaw, 12".

Loolu mooy bataaxal bi bépp. Du mukk am say gëstu, xàmmeekaayu dokimaŋ walla mbir, mbindu dokimaŋ, sa tur,
benn kontu, walla benn xàmmeekaay ci yaw walla ci sa ordinatëer. Lim yi dañuy xaar ci sa ordinatëer (ci
kàggu cache bu Fontes, `stats.json`) ba ñu leen yónne; su yónne bi antuwul, dañuy xaar ba ëllëg.

- **Nangu (opt-in)**: tontul "waaw" bu programu samp bi la laajee, walla defal `FONTES_STATS=1` ngir
  serwëer Fontes bi.
- **Bañ (opt-out)**: doxalaatal programu samp bi te bës Enter ci laaj boobu, walla dindi
  `FONTES_STATS`. Far `stats.json` dafay far lépp lu ñu yónneegul.

**3. Yégle njuumte (bu nga ci yónnee benn rekk).** Bu nga ko laajee (`fontes report-bug`, walla nga laaj
sa aplikasioŋ AI mu yégle njuumte ci Fontes), Fontes dafay la won yégle bi bépp jëkk, te du ko yónne lu
dul nga dëggal ko. Dafay am sumbu Fontes bi, njabootu sistem bu sa ordinatëer, kood juridiction, turu
jumtukaay ak bataaxalu njuumte bu woote jumtukaay bu mujj bu antuwul (ñu dindi ci say baatu gëstu ak say
xàmmeekaay), ak ab nót su nga ci bindee benn. Bul def ci nót bi xibaaru kiliyaan. Ngir lii, Fontes dafay
denc njuumte bu mujj bi ci sa ordinatëer (`last-error.json` ci kàggu cache-am, ñu koy wuutal saa su ne);
du mukk ko yónne moom kese.

**4. Lexifina (taal na ci njëlbéen).** `get_law_on_date`, `get_law_history`, 91 réew yi ak Acts yu Inde ñu jàng ci mbind mu Lexifina ci yoon, ñu dem ci Lexifina, ak sit bu Nguur gi walla ci kanam loolu. Sa baat yi, sa citation yi ak sa bés yi dañu dem ci serwëer bu free
bu Lexifina, `global-law.lexifina.com`, bu Lexifina moo ko defar, du ci defarkati Fontes. Lexifina dafay wax ne
serwëeru ko dafay bind ban jumtukaay la woo ak ban waxtu la ko jeexal, waaye du mukk lu ñu laaj; Fontes manul a
seetaan loolu, te sàrti Lexifina ci boppam a jëfandikoo. Lexifina dafay gis sa adrees IP, ni ci serwëeri web yépp.
Ngir tëj Lexifina bës tërëb, defal `WLM_LEXIFINA=0`; ginnaaw loolu, jumtukaay ñaar yooyu ak réew yooyu dinañu bàyyi
liggéey, te dara du dem fa.

## Fu muy dem ak ñaata diir lañu koy denc

Limu jëfandikoo yi ak yégle njuumte yi dañuy dem ci ab serwëer bu tuuti bu defarkatu Fontes bi di
yor (`relay.kinetra.fit`). Du denc benn adrees IP: ci biir memoire rekk lañu leen jëfandikoo, ci benn
diir bu gàtt, ngir tere laaj yu bare lool, te serwëer web bi du denc benn journal d'accès ngir moom. Lim yi
dañu leen di boole ci ay mbooloo bés bu nekk; duñu denc yónne yu nekk benn-benn. Mbooloo yi dañu leen di
denc ba 2 at, yégle njuumte yi ba 1 at, te ginnaaw loolu dañu leen di far. Duñu jaay dara te duñu séddoo
dara.

Su ñu mënul a jot ci serwëer boobu, dara du dem: lim yi dañuy des ci sa ordinatëer te yégle njuumte yi
dañu lay yónnee ci issue tracker bi.

## Kan moo ci yore, te ci lan la sukkandiku

Ki yor done yi (controller) ngir limu jëfandikoo yi ak yégle njuumte yi mooy Yüce Karapazar, defarkatu
Fontes. Jokkoo: fontesmcp@proton.me.

Sukkandikukaayu yoon bi mooy sa nangu (Article 6(1)(a) bu UK GDPR ak GDPR bu Uniyoŋ Tugal). Limu
jëfandikoo yi su nga nangoo rekk lañuy dem (opt-in), te yégle njuumte ginnaaw bi nga ko dëggalee rekk. Mën
nga dindi sa nangu saa su la neexee ci bañ ni ñu ko wonee ci kaw; loolu du soppi li ñu yónne ba noppi.

## Jokkoo

Laaj walla sàkku: bindal ci fontesmcp@proton.me, walla ubbil ab issue ci
<https://github.com/ykarapazar/fontes/issues>.
