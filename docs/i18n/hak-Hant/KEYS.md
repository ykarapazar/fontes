> 這係機器輔助个翻譯，以英文版本為準。

# API 金鑰

Fontes 肚項幾乎所有个來源無金鑰都做得用。有兩个需要免費个金鑰：

| 金鑰 | 打開个內容 | 無金鑰个時節 |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | 法國：Judilibre（法院裁判）同 Légifrance（法規） | 法國係關忒个。`list_jurisdictions` 會顯示佢無啟用。 |
| `WLM_US_GOVINFO_KEY` | 美國：govinfo 檢索（聯邦法院判決意見、Statutes at Large、公法） | Fontes 用共用个 `DEMO_KEY`：每一个 IP 位址逐日大約 10 擺檢索。打開已知个裁判同 US Code 毋使金鑰。 |

金鑰係選用个。你做得以後正加。

## 加金鑰

**用安裝程式。** Fontes 設定好以後，安裝程式會問你愛毋愛加金鑰。在 Mac 頂，撳 **加入金鑰**，或者撳 **完成**
略過；在 Windows 頂，回答問題（撳 Enter 略過）。以後愛加或者
改金鑰，請執行 **Add or change keys**：

- Mac：再打開 Fontes Installer 應用程式，揀 **加入或者修改金鑰**。
- Windows：開啟開始功能表，然後揀 **Fontes** → **加入或者修改金鑰**。

輸入个內容毋會顯示。對每一个金鑰：貼上金鑰、撳 Enter 保留現在个值，或者輸入 `-` 將佢移除。金鑰會寫入每一个
已經裝 Fontes 个應用程式。

**用 Claude Desktop 擴充功能（.mcpb）。** 打開 Claude > Settings > Extensions > Fontes，填欄位。所有个欄位
都係選填个。

**用手設定。** 將這兜變數加到你應用程式 MCP 設定肚項 `fontes` 項目个 `env` 區塊：

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

改過任何東西以後，請重新啟動應用程式。

## 法國：PISTE（免費）

