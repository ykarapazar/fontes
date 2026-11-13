> Iyi ni inyandiko yahinduwe hifashishijwe imashini. Inyandiko y'Icyongereza ni yo ifite agaciro.

# Itangazo rya Fontes ku buzima bwite

Fontes ikorera kuri mudasobwa yawe. Ibyo ushakisha n'inyandiko ufungura biguma hagati ya mudasobwa yawe,
inkomoko za Leta ushakishamo, na porogaramu ya AI ukoresha (hakurikijwe amabwiriza y'iyo porogaramu
ubwayo). Fontes ubwayo ntiyoherereza abakora Fontes **ikintu na kimwe mu buryo busanzwe**.

## Ibishobora kuva kuri mudasobwa yawe, n'igihe

**1. Kugenzura ivugurura (birafunguye mu buryo busanzwe).** Rimwe ku munsi, Fontes ibaza PyPI, ububiko
rusange bw'amapaki ya Python, verisiyo nshya kurusha izindi. Ubwo busabe nta kintu bukwerekeyeho cyangwa
cyerekeye akazi kawe bufite; PyPI ibona aderesi IP yawe, nk'uko bigenda ku gukuramo ikintu icyo ari cyo
cyose. Kugira ngo ubihagarike, shyiraho `FONTES_NO_UPDATE_CHECK=1` (itangazo riri muri porogaramu) na
`FONTES_NO_AUTO_UPDATE=1` (ivugurura ryikora rya porogaramu yo gushyiraho).

**2. Imibare y'ikoreshwa (birafunze keretse ubifunguye).** Niba ubyemeye (opt-in), rimwe ku munsi Fontes
yohereza:

- verisiyo ya Fontes n'ubwoko bwa sisitemu y'imikorere yawe (macOS, Windows, Linux);
- kuri buri munsi, inshuro buri gikoresho cyakoreshejwe kuri buri kode y'ifasi y'ubutabera, urugero
  "2026-11-10, nl, search_caselaw, 12".

Ubwo ni bwo butumwa bwose. Ntibujya burimo ibyo washakishije, ibiranga inyandiko cyangwa imanza,
inyandiko ubwazo, izina ryawe, konti, cyangwa ikiranga icyo ari cyo cyose cyawe cyangwa cya mudasobwa
yawe. Imibare itegerereza kuri mudasobwa yawe (mu bubiko bwa cache bwa Fontes, `stats.json`) kugeza
yoherejwe; iyo kohereza binaniranye, itegereza umunsi ukurikira.

- **Kubyemera (opt-in)**: subiza "yego" iyo porogaramu yo gushyiraho ikubajije, cyangwa ushyireho
  `FONTES_STATS=1` kuri seriveri ya Fontes.
- **Kubyanga (opt-out)**: ongera ukoreshe porogaramu yo gushyiraho ukande Enter kuri icyo kibazo,
  cyangwa ukureho `FONTES_STATS`. Gusiba `stats.json` bikuraho ibitaroherezwa byose.

**3. Raporo z'amakosa (gusa iyo wohereje imwe).** Iyo uyisabye (`fontes report-bug`, cyangwa usabye
porogaramu yawe ya AI gutangaza ikosa rya Fontes), Fontes ibanza kukwereka raporo yose, kandi
iyohereza gusa iyo ubyemeje. Irimo verisiyo ya Fontes, ubwoko bwa sisitemu y'imikorere yawe, kode y'ifasi
y'ubutabera, izina ry'igikoresho n'ubutumwa bw'ikosa by'ihamagara riheruka ryananiranye (amagambo
washakishije n'ibiranga byakuwemo), n'inyandiko (note) niba wanditse. Ntugashyire amakuru y'umukiliya
muri iyo note. Kugira ngo ibi bishoboke, Fontes ibika ikosa riheruka kuri mudasobwa yawe (`last-error.json`
mu bubiko bwayo bwa cache, risimburwa buri gihe); ntirijya ryoherezwa ryonyine.

## Aho bijya n'igihe bibikwa

Imibare y'ikoreshwa na raporo z'amakosa bijya kuri seriveri ntoya icungwa n'ukora Fontes
(`relay.kinetra.fit`). Ntibika aderesi IP: zikoreshwa gusa mu bubiko bw'agateganyo (memory), mu gihe
gito, kugira ngo hahagarikwe ubusabe bwinshi bukabije, kandi seriveri y'urubuga ntibika access log
yayo. Imibare ihurizwa mu mibare rusange ya buri munsi; ibyoherejwe kimwe kimwe ntibibikwa. Imibare
rusange ibikwa kugeza ku myaka 2, raporo z'amakosa kugeza ku mwaka 1, hanyuma bigasibwa. Nta kigurishwa
cyangwa ngo gisangizwe.

Niba iyo seriveri itagerwaho, nta kintu cyoherezwa: imibare iguma kuri mudasobwa yawe, kandi raporo
z'amakosa zikakwerekeza kuri issue tracker aho kubyohereza.

## Ubishinzwe, n'ishingiro ry'amategeko

Ugenzura amakuru (controller) ku mibare y'ikoreshwa na raporo z'amakosa ni Yüce Karapazar, ukora
Fontes. Aho wamugera: fontesmcp@proton.me.

Ishingiro ry'amategeko ni uburenganzira utanga (consent) (Ingingo ya 6(1)(a) ya UK GDPR na GDPR
y'Umuryango w'u Burayi). Imibare y'ikoreshwa yoherezwa gusa iyo wabyemeye (opt-in), na raporo y'ikosa
gusa umaze kuyemeza. Ushobora gukuraho uburenganzira watanze igihe icyo ari cyo cyose ubyanga nk'uko
byasobanuwe haruguru; ibi ntibigira ingaruka ku byari byaramaze koherezwa.

## Aho twabonekera

Ibibazo cyangwa ibyifuzo: andikira fontesmcp@proton.me, cyangwa ufungure issue kuri
<https://github.com/ykarapazar/fontes/issues>.
