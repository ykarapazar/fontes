> ນີ້ແມ່ນການແປໂດຍມີເຄື່ອງຈັກຊ່ວຍ. ສະບັບພາສາອັງກິດແມ່ນສະບັບທີ່ມີຜົນບັງຄັບ.

# ການຕິດຕັ້ງ Fontes

Fontes ຊ່ວຍໃຫ້ແອັບ AI ຂອງທ່ານຊອກຫາຄຳຕັດສິນຂອງສານ ແລະ ນິຕິກຳແບບສົດ ເທິງເວັບໄຊຂອງສານ ແລະ ຂອງລັດ
ໃນ 125 ເຂດອຳນາດ. ທຸກຜົນລັບມີລິ້ງໄປຫາຕົ້ນສະບັບ. ມັນເປັນເຊີບເວີ MCP
ມາດຕະຖານ, ສະນັ້ນ ມັນເຮັດວຽກໄດ້ໃນແອັບໃດກໍຕາມທີ່ສາມາດແລ່ນເຊີບເວີ MCP ໃນເຄື່ອງໄດ້: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline ແລະ ອື່ນໆ.

ເລືອກແອັບຂອງທ່ານ, ເຮັດຕາມຂັ້ນຕອນຂອງມັນ, ແລ້ວ [ກວດວ່າມັນເຮັດວຽກ](#ກວດວ່າມັນເຮັດວຽກ).

## Claude Desktop

1. ດາວໂຫຼດໄຟລ໌ `.mcpb` ຂອງ Fontes ຈາກ
   [ການເປີດຕົວລ່າສຸດ](https://github.com/ykarapazar/fontes/releases/latest).
2. ຄລິກສອງເທື່ອໃສ່ມັນ. Claude Desktop ຈະເປີດມັນ.
3. ຄລິກ **Install**.

## Codex

ໃນ terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI ແລະ ສ່ວນຂະຫຍາຍ Codex IDE ໃຊ້ການຕັ້ງຄ່ານີ້ຮ່ວມກັນ (`~/.codex/config.toml`).
ທ່ານຕ້ອງມີ [uv](#ທ່ານຕ້ອງມີ-uv).

## Claude Code

ໃນ terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

ທ່ານຕ້ອງມີ [uv](#ທ່ານຕ້ອງມີ-uv).

## ແອັບອື່ນໆ

ແຕ່ລະແອັບເຫຼົ່ານີ້ຕ້ອງການ [uv](#ທ່ານຕ້ອງມີ-uv). ເພີ່ມລາຍການ, ບັນທຶກ, ແລ້ວປິດແອັບ ແລະ ເປີດມັນຄືນໃໝ່.

**Cursor:** ໃນ `~/.cursor/mcp.json` (ທຸກໂຄງການ) ຫຼື `.cursor/mcp.json` (ໂຄງການດຽວ):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** ແລ່ນ **MCP: Add Server** ຈາກ Command Palette, ເລືອກ
**Command (stdio)**, ໃສ່ `uvx fontes-mcp` ແລະ ຕັ້ງຊື່ເຊີບເວີວ່າ `fontes`. ຫຼື ເພີ່ມສິ່ງນີ້ໃສ່
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

ການຕັ້ງຄ່າ VS Code ແບບເກົ່າໃຊ້ `.vscode/mcp.json`, ເຊິ່ງກະແຈລະດັບເທິງສຸດແມ່ນ `servers` ແທນທີ່ຈະເປັນ
`mcpServers`.

**Gemini CLI:** ໃນ terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. ຫຼື ເພີ່ມສິ່ງນີ້ໃສ່
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** ເປີດໄຟລ໌ການຕັ້ງຄ່າຂອງທ່ານ (**zed: open settings file**) ແລ້ວເພີ່ມ:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** ໃນແຖບດ້ານຂ້າງເບື້ອງຂວາ, ເປີດແຖບ **Program**, ຄລິກ **Install → Edit
mcp.json**, ແລ້ວເພີ່ມ:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** ຄລິກໄອຄອນ **MCP Servers**, ເປີດແຖບ **Configure**, ຄລິກ **Configure MCP
Servers**, ແລ້ວເພີ່ມລາຍການ `mcpServers` ດຽວກັນກັບຂອງ LM Studio.

**Claude Desktop, ດ້ວຍມື** (ແທນທີ່ຈະໃຊ້ໄຟລ໌ `.mcpb`): ເພີ່ມລາຍການ `mcpServers` ດຽວກັນໃສ່
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**ແອັບ MCP ອື່ນໆ** (Windsurf ແລະ ອື່ນໆ): ເອກະສານຂອງແອັບນັ້ນເອງ ບອກວ່າມັນເກັບເຊີບເວີ MCP
ໄວ້ຢູ່ໃສ. ສ່ວນໃຫຍ່ຮັບລາຍການດຽວກັນ: ຄຳສັ່ງ `uvx`, ອາກິວເມັນ `fontes-mcp`.

ຖ້າແອັບຊອກບໍ່ພົບ `uvx`, ໃຫ້ໃຊ້ເສັ້ນທາງເຕັມຂອງມັນ (ໃນ macOS ແລະ Linux, `which uvx` ຈະສະແດງມັນ).

## ທ່ານຕ້ອງມີ uv

Codex, Claude Code ແລະ ແອັບອື່ນໆ ເລີ່ມ Fontes ດ້ວຍ `uvx`, ເຊິ່ງມາພ້ອມກັບ **uv**, ເຄື່ອງມືນ້ອຍໆ
ທີ່ໃຊ້ຟຣີຈາກ Astral. ເພື່ອຕິດຕັ້ງມັນ, ເບິ່ງ
[ຄູ່ມືຂອງ Astral](https://docs.astral.sh/uv/getting-started/installation/), ຫຼື ແລ່ນ:

- macOS ຫຼື Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## ກະແຈ

ບາງແຫຼ່ງຕ້ອງການກະແຈຟຣີ: ເບິ່ງ [KEYS.md](KEYS.md).

## ກວດວ່າມັນເຮັດວຽກ

ໃນການສົນທະນາໃໝ່, ຖາມວ່າ: *"Fontes ສາມາດຄົ້ນຫາໃນເຂດອຳນາດໃດແດ່?"* ແອັບຄວນຕອບດ້ວຍ
ລາຍຊື່ປະເທດ. ຖ້າມັນບໍ່ຕອບ, ປິດແອັບ ແລະ ເປີດມັນຄືນໃໝ່ອີກຄັ້ງ.

## ໂປຣແກຣມຕິດຕັ້ງແບບຄລິກດຽວ (Mac ແລະ Windows)

ໂປຣແກຣມຕິດຕັ້ງຕັ້ງຄ່າ Fontes ໃນທຸກແອັບຂອງທ່ານໃນຄັ້ງດຽວ: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio ແລະ Cline.

**ກ່ອນທີ່ທ່ານຈະເລີ່ມ:** ປິດແຕ່ລະແອັບເຫຼົ່ານີ້ໃຫ້ໝົດ. ເລື່ອງນີ້ສຳຄັນທີ່ສຸດສຳລັບ Claude Code:
ໃນຂະນະທີ່ມັນແລ່ນຢູ່, ມັນຂຽນ `~/.claude.json` ຄືນໃໝ່ ແລະ ອາດຍົກເລີກການປ່ຽນແປງຂອງໂປຣແກຣມຕິດຕັ້ງ. ຖ້າທ່ານບໍ່ສາມາດ
ປິດ Claude Code ໄດ້, ໃຫ້ເພີ່ມ Fontes ເຂົ້າໃນມັນດ້ວຍ `claude mcp add` ແທນ (ເບິ່ງ [Claude Code](#claude-code)).

**Mac**

1. ດາວໂຫຼດໂປຣແກຣມຕິດຕັ້ງສຳລັບ Mac (`Fontes-Installer-…-mac.zip`) ຈາກ
   [ການເປີດຕົວລ່າສຸດ](https://github.com/ykarapazar/fontes/releases/latest) ແລ້ວຄລິກສອງເທື່ອໃສ່ມັນເພື່ອແຕກໄຟລ໌.
2. ຄລິກສອງເທື່ອໃສ່ **Fontes Installer**. ຖ້າ Mac ຂອງທ່ານຖາມວ່າຈະເປີດແອັບທີ່ດາວໂຫຼດມາຈາກ
   ອິນເຕີເນັດຫຼືບໍ່, ຄລິກ **Open**.
3. ເລືອກ **ຕິດຕັ້ງ** ແລ້ວຄລິກ **ຕົກລົງ**. ການຕັ້ງຄ່າໃຊ້ເວລາປະມານໜຶ່ງນາທີ.
4. ຂໍ້ຄວາມໜຶ່ງຈະລາຍຊື່ແອັບທີ່ມັນໄດ້ຕັ້ງຄ່າ. ຄລິກ **ສຳເລັດ**, ແລ້ວເປີດແອັບເຫຼົ່ານັ້ນອີກຄັ້ງ. ເພື່ອເພີ່ມ
   ກະແຈຟຣີທີ່ບໍ່ບັງຄັບກ່ອນ, ໃຫ້ຄລິກ **ເພີ່ມກະແຈ** ແທນ; ເບິ່ງ [ຂັ້ນຕອນກະແຈ](#ຂັ້ນຕອນກະແຈ).

**Windows**

1. ດາວໂຫຼດໂປຣແກຣມຕິດຕັ້ງສຳລັບ Windows (`Fontes-Setup-….exe`) ຈາກ [ການເປີດຕົວລ່າສຸດ](https://github.com/ykarapazar/fontes/releases/latest) ແລ້ວຄລິກສອງເທື່ອໃສ່ມັນ.
   - ຖ້າ Windows ສະແດງ "Windows protected your PC": ຄລິກ **More info**, ແລ້ວ **Run anyway**.
2. ຄລິກ **ຕິດຕັ້ງ**. ໜ້າຕ່າງຈະເປີດ ແລະ ຕິດຕັ້ງ Fontes.
3. ເມື່ອຖືກຖາມວ່າຈະສົ່ງຈຳນວນການນຳໃຊ້ແບບບໍ່ລະບຸຕົວຕົນຫຼືບໍ່, ກົດ Enter ສຳລັບ ບໍ່.
4. ມັນຖາມວ່າຈະເພີ່ມກະແຈດຽວນີ້ຫຼືບໍ່. ກົດ Enter ເພື່ອຂ້າມ; ເບິ່ງ [ຂັ້ນຕອນກະແຈ](#ຂັ້ນຕອນກະແຈ).
5. ເມື່ອມັນສະແດງ **Done**, ເປີດແອັບ AI ຂອງທ່ານອີກຄັ້ງ. ຖ້າມີແອັບໃດຍັງແລ່ນຢູ່, ປິດມັນ
   ໃຫ້ໝົດ (ລວມທັງຈາກ system tray, ໃກ້ກັບໂມງ) ແລ້ວເປີດມັນອີກຄັ້ງ.

ໃນຕອນທ້າຍ ໂປຣແກຣມຕິດຕັ້ງຈະລາຍຊື່ແອັບທີ່ມັນໄດ້ຕັ້ງຄ່າ.

### ມັນຕັ້ງຄ່າແອັບໃດແດ່

ມັນຕັ້ງຄ່າແອັບໜຶ່ງ ກໍຕໍ່ເມື່ອໂຟນເດີການຕັ້ງຄ່າຂອງແອັບນັ້ນມີຢູ່ໃນຄອມພິວເຕີຂອງທ່ານແລ້ວເທົ່ານັ້ນ. Claude Code
ຖືກຕັ້ງຄ່າ ກໍຕໍ່ເມື່ອ `~/.claude.json` ມີຢູ່ເທົ່ານັ້ນ. Claude Desktop ຖືກຕັ້ງຄ່າສະເໝີ. ແຕ່ລະແອັບໄດ້ຮັບ
ລາຍການດຽວ, `fontes`, ໃນໄຟລ໌ນີ້:

| ແອັບ | ໄຟລ໌ (Mac ແລະ Linux) | ໄຟລ໌ (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, ແລະ ສຳເນົາຂອງເວີຊັນ Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, ຫຼື `~/.codeium/windsurf/mcp_config.json` ໃນເວີຊັນເກົ່າ | `%APPDATA%\devin\mcp_config.json`, ຫຼື `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code ຖືກຕັ້ງຄ່າ ຖ້າ `~/.copilot` ຫຼື ໂຟນເດີການຕັ້ງຄ່າຂອງ VS Code ເອງມີຢູ່.

ສອງແອັບຕ້ອງການອີກໜຶ່ງຂັ້ນຕອນ:

- **Windsurf:** ຫຼັງຈາກເປີດມັນຄືນໃໝ່, ກົດ refresh ໃນ Cascade.
- **Cline ພາຍໃນສ່ວນຂະຫຍາຍ VS Code ແບບເກົ່າ:** ເພີ່ມ Fontes ດ້ວຍມື (ເບິ່ງ [Cline](#ແອັບອື່ນໆ)).

### ຂັ້ນຕອນກະແຈ

ທັນທີຫຼັງຈາກຕິດຕັ້ງ, ໂປຣແກຣມຕິດຕັ້ງສະເໜີໃຫ້ເພີ່ມກະແຈຟຣີຂອງຝຣັ່ງ ແລະ ສະຫະລັດ. ເພື່ອເພີ່ມ ຫຼື
ປ່ຽນພວກມັນໃນພາຍຫຼັງ:

- **Mac:** ເປີດ **Fontes Installer** ອີກຄັ້ງ ແລ້ວເລືອກ **ເພີ່ມ ຫຼື ປ່ຽນກະແຈ**.
- **Windows:** ເປີດເມນູ Start ແລ້ວເລືອກ **Fontes** → **Add or change keys**.

ສິ່ງທີ່ທ່ານພິມຈະຖືກເຊື່ອງໄວ້. ກະແຈຈະເຂົ້າໄປໃນທຸກແອັບທີ່ມີ Fontes ແລ້ວ. ປິດແອັບ ແລະ ເປີດພວກມັນຄືນໃໝ່
ຫຼັງຈາກນັ້ນ. ບ່ອນທີ່ຈະໄດ້ກະແຈ ແລະ ສິ່ງທີ່ພວກມັນເປີດໃຫ້ໃຊ້: [KEYS.md](KEYS.md).

### ສຳເນົາສຳຮອງ, ການແລ່ນຄືນ ແລະ ການຖອນອອກ

ໂປຣແກຣມຕິດຕັ້ງປ່ຽນແປງສະເພາະລາຍການ `fontes` ເທົ່ານັ້ນ. ການຕັ້ງຄ່າ ແລະ ຄຳເຫັນອື່ນໆທັງໝົດ ຍັງຄືເກົ່າ.
ກ່ອນທີ່ມັນຈະປ່ຽນໄຟລ໌ໃດ, ມັນບັນທຶກສຳເນົາໄວ້ຂ້າງໆ, ຕັ້ງຊື່ວ່າ `<file>.fontes-backup-<date>`. ສຳເນົາ
ທີ່ສ້າງຂຶ້ນຫຼັງຈາກທ່ານເພີ່ມກະແຈແລ້ວ ຈະມີກະແຈເຫຼົ່ານັ້ນຢູ່: ລຶບອັນທີ່ທ່ານບໍ່ຕ້ອງການອີກຕໍ່ໄປ. ມັນຍັງ
ຕິດຕັ້ງ uv ນຳ. ການແລ່ນມັນອີກຄັ້ງແມ່ນປອດໄພ: ມັນສ້ອມແປງການຕັ້ງຄ່າ ແລະ ບໍ່ປ່ຽນແປງສິ່ງອື່ນໃດ.

ເພື່ອຖອນ Fontes ອອກ, ເປີດ **Fontes Installer** ແລ້ວເລືອກ **ລຶບອອກ** (Mac), ຫຼື ຖອນ **Fontes** ອອກຈາກ Settings → Apps
(Windows). ມັນລຶບລາຍການ `fontes`, ລວມທັງກະແຈ, ອອກຈາກທຸກແອັບ. ການຕັ້ງຄ່າອື່ນໆຂອງທ່ານ
ແລະ ສຳເນົາສຳຮອງ ຍັງຄົງຢູ່.

## ການອັບເດດ

- **ໂປຣແກຣມຕິດຕັ້ງ ແລະ ໄຟລ໌ `.mcpb`:** ທ່ານບໍ່ຈຳເປັນຕ້ອງເຮັດຫຍັງ. ມື້ລະເທື່ອ, ເມື່ອແອັບ
  ເລີ່ມຕົ້ນ, Fontes ກວດຫາເວີຊັນໃໝ່ກວ່າໃນພື້ນຫຼັງ ແລະ ກະກຽມມັນໄວ້; ເທື່ອຕໍ່ໄປທີ່
  ແອັບເລີ່ມຕົ້ນ ມັນຈະໃຊ້ເວີຊັນນັ້ນ. ຖ້າການອັບເດດບໍ່ສາມາດດາວໂຫຼດໄດ້ ຫຼື ບໍ່ເຮັດວຽກ, Fontes ຈະສືບຕໍ່
  ໃຊ້ເວີຊັນທີ່ເຮັດວຽກໄດ້.
- **`uvx`:** Fontes ບອກທ່ານເມື່ອມີເວີຊັນໃໝ່ກວ່າ, ຢູ່ເທິງສຸດຂອງລາຍຊື່
  ເຂດອຳນາດຂອງມັນ. ເພື່ອແລ່ນເວີຊັນໃໝ່ທີ່ສຸດສະເໝີ, ໃຫ້ໃຊ້ `fontes-mcp@latest` ແທນ `fontes-mcp`.

ບໍ່ມີຂໍ້ມູນໃດໆກ່ຽວກັບທ່ານ ຫຼື ການຄົ້ນຫາຂອງທ່ານ ຖືກສົ່ງໄປບ່ອນໃດສຳລັບການນີ້.

## ຄວາມເປັນສ່ວນຕົວ

Fontes ບໍ່ສົ່ງຫຍັງກ່ຽວກັບທ່ານ ຫຼື ການຄົ້ນຫາຂອງທ່ານ ເປັນຄ່າເລີ່ມຕົ້ນ. ຈຳນວນການນຳໃຊ້ແມ່ນຕ້ອງເລືອກເຂົ້າຮ່ວມ, ແລະ ລາຍງານ
ຂໍ້ຜິດພາດຈະຖືກສົ່ງ ກໍຕໍ່ເມື່ອທ່ານໄດ້ເບິ່ງມັນ ແລະ ຢືນຢັນແລ້ວເທົ່ານັ້ນ. ລາຍລະອຽດ: [PRIVACY.md](PRIVACY.md).

## ການຖອນອອກ

ລຶບລາຍການ `fontes` ອອກຈາກການຕັ້ງຄ່າ MCP ຂອງແອັບທ່ານ (ໃນ Claude Code:
`claude mcp remove fontes`), ແລ້ວປິດແອັບ ແລະ ເປີດມັນຄືນໃໝ່.

## ສິ່ງທີ່ຄວນຮູ້

Fontes ອ່ານແຫຼ່ງສາທາລະນະ, ສ່ວນໃຫຍ່ແມ່ນເວັບໄຊຂອງສານ ແລະ ຂອງລັດ. ມັນໝາຍແຫຼ່ງທີ່ບໍ່ເປັນທາງການ ໃນ
ຄຳຕອບຂອງມັນ. ເປີດລິ້ງແຫຼ່ງທີ່ມາສະເໝີ ກ່ອນທີ່ຈະເຊື່ອຖືຄຳຕັດສິນ ຫຼື ບົດບັນຍັດໃດໜຶ່ງ.

ຖ້າມີບາງສິ່ງຜິດພາດ, ສົ່ງອີເມວບອກສິ່ງທີ່ທ່ານໄດ້ເຮັດ ແລະ ຂໍ້ຜິດພາດທີ່ທ່ານເຫັນ ໄປທີ່ fontesmcp@proton.me.

## ກ່ອນທີ່ທ່ານຈະເຊື່ອຖືມັນ

- Fontes ເປັນເຄື່ອງມືຄົ້ນຄວ້າ, ບໍ່ແມ່ນຄຳປຶກສາທາງກົດໝາຍ. ການໃຊ້ມັນບໍ່ໄດ້ເຮັດໃຫ້ຜູ້ໃດກາຍເປັນທະນາຍຄວາມຂອງທ່ານ.
- ມັນຖືກສະໜອງໃຫ້ "ຕາມສະພາບທີ່ເປັນຢູ່", ໂດຍບໍ່ມີການຮັບປະກັນ, ແລະ ຜູ້ຂຽນຂອງມັນບໍ່ຮັບຜິດຊອບຕໍ່ວິທີທີ່ມັນຖືກນຳໃຊ້,
  ເທົ່າທີ່ກົດໝາຍອະນຸຍາດ. ເງື່ອນໄຂເຕັມຢູ່ໃນ [ໃບອະນຸຍາດ](../../../LICENSE) (Apache 2.0).
