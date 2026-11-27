> Lii ab tekki la bu masin dimbali. Mbind mu Àngale mi moo am sañ-sañ.

# Caabi API

Lu ëpp ci cosaan yi ci Fontes dañuy dox te amuñu caabi. Ñett soxla nañu caabi bu ñu joxe ci neen:

| Caabi | Li muy ubbi | Su amul |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Faraas: Judilibre (àtte yi) ak Légifrance (yoon yi) | Faraas dafa fey. `list_jurisdictions` dafay won ne doxul. |
| `WLM_US_GOVINFO_KEY` | Etaa-Sini: gëstu ci govinfo (àtte yu àttekaay federaal yi, Statutes at Large, public laws) | Fontes dafay jëfandikoo caabi `DEMO_KEY` bi ñuy bokk: lu tollu ci 10 gëstu ci bés bi ci adrees IP bu nekk. Ngir ubbi ab àtte boo xam ba noppi ak US Code, soxlaa caabi. |
| `WLM_US_COURTLISTENER_KEY` | Àttekaay yu stat yu Etaa-Sini yi (`us-states`): àtte yu àttekaay yu kawe yi ak yu ñuy dellu ci yépp ci 50 stat yi ak DC, jóge ci CourtListener | Àtte yu stat yu Etaa-Sini yi dafay fey. `list_jurisdictions` dafay wone ni dafa tëj. |

Caabi yi, su la neexee lañu. Mën nga leen yokk ginnaaw.

## Yokk ab caabi

**Ak programu samp bi.** Bu Fontes sampu ba noppi, programu samp bi dafay la laaj ndax mu yokk ay caabi.
Ci Mac, cuqal **Yokk caabi yi**, walla **Jeex na** ngir bàyyi ko; ci Windows, tontu laaj bi (bësal Enter ngir
bàyyi ko). Ngir yokk walla soppi caabi yi ginnaaw, doxal **Yokk walla soppi caabi yi**:

- Mac: ubbiwaatal aplikasioŋ Fontes Installer te tànn **Yokk walla soppi caabi yi**.
- Windows: ubbil menu Start, ba noppi **Fontes** → **Yokk walla soppi caabi yi**.

Li ngay bind dafa nëbbu. Ci caabi bu nekk: tafal ko, bës Enter ngir denc li fi nekk, walla bind `-` ngir
dindi ko. Caabi yi dañuy dugg ci bépp aplikasioŋ bu am Fontes ba noppi.

**Ak extension Claude Desktop bi (.mcpb).** Ubbil Claude > Settings > Extensions > Fontes te fees
barab yi. Yépp, su la neexee lañu.

**Ak loxo.** Yokkal variables yi ci bloc `env` bu xaaju `fontes` bi ci réglage MCP yu sa aplikasioŋ:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Tàmbaliwaatal aplikasioŋ bi ginnaaw bépp coppite.

## Faraas: PISTE (ci neen)

