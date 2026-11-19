> Ito ay salin na ginawa sa tulong ng makina. Ang bersyong Ingles ang may bisa.

# Fontes: mga tanong at sagot

## Ano ang Fontes?

Isang libre at open-source na MCP server (Apache 2.0). Binibigyang-daan nito ang anumang app na gumagamit ng
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI at iba pa) na maghanap ng mga desisyon ng
korte at lehislasyon nang live sa mga website ng mga korte at ng pamahalaan sa 120+ hurisdiksyon at
internasyonal na korte (124 adapter). Bawat resulta ay nagsasaad ng sanggunian nito at may link sa orihinal.

## Opisyal ba ang mga teksto?

Kadalasan, pero hindi palagi.

- Karamihan ng mga sanggunian ay pinapatakbo ng isang korte, isang ministri o isang opisyal na gazette.
- Ang ilang consolidated na teksto ay inilalathala ng pamahalaan pero tahasang hindi opisyal: ang opisyal na
  gazette lamang ang awtentiko.
- May ilang sanggunian na hindi talaga site ng pamahalaan (halimbawa LexiVox, LawPhil, Maqam, Wikisource).

Nagdaragdag ang Fontes ng abisong "Hindi opisyal na sanggunian" sa bawat sagot na nagmumula sa isa sa mga ito.
Bago ka sumipi ng anuman, suriin ang opisyal na publikasyon. Pinapangalanan ng talahanayan ng saklaw sa
[README](README.md#saklaw) at ng `list_jurisdictions` ang sanggunian para sa bawat hurisdiksyon.

## Aling mga hurisdiksyon ang saklaw nito, at gaano kahusay?

124 adapter: 108 UN member state, Hong Kong, Kosovo, Palestine, Taiwan, ang DIFC Courts at
11 internasyonal na korte at katawan (tulad ng European Court of Human Rights, ng EU, ng ICJ at ng WTO).

Malaki ang pagkakaiba ng saklaw. Sa ilalim ng isang mahigpit na patakaran (ang mga precedent ng pinakamataas
na pangkalahatang korte, o ang konstitusyon at mga pangunahing batas, na naaabot nang buo), 72 sa 124 ang
itinuturing na saklaw. Inililista ng [COVERAGE.md](COVERAGE.md), para sa bawat hurisdiksyon, kung ano ang
naaabot ng Fontes, kung ano ang hindi, at bakit.

## Kailangan ko ba ng API key?

Para sa halos bawat hurisdiksyon, hindi. Kailangan ng ilang sanggunian ng libreng key: tingnan ang
[KEYS.md](KEYS.md).

- **France:** oo. Naka-off ang France hanggang itakda mo ang `WLM_FR_PISTE_CLIENT_ID` at
  `WLM_FR_PISTE_CLIENT_SECRET`. Nagmumula ang mga ito sa isang libreng PISTE account (piste.gouv.fr) na may app
  na naka-subscribe sa Judilibre at Légifrance.
- **United States:** opsyonal. Gumagana ang paghahanap ng jurisprudence nang walang key, pero ang shared na
  demo key ay nagpapahintulot lamang ng mga 10 paghahanap bawat araw bawat IP address. Tinataasan ito ng
  isang libreng api.data.gov key sa `WLM_US_GOVINFO_KEY`.

Itakda ang mga ito bilang mga environment variable para sa Fontes server sa mga MCP setting ng iyong app.
Kapag nailabas na ang installer, hihingin nito ang mga ito pagkatapos mag-install, at ang launcher nitong
**Add or change keys** ang magpapalit sa mga ito sa ibang pagkakataon.

Hiwalay rito, may ilang sanggunian na nagsasabi sa kanilang mga tuntunin na kailangan ng pahintulot ng
tagapaglathala para sa awtomatikong pag-access. May markang OFF ang mga ito at nananatiling naka-off. Hindi ito
binabago ng isang key; ang pahintulot lamang ng tagapaglathala ang nagbabago nito (pagkatapos ay itakda ang
`WLM_PERMITTED=<codes>`).

## Ano ang lumalabas sa aking computer?

Napupunta lamang ang iyong mga paghahanap sa sanggunian na hinahanapan. Walang iniimbak na database ang Fontes
at hindi ito nangangailangan ng account.

Bukod sa mga sanggunian, tinatanong ng Fontes ang PyPI minsan sa isang araw kung may mas bagong bersyon
(i-off ito gamit ang `FONTES_NO_UPDATE_CHECK=1`). Naka-off ang bilang ng paggamit maliban kung i-on mo, at
ipinapadala lamang ang isang bug report pagkatapos mo itong makita at kumpirmahin. Nakikita ng iyong AI app
ang iyong pag-uusap sa ilalim ng sarili nitong mga tuntunin.

Buong detalye: [PRIVACY.md](PRIVACY.md).

## Legal na payo ba ito?

Hindi. Ang Fontes ay isang tool sa pananaliksik. Naghahanap ito ng mga teksto; hindi nito sinasabi sa iyo kung
ano ang kahulugan ng mga ito para sa iyong kaso, at ang paggamit nito ay hindi lumilikha ng ugnayang
abogado–kliyente sa sinuman. Maaaring mali ang pagkabasa ng AI app sa isang teksto, kaya basahin nang buo ang
desisyon o probisyon bago ka umasa rito. Para sa payo, magtanong sa isang abogadong kwalipikado sa lugar kung
saan lumilitaw ang iyong tanong.

## Sino ang nagpapanatili nito? Patuloy ba itong gagana?

Iisang tao: si Yüce Karapazar. Walang kumpanya sa likod ng Fontes, walang kontrata ng suporta at walang
pangako sa antas ng serbisyo. Walang inaalok na serbisyong legal.

Sinusuri ang mga sanggunian minsan sa isang araw at inilalathala ang mga resulta sa
[status page](https://ykarapazar.github.io/fontes/status/?lang=fil). Nagbabago ang mga website ng korte at ng
pamahalaan nang walang abiso, kaya maaaring masira ang isang sanggunian anumang oras. Walang garantiya na
patuloy na gagana ang anumang sanggunian, o ang Fontes mismo. Ibinibigay ang Fontes "as is", nang walang
warranty (mga seksyon 7 at 8 ng [LICENSE](../../../LICENSE)).

## Mali o luma ang isang teksto, o sira ang isang sanggunian. Paano ko ito iuulat?

- Magbukas ng issue gamit ang form na "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Sabihin kung aling hurisdiksyon, ano ang itinanong
  mo, ano ang nakuha mo, at ang opisyal na pahinang nagpapakita ng tamang teksto.
- O hilingin sa iyong AI app na "mag-ulat ng bug sa Fontes" (o patakbuhin ang `fontes report-bug`). Makikita
  mo ang report bago may maipadala.
- O mag-email sa fontesmcp@proton.me.

Huwag maglagay ng mga detalye ng kliyente o kumpidensyal na impormasyon sa isang report.

**Kung pinapatakbo mo ang isa sa mga sanggunian** at may mali (ang iyong mga tuntunin, ang iyong robots.txt,
ang iyong mga rate limit), mag-email sa fontesmcp@proton.me. Aayusin o io-off ang sanggunian.

## Paano naiiba ang Fontes sa mga naka-host na tool sa legal na pananaliksik?

- **Tumatakbo ito sa iyong computer.** Walang Fontes server at walang account. Nangangahulugan din ito na
  gumagana lamang ito sa mga app na kayang magsimula ng lokal na MCP server (Claude Desktop, Codex, Cursor,
  VS Code at mga katulad nito), hindi sa mga web-only na app na tumatanggap lamang ng mga naka-host na
  connector.
- **Wala itong database.** Direktang napupunta nang live ang bawat paghahanap sa sariling website o API ng
  tagapaglathala, kaya kasing-bago ng sanggunian ang mga resulta, at ang kalidad ng paghahanap ay ang sa
  sanggunian mismo. Walang semantic search sa isang piniling index.
- **Wala itong itinatakdang limitasyon sa paggamit.** Walang buwanang limitasyon sa mga tawag ang Fontes.
  Nilalagyan nito ng pagitan ang mga request nito sa bawat website, at nililimitahan ng ilang sanggunian kung gaano
  kabilis o kadalas sila maaaring tanungin.
- **Open source ito.** Mababasa mo ang bawat adapter at makikita mo kung saan eksaktong nagmumula ang bawat
  teksto.
- **Walang vendor sa likod nito.** Walang kontrata, support desk o pangako sa uptime (tingnan ang "Sino ang
  nagpapanatili nito?").

## Aling mga app at system ang gumagana rito?

Anumang MCP app na kayang magpatakbo ng lokal (stdio) na server, halimbawa Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio at Cline. Tumatakbo ang Fontes
sa macOS, Windows at Linux, saanman tumatakbo ang uv (Python 3.13+). Sa Mac o Windows PC, sine-set up ng one-click installer
ang Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio at Cline
nang sabay-sabay. Mga hakbang para sa bawat app: [INSTALL.md](INSTALL.md).

## Maaari ba akong mag-ambag ng code?

Hindi sa ngayon. Tinatanggap ang mga issue, ulat tungkol sa mga sanggunian at kahilingan para sa mga
hurisdiksyon. Tingnan ang [CONTRIBUTING.md](../../../CONTRIBUTING.md).
