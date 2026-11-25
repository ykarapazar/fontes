> 這係機器輔助个翻譯，以英文版本為準。

# Fontes：問同答

## Fontes 係麼个？

免費、開放原始碼个 MCP 伺服器（Apache 2.0）。佢分任何支援 Model Context Protocol 个應用程式（Claude、
Codex、Cursor、VS Code、Gemini CLI 等等）在法院同政府个網站頂即時檢索法院裁判同法規，涵蓋 120 過个法域
同國際法院（124 个轉接器）。每一筆結果都寫明佢个來源，附原文个連結。

## 這兜文本係官方个無？

大部分係，毋過毋係全部。

- 大部分个來源係由法院、政府部會或者官方公報營運个。
- 有兜經過整合个現行條文係政府發布个，毋過明確聲明係非官方版本：單淨官方公報有正本效力。
- 少數來源根本毋係政府个網站（例如 LexiVox、LawPhil、Maqam、Wikisource）。

對來自這兜來源个每一个回答，Fontes 都會加「非官方來源」个提示。引用任何內容以前，請核對官方公布个版本。
[README](README.md#涵蓋範圍) 肚項个涵蓋範圍表同 `list_jurisdictions` 會列出每一个法域个來源。

## 佢涵蓋哪兜法域，涵蓋到麼个程度？

124 个轉接器：108 个聯合國會員國、香港、科索沃、巴勒斯坦、台灣、DIFC 法院，同 11 个國際法院同機構
（例如歐洲人權法院、歐盟、國際法院同世界貿易組織）。

涵蓋个程度差當多。照嚴格个標準（完整拿得著最高普通法院个判決先例，或者完整拿得著憲法同基本法律），
124 个肚項有 72 个算係已經涵蓋。[COVERAGE.md](../../COVERAGE.md) 列出每一个法域 Fontes 拿得著麼个、
拿毋著麼个，同原因。

## 𠊎需要 API 金鑰無？

幾乎所有个法域都毋使。有兜來源需要免費个金鑰：請看 [KEYS.md](KEYS.md)。

- **法國：** 需要。在你設定 `WLM_FR_PISTE_CLIENT_ID` 同 `WLM_FR_PISTE_CLIENT_SECRET` 以前，法國係關忒个。
  這兜金鑰來自免費个 PISTE 帳號（piste.gouv.fr），肚項愛有一个已經訂閱 Judilibre 同 Légifrance 个
  應用程式。
- **美國：** 選用。裁判檢索無金鑰也做得用，毋過共用个示範金鑰每一个 IP 位址逐日單淨允許大約 10 擺檢索。
  將免費个 api.data.gov 金鑰設定在 `WLM_US_GOVINFO_KEY` 肚項，做得提高這个限額。

請在你應用程式个 MCP 設定肚項，將這兜設定做 Fontes 伺服器个環境變數。安裝程式會在安裝好个時節
問你這兜金鑰，以後也做得透過佢个 **Add or change keys** 啟動器來改。

另外，少數來源在佢兜个條款肚項規定，自動化存取愛有發布者个許可。佢兜標做 OFF，一直保持關忒。金鑰改變毋得
這點；單淨發布者个許可做得改變（該時節設定 `WLM_PERMITTED=<codes>`）。

## 哪兜東西會離開𠊎个電腦？

你个檢索單淨會送到當在檢索个來源。Fontes 毋會建資料庫，也毋使帳號。

除忒這兜來源以外，Fontes 逐日會問 PyPI 一擺有無新个版本（做得用 `FONTES_NO_UPDATE_CHECK=1` 關忒）。除非你
打開，無就使用次數統計係關忒个；錯誤回報單淨在你看過、確認以後正會送出去。你个 AI 應用程式照佢自家个條款
看著你个對話。

完整个細節：[PRIVACY.md](PRIVACY.md)。

## 這係法律意見無？

毋係。Fontes 係研究工具。佢尋文本；佢毋會同你講這兜文本對你个案件有麼个意義，用佢也毋會同任何人成立律師
同當事人个委任關係。AI 應用程式可能讀毋著文本，所以愛靠以前請讀裁判或者條文个全文。若係需要意見，請問在你
問題發生个所在有執業資格个律師。

## 麼人在維護？佢會一直做得用無？

一个人：Yüce Karapazar。Fontes 後背無公司，無支援合約，也無服務水準个承諾。無提供任何法律服務。

每一个來源逐日檢查一擺，結果公布在[狀態頁面](https://ykarapazar.github.io/fontes/status/)頂高。法院同政府个
網站會無通知就改變，所以某一个來源隨時都可能壞忒。毋保證任何來源或者 Fontes 本身會一直做得用。Fontes 照
「現狀」提供，無附任何擔保（[LICENSE](../../../LICENSE) 第 7 條同第 8 條）。

## 某一个文本有錯、過時，或者某一个來源壞忒。愛仰般回報？

- 用「Broken or wrong source」表單提出 issue：
  <https://github.com/ykarapazar/fontes/issues/new/choose>。請講明係哪一个法域、你問麼个、你得著麼个，
  同顯示正確文本个官方頁面。
- 或者請你个 AI 應用程式「回報 Fontes 个錯誤」（或者執行 `fontes report-bug`）。在傳送任何東西以前，你會
  先看著回報。
- 或者寄電子郵件到 fontesmcp@proton.me。

請毋好在回報肚項包含當事人个詳細資料或者機密个事實。

**若係你營運其中一个來源**，而且有任何毋著（你个條款、你个 robots.txt、你个速率限制），請寄電子郵件到
fontesmcp@proton.me。該來源會改正或者關忒。

## Fontes 同雲端託管个法律研究工具有麼个無共樣？

- **佢在你个電腦頂執行。** 無 Fontes 伺服器，也無帳號。這也係講佢單淨做得在能啟動本機 MCP 伺服器个應用程式
  肚項用（Claude Desktop、Codex、Cursor、VS Code 等等），毋做得在單淨接受託管連接器个純網頁應用程式肚項用。
- **佢無資料庫。** 每一擺檢索都即時送到發布者自家个網站或者 API，所以結果同來源共樣新，檢索个品質也看來源
  本身。無根據精選索引个語意檢索。
- **佢無設使用上限。** Fontes 無每月个呼叫次數上限。佢會為送到每一个網站个請求設定間隔，而且有兜來源會限制
  查詢个速度或者次數。
- **佢係開放原始碼。** 你做得讀每一个轉接器，準確知每一个文本對哪位來。
- **佢後背無廠商。** 無合約、支援服務台或者正常運作時間个承諾（請看「麼人在維護？」）。

## 佢做得在哪兜應用程式同系統頂用？

任何做得執行本機（stdio）伺服器个 MCP 應用程式，例如 Claude Desktop、Claude Code、Codex、Cursor、
VS Code（GitHub Copilot）、Gemini CLI、Windsurf、Zed、LM Studio 同 Cline。Fontes 做得在 macOS、Windows 同
Linux 頂執行，凡係 uv 做得執行个所在都做得（Python 3.13+）。在 Mac 或者 Windows 電腦頂，一鍵安裝程式
會一擺設定好 Claude Desktop、Codex、Claude Code、Cursor、VS Code、Windsurf、Gemini CLI、Zed、
LM Studio 同 Cline。每一个應用程式个步驟：[INSTALL.md](INSTALL.md)。

## 𠊎做得貢獻程式碼無？

這下還毋做得。歡迎提出 issue、來源回報同法域个需求。請看 [CONTRIBUTING.md](../../../CONTRIBUTING.md)。
