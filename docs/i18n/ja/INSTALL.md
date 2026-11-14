> これは機械支援による翻訳です。英語版が正本です。

# Fontes のインストール

Fontes を使うと、AI アプリが 120 以上の法域について、裁判所や政府のウェブサイトから裁判例と法令を
リアルタイムで調べられます。すべての結果に原文へのリンクが付きます。標準的な MCP サーバーなので、
ローカルの MCP サーバーを実行できるアプリならどれでも動作します: Claude Desktop、Codex、Claude Code、
Cursor、VS Code（GitHub Copilot）、Gemini CLI、Windsurf、Zed、LM Studio、Cline など。

お使いのアプリを選んで手順に従い、[動作を確認](#動作の確認)してください。

## Claude Desktop

1. [最新リリース](https://github.com/ykarapazar/fontes/releases/latest)から Fontes の `.mcpb`
   ファイルをダウンロードします。
2. ダブルクリックします。Claude Desktop がファイルを開きます。
3. **Install** をクリックします。

## Codex

ターミナルで:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI と Codex の IDE 拡張機能は、この設定（`~/.codex/config.toml`）を共有します。
[uv が必要です](#uv-が必要です)。

## Claude Code

ターミナルで:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

[uv が必要です](#uv-が必要です)。

## その他のアプリ

いずれも [uv が必要です](#uv-が必要です)。エントリーを追加して保存し、アプリを終了してもう一度開きます。

**Cursor:** `~/.cursor/mcp.json`（すべてのプロジェクト）または `.cursor/mcp.json`（1 つのプロジェクト）に:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code（GitHub Copilot）:** コマンドパレットから **MCP: Add Server** を実行し、**Command (stdio)** を
選んで `uvx fontes-mcp` と入力し、サーバー名を `fontes` にします。または、`~/.copilot/mcp-config.json` に
次を追加します:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

古い VS Code の構成では `.vscode/mcp.json` を使い、最上位のキーは `mcpServers` ではなく `servers` です。

**Gemini CLI:** ターミナルで `gemini mcp add -s user fontes uvx fontes-mcp`。または、
`~/.gemini/settings.json` に次を追加します:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** 設定ファイルを開き（**zed: open settings file**）、次を追加します:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** 右側のサイドバーで **Program** タブを開き、**Install → Edit mcp.json** をクリックして、
次を追加します:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** アイコンをクリックし、**Configure** タブを開いて **Configure MCP Servers** を
クリックし、LM Studio と同じ `mcpServers` エントリーを追加します。

**Claude Desktop（手動）**（`.mcpb` ファイルの代わりに）: 同じ `mcpServers` エントリーを
`claude_desktop_config.json`（macOS: `~/Library/Application Support/Claude/`、Windows:
`%APPDATA%\Claude\`）に追加します。

**その他の MCP アプリ**（Windsurf など）: MCP サーバーの設定場所は、そのアプリのドキュメントに
記載されています。ほとんどは同じエントリー（コマンド `uvx`、引数 `fontes`）で動作します。

アプリが `uvx` を見つけられない場合は、フルパスを使ってください（macOS と Linux では `which uvx` で
表示されます）。

## uv が必要です

Codex、Claude Code、その他のアプリは `uvx` で Fontes を起動します。`uvx` は Astral の小さな無料ツール
**uv** に含まれています。インストールするには [Astral のガイド](https://docs.astral.sh/uv/getting-started/installation/)
を参照するか、次を実行します:

- macOS または Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows（PowerShell）: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## キー

一部の情報源には無料のキーが必要です: [KEYS.md](KEYS.md) をご覧ください。

## 動作の確認

新しいチャットで *「Fontes はどの法域を検索できますか？」* と質問してください。アプリが国の一覧で
答えるはずです。そうならない場合は、アプリをもう一度終了して開き直してください。

## ワンクリックインストーラー（Mac）

Mac 用インストーラーは、すべてのアプリに一度に Fontes を設定します: Claude Desktop、Codex、
Claude Code、Cursor、VS Code（GitHub Copilot）、Windsurf、Gemini CLI、Zed、LM Studio、Cline。Windows 用
インストーラーは準備中です。それまでは、上にあるお使いのアプリ用の手順を使ってください。

**始める前に:** これらのアプリをすべて完全に終了してください。特に Claude Code が重要です。実行中は
`~/.claude.json` を書き換えるため、インストーラーの変更が元に戻ることがあります。Claude Code を終了
できない場合は、代わりに `claude mcp add` で Fontes を追加してください（[Claude Code](#claude-code) を参照）。

**Mac**

1. [最新リリース](https://github.com/ykarapazar/fontes/releases/latest)から Mac 用インストーラー
   （`Fontes-Installer-…-mac.zip`）をダウンロードし、ダブルクリックして展開します。
2. **Fontes Installer** をダブルクリックします。インターネットからダウンロードしたアプリを開くかどうか
   Mac に尋ねられたら、**開く** をクリックします。
3. **インストール** を選び、**OK** をクリックします。設定には 1 分ほどかかります。
4. 設定したアプリの一覧がメッセージで表示されます。**完了** をクリックし、それらのアプリをもう一度
   開きます。先に任意の無料キーを追加するには、代わりに **キーを追加** をクリックします。
   [キーの手順](#キーの手順)をご覧ください。

**Windows**（Windows 用インストーラーの公開後）

1. ダウンロードした **Fontes Installer** を展開します（右クリック → **すべて展開**）。
2. **Install Fontes.cmd** をダブルクリックします。
   - 「Windows によって PC が保護されました」と表示された場合: **詳細情報** をクリックし、
     **実行** をクリックします。
3. 匿名の利用回数を送信するかどうかを尋ねられたら、送信しない場合は Enter を押します。
4. 今すぐキーを追加するかどうかを尋ねます。スキップするには Enter を押します。
   [キーの手順](#キーの手順)をご覧ください。
5. **Done** と表示されたら、AI アプリをもう一度開きます。実行中のままのアプリがあった場合は、
   （時計の近くのシステムトレイからも）完全に終了してから、もう一度開きます。

最後に、インストーラーが設定したアプリの一覧を表示します。

### 設定されるアプリ

アプリの設定フォルダーがすでにコンピューター上にある場合にのみ、そのアプリを設定します。Claude Code は
`~/.claude.json` がある場合にのみ設定されます。Claude Desktop は常に設定されます。各アプリには、次の
ファイルに `fontes` というエントリーが 1 つ追加されます:

| アプリ | ファイル（Mac と Linux） | ファイル（Windows） |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json`（Linux: `~/.config/Claude/`） | `%APPDATA%\Claude\claude_desktop_config.json` と、Microsoft Store 版の独自のコピー |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code（Copilot） | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`、古いバージョンでは `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`、または `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code は、`~/.copilot` または VS Code 自体の設定フォルダーがある場合に設定されます。

2 つのアプリでは、もう 1 つ手順が必要です:

- **Windsurf:** 開き直した後、Cascade で更新ボタンを押します。
- **古い VS Code 拡張機能内の Cline:** Fontes を手動で追加します（[Cline](#その他のアプリ) を参照）。

### キーの手順

インストールの直後に、インストーラーがフランスと米国の無料キーの追加を提案します。後で追加または変更する
には:

- **Mac:** **Fontes Installer** をもう一度開き、**キーを追加・変更** を選びます。
- **Windows:** インストーラーフォルダー内の **Add or change keys.cmd** をダブルクリックします。

入力内容は表示されません。キーは、Fontes がすでに設定されているすべてのアプリに書き込まれます。その後、
アプリを終了して開き直してください。キーの入手先と、キーで使えるようになるもの: [KEYS.md](KEYS.md)。

### バックアップ、再実行、削除

インストーラーが変更するのは `fontes` エントリーだけです。その他の設定やコメントはそのまま残ります。
ファイルを変更する前に、`<file>.fontes-backup-<date>` という名前のコピーを隣に保存します。キーを追加した
後に作られたコピーにはそのキーが含まれるので、不要になったものは削除してください。uv もインストール
します。再実行しても問題ありません。設定を修復するだけで、ほかには何も変更しません。

Fontes を削除するには、**Fontes Installer** を開いて **削除** を選ぶ（Mac）か、
**Uninstall Fontes.cmd** をダブルクリックします（Windows）。すべてのアプリから `fontes` エントリーを
キーごと削除します。その他の設定とバックアップのコピーは残ります。

## アップデート

- **インストーラーと `.mcpb` ファイル:** 何もする必要はありません。1 日 1 回、アプリの起動時に Fontes が
  バックグラウンドで新しいバージョンを確認して準備し、次にアプリを起動したときにそれを使います。
  アップデートをダウンロードできない場合や動作しない場合は、動作していたバージョンを使い続けます。
- **`uvx`:** 新しいバージョンがあると、Fontes が法域一覧の先頭でお知らせします。常に最新バージョンを
  実行するには、`fontes-mcp` の代わりに `fontes-mcp@latest` を使ってください。

このために、あなたや検索内容に関する情報がどこかに送信されることはありません。

## プライバシー

Fontes は、デフォルトではあなたや検索内容について何も送信しません。利用回数はオプトインで、バグ報告は
内容を確認して同意した後にのみ送信されます。詳細: [PRIVACY.md](PRIVACY.md)。

## 削除

アプリの MCP 設定から `fontes` エントリーを削除し（Claude Code では `claude mcp remove fontes`）、
アプリを終了して開き直します。

## 知っておくと良いこと

Fontes は公開されている情報源、主に裁判所や政府のウェブサイトを読みます。非公式の情報源には回答の中で
注記を付けます。裁判例や条文に依拠する前に、必ず情報源のリンクを開いてください。

問題が起きた場合は、行った操作と表示されたエラーを fontesmcp@proton.me までメールしてください。

## 依拠する前に

- Fontes は調査ツールであり、法的助言ではありません。利用しても、誰かがあなたの弁護士になるわけでは
  ありません。
- 「現状のまま」提供され、いかなる保証もなく、法律で認められる範囲で、作者はその利用について責任を
  負いません。条件の全文は[ライセンス](../../../LICENSE)（Apache 2.0）にあります。
