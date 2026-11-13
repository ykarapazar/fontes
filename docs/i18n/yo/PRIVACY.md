> Ìtúmọ̀ yìí ni a ṣe pẹ̀lú ìrànlọ́wọ́ ẹ̀rọ. Ẹ̀dà Gẹ̀ẹ́sì ni ó ní àṣẹ.

# Ìkéde ìpamọ́ àṣírí Fontes

Fontes ń ṣiṣẹ́ lórí kọ̀ǹpútà rẹ. Àwọn ìwádìí rẹ àti àwọn ìwé tí o ṣí wà láàárín kọ̀ǹpútà rẹ, àwọn orísun
ìjọba tí o wá nínú wọn, àti áàpù AI tí o ń lò (lábẹ́ òfin ìlò áàpù náà fúnra rẹ̀). Fontes fúnra rẹ̀ **kò fi
ohunkóhun ránṣẹ́ ní àìyípadà** sí àwọn olùgbéejáde Fontes.

## Ohun tí ó lè kúrò lórí kọ̀ǹpútà rẹ, àti ìgbà wo

**1. Àyẹ̀wò ìmúdójúìwọ̀n (ó wà ní títàn ní àìyípadà).** Lẹ́ẹ̀kan lójoojúmọ́, Fontes ń béèrè lọ́wọ́ PyPI, àtòjọ
àwọn package Python gbogbogbò, èwo ni ẹ̀dà tuntun jùlọ. Ìbéèrè náà kò gbé ohunkóhun nípa rẹ tàbí iṣẹ́ rẹ
dání; PyPI ń rí àdírẹ́sì IP rẹ, bí ó ṣe máa ń rí i fún gbogbo ìgbàsílẹ̀. Láti pa á, ṣètò
`FONTES_NO_UPDATE_CHECK=1` (ìfitónilétí nínú áàpù) àti `FONTES_NO_AUTO_UPDATE=1` (ìmúdójúìwọ̀n aládàáṣe ti
ẹ̀rọ ìfisílẹ̀).

**2. Iye ìlò (ó wà ní pípa àyàfi bí o bá tàn án).** Bí o bá gbà (opt in), lẹ́ẹ̀kan lójoojúmọ́ Fontes ń fi
ránṣẹ́:

- ẹ̀dà Fontes àti ìdílé ètò ìṣiṣẹ́ kọ̀ǹpútà rẹ (macOS, Windows, Linux);
- fún ọjọ́ kọ̀ọ̀kan, iye ìgbà tí a lo irinṣẹ́ kọ̀ọ̀kan fún kóòdù agbègbè ìdájọ́ kọ̀ọ̀kan, fún àpẹẹrẹ
  "2026-11-10, nl, search_caselaw, 12".

Ìyẹn ni gbogbo ìfiránṣẹ́ náà. Kò ní àwọn ìwádìí rẹ nínú láé, àwọn àmì ìdánimọ̀ ìwé tàbí ẹjọ́, ọ̀rọ̀ inú ìwé,
orúkọ rẹ, àkọọ́lẹ̀ kan, tàbí àmì ìdánimọ̀ èyíkéyìí fún ọ tàbí fún kọ̀ǹpútà rẹ. Àwọn iye náà ń dúró lórí
kọ̀ǹpútà rẹ (nínú fódà cache Fontes, `stats.json`) títí a ó fi fi wọ́n ránṣẹ́; bí ìfiránṣẹ́ kò bá yọrí sí
rere, wọ́n ń dúró dè ọjọ́ kejì.

- **Láti gbà (opt in)**: dáhùn "y" nígbà tí ẹ̀rọ ìfisílẹ̀ bá béèrè, tàbí ṣètò `FONTES_STATS=1` fún sáfà
  Fontes.
- **Láti kọ̀ (opt out)**: tún ẹ̀rọ ìfisílẹ̀ ṣe ìfilọ́lẹ̀ kí o sì tẹ Enter ní ìbéèrè náà, tàbí yọ
  `FONTES_STATS` kúrò. Pípa `stats.json` rẹ́ ń da ohunkóhun tí a kò tíì fi ránṣẹ́ nù.