1. 在 [piste.gouv.fr](https://piste.gouv.fr) 建立帳號。這表示你接受 PISTE 个條款（CGU）。
2. 去 API > **Consentement CGU API**。接受 **JUDILIBRE** 同 **Légifrance**（正式環境）个條款。
3. 建立一个**正式環境个應用程式**。系統為你建立个 `APP_SANDBOX` 無法度存取正式環境。
   在「Modifier l'application」下背，勾 **JUDILIBRE (production)** 同 **Légifrance (production)**，再套用。
4. 打開該應用程式个 **Authentification** 分頁。複製 `client_id` 同 `client_secret`。
5. 執行 **Add or change keys**，將佢兜貼上去。

條款摘要：

- 資料：Licence Ouverte / Etalab 2.0。允許再利用，包括商業再利用，毋過愛標示出處。
- 請毋好公開或者分享你个憑證。若係憑證洩漏，請通知 PISTE。
- Légifrance API 係測試版个服務。佢可能會暫停，而且有配額（每秒、每分鐘同逐日）。
- Légifrance 个文本毋係正本。單淨有簽署个 Journal officiel PDF 正係。
- Judilibre：請毋好用法官或者書記官个名來評估、比較或者預測佢兜个工作
  （Code de l'organisation judiciaire 第 L111-13 條；係刑事犯罪）。
- Judilibre：遵守 GDPR。請毋好試著重新識別當事人。

你个配額做得在 PISTE 个 API Sélectionnées > Actions > Consulter les quotas 下背看。

## 美國：api.data.gov（免費）

1. 去 [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup)（金鑰會顯示在畫面頂）
   或者 [api.data.gov/signup](https://api.data.gov/signup/)（金鑰會用電子郵件寄分你）。
2. 輸入你个名同電子郵件地址。「how will you use it」欄位係選填个。
3. 複製這个 40 个字元个金鑰。
4. 執行 **Add or change keys**，將佢貼上去做美國金鑰。

條款摘要：

- 用你自家个金鑰个時節，govinfo 每點鐘最多允許 36,000 擺請求。
- 𠊎兜無尋著專門針對這个 API 个服務條款（api.data.gov/terms/ 無存在）。無經過查證。
  請看 [govinfo 个政策](https://www.govinfo.gov/about/policies) 同
  [data.gov 隱私權政策](https://data.gov/privacy-policy/)。
- 請毋好將金鑰講分別人知。

## 金鑰放在哪位

- **安裝程式或者用手設定：** 用純文字个形式放在每一个應用程式个 MCP 設定檔肚項，在 `fontes` 項目个 `env`
  區塊肚項。任何讀得著你使用者檔案个人都讀得著這兜金鑰。
  - Claude Desktop：`~/Library/Application Support/Claude/claude_desktop_config.json`（Mac），
    `%APPDATA%\Claude\claude_desktop_config.json`（Windows）
  - Claude Code：`~/.claude.json`
  - Codex：`~/.codex/config.toml`
  - Cursor：`~/.cursor/mcp.json`
  - VS Code（Copilot）：`~/.copilot/mcp-config.json`
  - Windsurf：`~/.config/devin/mcp_config.json` 或者 `~/.codeium/windsurf/mcp_config.json`
    （Windows：`%APPDATA%\devin\mcp_config.json`）
  - Gemini CLI：`~/.gemini/settings.json`
  - Zed：`~/.config/zed/settings.json`（Windows：`%APPDATA%\Zed\settings.json`）
  - LM Studio：`~/.lmstudio/mcp.json`
  - Cline：`~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop 擴充功能（.mcpb）：** Claude 將這兜欄位保存在佢个設定肚項，用你系統个安全儲存區保護
  （Mac 頂係鑰匙圈，Windows 頂係認證管理員）。

每一擺改以前，安裝程式都會在設定檔旁邊儲存一份副本（`<file>.fontes-backup-<time>`）。在你加金鑰以後做个
副本也包含金鑰。請刪忒你毋使个舊副本。

## 改或者移除金鑰

- 執行 **Add or change keys**。貼上新金鑰來取代舊金鑰，或者輸入 `-` 將佢移除。
- 或者用手改 `env` 區塊，再重新啟動應用程式。
- 解除安裝 Fontes 會移除佢整个項目，連金鑰也做一下。佢毋會刪忒備份副本。
- 若係金鑰洩漏，也愛在來源該片換：在 PISTE 頂，為你个應用程式產生新个憑證；api.data.gov 个話，重新申請
  一个新金鑰。

## 你可能看著个訊息

| 訊息 | 意思 |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | 無法國金鑰。請加一个。 |
| `Inactive: needs a free PISTE account. ...`（在 `list_jurisdictions` 肚項） | 同頂高共樣。 |
| `PISTE refused the client credentials ...` | ID 或者密碼毋著或者失效。請從 Authentification 分頁重新複製兩个。 |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | 你个應用程式無訂閱該 API，或者你還吂接受佢个條款。請看步驟 2 同 3。 |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | 無美國金鑰。逐日做得做少少个檢索。 |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | 示範金鑰个額度用忒了。請加你自家个金鑰。 |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | 金鑰毋著，或者還吂透過電子郵件確認。 |

空白个值算做無金鑰。

## 許可（WLM_PERMITTED）

這毋係 API 金鑰，安裝程式也毋會設定佢。**單淨在你本人有該許可个時節正做得設定。**

有兜來源預設係關忒个，因為佢兜个條款或者 robots.txt 禁止無許可个自動化使用。若係你已經拿著發布者个許可，
做得將該來源个代碼用逗號分開加到 `env` 區塊肚項个 `WLM_PERMITTED`，來打開該來源：`"WLM_PERMITTED": "in,de"`。

| 代碼 | 來源 |
|---|---|
| `az` | 亞塞拜然：e-qanun.az（司法部） |
| `bh` | 巴林：立法同法律意見委員會（lloc.gov.bh） |
| `co` | 哥倫比亞：Función Pública，Gestor Normativo（經過整合个現行法規） |
| `de` | 德國：NeuRIS（聯邦法律資訊入口網站，試營運服務） |
| `difc` | 杜拜國際金融中心法院（difccourts.ae） |
| `gr` | 希臘：國家印刷局，政府公報檢索（search.et.gr） |
| `in` | 印度：India Code（indiacode.gov.in） |
| `mu` | 模里西斯：最高法院（supremecourt.govmu.org） |
| `sg` | 新加坡：法院判決（elitigation.sg） |

無許可个時節，Fontes 會顯示：`Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
