> Ito ay salin na ginawa sa tulong ng makina. Ang bersyong Ingles ang may bisa.

# Mga API key

Gumagana nang walang key ang halos bawat sanggunian sa Fontes. Dalawa ang nangangailangan ng libreng key:

| Key | Binubuksan | Kung wala ito |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | France: Judilibre (mga desisyon ng korte) at Légifrance (lehislasyon) | Naka-off ang France. Ipinapakita ito ng `list_jurisdictions` bilang hindi aktibo. |
| `WLM_US_GOVINFO_KEY` | United States: paghahanap sa govinfo (mga opinyon ng federal court, Statutes at Large, public laws) | Ginagamit ng Fontes ang shared na `DEMO_KEY`: mga 10 paghahanap bawat araw bawat IP address. Hindi kailangan ng key para magbukas ng kilalang desisyon at ng US Code. |

Opsyonal ang mga key. Maaari mo itong idagdag sa ibang pagkakataon.

## Pagdaragdag ng key

**Gamit ang installer.** Kapag na-set up na ang Fontes, nag-aalok ang installer na magdagdag ng mga key.
Sa Mac, i-click ang **Magdagdag ng mga key**, o ang **Tapos na** para laktawan; sa Windows, sagutin ang
tanong (pindutin ang Enter para laktawan). Para magdagdag o magpalit ng mga key sa ibang pagkakataon,
patakbuhin ang **Add or change keys**:

- Mac: buksang muli ang Fontes Installer app at piliin ang **Magdagdag o magpalit ng mga key**.
- Windows: buksan ang Start menu, pagkatapos **Fontes** → **Magdagdag o magpalit ng mga key**.

Nakatago ang tina-type. Para sa bawat key: i-paste ito, pindutin ang Enter para panatilihin ang naroon na, o
i-type ang `-` para alisin ito. Napupunta ang mga key sa bawat app na mayroon nang Fontes.

**Gamit ang Claude Desktop extension (.mcpb).** Buksan ang Claude > Settings > Extensions > Fontes at punan
ang mga field. Opsyonal ang lahat ng ito.

**Nang mano-mano.** Idagdag ang mga variable sa `env` block ng `fontes` entry sa MCP config ng iyong app:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

I-restart ang app pagkatapos ng anumang pagbabago.

## France: PISTE (libre)

