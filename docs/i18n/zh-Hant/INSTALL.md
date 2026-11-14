> 本文為機器輔助翻譯，以英文版本為準。

# 安裝 Fontes

Fontes 讓您的 AI 應用程式在法院與政府網站上即時查詢法院裁判與法規，涵蓋 120 多個法域。每筆結果都附有
原文連結。它是標準的 MCP 伺服器，因此可在任何能執行本機 MCP 伺服器的應用程式中使用：Claude Desktop、
Codex、Claude Code、Cursor、VS Code（GitHub Copilot）、Gemini CLI、Windsurf、Zed、LM Studio、Cline 等。

選擇您的應用程式，依照其步驟操作，然後[確認是否正常運作](#確認是否正常運作)。

## Claude Desktop

1. 從[最新版本](https://github.com/ykarapazar/fontes/releases/latest)下載 Fontes 的 `.mcpb` 檔案。
2. 按兩下該檔案。Claude Desktop 會開啟它。
3. 點選 **Install**。

## Codex

在終端機中：

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI 與 Codex IDE 擴充功能共用此設定（`~/.codex/config.toml`）。
您需要 [uv](#您需要-uv)。

## Claude Code

在終端機中：

```bash
claude mcp add fontes -- uvx fontes-mcp
```

您需要 [uv](#您需要-uv)。

## 其他應用程式

以下每個應用程式都需要 [uv](#您需要-uv)。加入項目、儲存，然後結束並重新開啟應用程式。

**Cursor：** 在 `~/.cursor/mcp.json`（所有專案）或 `.cursor/mcp.json`（單一專案）中：

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code（GitHub Copilot）：** 從命令選擇區執行 **MCP: Add Server**，選擇
**Command (stdio)**，輸入 `uvx fontes-mcp`，並將伺服器命名為 `fontes`。或將以下內容加入
`~/.copilot/mcp-config.json`：

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

較舊的 VS Code 設定使用 `.vscode/mcp.json`，其中最上層鍵名是 `servers` 而不是 `mcpServers`。

**Gemini CLI：** 在終端機中執行 `gemini mcp add -s user fontes uvx fontes-mcp`。或將以下內容加入
`~/.gemini/settings.json`：

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed：** 開啟您的設定檔（**zed: open settings file**）並加入：

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio：** 在右側側邊欄開啟 **Program** 分頁，點選 **Install → Edit mcp.json**，並加入：

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline：** 點選 **MCP Servers** 圖示，開啟 **Configure** 分頁，點選 **Configure MCP
Servers**，並加入與 LM Studio 相同的 `mcpServers` 項目。

**手動設定 Claude Desktop**（取代 `.mcpb` 檔案）：將相同的 `mcpServers` 項目加入
`claude_desktop_config.json`（macOS：`~/Library/Application Support/Claude/`，Windows：
`%APPDATA%\Claude\`）。

**任何其他 MCP 應用程式**（Windsurf 等）：其本身的說明文件會說明它將 MCP 伺服器存放在哪裡。大多數使用相同的
項目：命令 `uvx`，引數 `fontes`。

如果應用程式找不到 `uvx`，請使用其完整路徑（在 macOS 與 Linux 上，`which uvx` 會顯示該路徑）。

## 您需要 uv

Codex、Claude Code 與其他應用程式透過 `uvx` 啟動 Fontes，`uvx` 隨 **uv** 一併提供，uv 是 Astral 推出的
小型免費工具。安裝方式請參閱 [Astral 的指南](https://docs.astral.sh/uv/getting-started/installation/)，
或執行：

- macOS 或 Linux：`curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows（PowerShell）：`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## 金鑰

部分來源需要免費金鑰：請參閱 [KEYS.md](KEYS.md)。

## 確認是否正常運作

在新的對話中詢問：*「Fontes 可以檢索哪些法域？」* 應用程式應該會回覆一份國家清單。如果沒有，請再結束並
重新開啟應用程式一次。

## 一鍵安裝程式（Mac）

Mac 安裝程式可一次在您所有的應用程式中設定 Fontes：Claude Desktop、Codex、Claude Code、Cursor、
VS Code（GitHub Copilot）、Windsurf、Gemini CLI、Zed、LM Studio 與 Cline。Windows 安裝程式即將推出；
在那之前，請依照上方您所用應用程式的步驟操作。

**開始之前：** 完全結束上述每個應用程式。這一點對 Claude Code 最重要：它執行時會改寫 `~/.claude.json`，
可能復原安裝程式所做的變更。如果您無法結束 Claude Code，請改用 `claude mcp add` 將 Fontes 加入其中
（請參閱 [Claude Code](#claude-code)）。

**Mac**

1. 從[最新發行版本](https://github.com/ykarapazar/fontes/releases/latest)下載 Mac 安裝程式
   （`Fontes-Installer-…-mac.zip`），然後按兩下將其解壓縮。
2. 按兩下 **Fontes Installer**。如果您的 Mac 詢問是否要打開從網際網路下載的應用程式，請按一下
   **打開**。
3. 選擇 **安裝**，然後按一下 **確定**。設定約需一分鐘。
4. 訊息會列出已設定的應用程式。按一下 **完成**，然後重新開啟這些應用程式。若要先新增選用的免費
   金鑰，請改按 **新增金鑰**；請參閱[金鑰步驟](#金鑰步驟)。

**Windows**（Windows 安裝程式發布之後）

1. 解壓縮下載的 **Fontes Installer**（按右鍵 → 解壓縮全部）。
2. 按兩下 **Install Fontes.cmd**。
   - 如果 Windows 顯示「Windows 已保護您的電腦」：按一下 **其他資訊**，然後按 **仍要執行**。
3. 詢問是否傳送匿名使用次數統計時，按 Enter 表示否。
4. 它會詢問是否現在新增金鑰。按 Enter 略過；請參閱[金鑰步驟](#金鑰步驟)。
5. 顯示 **Done** 時，重新開啟您的 AI 應用程式。如果某個應用程式仍在執行，請將其完全關閉（也要從時鐘附近的
   系統匣關閉），然後重新開啟。

最後，安裝程式會列出它已設定的應用程式。

### 安裝程式會設定哪些應用程式

只有當某個應用程式的設定資料夾已存在於您的電腦上時，安裝程式才會設定該應用程式。只有在 `~/.claude.json`
存在時，才會設定 Claude Code。Claude Desktop 一律會被設定。每個應用程式都會在下列檔案中取得一個項目
`fontes`：

| 應用程式 | 檔案（Mac 與 Linux） | 檔案（Windows） |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json`（Linux：`~/.config/Claude/`） | `%APPDATA%\Claude\claude_desktop_config.json`，以及 Microsoft Store 版本自己的副本 |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code（Copilot） | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`，舊版本為 `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`，或 `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

如果 `~/.copilot` 或 VS Code 本身的設定資料夾存在，就會設定 VS Code。

有兩個應用程式還需要多一個步驟：

- **Windsurf：** 重新開啟後，在 Cascade 中按重新整理。
- **舊版 VS Code 擴充功能中的 Cline：** 手動加入 Fontes（請參閱 [Cline](#其他應用程式)）。

### 金鑰步驟

安裝完成後，安裝程式會立即提供新增免費的法國與美國金鑰的選項。日後要新增或變更金鑰：

- **Mac：** 再次開啟 **Fontes Installer** 並選擇 **新增或變更金鑰**。
- **Windows：** 按兩下安裝程式資料夾中的 **Add or change keys.cmd**。

輸入內容不會顯示。金鑰會寫入每個已安裝 Fontes 的應用程式。之後請結束並重新開啟這些應用程式。金鑰的取得
方式以及它們能開啟的內容：[KEYS.md](KEYS.md)。

### 備份、重新執行與移除

安裝程式只會變更 `fontes` 項目。其他所有設定與註解都維持原樣。在變更某個檔案之前，它會在旁邊儲存一份副本，
名稱為 `<file>.fontes-backup-<date>`。在您新增金鑰之後產生的副本包含這些金鑰：請刪除您不再需要的副本。它也會
安裝 uv。再次執行是安全的：它會修復設定，不會變更其他任何內容。

要移除 Fontes，請開啟 **Fontes Installer** 並選擇 **移除**（Mac），或按兩下 **Uninstall Fontes.cmd**
（Windows）。它會從每個應用程式中移除 `fontes` 項目（包括金鑰）。您的其他設定與備份副本會保留。

## 更新

- **安裝程式與 `.mcpb` 檔案：** 您不需要做任何事。每天一次，在應用程式啟動時，Fontes 會在背景檢查是否有
  新版本並將其準備好；應用程式下次啟動時就會使用它。如果更新無法下載或無法正常運作，Fontes 會繼續使用原先
  可正常運作的版本。
- **`uvx`：** 有新版本可用時，Fontes 會在其法域清單的最上方告訴您。若要一律執行最新版本，請以
  `fontes-mcp@latest` 取代 `fontes-mcp`。

為此不會將任何關於您或您檢索內容的資訊傳送到任何地方。

## 隱私

預設情況下，Fontes 不會傳送任何關於您或您檢索內容的資訊。使用次數統計須由您選擇加入，錯誤回報只有在您
看過並確認後才會傳送。詳情：[PRIVACY.md](PRIVACY.md)。

## 移除

從應用程式的 MCP 設定中移除 `fontes` 項目（在 Claude Code 中：`claude mcp remove fontes`），然後結束並
重新開啟應用程式。

## 須知

Fontes 讀取公開來源，主要是法院與政府網站。它會在回答中標示非官方來源。依賴某則裁判或條文之前，
請務必開啟來源連結。

如果發生問題，請將您的操作與看到的錯誤以電子郵件寄至 fontesmcp@proton.me。

## 依賴之前

- Fontes 是研究工具，並非法律意見。使用它不會使任何人成為您的律師。
- 它依「現狀」提供，不附帶任何擔保；在法律允許的範圍內，其作者對其使用方式不負任何責任。完整條款請見
  [授權條款](../../../LICENSE)（Apache 2.0）。
