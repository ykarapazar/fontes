> 本文为机器辅助翻译，以英文版本为准。

# API 密钥

Fontes 中几乎所有来源都无需密钥即可使用。有三个需要免费密钥：

| 密钥 | 开启的内容 | 没有它时 |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | 法国：Judilibre（裁判文书）和 Légifrance（法律法规） | 法国处于关闭状态。`list_jurisdictions` 将其显示为未启用。 |
| `WLM_US_GOVINFO_KEY` | 美国：govinfo 检索（联邦法院判决意见、Statutes at Large、公法） | Fontes 使用共享的 `DEMO_KEY`：每个 IP 地址每天约 10 次检索。打开已知的裁判文书和 US Code 无需密钥。 |
| `WLM_US_COURTLISTENER_KEY` | 美国州法院（`us-states`）：来自 CourtListener 的全部 50 个州及 DC 的最高法院和上诉法院的裁判意见 | 美国州判例已关闭。`list_jurisdictions` 会将其显示为未启用。 |

密钥是可选的。您可以以后再添加。

## 添加密钥

**使用安装程序。** Fontes 设置完成后，安装程序会提示您添加密钥。在 Mac 上，点击 **添加密钥**，或点击
**完成** 跳过；在 Windows 上，回答提问（按 Enter 跳过）。以后要添加或更改密钥，请运行
**添加或更改密钥**：

- Mac：再次打开 Fontes Installer 应用并选择 **添加或更改密钥**。
- Windows：打开开始菜单，然后点击 **Fontes** → **添加或更改密钥**。

输入内容不会显示。对于每个密钥：粘贴密钥，按 Enter 保留现有值，或输入 `-` 将其删除。密钥会写入每个已安装
Fontes 的应用。

**使用 Claude Desktop 扩展（.mcpb）。** 打开 Claude > Settings > Extensions > Fontes 并填写字段。所有字段
都是可选的。

**手动设置。** 将这些变量添加到您应用的 MCP 配置中 `fontes` 条目的 `env` 块：

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

任何更改之后都请重新启动应用。

## 法国：PISTE（免费）

