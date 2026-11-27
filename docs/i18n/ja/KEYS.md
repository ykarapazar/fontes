> これは機械支援による翻訳です。英語版が正本です。

# API キー

Fontes のほとんどすべての情報源はキーなしで動作します。無料のキーが必要なのは 3 つです:

| キー | 使えるようになるもの | キーがない場合 |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | フランス: Judilibre（裁判例）と Légifrance（法令） | フランスはオフです。`list_jurisdictions` では無効と表示されます。 |
| `WLM_US_GOVINFO_KEY` | 米国: govinfo 検索（連邦裁判所の判決意見、Statutes at Large、公法） | Fontes は共有の `DEMO_KEY` を使います: IP アドレスごとに 1 日約 10 回の検索。既知の裁判例と US Code を開くのにキーは不要です。 |
| `WLM_US_COURTLISTENER_KEY` | 米国の州裁判所（`us-states`）: 50 州すべてと DC の最高裁判所・控訴裁判所の判決意見（CourtListener 提供） | 米国の州の判例はオフです。`list_jurisdictions` では無効と表示されます。 |

キーは任意です。後から追加できます。

## キーの追加

**インストーラーで。** Fontes の設定が終わると、インストーラーがキーの追加を勧めます。Mac では
**キーを追加** をクリックし、スキップするには **完了** をクリックします。Windows では質問に答えます（スキップ
するには Enter を押します）。後でキーを追加または変更するには、**Add or change keys** を実行します:

- Mac: Fontes Installer アプリをもう一度開いて **キーを追加・変更** を選びます。
- Windows: スタート メニューを開き、**Fontes** → **キーを追加・変更** を選びます。

入力内容は表示されません。各キーについて: 貼り付けるか、Enter を押して現在の値を保持するか、`-` を入力して
削除します。キーは、Fontes がすでに設定されているすべてのアプリに書き込まれます。

**Claude Desktop の拡張機能（.mcpb）で。** Claude > Settings > Extensions > Fontes を開き、各欄に入力します。
すべての欄は任意です。

**手動で。** アプリの MCP 設定にある `fontes` エントリーの `env` ブロックに変数を追加します:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

変更した後は、アプリを再起動してください。

## フランス: PISTE（無料）

