> 本文为机器辅助翻译，以英文版本为准。

# Fontes：问答

## Fontes 是什么？

一个免费、开源的 MCP 服务器（Apache 2.0）。它让任何支持 Model Context Protocol 的应用（Claude、Codex、
Cursor、VS Code、Gemini CLI 等）在法院和政府网站上实时检索裁判文书和法律法规，覆盖 120 多个法域和国际
法院（124 个适配器）。每条结果都注明其来源，并附有原文链接。

## 这些文本是官方的吗？

大多数是，但并非全部。

- 大多数来源由法院、政府部门或官方公报运营。
- 有些现行整合文本由政府发布，但明确声明为非官方版本：只有官方公报具有权威效力。
- 少数来源根本不是政府网站（例如 LexiVox、LawPhil、Maqam、Wikisource）。

对于来自这些来源的每个回答，Fontes 都会加上“非官方来源”提示。引用任何内容之前，请核对官方公布文本。
[README](README.md#覆盖范围) 中的覆盖范围表和 `list_jurisdictions` 会列出每个法域的来源。

## 它覆盖哪些法域，覆盖程度如何？

124 个适配器：108 个联合国会员国、香港、科索沃、巴勒斯坦、台湾、DIFC 法院，以及 11 个国际法院和机构
（例如欧洲人权法院、欧盟、国际法院和世界贸易组织）。

覆盖程度差异很大。按照严格的标准（完整获取最高普通法院的判例，或完整获取宪法和基本法律），124 个中有
72 个算作已覆盖。[COVERAGE.md](../../COVERAGE.md) 列出了每个法域中 Fontes 能获取什么、不能获取什么，
以及原因。

## 我需要 API 密钥吗？

对于几乎所有法域，不需要。有些来源需要免费密钥：参见 [KEYS.md](KEYS.md)。

- **法国：** 需要。在您设置 `WLM_FR_PISTE_CLIENT_ID` 和 `WLM_FR_PISTE_CLIENT_SECRET` 之前，法国处于
  关闭状态。这些密钥来自一个免费的 PISTE 账户（piste.gouv.fr），其中需有一个订阅了 Judilibre 和
  Légifrance 的应用。
- **美国：** 可选。判例检索无需密钥即可使用，但共享的演示密钥每个 IP 地址每天只允许约 10 次检索。将免费的
  api.data.gov 密钥设置在 `WLM_US_GOVINFO_KEY` 中可提高这一限额。

请在您应用的 MCP 设置中将这些设置为 Fontes 服务器的环境变量。安装程序推出后，它会在安装完成后询问这些
密钥，以后也可以通过其 **Add or change keys** 启动器进行更改。

另外，少数来源在其条款中规定，自动访问需要发布者的许可。它们标为 OFF 并保持关闭。密钥不会改变这一点；
只有发布者的许可才能改变（届时设置 `WLM_PERMITTED=<codes>`）。

## 什么内容会离开我的电脑？

您的检索只会发往被检索的来源。Fontes 不保存数据库，也无需账户。

除这些来源外，Fontes 每天会询问 PyPI 一次是否有新版本（可用 `FONTES_NO_UPDATE_CHECK=1` 关闭）。除非您
开启，否则使用计数处于关闭状态；错误报告只有在您查看并确认后才会发送。您的 AI 应用按其自己的条款查看
您的对话。

完整详情：[PRIVACY.md](PRIVACY.md)。

## 这是法律意见吗？

不是。Fontes 是一个研究工具。它查找文本；它不会告诉您这些文本对您的案件意味着什么，使用它也不会与任何人
建立律师–委托人关系。AI 应用可能误读文本，因此依赖之前请阅读裁判文书或条文的全文。如需意见，请咨询在您的
问题所涉地具有执业资格的律师。

## 由谁维护？它会一直可用吗？

一个人：Yüce Karapazar。Fontes 背后没有公司，没有支持合同，也没有服务水平承诺。不提供任何法律服务。

各来源每天检查一次，结果发布在[状态页面](https://ykarapazar.github.io/fontes/status/)上。法院和政府网站会
在不通知的情况下变更，因此某个来源随时可能失效。不保证任何来源或 Fontes 本身会一直可用。Fontes 按“原样”
提供，不附带任何担保（[LICENSE](../../../LICENSE) 第 7 条和第 8 条）。

## 某个文本有误、已过时，或某个来源失效。如何报告？

- 使用“Broken or wrong source”表单提交问题：
  <https://github.com/ykarapazar/fontes/issues/new/choose>。请说明是哪个法域、您问了什么、您得到了什么，
  以及显示正确文本的官方页面。
- 或者让您的 AI 应用“报告 Fontes 的错误”（或运行 `fontes report-bug`）。在发送任何内容之前，您会先看到
  报告。
- 或者发送电子邮件至 fontesmcp@proton.me。

请勿在报告中包含客户的详细信息或保密事实。

**如果您运营其中某个来源**，而有任何错误（您的条款、您的 robots.txt、您的速率限制），请发送电子邮件至
fontesmcp@proton.me。该来源将被更正或关闭。

## Fontes 与托管式法律研究工具有何不同？

- **它在您的电脑上运行。** 没有 Fontes 服务器，也没有账户。这也意味着它只能在能够启动本地 MCP 服务器的
  应用中使用（Claude Desktop、Codex、Cursor、VS Code 等），而不能在只接受托管连接器的纯网页应用中使用。
- **它没有数据库。** 每次检索都实时发往发布者自己的网站或 API，因此结果与来源同样新，检索质量也取决于
  来源本身。没有基于精选索引的语义检索。
- **它不设使用上限。** Fontes 没有每月调用次数上限。它会为发往每个网站的请求设置间隔，而有些来源会限制
  查询的速度或频率。
- **它是开源的。** 您可以阅读每个适配器，确切了解每个文本来自何处。
- **它背后没有供应商。** 没有合同、支持服务台或正常运行时间承诺（参见“由谁维护？”）。

## 它适用于哪些应用和系统？

任何能够运行本地（stdio）服务器的 MCP 应用，例如 Claude Desktop、Claude Code、Codex、Cursor、
VS Code（GitHub Copilot）、Gemini CLI、Windsurf、Zed、LM Studio 和 Cline。Fontes 可在 macOS、Windows 和
Linux 上运行，凡是 uv 能运行的地方都可以（Python 3.13+）。在 Mac 上，一键安装程序会一次性设置
Claude Desktop、Codex、Claude Code、Cursor、VS Code、Windsurf、Gemini CLI、Zed、LM Studio 和 Cline；
Windows 安装程序即将推出。各应用的步骤：[INSTALL.md](INSTALL.md)。

## 我可以贡献代码吗？

目前不可以。欢迎提交问题、来源报告和法域请求。参见 [CONTRIBUTING.md](../../../CONTRIBUTING.md)。
