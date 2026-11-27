> 這是機器輔助的翻譯，以英文版本為準。

# Fontes：問佮答

## Fontes 是啥物？

免費、開放原始碼的 MCP 伺服器（Apache 2.0）。伊予任何支援 Model Context Protocol 的應用程式（Claude、
Codex、Cursor、VS Code、Gemini CLI 等等）佇法院佮政府的網站頂即時檢索法院裁判佮法規，涵蓋 125 个法域佮國際法院，
閣有另外 91 个國家經由 Lexifina 的記錄提供（看下面）。逐筆結果攏寫明伊的來源，附原文的連結。

## 這寡文本是官方的無？

大部分是，毋過毋是全部。

- 大部分的來源是由法院、政府部會抑是官方公報營運的。
- 有一寡經過整合的現行條文是政府發布的，毋過明確聲明是非官方版本：干焦官方公報有正本效力。
- 少數來源根本毋是政府的網站（比如 LexiVox、LawPhil、Maqam、Wikisource）。

對來自這寡來源的逐个回答，Fontes 攏會加「非官方來源」的提示。引用任何內容進前，請核對官方公布的版本。
[README](README.md#涵蓋範圍) 內底的涵蓋範圍表佮 `list_jurisdictions` 會列出逐个法域的來源。

## 伊涵蓋佗一寡法域，涵蓋到啥物程度？

125 个轉接器：108 个聯合國會員國、香港、科索沃、巴勒斯坦、台灣、DIFC 法院、美國各州法院，佮 11 个國際法院佮機構
（比如歐洲人權法院、歐盟、國際法院佮世界貿易組織）。

涵蓋的程度差真濟。照嚴格的標準（完整提會著上懸普通法院的判決先例，抑是完整提會著憲法佮基本法律），
125 个內底有 72 个算是已經涵蓋。[COVERAGE.md](../../COVERAGE.md) 列出逐个法域 Fontes 提會著啥物、
提袂著啥物，佮原因。

## 我需要 API 金鑰無？

差不多所有的法域攏免。有一寡來源需要免費的金鑰：請看 [KEYS.md](KEYS.md)。

- **法國：** 需要。佇你設定 `WLM_FR_PISTE_CLIENT_ID` 佮 `WLM_FR_PISTE_CLIENT_SECRET` 進前，法國是關掉的。
  這寡金鑰來自免費的 PISTE 帳號（piste.gouv.fr），內底愛有一个已經訂閱 Judilibre 佮 Légifrance 的
  應用程式。
- **美國：** 選用。裁判檢索無金鑰嘛會當用，毋過共用的示範金鑰逐个 IP 位址逐工干焦允准大約 10 擺檢索。
  共免費的 api.data.gov 金鑰設定佇 `WLM_US_GOVINFO_KEY` 內底，會當提懸這个限額。
- **美國各州法院：** 需要。佇你共 `WLM_US_COURTLISTENER_KEY` 設定做你家己免費的 CourtListener API token 進前，各州的裁判是關掉的（`us-states`）。CourtListener 是由非營利組織 Free Law Project 營運的；伊毋是官方來源，逐筆回答攏會講明這點。

請佇你應用程式的 MCP 設定內底，共這寡設定做 Fontes 伺服器的環境變數。安裝程式會佇安裝好的時
問你這寡金鑰，以後嘛會當透過𪜶的 **Add or change keys** 啟動器來改。

另外，少數來源佇𪜶的條款內底規定，自動化存取愛有發布者的許可。𪜶標做 OFF，一直保持關掉。金鑰改變袂著
這點；干焦發布者的許可會當改變（彼時設定 `WLM_PERMITTED=<codes>`）。

## 過去版本佮其他國家是佗來的？

[Lexifina](https://github.com/lexifina/global-law) 用 git 歷史保存約 200 个國家的法律：逐擺改變攏是一个 commit，日期是伊生效的那一工。Fontes 經過 Lexifina 的免費託管伺服器讀這寡資料。兩个工具用著這寡資料：`get_law_on_date`（一條條文佇某一个日期的效力，嘛會當是過去的日期，連同最後改變伊的法律）佮 `get_law_history`（逐部改變一條條文的法律，或是兩个日期之間逐字的改變）。Fontes 嘛用這種方式讀另外 91 个國家佮領土，干焦法規，無裁判（比如南非、肯亞、墨西哥、紐西蘭、俄羅斯、南韓、比利時、立陶宛、烏克蘭、馬來西亞、泰國佮沙烏地阿拉伯）。這寡國家佮有官方即時涵蓋的 125 个法域分開講；逐國的涵蓋範圍差真濟（肯亞的國家記錄干焦有 9 部法）。印度的法（Acts）嘛是對 Lexifina 的記錄讀的，因為印度法典（India Code）的條款禁止無書面許可的自動化存取；印度的最高法院判決是即時的。

Lexifina 毋是官方發布者，伊的記錄嘛毋是即時的：Lexifina 會時常重新檢查逐个國家，伊佇 2026-11-26 自己的報告，講 383 个國家法律機關內底有 338 个佇上尾 7 工內猶未檢查。逐筆答案攏會寫明 Lexifina 是來源，連結官方發布者的頁面，講記錄到佗位。

Lexifina 認為官方法律文本無受著作權保護，所以佇一寡國家，伊複製的網站，正是 Fontes 自己會尊重其條款抑 robots.txt 的網站。Fontes 對伊自己提的資料猶是會尊重這寡條款；經過 Lexifina 來的，依 Lexifina 自己的判斷，逐國記錄佇伊的儲存庫。有幾个會限制使用（肯亞的發布者：CC BY-NC）。這寡工具佮國家的檢索詞、引註佮日期，會送去 Lexifina 的伺服器。預設是開的；設 `WLM_LEXIFINA=0` 就會關掉。免金鑰、免帳號。免費伺服器每分鐘允許 60 擺呼叫、每工 10,000 擺（逐个網路位址）。Fontes 佮 Lexifina 無隸屬關係。

## 佗一寡物件會離開我的電腦？

你的檢索干焦會送去當咧檢索的來源（若是 Lexifina 的工具佮國家，就是 Lexifina 的伺服器）。Fontes 袂起資料庫，嘛免帳號。

除了這寡來源，Fontes 逐工會問 PyPI 一擺有新的版本無（會當用 `FONTES_NO_UPDATE_CHECK=1` 關掉）。除非你
拍開，若無使用次數統計是關掉的；錯誤回報干焦佇你看過、確認了後才會送出去。你的 AI 應用程式照伊家己的條款
看著你的對話。

完整的細節：[PRIVACY.md](PRIVACY.md)。

## 這是法律意見無？

毋是。Fontes 是研究工具。伊揣文本；伊袂共你講這寡文本對你的案件有啥物意義，用伊嘛袂佮任何人成立律師
佮當事人的委任關係。AI 應用程式可能讀毋著文本，所以欲靠進前請讀裁判抑是條文的全文。若是需要意見，請問佇你
問題發生的所在有執業資格的律師。

## 啥人咧維護？伊會一直會當用無？

一个人：Yüce Karapazar。Fontes 後壁無公司，無支援合約，嘛無服務水準的承諾。無提供任何法律服務。

逐个來源逐工檢查一擺，結果公布佇[狀態頁面](https://ykarapazar.github.io/fontes/status/)頂懸。法院佮政府的
網站會無通知就改變，所以某一个來源隨時攏可能歹去。無保證任何來源抑是 Fontes 本身會一直會當用。Fontes 照
「現狀」提供，無附任何擔保（[LICENSE](../../../LICENSE) 第 7 條佮第 8 條）。

## 某一个文本有錯、過時，抑是某一个來源歹去。欲按怎回報？

- 用「Broken or wrong source」表單提出 issue：
  <https://github.com/ykarapazar/fontes/issues/new/choose>。請講明是佗一个法域、你問啥物、你得著啥物，
  佮顯示正確文本的官方頁面。
- 抑是請你的 AI 應用程式「回報 Fontes 的錯誤」（抑是執行 `fontes report-bug`）。佇傳送任何物件進前，你會
  先看著回報。
- 抑是寄電子批到 fontesmcp@proton.me。

請毋通佇回報內底包含當事人的詳細資料抑是機密的事實。

**若是你營運其中一个來源**，而且有任何毋著（你的條款、你的 robots.txt、你的速率限制），請寄電子批到
fontesmcp@proton.me。彼个來源會改正抑是關掉。

## Fontes 佮雲端託管的法律研究工具有啥物無仝？

- **伊佇你的電腦頂執行。** 無 Fontes 伺服器，嘛無帳號。這嘛是講伊干焦會當佇會啟動本機 MCP 伺服器的應用程式
  內底用（Claude Desktop、Codex、Cursor、VS Code 等等），袂當佇干焦接受託管連接器的純網頁應用程式內底用。
- **伊無資料庫。** 逐擺檢索攏即時送去發布者家己的網站抑是 API，所以結果佮來源仝款新，檢索的品質嘛看來源
  本身。無根據精選索引的語意檢索。
- **伊無設使用上限。** Fontes 無每月的呼叫次數上限。伊會為送去逐个網站的請求設定間隔，而且有一寡來源會限制
  查詢的速度抑是次數。
- **伊是開放原始碼。** 你會當讀逐个轉接器，準確知影逐个文本對佗位來。
- **伊後壁無廠商。** 無合約、支援服務台抑是正常運作時間的承諾（請看「啥人咧維護？」）。

## 伊會當佇佗一寡應用程式佮系統頂用？

任何會當執行本機（stdio）伺服器的 MCP 應用程式，比如 Claude Desktop、Claude Code、Codex、Cursor、
VS Code（GitHub Copilot）、Gemini CLI、Windsurf、Zed、LM Studio 佮 Cline。Fontes 會當佇 macOS、Windows 佮
Linux 頂執行，凡是 uv 會當執行的所在攏會使（Python 3.13+）。佇 Mac 抑是 Windows 電腦，一鍵安裝程式
會一擺設定好 Claude Desktop、Codex、Claude Code、Cursor、VS Code、Windsurf、Gemini CLI、Zed、
LM Studio 佮 Cline。逐个應用程式的步驟：[INSTALL.md](INSTALL.md)。

## 我會當貢獻程式碼無？

這馬猶袂當。歡迎提出 issue、來源回報佮法域的需求。請看 [CONTRIBUTING.md](../../../CONTRIBUTING.md)。