1. Gumawa ng account sa [piste.gouv.fr](https://piste.gouv.fr). Nangangahulugan ito ng pagtanggap sa mga
   tuntunin ng PISTE (CGU).
2. Pumunta sa API > **Consentement CGU API**. Tanggapin ang mga tuntunin para sa **JUDILIBRE** at
   **Légifrance** (production).
3. Gumawa ng **production application**. Hindi makakaabot sa production ang `APP_SANDBOX` na ginawa para sa
   iyo. Sa ilalim ng "Modifier l'application", lagyan ng tsek ang **JUDILIBRE (production)** at
   **Légifrance (production)**, at saka i-apply.
4. Buksan ang tab na **Authentification** ng app. Kopyahin ang `client_id` at ang `client_secret`.
5. Patakbuhin ang **Add or change keys** at i-paste ang mga ito.

Ang mga tuntunin, sa madaling sabi:

- Data: Licence Ouverte / Etalab 2.0. Pinapayagan ang muling paggamit, kasama ang komersyal na muling
  paggamit, nang may atribusyon.
- Huwag ilathala o ibahagi ang iyong mga credential. Sabihan ang PISTE kung na-leak ang mga ito.
- Ang Légifrance API ay isang beta na serbisyo. Maaari itong suspindihin, at may mga quota ito (bawat
  segundo, minuto at araw).
- Hindi ang awtentikong bersyon ang mga teksto ng Légifrance. Ang nilagdaang PDF ng Journal officiel lamang
  ang awtentiko.
- Judilibre: huwag gamitin ang mga pangalan ng mga hukom o clerk para suriin, ihambing o hulaan ang kanilang
  trabaho (Code de l'organisation judiciaire art. L111-13; isang kriminal na pagkakasala).
- Judilibre: sundin ang GDPR. Huwag subukang muling tukuyin ang pagkakakilanlan ng mga partido.

Nasa PISTE ang iyong mga quota sa ilalim ng API Sélectionnées > Actions > Consulter les quotas.

## United States: api.data.gov (libre)

1. Pumunta sa [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ipinapakita ang key sa screen)
   o sa [api.data.gov/signup](https://api.data.gov/signup/) (ipinapadala sa iyo ang key sa email).
2. Ilagay ang iyong pangalan at email. Opsyonal ang field na "how will you use it".
3. Kopyahin ang 40-character na key.
4. Patakbuhin ang **Add or change keys** at i-paste ito bilang US key.

Ang mga tuntunin, sa madaling sabi:

- Gamit ang sarili mong key, nagpapahintulot ang govinfo ng hanggang 36,000 request bawat oras.
- Wala kaming nakitang terms of service na partikular sa API (hindi umiiral ang api.data.gov/terms/).
  Hindi pa napatutunayan. Tingnan ang [mga patakaran ng govinfo](https://www.govinfo.gov/about/policies) at
  ang [privacy policy ng data.gov](https://data.gov/privacy-policy/).
- Itago ang key para sa iyong sarili.

## Saan iniimbak ang mga key

- **Installer o mano-mano:** bilang plain text sa MCP config file ng bawat app, sa `env` block ng `fontes`
  entry. Mababasa ng sinumang makakabasa ng iyong mga user file ang mga key.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` o `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop extension (.mcpb):** iniingatan ng Claude ang mga field na ito sa mga setting nito at
  pinoprotektahan ang mga ito gamit ang secure storage ng iyong system (Keychain sa Mac, Credential Manager
  sa Windows).

Bago ang bawat pagbabago, nagse-save ang installer ng kopya ng config file sa tabi nito
(`<file>.fontes-backup-<time>`). Naglalaman din ng mga key ang mga kopyang ginawa pagkatapos mong magdagdag ng
mga key. Burahin ang mga lumang kopya na hindi mo kailangan.

## Pagpapalit o pag-alis ng key

- Patakbuhin ang **Add or change keys**. Mag-paste ng bagong key para palitan ito, o i-type ang `-` para
  alisin ito.
- O i-edit nang mano-mano ang `env` block at i-restart ang app.
- Ang pag-uninstall sa Fontes ay nag-aalis ng buong entry nito, kasama ang mga key. Hindi nito binubura ang
  mga backup na kopya.
- Kung na-leak ang isang key, palitan din ito sa sanggunian: sa PISTE, gumawa ng mga bagong credential para
  sa iyong app; para sa api.data.gov, mag-sign up para sa bagong key.

## Mga mensaheng maaari mong makita

| Mensahe | Kahulugan |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Walang key para sa France. Magdagdag ng isa. |
| `Inactive: needs a free PISTE account. ...` (sa `list_jurisdictions`) | Pareho. |
| `PISTE refused the client credentials ...` | Mali o hindi na valid ang ID o ang secret. Kopyahin muli ang dalawa mula sa tab na Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Hindi naka-subscribe ang iyong app sa API na iyon, o hindi mo pa tinatanggap ang mga tuntunin nito. Tingnan ang mga hakbang 2 at 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Walang US key. Gumagana ang paghahanap para sa ilang tawag bawat araw. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Naubos na ang demo key. Idagdag ang sarili mong key. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Mali ang key, o hindi pa nakukumpirma mula sa email. |

Ang walang lamang value ay itinuturing na walang key.

## Mga pahintulot (WLM_PERMITTED)

Hindi ito isang API key, at hindi ito itinatakda ng installer. **Itakda lamang ito kung ikaw mismo ang may
hawak ng pahintulot na iyon.**

Naka-off bilang default ang ilang sanggunian dahil ipinagbabawal ng kanilang mga tuntunin o robots.txt ang
awtomatikong paggamit nang walang pahintulot. Kung may pahintulot ka mula sa tagapaglathala, i-on ang isang
sanggunian sa pamamagitan ng pagdaragdag ng code nito sa `WLM_PERMITTED`, na pinaghihiwalay ng kuwit, sa `env`
block: `"WLM_PERMITTED": "in,de"`.

| Code | Sanggunian |
|---|---|
| `az` | Azerbaijan: e-qanun.az (Ministry of Justice) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (consolidated na lehislasyon) |
| `de` | Germany: NeuRIS (pederal na portal ng legal na impormasyon, serbisyong pansubok) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Greece: National Printing Office, paghahanap sa Government Gazette (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: mga hatol ng korte (elitigation.sg) |

Kung walang pahintulot, sinasabi ng Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
