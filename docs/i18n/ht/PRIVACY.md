> Sa a se yon tradiksyon ki fèt avèk èd machin. Se vèsyon angle a ki fè lafwa.

# Avi sou vi prive Fontes

Fontes mache sou òdinatè ou. Rechèch ou yo ak dokiman ou louvri yo rete ant òdinatè ou, sous ofisyèl ou
fè rechèch ladan yo, ak aplikasyon IA w ap sèvi a (dapre pwòp kondisyon aplikasyon sa a). Fontes li menm
pa voye **anyen pa defo** bay devlopè Fontes yo.

## Sa ki ka soti sou òdinatè ou, ak ki lè

**1. Verifikasyon mizajou (limen pa defo).** Yon fwa pa jou, Fontes mande PyPI, endèks piblik pakè
Python yo, ki dènye vèsyon an. Demann lan pa gen anyen sou ou oswa sou travay ou; PyPI wè adrès IP ou,
tankou pou nenpòt telechajman. Pou etenn li, mete `FONTES_NO_UPDATE_CHECK=1` (avi nan aplikasyon an) ak
`FONTES_NO_AUTO_UPDATE=1` (mizajou otomatik enstalatè a).

**2. Kantite itilizasyon (etenn sof si ou limen yo).** Si ou dakò (opt-in), yon fwa pa jou Fontes voye:

- vèsyon Fontes la ak fanmi sistèm operasyon ou (macOS, Windows, Linux);
- pou chak jou, konbyen fwa yo te sèvi ak chak zouti pou chak kòd jiridiksyon, pa egzanp
  "2026-11-10, nl, search_caselaw, 12".

Se tout mesaj la sa. Li pa janm gen rechèch ou yo, idantifyan dokiman oswa dosye, tèks dokiman, non ou,
yon kont, oswa okenn idantifyan pou ou oswa pou òdinatè ou. Kantite yo tann sou òdinatè ou (nan dosye
kach Fontes la, `stats.json`) jiskaske yo voye; si voye a echwe, yo tann jiska nan demen.

- **Limen (opt-in)**: reponn "wi" lè enstalatè a mande w, oswa mete `FONTES_STATS=1` pou sèvè Fontes la.
- **Etenn (opt-out)**: lanse enstalatè a ankò epi peze Enter nan kesyon sa a, oswa retire
  `FONTES_STATS`. Si ou efase `stats.json`, sa retire tout sa ki poko voye.

**3. Rapò erè (sèlman lè ou voye youn).** Lè ou mande youn (`fontes report-bug`, oswa ou mande aplikasyon
IA ou a pou rapòte yon erè Fontes), Fontes montre w tout rapò a anvan, epi li voye l sèlman si ou konfime.
Li gen vèsyon Fontes la, fanmi sistèm operasyon ou, kòd jiridiksyon an, non zouti a ak mesaj erè dènye
apèl ki te echwe a (san tèm rechèch ak idantifyan yo), ak yon nòt si ou ekri youn. Pa mete done kliyan nan
nòt la. Pou sa, Fontes kenbe dènye erè a sou òdinatè ou (`last-error.json` nan dosye kach li, ki ranplase
chak fwa); li pa janm voye apa.

## Ki kote li ale ak konbyen tan yo kenbe l

Kantite itilizasyon ak rapò erè ale sou yon ti sèvè devlopè Fontes la jere (`relay.kinetra.fit`). Li pa
estoke adrès IP: yo sèvi ak yo sèlman nan memwa, pou yon ti tan, pou bloke twòp demann, e sèvè entènèt la
pa kenbe okenn jounal aksè pou li. Kantite yo mete ansanm an total pa jou; yo pa kenbe chak voye apa. Yo
kenbe total yo jiska 2 an, rapò erè yo jiska 1 an, epi apre sa yo efase yo. Anyen pa vann ni pataje.

Si yo pa ka jwenn sèvè sa a, anyen pa voye: kantite yo rete sou òdinatè ou, e rapò erè yo voye w sou
sistèm swivi pwoblèm yo (issue tracker) pito.

## Kiyès ki responsab, e sou ki baz

Moun ki responsab done yo (controller) pou kantite itilizasyon ak rapò erè se Yüce Karapazar, devlopè
Fontes la. Kontak: fontesmcp@proton.me.

Baz legal la se konsantman ou (atik 6(1)(a) UK GDPR ak GDPR Inyon Ewopeyen an). Kantite itilizasyon voye
sèlman si ou dakò (opt-in), e yon rapò erè sèlman apre ou konfime l. Ou ka retire konsantman ou nenpòt ki
lè lè ou etenn li jan sa eksplike pi wo a; sa pa chanje sa ki te deja voye.

## Kontak

Kesyon oswa demann: voye yon imèl bay fontesmcp@proton.me oswa louvri yon issue nan
<https://github.com/ykarapazar/fontes/issues>.
