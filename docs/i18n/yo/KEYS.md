> Ìtúmọ̀ yìí ni a ṣe pẹ̀lú ìrànlọ́wọ́ ẹ̀rọ. Ẹ̀dà Gẹ̀ẹ́sì ni ó ní àṣẹ.

# Àwọn kọ́kọ́rọ́ API

Fere gbogbo orísun nínú Fontes ń ṣiṣẹ́ láìsí kọ́kọ́rọ́. Méjì nílò kọ́kọ́rọ́ ọ̀fẹ́:

| Kọ́kọ́rọ́ | Ohun tí ó ń ṣí | Láìsí i |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | France: Judilibre (ìdájọ́ ilé-ẹjọ́) àti Légifrance (òfin) | France wà ní pípa. `list_jurisdictions` ń fi í hàn gẹ́gẹ́ bí èyí tí kò ṣiṣẹ́. |
| `WLM_US_GOVINFO_KEY` | United States: ìwádìí govinfo (èrò ilé-ẹjọ́ àpapọ̀, Statutes at Large, public laws) | Fontes ń lo `DEMO_KEY` tí a pín: ìwádìí bíi 10 lójoojúmọ́ fún àdírẹ́sì IP kọ̀ọ̀kan. A kò nílò kọ́kọ́rọ́ láti ṣí ìdájọ́ tí a mọ̀ àti US Code. |

Àwọn kọ́kọ́rọ́ kò pọn dandan. O lè fi wọ́n kún un lẹ́yìn náà.

## Fífi kọ́kọ́rọ́ kún un

**Pẹ̀lú ẹ̀rọ ìfisílẹ̀.** Lẹ́yìn tí a bá ti ṣètò Fontes, ẹ̀rọ ìfisílẹ̀ yóò fún ọ ní àǹfààní láti fi
kọ́kọ́rọ́ kún un. Lórí Mac, tẹ **Fi kọ́kọ́rọ́ kún**, tàbí **Ó ti parí** láti fò ó; lórí Windows,
dáhùn ìbéèrè náà (tẹ Enter láti fò ó). Láti fi kọ́kọ́rọ́ kún un tàbí yí wọn padà lẹ́yìn náà, ṣe
ìfilọ́lẹ̀ **Add or change keys**:

- Mac: tún áàpù Fontes Installer ṣí kí o sì yan **Fi kọ́kọ́rọ́ kún tàbí yí i padà**.
- Windows: tẹ `Add or change keys.cmd` lẹ́ẹ̀mejì nínú fódà ẹ̀rọ ìfisílẹ̀. Ètò ìfisílẹ̀ fún Windows, nígbà tí
  ó bá wà, yóò tún fi í sínú Start menu > Fontes.

Ohun tí o bá tẹ kò ní hàn. Fún kọ́kọ́rọ́ kọ̀ọ̀kan: lẹ̀ ẹ́, tẹ Enter láti pa èyí tí ó ti wà mọ́, tàbí tẹ `-`
láti yọ ọ́ kúrò. Àwọn kọ́kọ́rọ́ náà ń lọ sí gbogbo áàpù tí ó ti ní Fontes.

**Pẹ̀lú àfikún Claude Desktop (.mcpb).** Ṣí Claude > Settings > Extensions > Fontes kí o sì kún àwọn àyè
náà. Gbogbo wọn kò pọn dandan.

**Pẹ̀lú ọwọ́.** Fi àwọn variable náà kún búlọ́ọ̀kù `env` ti ìtẹ̀sí `fontes` nínú ètò MCP áàpù rẹ:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Tún áàpù náà bẹ̀rẹ̀ lẹ́yìn ìyípadà èyíkéyìí.

## France: PISTE (ọ̀fẹ́)

