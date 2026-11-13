> Fandikan-teny natao tamin'ny fanampian'ny milina ity. Ny dikan-teny anglisy no manan-kery.

# Fampahafantarana momba ny fiainana manokana ao amin'ny Fontes

Mandeha ao amin'ny solosainao ny Fontes. Mijanona eo anelanelan'ny solosainao, ireo loharano ofisialy
karohinao, ary ny rindranasa AI ampiasainao (eo ambanin'ny fepetran'io rindranasa io manokana) ny
fikarohanao sy ireo antontan-taratasy sokafanao. Ny Fontes mihitsy dia **tsy mandefa na inona na inona raha
tsy misy fanovana** any amin'ireo mpamorona ny Fontes.

## Inona no mety hivoaka ny solosainao, ary rahoviana

**1. Fanamarinana fanavaozana (mandeha raha tsy misy fanovana).** Indray mandeha isan'andro, manontany ny
PyPI, ny lisitry ny fonosana Python ampahibemaso, ny Fontes hoe kinova inona no farany. Tsy mitondra na
inona na inona momba anao na ny asanao ilay fangatahana; hitan'ny PyPI ny adiresy IP-nao, toy ny amin'ny
fakana rehetra. Raha hamono azy, apetraho ny `FONTES_NO_UPDATE_CHECK=1` (ilay fampahafantarana ao amin'ny
rindranasa) sy ny `FONTES_NO_AUTO_UPDATE=1` (ny fanavaozana mandeha ho azy an'ny mpametraka).

**2. Isa fampiasana (maty raha tsy alefanao).** Raha manaiky (opt in) ianao, indray mandeha isan'andro ny
Fontes no mandefa:

- ny kinovan'ny Fontes sy ny fianakavian'ny rafitra fiasan'ny solosainao (macOS, Windows, Linux);
- isan'andro, impiry no nampiasaina ny fitaovana tsirairay ho an'ny kaodin'ny faritra ara-pitsarana
  tsirairay, ohatra "2026-11-10, nl, search_caselaw, 12".

Izay ihany ny hafatra manontolo. Tsy ahitana mihitsy ny fikarohanao, ny mari-pamantarana antontan-taratasy
na raharaha, ny lahatsoratry ny antontan-taratasy, ny anaranao, kaonty, na mari-pamantarana na inona na
inona ho anao na ho an'ny solosainao. Miandry ao amin'ny solosainao ireo isa (ao amin'ny lahatahiry cache
an'ny Fontes, `stats.json`) mandra-pandefasana azy; raha tsy nahomby ny fandefasana, miandry ny ampitso izy.

- **Opt in**: valio hoe "y" rehefa manontany ny mpametraka, na apetraho ny `FONTES_STATS=1` ho an'ny mpizara
  Fontes.
- **Opt out**: alefaso indray ny mpametraka ary tsindrio ny Enter amin'ilay fanontaniana, na esory ny
  `FONTES_STATS`. Ny famafana ny `stats.json` dia manary izay rehetra mbola tsy nalefa.

**3. Tatitra momba ny olana (rehefa alefanao ihany).** Rehefa angatahinao izany (`fontes report-bug`, na
angataho amin'ny rindranasa AI-nao ny hitaterana olana ao amin'ny Fontes), asehon'ny Fontes aminao aloha ny
tatitra feno ary alefany ihany raha manamafy ianao. Ahitana ny kinovan'ny Fontes izy, ny fianakavian'ny
rafitra fiasan'ny solosainao, ny kaodin'ny faritra ara-pitsarana, ny anaran'ny fitaovana sy ny hafatra
hadisoana amin'ny antso fitaovana farany tsy nahomby (nesorina ireo teny nokarohinao sy ireo
mari-pamantarana), ary fanamarihana raha nanoratra izany ianao. Aza mampiditra antsipirian'ny mpanjifa ao
amin'ilay fanamarihana. Mba hanohanana izany, tehirizin'ny Fontes ao amin'ny solosainao ny hadisoana farany
(`last-error.json` ao amin'ny lahatahiry cache-ny, soloina isaky ny mandeha); tsy alefa ho azy mihitsy izy.

## Aiza no alehany ary hafiriana no itahirizana azy

Mankany amin'ny mpizara kely tantanan'ny mpamorona ny Fontes (`relay.kinetra.fit`) ny isa fampiasana sy ny
tatitra momba ny olana. Tsy mitahiry adiresy IP izy: ampiasaina ao amin'ny fitadidiana ihany izy ireo, vetivety,
mba hanakanana ny fangatahana be loatra, ary tsy mitahiry diarin'ny fidirana (access logs) ho an'izany ny
mpizara tranonkala. Atambatra ho isa totaly isan'andro ireo isa; tsy tehirizina ny fandefasana tsirairay.
Tehirizina hatramin'ny 2 taona ny totaly, hatramin'ny 1 taona ny tatitra momba ny olana, dia fafana avy eo.
Tsy misy amidy na zaraina.

Raha tsy tratra io mpizara io, tsy misy alefa: mijanona ao amin'ny solosainao ireo isa ary ny tatitra momba
ny olana kosa mitondra anao any amin'ny issue tracker.

## Iza no tompon'andraikitra, ary mifototra amin'inona

Ny mpanara-maso ny angona (data controller) ho an'ny isa fampiasana sy ny tatitra momba ny olana dia Yüce
Karapazar, mpamorona ny Fontes. Fifandraisana: fontesmcp@proton.me.

Ny fanekenao (consent) no fototra ara-dalàna (Andininy 6(1)(a) amin'ny UK GDPR sy ny EU GDPR). Alefa ihany ny
isa fampiasana raha nanaiky (opt in) ianao, ary ny tatitra momba ny olana rehefa avy nanamafy azy ianao.
Azonao atao ny misintona ny fanekenao amin'ny fotoana rehetra amin'ny alalan'ny opt out araka ny voalaza
etsy ambony; tsy misy fiantraikany amin'izay efa nalefa talohan'izay izany.

## Fifandraisana

Fanontaniana na fangatahana: alefaso mailaka any amin'ny fontesmcp@proton.me, na sokafy issue ao amin'ny
<https://github.com/ykarapazar/fontes/issues>.
