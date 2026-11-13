> Ìtúmọ̀ yìí ni a ṣe pẹ̀lú ìrànlọ́wọ́ ẹ̀rọ. Ẹ̀dà Gẹ̀ẹ́sì ni ó ní àṣẹ.

# Bí a ṣe ń fi Fontes sílẹ̀

Fontes ń jẹ́ kí áàpù AI rẹ wá àwọn ìdájọ́ ilé-ẹjọ́ àti òfin láàyè lórí ojú-ìwé ayélujára ti ilé-ẹjọ́ àti ti
ìjọba, ní agbègbè ìdájọ́ tí ó ju 120 lọ. Gbogbo èsì ní ìjápọ̀ sí ìwé ojúlówó. Sáfà MCP àbọ̀dé ni, nítorí náà
ó ń ṣiṣẹ́ nínú áàpù èyíkéyìí tí ó lè ṣe ìfilọ́lẹ̀ sáfà MCP lórí kọ̀ǹpútà rẹ: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline àti àwọn mìíràn.

**Fontes kò tíì sí lórí PyPI.** Àwọn ìgbésẹ̀ ìsàlẹ̀ yìí yóò ṣiṣẹ́ nígbà tí a bá ti tẹ ẹ̀dà àkọ́kọ́ jáde.

Yan áàpù rẹ, tẹ̀lé àwọn ìgbésẹ̀, lẹ́yìn náà [ṣàyẹ̀wò pé ó ń ṣiṣẹ́](#ṣíṣàyẹ̀wò-pé-ó-ń-ṣiṣẹ́).

## Claude Desktop

1. Gba fáìlì `.mcpb` ti Fontes sílẹ̀ láti inú
   [ẹ̀dà tuntun jùlọ](https://github.com/ykarapazar/fontes/releases/latest).
2. Tẹ̀ ẹ́ lẹ́ẹ̀mejì. Claude Desktop yóò ṣí i.
3. Tẹ **Install**.

## Codex

Nínú terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI àti àfikún Codex IDE ń pín ètò yìí (`~/.codex/config.toml`). O nílò [uv](#o-nílò-uv).

## Claude Code

Nínú terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

O nílò [uv](#o-nílò-uv).

## Àwọn áàpù mìíràn

Gbogbo ìwọ̀nyí nílò [uv](#o-nílò-uv). Fi ìtẹ̀sí náà kún un, fi pamọ́, lẹ́yìn náà pa áàpù náà dé kí o sì tún
un ṣí.

**Cursor:** nínú `~/.cursor/mcp.json` (gbogbo iṣẹ́) tàbí `.cursor/mcp.json` (iṣẹ́ kan):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** ṣe ìfilọ́lẹ̀ **MCP: Add Server** láti inú Command Palette, yan **Command
(stdio)**, tẹ `uvx fontes-mcp` kí o sì pe sáfà náà ní `fontes`. Tàbí fi èyí kún `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Àwọn ètò VS Code àtijọ́ ń lo `.vscode/mcp.json`, pẹ̀lú kọ́kọ́rọ́ òkè-jùlọ `servers` dípò `mcpServers`.

**Gemini CLI:** nínú terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Tàbí fi èyí kún
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** ṣí fáìlì ètò rẹ (**zed: open settings file**) kí o sì fi èyí kún un:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** nínú ọ̀pá ẹ̀gbẹ́ ọ̀tún, ṣí táàbù **Program**, tẹ **Install → Edit mcp.json**, kí o sì fi èyí
kún un:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** tẹ àmì **MCP Servers**, ṣí táàbù **Configure**, tẹ **Configure MCP Servers**, kí o sì fi ìtẹ̀sí
`mcpServers` kan náà bí ti LM Studio kún un.

**Claude Desktop, pẹ̀lú ọwọ́** (dípò fáìlì `.mcpb`): fi ìtẹ̀sí `mcpServers` kan náà kún
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`).

**Áàpù MCP mìíràn èyíkéyìí** (Windsurf àti àwọn mìíràn): ìwé ìtọ́sọ́nà tirẹ̀ ló ń sọ ibi tí ó ń tọ́jú àwọn
sáfà MCP rẹ̀ sí. Ọ̀pọ̀ jùlọ gba ìtẹ̀sí kan náà: àṣẹ `uvx`, àríyànjiyàn (argument) `fontes`.

Bí áàpù náà kò bá rí `uvx`, lo ipa-ọ̀nà rẹ̀ kíkún (lórí macOS àti Linux, `which uvx` ń fi í hàn).

## O nílò uv

Codex, Claude Code àti àwọn áàpù mìíràn ń bẹ̀rẹ̀ Fontes pẹ̀lú `uvx`; `uvx` wá pẹ̀lú **uv**, irinṣẹ́ kékeré ọ̀fẹ́
láti ọ̀dọ̀ Astral. Láti fi í sílẹ̀, wo [ìtọ́sọ́nà Astral](https://docs.astral.sh/uv/getting-started/installation/),
tàbí ṣe ìfilọ́lẹ̀:

- macOS tàbí Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Àwọn kọ́kọ́rọ́

Àwọn orísun kan nílò kọ́kọ́rọ́ ọ̀fẹ́: wo [KEYS.md](KEYS.md).

## Ṣíṣàyẹ̀wò pé ó ń ṣiṣẹ́

Nínú ìjíròrò tuntun, béèrè: *"Àwọn agbègbè ìdájọ́ wo ni Fontes lè wá nínú wọn?"* Áàpù náà yẹ kí ó dáhùn pẹ̀lú
àtòjọ àwọn orílẹ̀-èdè. Bí kò bá ṣe bẹ́ẹ̀, pa áàpù náà dé kí o sì tún un ṣí lẹ́ẹ̀kan sí i.

## Ẹ̀rọ ìfisílẹ̀ onítẹ̀-ẹ̀ẹ̀kan (ń bọ̀ láìpẹ́)

Ẹ̀rọ ìfisílẹ̀ fún Mac àti Windows tí ó ń ṣètò Fontes nínú gbogbo áàpù rẹ lẹ́ẹ̀kan náà ń bọ̀ láìpẹ́. Ó ń ṣètò
Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio
àti Cline. Nígbà tí a bá tẹ̀ ẹ́ jáde:

**Kí o tó bẹ̀rẹ̀:** pa ọ̀kọ̀ọ̀kan àwọn áàpù wọ̀nyẹn dé pátápátá. Èyí ṣe pàtàkì jùlọ fún Claude Code: bí ó bá
ń ṣiṣẹ́, ó ń kọ `~/.claude.json` sílẹ̀ lẹ́ẹ̀kan sí i ó sì lè pa ohun tí ẹ̀rọ ìfisílẹ̀ yí padà rẹ́. Bí o kò bá
lè pa Claude Code dé, fi Fontes kún un pẹ̀lú `claude mcp add` (wo [Claude Code](#claude-code)).

**Mac**

1. Ṣí fódà **Fontes Installer** tí o gbà sílẹ̀.
2. Tẹ **Install Fontes.command** lẹ́ẹ̀mejì.
   - Bí Mac rẹ bá sọ pé "cannot be opened because it is from an unidentified developer": tẹ fáìlì náà
     pẹ̀lú bọ́tìnnì ọ̀tún (tàbí Control-tẹ̀ ẹ́), yan **Open**, lẹ́yìn náà **Open** lẹ́ẹ̀kan sí i. Ìgbà kan
     péré ni o máa ní láti ṣe èyí.
3. Fèrèsé kan yóò ṣí, yóò sì béèrè bóyá kí ó fi iye ìlò aláìlórúkọ ránṣẹ́; tẹ Enter fún "bẹ́ẹ̀kọ́".
4. Ó máa béèrè bóyá kí o fi àwọn kọ́kọ́rọ́ kún un báyìí. Tẹ Enter láti fò ó; wo
   [Ìgbésẹ̀ kọ́kọ́rọ́](#ìgbésẹ̀-kọ́kọ́rọ́).
5. Nígbà tí ó bá fi **Ó ti parí** hàn, tún àwọn áàpù AI rẹ ṣí.

**Windows**

1. Ṣí (unzip) **Fontes Installer** tí o gbà sílẹ̀ (tẹ pẹ̀lú bọ́tìnnì ọ̀tún → Extract All).
2. Tẹ **Install Fontes.cmd** lẹ́ẹ̀mejì.
   - Bí Windows bá fi "Windows protected your PC" hàn: tẹ **More info**, lẹ́yìn náà **Run anyway**.
3. Nígbà tí a bá béèrè bóyá kí ó fi iye ìlò aláìlórúkọ ránṣẹ́, tẹ Enter fún "bẹ́ẹ̀kọ́".
4. Ó máa béèrè bóyá kí o fi àwọn kọ́kọ́rọ́ kún un báyìí. Tẹ Enter láti fò ó; wo
   [Ìgbésẹ̀ kọ́kọ́rọ́](#ìgbésẹ̀-kọ́kọ́rọ́).
5. Nígbà tí ó bá fi **Ó ti parí** hàn, tún àwọn áàpù AI rẹ ṣí. Bí ọ̀kan bá ṣì ń ṣiṣẹ́, pa á dé pátápátá (lórí
   system tray pẹ̀lú, lẹ́gbẹ̀ẹ́ aago) kí o sì tún un ṣí.

Ní ìparí, ẹ̀rọ ìfisílẹ̀ ń ka àwọn áàpù tí ó ṣètò.

### Àwọn áàpù tí ó ń ṣètò

Ó ń ṣètò áàpù kan kìkì bí fódà ètò áàpù náà bá ti wà lórí kọ̀ǹpútà rẹ. A máa ṣètò Claude Code kìkì bí
`~/.claude.json` bá wà. A máa ń ṣètò Claude Desktop nígbà gbogbo. Áàpù kọ̀ọ̀kan ń gba ìtẹ̀sí kan, `fontes`,
nínú fáìlì yìí:

| Áàpù | Fáìlì (Mac àti Linux) | Fáìlì (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, àti ẹ̀dà tí ẹ̀yà Microsoft Store ń lò |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, tàbí `~/.codeium/windsurf/mcp_config.json` lórí àwọn ẹ̀yà àtijọ́ | `%APPDATA%\devin\mcp_config.json`, tàbí `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

A máa ṣètò VS Code bí `~/.copilot` tàbí fódà ètò VS Code fúnra rẹ̀ bá wà.

Áàpù méjì nílò ìgbésẹ̀ kan sí i:

- **Windsurf:** lẹ́yìn tí o bá tún un ṣí, tẹ refresh nínú Cascade.
- **Cline nínú àfikún VS Code àtijọ́:** fi Fontes kún un pẹ̀lú ọwọ́ (wo [Cline](#àwọn-áàpù-mìíràn)).

### Ìgbésẹ̀ kọ́kọ́rọ́

Lẹ́sẹ̀kẹsẹ̀ lẹ́yìn ìfisílẹ̀, ẹ̀rọ ìfisílẹ̀ ń fún ọ ní àǹfààní láti fi àwọn kọ́kọ́rọ́ ọ̀fẹ́ fún France àti United
States kún un. Láti fi wọ́n kún un tàbí yí wọn padà lẹ́yìn náà:

- **Mac:** tẹ **Add or change keys.command** lẹ́ẹ̀mejì nínú fódà ẹ̀rọ ìfisílẹ̀, tàbí tún áàpù Fontes Installer
  ṣí kí o sì yan **Fi kọ́kọ́rọ́ kún tàbí yí i padà**.
- **Windows:** tẹ **Add or change keys.cmd** lẹ́ẹ̀mejì nínú fódà ẹ̀rọ ìfisílẹ̀.

Ohun tí o bá tẹ kò ní hàn. Àwọn kọ́kọ́rọ́ náà ń lọ sí gbogbo áàpù tí ó ti ní Fontes. Pa àwọn áàpù náà dé kí o
sì tún wọn ṣí lẹ́yìn náà. Ibi tí a ti lè gba kọ́kọ́rọ́ àti ohun tí ọ̀kọ̀ọ̀kan ń ṣí: [KEYS.md](KEYS.md).

### Ẹ̀dà ìpamọ́, títún-un ṣe àti yíyọ kúrò

Ẹ̀rọ ìfisílẹ̀ ń yí ìtẹ̀sí `fontes` nìkan padà. Gbogbo ètò àti àkíyèsí mìíràn kò ní yí padà. Kí ó tó yí fáìlì
kan padà, ó ń fi ẹ̀dà kan pamọ́ sí ẹ̀gbẹ́ rẹ̀, tí a ń pè ní `<file>.fontes-backup-<date>`. Àwọn ẹ̀dà tí a ṣe
lẹ́yìn tí o fi kọ́kọ́rọ́ kún un ní àwọn kọ́kọ́rọ́ náà nínú: pa àwọn tí o kò nílò mọ́ rẹ́. Ó tún ń fi uv sílẹ̀.
Kò léwu láti tún un ṣe ìfilọ́lẹ̀: ó ń tún ìfisílẹ̀ ṣe kò sì yí ohunkóhun mìíràn padà.

Láti yọ Fontes kúrò, tẹ **Uninstall Fontes.command** (Mac) tàbí **Uninstall Fontes.cmd** (Windows)
lẹ́ẹ̀mejì. Ó ń yọ ìtẹ̀sí `fontes` kúrò nínú áàpù kọ̀ọ̀kan, pẹ̀lú àwọn kọ́kọ́rọ́ rẹ̀. Àwọn ètò mìíràn àti àwọn
ẹ̀dà ìpamọ́ ń wà níbẹ̀.

## Àwọn ìmúdójúìwọ̀n

- **Ẹ̀rọ ìfisílẹ̀ àti fáìlì `.mcpb`:** o kò ní láti ṣe nǹkankan. Lẹ́ẹ̀kan lójoojúmọ́, nígbà tí áàpù kan bá
  bẹ̀rẹ̀, Fontes ń ṣàyẹ̀wò lẹ́yìn ìgbà bóyá ẹ̀dà tuntun wà, ó sì ń pèsè rẹ̀; ní ìgbà tí áàpù náà bá bẹ̀rẹ̀
  tẹ̀lé e, ó máa lò ó. Bí a kò bá lè gba ìmúdójúìwọ̀n kan sílẹ̀ tàbí tí kò bá ṣiṣẹ́, Fontes ń bá a lọ láti
  lo ẹ̀dà tí ó ń ṣiṣẹ́.
- **`uvx`:** Fontes ń sọ fún ọ nígbà tí ẹ̀dà tuntun bá wà, ní òkè àtòjọ àwọn agbègbè ìdájọ́. Láti máa ṣe
  ìfilọ́lẹ̀ èyí tuntun jùlọ nígbà gbogbo, lo `fontes-mcp@latest` dípò `fontes-mcp`.

A kò fi ìwífún kankan nípa rẹ tàbí àwọn ìwádìí rẹ ránṣẹ́ sí ibikíbi fún èyí.

## Ìpamọ́ àṣírí

Fontes kò fi ohunkóhun nípa rẹ tàbí àwọn ìwádìí rẹ ránṣẹ́ ní àìyípadà. Iye ìlò jẹ́ opt-in, a sì máa fi ìròyìn
àṣìṣe ránṣẹ́ kìkì lẹ́yìn tí o bá ti rí i tí o sì jẹ́rìí sí i. Àlàyé: [PRIVACY.md](PRIVACY.md).

## Yíyọ ọ́ kúrò

Yọ ìtẹ̀sí `fontes` kúrò nínú ètò MCP áàpù rẹ (nínú Claude Code: `claude mcp remove fontes`), lẹ́yìn náà pa
áàpù náà dé kí o sì tún un ṣí.

## Ohun tí ó yẹ kí o mọ̀

Fontes ń ka àwọn orísun gbogbogbò, èyí tí ó pọ̀ jùlọ jẹ́ ojú-ìwé ayélujára ti ilé-ẹjọ́ àti ti ìjọba. Ó ń sàmì
sí àwọn orísun tí kì í ṣe ti ìjọba nínú àwọn ìdáhùn rẹ̀. Ṣí ìjápọ̀ orísun nígbà gbogbo kí o tó gbẹ́kẹ̀lé
ìdájọ́ tàbí abala kan.

Bí ohun kan kò bá ṣiṣẹ́, fi ímeèlì ránṣẹ́ sí fontesmcp@proton.me pẹ̀lú ohun tí o ṣe àti àṣìṣe tí o rí.

## Kí o tó gbẹ́kẹ̀lé e

- Fontes jẹ́ irinṣẹ́ ìwádìí, kì í ṣe ìmọ̀ràn òfin. Lílò rẹ̀ kò sọ ẹnikẹ́ni di agbẹjọ́rò rẹ.
- A pèsè rẹ̀ "bí ó ṣe wà" (as is), láìsí ìdánilójú, àwọn òǹkọ̀wé rẹ̀ kò sì ní ojúṣe fún bí a ṣe ń lò ó, dé
  ibi tí òfin gbà láàyè. Àwọn ìlànà kíkún wà nínú [ìwé-àṣẹ](../../../LICENSE) (Apache 2.0).
