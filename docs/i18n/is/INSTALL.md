> Þetta er vélstudd þýðing. Enska útgáfan gildir.

# Uppsetning Fontes

Fontes gerir gervigreindarforritinu þínu kleift að fletta upp dómum og löggjöf í rauntíma á vefsíðum dómstóla og
stjórnvalda í 125 lögsögum. Hver niðurstaða tengir á frumritið. Þetta er staðlaður MCP-þjónn,
svo hann virkar í hvaða forriti sem getur keyrt staðbundinn MCP-þjón: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline og fleirum.

Veldu forritið þitt, fylgdu skrefunum fyrir það og [athugaðu svo hvort það virki](#athugaðu-hvort-það-virki).

## Claude Desktop

1. Sæktu `.mcpb`-skrá Fontes úr
   [nýjustu útgáfunni](https://github.com/ykarapazar/fontes/releases/latest).
2. Tvísmelltu á hana. Claude Desktop opnar hana.
3. Smelltu á **Install**.

## Codex

Í skipanalínu (terminal):

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI og Codex-viðbótin fyrir IDE deila þessari stillingu (`~/.codex/config.toml`).
Þú þarft [uv](#þú-þarft-uv).

## Claude Code

Í skipanalínu (terminal):

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Þú þarft [uv](#þú-þarft-uv).

## Önnur forrit

Hvert þeirra þarf [uv](#þú-þarft-uv). Bættu færslunni við, vistaðu, og lokaðu svo forritinu og opnaðu það aftur.

**Cursor:** í `~/.cursor/mcp.json` (öll verkefni) eða `.cursor/mcp.json` (eitt verkefni):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** keyrðu **MCP: Add Server** úr Command Palette, veldu
**Command (stdio)**, sláðu inn `uvx fontes-mcp` og nefndu þjóninn `fontes`. Eða bættu þessu við
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Eldri VS Code-uppsetningar nota `.vscode/mcp.json`, þar sem efsti lykillinn er `servers` í stað
`mcpServers`.

**Gemini CLI:** í skipanalínu, `gemini mcp add -s user fontes uvx fontes-mcp`. Eða bættu þessu við
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** opnaðu stillingaskrána þína (**zed: open settings file**) og bættu við:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** í hliðarstikunni til hægri, opnaðu flipann **Program**, smelltu á **Install → Edit
mcp.json** og bættu við:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** smelltu á táknið **MCP Servers**, opnaðu flipann **Configure**, smelltu á **Configure MCP
Servers** og bættu við sömu `mcpServers`-færslu og fyrir LM Studio.

**Claude Desktop, handvirkt** (í stað `.mcpb`-skrárinnar): bættu sömu `mcpServers`-færslu við
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Hvaða annað MCP-forrit sem er** (Windsurf og fleiri): eigin skjölun forritsins segir hvar það geymir MCP-þjóna sína.
Flest nota sömu færslu: skipun `uvx`, færibreytur `fontes-mcp`.

Ef forritið finnur ekki `uvx`, notaðu fulla slóð þess (á macOS og Linux birtir `which uvx` hana).

## Þú þarft uv

Codex, Claude Code og hin forritin ræsa Fontes með `uvx`, sem fylgir **uv**, litlu
ókeypis tóli frá Astral. Til að setja það upp, sjá
[leiðbeiningar Astral](https://docs.astral.sh/uv/getting-started/installation/), eða keyrðu:

- macOS eða Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Lyklar

Sumar heimildir þurfa ókeypis lykil: sjá [KEYS.md](KEYS.md).

## Athugaðu hvort það virki

Spyrðu í nýju spjalli: *„Í hvaða lögsögum getur Fontes leitað?“* Forritið ætti að svara með
lista yfir lönd. Ef það gerir það ekki, lokaðu forritinu og opnaðu það einu sinni enn.

## Uppsetningarforrit með einum smelli (Mac og Windows)

Uppsetningarforritið setur Fontes upp í öllum forritunum þínum í einu: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio og Cline.

**Áður en þú byrjar:** lokaðu hverju þessara forrita alveg. Það skiptir mestu fyrir Claude Code:
á meðan það keyrir endurskrifar það `~/.claude.json` og getur afturkallað breytingu uppsetningarforritsins. Ef þú getur ekki
lokað Claude Code, bættu Fontes frekar við það með `claude mcp add` (sjá [Claude Code](#claude-code)).

**Mac**

1. Sæktu Mac-uppsetningarforritið (`Fontes-Installer-…-mac.zip`) úr [nýjustu
   útgáfunni](https://github.com/ykarapazar/fontes/releases/latest) og tvísmelltu á það til að
   afþjappa það.
2. Tvísmelltu á **Fontes Installer**. Ef Mac-tölvan spyr hvort opna eigi forrit sem var sótt af
   netinu, smelltu á **Open**.
3. Veldu **Setja upp** og smelltu á **Í lagi**. Uppsetningin tekur um eina mínútu.
4. Skilaboð telja upp forritin sem það setti upp. Smelltu á **Lokið** og opnaðu svo þessi forrit
   aftur. Til að bæta fyrst við valfrjálsu ókeypis lyklunum skaltu frekar smella á **Bæta við
   lyklum**; sjá [Lyklaskrefið](#lyklaskrefið).

**Windows**

1. Sæktu Windows-uppsetningarforritið (`Fontes-Setup-….exe`) úr [nýjustu útgáfunni](https://github.com/ykarapazar/fontes/releases/latest) og tvísmelltu á það.
   - Ef Windows sýnir „Windows protected your PC“: smelltu á **More info** og svo **Run anyway**.
2. Smelltu á **Setja upp**. Gluggi opnast og setur upp Fontes.
3. Þegar spurt er hvort senda eigi nafnlausar notkunartölur, ýttu á Enter fyrir nei.
4. Það spyr hvort bæta eigi við lyklum núna. Ýttu á Enter til að sleppa því; sjá [Lyklaskrefið](#lyklaskrefið).
5. Þegar stendur **Done**, opnaðu gervigreindarforritin þín aftur. Ef eitthvert þeirra var enn í gangi, lokaðu því
   alveg (líka úr kerfisbakkanum, við klukkuna) og opnaðu það aftur.

Að lokum telur uppsetningarforritið upp forritin sem það setti upp.

### Hvaða forrit það setur upp

Það setur forrit aðeins upp ef stillingamappa forritsins er þegar á tölvunni þinni. Claude Code
er aðeins sett upp ef `~/.claude.json` er til. Claude Desktop er alltaf sett upp. Hvert forrit fær eina
færslu, `fontes`, í þessari skrá:

| Forrit | Skrá (Mac og Linux) | Skrá (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, auk eigin afrits Microsoft Store-útgáfunnar |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, eða `~/.codeium/windsurf/mcp_config.json` í eldri útgáfum | `%APPDATA%\devin\mcp_config.json`, eða `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code er sett upp ef `~/.copilot` eða eigin stillingamappa VS Code er til.

Tvö forrit þurfa eitt skref í viðbót:

- **Windsurf:** eftir að þú opnar það aftur, ýttu á endurnýja í Cascade.
- **Cline í eldri VS Code-viðbótinni:** bættu Fontes við handvirkt (sjá [Cline](#önnur-forrit)).

### Lyklaskrefið

Strax eftir uppsetningu býðst uppsetningarforritið til að bæta við ókeypis lyklunum fyrir Frakkland og Bandaríkin. Til að bæta þeim við eða
breyta þeim síðar:

- **Mac:** opnaðu **Fontes Installer** aftur og veldu **Bæta við eða breyta lyklum**.
- **Windows:** opnaðu Start-valmyndina, og veldu síðan **Fontes** → **Add or change keys**.

Það sem þú slærð inn er falið. Lyklarnir fara í öll forrit sem þegar hafa Fontes. Lokaðu forritunum og opnaðu þau
aftur á eftir. Hvar á að fá lyklana og hvað þeir opna: [KEYS.md](KEYS.md).

### Afrit, endurkeyrslur og fjarlæging

Uppsetningarforritið breytir aðeins færslunni `fontes`. Allar aðrar stillingar og athugasemdir haldast eins og þær voru.
Áður en það breytir skrá vistar það afrit við hlið hennar, nefnt `<file>.fontes-backup-<date>`. Afrit
sem gerð eru eftir að þú bættir við lyklum innihalda þá lykla: eyddu þeim sem þú þarft ekki lengur. Það
setur einnig upp uv. Óhætt er að keyra það aftur: það lagfærir uppsetninguna og breytir engu öðru.

Til að fjarlægja Fontes, opnaðu **Fontes Installer** og veldu **Fjarlægja** (Mac), eða fjarlægðu
**Fontes** í Settings → Apps (Windows). Það fjarlægir færsluna `fontes`, lykla meðtalda, úr hverju forriti. Aðrar stillingar þínar
og afritin eru áfram til staðar.

## Uppfærslur

- **Uppsetningarforritið og `.mcpb`-skráin:** þú þarft ekkert að gera. Einu sinni á dag, þegar forritið
  ræsist, leitar Fontes að nýrri útgáfu í bakgrunni og gerir hana tilbúna; næst þegar
  forritið ræsist notar það hana. Ef ekki er hægt að sækja uppfærslu eða hún virkar ekki heldur Fontes
  áfram að nota útgáfuna sem virkaði.
- **`uvx`:** Fontes lætur þig vita þegar nýrri útgáfa er til, efst í lista sínum yfir
  lögsögur. Til að keyra alltaf nýjustu útgáfuna, notaðu `fontes-mcp@latest` í stað `fontes-mcp`.

Engar upplýsingar um þig eða leitir þínar eru sendar neitt vegna þessa.

## Persónuvernd

Fontes sendir sjálfgefið ekkert um þig eða leitir þínar. Notkunartölur eru valkvæðar (opt-in), og villuskýrsla
er aðeins send eftir að þú hefur séð hana og staðfest. Nánar: [PRIVACY.md](PRIVACY.md).

## Að fjarlægja það

Fjarlægðu færsluna `fontes` úr MCP-stillingum forritsins (í Claude Code:
`claude mcp remove fontes`), lokaðu svo forritinu og opnaðu það aftur.

## Gott að vita

Fontes les opinberar heimildir, aðallega vefsíður dómstóla og stjórnvalda. Það merkir óopinberar heimildir í
svörum sínum. Opnaðu alltaf tengil heimildarinnar áður en þú treystir á dóm eða ákvæði.

Ef eitthvað fer úrskeiðis, sendu tölvupóst á fontesmcp@proton.me um hvað þú gerðir og hvaða villu þú fékkst.

## Áður en þú treystir á það

- Fontes er tæki til heimildaleitar, ekki lögfræðiráðgjöf. Notkun þess gerir engan að lögmanni þínum.
- Það er látið í té „eins og það er“, án ábyrgðar, og höfundar þess bera ekki ábyrgð á því hvernig það er notað,
  að því marki sem lög leyfa. Allir skilmálarnir eru í [leyfinu](../../../LICENSE) (Apache 2.0).
