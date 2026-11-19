> Ово је машински потпомогнут пријевод. Мјеродавна је верзија на енглеском.

# Инсталација алата Fontes

Fontes омогућава вашој AI апликацији да претражује судске одлуке и прописе уживо на страницама
судова и државних органа у више од 120 јурисдикција. Сваки резултат садржи линк на оригинал. То
је стандардни MCP сервер, па ради у свакој апликацији која може покренути локални MCP сервер:
Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio, Cline и другим.

Одаберите своју апликацију, слиједите њене кораке, а затим [провјерите да ли ради](#провјера-да-ли-ради).

## Claude Desktop

1. Преузмите Fontes датотеку `.mcpb` из
   [најновијег издања](https://github.com/ykarapazar/fontes/releases/latest).
2. Двапут кликните на њу. Claude Desktop ће је отворити.
3. Кликните **Install**.

## Codex

У терминалу:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI и Codex проширење за IDE дијеле ову поставку (`~/.codex/config.toml`).
Потребан вам је [uv](#потребан-вам-је-uv).

## Claude Code

У терминалу:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Потребан вам је [uv](#потребан-вам-је-uv).

## Остале апликације

За сваку од ових апликација потребан је [uv](#потребан-вам-је-uv). Додајте унос, сачувајте, а
затим затворите и поново отворите апликацију.

**Cursor:** у `~/.cursor/mcp.json` (сви пројекти) или `.cursor/mcp.json` (један пројекат):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** из Command Palette покрените **MCP: Add Server**, одаберите
**Command (stdio)**, унесите `uvx fontes-mcp` и назовите сервер `fontes`. Или додајте ово у
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Старије поставке VS Code користе `.vscode/mcp.json`, гдје је кључ највишег нивоа `servers`
умјесто `mcpServers`.

**Gemini CLI:** у терминалу, `gemini mcp add -s user fontes uvx fontes-mcp`. Или додајте ово у
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** отворите датотеку поставки (**zed: open settings file**) и додајте:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** у десној бочној траци отворите картицу **Program**, кликните **Install → Edit
mcp.json** и додајте:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** кликните икону **MCP Servers**, отворите картицу **Configure**, кликните **Configure MCP
Servers** и додајте исти унос `mcpServers` као за LM Studio.

**Claude Desktop, ручно** (умјесто датотеке `.mcpb`): додајте исти унос `mcpServers` у
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Било која друга MCP апликација** (Windsurf и друге): њена властита документација наводи гдје
чува своје MCP сервере. Већина прихвата исти унос: наредба `uvx`, аргумент `fontes`.

Ако апликација не може пронаћи `uvx`, користите пуну путању (на macOS и Linux-у исписује је
`which uvx`).

## Потребан вам је uv

Codex, Claude Code и остале апликације покрећу Fontes помоћу `uvx`, који долази уз **uv**, мали
бесплатни алат компаније Astral. Да га инсталирате, погледајте
[упутство компаније Astral](https://docs.astral.sh/uv/getting-started/installation/) или покрените:

- macOS или Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Кључеви

Неким изворима је потребан бесплатан кључ: погледајте [KEYS.md](KEYS.md).

## Провјера да ли ради

У новом разговору питајте: *„Које јурисдикције Fontes може претраживати?“* Апликација би требала
одговорити списком држава. Ако то не уради, затворите и поново отворите апликацију још једном.

## Инсталацијски програм једним кликом (Mac и Windows)

Инсталацијски програм поставља Fontes у све ваше апликације одједном: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio и Cline.

**Прије него што почнете:** потпуно затворите сваку од ових апликација. То је најважније за Claude
Code: док ради, он поново записује `~/.claude.json` и може поништити измјену инсталацијског
програма. Ако не можете затворити Claude Code, додајте Fontes у њега помоћу `claude mcp add`
(погледајте [Claude Code](#claude-code)).

**Mac**

1. Преузмите инсталацијски програм за Mac (`Fontes-Installer-…-mac.zip`) са
   [најновијег издања](https://github.com/ykarapazar/fontes/releases/latest) и двапут кликните на њега да га распакујете.
2. Двапут кликните на **Fontes Installer**. Ако ваш Mac пита да ли да отвори апликацију преузету
   с интернета, кликните на **Open**.
3. Одаберите **Инсталирај** и кликните на **У реду**. Постављање траје око минуту.
4. Порука наводи апликације које је поставио. Кликните на **Готово**, а затим поново отворите те
   апликације. Да прво додате опционалне бесплатне кључеве, умјесто тога кликните на
   **Додај кључеве**; погледајте [Корак с кључевима](#корак-с-кључевима).

**Windows**

1. Преузмите инсталацијски програм за Windows (`Fontes-Setup-….exe`) са [најновијег издања](https://github.com/ykarapazar/fontes/releases/latest) и двапут кликните на њега.
   - Ако Windows прикаже "Windows protected your PC": кликните **More info**, затим **Run anyway**.
2. Одаберите **Инсталирај**. Отвара се прозор и поставља Fontes.
3. Када вас пита да ли да шаље анонимне бројеве кориштења, притисните Enter за не.
4. Пита да ли да сада додате кључеве. Притисните Enter да прескочите; погледајте
   [Корак с кључевима](#корак-с-кључевима).
5. Када се појави **Готово**, поново отворите своје AI апликације. Ако је нека још била покренута,
   потпуно је затворите (и из системске траке, поред сата) и поново је отворите.

На крају инсталацијски програм наводи апликације које је поставио.

### Које апликације поставља

Апликацију поставља само ако је мапа с њеним поставкама већ на вашем рачунару. Claude Code се
поставља само ако постоји `~/.claude.json`. Claude Desktop се увијек поставља. Свака апликација
добија један унос, `fontes`, у овој датотеци:

| Апликација | Датотека (Mac и Linux) | Датотека (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, и властита копија верзије из Microsoft Store-а |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, или `~/.codeium/windsurf/mcp_config.json` у старијим верзијама | `%APPDATA%\devin\mcp_config.json`, или `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code се поставља ако постоји `~/.copilot` или властита мапа поставки програма VS Code.

Двије апликације захтијевају још један корак:

- **Windsurf:** након што га поново отворите, притисните освјежавање у Cascade-у.
- **Cline унутар старијег проширења за VS Code:** додајте Fontes ручно (погледајте
  [Cline](#остале-апликације)).

### Корак с кључевима

Одмах након инсталације, инсталацијски програм нуди да додате бесплатне кључеве за Француску и
САД. Да их додате или промијените касније:

- **Mac:** поново отворите **Fontes Installer** и одаберите **Додај или промијени кључеве**.
- **Windows:** отворите мени Start, затим **Fontes** → **Додај или промијени кључеве**.

Унос се не приказује. Кључеви се уписују у сваку апликацију која већ има Fontes. Након тога
затворите и поново отворите апликације. Гдје набавити кључеве и шта откључавају: [KEYS.md](KEYS.md).

### Резервне копије, поновно покретање и уклањање

Инсталацијски програм мијења само унос `fontes`. Све остале поставке и коментари остају какви
су били. Прије него што измијени датотеку, поред ње сачува копију под називом
`<file>.fontes-backup-<date>`. Копије направљене након што сте додали кључеве садрже те
кључеве: обришите оне које вам више не требају. Инсталира и uv. Поновно покретање је сигурно:
поправља поставку и не мијења ништа друго.

Да уклоните Fontes, отворите **Fontes Installer** и одаберите **Уклони** (Mac) или у Settings → Apps (Windows) уклоните **Fontes**. Уклања унос `fontes`, заједно с кључевима, из сваке
апликације. Ваше остале поставке и резервне копије остају.

## Ажурирања

- **Инсталацијски програм и датотека `.mcpb`:** не морате ништа радити. Једном дневно, када се
  апликација покрене, Fontes у позадини провјерава постоји ли новија верзија и припрема је;
  сљедећи пут када се апликација покрене, користи њу. Ако се ажурирање не може преузети или
  не ради, Fontes наставља користити верзију која је радила.
- **`uvx`:** Fontes вам јавља када је доступна новија верзија, на врху свог списка јурисдикција.
  Да увијек покрећете најновију верзију, користите `fontes-mcp@latest` умјесто `fontes-mcp`.

За ово се никамо не шаљу никакве информације о вама или вашим претрагама.

## Приватност

Fontes задано не шаље ништа о вама или вашим претрагама. Бројеви кориштења шаљу се само уз
ваш пристанак (opt-in), а пријава грешке шаље се тек након што је видите и потврдите.
Детаљи: [PRIVACY.md](PRIVACY.md).

## Уклањање

Уклоните унос `fontes` из MCP поставки своје апликације (у Claude Code:
`claude mcp remove fontes`), а затим затворите и поново отворите апликацију.

## Добро је знати

Fontes чита јавне изворе, углавном странице судова и државних органа. Незваничне изворе означава
у својим одговорима. Увијек отворите линк на извор прије него што се ослоните на одлуку или
одредбу.

Ако нешто пође по злу, пошаљите опис онога што сте урадили и грешке коју сте видјели на
fontesmcp@proton.me.

## Прије него што се ослоните на Fontes

- Fontes је алат за истраживање, а не правни савјет. Његово кориштење никога не чини вашим
  адвокатом.
- Пружа се „такав какав јесте“, без гаранције, а његови аутори нису одговорни за начин на који
  се користи, у мјери у којој то закон допушта. Потпуни услови су у [лиценци](../../../LICENSE)
  (Apache 2.0).
