> Энэ бол машины тусламжтай хийсэн орчуулга. Англи хэл дээрх хувилбар нь давамгайлна.

# Fontes суулгах

Fontes нь таны AI аппад 125 харьяаллын шүүх болон төрийн вэбсайтаас шүүхийн шийдвэр,
хууль тогтоомжийг шууд хайх боломж олгодог. Үр дүн бүр эх хувь руу холбоостой. Энэ нь стандарт MCP
сервер тул локал MCP сервер ажиллуулж чаддаг аливаа аппад ажилладаг: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline болон бусад.

Аппаа сонгож, түүний алхмуудыг дагаад, дараа нь [ажиллаж байгааг шалгана уу](#ажиллаж-байгааг-шалгах).

## Claude Desktop

1. Fontes-ийн `.mcpb` файлыг
   [сүүлийн хувилбараас](https://github.com/ykarapazar/fontes/releases/latest) татна уу.
2. Үүнийг давхар товшино уу. Claude Desktop үүнийг нээнэ.
3. **Install**-ийг дарна уу.

## Codex

Терминалд:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI болон Codex IDE өргөтгөл энэ тохиргоог хуваалцдаг (`~/.codex/config.toml`).
Танд [uv](#uv-хэрэгтэй) хэрэгтэй.

## Claude Code

Терминалд:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Танд [uv](#uv-хэрэгтэй) хэрэгтэй.

## Бусад аппууд

Эдгээр бүрд [uv](#uv-хэрэгтэй) хэрэгтэй. Бичлэгийг нэмж, хадгалаад, аппыг хаагаад дахин нээнэ үү.

**Cursor:** `~/.cursor/mcp.json` (бүх төсөл) эсвэл `.cursor/mcp.json` (нэг төсөл)-д:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Command Palette-аас **MCP: Add Server**-ийг ажиллуулж,
**Command (stdio)**-г сонгоод, `uvx fontes-mcp` гэж оруулаад серверийг `fontes` гэж нэрлэнэ үү. Эсвэл үүнийг
`~/.copilot/mcp-config.json`-д нэмнэ үү:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

VS Code-ийн хуучин тохиргоонууд `.vscode/mcp.json`-г ашигладаг бөгөөд тэнд дээд түвшний түлхүүр нь `mcpServers`-ийн оронд
`servers` байдаг.

**Gemini CLI:** терминалд `gemini mcp add -s user fontes uvx fontes-mcp`. Эсвэл үүнийг
`~/.gemini/settings.json`-д нэмнэ үү:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** тохиргооны файлаа нээгээд (**zed: open settings file**) нэмнэ үү:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** баруун талын самбарт **Program** табыг нээж, **Install → Edit
mcp.json**-г дараад нэмнэ үү:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** дүрс тэмдгийг дарж, **Configure** табыг нээгээд, **Configure MCP
Servers**-ийг дарж, LM Studio-гийнхтой ижил `mcpServers` бичлэгийг нэмнэ үү.

**Claude Desktop, гараар** (`.mcpb` файлын оронд): ижил `mcpServers` бичлэгийг
`claude_desktop_config.json`-д нэмнэ үү (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Бусад аливаа MCP апп** (Windsurf болон бусад): өөрийнх нь баримт бичигт MCP серверүүдээ хаана
хадгалдгийг заасан байдаг. Ихэнх нь ижил бичлэгийг хүлээн авдаг: команд `uvx`, аргумент `fontes-mcp`.

Хэрэв апп `uvx`-ийг олж чадахгүй бол бүтэн замыг нь ашиглана уу (macOS болон Linux дээр `which uvx` үүнийг хэвлэнэ).

## uv хэрэгтэй

Codex, Claude Code болон бусад аппууд Fontes-ийг `uvx`-ээр эхлүүлдэг бөгөөд энэ нь Astral-ийн жижиг
үнэгүй хэрэгсэл болох **uv**-тай хамт ирдэг. Үүнийг суулгахын тулд
[Astral-ийн гарын авлагыг](https://docs.astral.sh/uv/getting-started/installation/) үзэх, эсвэл ажиллуулна уу:

- macOS эсвэл Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Түлхүүрүүд

Зарим эх сурвалжид үнэгүй түлхүүр хэрэгтэй: [KEYS.md](KEYS.md)-г үзнэ үү.

## Ажиллаж байгааг шалгах

Шинэ чат дээр асуу: *"Fontes ямар харьяаллуудаас хайж чадах вэ?"* Апп улсуудын жагсаалтаар
хариулах ёстой. Хэрэв хариулахгүй бол аппыг дахин нэг удаа хаагаад нээнэ үү.

## Нэг товшилтын суулгагч (Mac ба Windows)

Суулгагч Fontes-ийг бүх аппад тань нэг дор тохируулна: Claude Desktop, Codex, Claude Code,
Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio болон Cline.

**Эхлэхээсээ өмнө:** эдгээр апп бүрийг бүрэн хаана уу. Энэ нь Claude Code-д хамгийн чухал:
ажиллаж байх үедээ тэр `~/.claude.json`-г дахин бичиж, суулгагчийн өөрчлөлтийг буцааж болно. Хэрэв та Claude Code-ийг
хааж чадахгүй бол оронд нь `claude mcp add`-аар Fontes-ийг нэмнэ үү ([Claude Code](#claude-code)-г үзнэ үү).

**Mac**

1. Mac-ийн суулгагчийг (`Fontes-Installer-…-mac.zip`) [хамгийн сүүлийн
   хувилбараас](https://github.com/ykarapazar/fontes/releases/latest) татаж аваад, задлахын тулд
   давхар товшино уу.
2. **Fontes Installer**-ийг давхар товшино уу. Хэрэв таны Mac интернетээс татсан аппыг нээх эсэхийг
   асуувал **Open**-ийг товшино уу.
3. **Суулгах**-ыг сонгоод **OK**-г товшино уу. Тохируулга ойролцоогоор нэг минут үргэлжилнэ.
4. Мессежид тохируулсан аппуудыг жагсаана. **Дууссан**-ыг товшоод, дараа нь тэдгээр аппыг дахин
   нээнэ үү. Эхлээд заавал биш, үнэгүй түлхүүрүүдийг нэмэхийн тулд оронд нь **Түлхүүр нэмэх**-ийг
   товшино уу; [Түлхүүрийн алхам](#түлхүүрийн-алхам)-ыг үзнэ үү.

**Windows**

1. Windows-ийн суулгагчийг (`Fontes-Setup-….exe`) [хамгийн сүүлийн
   хувилбараас](https://github.com/ykarapazar/fontes/releases/latest) татаж аваад давхар товшино уу.
   - Хэрэв Windows "Windows protected your PC" гэж харуулбал: **More info**-г дараад, **Run anyway**-г дарна уу.
2. **Суулгах**-ыг товшино уу. Цонх нээгдэж Fontes-ийг тохируулна.
3. Нэргүй ашиглалтын тоо илгээх эсэхийг асуухад үгүй бол Enter дарна уу.
4. Түлхүүрүүдийг одоо нэмэх эсэхийг асууна. Алгасахын тулд Enter дарна уу; [Түлхүүрийн алхам](#түлхүүрийн-алхам)-ыг үзнэ үү.
5. **Done** гэж гарахад AI аппуудаа дахин нээнэ үү. Хэрэв аль нэг нь ажилласаар байсан бол түүнийг
   бүрэн хааж (цагны ойролцоох system tray-гаас ч), дахин нээнэ үү.

Төгсгөлд нь суулгагч тохируулсан аппуудаа жагсаана.

### Ямар аппуудыг тохируулдаг вэ

Аппын тохиргооны хавтас таны компьютер дээр аль хэдийн байгаа тохиолдолд л тэр аппыг тохируулна. Claude Code-ийг
`~/.claude.json` байгаа тохиолдолд л тохируулна. Claude Desktop-ийг үргэлж тохируулна. Апп бүр энэ файлд
нэг бичлэг, `fontes`-ийг авна:

| Апп | Файл (Mac ба Linux) | Файл (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, мөн Microsoft Store хувилбарын өөрийн хуулбар |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, эсвэл хуучин хувилбаруудад `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`, эсвэл `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

`~/.copilot` эсвэл VS Code-ийн өөрийн тохиргооны хавтас байвал VS Code-ийг тохируулна.

Хоёр апп нэг нэмэлт алхам шаарддаг:

- **Windsurf:** дахин нээсний дараа Cascade дотор refresh-ийг дарна уу.
- **VS Code-ийн хуучин өргөтгөл доторх Cline:** Fontes-ийг гараар нэмнэ үү ([Cline](#бусад-аппууд)-г үзнэ үү).

### Түлхүүрийн алхам

Суулгасны дараа шууд суулгагч Франц болон АНУ-ын үнэгүй түлхүүрүүдийг нэмэхийг санал болгоно. Тэдгээрийг дараа нь нэмэх эсвэл
өөрчлөхийн тулд:

- **Mac:** **Fontes Installer**-ийг дахин нээгээд **Түлхүүр нэмэх эсвэл өөрчлөх**-ийг сонгоно уу.
- **Windows:** Start цэснээс **Fontes** → **Түлхүүр нэмэх эсвэл өөрчлөх**-ийг сонгоно уу.

Бичсэн зүйл харагдахгүй. Түлхүүрүүд Fontes аль хэдийн байгаа апп бүрт орно. Дараа нь аппуудыг хаагаад
дахин нээнэ үү. Түлхүүрүүдийг хаанаас авах, юуг нээдэг тухай: [KEYS.md](KEYS.md).

### Нөөц хуулбар, дахин ажиллуулах ба хасах

Суулгагч зөвхөн `fontes` бичлэгийг өөрчилдөг. Бусад бүх тохиргоо болон тайлбар хэвээрээ үлдэнэ.
Файлыг өөрчлөхөөсөө өмнө хажууд нь `<file>.fontes-backup-<date>` нэртэй хуулбар хадгалдаг. Та түлхүүр
нэмсний дараа хийгдсэн хуулбарууд тэдгээр түлхүүрийг агуулдаг: хэрэггүй болсныг нь устгана уу. Мөн
uv-г суулгадаг. Дахин ажиллуулах нь аюулгүй: тохиргоог засаад өөр юуг ч өөрчлөхгүй.

Fontes-ийг хасахын тулд **Fontes Installer**-ийг нээгээд **Хасах**-ыг сонгох (Mac), эсвэл Windows-ийн Settings → Apps-аас **Fontes**-ийг устгана уу. Энэ нь `fontes` бичлэгийг түлхүүрүүдийн хамт апп бүрээс хасна. Таны бусад тохиргоо
болон нөөц хуулбарууд үлдэнэ.

## Шинэчлэлт

- **Суулгагч болон `.mcpb` файл:** та юу ч хийх шаардлагагүй. Өдөрт нэг удаа, апп
  эхлэх үед Fontes арын горимд шинэ хувилбар шалгаж, бэлтгэдэг; дараагийн удаа
  апп эхлэхэд түүнийг ашиглана. Шинэчлэлтийг татаж чадахгүй эсвэл ажиллахгүй бол Fontes
  ажиллаж байсан хувилбараа үргэлжлүүлэн ашиглана.
- **`uvx`:** шинэ хувилбар гарсан үед Fontes харьяаллын жагсаалтынхаа дээд хэсэгт танд
  мэдэгдэнэ. Үргэлж хамгийн шинэ хувилбарыг ажиллуулахын тулд `fontes-mcp`-ийн оронд `fontes-mcp@latest`-ийг ашиглана уу.

Үүний тулд таны тухай эсвэл таны хайлтын талаар ямар ч мэдээлэл хаашаа ч илгээгддэггүй.

## Нууцлал

Fontes анхдагчаар таны тухай эсвэл таны хайлтын талаар юу ч илгээдэггүй. Ашиглалтын тоо сонголтоор идэвхжих бөгөөд алдааны
тайланг зөвхөн та харж, баталгаажуулсны дараа илгээнэ. Дэлгэрэнгүй: [PRIVACY.md](PRIVACY.md).

## Хасах

Аппынхаа MCP тохиргооноос `fontes` бичлэгийг хасаад (Claude Code-д:
`claude mcp remove fontes`), дараа нь аппыг хаагаад дахин нээнэ үү.

## Мэдэж байх зүйлс

Fontes нийтийн эх сурвалжууд, голдуу шүүх болон төрийн вэбсайтуудыг уншдаг. Албан бус эх сурвалжуудыг
хариултдаа тэмдэглэдэг. Шийдвэр эсвэл заалтад найдахаасаа өмнө эх сурвалжийн холбоосыг үргэлж нээнэ үү.

Ямар нэг зүйл буруу болбол юу хийсэн, ямар алдаа харсан тухайгаа fontesmcp@proton.me хаягаар имэйлээр илгээнэ үү.

## Найдахаасаа өмнө

- Fontes бол судалгааны хэрэгсэл болохоос хуулийн зөвлөгөө биш. Үүнийг ашигласнаар хэн ч таны хуульч болохгүй.
- Үүнийг "байгаагаар нь" (as is), ямар ч баталгаагүйгээр олгож байгаа бөгөөд зохиогчид нь хуулийн зөвшөөрсөн хэмжээнд
  түүнийг хэрхэн ашигласанд хариуцлага хүлээхгүй. Бүрэн нөхцөл нь [лицензэд](../../../LICENSE) (Apache 2.0) бий.
