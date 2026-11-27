> Din hija traduzzjoni magħmula bl-għajnuna tal-magna. Il-verżjoni Ingliża hija dik awtorevoli.

# Fontes: mistoqsijiet u tweġibiet

## X'inhu Fontes?

Server MCP b'xejn u b'kodiċi miftuħ (Apache 2.0). Jippermetti lil kwalunkwe app li titkellem
il-Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI u oħrajn) tfittex
deċiżjonijiet tal-qorti u leġiżlazzjoni direttament fuq is-siti web tal-qrati u tal-gvern
f'120+ ġurisdizzjoni u qorti internazzjonali (125 adapter). Kull riżultat isemmi s-sors tiegħu
u għandu link għall-oriġinal.

## It-testi huma uffiċjali?

Fil-biċċa l-kbira, iva, iżda mhux dejjem.

- Il-biċċa l-kbira tas-sorsi huma mmexxija minn qorti, ministeru jew gazzetta uffiċjali.
- Xi testi konsolidati huma ppubblikati minn gvern iżda huma espressament mhux uffiċjali: awtentika
  hija biss il-gazzetta uffiċjali.
- Ftit sorsi mhumiex siti tal-gvern xejn (pereżempju LexiVox, LawPhil, Maqam, Wikisource).

Fontes iżid avviż "Unofficial source" ma' kull tweġiba li tiġi minn wieħed minn dawn. Qabel ma
tiċċita xi ħaġa, iċċekkja l-pubblikazzjoni uffiċjali. It-tabella tal-kopertura fir-
[README](README.md#kopertura) u `list_jurisdictions` isemmu s-sors għal kull ġurisdizzjoni.

## Liema ġurisdizzjonijiet ikopri, u kemm tajjeb?

125 adapter: 108 stati membri tan-NU, Hong Kong, il-Kosovo, il-Palestina, Taiwan, id-DIFC Courts, il-qrati statali tal-Istati Uniti u 11-il qorti u korp internazzjonali (bħall-Qorti Ewropea tad-Drittijiet tal-Bniedem, l-UE,
il-QIĠ u d-WTO).

Il-kopertura tvarja ħafna. Taħt regola stretta (il-preċedenti tal-ogħla qorti ġenerali, jew
il-kostituzzjoni u l-atti primarji, milħuqa għal kollox), 72 mill-125 jitqiesu koperti.
[COVERAGE.md](../../COVERAGE.md) jelenka, għal kull ġurisdizzjoni, x'jilħaq Fontes, x'ma jilħaqx,
u għaliex.

## Għandi bżonn ċavetta tal-API?

Għal kważi kull ġurisdizzjoni, le. Xi sorsi jeħtieġu ċavetta b'xejn: ara [KEYS.md](KEYS.md).

- **Franza:** iva. Franza hija mitfija sakemm ma tissettjax `WLM_FR_PISTE_CLIENT_ID` u
  `WLM_FR_PISTE_CLIENT_SECRET`. Dawn jiġu minn kont PISTE b'xejn (piste.gouv.fr) b'app abbonata
  għal Judilibre u Légifrance.
- **Stati Uniti:** mhux obbligatorja. It-tfittxija tal-ġurisprudenza taħdem mingħajr ċavetta,
  iżda ċ-ċavetta demo komuni tippermetti biss madwar 10 tfittxijiet kuljum għal kull indirizz IP.
  Ċavetta b'xejn ta' api.data.gov f'`WLM_US_GOVINFO_KEY` togħlih.
- **Il-qrati statali tal-Istati Uniti:** iva. Il-ġurisprudenza statali (`us-states`) hija mitfija sakemm ma tissettjax `WLM_US_COURTLISTENER_KEY` bit-token tal-API ta' CourtListener b'xejn tiegħek stess. CourtListener huwa mmexxi mill-organizzazzjoni mingħajr skop ta' qligħ Free Law Project; mhuwiex sors uffiċjali, u kull tweġiba tgħid hekk.

Issettja dawn bħala varjabbli tal-ambjent għas-server Fontes fis-settings MCP tal-app tiegħek.
L-installers jistaqsuk għalihom wara l-installazzjoni, u l-launcher tagħhom
**Add or change keys** jibdilhom aktar tard.

Separatament, ftit sorsi jgħidu fit-termini tagħhom li l-aċċess awtomatizzat jeħtieġ il-permess
tal-pubblikatur. Dawn huma mmarkati OFF u jibqgħu mitfija. Ċavetta ma tbiddilx dan; il-permess
tal-pubblikatur biss ibiddlu (imbagħad issettja `WLM_PERMITTED=<codes>`).

## X'joħroġ mill-kompjuter tiegħi?

It-tfittxijiet tiegħek imorru biss lis-sors li qed jiġi mfittex. Fontes ma jżomm l-ebda database
u ma jeħtieġ l-ebda kont.

Minbarra s-sorsi, Fontes jistaqsi lil PyPI darba kuljum jekk teżistix verżjoni ġdida (titfiha
b'`FONTES_NO_UPDATE_CHECK=1`). L-għadd tal-użu huwa mitfi sakemm ma tixgħlux int, u rapport ta'
żball jintbagħat biss wara li tkun rajtu u kkonfermajtu. L-app tal-AI tiegħek tara l-konversazzjoni
tiegħek taħt it-termini tagħha stess.

Dettalji sħaħ: [PRIVACY.md](PRIVACY.md).

## Dan huwa parir legali?

Le. Fontes huwa għodda tar-riċerka. Isib it-testi; ma jgħidlekx xi jfissru għall-każ tiegħek, u
l-użu tiegħu ma joħloq l-ebda relazzjoni bejn avukat u klijent ma' ħadd. L-app tal-AI tista'
taqra test ħażin, għalhekk aqra d-deċiżjoni jew id-dispożizzjoni kollha qabel ma tistrieħ fuqha.
Għal parir, staqsi avukat kwalifikat fejn tqum il-mistoqsija tiegħek.

## Min iżommu? Se jibqa' jaħdem?

Persuna waħda: Yüce Karapazar. M'hemm l-ebda kumpanija wara Fontes, l-ebda kuntratt ta' appoġġ
u l-ebda wegħda dwar il-livell tas-servizz. Ma jiġu offruti l-ebda servizzi legali.

Is-sorsi jiġu ċċekkjati darba kuljum u r-riżultati jiġu ppubblikati fuq
[il-paġna tal-istatus](https://ykarapazar.github.io/fontes/status/?lang=mt). Is-siti web tal-qrati
u tal-gvern jinbidlu mingħajr avviż, għalhekk sors jista' jieqaf jaħdem fi kwalunkwe ħin. M'hemm
l-ebda garanzija li xi sors, jew Fontes innifsu, se jibqa' jaħdem. Fontes huwa pprovdut "kif
inhu" ("as is"), mingħajr garanzija (it-taqsimiet 7 u 8 tal-[LICENSE](../../../LICENSE)).

## Test huwa ħażin jew mhux aġġornat, jew sors ma jaħdimx. Kif nirrappurtah?

- Iftaħ issue bil-formola "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Għid liema ġurisdizzjoni, x'staqsejt,
  x'ksibt, u l-paġna uffiċjali li turi t-test it-tajjeb.
- Jew staqsi lill-app tal-AI tiegħek biex "tirrapporta żball ta' Fontes" (jew ħaddem
  `fontes report-bug`). Tara r-rapport qabel ma jintbagħat xejn.
- Jew ibgħat email lil fontesmcp@proton.me.

Tinkludix dettalji tal-klijenti jew fatti kunfidenzjali f'rapport.

**Jekk tmexxi wieħed mis-sorsi** u xi ħaġa hija ħażina (it-termini tiegħek, ir-robots.txt
tiegħek, il-limiti tar-rati tiegħek), ibgħat email lil fontesmcp@proton.me. Is-sors jiġi
rranġat jew mitfi.

## Kif inhu differenti Fontes minn għodod tar-riċerka legali ospitati?

- **Jaħdem fuq il-kompjuter tiegħek.** M'hemm l-ebda server ta' Fontes u l-ebda kont. Dan ifisser
  ukoll li jaħdem biss f'apps li jistgħu jibdew server MCP lokali (Claude Desktop, Codex, Cursor,
  VS Code u simili), mhux f'apps tal-web biss li jaċċettaw biss connectors ospitati.
- **M'għandux database.** Kull tfittxija tmur direttament fuq is-sit web jew l-API
  tal-pubblikatur innifsu, għalhekk ir-riżultati huma aġġornati daqs is-sors, u l-kwalità
  tat-tfittxija hija dik tas-sors stess. M'hemm l-ebda tfittxija semantika fuq indiċi kkurat.
- **Ma jimponi l-ebda limitu tal-użu.** Fontes m'għandux limitu ta' kull xahar fuq is-sejħiet.
  Jispazja t-talbiet tiegħu lil kull sit web, u xi sorsi jillimitaw kemm malajr jew kemm-il darba
  jistgħu jiġu mfittxija.
- **Huwa open source.** Tista' taqra kull adapter u tara eżattament minn fejn jiġi kull test.
- **M'hemm l-ebda fornitur warajh.** L-ebda kuntratt, desk tal-appoġġ jew wegħda dwar l-uptime
  (ara "Min iżommu?").

## Ma' liema apps u sistemi jaħdem?

Kwalunkwe app MCP li tista' tħaddem server lokali (stdio), pereżempju Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio u Cline. Fontes
jaħdem fuq macOS, Windows u Linux, kull fejn jaħdem uv (Python 3.13+). Fuq Mac jew PC Windows, installer bi klikk
waħda jissettja Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio
u Cline f'daqqa. Il-passi għal kull app: [INSTALL.md](INSTALL.md).

## Nista' nikkontribwixxi kodiċi?

Mhux bħalissa. Issues, rapporti dwar is-sorsi u talbiet għal ġurisdizzjonijiet ġodda huma
milqugħa. Ara [CONTRIBUTING.md](../../../CONTRIBUTING.md).
