# API keys

Almost every source in Fontes works without a key. Two need a free one:

| Key | Unlocks | Without it |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | France: Judilibre (court decisions) and Légifrance (legislation) | France is off. `list_jurisdictions` shows it as inactive. |
| `WLM_US_GOVINFO_KEY` | United States: govinfo search (federal court opinions, Statutes at Large, public laws) | Fontes uses the shared `DEMO_KEY`: about 10 searches a day per IP address. Opening a known decision and the US Code need no key. |

Keys are optional. You can add them later.

## Adding a key

**With the installer.** Once Fontes is set up, the installer offers to add keys. On a Mac, click
**Add keys**, or **Done** to skip; on Windows, answer the question (press Enter to skip). To add
or change keys later, run **Add or change keys**:

- Mac: open the Fontes Installer app again and choose **Add or change keys**.
- Windows: double-click `Add or change keys.cmd` in the installer folder. The Windows setup
  program, once available, also puts it in Start menu > Fontes.

Typing is hidden. For each key: paste it, press Enter to keep what is there, or type `-` to
remove it. The keys go into every app that already has Fontes.

**With the Claude Desktop extension (.mcpb).** Open Claude > Settings > Extensions > Fontes and
fill in the fields. All of them are optional.

**By hand.** Add the variables to the `env` block of the `fontes` entry in your app's MCP config:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Restart the app after any change.

## France: PISTE (free)

1. Create an account at [piste.gouv.fr](https://piste.gouv.fr). This means accepting the PISTE terms (CGU).
2. Go to API > **Consentement CGU API**. Accept the terms for **JUDILIBRE** and **Légifrance** (production).
3. Create a **production application**. The `APP_SANDBOX` made for you cannot reach production.
   Under "Modifier l'application", tick **JUDILIBRE (production)** and **Légifrance (production)**, then apply.
4. Open the app's **Authentification** tab. Copy the `client_id` and the `client_secret`.
5. Run **Add or change keys** and paste them.

Terms, in short:

- Data: Licence Ouverte / Etalab 2.0. Reuse, including commercial reuse, is allowed with attribution.
- Do not publish or share your credentials. Tell PISTE if they leak.
- The Légifrance API is a beta service. It may be suspended, and it has quotas (per second, minute and day).
- Légifrance texts are not the authentic version. Only the signed Journal officiel PDF is.
- Judilibre: do not use judges' or clerks' names to evaluate, compare or predict their work
  (Code de l'organisation judiciaire art. L111-13; a criminal offence).
- Judilibre: follow the GDPR. Do not try to re-identify the parties.

Your quotas are on PISTE under API Sélectionnées > Actions > Consulter les quotas.

## United States: api.data.gov (free)

1. Go to [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (the key is shown on screen)
   or [api.data.gov/signup](https://api.data.gov/signup/) (the key is emailed to you).
2. Enter your name and email. The "how will you use it" field is optional.
3. Copy the 40-character key.
4. Run **Add or change keys** and paste it as the US key.

Terms, in short:

- With your own key, govinfo allows up to 36,000 requests an hour.
- We found no API-specific terms of service (api.data.gov/terms/ does not exist). Unverified.
  See [govinfo's policies](https://www.govinfo.gov/about/policies) and the
  [data.gov privacy policy](https://data.gov/privacy-policy/).
- Keep the key to yourself.

## Where keys are stored

- **Installer or by hand:** as plain text in each app's MCP config file, in the `env` block of the
  `fontes` entry. Anyone who can read your user files can read the keys.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` or `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop extension (.mcpb):** Claude keeps these fields in its settings and protects them
  with your system's secure storage (Keychain on Mac, Credential Manager on Windows).

Before each change, the installer saves a copy of the config file next to it
(`<file>.fontes-backup-<time>`). Copies made after you added keys contain the keys too. Delete old
copies you do not need.

## Changing or removing a key

- Run **Add or change keys**. Paste a new key to replace it, or type `-` to remove it.
- Or edit the `env` block by hand and restart the app.
- Uninstalling Fontes removes its whole entry, keys included. It does not delete the backup copies.
- If a key leaked, also replace it at the source: on PISTE, make new credentials for your app;
  for api.data.gov, sign up for a new key.

## Messages you may see

| Message | Meaning |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | No France key. Add one. |
| `Inactive: needs a free PISTE account. ...` (in `list_jurisdictions`) | Same. |
| `PISTE refused the client credentials ...` | The ID or secret is wrong or no longer valid. Copy both again from the Authentification tab. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Your app is not subscribed to that API, or you have not accepted its terms. See steps 2 and 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | No US key. Search works for a few calls a day. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | The demo key is used up. Add your own key. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | The key is wrong, or not yet confirmed from the email. |

An empty value counts as no key.

## Permissions (WLM_PERMITTED)

This is not an API key, and the installer does not set it. **Set it only if you hold that
permission yourself.**

Some sources are off by default because their terms or robots.txt forbid automated use without
permission. If you have permission from the publisher, turn a source on by adding its code to
`WLM_PERMITTED`, comma-separated, in the `env` block: `"WLM_PERMITTED": "in,de"`.

| Code | Source |
|---|---|
| `az` | Azerbaijan: e-qanun.az (Ministry of Justice) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (consolidated legislation) |
| `de` | Germany: NeuRIS (federal legal information portal, trial service) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Greece: National Printing Office, Government Gazette search (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: court judgments (elitigation.sg) |

Without permission, Fontes says: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
