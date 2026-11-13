> 這係機器輔助个翻譯，以英文版本為準。

# 安裝 Fontes

Fontes 分你个 AI 應用程式在法院同政府个網站頂即時查法院裁判同法規，涵蓋 120 過个法域。每一筆結果都附
原文个連結。佢係標準个 MCP 伺服器，所以在任何做得執行本機 MCP 伺服器个應用程式肚項都做得用：
Claude Desktop、Codex、Claude Code、Cursor、VS Code（GitHub Copilot）、Gemini CLI、Windsurf、Zed、
LM Studio、Cline 等等。

揀你个應用程式，照佢个步驟做，再[確定有正常運作](#確定有正常運作)。

## Claude Desktop

1. 從[最新版本](https://github.com/ykarapazar/fontes/releases/latest)下載 Fontes 个 `.mcpb` 檔案。
2. 撳兩下。Claude Desktop 會打開佢。
3. 撳 **Install**。

## Codex

在終端機肚項：

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI 同 Codex IDE 擴充功能共用這个設定（`~/.codex/config.toml`）。
你需要 [uv](#你需要-uv)。

## Claude Code

在終端機肚項：

```bash
claude mcp add fontes -- uvx fontes-mcp
```

你需要 [uv](#你需要-uv)。

## 其他應用程式

這兜應用程式都需要 [uv](#你需要-uv)。加入項目、儲存，再將應用程式關忒、重新打開。

**Cursor：** 在 `~/.cursor/mcp.json`（所有專案）或者 `.cursor/mcp.json`（一个專案）肚項：

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code（GitHub Copilot）：** 從 Command Palette 執行 **MCP: Add Server**，揀
**Command (stdio)**，輸入 `uvx fontes-mcp`，將伺服器號名做 `fontes`。或者將下背个內容加到
`~/.copilot/mcp-config.json`：

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

較舊个 VS Code 設定用 `.vscode/mcp.json`，該位个最上層鍵名係 `servers`，毋係 `mcpServers`。

**Gemini CLI：** 在終端機肚項執行 `gemini mcp add -s user fontes uvx fontes-mcp`。或者將下背个內容加到
`~/.gemini/settings.json`：

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed：** 打開你个設定檔（**zed: open settings file**），加入：

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio：** 在右片个側欄打開 **Program** 分頁，撳 **Install → Edit mcp.json**，加入：

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline：** 撳 **MCP Servers** 圖示，打開 **Configure** 分頁，撳 **Configure MCP Servers**，加入同
LM Studio 共樣个 `mcpServers` 項目。

**Claude Desktop，用手設定**（代替 `.mcpb` 檔案）：將共樣个 `mcpServers` 項目加到
`claude_desktop_config.json`（macOS：`~/Library/Application Support/Claude/`，Windows：
`%APPDATA%\Claude\`）。

**任何其他个 MCP 應用程式**（Windsurf 等等）：佢自家个說明文件會講佢將 MCP 伺服器放在哪位。大部分用共樣个
項目：命令 `uvx`，參數 `fontes`。

若係應用程式尋毋著 `uvx`，請用佢个完整路徑（在 macOS 同 Linux 頂，`which uvx` 會印出來）。

## 你需要 uv

Codex、Claude Code 同其他應用程式用 `uvx` 啟動 Fontes，`uvx` 係同 **uv** 做一下來个；uv 係 Astral 出个
細細个免費工具。安裝方法請看 [Astral 个說明](https://docs.astral.sh/uv/getting-started/installation/)，
或者執行：

- macOS 或者 Linux：`curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows（PowerShell）：`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## 金鑰

有兜來源需要免費个金鑰：請看 [KEYS.md](KEYS.md)。

## 確定有正常運作

在新个對話肚項問：*「Fontes 做得檢索哪兜法域？」* 應用程式應該會用一張國家清單回答。若係無，請將應用程式
關忒，再打開一擺。

## 一鍵安裝程式（就會推出）

一个做得一擺就在你所有个應用程式肚項設定好 Fontes 个 Mac 同 Windows 安裝程式就會推出。佢會設定
Claude Desktop、Codex、Claude Code、Cursor、VS Code（GitHub Copilot）、Windsurf、Gemini CLI、Zed、
LM Studio 同 Cline。發布以後：

**開始以前：** 將這兜應用程式逐个都完全關忒。這對 Claude Code 上重要：佢在執行个時節會重寫
`~/.claude.json`，可能會將安裝程式个修改復原。若係你關毋忒 Claude Code，請改用 `claude mcp add` 將 Fontes
加到佢肚項（請看 [Claude Code](#claude-code)）。

**Mac**

1. 打開下載个 **Fontes Installer** 資料夾。
2. 撳兩下 **Install Fontes.command**。
   - 若係你个 Mac 講「無法打開，因為佢來自未識別个開發者」：用滑鼠右鍵撳（或者撳 Control 再撳）該檔案，
     揀 **Open**，再撳一擺 **Open**。這單淨愛做一擺。
3. 會打開一个視窗，問你愛毋愛傳送匿名个使用次數統計；撳 Enter 就係毋愛。
4. 佢會問你這下愛毋愛加金鑰。撳 Enter 略過；請看[金鑰步驟](#金鑰步驟)。
5. 佢講 **Done** 个時節，再打開你个 AI 應用程式。

**Windows**

1. 將下載个 **Fontes Installer** 解壓縮（滑鼠右鍵 → 全部解壓縮）。
2. 撳兩下 **Install Fontes.cmd**。
   - 若係 Windows 顯示「Windows 已保護您的電腦」：撳 **其他資訊**，再撳 **仍要執行**。
3. 問你愛毋愛傳送匿名个使用次數統計个時節，撳 Enter 就係毋愛。
4. 佢會問你這下愛毋愛加金鑰。撳 Enter 略過；請看[金鑰步驟](#金鑰步驟)。
5. 佢講 **Done** 个時節，再打開你个 AI 應用程式。若係有一个還在執行，請將佢完全關忒（也愛從時鐘附近个
   系統匣關忒），再打開。

最尾，安裝程式會列出佢設定好个應用程式。

### 安裝程式會設定哪兜應用程式

單淨在該應用程式个設定資料夾已經在你電腦頂个時節，佢正會設定該應用程式。單淨在 `~/.claude.json` 存在个時節
正會設定 Claude Code。Claude Desktop 一定會設定。每一个應用程式在下背个檔案肚項會有一个項目 `fontes`：

| 應用程式 | 檔案（Mac 同 Linux） | 檔案（Windows） |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json`（Linux：`~/.config/Claude/`） | `%APPDATA%\Claude\claude_desktop_config.json`，同 Microsoft Store 版本自家个副本 |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code（Copilot） | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`，較舊个版本係 `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`，或者 `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

若係 `~/.copilot` 或者 VS Code 自家个設定資料夾存在，就會設定 VS Code。

有兩个應用程式愛多做一步：

- **Windsurf：** 重新打開以後，在 Cascade 肚項撳重新整理。
- **舊版 VS Code 擴充功能肚項个 Cline：** 用手加入 Fontes（請看 [Cline](#其他應用程式)）。

### 金鑰步驟

安裝好以後，安裝程式馬上會問你愛毋愛加免費个法國同美國金鑰。以後愛加或者改金鑰：

- **Mac：** 撳兩下安裝程式資料夾肚項个 **Add or change keys.command**，或者再打開 Fontes Installer
  應用程式，揀 **Add or change keys**。
- **Windows：** 撳兩下安裝程式資料夾肚項个 **Add or change keys.cmd**。

輸入个內容毋會顯示。金鑰會寫入每一个已經有 Fontes 个應用程式。做好以後，請將應用程式關忒再打開。
金鑰對哪位拿、做得打開麼个：[KEYS.md](KEYS.md)。

### 備份、再執行同移除

安裝程式單淨會改 `fontes` 項目。其他个設定同註解都保持原樣。改一个檔案以前，佢會在旁邊儲存一份副本，
名做 `<file>.fontes-backup-<date>`。在你加金鑰以後做个副本包含這兜金鑰：毋使个請刪忒。佢也會安裝 uv。
再執行一擺係安全个：佢會修復設定，其他个麼个都毋會改。

愛移除 Fontes，請撳兩下 **Uninstall Fontes.command**（Mac）或者 **Uninstall Fontes.cmd**（Windows）。
佢會從每一个應用程式移除 `fontes` 項目，連金鑰也做一下。你其他个設定同備份副本會保留。

## 更新

- **安裝程式同 `.mcpb` 檔案：** 你麼个都毋使做。逐日一擺，在應用程式啟動个時節，Fontes 會在背景檢查有無
  較新个版本，先準備好；下一擺應用程式啟動个時節就會用佢。若係更新下載毋著或者無法度用，Fontes 會繼續用
  原來做得用个版本。
- **`uvx`：** 有較新个版本个時節，Fontes 會在佢个法域清單个頂高通知你。若愛一直執行最新个版本，請用
  `fontes-mcp@latest` 代替 `fontes-mcp`。

為了這件事，有關你或者你个檢索个任何資訊都毋會送到任何所在。

## 隱私

Fontes 預設毋會傳送任何有關你或者你个檢索个東西。使用次數統計愛你選擇加入，錯誤回報單淨在你看過、確認
以後正會送出去。詳細：[PRIVACY.md](PRIVACY.md)。

## 移除

從你應用程式个 MCP 設定移除 `fontes` 項目（在 Claude Code 肚項：`claude mcp remove fontes`），再將應用程式
關忒、重新打開。

## 愛知个事

Fontes 讀公開个來源，大部分係法院同政府个網站。佢會在回答肚項標出非官方个來源。愛靠一則裁判或者一條條文
以前，一定愛先打開來源个連結。

若係出問題，請將你做麼个同你看著个錯誤訊息寄電子郵件到 fontesmcp@proton.me。

## 愛靠佢以前

- Fontes 係研究工具，毋係法律意見。用佢毋會使任何人變做你个律師。
- 佢照「現狀」提供，無任何擔保；在法律允許个範圍內，佢个作者對佢个使用方式毋使負責任。完整个條款在
  [授權條款](../../../LICENSE)（Apache 2.0）肚項。
