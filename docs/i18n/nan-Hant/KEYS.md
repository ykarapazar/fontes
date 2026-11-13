> 這是機器輔助的翻譯，以英文版本為準。

# API 金鑰

Fontes 內底差不多所有的來源無金鑰攏會當用。有兩个需要免費的金鑰：

| 金鑰 | 拍開的內容 | 無金鑰的時 |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | 法國：Judilibre（法院裁判）佮 Légifrance（法規） | 法國是關掉的。`list_jurisdictions` 會顯示伊無啟用。 |
| `WLM_US_GOVINFO_KEY` | 美國：govinfo 檢索（聯邦法院判決意見、Statutes at Large、公法） | Fontes 用共用的 `DEMO_KEY`：逐个 IP 位址逐工大約 10 擺檢索。拍開已知的裁判佮 US Code 免金鑰。 |

金鑰是選用的。你會當以後才加。

## 加金鑰

**用安裝程式。** 安裝的時，安裝程式會問你欲加金鑰無。揀 **Not now**（抑是揤 Enter）跳過。以後欲加抑是
改金鑰，請執行 **Add or change keys**：

- Mac：閣拍開 Fontes Installer 應用程式，揀 **Add or change keys**，抑是揤兩下安裝程式資料夾內底的
  `Add or change keys.command`。
- Windows：揤兩下安裝程式資料夾內底的 `Add or change keys.cmd`。Windows 安裝程式推出了後，嘛會共伊囥佇
  開始功能表 > Fontes 內底。

輸入的內容袂顯示。對逐个金鑰：貼上金鑰、揤 Enter 保留這馬的值，抑是輸入 `-` 共伊移除。金鑰會寫入逐个
已經裝 Fontes 的應用程式。

**用 Claude Desktop 擴充功能（.mcpb）。** 拍開 Claude > Settings > Extensions > Fontes，填欄位。所有的欄位
攏是選填的。

**用手設定。** 共這寡變數加到你應用程式 MCP 設定內底 `fontes` 項目的 `env` 區塊：

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

改過任何物件了後，請重新啟動應用程式。

## 法國：PISTE（免費）

