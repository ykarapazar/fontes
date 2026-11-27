> 本文為機器輔助翻譯，以英文版本為準。

# Fontes：問與答

## Fontes 是什麼？

免費、開放原始碼的 MCP 伺服器（Apache 2.0）。它讓任何支援 Model Context Protocol 的應用程式（Claude、Codex、
Cursor、VS Code、Gemini CLI 等）在法院與政府網站上即時檢索法院裁判與法規，涵蓋 120 多個法域及國際法院
（125 個轉接器）。每筆結果都註明其來源，並附有原文連結。

## 這些文本是官方的嗎？

大多數是，但並非全部。

- 大多數來源由法院、政府部會或官方公報營運。
- 有些經整合之現行條文由政府發布，但明確聲明為非官方版本：只有官方公報具正本效力。
- 少數來源根本不是政府網站（例如 LexiVox、LawPhil、Maqam、Wikisource）。

對於來自這些來源的每個回答，Fontes 都會加上「非官方來源」提示。引用任何內容之前，請核對官方公布版本。
[README](README.md#涵蓋範圍) 中的涵蓋範圍表與 `list_jurisdictions` 會列出每個法域的來源。

## 它涵蓋哪些法域，涵蓋程度如何？

125 個轉接器：108 個聯合國會員國、香港、科索沃、巴勒斯坦、台灣、DIFC 法院、美國各州法院，以及 11 個國際法院與機構
（例如歐洲人權法院、歐盟、國際法院與世界貿易組織）。

涵蓋程度差異很大。依照嚴格的標準（完整取得最高普通法院的判決先例，或完整取得憲法與基本法律），125 個中有
72 個算是已涵蓋。[COVERAGE.md](../../COVERAGE.md) 列出每個法域中 Fontes 能取得什麼、不能取得什麼，以及原因。

## 我需要 API 金鑰嗎？

幾乎所有法域都不需要。部分來源需要免費金鑰：請參閱 [KEYS.md](KEYS.md)。

- **法國：** 需要。在您設定 `WLM_FR_PISTE_CLIENT_ID` 與 `WLM_FR_PISTE_CLIENT_SECRET` 之前，法國處於關閉
  狀態。這些金鑰來自免費的 PISTE 帳號（piste.gouv.fr），其中須有一個已訂閱 Judilibre 與 Légifrance 的
  應用程式。
- **美國：** 選用。裁判檢索不需要金鑰即可使用，但共用的示範金鑰每個 IP 位址每天只允許約 10 次檢索。將免費的
  api.data.gov 金鑰設定在 `WLM_US_GOVINFO_KEY` 中可提高此限額。
- **美國州法院：** 需要。在您將 `WLM_US_COURTLISTENER_KEY` 設定為您自己的免費 CourtListener API 權杖之前，州判例（`us-states`）處於關閉狀態。CourtListener 由非營利組織 Free Law Project 營運；它不是官方來源，每則回答都會說明這一點。

請在您應用程式的 MCP 設定中，將這些設定為 Fontes 伺服器的環境變數。安裝程式會在安裝完成後詢問這些
金鑰，日後也可以透過其 **Add or change keys** 啟動器變更。

另外，少數來源在其條款中規定，自動化存取須取得發布者的許可。它們標示為 OFF 並維持關閉。金鑰不會改變這一點；
只有發布者的許可才能改變（屆時設定 `WLM_PERMITTED=<codes>`）。

## 哪些內容會離開我的電腦？

您的檢索只會傳送到正在檢索的來源。Fontes 不建立資料庫，也不需要帳號。

除了這些來源之外，Fontes 每天會詢問 PyPI 一次是否有新版本（可用 `FONTES_NO_UPDATE_CHECK=1` 關閉）。除非您
開啟，否則使用次數統計處於關閉狀態；錯誤回報只有在您看過並確認後才會傳送。您的 AI 應用程式依其本身的條款
看到您的對話。

完整細節：[PRIVACY.md](PRIVACY.md)。

## 這是法律意見嗎？

不是。Fontes 是研究工具。它查找文本；它不會告訴您這些文本對您的案件有何意義，使用它也不會與任何人成立律師與
當事人間的委任關係。AI 應用程式可能誤讀文本，因此依賴之前請閱讀裁判或條文的全文。如需意見，請諮詢在您的
問題所在地具執業資格的律師。

## 由誰維護？它會一直可用嗎？

一個人：Yüce Karapazar。Fontes 背後沒有公司，沒有支援合約，也沒有服務水準承諾。不提供任何法律服務。

各來源每天檢查一次，結果公布在[狀態頁面](https://ykarapazar.github.io/fontes/status/)上。法院與政府網站會在
未經通知的情況下變更，因此某個來源隨時可能失效。不保證任何來源或 Fontes 本身會一直可用。Fontes 依「現狀」
提供，不附帶任何擔保（[LICENSE](../../../LICENSE) 第 7 條及第 8 條）。

## 某個文本有誤、已過時，或某個來源失效。要如何回報？

- 使用「Broken or wrong source」表單提出 issue：
  <https://github.com/ykarapazar/fontes/issues/new/choose>。請說明是哪個法域、您問了什麼、您得到什麼，
  以及顯示正確文本的官方頁面。
- 或請您的 AI 應用程式「回報 Fontes 的錯誤」（或執行 `fontes report-bug`）。在傳送任何內容之前，您會先看到
  回報。
- 或寄電子郵件至 fontesmcp@proton.me。

請勿在回報中包含當事人的詳細資料或機密事實。

**如果您營運其中某個來源**，而有任何錯誤（您的條款、您的 robots.txt、您的速率限制），請寄電子郵件至
fontesmcp@proton.me。該來源將被修正或關閉。

## Fontes 與雲端託管的法律研究工具有何不同？

- **它在您的電腦上執行。** 沒有 Fontes 伺服器，也沒有帳號。這也表示它只能在能啟動本機 MCP 伺服器的應用程式中
  使用（Claude Desktop、Codex、Cursor、VS Code 等），而不能在只接受託管連接器的純網頁應用程式中使用。
- **它沒有資料庫。** 每次檢索都即時傳送到發布者自己的網站或 API，因此結果與來源一樣新，檢索品質也取決於
  來源本身。沒有基於精選索引的語意檢索。
- **它不設使用上限。** Fontes 沒有每月呼叫次數上限。它會為傳送到每個網站的請求設定間隔，而有些來源會限制
  查詢的速度或頻率。
- **它是開放原始碼。** 您可以閱讀每個轉接器，確切了解每個文本來自何處。
- **它背後沒有廠商。** 沒有合約、支援服務台或正常運作時間承諾（請參閱「由誰維護？」）。

## 它適用於哪些應用程式與系統？

任何能執行本機（stdio）伺服器的 MCP 應用程式，例如 Claude Desktop、Claude Code、Codex、Cursor、
VS Code（GitHub Copilot）、Gemini CLI、Windsurf、Zed、LM Studio 與 Cline。Fontes 可在 macOS、Windows 與
Linux 上執行，凡是 uv 能執行的地方都可以（Python 3.13+）。在 Mac 或 Windows PC 上，一鍵安裝程式可一次設定
Claude Desktop、Codex、Claude Code、Cursor、VS Code、Windsurf、Gemini CLI、Zed、LM Studio 與 Cline。各應用程式的步驟：[INSTALL.md](INSTALL.md)。

## 我可以貢獻程式碼嗎？

目前不行。歡迎提出 issue、來源回報與法域需求。請參閱 [CONTRIBUTING.md](../../../CONTRIBUTING.md)。