**3. Ìròyìn àṣìṣe (kìkì nígbà tí o bá fi ránṣẹ́).** Nígbà tí o bá béèrè fún un (`fontes report-bug`, tàbí
béèrè lọ́wọ́ áàpù AI rẹ láti ròyìn àṣìṣe kan nínú Fontes), Fontes ń fi gbogbo ìròyìn náà hàn ọ́ ní àkọ́kọ́, ó
sì ń fi ránṣẹ́ kìkì bí o bá jẹ́rìí sí i. Ó ní ẹ̀dà Fontes, ìdílé ètò ìṣiṣẹ́ kọ̀ǹpútà rẹ, kóòdù agbègbè
ìdájọ́, orúkọ irinṣẹ́ àti ọ̀rọ̀ àṣìṣe láti inú ìpè irinṣẹ́ tí ó kùnà kẹ́yìn (a yọ àwọn ọ̀rọ̀ ìwádìí rẹ àti àwọn
àmì ìdánimọ̀ kúrò), àti àkíyèsí bí o bá kọ ọ̀kan. Má ṣe fi àlàyé oníbàárà sínú àkíyèsí náà. Láti ṣe
àtìlẹ́yìn fún èyí, Fontes ń tọ́jú àṣìṣe tí ó kẹ́yìn sórí kọ̀ǹpútà rẹ (`last-error.json` nínú fódà cache rẹ̀,
a ń rọ́pò rẹ̀ ní ìgbà kọ̀ọ̀kan); a kì í fi ránṣẹ́ fúnra rẹ̀ láé.

## Ibi tí ó ń lọ àti bí a ṣe ń pẹ́ tó tọ́jú rẹ̀

Iye ìlò àti ìròyìn àṣìṣe ń lọ sí sáfà kékeré kan tí olùgbéejáde Fontes ń ṣiṣẹ́ (`relay.kinetra.fit`). Kò
tọ́jú àwọn àdírẹ́sì IP: a ń lò wọ́n nínú ìrántí nìkan, fún ìgbà díẹ̀, láti dènà àwọn ìbéèrè tí ó pọ̀ jù, sáfà
ojú-ìwé ayélujára kò sì tọ́jú àkọsílẹ̀ ìráyè (access logs) fún un. A ń kó àwọn iye pọ̀ sí àpapọ̀ ojoojúmọ́; a
kò tọ́jú àwọn ìfiránṣẹ́ ẹnìkọ̀ọ̀kan. A ń tọ́jú àwọn àpapọ̀ fún ọdún 2 jùlọ, àwọn ìròyìn àṣìṣe fún ọdún 1 jùlọ,
lẹ́yìn náà a ó pa wọ́n rẹ́. A kò ta nǹkankan tàbí pín in.

Bí a kò bá lè dé sáfà yẹn, a kò fi nǹkankan ránṣẹ́: àwọn iye ń wà lórí kọ̀ǹpútà rẹ, ìròyìn àṣìṣe sì ń mú ọ lọ
sí issue tracker dípò.

## Ta ni ó ní ojúṣe, àti lórí ìpìlẹ̀ wo

Olùdarí dátà (data controller) fún iye ìlò àti ìròyìn àṣìṣe ni Yüce Karapazar, olùgbéejáde Fontes.
Ìbánisọ̀rọ̀: fontesmcp@proton.me.

Ìpìlẹ̀ òfin ni ìfọwọ́sí rẹ (consent) (Abala 6(1)(a) ti UK GDPR àti EU GDPR). A ń fi iye ìlò ránṣẹ́ kìkì bí o
bá ti gbà (opt in), a sì ń fi ìròyìn àṣìṣe ránṣẹ́ kìkì lẹ́yìn tí o bá ti jẹ́rìí sí i. O lè fa ìfọwọ́sí rẹ
padà nígbàkúùgbà nípa kíkọ̀ (opt out) bí a ṣe ṣàlàyé lókè; èyí kò kan ohun tí a ti fi ránṣẹ́ ṣáájú.

## Ìbánisọ̀rọ̀

Àwọn ìbéèrè tàbí ẹ̀bẹ̀: fi ímeèlì ránṣẹ́ sí fontesmcp@proton.me, tàbí ṣí issue kan ní
<https://github.com/ykarapazar/fontes/issues>.
