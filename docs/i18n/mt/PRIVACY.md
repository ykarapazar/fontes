> Din hija traduzzjoni magħmula bl-għajnuna tal-magna. Il-verżjoni Ingliża hija dik awtorevoli.

# Avviż ta' privatezza ta' Fontes

Fontes jaħdem fuq il-kompjuter tiegħek. It-tfittxijiet tiegħek u d-dokumenti li tiftaħ jibqgħu
bejn il-kompjuter tiegħek, is-sorsi li tfittex fihom (dawk uffiċjali, u CourtListener u Lexifina fejn tużahom, ara hawn taħt), u l-app tal-AI li tuża (taħt
it-termini ta' dik l-app stess). Fontes innifsu ma jibgħat lill-iżviluppaturi ta' Fontes
**xejn b'mod awtomatiku**.

## X'jista' joħroġ mill-kompjuter tiegħek, u meta

**1. Verifika tal-aġġornamenti (mixgħula b'mod awtomatiku).** Darba kuljum Fontes jistaqsi lil
PyPI, l-indiċi pubbliku tal-pakketti Python, liema hija l-aħħar verżjoni. It-talba ma ġġorr xejn
dwarek jew dwar xogħlok; PyPI jara l-indirizz IP tiegħek, bħal fi kwalunkwe download. Biex titfiha,
issettja `FONTES_NO_UPDATE_CHECK=1` (l-avviż fl-app) u `FONTES_NO_AUTO_UPDATE=1` (l-aġġornamenti
awtomatiċi tal-installer).

**2. Għadd tal-użu (mitfi sakemm ma tixgħlux int).** Jekk tagħti l-kunsens (opt-in), darba kuljum
Fontes jibgħat:

- il-verżjoni ta' Fontes u l-familja tas-sistema operattiva tiegħek (macOS, Windows, Linux);
- għal kull jum, kemm-il darba ntużat kull għodda għal kull kodiċi ta' ġurisdizzjoni, pereżempju
  "2026-11-10, nl, search_caselaw, 12".

Dak huwa l-messaġġ kollu. Qatt ma jinkludi t-tfittxijiet tiegħek, identifikaturi ta' dokumenti
jew ta' kawżi, test ta' dokumenti, ismek, kont, jew xi identifikatur għalik jew għall-kompjuter
tiegħek. L-għadd jistenna fuq il-kompjuter tiegħek (fil-folder tal-cache ta' Fontes,
`stats.json`) sakemm jintbagħat; jekk il-bgħit ifalli, jistenna għall-jum ta' wara.

- **Biex tagħti l-kunsens (opt in)**: wieġeb "i" meta l-installer jistaqsik, jew issettja
  `FONTES_STATS=1` għas-server Fontes.
- **Biex tirtiraħ (opt out)**: erġa' ħaddem l-installer u agħfas Enter f'dik il-mistoqsija, jew
  neħħi `FONTES_STATS`. Li tħassar `stats.json` jarmi kull ħaġa li għadha ma ntbagħtitx.

**3. Rapporti ta' żbalji (biss meta tibgħat wieħed).** Meta titlob wieħed (`fontes report-bug`,
jew titlob lill-app tal-AI tiegħek tirrapporta żball ta' Fontes), Fontes jurik ir-rapport kollu
l-ewwel u jibagħtu biss jekk tikkonferma. Fih il-verżjoni ta' Fontes, il-familja tas-sistema
operattiva tiegħek, il-kodiċi tal-ġurisdizzjoni, l-isem tal-għodda u l-messaġġ tal-iżball
tal-aħħar sejħa ta' għodda li falliet (bil-kliem tat-tfittxija u l-identifikaturi tiegħek
imneħħija), u nota jekk tikteb waħda. Tpoġġix dettalji tal-klijenti fin-nota. Biex jappoġġja dan,
Fontes iżomm l-aħħar żball fuq il-kompjuter tiegħek (`last-error.json` fil-folder tal-cache
tiegħu, jinbidel kull darba); qatt ma jintbagħat waħdu.

**4. Lexifina (mixgħula b'mod awtomatiku).** `get_law_on_date`, `get_law_history`, il-91 pajjiż u l-Atti tal-Indja jinqraw mir-rekord ta' Lexifina, u għalhekk jmorru għand Lexifina kemm flimkien mas-sit uffiċjali kif ukoll minflok. Il-kliem tat-tfittxija, iċ-ċitazzjonijiet u d-dati tiegħek jmorru għas-server b'xejn ta' Lexifina, `global-law.lexifina.com`, li jmexxih Lexifina, mhux l-iżviluppaturi ta' Fontes. Lexifina tiddokumenta li s-server tagħha jirrekordja liema għodda ntużat u kemm damet, qatt mhux x'intalab; Fontes ma jistax jivverifika dan, u t-termini ta' Lexifina japplikaw. Lexifina jara l-indirizz IP tiegħek, bħal kwalunkwe server tal-web. Biex titfiha għalkollox, issettja `WLM_LEXIFINA=0`; dawk iż-żewġ għodod u dawk il-pajjiżi jieqfu jaħdmu u xejn ma jintbagħat hemm.

## Fejn imur u kemm jinżamm

L-għadd tal-użu u r-rapporti ta' żbalji jmorru għal server żgħir immexxi mill-iżviluppatur ta'
Fontes (`relay.kinetra.fit`). Ma jaħżen l-ebda indirizz IP: jintużaw biss fil-memorja, għal ftit
ħin, biex iwaqqfu l-għargħar ta' talbiet (floods), u l-web server ma jżomm l-ebda access log
għalih. L-għadd jingħadd f'totali ta' kuljum; is-sottomissjonijiet individwali ma jinżammux.
It-totali jinżammu sa sentejn, ir-rapporti ta' żbalji sa sena, imbagħad jitħassru. Xejn ma
jinbiegħ jew jinqasam.

Jekk dak is-server ma jkunx jista' jintlaħaq, ma jintbagħat xejn: l-għadd jibqa' fuq il-kompjuter
tiegħek u r-rapporti ta' żbalji jirreferuk għall-issue tracker minflok.

## Min huwa responsabbli, u fuq liema bażi

Il-kontrollur tad-data għall-għadd tal-użu u għar-rapporti ta' żbalji huwa Yüce Karapazar,
l-iżviluppatur ta' Fontes. Kuntatt: fontesmcp@proton.me.

Il-bażi legali hija l-kunsens tiegħek (l-Artikolu 6(1)(a) tal-UK GDPR u tal-GDPR tal-UE).
L-għadd tal-użu jintbagħat biss jekk tagħti l-kunsens (opt-in), u rapport ta' żball biss wara li
tikkonfermah. Tista' tirtira l-kunsens tiegħek fi kwalunkwe ħin billi tagħmel opt-out kif deskritt
hawn fuq; dan ma jaffettwax dak li ntbagħat qabel.

## Kuntatt

Mistoqsijiet jew talbiet: ibgħat email lil fontesmcp@proton.me, jew iftaħ issue fuq
<https://github.com/ykarapazar/fontes/issues>.
