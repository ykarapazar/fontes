> Ìtúmọ̀ yìí ni a ṣe pẹ̀lú ìrànlọ́wọ́ ẹ̀rọ. Ẹ̀dà Gẹ̀ẹ́sì ni ó ní àṣẹ.

# Fontes: ìbéèrè àti ìdáhùn

## Kí ni Fontes?

Sáfà MCP ọ̀fẹ́ àti open source (Apache 2.0). Ó ń jẹ́ kí áàpù èyíkéyìí tí ó ń lo Model Context Protocol
(Claude, Codex, Cursor, VS Code, Gemini CLI àti àwọn mìíràn) wá àwọn ìdájọ́ ilé-ẹjọ́ àti òfin láàyè lórí
ojú-ìwé ayélujára ti ilé-ẹjọ́ àti ti ìjọba ní agbègbè ìdájọ́ 120+ àti àwọn ilé-ẹjọ́ àgbáyé (adapter 124).
Gbogbo èsì ń dárúkọ orísun rẹ̀ ó sì ní ìjápọ̀ sí ojúlówó.

## Ṣé ti ìjọba ni àwọn ọ̀rọ̀ náà?

Ọ̀pọ̀ ìgbà, ṣùgbọ́n kì í ṣe nígbà gbogbo.

- Èyí tí ó pọ̀ jùlọ nínú àwọn orísun ni ilé-ẹjọ́, iléeṣẹ́ ìjọba (ministry) tàbí Ìwé Ìròyìn Ìjọba (official
  gazette) ń ṣiṣẹ́.
- Àwọn ọ̀rọ̀ tí a ti ṣàkópọ̀ (consolidated) kan ni ìjọba tẹ̀ jáde ṣùgbọ́n a sọ ní gbangba pé wọn kì í ṣe ti
  ìjọba: Ìwé Ìròyìn Ìjọba nìkan ni ojúlówó.
- Àwọn orísun díẹ̀ kì í ṣe ojú-ìwé ayélujára ìjọba rárá (fún àpẹẹrẹ LexiVox, LawPhil, Maqam, Wikisource).

