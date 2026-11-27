> Fandikan-teny natao tamin'ny fanampian'ny milina ity. Ny dikan-teny anglisy no manan-kery.

# Fontes: fanontaniana sy valiny

## Inona ny Fontes?

Mpizara MCP maimaim-poana sy open source (Apache 2.0). Ahafahan'ny rindranasa rehetra mampiasa ny Model
Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI sy ny hafa) mitady didim-pitsarana sy lalàna
mivantana ao amin'ny tranonkalan'ny fitsarana sy ny fanjakana amin'ny faritra ara-pitsarana 125 sy fitsarana
iraisam-pirenena, ary lalàna avy amin'ny firenena 91 hafa amin'ny alalan'ny tahiry an'i Lexifina (jereo ambany).
Mitonona ny loharanony sy misy rohy mankany amin'ny tany am-boalohany ny valiny tsirairay.

## Ofisialy ve ireo lahatsoratra?

Matetika, saingy tsy isaky ny mandeha.

- Ny ankamaroan'ny loharano dia tantanan'ny fitsarana, ministera na gazety ofisialy.
- Misy lahatsoratra natambatra (consolidé) navoakan'ny fanjakana nefa voalaza mazava fa tsy ofisialy: ny
  gazety ofisialy ihany no tena marina.
- Misy loharano vitsivitsy tsy tranonkalam-panjakana mihitsy (ohatra LexiVox, LawPhil, Maqam, Wikisource).

Manampy fampitandremana "Loharano tsy ofisialy" amin'ny valiny rehetra avy amin'ny iray amin'ireo ny Fontes.
Alohan'ny hitanisanao na inona na inona, hamarino ao amin'ny famoahana ofisialy. Ny tabilao fandrakofana ao
amin'ny [README](README.md#fandrakofana) sy ny `list_jurisdictions` no milaza ny loharano ho an'ny faritra
ara-pitsarana tsirairay.

## Faritra ara-pitsarana inona avy no rakofany, ary hatraiza ny tsarany?

Adapter 125: firenena mpikambana ao amin'ny ONU 108, Hong Kong, Kosovo, Palestina, Taiwan, ny DIFC Courts, ny fitsarana ao amin'ny fanjakana Amerikana ary fitsarana sy fikambanana iraisam-pirenena 11 (toy ny European Court of Human Rights, ny UE, ny ICJ ary
ny WTO).

Miovaova be ny fandrakofana. Araka ny fitsipika henjana iray (ny jurisprudence an'ny fitsarana ambony
indrindra ankapobeny, na ny lalàm-panorenana sy ireo lalàna fototra, tratra feno), 72 amin'ireo 125 no
heverina ho voarakotra. Ny [COVERAGE.md](COVERAGE.md) dia mitanisa, isaky ny faritra ara-pitsarana, izay
tratran'ny Fontes, izay tsy tratrany, ary ny antony.

## Mila fanalahidy API ve aho?

Ho an'ny saika faritra ara-pitsarana rehetra, tsia. Mila fanalahidy maimaim-poana ny loharano vitsivitsy:
jereo ny [KEYS.md](KEYS.md).

- **Frantsa:** eny. Maty i Frantsa mandra-pametrakao ny `WLM_FR_PISTE_CLIENT_ID` sy ny
  `WLM_FR_PISTE_CLIENT_SECRET`. Avy amin'ny kaonty PISTE maimaim-poana (piste.gouv.fr) misy rindranasa
  misoratra anarana amin'ny Judilibre sy Légifrance ireo.
- **Etazonia:** tsy voatery. Mandeha tsy misy fanalahidy ny fikarohana didim-pitsarana, saingy ny fanalahidy
  demo iombonana dia tsy mamela afa-tsy fikarohana 10 eo ho eo isan'andro isaky ny adiresy IP. Ampitomboin'ny
  fanalahidy api.data.gov maimaim-poana ao amin'ny `WLM_US_GOVINFO_KEY` izany.
- **Fitsarana ao amin'ny fanjakana Amerikana:** eny. Maty ny jurisprudence an'ny fanjakana (`us-states`) mandra-pametrakao ny `WLM_US_COURTLISTENER_KEY` amin'ny API token CourtListener maimaim-poana anao manokana. Ny CourtListener dia tantanan'ny fikambanana tsy mitady tombony Free Law Project; tsy loharano ofisialy izy, ary milaza izany ny valiny rehetra.

Apetraho ho environment variables ho an'ny mpizara Fontes ireo ao amin'ny fandrindrana MCP an'ny
rindranasanao. Ny mpametraka dia mangataka ireo aorian'ny fametrahana, ary ny launcher-ny
**Add or change keys** no manova azy ireo any aoriana.

