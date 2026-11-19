> 這是機器輔助的翻譯，以英文版本為準。

# 安裝 Fontes

Fontes 予你的 AI 應用程式佇法院佮政府的網站頂即時查法院裁判佮法規，涵蓋超過 120 个法域。逐筆結果攏有附
原文的連結。伊是標準的 MCP 伺服器，所以佇任何會當執行本機 MCP 伺服器的應用程式內底攏會當用：
Claude Desktop、Codex、Claude Code、Cursor、VS Code（GitHub Copilot）、Gemini CLI、Windsurf、Zed、
LM Studio、Cline 等等。

揀你的應用程式，照伊的步驟做，閣[確認有正常運作](#確認有正常運作)。

## Claude Desktop

1. 對[最新版本](https://github.com/ykarapazar/fontes/releases/latest)下載 Fontes 的 `.mcpb` 檔案。
2. 揤兩下。Claude Desktop 會拍開伊。
3. 揤 **Install**。

## Codex

佇終端機內底：

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI 佮 Codex IDE 擴充功能共用這个設定（`~/.codex/config.toml`）。
你需要 [uv](#你需要-uv)。

## Claude Code

佇終端機內底：

```bash
claude mcp add fontes -- uvx fontes-mcp
```

你需要 [uv](#你需要-uv)。

## 其他的應用程式

這寡應用程式攏需要 [uv](#你需要-uv)。加入項目、儲存，閣共應用程式關掉、重新拍開。

**Cursor：** 佇 `~/.cursor/mcp.json`（所有的專案）抑是 `.cursor/mcp.json`（一个專案）內底：

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code（GitHub Copilot）：** 對 Command Palette 執行 **MCP: Add Server**，揀
**Command (stdio)**，輸入 `uvx fontes-mcp`，共伺服器號做 `fontes`。抑是共下面的內容加到
`~/.copilot/mcp-config.json`：

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

較舊的 VS Code 設定用 `.vscode/mcp.json`，遐的上頂層鍵名是 `servers`，毋是 `mcpServers`。

**Gemini CLI：** 佇終端機內底執行 `gemini mcp add -s user fontes uvx fontes-mcp`。抑是共下面的內容加到
`~/.gemini/settings.json`：

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed：** 拍開你的設定檔（**zed: open settings file**），加入：

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio：** 佇正爿的側欄拍開 **Program** 分頁，揤 **Install → Edit mcp.json**，加入：

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline：** 揤 **MCP Servers** 圖示，拍開 **Configure** 分頁，揤 **Configure MCP Servers**，加入佮
LM Studio 仝款的 `mcpServers` 項目。

**Claude Desktop，用手設定**（代替 `.mcpb` 檔案）：共仝款的 `mcpServers` 項目加到
`claude_desktop_config.json`（macOS：`~/Library/Application Support/Claude/`，Windows：
`%APPDATA%\Claude\`）。

**任何其他的 MCP 應用程式**（Windsurf 等等）：伊家己的說明文件會講伊共 MCP 伺服器囥佇佗位。大部分用仝款的
項目：命令 `uvx`，參數 `fontes`。

若是應用程式揣無 `uvx`，請用伊的完整路徑（佇 macOS 佮 Linux 頂，`which uvx` 會印出來）。

## 你需要 uv

Codex、Claude Code 佮其他的應用程式用 `uvx` 啟動 Fontes，`uvx` 是佮 **uv** 做伙來的；uv 是 Astral 出的
細細仔免費工具。安裝方法請看 [Astral 的說明](https://docs.astral.sh/uv/getting-started/installation/)，
抑是執行：

- macOS 抑是 Linux：`curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows（PowerShell）：`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## 金鑰

有一寡來源需要免費的金鑰：請看 [KEYS.md](KEYS.md)。

## 確認有正常運作

佇新的對話內底問：*「Fontes 會當檢索佗一寡法域？」* 應用程式應該會用一張國家清單回答。若無，請共應用程式
關掉，閣拍開一擺。

## 一鍵安裝程式（Mac 佮 Windows）

安裝程式會一擺就佇你所有的應用程式內底設定好 Fontes：Claude Desktop、Codex、Claude Code、Cursor、
VS Code（GitHub Copilot）、Windsurf、Gemini CLI、Zed、LM Studio 佮 Cline。

**開始進前：** 共這寡應用程式逐个攏完全關掉。這對 Claude Code 上要緊：伊咧執行的時會重寫
`~/.claude.json`，可能會共安裝程式的修改復原。若是你關袂掉 Claude Code，請改用 `claude mcp add` 共 Fontes
加入去（請看 [Claude Code](#claude-code)）。

**Mac**

1. 對[最新版本](https://github.com/ykarapazar/fontes/releases/latest)下載 Mac 安裝程式（`Fontes-Installer-…-mac.zip`），
   揤兩下共伊解壓縮。
2. 揤兩下 **Fontes Installer**。若是你的 Mac 問你欲拍開對網路下載的應用程式無，揤 **Open**。
3. 揀 **安裝**，閣揤 **確定**。設定差不多愛一分鐘。
4. 會有一个訊息列出伊設定好的應用程式。揤 **完成**，才閣拍開遐的應用程式。若欲先加選擇性的免費金鑰，
   就改揤 **加入金鑰**；請看[金鑰步驟](#金鑰步驟)。

**Windows**

1. 對[最新版本](https://github.com/ykarapazar/fontes/releases/latest)下載 Windows 安裝程式（`Fontes-Setup-….exe`），揤兩下伊。
   - 若是 Windows 顯示「Windows 已保護您的電腦」：揤 **其他資訊**，閣揤 **仍要執行**。
2. 揤 **安裝**。會拍開一个視窗，設定好 Fontes。
3. 問你欲傳送匿名的使用次數統計無的時，揤 Enter 就是無愛。
4. 伊會問你這馬欲加金鑰無。揤 Enter 跳過；請看[金鑰步驟](#金鑰步驟)。
5. 伊講 **Done** 的時，閣拍開你的 AI 應用程式。若是有一个猶咧執行，請共伊完全關掉（嘛愛對時鐘邊仔的
   系統匣關掉），閣拍開。

上尾，安裝程式會列出伊設定好的應用程式。

### 安裝程式會設定佗一寡應用程式

干焦佇彼个應用程式的設定資料夾已經佇你電腦頂的時，伊才會設定彼个應用程式。干焦佇 `~/.claude.json` 存在的時
才會設定 Claude Code。Claude Desktop 一定會設定。逐个應用程式佇下面的檔案內底會有一个項目 `fontes`：

| 應用程式 | 檔案（Mac 佮 Linux） | 檔案（Windows） |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json`（Linux：`~/.config/Claude/`） | `%APPDATA%\Claude\claude_desktop_config.json`，佮 Microsoft Store 版本家己的副本 |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code（Copilot） | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`，較舊的版本是 `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`，抑是 `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

若是 `~/.copilot` 抑是 VS Code 家己的設定資料夾存在，就會設定 VS Code。

有兩个應用程式愛加做一步：

- **Windsurf：** 重新拍開了後，佇 Cascade 內底揤重新整理。
- **舊版 VS Code 擴充功能內底的 Cline：** 用手加入 Fontes（請看 [Cline](#其他的應用程式)）。

### 金鑰步驟

安裝好了後，安裝程式隨會問你欲加免費的法國佮美國金鑰無。以後欲加抑是改金鑰：

- **Mac：** 閣拍開 **Fontes Installer**，揀 **加入抑是更改金鑰**。
- **Windows：** 佇開始功能表揤 **Fontes** → **加入抑是更改金鑰**。

輸入的內容袂顯示。金鑰會寫入逐个已經有 Fontes 的應用程式。做好了後，請共應用程式關掉閣拍開。
金鑰對佗位提、會當拍開啥物：[KEYS.md](KEYS.md)。

### 備份、閣執行佮移除

安裝程式干焦會改 `fontes` 項目。其他的設定佮註解攏保持原樣。改一个檔案進前，伊會佇邊仔儲存一份副本，
號做 `<file>.fontes-backup-<date>`。佇你加金鑰了後做的副本包含這寡金鑰：無愛的請刪掉。伊嘛會安裝 uv。
閣執行一擺是安全的：伊會修復設定，其他的攏袂改。

欲移除 Fontes，請拍開 **Fontes Installer** 揀 **移除**（Mac），抑是佇 Settings → Apps 解除安裝 **Fontes**（Windows）。
伊會對逐个應用程式移除 `fontes` 項目，連金鑰嘛做伙。你其他的設定佮備份副本會保留。

## 更新

- **安裝程式佮 `.mcpb` 檔案：** 你啥物攏免做。逐工一擺，佇應用程式啟動的時，Fontes 會佇背景檢查有較新的
  版本無，先準備好；下一擺應用程式啟動的時就會用伊。若是更新下載袂成抑是袂當用，Fontes 會繼續用原來
  會用得的版本。
- **`uvx`：** 有較新的版本的時，Fontes 會佇伊的法域清單頂懸通知你。若欲一直執行上新的版本，請用
  `fontes-mcp@latest` 代替 `fontes-mcp`。

為著這件代誌，有關你抑是你的檢索的任何資訊攏袂送去任何所在。

## 隱私

Fontes 預設袂傳送任何有關你抑是你的檢索的物件。使用次數統計愛你選擇加入，錯誤回報干焦佇你看過、確認
了後才會送出去。詳細：[PRIVACY.md](PRIVACY.md)。

## 移除

對你應用程式的 MCP 設定移除 `fontes` 項目（佇 Claude Code 內底：`claude mcp remove fontes`），閣共應用程式
關掉、重新拍開。

## 愛知影的代誌

Fontes 讀公開的來源，大部分是法院佮政府的網站。伊會佇回答內底標出非官方的來源。欲靠一則裁判抑是一條條文
進前，一定愛先拍開來源的連結。

若是出問題，請共你做啥物佮你看著的錯誤訊息寄電子批到 fontesmcp@proton.me。

## 欲靠伊進前

- Fontes 是研究工具，毋是法律意見。用伊袂予任何人變做你的律師。
- 伊照「現狀」提供，無任何擔保；佇法律允准的範圍內，伊的作者對伊的使用方式無負責任。完整的條款佇
  [授權條款](../../../LICENSE)（Apache 2.0）內底。
