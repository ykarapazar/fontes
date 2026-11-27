> Fandikan-teny natao tamin'ny fanampian'ny milina ity. Ny dikan-teny anglisy no manan-kery.

# Fametrahana ny Fontes

Ahafahan'ny rindranasa AI-nao mitady didim-pitsarana sy lalàna mivantana ao amin'ny tranonkalan'ny
fitsarana sy ny fanjakana ny Fontes, amin'ny faritra ara-pitsarana 125. Misy rohy mankany
amin'ny antontan-taratasy tany am-boalohany ny valiny tsirairay. Mpizara MCP mahazatra izy, ka mandeha
amin'ny rindranasa rehetra afaka mandefa mpizara MCP eo an-toerana: Claude Desktop, Codex, Claude Code,
Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline sy ny hafa.

Safidio ny rindranasanao, araho ny dingana, dia [hamarino fa mandeha izy](#fanamarinana-fa-mandeha-izy).

## Claude Desktop

1. Alaivo ny rakitra `.mcpb` an'ny Fontes avy amin'ny
   [famoahana farany](https://github.com/ykarapazar/fontes/releases/latest).
2. Tsindrio indroa izy. Hosokafan'ny Claude Desktop izy.
3. Tsindrio ny **Install**.

## Codex

Ao anaty terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Mizara io fandrindrana io ny Codex CLI sy ny fanitarana Codex IDE (`~/.codex/config.toml`).
Mila [uv](#mila-uv-ianao) ianao.

## Claude Code

Ao anaty terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Mila [uv](#mila-uv-ianao) ianao.

## Rindranasa hafa

Samy mila [uv](#mila-uv-ianao) avokoa ireto. Ampidiro ilay fidirana, tehirizo, dia akatony ary sokafy
indray ilay rindranasa.

**Cursor:** ao amin'ny `~/.cursor/mcp.json` (tetikasa rehetra) na `.cursor/mcp.json` (tetikasa iray):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** alefaso ny **MCP: Add Server** avy ao amin'ny Command Palette, safidio ny
**Command (stdio)**, ampidiro ny `uvx fontes-mcp` ary omeo anarana hoe `fontes` ilay mpizara. Na ampio ity ao
amin'ny `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Ny fandrindrana VS Code taloha dia mampiasa ny `.vscode/mcp.json`, miaraka amin'ny fanalahidy ambony
indrindra `servers` fa tsy `mcpServers`.

**Gemini CLI:** ao anaty terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Na ampio ity ao amin'ny
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** sokafy ny rakitry ny fandrindrananao (**zed: open settings file**) ary ampio:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** ao amin'ny tsanganana an-daniny ankavanana, sokafy ny tabilao **Program**, tsindrio ny
**Install → Edit mcp.json**, ary ampio:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** tsindrio ny kisary **MCP Servers**, sokafy ny tabilao **Configure**, tsindrio ny **Configure MCP
Servers**, ary ampio ilay fidirana `mcpServers` mitovy amin'ny an'ny LM Studio.

**Claude Desktop, amin'ny tanana** (fa tsy ny rakitra `.mcpb`): ampio ilay fidirana `mcpServers` mitovy ao
amin'ny `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Rindranasa MCP hafa rehetra** (Windsurf sy ny hafa): ny antontan-taratasiny manokana no milaza ny toerana
itahirizany ny mpizara MCP-ny. Mandray ny fidirana mitovy ny ankamaroany: baiko `uvx`, tohan-kevitra
`fontes-mcp`.

Raha tsy hitan'ilay rindranasa ny `uvx`, ampiasao ny lalany feno (amin'ny macOS sy Linux, asehon'ny
`which uvx` izany).

## Mila uv ianao

Manomboka ny Fontes amin'ny `uvx` ny Codex, Claude Code ary ireo rindranasa hafa; miaraka amin'ny **uv** ny
`uvx`, fitaovana kely maimaim-poana avy amin'ny Astral. Raha hametraka azy, jereo ny
[torolalan'ny Astral](https://docs.astral.sh/uv/getting-started/installation/), na alefaso:

- macOS na Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Fanalahidy

Mila fanalahidy maimaim-poana ny loharano sasany: jereo ny [KEYS.md](KEYS.md).

## Fanamarinana fa mandeha izy

Ao amin'ny resaka vaovao, anontanio: *"Faritra ara-pitsarana inona avy no azon'ny Fontes karohina?"* Tokony
hamaly amin'ny lisitry ny firenena ilay rindranasa. Raha tsy izany, akatony ary sokafy indray ilay
rindranasa indray mandeha fanampiny.

## Mpametraka tsindry iray (Mac sy Windows)

Mametraka ny Fontes ao amin'ny rindranasanao rehetra indray mandeha ny mpametraka: Claude
Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio ary Cline.

**Alohan'ny hanombohanao:** akatony tanteraka ny tsirairay amin'ireo rindranasa ireo. Zava-dehibe indrindra
izany ho an'ny Claude Code: raha mandeha izy dia manoratra indray ny `~/.claude.json` ary mety hanafoana izay
novain'ny mpametraka. Raha tsy afaka manakatona ny Claude Code ianao, ampidiro ao aminy ny Fontes amin'ny
`claude mcp add` (jereo ny [Claude Code](#claude-code)).

**Mac**

1. Alaivo avy amin'ny [famoahana farany](https://github.com/ykarapazar/fontes/releases/latest) ny mpametraka
   ho an'ny Mac (`Fontes-Installer-…-mac.zip`) ary tsindrio indroa izy mba hamoahana azy.
2. Tsindrio indroa ny **Fontes Installer**. Raha manontany ny Mac-nao raha hanokatra rindranasa nalaina
   tamin'ny Internet, tsindrio ny **Open**.
3. Safidio ny **Apetraho** ary tsindrio ny **OK**. Iray minitra eo ho eo ny fametrahana.
4. Misy hafatra mitanisa ireo rindranasa napetrany. Tsindrio ny **Vita**, dia sokafy indray ireo rindranasa
   ireo. Raha te hanampy aloha ireo fanalahidy maimaim-poana tsy voatery ianao, tsindrio kosa ny
   **Hanampy fanalahidy**; jereo ny [Dingana fanalahidy](#dingana-fanalahidy).

**Windows**

1. Alaivo avy amin'ny [famoahana farany](https://github.com/ykarapazar/fontes/releases/latest) ny mpametraka ho an'ny Windows (`Fontes-Setup-….exe`) ary tsindrio indroa izy.
   - Raha aseho ny Windows ny "Windows protected your PC": tsindrio ny **More info**, dia **Run anyway**.
2. Tsindrio ny **Apetraho**. Misokatra ny varavarankely ary mametraka ny Fontes.
3. Rehefa anontaniana raha handefa isa fampiasana tsy mitonona anarana, tsindrio ny Enter raha tsia.
4. Manontany izy raha hanampy fanalahidy izao. Tsindrio ny Enter handinganana; jereo ny
   [Dingana fanalahidy](#dingana-fanalahidy).
5. Rehefa aseho ny **Vita**, sokafy indray ireo rindranasa AI-nao. Raha mbola mandeha ny iray, akatony
   tanteraka izy (eo amin'ny system tray koa, akaikin'ny famantaranandro) ary sokafy indray.

Amin'ny farany, mitanisa ireo rindranasa napetrany ny mpametraka.

### Rindranasa apetrany

Tsy mametraka rindranasa iray izy raha tsy efa ao amin'ny solosainao ny lahatahirin'ny fandrindrana an'io
rindranasa io. Tsy apetraka ny Claude Code raha tsy misy ny `~/.claude.json`. Apetraka foana ny Claude
Desktop. Mahazo fidirana iray, `fontes`, ao amin'ity rakitra ity ny rindranasa tsirairay:

| Rindranasa | Rakitra (Mac sy Linux) | Rakitra (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, sy ny dika manokan'ny kinova Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, na `~/.codeium/windsurf/mcp_config.json` amin'ny kinova taloha | `%APPDATA%\devin\mcp_config.json`, na `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

Apetraka ny VS Code raha misy ny `~/.copilot` na ny lahatahirin'ny fandrindrana an'ny VS Code mihitsy.

Rindranasa roa no mila dingana iray fanampiny:

- **Windsurf:** rehefa nosokafana indray, tsindrio ny refresh ao amin'ny Cascade.
- **Cline ao anatin'ny fanitarana VS Code taloha:** ampidiro amin'ny tanana ny Fontes (jereo ny
  [Cline](#rindranasa-hafa)).

### Dingana fanalahidy

Avy hatrany aorian'ny fametrahana, manolotra ny hanampy ireo fanalahidy maimaim-poana ho an'i Frantsa sy
Etazonia ny mpametraka. Raha hanampy na hanova azy ireo any aoriana:

- **Mac:** sokafy indray ny **Fontes Installer** ary safidio ny **Hanampy na hanova fanalahidy**.
- **Windows:** ao amin'ny menu Start, tsindrio **Fontes** → **Hanampy na hanova fanalahidy**.

Tsy aseho ny soratanao. Miditra ao amin'ny rindranasa rehetra efa manana ny Fontes ireo fanalahidy. Akatony
ary sokafy indray ireo rindranasa avy eo. Toerana hahazoana fanalahidy sy izay sokafany: [KEYS.md](KEYS.md).

### Dika fiarovana, famerenana sy fanesorana

Ny fidirana `fontes` ihany no ovain'ny mpametraka. Mijanona tsy miova ny fandrindrana sy fanamarihana hafa
rehetra. Alohan'ny hanovany rakitra iray, mitahiry dika eo akaikiny izy, antsoina hoe
`<file>.fontes-backup-<date>`. Misy ireo fanalahidy ireo dika natao taorian'ny nanampianao fanalahidy:
fafao izay tsy ilainao intsony. Mametraka ny uv koa izy. Azo antoka ny mamerina mandefa azy: manamboatra ny
fametrahana izy ary tsy manova zavatra hafa.

Raha hanala ny Fontes, sokafy ny **Fontes Installer** ary safidio ny **Esory** (Mac), na esorio **Fontes** ao amin'ny
Settings → Apps (Windows). Esoriny amin'ny rindranasa tsirairay ny fidirana `fontes`, anisan'izany
ny fanalahidy. Mijanona ny fandrindrana hafa sy ny dika fiarovana.

## Fanavaozana

- **Mpametraka sy rakitra `.mcpb`:** tsy misy tokony hataonao. Indray mandeha isan'andro, rehefa manomboka ny
  rindranasa iray, mijery ao ambadika raha misy kinova vaovao kokoa ny Fontes ary manomana azy; amin'ny
  fanombohana manaraka an'ilay rindranasa, io no ampiasainy. Raha tsy azo alaina na tsy mandeha ny
  fanavaozana iray, mbola mampiasa ny kinova mandeha ihany ny Fontes.
- **`uvx`:** milaza aminao ny Fontes rehefa misy kinova vaovao kokoa, eo an-tampon'ny lisitry ny faritra
  ara-pitsarana. Raha te handefa ny farany foana, ampiasao ny `fontes-mcp@latest` fa tsy `fontes-mcp`.

Tsy misy fampahalalana momba anao na ny fikarohanao alefa na aiza na aiza noho izany.

## Fiainana manokana (Privacy)

Tsy mandefa na inona na inona momba anao na ny fikarohanao ny Fontes raha tsy misy fanovana. Opt-in ny isa
fampiasana, ary alefa ihany ny tatitra momba ny olana rehefa avy nijery sy nanamafy azy ianao.
Antsipiriany: [PRIVACY.md](PRIVACY.md).

## Fanesorana azy

Esory ao amin'ny fandrindrana MCP an'ny rindranasanao ny fidirana `fontes` (ao amin'ny Claude Code:
`claude mcp remove fontes`), dia akatony ary sokafy indray ilay rindranasa.

## Tokony ho fantatra

Mamaky loharano ampahibemaso ny Fontes, ny ankamaroany tranonkalan'ny fitsarana sy ny fanjakana. Marihiny ao
amin'ny valiny omeny ireo loharano tsy ofisialy. Sokafy foana ny rohin'ny loharano alohan'ny hianteheranao
amin'ny didim-pitsarana na andininy iray.

Raha misy tsy mety, alefaso mailaka any amin'ny fontesmcp@proton.me izay nataonao sy ny hadisoana hitanao.

## Alohan'ny hianteheranao aminy

- Fitaovana fikarohana ny Fontes, fa tsy torohevitra ara-dalàna. Ny fampiasana azy dia tsy mahatonga na iza
  na iza ho mpisolovavanao.
- Omena "araka izao misy azy izao" izy, tsy misy antoka, ary tsy tompon'andraikitra amin'ny fomba
  fampiasana azy ireo mpanoratra azy, araka izay avelan'ny lalàna. Ao amin'ny
  [fahazoan-dalana](../../../LICENSE) (Apache 2.0) ny fepetra feno.