Ankoatra izany, misy loharano milaza ao amin'ny fepetrany fa ilaina ny fahazoan-dalan'ny mpamoaka ho an'ny
fidirana mandeha ho azy. Voamarika OFF ireo ary mijanona ho maty. Tsy manova izany ny fanalahidy; ny
fahazoan-dalan'ny mpamoaka ihany no manova azy (avy eo apetraho ny `WLM_PERMITTED=<codes>`).

## Avy aiza ny kinova taloha sy ny firenena fanampiny?

Avy amin'ny [Lexifina](https://github.com/lexifina/global-law), izay mitahiry ny lalàn'ny firenena manodidina ny 200 ho tantara git: ny fanovana tsirairay dia commit misy daty ny andro nanan-kery azy. Ny Fontes dia mamaky azy amin'ny alalan'ny servera maimaim-poana an-tserasera an'i Lexifina. Fitaovana roa no mampiasa azy: `get_law_on_date` (andininy tahaka ny nanan-kery tamin'ny daty iray, na tamin'ny daty lasa koa, miaraka amin'ny lalàna nanova azy farany) ary `get_law_history` (lalàna rehetra nanova andininy, na ny fanovana teny an-teny eo anelanelan'ny daty roa). Mamaky firenena sy faritany 91 hafa koa ny Fontes amin'io fomba io, ho an'ny lalàna ihany (ohatra Afrika Atsimo, Kenya, Meksika, Zelanda Vaovao, Rosia, Korea Atsimo, Belzika, Lituania, Okraina, Malezia, Taylandy sy Arabia Saodita). Misaraka amin'ny faritra ara-pitsarana 125 misy fandrakofana ofisialy mivantana izy ireny, ary miovaova be ny fandrakofana isaky ny firenena (ny tahiry nasionaly an'i Kenya misy lalàna 9). Ny lalàna an'i India koa dia avy amin'ny tahiry an'i Lexifina, satria ny fepetran'ny India Code dia mandrara ny fidirana amin'ny fomba mandeha ho azy; ny didim-pitsarana an'ny Fitsarana Tampony dia mivantana.

Tsy ny mpamoaka ofisialy i Lexifina, ary tsy mivantana ny tahiriny: mijery indray ny firenena tsirairay amin'ny loharano ofisialiny indraindray izy, ary ny tatitra momba ny fahavaoany tamin'ny 2026-11-26 dia nanisa 338 amin'ny 383 vondrona lalàna nasionaly ho tsy voamarina tato anatin'ny andro 7 farany. Ny valiny tsirairay dia manonona an'i Lexifina ho loharano, mampifandray ny pejin'ny mpamoaka ofisialy, ary milaza hatramin'ny ahoana ny tahiry.

Lexifina mihevitra fa tsy arovan'ny copyright ny lahatsoratra ofisialy momba ny lalàna, ka any amin'ny firenena sasany dia mandrafitra kopia amin'ny tranonkala izay manaja ny fepetra na ny robots.txt ny Fontes mihitsy. Mbola manaja azy ireny ny Fontes ho an'ny zavatra rehetra izay izy mihitsy no maka; izay tonga amin'i Lexifina dia manaraka ny fanapahan-keviny manokana, voarakitra isaky ny firenena ao amin'ny tahiriny. Misy vitsivitsy mandrara ny fampiasana (mpamoaka an'i Kenya: CC BY-NC). Ny teny nokarohinao, ny fanondroana ary ny daty dia alefa any amin'ny servera an'i Lexifina ho an'ireny. Apetraho ny `WLM_LEXIFINA=0` mba hamongorana azy. Ny servera maimaim-poana dia mamela 60 antso isan'minitra sy 10 000 isan'andro isaky ny adiresy IP; tsy mila fanalahidy na kaonty. Tsy miankina amin'i Lexifina ny Fontes.

## Inona no mivoaka ny solosaiko?

Mankany amin'ny loharano karohina ihany ny fikarohanao (ho an'ny fitaovana sy firenena an'i Lexifina, dia servera an'i Lexifina izany). Tsy mitahiry tahiry angona ny Fontes ary tsy mila
kaonty.

Ankoatra ireo loharano, manontany ny PyPI indray mandeha isan'andro ny Fontes raha misy kinova vaovao kokoa
(vonoy amin'ny `FONTES_NO_UPDATE_CHECK=1`). Maty ny isa fampiasana raha tsy alefanao, ary alefa ihany ny
tatitra momba ny olana rehefa avy nijery sy nanamafy azy ianao. Hitan'ny rindranasa AI-nao ny resakao
araka ny fepetrany manokana.

Antsipiriany feno: [PRIVACY.md](PRIVACY.md).

## Torohevitra ara-dalàna ve ity?

Tsia. Fitaovana fikarohana ny Fontes. Mitady lahatsoratra izy; tsy milaza aminao izay dikan'ireo ho an'ny
raharahanao izy, ary ny fampiasana azy dia tsy mamorona fifandraisana mpisolovava sy mpanjifa amin'iza na
iza. Mety ho diso ny famakian'ny rindranasa AI lahatsoratra iray, koa vakio feno ny didim-pitsarana na ny
andininy alohan'ny hianteheranao aminy. Raha mila torohevitra, manontania mpisolovava mahafeno fepetra any
amin'ny toerana ipoiran'ny fanontanianao.

## Iza no mikojakoja azy? Hitohy handeha ve izy?

Olona iray: Yüce Karapazar. Tsy misy orinasa ao ambadiky ny Fontes, tsy misy fifanarahana fanohanana ary
tsy misy fanomezan-toky momba ny haavon'ny tolotra. Tsy misy tolotra ara-dalàna atolotra.

Hamarinina indray mandeha isan'andro ireo loharano ary avoaka ao amin'ny
[pejy toe-javatra](https://ykarapazar.github.io/fontes/status/?lang=mg) ny vokatra. Miova tsy misy
fampandrenesana ny tranonkalan'ny fitsarana sy ny fanjakana, ka mety ho tapaka amin'ny fotoana rehetra ny
loharano iray. Tsy misy antoka fa hitohy handeha ny loharano iray, na ny Fontes mihitsy. Omena "araka izao
misy azy izao" ny Fontes, tsy misy antoka (fizarana 7 sy 8 amin'ny [LICENSE](../../../LICENSE)).

## Diso na tranainy ny lahatsoratra iray, na tapaka ny loharano iray. Ahoana no hitaterako izany?

- Sokafy issue amin'ny alalan'ny taratasy "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Lazao hoe faritra ara-pitsarana inona, inona no
  nanontanianao, inona no azonao, ary ny pejy ofisialy mampiseho ny lahatsoratra marina.
- Na angataho amin'ny rindranasa AI-nao ny "hitaterana olana ao amin'ny Fontes" (na alefaso ny
  `fontes report-bug`). Ho hitanao ny tatitra alohan'ny hisian'ny zavatra alefa.
- Na alefaso mailaka any amin'ny fontesmcp@proton.me.

Aza mampiditra antsipirian'ny mpanjifa na fampahalalana tsiambaratelo ao anaty tatitra.

**Raha ianao no mitantana ny iray amin'ireo loharano** ary misy tsy mety (ny fepetranao, ny robots.txt-nao,
ny fetran'ny fangatahanao), alefaso mailaka any amin'ny fontesmcp@proton.me. Hahitsy na hovonoina ilay
loharano.

## Amin'ny inona no hahasamihafan'ny Fontes amin'ireo fitaovana fikarohana ara-dalàna an-tserasera?

- **Mandeha ao amin'ny solosainao izy.** Tsy misy mpizara Fontes ary tsy misy kaonty. Midika koa izany fa
  mandeha amin'ireo rindranasa afaka manomboka mpizara MCP eo an-toerana ihany izy (Claude Desktop, Codex,
  Cursor, VS Code sy ny toy izany), fa tsy amin'ireo rindranasa an-tranonkala fotsiny izay tsy mandray afa-tsy
  connector an-tserasera.
- **Tsy manana tahiry angona izy.** Mankany mivantana sy amin'izao fotoana izao amin'ny tranonkala na API
  an'ny mpamoaka ny fikarohana tsirairay, ka vaovao toy ny loharano ny valiny, ary ny kalitaon'ny fikarohana
  dia an'ny loharano mihitsy. Tsy misy fikarohana semantika ao anaty index voafantina.
- **Tsy mametraka fetra fampiasana izy.** Tsy misy fetra isam-bolana amin'ny antso ny Fontes. Asiany elanelana
  ny fangatahany amin'ny tranonkala tsirairay, ary misy loharano mametra ny hafainganana na ny fahatetezana
  azo anontaniana azy.
- **Open source izy.** Azonao vakiana ny adapter tsirairay ary hitanao tsara izay niavian'ny lahatsoratra
  tsirairay.
- **Tsy misy mpivarotra ao ambadiny.** Tsy misy fifanarahana, birao fanohanana na fanomezan-toky momba ny
  uptime (jereo ny "Iza no mikojakoja azy?").

## Rindranasa sy rafitra inona avy no mandeha aminy?

Rindranasa MCP rehetra afaka mandefa mpizara eo an-toerana (stdio), ohatra Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio ary Cline. Mandeha amin'ny
macOS, Windows ary Linux ny Fontes, na aiza na aiza mandehanan'ny uv (Python 3.13+). Amin'ny Mac na PC Windows, mametraka ny Claude Desktop,
Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio ary Cline indray mandeha ny
mpametraka tsindry iray. Dingana ho an'ny rindranasa tsirairay:
[INSTALL.md](INSTALL.md).

## Afaka mandray anjara amin'ny kaody ve aho?

Tsy amin'izao fotoana izao. Raisina ny issue, ny tatitra momba ny loharano ary ny fangatahana faritra
ara-pitsarana. Jereo ny [CONTRIBUTING.md](../../../CONTRIBUTING.md).
