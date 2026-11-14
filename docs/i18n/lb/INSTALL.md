> Dëst ass eng maschinnegestëtzt Iwwersetzung. Déi englesch Versioun ass moossgeblech.

# Fontes installéieren

Mat Fontes kann Är KI-App Geriichtsentscheedungen a Gesetzgebung live op de Websäite vu
Geriichter a Regierungen a méi wéi 120 Rechtsuerdnungen nokucken. All Resultat verlinkt op
d'Original. Et ass e Standard-MCP-Server a funktionéiert dofir an all App, déi e lokale MCP-Server
lafe loosse kann: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI,
Windsurf, Zed, LM Studio, Cline an anerer.

Wielt Är App, maacht d'Schrëtt, an
[kontrolléiert dann, ob et funktionéiert](#kontrolléieren-ob-et-funktionéiert).

## Claude Desktop

1. Luet de Fontes-Fichier `.mcpb` aus der
   [neister Release](https://github.com/ykarapazar/fontes/releases/latest) erof.
2. Klickt duebel drop. Claude Desktop mécht en op.
3. Klickt op **Install**.

## Codex

An engem Terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

D'Codex CLI an d'Codex-IDE-Extensioun deelen dës Astellung (`~/.codex/config.toml`).
Dir braucht [uv](#dir-braucht-uv).

## Claude Code

An engem Terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Dir braucht [uv](#dir-braucht-uv).

## Aner Apps

All dës Apps brauchen [uv](#dir-braucht-uv). Setzt d'Entrée derbäi, späichert, maacht d'App zou a
maacht se nees op.

**Cursor:** an `~/.cursor/mcp.json` (all Projeten) oder `.cursor/mcp.json` (ee Projet):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Lafe loosst **MCP: Add Server** aus der Befehlspalett, wielt
**Command (stdio)**, gitt `uvx fontes-mcp` an a nennt de Server `fontes`. Oder setzt dat hei an
`~/.copilot/mcp-config.json` derbäi:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Méi al VS-Code-Installatioune benotzen `.vscode/mcp.json`, wou den ieweschte Schlëssel `servers`
amplaz `mcpServers` ass.

**Gemini CLI:** an engem Terminal `gemini mcp add -s user fontes uvx fontes-mcp`. Oder setzt dat hei an
`~/.gemini/settings.json` derbäi:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** Maacht Ären Astellungsfichier op (**zed: open settings file**) a setzt derbäi:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** Maacht an der rietser Säiteleescht den Tab **Program** op, klickt op **Install → Edit
mcp.json** a setzt derbäi:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** Klickt op d'Symbol **MCP Servers**, maacht den Tab **Configure** op, klickt op
**Configure MCP Servers** a setzt déi selwecht `mcpServers`-Entrée derbäi wéi bei LM Studio.

**Claude Desktop, mat der Hand** (amplaz vum `.mcpb`-Fichier): Setzt déi selwecht
`mcpServers`-Entrée an `claude_desktop_config.json` derbäi (macOS:
`~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`).

**All aner MCP-App** (Windsurf an anerer): an der eegener Dokumentatioun vun der App steet, wou se
hir MCP-Server späichert. Déi meescht benotzen déi selwecht Entrée: Befeel `uvx`, Argument `fontes`.

Wann d'App `uvx` net fënnt, benotzt de komplette Wee (op macOS a Linux weist `which uvx` en).

## Dir braucht uv

Codex, Claude Code an déi aner Apps starte Fontes mat `uvx`, dat mat **uv** kënnt, engem klenge
gratis Tool vun Astral. Fir et z'installéieren, kuckt de
[Guide vun Astral](https://docs.astral.sh/uv/getting-started/installation/), oder lafe loosst:

- macOS oder Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Schlësselen

E puer Quelle brauchen e gratis Schlëssel: kuckt [KEYS.md](KEYS.md).

## Kontrolléieren, ob et funktionéiert

Frot an engem neie Chat: *„Wéi eng Rechtsuerdnunge kann Fontes duerchsichen?“* D'App sollt mat
enger Lëscht vu Länner äntweren. Wann net, maacht d'App nach eng Kéier zou a nees op.

## Installatiounsprogramm mat engem Klick (Mac)

Den Installatiounsprogramm fir Mac riicht Fontes an engem Gang an all Ären Apps an: Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio a Cline.
En Installatiounsprogramm fir Windows ass ënnerwee; bis dohin benotzt d'Schrëtt fir Är App hei uewen.

**Ier Dir ufänkt:** Maacht all dës Apps komplett zou. Dat ass besonnesch fir Claude Code wichteg:
Wärend et leeft, schreift et `~/.claude.json` nei a kann d'Ännerung vum Installatiounsprogramm
réckgängeg maachen. Wann Dir Claude Code net zoumaache kënnt, setzt Fontes amplaz dovunner mat
`claude mcp add` derbäi (kuckt [Claude Code](#claude-code)).

**Mac**

1. Luet den Installatiounsprogramm fir Mac (`Fontes-Installer-…-mac.zip`) vun der
   [neister Versioun](https://github.com/ykarapazar/fontes/releases/latest) erof a klickt duebel drop, fir en auszepaken.
2. Klickt duebel op **Fontes Installer**. Wann Äre Mac freet, ob en eng App opmaache soll, déi vum
   Internet erofgeluede gouf, klickt op **Open**.
3. Wielt **Installéieren** a klickt op **OK**. D'Ariichten dauert ongeféier eng Minutt.
4. E Message weist d'Apps, déi en ageriicht huet. Klickt op **Fäerdeg** a maacht dës Apps dann nees
   op. Fir d'éischt déi fakultativ gratis Schlësselen derbäizesetzen, klickt amplaz op
   **Schlësselen derbäisetzen**; kuckt
   [Schlësselen am Installatiounsprogramm](#schlësselen-am-installatiounsprogramm).

**Windows** (soubal den Installatiounsprogramm fir Windows eraus ass)

1. Paakt den erofgeluedenen **Fontes Installer** aus (Klick mat der rietser Maustast → **Extract
   All**).
2. Klickt duebel op **Install Fontes.cmd**.
   - Wann Windows "Windows protected your PC" weist: Klickt op **More info**, an dann op
     **Run anyway**.
3. Wann et freet, ob Dir anonym Notzungszuele schécke wëllt, dréckt Enter fir nee.
4. Et freet, ob Dir elo Schlësselen derbäisetze wëllt. Dréckt Enter fir ze iwwersprangen; kuckt
   [Schlësselen am Installatiounsprogramm](#schlësselen-am-installatiounsprogramm).
5. Wann **Fäerdeg** erschéngt, maacht Är KI-Apps nees op. Wann eng nach leeft, maacht se komplett
   zou (och aus dem Systembereich nieft der Auer) a maacht se nees op.

Um Enn weist den Installatiounsprogramm d'Apps, déi en ageriicht huet.

### Wéi eng Apps et ariicht

En riicht eng App just an, wann den Astellungsdossier vun där App schonn op Ärem Computer ass.
Claude Code gëtt just ageriicht, wann `~/.claude.json` existéiert. Claude Desktop gëtt ëmmer
ageriicht. All App kritt eng Entrée, `fontes`, an dësem Fichier:

| App | Fichier (Mac a Linux) | Fichier (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, an déi eege Kopie vun der Microsoft-Store-Versioun |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, oder `~/.codeium/windsurf/mcp_config.json` bei méi alen Versiounen | `%APPDATA%\devin\mcp_config.json`, oder `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code gëtt ageriicht, wann `~/.copilot` oder den eegenen Astellungsdossier vu VS Code existéiert.

Zwou Apps brauchen nach ee Schrëtt:

- **Windsurf:** Dréckt nom Neiopmaachen a Cascade op refresh.
- **Cline an der méi aler VS-Code-Extensioun:** Setzt Fontes mat der Hand derbäi (kuckt
  [Cline](#aner-apps)).

### Schlësselen am Installatiounsprogramm

Direkt no der Installatioun proposéiert den Installatiounsprogramm, déi gratis Schlësselen fir
Frankräich an d'USA derbäizesetzen. Fir se méi spéit derbäizesetzen oder z'änneren:

- **Mac:** Maacht **Fontes Installer** nees op a wielt **Schlësselen derbäisetzen oder änneren**.
- **Windows:** Klickt duebel op **Add or change keys.cmd** am Dossier vum Installatiounsprogramm.

Wat Dir tippt, bleift verstoppt. D'Schlësselen ginn an all App derbäigesat, déi Fontes schonn huet.
Maacht d'Apps duerno zou an nees op. Wou Dir d'Schlësselen kritt a wat se zougänglech maachen:
[KEYS.md](KEYS.md).

### Sécherheetskopien, nach eng Kéier lafe loossen an ewechhuelen

Den Installatiounsprogramm ännert just d'Entrée `fontes`. All aner Astellungen a Kommentarer
bleiwen, wéi se waren. Ier en e Fichier ännert, späichert en eng Kopie dernieft, mam Numm
`<file>.fontes-backup-<date>`. Kopien, déi gemaach goufen, nodeems Dir Schlësselen derbäigesat hutt,
enthalen dës Schlësselen: läscht déi Kopien, déi Dir net méi braucht. En installéiert och uv. Nach
eng Kéier lafe loossen ass ouni Risiko: et fléckt d'Installatioun an ännert soss näischt.

Fir Fontes ewechzehuelen, maacht **Fontes Installer** op a wielt **Ewechhuelen** (Mac), oder
klickt duebel op **Uninstall Fontes.cmd** (Windows). Dat hëlt d'Entrée `fontes`, mat de
Schlësselen, aus all App eraus. Är aner Astellungen an d'Sécherheetskopie bleiwen.

## Updates

- **Installatiounsprogramm an `.mcpb`-Fichier:** Dir musst näischt maachen. Eemol am Dag, wann d'App
  start, kuckt Fontes am Hannergrond, ob et eng méi nei Versioun gëtt, a mécht se prett; déi nächst
  Kéier, wou d'App start, gëtt se benotzt. Wann en Update net erofgeluede ka ginn oder net
  funktionéiert, benotzt Fontes weider d'Versioun, déi funktionéiert huet.
- **`uvx`:** Fontes seet uewen a senger Lëscht vu Rechtsuerdnungen, wann eng méi nei Versioun
  disponibel ass. Fir ëmmer déi neiste Versioun ze benotzen, benotzt `fontes-mcp@latest` amplaz
  `fontes`.

Dofir gëtt keng Informatioun iwwer Iech oder Är Sich geschéckt.

## Dateschutz

Fontes schéckt standardméisseg näischt iwwer Iech oder Är Sich. Notzungszuele sinn Opt-in, an e
Feelerbericht gëtt just geschéckt, nodeems Dir en gesinn a bestätegt hutt. Detailer:
[PRIVACY.md](PRIVACY.md).

## Desinstalléieren

Läscht d'Entrée `fontes` aus den MCP-Astellunge vun Ärer App (an Claude Code:
`claude mcp remove fontes`), maacht d'App dann zou a nees op.

## Gutt ze wëssen

Fontes liest ëffentlech Quellen, haaptsächlech Websäite vu Geriichter a Regierungen. Inoffiziell
Quelle markéiert et a sengen Äntwerten. Maacht ëmmer de Link op d'Quell op, ier Dir Iech op eng
Entscheedung oder eng Bestëmmung verloosst.

Wann eppes schifgeet, schreift un fontesmcp@proton.me, wat Dir gemaach hutt a wéi eng Feelermeldung
Dir gesinn hutt.

## Ier Dir Iech drop verloosst

- Fontes ass e Recherche-Tool, keng Rechtsberodung. Duerch seng Notzung gëtt keen Ären Affekot.
- Et gëtt „sou wéi et ass“ zur Verfügung gestallt, ouni Garantie, a seng Auteure sinn, souwäit
  d'Gesetz et erlaabt, net haftbar fir dat, wat domat gemaach gëtt. Déi komplett Konditioune stinn
  an der [Lizenz](../../../LICENSE) (Apache 2.0).