1. 在 [piste.gouv.fr](https://piste.gouv.fr) 创建账户。这意味着接受 PISTE 条款（CGU）。
2. 前往 API > **Consentement CGU API**。接受 **JUDILIBRE** 和 **Légifrance**（生产环境）的条款。
3. 创建一个**生产环境应用**。系统为您创建的 `APP_SANDBOX` 无法访问生产环境。
   在“Modifier l'application”下，勾选 **JUDILIBRE (production)** 和 **Légifrance (production)**，然后应用。
4. 打开该应用的 **Authentification** 选项卡。复制 `client_id` 和 `client_secret`。
5. 运行 **Add or change keys** 并粘贴它们。

条款要点：

- 数据：Licence Ouverte / Etalab 2.0。允许再利用，包括商业再利用，但须署名。
- 请勿公开或分享您的凭据。如果凭据泄露，请告知 PISTE。
- Légifrance API 是测试版服务。它可能被暂停，并且有配额（每秒、每分钟和每天）。
- Légifrance 的文本不是具有权威效力的版本。只有经签署的 Journal officiel PDF 才是。
- Judilibre：请勿使用法官或书记员的姓名来评估、比较或预测其工作
  （Code de l'organisation judiciaire 第 L111-13 条；属于刑事犯罪）。
- Judilibre：遵守 GDPR。请勿尝试重新识别当事人。

您的配额可在 PISTE 的 API Sélectionnées > Actions > Consulter les quotas 下查看。

## 美国：api.data.gov（免费）

1. 前往 [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup)（密钥显示在屏幕上）
   或 [api.data.gov/signup](https://api.data.gov/signup/)（密钥通过电子邮件发送给您）。
2. 输入您的姓名和电子邮件地址。“how will you use it”字段是可选的。
3. 复制这个 40 个字符的密钥。
4. 运行 **Add or change keys** 并将其粘贴为美国密钥。

条款要点：

- 使用您自己的密钥时，govinfo 每小时最多允许 36,000 次请求。
- 我们没有找到专门针对该 API 的服务条款（api.data.gov/terms/ 不存在）。未经核实。
  参见 [govinfo 的政策](https://www.govinfo.gov/about/policies) 和
  [data.gov 隐私政策](https://data.gov/privacy-policy/)。
- 请勿将密钥告诉他人。

## 美国州法院：CourtListener（免费）

CourtListener 由 [Free Law Project](https://free.law) 运营，这是一家非营利组织，自 2010 年起收集美国法院的裁判意见，并向所有人免费开放。按其自身的统计，它收录了超过九百万份裁判。它不是官方来源：各法院自行发布裁判意见，CourtListener 从法院网站和扫描的判例汇编中收集它们。Fontes 来自它的每一条回答都会说明这一点。Fontes 与 Free Law Project 没有任何隶属关系。

1. 在 [courtlistener.com](https://www.courtlistener.com/sign-in/) 创建一个免费账户。
2. 打开您的个人资料，复制您的 API 令牌。
3. 运行 **Add or change keys**，将其粘贴为 CourtListener 密钥。

条款要点（[完整条款](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)）：

- 令牌仅供您本人使用：请勿分享、合并或转售，也不要使用多个账户。
- 您需对 AI 应用使用您的令牌所做的一切负责。
- 请勿将 AI 对其数据的分析表述为由 Free Law Project 制作、认可或核查。
- 免费账户每分钟允许 5 次请求，每小时 50 次，每天 125 次。一次检索算一次请求；打开一份裁判算两次。成为 Free Law Project 会员可提高这些限额。
- CourtListener 不保证准确性。在依赖某份裁判意见之前，请对照法院的原件核对。

## 密钥保存在哪里

- **安装程序或手动设置：** 以明文形式保存在每个应用的 MCP 配置文件中，位于 `fontes` 条目的 `env` 块内。
  任何能够读取您的用户文件的人都能读取这些密钥。
  - Claude Desktop：`~/Library/Application Support/Claude/claude_desktop_config.json`（Mac），
    `%APPDATA%\Claude\claude_desktop_config.json`（Windows）
  - Claude Code：`~/.claude.json`
  - Codex：`~/.codex/config.toml`
  - Cursor：`~/.cursor/mcp.json`
  - VS Code（Copilot）：`~/.copilot/mcp-config.json`
  - Windsurf：`~/.config/devin/mcp_config.json` 或 `~/.codeium/windsurf/mcp_config.json`
    （Windows：`%APPDATA%\devin\mcp_config.json`）
  - Gemini CLI：`~/.gemini/settings.json`
  - Zed：`~/.config/zed/settings.json`（Windows：`%APPDATA%\Zed\settings.json`）
  - LM Studio：`~/.lmstudio/mcp.json`
  - Cline：`~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop 扩展（.mcpb）：** Claude 将这些字段保存在其设置中，并使用您系统的安全存储加以保护
  （Mac 上为钥匙串，Windows 上为凭据管理器）。

每次更改之前，安装程序都会在配置文件旁边保存一份副本（`<file>.fontes-backup-<time>`）。在您添加密钥之后
生成的副本也包含密钥。请删除您不需要的旧副本。

## 更改或删除密钥

- 运行 **Add or change keys**。粘贴新密钥以替换旧密钥，或输入 `-` 将其删除。
- 或者手动编辑 `env` 块，然后重新启动应用。
- 卸载 Fontes 会删除其整个条目，包括密钥。它不会删除备份副本。
- 如果密钥泄露，还要在来源处更换：在 PISTE 上，为您的应用生成新的凭据；对于 api.data.gov，重新注册
  一个新密钥。

## 您可能看到的消息

| 消息 | 含义 |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | 没有法国密钥。请添加一个。 |
| `Inactive: needs a free PISTE account. ...`（在 `list_jurisdictions` 中） | 同上。 |
| `PISTE refused the client credentials ...` | ID 或密钥有误或已失效。请从 Authentification 选项卡重新复制两者。 |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | 您的应用未订阅该 API，或您尚未接受其条款。参见第 2 步和第 3 步。 |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | 没有美国密钥。每天可进行少量检索。 |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | 演示密钥的额度已用完。请添加您自己的密钥。 |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | 密钥有误，或尚未通过电子邮件确认。 |

空值视为没有密钥。

## 许可（WLM_PERMITTED）

这不是 API 密钥，安装程序也不会设置它。**只有在您本人持有该许可时才可设置。**

有些来源默认关闭，因为其条款或 robots.txt 禁止未经许可的自动使用。如果您已获得发布者的许可，可将该来源的
代码以逗号分隔添加到 `env` 块中的 `WLM_PERMITTED`，以开启该来源：`"WLM_PERMITTED": "in,de"`。

| 代码 | 来源 |
|---|---|
| `az` | 阿塞拜疆：e-qanun.az（司法部） |
| `bh` | 巴林：立法和法律意见委员会（lloc.gov.bh） |
| `co` | 哥伦比亚：Función Pública，Gestor Normativo（现行整合法律法规） |
| `de` | 德国：NeuRIS（联邦法律信息门户，试运行服务） |
| `difc` | 迪拜国际金融中心法院（difccourts.ae） |
| `gr` | 希腊：国家印刷局，政府公报检索（search.et.gr） |
| `mu` | 毛里求斯：最高法院（supremecourt.govmu.org） |
| `sg` | 新加坡：法院判决（elitigation.sg） |

没有许可时，Fontes 会显示：`Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