Fontes ń fi ìkìlọ̀ "Orísun tí kì í ṣe ti ìjọba" kún gbogbo ìdáhùn tí ó wá láti ọ̀kan nínú wọn. Kí o tó tọ́ka
sí ohunkóhun, ṣàyẹ̀wò ìtẹ̀jáde ìjọba. Tábìlì ìbòrí nínú [README](README.md#ìbòrí) àti `list_jurisdictions`
ń dárúkọ orísun fún agbègbè ìdájọ́ kọ̀ọ̀kan.

## Àwọn agbègbè ìdájọ́ wo ni ó bò, àti bí ó ṣe dára tó?

Adapter 124: orílẹ̀-èdè ọmọ ẹgbẹ́ UN 108, Hong Kong, Kosovo, Palestine, Taiwan, DIFC Courts àti ilé-ẹjọ́ àti
àjọ àgbáyé 11 (bíi European Court of Human Rights, EU, ICJ àti WTO).

Ìbòrí yàtọ̀ gidigidi. Lábẹ́ òfin líle kan (àwọn ìdájọ́ ìṣáájú ti ilé-ẹjọ́ gbogbogbò tí ó ga jùlọ, tàbí
òfin-ìpìlẹ̀ àti àwọn òfin pàtàkì, tí a dé ní kíkún), 72 nínú 124 ni a kà sí èyí tí a bò. [COVERAGE.md](COVERAGE.md)
ń kà, fún agbègbè ìdájọ́ kọ̀ọ̀kan, ohun tí Fontes dé, ohun tí kò dé, àti ìdí rẹ̀.

## Ṣé mo nílò kọ́kọ́rọ́ API?

Fún fere gbogbo agbègbè ìdájọ́, rárá. Àwọn orísun díẹ̀ nílò kọ́kọ́rọ́ ọ̀fẹ́: wo [KEYS.md](KEYS.md).

- **France:** bẹ́ẹ̀ni. France wà ní pípa títí o fi ṣètò `WLM_FR_PISTE_CLIENT_ID` àti
  `WLM_FR_PISTE_CLIENT_SECRET`. Wọ́n wá láti àkọọ́lẹ̀ PISTE ọ̀fẹ́ (piste.gouv.fr) pẹ̀lú áàpù kan tí ó forúkọ
  sílẹ̀ fún Judilibre àti Légifrance.
- **United States:** kò pọn dandan. Ìwádìí ìdájọ́ ilé-ẹjọ́ ń ṣiṣẹ́ láìsí kọ́kọ́rọ́, ṣùgbọ́n kọ́kọ́rọ́ demo tí
  a pín gbà ìwádìí bíi 10 péré lójoojúmọ́ fún àdírẹ́sì IP kọ̀ọ̀kan. Kọ́kọ́rọ́ api.data.gov ọ̀fẹ́ nínú
  `WLM_US_GOVINFO_KEY` ń gbé e sókè.

Ṣètò wọn gẹ́gẹ́ bí environment variable fún sáfà Fontes nínú ètò MCP áàpù rẹ. Nígbà tí a bá tẹ ẹ̀rọ
ìfisílẹ̀ jáde, yóò béèrè fún wọn lẹ́yìn ìfisílẹ̀, launcher rẹ̀ **Add or change keys** yóò sì yí wọn padà
lẹ́yìn náà.

Lọ́tọ̀, àwọn orísun kan sọ nínú òfin ìlò wọn pé ìráyè aládàáṣe nílò àṣẹ olùtẹ̀jáde. A sàmì sí wọn ní OFF, wọ́n
sì ń wà ní pípa. Kọ́kọ́rọ́ kò yí èyí padà; àṣẹ olùtẹ̀jáde nìkan ni ó ń yí i padà (lẹ́yìn náà ṣètò
`WLM_PERMITTED=<codes>`).

## Kí ni ó ń kúrò lórí kọ̀ǹpútà mi?

Àwọn ìwádìí rẹ ń lọ sí orísun tí a ń wá nínú rẹ̀ nìkan. Fontes kò tọ́jú ibi ìpamọ́ dátà (database), kò sì nílò
àkọọ́lẹ̀.

Yàtọ̀ sí àwọn orísun, Fontes ń béèrè lọ́wọ́ PyPI lẹ́ẹ̀kan lójoojúmọ́ bóyá ẹ̀dà tuntun wà (pa á pẹ̀lú
`FONTES_NO_UPDATE_CHECK=1`). Iye ìlò wà ní pípa àyàfi bí o bá tàn án, a sì ń fi ìròyìn àṣìṣe ránṣẹ́ kìkì lẹ́yìn
tí o bá ti rí i tí o sì jẹ́rìí sí i. Áàpù AI rẹ ń rí ìjíròrò rẹ lábẹ́ òfin ìlò tirẹ̀.

Àlàyé kíkún: [PRIVACY.md](PRIVACY.md).

## Ṣé ìmọ̀ràn òfin ni èyí?

Rárá. Irinṣẹ́ ìwádìí ni Fontes. Ó ń wá àwọn ọ̀rọ̀; kò sọ fún ọ ohun tí wọ́n túmọ̀ sí fún ọ̀ràn rẹ, lílò rẹ̀ kò
sì dá àjọṣe agbẹjọ́rò àti oníbàárà sílẹ̀ pẹ̀lú ẹnikẹ́ni. Áàpù AI lè ṣì ọ̀rọ̀ kan kà, nítorí náà ka ìdájọ́
tàbí abala náà ní kíkún kí o tó gbẹ́kẹ̀lé e. Fún ìmọ̀ràn, béèrè lọ́wọ́ agbẹjọ́rò tí ó tóótun ní ibi tí ìbéèrè
rẹ ti dìde.

## Ta ni ó ń tọ́jú rẹ̀? Ṣé yóò máa ṣiṣẹ́ lọ?

Ènìyàn kan: Yüce Karapazar. Kò sí iléeṣẹ́ kankan lẹ́yìn Fontes, kò sí àdéhùn ìrànlọ́wọ́ kò sì sí ìlérí nípa
ìpele iṣẹ́. A kò pèsè iṣẹ́ òfin kankan.

A ń ṣàyẹ̀wò àwọn orísun lẹ́ẹ̀kan lójoojúmọ́, a sì ń tẹ àwọn èsì jáde lórí
[ojú-ìwé ipò](https://ykarapazar.github.io/fontes/status/?lang=yo). Ojú-ìwé ayélujára ti ilé-ẹjọ́ àti ti
ìjọba ń yí padà láìsí ìkìlọ̀, nítorí náà orísun kan lè bàjẹ́ nígbàkúùgbà. Kò sí ìdánilójú pé orísun èyíkéyìí,
tàbí Fontes fúnra rẹ̀, yóò máa ṣiṣẹ́ lọ. A pèsè Fontes "bí ó ṣe wà" (as is), láìsí ìdánilójú (abala 7 àti 8
ti [LICENSE](../../../LICENSE)).

## Ọ̀rọ̀ kan kò tọ́ tàbí ti gbó, tàbí orísun kan ti bàjẹ́. Báwo ni mo ṣe lè ròyìn rẹ̀?

- Ṣí issue kan pẹ̀lú fọ́ọ̀mù "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Sọ agbègbè ìdájọ́ wo, ohun tí o béèrè, ohun tí
  o rí gbà, àti ojú-ìwé ìjọba tí ó fi ọ̀rọ̀ tí ó tọ́ hàn.
- Tàbí béèrè lọ́wọ́ áàpù AI rẹ láti "ròyìn àṣìṣe kan nínú Fontes" (tàbí ṣe ìfilọ́lẹ̀ `fontes report-bug`). O
  máa rí ìròyìn náà kí a tó fi ohunkóhun ránṣẹ́.
- Tàbí fi ímeèlì ránṣẹ́ sí fontesmcp@proton.me.

Má ṣe fi àlàyé oníbàárà tàbí ìwífún àṣírí sínú ìròyìn.

**Bí o bá ń ṣiṣẹ́ ọ̀kan nínú àwọn orísun náà** tí ohun kan kò sì tọ́ (òfin ìlò rẹ, robots.txt rẹ, ìdíwọ̀n
ìbéèrè rẹ), fi ímeèlì ránṣẹ́ sí fontesmcp@proton.me. A máa ṣàtúnṣe orísun náà tàbí pa á.

## Báwo ni Fontes ṣe yàtọ̀ sí àwọn irinṣẹ́ ìwádìí òfin orí ayélujára?

- **Ó ń ṣiṣẹ́ lórí kọ̀ǹpútà rẹ.** Kò sí sáfà Fontes kò sì sí àkọọ́lẹ̀. Èyí tún túmọ̀ sí pé ó ń ṣiṣẹ́ kìkì
  nínú àwọn áàpù tí ó lè bẹ̀rẹ̀ sáfà MCP lórí kọ̀ǹpútà rẹ (Claude Desktop, Codex, Cursor, VS Code àti
  irúfẹ́ wọn), kì í ṣe nínú àwọn áàpù orí ayélujára nìkan tí ó ń gba connector orí ayélujára nìkan.
- **Kò ní ibi ìpamọ́ dátà.** Ìwádìí kọ̀ọ̀kan ń lọ ní tààrà àti láàyè sí ojú-ìwé ayélujára tàbí API ti
  olùtẹ̀jáde fúnra rẹ̀, nítorí náà àwọn èsì jẹ́ tuntun bí orísun náà, dídára ìwádìí sì jẹ́ ti orísun
  náà fúnra rẹ̀. Kò sí ìwádìí semantic nínú index tí a ti ṣà.
- **Kò fi ìdíwọ̀n ìlò lélẹ̀.** Fontes kò ní ìdíwọ̀n oṣooṣù lórí àwọn ìpè. Ó ń fi àlàfo sáàárín àwọn ìbéèrè
  rẹ̀ sí ojú-ìwé ayélujára kọ̀ọ̀kan, àwọn orísun kan sì ń dín bí a ṣe lè béèrè lọ́wọ́ wọn yára tàbí lọ́pọ̀ tó kù.
- **Open source ni.** O lè ka adapter kọ̀ọ̀kan kí o sì rí ibi gangan tí ọ̀rọ̀ kọ̀ọ̀kan ti wá.
- **Kò sí olùtajà lẹ́yìn rẹ̀.** Kò sí àdéhùn, ibùdó ìrànlọ́wọ́ tàbí ìlérí uptime (wo "Ta ni ó ń tọ́jú rẹ̀?").

## Àwọn áàpù àti ètò wo ni ó ń bá ṣiṣẹ́?

Áàpù MCP èyíkéyìí tí ó lè ṣe ìfilọ́lẹ̀ sáfà lórí kọ̀ǹpútà (stdio), fún àpẹẹrẹ Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio àti Cline. Fontes ń ṣiṣẹ́ lórí
macOS, Windows àti Linux, níbikíbi tí uv bá ti ń ṣiṣẹ́ (Python 3.13+). Ẹ̀rọ ìfisílẹ̀ onítẹ̀-ẹ̀ẹ̀kan fún Mac àti Windows ń bọ̀ láìpẹ́. Ó ń ṣètò Claude Desktop, Codex, Claude
Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio àti Cline lẹ́ẹ̀kan náà. Àwọn ìgbésẹ̀ fún áàpù
kọ̀ọ̀kan: [INSTALL.md](INSTALL.md).

## Ṣé mo lè ṣe àfikún kóòdù?

Kì í ṣe báyìí. A gba issue, ìròyìn nípa àwọn orísun àti ẹ̀bẹ̀ fún agbègbè ìdájọ́. Wo
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
