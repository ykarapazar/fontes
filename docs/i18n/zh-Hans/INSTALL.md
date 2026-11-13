> 本文为机器辅助翻译，以英文版本为准。

# 安装 Fontes

Fontes 让您的 AI 应用在法院和政府网站上实时查询裁判文书和法律法规，覆盖 120 多个法域。每条结果都附有
原文链接。它是一个标准的 MCP 服务器，因此可在任何能够运行本地 MCP 服务器的应用中使用：Claude Desktop、
Codex、Claude Code、Cursor、VS Code（GitHub Copilot）、Gemini CLI、Windsurf、Zed、LM Studio、Cline 等。

选择您的应用，按照其步骤操作，然后[检查是否正常运行](#检查是否正常运行)。

## Claude Desktop

1. 从[最新版本](https://github.com/ykarapazar/fontes/releases/latest)下载 Fontes 的 `.mcpb` 文件。
2. 双击它。Claude Desktop 会打开它。
3. 点击 **Install**。

## Codex

在终端中：

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI 和 Codex IDE 扩展共用这一设置（`~/.codex/config.toml`）。
您需要 [uv](#您需要-uv)。

## Claude Code

在终端中：

```bash
claude mcp add fontes -- uvx fontes-mcp
```

您需要 [uv](#您需要-uv)。

## 其他应用

以下每个应用都需要 [uv](#您需要-uv)。添加条目，保存，然后退出并重新打开应用。

**Cursor：** 在 `~/.cursor/mcp.json`（所有项目）或 `.cursor/mcp.json`（单个项目）中：

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code（GitHub Copilot）：** 在命令面板中运行 **MCP: Add Server**，选择
**Command (stdio)**，输入 `uvx fontes-mcp`，并将服务器命名为 `fontes`。或者将以下内容添加到
`~/.copilot/mcp-config.json`：

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

较旧的 VS Code 设置使用 `.vscode/mcp.json`，其中顶层键是 `servers` 而不是 `mcpServers`。

**Gemini CLI：** 在终端中运行 `gemini mcp add -s user fontes uvx fontes-mcp`。或者将以下内容添加到
`~/.gemini/settings.json`：

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed：** 打开您的设置文件（**zed: open settings file**）并添加：

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio：** 在右侧边栏中打开 **Program** 选项卡，点击 **Install → Edit mcp.json**，并添加：

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline：** 点击 **MCP Servers** 图标，打开 **Configure** 选项卡，点击 **Configure MCP
Servers**，并添加与 LM Studio 相同的 `mcpServers` 条目。

**手动配置 Claude Desktop**（代替 `.mcpb` 文件）：将相同的 `mcpServers` 条目添加到
`claude_desktop_config.json`（macOS：`~/Library/Application Support/Claude/`，Windows：
`%APPDATA%\Claude\`）。

**任何其他 MCP 应用**（Windsurf 等）：其自身的文档会说明它在哪里保存 MCP 服务器。大多数使用相同的条目：
命令 `uvx`，参数 `fontes`。

如果应用找不到 `uvx`，请使用其完整路径（在 macOS 和 Linux 上，`which uvx` 会显示该路径）。

## 您需要 uv

Codex、Claude Code 和其他应用通过 `uvx` 启动 Fontes，`uvx` 随 **uv** 一起提供，uv 是 Astral 出品的一个
小型免费工具。安装方法请参见 [Astral 的指南](https://docs.astral.sh/uv/getting-started/installation/)，
或运行：

- macOS 或 Linux：`curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows（PowerShell）：`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## 密钥

有些来源需要免费密钥：参见 [KEYS.md](KEYS.md)。

## 检查是否正常运行

在新的对话中提问：*“Fontes 可以检索哪些法域？”* 应用应当回复一份国家列表。如果没有，请再次退出并重新
打开应用。

## 一键安装程序（即将推出）

一个可一次性在您所有应用中设置 Fontes 的 Mac 和 Windows 安装程序即将推出。它会设置 Claude Desktop、
Codex、Claude Code、Cursor、VS Code（GitHub Copilot）、Windsurf、Gemini CLI、Zed、LM Studio 和
Cline。发布后：

**开始之前：** 完全退出上述每个应用。这一点对 Claude Code 最为重要：它运行时会重写 `~/.claude.json`，
可能撤销安装程序所做的更改。如果您无法退出 Claude Code，请改用 `claude mcp add` 将 Fontes 添加到其中
（参见 [Claude Code](#claude-code)）。

**Mac**

1. 打开下载的 **Fontes Installer** 文件夹。
2. 双击 **Install Fontes.command**。
   - 如果您的 Mac 提示“无法打开，因为它来自身份不明的开发者”：
     右键点击（或按住 Control 键点击）该文件，选择 **打开**，然后再点击一次 **打开**。此操作只需
     进行一次。
3. 会打开一个窗口，询问是否发送匿名使用计数；按 Enter 表示否。
4. 它会询问是否现在添加密钥。按 Enter 跳过；参见[密钥步骤](#密钥步骤)。
5. 显示 **Done** 时，重新打开您的 AI 应用。

**Windows**

1. 解压下载的 **Fontes Installer**（右键点击 → 全部解压缩）。
2. 双击 **Install Fontes.cmd**。
   - 如果 Windows 显示“Windows 已保护你的电脑”：点击 **更多信息**，然后点击 **仍要运行**。
3. 询问是否发送匿名使用计数时，按 Enter 表示否。
4. 它会询问是否现在添加密钥。按 Enter 跳过；参见[密钥步骤](#密钥步骤)。
5. 显示 **Done** 时，重新打开您的 AI 应用。如果某个应用仍在运行，请将其完全关闭（也要从时钟附近的
   系统托盘中关闭），然后重新打开。

最后，安装程序会列出它已设置的应用。

### 安装程序会设置哪些应用

只有当某个应用的设置文件夹已存在于您的电脑上时，安装程序才会设置该应用。只有当 `~/.claude.json`
存在时，才会设置 Claude Code。Claude Desktop 总是会被设置。每个应用都会在以下文件中获得一个条目
`fontes`：

| 应用 | 文件（Mac 和 Linux） | 文件（Windows） |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json`（Linux：`~/.config/Claude/`） | `%APPDATA%\Claude\claude_desktop_config.json`，以及 Microsoft Store 版本自己的副本 |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code（Copilot） | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`，旧版本为 `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`，或 `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

如果 `~/.copilot` 或 VS Code 自己的设置文件夹存在，就会设置 VS Code。

有两个应用还需要多做一步：

- **Windsurf：** 重新打开后，在 Cascade 中点击刷新。
- **较旧的 VS Code 扩展中的 Cline：** 手动添加 Fontes（参见 [Cline](#其他应用)）。

### 密钥步骤

安装完成后，安装程序会立即提示您添加免费的法国和美国密钥。以后要添加或更改密钥：

- **Mac：** 双击安装程序文件夹中的 **Add or change keys.command**，或再次打开 Fontes Installer 应用并选择
  **Add or change keys**。
- **Windows：** 双击安装程序文件夹中的 **Add or change keys.cmd**。

输入内容不会显示。密钥会写入每个已安装 Fontes 的应用。之后请退出并重新打开这些应用。在哪里获取密钥以及
它们能开启什么：[KEYS.md](KEYS.md)。

### 备份、重复运行和移除

安装程序只更改 `fontes` 条目。其他所有设置和注释都保持原样。在更改某个文件之前，它会在旁边保存一份副本，
名为 `<file>.fontes-backup-<date>`。在您添加密钥之后生成的副本包含这些密钥：请删除不再需要的副本。它还会
安装 uv。再次运行是安全的：它会修复设置，不会更改其他任何内容。

要移除 Fontes，请双击 **Uninstall Fontes.command**（Mac）或 **Uninstall Fontes.cmd**（Windows）。它会从
每个应用中移除 `fontes` 条目（包括密钥）。您的其他设置和备份副本会保留。

## 更新

- **安装程序和 `.mcpb` 文件：** 您无需执行任何操作。每天一次，在应用启动时，Fontes 会在后台检查是否有
  新版本并将其准备好；应用下次启动时就会使用它。如果更新无法下载或无法正常工作，Fontes 会继续使用原先
  正常工作的版本。
- **`uvx`：** 有新版本可用时，Fontes 会在其法域列表的顶部告诉您。若要始终运行最新版本，请用
  `fontes-mcp@latest` 代替 `fontes-mcp`。

为此不会向任何地方发送有关您或您的检索的任何信息。

## 隐私

默认情况下，Fontes 不会发送任何有关您或您的检索的信息。使用计数需要您主动选择开启，错误报告只有在您
查看并确认后才会发送。详情：[PRIVACY.md](PRIVACY.md)。

## 移除

从应用的 MCP 设置中移除 `fontes` 条目（在 Claude Code 中：`claude mcp remove fontes`），然后退出并
重新打开应用。

## 须知

Fontes 读取公开来源，主要是法院和政府网站。它会在回答中标出非官方来源。依赖某一裁判文书或条文之前，
请务必打开来源链接。

如果出现问题，请将您的操作和看到的错误通过电子邮件发送至 fontesmcp@proton.me。

## 依赖之前

- Fontes 是一个研究工具，不是法律意见。使用它不会使任何人成为您的律师。
- 它按“原样”提供，不附带任何担保；在法律允许的范围内，其作者不对其使用方式承担责任。完整条款见
  [许可](../../../LICENSE)（Apache 2.0）。
