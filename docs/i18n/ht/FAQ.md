> Sa a se yon tradiksyon ki fèt avèk èd machin. Se vèsyon angle a ki fè lafwa.

# Fontes: kesyon ak repons

## Kisa Fontes ye?

Yon sèvè MCP gratis ak sous louvri (Apache 2.0). Li pèmèt nenpòt aplikasyon ki pale Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI ak lòt) chèche desizyon tribinal ak lejislasyon an
dirèk sou sit entènèt tribinal ak gouvènman yo, nan plis pase 120 jiridiksyon ak tribinal entènasyonal
(124 adaptè). Chak rezilta bay non sous li epi li gen yon lyen ki mennen nan orijinal la.

## Èske tèks yo ofisyèl?

Pi souvan wi, men pa toujou.

- Pifò sous se yon tribinal, yon ministè oswa yon jounal ofisyèl ki jere yo.
- Kèk tèks konsolide se yon gouvènman ki pibliye yo, men yo deklare klèman yo pa ofisyèl: se sèlman
  jounal ofisyèl la ki otantik.
- Kèk sous pa sit gouvènman ditou (pa egzanp LexiVox, LawPhil, Maqam, Wikisource).

Fontes ajoute yon avètisman "Sous pa ofisyèl" nan chak repons ki soti nan youn nan sous sa yo. Anvan ou
site nenpòt bagay, verifye piblikasyon ofisyèl la. Tablo kouvèti ki nan [README](README.md#kouvèti) a ak
`list_jurisdictions` bay non sous la pou chak jiridiksyon.

## Ki jiridiksyon li kouvri, e ki jan li kouvri yo?

124 adaptè: 108 eta manm ONI, Hong Kong, Kosovo, Palestin, Taywan, Tribinal DIFC yo ak 11 tribinal ak
òganis entènasyonal (tankou Tribinal Ewopeyen Dwa Moun, Inyon Ewopeyen, CIJ ak OMC).

Kouvèti a varye anpil. Dapre yon règ sevè (presedan tribinal jeneral ki pi wo a, oswa konstitisyon an ak
lwa prensipal yo, jwenn nèt), 72 sou 124 yo konte kòm kouvri. [COVERAGE.md](../../COVERAGE.md) (an angle)
bay, pou chak jiridiksyon, sa Fontes rive jwenn, sa li pa rive jwenn, ak poukisa.

## Èske m bezwen yon kle API?

Pou prèske tout jiridiksyon, non. Kèk sous bezwen yon kle gratis: gade [KEYS.md](KEYS.md).

- **Lafrans:** wi. Lafrans etenn jiskaske ou mete `WLM_FR_PISTE_CLIENT_ID` ak
  `WLM_FR_PISTE_CLIENT_SECRET`. Yo soti nan yon kont PISTE gratis (piste.gouv.fr) ak yon aplikasyon ki
  abòne ak Judilibre ak Légifrance.
- **Etazini:** opsyonèl. Rechèch jirisprudans mache san kle, men kle demo pataje a pèmèt sèlman anviwon
  10 rechèch pa jou pou chak adrès IP. Yon kle api.data.gov gratis nan `WLM_US_GOVINFO_KEY` ogmante limit
  sa a.

Mete yo kòm varyab anviwònman pou sèvè Fontes la nan paramèt MCP aplikasyon ou. Lè enstalatè a soti, l ap
mande w yo apre enstalasyon an, e lansè **Ajoute oswa chanje kle** li a chanje yo pita.

Apa sa, kèk sous di nan kondisyon yo ke aksè otomatik bezwen pèmisyon piblikatè a. Yo make OFF e yo rete
etenn. Yon kle pa chanje sa; se sèlman pèmisyon piblikatè a ki chanje l (apre sa, mete
`WLM_PERMITTED=<codes>`).

## Kisa ki soti sou òdinatè m?

Rechèch ou yo ale sèlman nan sous kote rechèch la ap fèt la. Fontes pa kenbe okenn baz done e li pa bezwen
okenn kont.

Apa sous yo, Fontes mande PyPI yon fwa pa jou si gen yon vèsyon ki pi nouvo (etenn li ak
`FONTES_NO_UPDATE_CHECK=1`). Kantite itilizasyon etenn sof si ou limen yo, e yon rapò erè voye sèlman
apre ou fin wè l epi ou konfime l. Aplikasyon IA ou a wè konvèsasyon ou dapre pwòp kondisyon pa l.

Tout detay: [PRIVACY.md](PRIVACY.md).

## Èske sa se konsèy jiridik?

Non. Fontes se yon zouti rechèch. Li jwenn tèks; li pa di w kisa yo vle di pou ka ou, e lè w sèvi avè l
sa pa kreye yon relasyon avoka–kliyan ak pèsonn. Aplikasyon IA a ka li yon tèks mal, kidonk li tout
desizyon an oswa tout dispozisyon an anvan ou konte sou li. Pou konsèy, mande yon avoka ki kalifye kote
kesyon ou a poze a.

## Kiyès ki okipe l? Èske l ap kontinye mache?

Yon sèl moun: Yüce Karapazar. Pa gen okenn konpayi dèyè Fontes, pa gen kontra sipò, e pa gen okenn
pwomès sou nivo sèvis. Pa gen okenn sèvis jiridik ki ofri.

Yo verifye sous yo yon fwa pa jou, e yo pibliye rezilta yo sou
[paj eta a](https://ykarapazar.github.io/fontes/status/?lang=ht). Sit entènèt tribinal ak gouvènman yo
chanje san avètisman, kidonk yon sous ka kase nenpòt ki lè. Pa gen garanti okenn sous, ni Fontes li menm,
ap kontinye mache. Fontes bay "jan li ye a", san garanti (seksyon 7 ak 8 [LISANS](../../../LICENSE) la).

## Yon tèks pa bon, li pa ajou, oswa yon sous kase. Ki jan pou m rapòte l?

- Louvri yon issue ak fòmilè "Broken or wrong source" la:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Di ki jiridiksyon, kisa ou te mande, kisa ou
  te jwenn, ak paj ofisyèl ki montre bon tèks la.
- Oswa mande aplikasyon IA ou a pou "rapòte yon erè Fontes" (oswa lanse `fontes report-bug`). Ou wè rapò
  a anvan anyen voye.
- Oswa voye yon imèl bay fontesmcp@proton.me.

Pa mete detay kliyan oswa fè konfidansyèl nan yon rapò.

**Si se ou ki jere youn nan sous yo** e gen yon bagay ki pa bon (kondisyon ou yo, robots.txt ou, limit
demann ou yo), voye yon imèl bay fontesmcp@proton.me. Y ap repare sous la oswa y ap etenn li.

## Ki diferans ant Fontes ak zouti rechèch jiridik ki sou sèvè lòt moun?

- **Li mache sou òdinatè ou.** Pa gen sèvè Fontes e pa gen kont. Sa vle di tou li mache sèlman nan
  aplikasyon ki ka lanse yon sèvè MCP lokal (Claude Desktop, Codex, Cursor, VS Code ak lòt ki sanble),
  pa nan aplikasyon ki sèlman sou entènèt e ki aksepte sèlman konektè ki sou sèvè.
- **Li pa gen baz done.** Chak rechèch ale an dirèk sou pwòp sit entènèt oswa API piblikatè a, kidonk
  rezilta yo ajou otan sous la ajou, e kalite rechèch la se pa sous la. Pa gen rechèch semantik nan yon
  endèks yo chwazi.
- **Li pa mete okenn limit itilizasyon.** Fontes pa gen limit apèl pa mwa. Li espase demann li yo bay
  chak sit, e kèk sous limite ki vitès oswa konbyen fwa yo ka poze yo kesyon.
- **Li gen sous louvri.** Ou ka li chak adaptè epi wè egzakteman ki kote chak tèks soti.
- **Pa gen okenn founisè dèyè l.** Pa gen kontra, biwo sipò oswa pwomès disponiblite (gade "Kiyès ki
  okipe l?").

## Ak ki aplikasyon ak sistèm li mache?

Nenpòt aplikasyon MCP ki ka fè yon sèvè lokal (stdio) mache, pa egzanp Claude Desktop, Claude Code, Codex,
Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio ak Cline. Fontes mache sou macOS,
Windows ak Linux, tout kote uv mache (Python 3.13+). Li poko sou PyPI; lè l sou li, pifò aplikasyon ap
bezwen yon sèl kòmand oswa yon sèl antre konfigirasyon, e Claude Desktop pran yon fichye `.mcpb` ou klike
de fwa sou li. Yon enstalatè an yon sèl klik pou Mac ak Windows ap vini. Li konfigire Claude Desktop,
Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio ak Cline an yon sèl fwa. Etap
pou chak aplikasyon: [INSTALL.md](INSTALL.md).

## Èske m ka kontribye kòd?

Pa pou kounye a. Issue, rapò sou sous ak demann jiridiksyon akeyi ak plezi. Gade
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