1. Ṣẹ̀dá àkọọ́lẹ̀ kan lórí [piste.gouv.fr](https://piste.gouv.fr). Èyí túmọ̀ sí gbígbà àwọn òfin ìlò PISTE
   (CGU).
2. Lọ sí API > **Consentement CGU API**. Gba àwọn òfin ìlò fún **JUDILIBRE** àti **Légifrance**
   (production).
3. Ṣẹ̀dá **production application** kan. `APP_SANDBOX` tí a ṣẹ̀dá fún ọ kò lè dé production. Lábẹ́
   "Modifier l'application", sàmì sí **JUDILIBRE (production)** àti **Légifrance (production)**, lẹ́yìn náà lò
   ó (apply).
4. Ṣí táàbù **Authentification** ti áàpù náà. Ṣe ẹ̀dà `client_id` àti `client_secret`.
5. Ṣe ìfilọ́lẹ̀ **Add or change keys** kí o sì lẹ̀ wọ́n.

Àwọn òfin ìlò, ní kúkúrú:

- Dátà: Licence Ouverte / Etalab 2.0. A gba àtúnlò láàyè, pẹ̀lú àtúnlò fún òwò, pẹ̀lú ìdárúkọ orísun.
- Má ṣe tẹ àwọn ẹ̀rí ìwọlé rẹ (credentials) jáde tàbí pín wọn. Sọ fún PISTE bí wọ́n bá jò síta.
- API Légifrance jẹ́ iṣẹ́ beta. A lè dá a dúró, ó sì ní àwọn quota (fún ìṣẹ́jú-àáyá, ìṣẹ́jú àti ọjọ́).
- Àwọn ọ̀rọ̀ Légifrance kì í ṣe ẹ̀dà ojúlówó. PDF Journal officiel tí a fọwọ́ sí nìkan ni ojúlówó.
- Judilibre: má ṣe lo orúkọ àwọn adájọ́ tàbí akọ̀wé ilé-ẹjọ́ láti ṣe àgbéyẹ̀wò, fi wé ara wọn tàbí sọ
  àsọtẹ́lẹ̀ nípa iṣẹ́ wọn (Code de l'organisation judiciaire art. L111-13; ẹ̀ṣẹ̀ ọ̀daràn).
- Judilibre: tẹ̀lé GDPR. Má ṣe gbìyànjú láti tún dá àwọn ẹgbẹ́ ẹjọ́ mọ̀.

Àwọn quota rẹ wà nínú PISTE lábẹ́ API Sélectionnées > Actions > Consulter les quotas.

## United States: api.data.gov (ọ̀fẹ́)

1. Lọ sí [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (kọ́kọ́rọ́ náà ń hàn lórí ojú-ìbòjú)
   tàbí [api.data.gov/signup](https://api.data.gov/signup/) (a ń fi kọ́kọ́rọ́ náà ránṣẹ́ sí ọ nípasẹ̀ ímeèlì).
2. Tẹ orúkọ àti ímeèlì rẹ. Àyè "how will you use it" kò pọn dandan.
3. Ṣe ẹ̀dà kọ́kọ́rọ́ oní-lẹ́tà 40 náà.
4. Ṣe ìfilọ́lẹ̀ **Add or change keys** kí o sì lẹ̀ ẹ́ gẹ́gẹ́ bí kọ́kọ́rọ́ US.

Àwọn òfin ìlò, ní kúkúrú:

- Pẹ̀lú kọ́kọ́rọ́ tìrẹ, govinfo gba ìbéèrè tó 36,000 láàyè ní wákàtí kan.
- A kò rí òfin ìlò pàtó fún API náà (api.data.gov/terms/ kò sí). A kò tíì jẹ́rìí sí i. Wo
  [àwọn ìlànà govinfo](https://www.govinfo.gov/about/policies) àti
  [ìlànà ìpamọ́ àṣírí data.gov](https://data.gov/privacy-policy/).
- Pa kọ́kọ́rọ́ náà mọ́ fún ara rẹ.

## Ibi tí a ń tọ́jú àwọn kọ́kọ́rọ́ sí

- **Ẹ̀rọ ìfisílẹ̀ tàbí pẹ̀lú ọwọ́:** gẹ́gẹ́ bí ọ̀rọ̀ lásán nínú fáìlì ètò MCP ti áàpù kọ̀ọ̀kan, nínú búlọ́ọ̀kù
  `env` ti ìtẹ̀sí `fontes`. Ẹnikẹ́ni tí ó lè ka àwọn fáìlì olùlò rẹ lè ka àwọn kọ́kọ́rọ́ náà.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` tàbí `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Àfikún Claude Desktop (.mcpb):** Claude ń tọ́jú àwọn àyè wọ̀nyí sínú ètò rẹ̀, ó sì ń dáàbò bò wọ́n pẹ̀lú
  ibi ìpamọ́ aláàbò ti ètò rẹ (Keychain lórí Mac, Credential Manager lórí Windows).

Ṣáájú ìyípadà kọ̀ọ̀kan, ẹ̀rọ ìfisílẹ̀ ń fi ẹ̀dà fáìlì ètò náà pamọ́ sí ẹ̀gbẹ́ rẹ̀
(`<file>.fontes-backup-<time>`). Àwọn ẹ̀dà tí a ṣe lẹ́yìn tí o fi kọ́kọ́rọ́ kún un ní àwọn kọ́kọ́rọ́ náà nínú
pẹ̀lú. Pa àwọn ẹ̀dà àtijọ́ tí o kò nílò rẹ́.

## Yíyí tàbí yíyọ kọ́kọ́rọ́ kúrò

- Ṣe ìfilọ́lẹ̀ **Add or change keys**. Lẹ kọ́kọ́rọ́ tuntun láti rọ́pò rẹ̀, tàbí tẹ `-` láti yọ ọ́ kúrò.
- Tàbí ṣàtúnṣe búlọ́ọ̀kù `env` pẹ̀lú ọwọ́ kí o sì tún áàpù náà bẹ̀rẹ̀.
- Yíyọ Fontes kúrò ń yọ gbogbo ìtẹ̀sí rẹ̀ kúrò, pẹ̀lú àwọn kọ́kọ́rọ́. Kò pa àwọn ẹ̀dà ìpamọ́ rẹ́.
- Bí kọ́kọ́rọ́ kan bá jò síta, rọ́pò rẹ̀ ní orísun náà pẹ̀lú: nínú PISTE, ṣẹ̀dá ẹ̀rí ìwọlé tuntun fún áàpù rẹ;
  fún api.data.gov, forúkọ sílẹ̀ fún kọ́kọ́rọ́ tuntun.

## Àwọn ọ̀rọ̀ tí o lè rí

| Ọ̀rọ̀ | Ìtumọ̀ |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Kò sí kọ́kọ́rọ́ fún France. Fi ọ̀kan kún un. |
| `Inactive: needs a free PISTE account. ...` (nínú `list_jurisdictions`) | Bákan náà. |
| `PISTE refused the client credentials ...` | ID tàbí secret kò tọ́ tàbí kò wúlò mọ́. Ṣe ẹ̀dà méjèèjì lẹ́ẹ̀kan sí i láti táàbù Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Áàpù rẹ kò forúkọ sílẹ̀ fún API yẹn, tàbí o kò tíì gba àwọn òfin ìlò rẹ̀. Wo ìgbésẹ̀ 2 àti 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Kò sí kọ́kọ́rọ́ US. Ìwádìí ń ṣiṣẹ́ fún ìpè díẹ̀ lójoojúmọ́. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Kọ́kọ́rọ́ demo ti tán. Fi kọ́kọ́rọ́ tìrẹ kún un. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Kọ́kọ́rọ́ náà kò tọ́, tàbí a kò tíì jẹ́rìí sí i láti inú ímeèlì. |

Ìye òfo ni a kà sí àìsí kọ́kọ́rọ́.

## Àwọn àṣẹ (WLM_PERMITTED)

Èyí kì í ṣe kọ́kọ́rọ́ API, ẹ̀rọ ìfisílẹ̀ kò sì ṣètò rẹ̀. **Ṣètò rẹ̀ kìkì bí ìwọ fúnra rẹ bá ní àṣẹ yẹn.**

Àwọn orísun kan wà ní pípa ní àìyípadà nítorí pé òfin ìlò wọn tàbí robots.txt wọn kà ìlò aládàáṣe léèwọ̀
láìsí àṣẹ. Bí o bá ní àṣẹ láti ọ̀dọ̀ olùtẹ̀jáde, tan orísun kan nípa fífi kóòdù rẹ̀ kún `WLM_PERMITTED`, tí a
fi àmì ìdánudúró (comma) yà sọ́tọ̀, nínú búlọ́ọ̀kù `env`: `"WLM_PERMITTED": "in,de"`.

| Kóòdù | Orísun |
|---|---|
| `az` | Azerbaijan: e-qanun.az (Ministry of Justice) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (òfin tí a ti ṣàkópọ̀) |
| `de` | Germany: NeuRIS (ẹnu-ọ̀nà ìwífún òfin àpapọ̀, iṣẹ́ ìdánwò) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Greece: National Printing Office, ìwádìí Government Gazette (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: àwọn ìdájọ́ ilé-ẹjọ́ (elitigation.sg) |

Láìsí àṣẹ, Fontes sọ pé: `Off by default (<code>): the terms or robots.txt of ... forbid automated use
without the operator's permission.`