1. Sosal ab kontu ci [piste.gouv.fr](https://piste.gouv.fr). Loolu dafay tekki ne nangu nga sàrti PISTE
   yi (CGU).
2. Demal ci API > **Consentement CGU API**. Nangul sàrt yi ngir **JUDILIBRE** ak **Légifrance** (production).
3. Sosal ab **aplikasioŋ production**. `APP_SANDBOX` bi ñu la sosal mënul a jot ci production.
   Ci "Modifier l'application", tànnal **JUDILIBRE (production)** ak **Légifrance (production)**, te
   jëfandikoo ko.
4. Ubbil onglet **Authentification** bu aplikasioŋ bi. Kopil `client_id` ak `client_secret`.
5. Doxal **Yokk walla soppi caabi yi** te tafal leen.

Sàrt yi, ci lu gàtt:

- Done yi: Licence Ouverte / Etalab 2.0. Mën nga leen jëfandikoowaat, ak ngir njaay itam, su nga tuddee
  cosaan bi.
- Bul siiwal te bul séddoo say xàmmeekaay. Yégal PISTE su ñu rotee.
- API Légifrance ab liggéey bu ñuy jéem (bêta) la. Mën na taxaw, te am na ay dayo (ci seconde, ci minit
  ak ci bés).
- Mbind yu Légifrance duñu sumb bu dëggu bi. PDF bu Journal officiel bi ñu xaatim rekk moo dëggu.
- Judilibre: bul jëfandikoo turu àttekat yi walla greffier yi ngir natt, méngale walla wax lu jiitu ci seen
  liggéey (Code de l'organisation judiciaire art. L111-13; tooñ la bu yoonu mbugal di mbugal).
- Judilibre: toppal GDPR. Bul jéem a xàmmeewaat ñi bokk ci mbir mi.

Say dayo ci PISTE ñu ngi ci API Sélectionnées > Actions > Consulter les quotas.

## Etaa-Sini: api.data.gov (ci neen)

1. Demal ci [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (caabi bi dafay feeñ ci
   ekraŋ bi) walla ci [api.data.gov/signup](https://api.data.gov/signup/) (dañu lay yónnee caabi bi ci
   imeel).
2. Bindal sa tur ak sa imeel. Barab "how will you use it" bi, su la neexee la.
3. Kopil caabi bu am 40 araf bi.
4. Doxal **Yokk walla soppi caabi yi** te tafal ko ni caabi Etaa-Sini.

Sàrt yi, ci lu gàtt:

- Ak sa caabi ci boppam, govinfo dafay may ba 36,000 laaj ci waxtu wi.
- Gisunu benn sàrt bu jëfandikoo bu API bi ci boppam (api.data.gov/terms/ amul). Saytuwuñu ko.
  Xoolal [politik yu govinfo](https://www.govinfo.gov/about/policies) ak
  [politik sutura bu data.gov](https://data.gov/privacy-policy/).
- Denc caabi bi ci sa bopp.

## Àttekaay yu stat yu Etaa-Sini yi: CourtListener (ci neen)

[Free Law Project](https://free.law) mooy dugal CourtListener, mbootaay (non-profit) bu amul njariñ, bu nga xam ne dafa dajale àtte yu àttekaay yu Etaa-Sini yi ca atum 2010 te di leen joxe ñépp ci neen. Ni mu ko tërale boppam, am na ci ay àtte yu ëpp ñeent-fukk ak juroom-benn milyoŋ. Du cosaan bu am sañ-sañ: àttekaay yi ñoo bokk di wàcce seeni àtte, te CourtListener dafay leen dajale ci sàmmu web yu àttekaay yi ak ci téereem àtte yi ñu skane. Tontu bu nekk bu Fontes jële ca moom dafay wax loolu. Fontes dafa bokkul ak Free Law Project.

1. Sosal ab kontu bu ñu joxe ci neen ci [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Ubbil sa profil te kopil sa token API.
3. Doxal **Yokk walla soppi caabi yi** te tafal ko ni caabi CourtListener.

Sàrt yi, ci lu gàtt ([sàrt yépp](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token bi say yaw rekk la: bu ko séddoo, bu ko boole ak yeneen, bu ko jaaye, te bu jëfandikoo ay kontu yu bari.
- Yaw ngay tontu ci li aplikasioŋ AI di def ak sa token.
- Bul wone ne Free Law Project moo defar, nangu walla seet xam-xam bu AI mi def ci seeni donne.
- Kontu bu ñu joxe ci neen dafay may 5 laaj ci simili, 50 ci waxtu, ak 125 ci bés. Wut bi benn laaj la; ubbi àtte bi ñaar la. Bokk ci Free Law Project dafay yokk dayo yi.
- CourtListener du wóor ne lépp dëgg la. Seetal àtte bi ci kopi àttekaay bi laata nga koy sukkandikoo.

## Fu ñuy denc caabi yi

- **Ak programu samp bi walla ak loxo:** ci mbind mu ñépp mën a jàng ci fichier réglage MCP bu
  aplikasioŋ bu nekk, ci bloc `env` bu xaaju `fontes` bi. Ku mën a jàng say fichier mën na jàng caabi yi.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` walla `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Extension Claude Desktop bi (.mcpb):** Claude dafay denc barab yooyu ci réglage-am te aar leen ak
  denckaay bu kaaraange bu sa sistem (Keychain ci Mac, Credential Manager ci Windows).

Balaa bépp coppite, programu samp bi dafay denc ab kopi bu fichier réglage bi ci wetam
(`<file>.fontes-backup-<time>`). Kopi yi ñu def ginnaaw bi nga yokkee caabi yi am nañu caabi yooyu itam.
Faral kopi yu yàgg yi nga soxlaatul.

## Soppi walla dindi ab caabi

- Doxal **Yokk walla soppi caabi yi**. Tafal ab caabi bu bees ngir wuutal ko, walla bind `-` ngir dindi ko.
- Walla soppil bloc `env` bi ak loxo te tàmbaliwaat aplikasioŋ bi.
- Dindi Fontes dafay dindi xaajam bépp, ak caabi yi. Du far kopi yi ñu denc.
- Su ab caabi rotee, wuutal ko itam ci cosaan bi: ci PISTE, sosal ay xàmmeekaay yu bees ngir sa
  aplikasioŋ; ci api.data.gov, binduwaatal ngir am caabi bu bees.

## Bataaxal yi nga mën a gis

| Bataaxal | Li muy tekki |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Amul caabi Faraas. Yokkal benn. |
| `Inactive: needs a free PISTE account. ...` (ci `list_jurisdictions`) | Benn la. |
| `PISTE refused the client credentials ...` | ID bi walla secret bi baaxul walla jeex na. Kopiwaatal ñoom ñaar ci onglet Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Sa aplikasioŋ binduwul ci API boobu, walla nanguloo seeni sàrt. Xoolal tànk 2 ak 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Amul caabi Etaa-Sini. Gëstu bi dafay dox ci ay woote yu néew ci bés bi. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Caabi demo bi jeex na. Yokkal sa caabi ci boppam. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Caabi bi baaxul, walla dëggaloo ko ci imeel bi. |

Ab barab bu amul dara, dañu koy lim ni amul caabi.

## Sañ-sañ (WLM_PERMITTED)

Lii du caabi API, te programu samp bi du ko def. **Defal ko rekk su fekkee yaw ci sa bopp am nga sañ-sañ
boobu.**

Am na ay cosaan yu fey ci njëlbéen ndax seeni sàrt walla seen robots.txt dañu tere jëfandikoo ci masin bu
amul sañ-sañ. Su am nga sañ-sañu ki siiwal, taalal ab cosaan ci yokk koodam ci `WLM_PERMITTED`, ñu xaajale
leen ak virgule, ci bloc `env` bi: `"WLM_PERMITTED": "in,de"`.

| Kood | Cosaan |
|---|---|
| `az` | Aserbayjaan: e-qanun.az (Ministeeru Yoon) |
| `bh` | Bahreyn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolombi: Función Pública, Gestor Normativo (yoon yu ñu yeesal) |
| `de` | Almaañ: NeuRIS (portail federaal bu xibaaru yoon, liggéey bu ñuy jéem) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Gerees: Imprimerie nationale, gëstu ci Journal officiel (search.et.gr) |
| `in` | Inde: India Code (indiacode.gov.in) |
| `mu` | Moris: Àttekaay bu Kawe (supremecourt.govmu.org) |
| `sg` | Singapuur: àtte yu àttekaay yi (elitigation.sg) |

Su amul sañ-sañ, Fontes dafay wax: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