1. [piste.gouv.fr](https://piste.gouv.fr) でアカウントを作成します。これは PISTE の利用条件（CGU）に同意する
   ことを意味します。
2. API > **Consentement CGU API** に進みます。**JUDILIBRE** と **Légifrance**（本番環境）の利用条件に
   同意します。
3. **本番環境用のアプリケーション**を作成します。自動的に作られる `APP_SANDBOX` からは本番環境に
   アクセスできません。「Modifier l'application」で **JUDILIBRE (production)** と
   **Légifrance (production)** にチェックを入れ、適用します。
4. そのアプリの **Authentification** タブを開きます。`client_id` と `client_secret` をコピーします。
5. **Add or change keys** を実行して貼り付けます。

利用条件の要点:

- データ: Licence Ouverte / Etalab 2.0。出典を表示すれば、商用を含む再利用が認められています。
- 認証情報を公開・共有しないでください。漏えいした場合は PISTE に知らせてください。
- Légifrance API はベータ版のサービスです。停止されることがあり、クォータ（毎秒・毎分・毎日）があります。
- Légifrance のテキストは正本ではありません。正本は署名入りの Journal officiel の PDF だけです。
- Judilibre: 裁判官や書記官の氏名を使って、その仕事を評価・比較・予測しないでください
  （Code de l'organisation judiciaire 第 L111-13 条。刑事犯罪です）。
- Judilibre: GDPR を遵守してください。当事者を再識別しようとしないでください。

クォータは PISTE の API Sélectionnées > Actions > Consulter les quotas で確認できます。

## 米国: api.data.gov（無料）

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup)（キーは画面に表示されます）または
   [api.data.gov/signup](https://api.data.gov/signup/)（キーはメールで届きます）に進みます。
2. 名前とメールアドレスを入力します。「how will you use it」欄は任意です。
3. 40 文字のキーをコピーします。
4. **Add or change keys** を実行し、米国のキーとして貼り付けます。

利用条件の要点:

- 自分のキーを使う場合、govinfo では 1 時間あたり最大 36,000 件のリクエストが認められています。
- API 固有の利用規約は見つかりませんでした（api.data.gov/terms/ は存在しません）。未確認です。
  [govinfo のポリシー](https://www.govinfo.gov/about/policies)と
  [data.gov のプライバシーポリシー](https://data.gov/privacy-policy/)をご覧ください。
- キーは他人に教えないでください。

## 米国の州裁判所: CourtListener（無料）

CourtListener は [Free Law Project](https://free.law) が運営しています。Free Law Project は 2010 年から米国の裁判所の判決意見を収集し、誰でも無料で利用できるようにしている非営利団体です。同団体の集計では、900 万件を超える判決を保有しています。公的な情報源ではありません。判決意見は各裁判所が自ら公開しており、CourtListener は裁判所のウェブサイトやスキャンされた判例集から収集しています。CourtListener 由来の Fontes の回答には、すべてその旨が示されます。Fontes は Free Law Project とは提携していません。

1. [courtlistener.com](https://www.courtlistener.com/sign-in/) で無料アカウントを作成します。
2. プロフィールを開き、API トークンをコピーします。
3. **Add or change keys** を実行し、CourtListener のキーとして貼り付けます。

利用条件の要点（[全文](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)）:

- トークンはあなた専用です。共有、プール、再販はせず、複数のアカウントも使わないでください。
- AI アプリがトークンを使って行うことについては、あなたが責任を負います。
- 同団体のデータに対する AI の分析を、Free Law Project が作成・承認・確認したものとして示さないでください。
- 無料アカウントでは 1 分あたり 5 件、1 時間あたり 50 件、1 日あたり 125 件のリクエストが認められています。検索は 1 件、判決を開くと 2 件と数えます。Free Law Project の会員になると上限が上がります。
- CourtListener は正確性を保証しません。依拠する前に、判決意見を裁判所の写しと照合してください。

## キーの保存場所

- **インストーラーまたは手動:** 各アプリの MCP 設定ファイル内の、`fontes` エントリーの `env` ブロックに
  プレーンテキストで保存されます。あなたのユーザーファイルを読める人は、誰でもキーを読めます。
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json`（Mac）、
    `%APPDATA%\Claude\claude_desktop_config.json`（Windows）
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code（Copilot）: `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` または `~/.codeium/windsurf/mcp_config.json`
    （Windows: `%APPDATA%\devin\mcp_config.json`）
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json`（Windows: `%APPDATA%\Zed\settings.json`）
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop の拡張機能（.mcpb）:** Claude がこれらの欄を設定内に保存し、システムの安全な保存領域
  （Mac ではキーチェーン、Windows では資格情報マネージャー）で保護します。

変更のたびに、インストーラーは設定ファイルのコピーを隣に保存します（`<file>.fontes-backup-<time>`）。
キーを追加した後に作られたコピーにはキーも含まれます。不要な古いコピーは削除してください。

## キーの変更・削除

- **Add or change keys** を実行します。新しいキーを貼り付けて置き換えるか、`-` を入力して削除します。
- または、`env` ブロックを手動で編集し、アプリを再起動します。
- Fontes をアンインストールすると、そのエントリー全体がキーごと削除されます。バックアップのコピーは
  削除されません。
- キーが漏えいした場合は、情報源の側でも差し替えてください: PISTE ではアプリの認証情報を新たに作成し、
  api.data.gov では新しいキーを申請します。

## 表示される可能性のあるメッセージ

| メッセージ | 意味 |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | フランスのキーがありません。追加してください。 |
| `Inactive: needs a free PISTE account. ...`（`list_jurisdictions` 内） | 同上。 |
| `PISTE refused the client credentials ...` | ID またはシークレットが誤っているか、無効になっています。Authentification タブから両方をコピーし直してください。 |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | アプリがその API を購読していないか、利用条件に同意していません。手順 2 と 3 をご覧ください。 |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | 米国のキーがありません。1 日に数回は検索できます。 |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | デモキーの上限に達しました。自分のキーを追加してください。 |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | キーが誤っているか、まだメールで確認されていません。 |

空の値はキーなしとして扱われます。

## 許可（WLM_PERMITTED）

これは API キーではなく、インストーラーでは設定されません。**その許可をあなた自身が得ている場合にのみ
設定してください。**

一部の情報源は、利用条件または robots.txt が許可のない自動利用を禁じているため、デフォルトでオフです。
発行元から許可を得ている場合は、`env` ブロックの `WLM_PERMITTED` にその情報源のコードをカンマ区切りで
追加すると、オンになります: `"WLM_PERMITTED": "in,de"`。

| コード | 情報源 |
|---|---|
| `az` | アゼルバイジャン: e-qanun.az（司法省） |
| `bh` | バーレーン: 立法・法律意見委員会（lloc.gov.bh） |
| `co` | コロンビア: Función Pública、Gestor Normativo（現行統合版の法令） |
| `de` | ドイツ: NeuRIS（連邦法情報ポータル、試験運用サービス） |
| `difc` | ドバイ国際金融センター裁判所（difccourts.ae） |
| `gr` | ギリシャ: 国立印刷局、官報検索（search.et.gr） |
| `in` | インド: India Code（indiacode.gov.in） |
| `mu` | モーリシャス: 最高裁判所（supremecourt.govmu.org） |
| `sg` | シンガポール: 裁判所の判決（elitigation.sg） |

許可がない場合、Fontes は次のように表示します: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
