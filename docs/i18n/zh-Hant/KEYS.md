> 本文為機器輔助翻譯，以英文版本為準。

# API 金鑰

Fontes 中幾乎所有來源都不需要金鑰即可使用。有兩個需要免費金鑰：

| 金鑰 | 開啟的內容 | 沒有金鑰時 |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | 法國：Judilibre（法院裁判）與 Légifrance（法規） | 法國處於關閉狀態。`list_jurisdictions` 會將其顯示為未啟用。 |
| `WLM_US_GOVINFO_KEY` | 美國：govinfo 檢索（聯邦法院判決意見、Statutes at Large、公法） | Fontes 使用共用的 `DEMO_KEY`：每個 IP 位址每天約 10 次檢索。開啟已知的裁判與 US Code 不需要金鑰。 |

金鑰為選用。您可以日後再新增。

## 新增金鑰

**使用安裝程式。** Fontes 設定完成後，安裝程式會提供新增金鑰的選項。在 Mac 上，按一下 **新增金鑰**，
或按 **完成** 略過；在 Windows 上，回答提問（按 Enter 略過）。日後要新增或變更金鑰，請執行
**Add or change keys**：

- Mac：再次開啟 Fontes Installer 應用程式並選擇 **新增或變更金鑰**。
- Windows：開啟開始功能表，然後點選 **Fontes** → **新增或變更金鑰**。

輸入內容不會顯示。對於每個金鑰：貼上金鑰、按 Enter 保留現有值，或輸入 `-` 將其移除。金鑰會寫入每個已安裝
Fontes 的應用程式。

**使用 Claude Desktop 擴充功能（.mcpb）。** 開啟 Claude > Settings > Extensions > Fontes 並填寫欄位。所有欄位
皆為選填。

**手動設定。** 將這些變數加入您應用程式 MCP 設定中 `fontes` 項目的 `env` 區塊：

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

任何變更之後都請重新啟動應用程式。

## 法國：PISTE（免費）

1. 在 [piste.gouv.fr](https://piste.gouv.fr) 建立帳號。這表示您接受 PISTE 條款（CGU）。
2. 前往 API > **Consentement CGU API**。接受 **JUDILIBRE** 與 **Légifrance**（正式環境）的條款。
3. 建立一個**正式環境應用程式**。系統為您建立的 `APP_SANDBOX` 無法存取正式環境。
   在「Modifier l'application」下，勾選 **JUDILIBRE (production)** 與 **Légifrance (production)**，然後套用。
4. 開啟該應用程式的 **Authentification** 分頁。複製 `client_id` 與 `client_secret`。
5. 執行 **Add or change keys** 並貼上它們。

條款摘要：

- 資料：Licence Ouverte / Etalab 2.0。允許再利用，包括商業再利用，但須標示出處。
- 請勿公開或分享您的憑證。如果憑證外洩，請告知 PISTE。
- Légifrance API 是測試版服務。它可能被暫停，而且有配額（每秒、每分鐘與每天）。
- Légifrance 的文本不是正本。只有經簽署的 Journal officiel PDF 才是。
- Judilibre：請勿使用法官或書記官的姓名來評估、比較或預測其工作
  （Code de l'organisation judiciaire 第 L111-13 條；屬刑事犯罪）。
- Judilibre：遵守 GDPR。請勿嘗試重新識別當事人。

您的配額可在 PISTE 的 API Sélectionnées > Actions > Consulter les quotas 下查看。

## 美國：api.data.gov（免費）

1. 前往 [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup)（金鑰會顯示在畫面上）
   或 [api.data.gov/signup](https://api.data.gov/signup/)（金鑰會以電子郵件寄給您）。
2. 輸入您的姓名與電子郵件地址。「how will you use it」欄位為選填。
3. 複製這個 40 個字元的金鑰。
4. 執行 **Add or change keys** 並將其貼上作為美國金鑰。

條款摘要：

- 使用您自己的金鑰時，govinfo 每小時最多允許 36,000 次請求。
- 我們沒有找到專門針對此 API 的服務條款（api.data.gov/terms/ 不存在）。未經查證。
  請參閱 [govinfo 的政策](https://www.govinfo.gov/about/policies) 與
  [data.gov 隱私權政策](https://data.gov/privacy-policy/)。
- 請勿將金鑰告訴他人。

## 金鑰存放在哪裡

- **安裝程式或手動設定：** 以純文字形式存放在每個應用程式的 MCP 設定檔中，位於 `fontes` 項目的 `env` 區塊內。
  任何能讀取您使用者檔案的人都能讀取這些金鑰。
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
- **Claude Desktop 擴充功能（.mcpb）：** Claude 將這些欄位保存在其設定中，並以您系統的安全儲存區加以保護
  （Mac 上為鑰匙圈，Windows 上為認證管理員）。

每次變更之前，安裝程式都會在設定檔旁邊儲存一份副本（`<file>.fontes-backup-<time>`）。在您新增金鑰之後產生的
副本也包含金鑰。請刪除您不需要的舊副本。

## 變更或移除金鑰

- 執行 **Add or change keys**。貼上新金鑰以取代舊金鑰，或輸入 `-` 將其移除。
- 或手動編輯 `env` 區塊，然後重新啟動應用程式。
- 解除安裝 Fontes 會移除其整個項目，包括金鑰。它不會刪除備份副本。
- 如果金鑰外洩，也要在來源端更換：在 PISTE 上，為您的應用程式產生新的憑證；對於 api.data.gov，重新申請
  一個新金鑰。

## 您可能看到的訊息

| 訊息 | 意義 |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | 沒有法國金鑰。請新增一個。 |
| `Inactive: needs a free PISTE account. ...`（在 `list_jurisdictions` 中） | 同上。 |
| `PISTE refused the client credentials ...` | ID 或密碼有誤或已失效。請從 Authentification 分頁重新複製兩者。 |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | 您的應用程式未訂閱該 API，或您尚未接受其條款。請參閱步驟 2 與 3。 |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | 沒有美國金鑰。每天可進行少量檢索。 |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | 示範金鑰的額度已用完。請新增您自己的金鑰。 |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | 金鑰有誤，或尚未透過電子郵件確認。 |

空白值視為沒有金鑰。

## 許可（WLM_PERMITTED）

這不是 API 金鑰，安裝程式也不會設定它。**只有在您本人持有該許可時才可設定。**

有些來源預設關閉，因為其條款或 robots.txt 禁止未經許可的自動化使用。如果您已取得發布者的許可，可將該來源的
代碼以逗號分隔加入 `env` 區塊中的 `WLM_PERMITTED`，以開啟該來源：`"WLM_PERMITTED": "in,de"`。

| 代碼 | 來源 |
|---|---|
| `az` | 亞塞拜然：e-qanun.az（司法部） |
| `bh` | 巴林：立法與法律意見委員會（lloc.gov.bh） |
| `co` | 哥倫比亞：Función Pública，Gestor Normativo（經整合之現行法規） |
| `de` | 德國：NeuRIS（聯邦法律資訊入口網站，試營運服務） |
| `difc` | 杜拜國際金融中心法院（difccourts.ae） |
| `gr` | 希臘：國家印刷局，政府公報檢索（search.et.gr） |
| `in` | 印度：India Code（indiacode.gov.in） |
| `mu` | 模里西斯：最高法院（supremecourt.govmu.org） |
| `sg` | 新加坡：法院判決（elitigation.sg） |

沒有許可時，Fontes 會顯示：`Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