1. 佇 [piste.gouv.fr](https://piste.gouv.fr) 建立帳號。這表示你接受 PISTE 的條款（CGU）。
2. 去 API > **Consentement CGU API**。接受 **JUDILIBRE** 佮 **Légifrance**（正式環境）的條款。
3. 建立一个**正式環境的應用程式**。系統為你建立的 `APP_SANDBOX` 無法度存取正式環境。
   佇「Modifier l'application」下面，勾 **JUDILIBRE (production)** 佮 **Légifrance (production)**，閣套用。
4. 拍開彼个應用程式的 **Authentification** 分頁。複製 `client_id` 佮 `client_secret`。
5. 執行 **Add or change keys**，共𪜶貼起去。

條款摘要：

- 資料：Licence Ouverte / Etalab 2.0。允准再利用，包括商業再利用，毋過愛標示出處。
- 請毋通公開抑是分享你的憑證。若是憑證洩漏，請通知 PISTE。
- Légifrance API 是測試版的服務。伊可能會暫停，而且有配額（每秒、每分鐘佮逐工）。
- Légifrance 的文本毋是正本。干焦有簽署的 Journal officiel PDF 才是。
- Judilibre：請毋通用法官抑是書記官的名來評估、比較抑是預測𪜶的工作
  （Code de l'organisation judiciaire 第 L111-13 條；是刑事犯罪）。
- Judilibre：遵守 GDPR。請毋通試欲重新識別當事人。

你的配額會當佇 PISTE 的 API Sélectionnées > Actions > Consulter les quotas 下面看。

## 美國：api.data.gov（免費）

1. 去 [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup)（金鑰會顯示佇畫面頂）
   抑是 [api.data.gov/signup](https://api.data.gov/signup/)（金鑰會用電子批寄予你）。
2. 輸入你的名佮電子批地址。「how will you use it」欄位是選填的。
3. 複製這个 40 个字元的金鑰。
4. 執行 **Add or change keys**，共伊貼起去做美國金鑰。

條款摘要：

- 用你家己的金鑰的時，govinfo 每點鐘上濟允准 36,000 擺請求。
- 阮無揣著專門針對這个 API 的服務條款（api.data.gov/terms/ 無存在）。無經過查證。
  請看 [govinfo 的政策](https://www.govinfo.gov/about/policies) 佮
  [data.gov 隱私權政策](https://data.gov/privacy-policy/)。
- 請毋通共金鑰講予別人知。

## 金鑰囥佇佗位

- **安裝程式抑是用手設定：** 用純文字的形式囥佇逐个應用程式的 MCP 設定檔內底，佇 `fontes` 項目的 `env`
  區塊內底。任何讀會著你使用者檔案的人攏讀會著這寡金鑰。
  - Claude Desktop：`~/Library/Application Support/Claude/claude_desktop_config.json`（Mac），
    `%APPDATA%\Claude\claude_desktop_config.json`（Windows）
  - Claude Code：`~/.claude.json`
  - Codex：`~/.codex/config.toml`
  - Cursor：`~/.cursor/mcp.json`
  - VS Code（Copilot）：`~/.copilot/mcp-config.json`
  - Windsurf：`~/.config/devin/mcp_config.json` 抑是 `~/.codeium/windsurf/mcp_config.json`
    （Windows：`%APPDATA%\devin\mcp_config.json`）
  - Gemini CLI：`~/.gemini/settings.json`
  - Zed：`~/.config/zed/settings.json`（Windows：`%APPDATA%\Zed\settings.json`）
  - LM Studio：`~/.lmstudio/mcp.json`
  - Cline：`~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop 擴充功能（.mcpb）：** Claude 共這寡欄位保存佇伊的設定內底，用你系統的安全儲存區保護
  （Mac 頂是鑰匙圈，Windows 頂是認證管理員）。

逐擺改進前，安裝程式攏會佇設定檔邊仔儲存一份副本（`<file>.fontes-backup-<time>`）。佇你加金鑰了後做的
副本嘛包含金鑰。請刪掉你無愛的舊副本。

## 改抑是移除金鑰

- 執行 **Add or change keys**。貼上新金鑰來取代舊金鑰，抑是輸入 `-` 共伊移除。
- 抑是用手改 `env` 區塊，閣重新啟動應用程式。
- 解除安裝 Fontes 會移除伊規个項目，連金鑰嘛做伙。伊袂刪掉備份副本。
- 若是金鑰洩漏，嘛愛佇來源遐換：佇 PISTE 頂，為你的應用程式產生新的憑證；api.data.gov 的話，重新申請
  一个新金鑰。

## 你可能看著的訊息

| 訊息 | 意思 |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | 無法國金鑰。請加一个。 |
| `Inactive: needs a free PISTE account. ...`（佇 `list_jurisdictions` 內底） | 佮頂面仝款。 |
| `PISTE refused the client credentials ...` | ID 抑是密碼毋著抑是失效。請對 Authentification 分頁重新複製兩个。 |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | 你的應用程式無訂閱彼个 API，抑是你猶未接受伊的條款。請看步驟 2 佮 3。 |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | 無美國金鑰。逐工會當做少少的檢索。 |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | 示範金鑰的額度用了矣。請加你家己的金鑰。 |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | 金鑰毋著，抑是猶未透過電子批確認。 |

空白的值算做無金鑰。

## 許可（WLM_PERMITTED）

這毋是 API 金鑰，安裝程式嘛袂設定伊。**干焦佇你本人有彼个許可的時才會使設定。**

有一寡來源預設是關掉的，因為𪜶的條款抑是 robots.txt 禁止無許可的自動化使用。若是你已經提著發布者的許可，
會當共彼个來源的代碼用逗號分開加到 `env` 區塊內底的 `WLM_PERMITTED`，來拍開彼个來源：`"WLM_PERMITTED": "in,de"`。

| 代碼 | 來源 |
|---|---|
| `az` | 亞塞拜然：e-qanun.az（司法部） |
| `bh` | 巴林：立法佮法律意見委員會（lloc.gov.bh） |
| `co` | 哥倫比亞：Función Pública，Gestor Normativo（經過整合的現行法規） |
| `de` | 德國：NeuRIS（聯邦法律資訊入口網站，試營運服務） |
| `difc` | 杜拜國際金融中心法院（difccourts.ae） |
| `gr` | 希臘：國家印刷局，政府公報檢索（search.et.gr） |
| `in` | 印度：India Code（indiacode.gov.in） |
| `mu` | 模里西斯：最高法院（supremecourt.govmu.org） |
| `sg` | 新加坡：法院判決（elitigation.sg） |

無許可的時，Fontes 會顯示：`Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
