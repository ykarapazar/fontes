> Din hija traduzzjoni magħmula bl-għajnuna tal-magna. Il-verżjoni Ingliża hija dik awtorevoli.

# Kif tinstalla Fontes

Fontes jippermetti lill-app tal-AI tiegħek tfittex deċiżjonijiet tal-qorti u leġiżlazzjoni
direttament fuq is-siti web tal-qrati u tal-gvern f'aktar minn 120 ġurisdizzjoni. Kull riżultat
għandu link għall-oriġinal. Huwa server MCP standard, għalhekk jaħdem fi kwalunkwe app li tista'
tħaddem server MCP lokali: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline u oħrajn.

Agħżel l-app tiegħek, segwi l-passi tagħha, imbagħad [iċċekkja li jaħdem](#kif-tiċċekkja-li-jaħdem).

## Claude Desktop

1. Niżżel il-fajl `.mcpb` ta' Fontes mill-
   [aħħar verżjoni (latest release)](https://github.com/ykarapazar/fontes/releases/latest).
2. Agħfas darbtejn fuqu. Claude Desktop jiftħu.
3. Agħfas **Install**.

## Codex

F'terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Is-CLI ta' Codex u l-estensjoni ta' Codex għall-IDE jaqsmu dan is-setting (`~/.codex/config.toml`).
Għandek bżonn [uv](#għandek-bżonn-uv).

## Claude Code

F'terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Għandek bżonn [uv](#għandek-bżonn-uv).

## Apps oħra

Kull waħda minn dawn teħtieġ [uv](#għandek-bżonn-uv). Żid l-entrata, issejvja, imbagħad agħlaq
u erġa' iftaħ l-app.

**Cursor:** f'`~/.cursor/mcp.json` (il-proġetti kollha) jew `.cursor/mcp.json` (proġett wieħed):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** ħaddem **MCP: Add Server** mill-Command Palette, agħżel
**Command (stdio)**, daħħal `uvx fontes-mcp` u sejjaħ is-server `fontes`. Jew żid dan ma'
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Konfigurazzjonijiet eqdem ta' VS Code jużaw `.vscode/mcp.json`, fejn iċ-ċavetta tal-ogħla livell
hija `servers` minflok `mcpServers`.

**Gemini CLI:** f'terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Jew żid dan ma'
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** iftaħ il-fajl tas-settings tiegħek (**zed: open settings file**) u żid:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** fil-sidebar fuq il-lemin, iftaħ it-tab **Program**, agħfas **Install → Edit
mcp.json**, u żid:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** agħfas l-ikona **MCP Servers**, iftaħ it-tab **Configure**, agħfas **Configure MCP
Servers**, u żid l-istess entrata `mcpServers` bħal għal LM Studio.

**Claude Desktop, bl-idejn** (minflok il-fajl `.mcpb`): żid l-istess entrata `mcpServers` ma'
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Kwalunkwe app MCP oħra** (Windsurf u oħrajn): id-dokumentazzjoni tagħha stess tgħid fejn iżżomm
is-servers MCP tagħha. Il-biċċa l-kbira jieħdu l-istess entrata: kmand `uvx`, argument `fontes`.

Jekk l-app ma ssibx `uvx`, uża l-path sħiħ tiegħu (fuq macOS u Linux, `which uvx` jurih).

## Għandek bżonn uv

Codex, Claude Code u l-apps l-oħra jibdew Fontes b'`uvx`, li jiġi ma' **uv**, għodda żgħira
b'xejn minn Astral. Biex tinstallah, ara
[il-gwida ta' Astral](https://docs.astral.sh/uv/getting-started/installation/), jew ħaddem:

- macOS jew Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Ċwievet

Xi sorsi jeħtieġu ċavetta b'xejn: ara [KEYS.md](KEYS.md).

## Kif tiċċekkja li jaħdem

F'chat ġdid, staqsi: *"F'liema ġurisdizzjonijiet jista' jfittex Fontes?"* L-app għandha twieġeb
b'lista ta' pajjiżi. Jekk ma tagħmilx hekk, agħlaq u erġa' iftaħ l-app darba oħra.

## Installer bi klikk waħda (Mac)

L-installer għal Mac jissettja Fontes fl-apps kollha tiegħek f'daqqa: Claude Desktop, Codex, Claude Code,
Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio u Cline. Installer għal Windows
qiegħed fi triqtu; sa dakinhar, uża l-passi għall-app tiegħek hawn fuq.

**Qabel ma tibda:** agħlaq kull waħda minn dawn l-apps għal kollox. Dan huwa l-aktar importanti
għal Claude Code: waqt li jkun qed jaħdem, jerġa' jikteb `~/.claude.json` u jista' jħassar
il-bidla tal-installer. Jekk ma tistax tagħlaq Claude Code, żid Fontes miegħu b'`claude mcp add`
minflok (ara [Claude Code](#claude-code)).

**Mac**

1. Niżżel l-installer għal Mac (`Fontes-Installer-…-mac.zip`)
   mill-[aħħar release](https://github.com/ykarapazar/fontes/releases/latest) u agħfas darbtejn fuqu biex tħoll iż-zip.
2. Agħfas darbtejn fuq **Fontes Installer**. Jekk il-Mac tiegħek jistaqsik jekk tiftaħx app li tniżżlet
   mill-internet, agħfas **Open**.
3. Agħżel **Installa** u agħfas **OK**. Is-setup jieħu madwar minuta.
4. Messaġġ jelenka l-apps li ssettja. Agħfas **Lest**, imbagħad erġa' iftaħ dawk l-apps. Biex iżżid
   l-ewwel iċ-ċwievet b'xejn mhux obbligatorji, agħfas **Żid iċ-ċwievet** minflok; ara
   [Il-pass taċ-ċwievet](#il-pass-taċ-ċwievet).

**Windows** (ladarba joħroġ l-installer għal Windows)

1. Ħoll iż-zip ta' **Fontes Installer** li niżżilt (buttuna tal-lemin → Extract All).
2. Agħfas darbtejn fuq **Install Fontes.cmd**.
   - Jekk Windows juri "Windows protected your PC": agħfas **More info**, imbagħad **Run anyway**.
3. Meta tiġi mistoqsi jekk tibgħatx għadd anonimu tal-użu, agħfas Enter għal le.
4. Tistaqsik jekk iżżidx iċ-ċwievet issa. Agħfas Enter biex taqbeż; ara
   [Il-pass taċ-ċwievet](#il-pass-taċ-ċwievet).
5. Meta tgħid **Done**, erġa' iftaħ l-apps tal-AI tiegħek. Jekk waħda kienet għadha miftuħa,
   agħlaqha għal kollox (anke mis-system tray, ħdejn l-arloġġ) u erġa' iftaħha.

Fl-aħħar l-installer jelenka l-apps li ssettja.

### Liema apps jissettja

Jissettja app biss jekk il-folder tas-settings ta' dik l-app ikun diġà fuq il-kompjuter tiegħek.
Claude Code jiġi ssettjat biss jekk jeżisti `~/.claude.json`. Claude Desktop jiġi ssettjat
dejjem. Kull app tieħu entrata waħda, `fontes`, f'dan il-fajl:

| App | Fajl (Mac u Linux) | Fajl (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, u l-kopja proprja tal-verżjoni tal-Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, jew `~/.codeium/windsurf/mcp_config.json` f'verżjonijiet eqdem | `%APPDATA%\devin\mcp_config.json`, jew `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code jiġi ssettjat jekk jeżisti `~/.copilot` jew il-folder tas-settings ta' VS Code stess.

Żewġ apps jeħtieġu pass ieħor:

- **Windsurf:** wara li terġa' tiftaħha, agħfas refresh f'Cascade.
- **Cline ġewwa l-estensjoni eqdem ta' VS Code:** żid Fontes bl-idejn (ara [Cline](#apps-oħra)).

### Il-pass taċ-ċwievet

Eżatt wara l-installazzjoni, l-installer joffri li jżid iċ-ċwievet b'xejn għal Franza u l-Istati
Uniti. Biex iżżidhom jew tibdilhom aktar tard:

- **Mac:** erġa' iftaħ **Fontes Installer** u agħżel **Żid jew ibdel iċ-ċwievet**.
- **Windows:** agħfas darbtejn fuq **Add or change keys.cmd** fil-folder tal-installer.

It-tajpjar huwa moħbi. Iċ-ċwievet imorru f'kull app li diġà għandha Fontes. Wara, agħlaq u erġa'
iftaħ l-apps. Minn fejn tikseb iċ-ċwievet u x'jiftħu: [KEYS.md](KEYS.md).

### Kopji ta' riżerva, tħaddim mill-ġdid u tneħħija

L-installer jibdel biss l-entrata `fontes`. Kull setting u kumment ieħor jibqa' kif kien. Qabel
ma jibdel fajl, jissejvja kopja ħdejh, bl-isem `<file>.fontes-backup-<date>`. Il-kopji magħmula
wara li żidt iċ-ċwievet fihom dawk iċ-ċwievet: ħassar dawk li m'għadekx bżonn. Jinstalla wkoll
uv. Li tħaddmu mill-ġdid huwa sigur: isewwi s-setup u ma jibdel xejn ieħor.

Biex tneħħi Fontes, iftaħ **Fontes Installer** u agħżel **Neħħi** (Mac), jew agħfas darbtejn fuq
**Uninstall Fontes.cmd** (Windows). Ineħħi l-entrata `fontes`, iċ-ċwievet inklużi, minn kull app.
Is-settings l-oħra tiegħek u l-kopji ta' riżerva jibqgħu.

## Aġġornamenti

- **Installer u fajl `.mcpb`:** m'għandek bżonn tagħmel xejn. Darba kuljum, meta tibda l-app,
  Fontes jiċċekkja fl-isfond jekk hemmx verżjoni ġdida u jħejjiha; id-darba ta' wara li tibda
  l-app tużaha. Jekk aġġornament ma jistax jitniżżel jew ma jaħdimx, Fontes jibqa' juża
  l-verżjoni li ħadmet.
- **`uvx`:** Fontes jgħidlek meta tkun disponibbli verżjoni ġdida, fil-quċċata tal-lista
  tal-ġurisdizzjonijiet tiegħu. Biex dejjem tħaddem l-aħħar verżjoni, uża `fontes-mcp@latest`
  minflok `fontes`.

Għal dan ma tintbagħat imkien l-ebda informazzjoni dwarek jew dwar it-tfittxijiet tiegħek.

## Privatezza

Fontes ma jibgħat xejn dwarek jew dwar it-tfittxijiet tiegħek b'mod awtomatiku. L-għadd tal-użu
jsir biss bil-kunsens tiegħek (opt-in), u rapport ta' żball jintbagħat biss wara li tarah u
tikkonferma. Dettalji: [PRIVACY.md](PRIVACY.md).

## Kif tneħħih

Neħħi l-entrata `fontes` mis-settings MCP tal-app tiegħek (f'Claude Code:
`claude mcp remove fontes`), imbagħad agħlaq u erġa' iftaħ l-app.

## Tajjeb tkun taf

Fontes jaqra sorsi pubbliċi, l-aktar siti web tal-qrati u tal-gvern. Jimmarka dawk mhux uffiċjali
fit-tweġibiet tiegħu. Dejjem iftaħ il-link tas-sors qabel ma tistrieħ fuq deċiżjoni jew
dispożizzjoni.

Jekk xi ħaġa tmur ħażin, ibgħat email lil fontesmcp@proton.me b'dak li għamilt u l-iżball li
rajt.

## Qabel ma tistrieħ fuqu

- Fontes huwa għodda tar-riċerka, mhux parir legali. L-użu tiegħu ma jagħmel lil ħadd l-avukat
  tiegħek.
- Huwa pprovdut "kif inhu" ("as is"), mingħajr garanzija, u l-awturi tiegħu mhumiex responsabbli
  għal kif jintuża, safejn il-liġi tippermetti. It-termini sħaħ jinsabu fil-
  [liċenzja](../../../LICENSE) (Apache 2.0).
