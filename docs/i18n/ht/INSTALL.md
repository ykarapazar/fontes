> Sa a se yon tradiksyon ki fèt avèk èd machin. Se vèsyon angle a ki fè lafwa.

# Enstale Fontes

Fontes pèmèt aplikasyon IA ou chèche desizyon tribinal ak lejislasyon an dirèk sou sit entènèt tribinal ak
gouvènman yo, nan plis pase 120 jiridiksyon. Chak rezilta gen yon lyen ki mennen nan orijinal la. Se yon
sèvè MCP estanda, kidonk li mache nan nenpòt aplikasyon ki ka fè yon sèvè MCP lokal mache: Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline ak lòt
ankò.

Chwazi aplikasyon ou, swiv etap pou li yo, epi [verifye si li mache](#verifye-si-li-mache).

## Claude Desktop

1. Telechaje fichye `.mcpb` Fontes la nan
   [dènye vèsyon an](https://github.com/ykarapazar/fontes/releases/latest).
2. Klike de fwa sou li. Claude Desktop louvri l.
3. Klike sou **Install**.

## Codex

Nan yon tèminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI ak ekstansyon Codex pou IDE a pataje paramèt sa a (`~/.codex/config.toml`).
Ou bezwen [uv](#ou-bezwen-uv).

## Claude Code

Nan yon tèminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Ou bezwen [uv](#ou-bezwen-uv).

## Lòt aplikasyon

Chak nan aplikasyon sa yo bezwen [uv](#ou-bezwen-uv). Ajoute antre a, sove, epi fèmen aplikasyon an nèt
e louvri l ankò.

**Cursor:** nan `~/.cursor/mcp.json` (tout pwojè) oswa `.cursor/mcp.json` (yon sèl pwojè):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** lanse **MCP: Add Server** nan Command Palette, chwazi **Command (stdio)**,
antre `uvx fontes-mcp`, epi rele sèvè a `fontes`. Oswa ajoute sa a nan `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Ansyen konfigirasyon VS Code yo sèvi ak `.vscode/mcp.json`, kote kle nivo siperyè a se `servers` olye de
`mcpServers`.

**Gemini CLI:** nan yon tèminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Oswa ajoute sa a nan
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** louvri fichye paramèt la (**zed: open settings file**) epi ajoute:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** nan ba kote adwat la, louvri onglè **Program** la, klike sou **Install → Edit mcp.json**,
epi ajoute:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klike sou ikòn **MCP Servers** la, louvri onglè **Configure** la, klike sou **Configure MCP
Servers**, epi ajoute menm antre `mcpServers` la tankou pou LM Studio.

**Claude Desktop, alamen** (olye de fichye `.mcpb` la): ajoute menm antre `mcpServers` la nan
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Nenpòt lòt aplikasyon MCP** (Windsurf ak lòt): pwòp dokimantasyon li di ki kote li kenbe sèvè MCP li
yo. Pifò pran menm antre a: kòmand `uvx`, agiman `fontes`.

Si aplikasyon an pa jwenn `uvx`, sèvi ak chemen konplè a (sou macOS ak Linux, `which uvx` montre l).

## Ou bezwen uv

Codex, Claude Code ak lòt aplikasyon yo lanse Fontes ak `uvx`, ki vini ak **uv**, yon ti zouti gratis
Astral fè. Pou enstale l, gade [gid Astral la](https://docs.astral.sh/uv/getting-started/installation/)
oswa lanse:

- macOS oswa Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Kle

Kèk sous bezwen yon kle gratis: gade [KEYS.md](KEYS.md).

## Verifye si li mache

Nan yon nouvo konvèsasyon, mande: *"Nan ki jiridiksyon Fontes ka fè rechèch?"* Aplikasyon an ta dwe
reponn ak yon lis peyi. Si li pa fè sa, fèmen aplikasyon an nèt epi louvri l ankò yon lòt fwa.

## Enstalatè an yon sèl klik (Mac ak Windows)

Enstalatè a mete Fontes nan tout aplikasyon ou yo an yon sèl fwa: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio ak Cline.

**Anvan ou kòmanse:** fèmen chak nan aplikasyon sa yo nèt. Sa pi enpòtan pou Claude Code: pandan l ap
mache, li reekri `~/.claude.json` e li ka defèt chanjman enstalatè a. Si ou pa ka fèmen Claude Code, ajoute
Fontes ladan l ak `claude mcp add` pito (gade [Claude Code](#claude-code)).

**Mac**

1. Telechaje enstalatè Mac la (`Fontes-Installer-…-mac.zip`) nan
   [dènye vèsyon an](https://github.com/ykarapazar/fontes/releases/latest) epi klike de fwa sou li
   pou dekonprese l.
2. Klike de fwa sou **Fontes Installer**. Si Mac la mande w si pou l louvri yon aplikasyon ki
   telechaje sou entènèt, klike sou **Open**.
3. Chwazi **Enstale** epi klike sou **OK**. Konfigirasyon an pran anviwon yon minit.
4. Yon mesaj bay lis aplikasyon li konfigire yo. Klike sou **Fini**, epi louvri aplikasyon sa yo ankò.
   Pou ajoute kle gratis opsyonèl yo anvan, klike sou **Ajoute kle** pito; gade
   [Etap kle yo](#etap-kle-yo).

**Windows**

1. Telechaje enstalatè Windows la (`Fontes-Setup-….exe`) nan
   [dènye vèsyon an](https://github.com/ykarapazar/fontes/releases/latest) epi klike de fwa sou li.
   - Si Windows montre "Windows protected your PC": klike sou **More info**, epi sou **Run anyway**.
2. Klike sou **Enstale**. Yon fenèt louvri epi konfigire Fontes.
3. Lè li mande w si ou vle voye kantite itilizasyon anonim, peze Enter pou non.
4. Li mande w si ou vle ajoute kle kounye a. Peze Enter pou sote sa; gade [Etap kle yo](#etap-kle-yo).
5. Lè **Fini** parèt, louvri aplikasyon IA ou yo ankò. Si youn te toujou ap mache, fèmen l nèt (ladan l
   nan zòn notifikasyon an, akote revèy la) epi louvri l ankò.

Nan fen, enstalatè a bay lis aplikasyon li konfigire yo.

### Ki aplikasyon li konfigire

Li konfigire yon aplikasyon sèlman si dosye paramèt aplikasyon sa a deja egziste sou òdinatè a. Claude
Code konfigire sèlman si `~/.claude.json` egziste. Claude Desktop toujou konfigire. Chak aplikasyon resevwa
yon sèl antre, `fontes`, nan fichye sa a:

| Aplikasyon | Fichye (Mac ak Linux) | Fichye (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` ak pwòp kopi vèsyon Microsoft Store la |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` oswa, pou ansyen vèsyon yo, `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` oswa `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code konfigire si `~/.copilot` oswa pwòp dosye paramèt VS Code la egziste.

De aplikasyon bezwen yon etap anplis:

- **Windsurf:** apre ou relouvri l, peze rafrechi nan Cascade.
- **Cline nan ansyen ekstansyon VS Code la:** ajoute Fontes alamen (gade [Cline](#lòt-aplikasyon)).

### Etap kle yo

Touswit apre enstalasyon an, enstalatè a ofri w pou ajoute kle gratis pou Lafrans ak Etazini. Pou ajoute
oswa chanje yo pita:

- **Mac:** louvri **Fontes Installer** ankò epi chwazi **Ajoute oswa chanje kle**.
- **Windows:** louvri meni Start la, epi chwazi **Fontes** → **Add or change keys**.

Sa ou tape a kache. Kle yo ale nan chak aplikasyon ki deja gen Fontes. Apre sa, fèmen aplikasyon yo nèt
epi louvri yo ankò. Ki kote pou jwenn kle yo ak sa yo debloke: [KEYS.md](KEYS.md).

### Kopi sekou, relanse ak retire

Enstalatè a chanje sèlman antre `fontes` la. Tout lòt paramèt ak kòmantè rete jan yo te ye a. Anvan li
chanje yon fichye, li sove yon kopi akote l, ki rele `<file>.fontes-backup-<date>`. Kopi ki fèt apre ou
ajoute kle yo gen kle sa yo ladan yo: efase sa ou pa bezwen yo. Li enstale uv tou. Ou ka lanse l ankò san
pwoblèm: li repare konfigirasyon an e li pa chanje anyen lòt.

Pou retire Fontes, louvri **Fontes Installer** epi chwazi **Retire** (Mac), oswa retire **Fontes** nan Settings → Apps (Windows). Li retire antre `fontes` la, ansanm ak kle yo, nan chak aplikasyon.
Lòt paramèt ak kopi sekou yo rete.

## Mizajou

- **Enstalatè a ak fichye `.mcpb` la:** ou pa bezwen fè anyen. Yon fwa pa jou, lè aplikasyon ou demare,
  Fontes tcheke an awyè-plan si gen yon vèsyon ki pi nouvo epi li prepare l; pwochen fwa aplikasyon an
  demare, li sèvi avè l. Si yon mizajou pa ka telechaje oswa li pa mache, Fontes kontinye sèvi ak vèsyon ki
  t ap mache a.
- **`uvx`:** Fontes di w lè gen yon vèsyon ki pi nouvo, anwo lis jiridiksyon li yo. Pou toujou fè dènye
  vèsyon an mache, sèvi ak `fontes-mcp@latest` olye de `fontes-mcp`.

Pou sa, pa gen anyen sou ou oswa sou rechèch ou yo ki voye okenn kote.

## Vi prive

Pa defo, Fontes pa voye anyen sou ou oswa sou rechèch ou yo. Kantite itilizasyon se sèlman si ou dakò
(opt-in), e yon rapò erè voye sèlman apre ou fin wè l epi ou konfime l. Detay: [PRIVACY.md](PRIVACY.md).

## Retire l

Retire antre `fontes` la nan paramèt MCP aplikasyon an (nan Claude Code: `claude mcp remove fontes`), epi
fèmen aplikasyon an nèt e louvri l ankò.

## Bon pou konnen

Fontes li sous piblik, sitou sit entènèt tribinal ak gouvènman. Li make sous ki pa ofisyèl yo nan repons
li yo. Toujou louvri lyen sous la anvan ou konte sou yon desizyon oswa yon dispozisyon.

Si yon bagay pa mache, voye yon imèl bay fontesmcp@proton.me ak sa ou te fè ak erè ou te wè a.

## Anvan ou konte sou li

- Fontes se yon zouti rechèch, se pa konsèy jiridik. Lè w sèvi avè l sa pa fè pèsonn tounen avoka ou.
- Li bay "jan li ye a", san garanti, e otè li yo pa responsab pou jan moun sèvi avè l, otan lalwa
  pèmèt. Tout kondisyon yo nan [lisans lan](../../../LICENSE) (Apache 2.0).
