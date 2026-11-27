> Đây là bản dịch có sự hỗ trợ của máy. Bản tiếng Anh là bản có giá trị quyết định.

# Khóa API

Hầu hết mọi nguồn trong Fontes đều hoạt động không cần khóa. Ba nguồn cần một khóa miễn phí:

| Khóa | Mở ra | Nếu không có |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Pháp: Judilibre (bản án) và Légifrance (văn bản quy phạm pháp luật) | Pháp bị tắt. `list_jurisdictions` hiển thị Pháp là không hoạt động. |
| `WLM_US_GOVINFO_KEY` | Hoa Kỳ: tìm kiếm govinfo (phán quyết của tòa án liên bang, Statutes at Large, public laws) | Fontes dùng `DEMO_KEY` dùng chung: khoảng 10 lượt tìm kiếm mỗi ngày cho mỗi địa chỉ IP. Mở một bản án đã biết và US Code không cần khóa. |
| `WLM_US_COURTLISTENER_KEY` | Tòa án tiểu bang Hoa Kỳ (`us-states`): các phán quyết của tòa tối cao và tòa phúc thẩm của cả 50 tiểu bang và DC, từ CourtListener | Án lệ tiểu bang Hoa Kỳ bị tắt. `list_jurisdictions` hiển thị nó là không hoạt động. |

Khóa là tùy chọn. Bạn có thể thêm sau.

## Thêm khóa

**Bằng trình cài đặt.** Sau khi Fontes được thiết lập, trình cài đặt đề nghị thêm khóa. Trên máy Mac, nhấp
**Thêm khóa**, hoặc **Xong** để bỏ qua; trên Windows, trả lời câu hỏi (nhấn Enter để bỏ qua). Để thêm hoặc thay đổi khóa sau này, hãy chạy **Add or change keys**:

- Mac: mở lại ứng dụng Fontes Installer và chọn **Thêm hoặc đổi khóa**.
- Windows: mở menu Start, rồi chọn **Fontes** → **Thêm hoặc đổi khóa**.

Nội dung bạn gõ sẽ bị ẩn. Với mỗi khóa: dán khóa vào, nhấn Enter để giữ giá trị hiện có, hoặc gõ `-` để
xóa. Các khóa được đưa vào mọi ứng dụng đã có Fontes.

**Bằng tiện ích mở rộng Claude Desktop (.mcpb).** Mở Claude > Settings > Extensions > Fontes và
điền vào các trường. Tất cả các trường đều là tùy chọn.

**Thủ công.** Thêm các biến vào khối `env` của mục `fontes` trong cấu hình MCP của ứng dụng:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Khởi động lại ứng dụng sau mỗi thay đổi.

## Pháp: PISTE (miễn phí)

1. Tạo tài khoản tại [piste.gouv.fr](https://piste.gouv.fr). Việc này đồng nghĩa với chấp nhận điều khoản của PISTE (CGU).
2. Vào API > **Consentement CGU API**. Chấp nhận điều khoản cho **JUDILIBRE** và **Légifrance** (production).
3. Tạo một **ứng dụng production**. `APP_SANDBOX` được tạo sẵn cho bạn không truy cập được production.
   Trong "Modifier l'application", đánh dấu **JUDILIBRE (production)** và **Légifrance (production)**, rồi áp dụng.
4. Mở thẻ **Authentification** của ứng dụng. Sao chép `client_id` và `client_secret`.
5. Chạy **Add or change keys** và dán chúng vào.

Tóm tắt điều khoản:

- Dữ liệu: Licence Ouverte / Etalab 2.0. Được phép tái sử dụng, kể cả tái sử dụng thương mại, với điều kiện ghi nguồn.
- Không công bố hoặc chia sẻ thông tin xác thực của bạn. Hãy báo cho PISTE nếu thông tin đó bị lộ.
- API Légifrance là dịch vụ beta. Dịch vụ có thể bị tạm ngừng, và có hạn mức (theo giây, phút và ngày).
- Văn bản trên Légifrance không phải là bản xác thực. Chỉ bản PDF Journal officiel có chữ ký mới là bản xác thực.
- Judilibre: không dùng tên của thẩm phán hoặc thư ký tòa án để đánh giá, so sánh hoặc dự đoán công việc của họ
  (Code de l'organisation judiciaire điều L111-13; đây là một tội phạm hình sự).
- Judilibre: tuân thủ GDPR. Không tìm cách xác định lại danh tính các bên.

Hạn mức của bạn nằm trên PISTE tại API Sélectionnées > Actions > Consulter les quotas.

## Hoa Kỳ: api.data.gov (miễn phí)

1. Vào [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (khóa hiển thị trên màn hình)
   hoặc [api.data.gov/signup](https://api.data.gov/signup/) (khóa được gửi qua email cho bạn).
2. Nhập tên và email của bạn. Trường "how will you use it" là tùy chọn.
3. Sao chép khóa gồm 40 ký tự.
4. Chạy **Add or change keys** và dán khóa vào làm khóa Hoa Kỳ.

Tóm tắt điều khoản:

- Với khóa riêng của bạn, govinfo cho phép tối đa 36.000 yêu cầu mỗi giờ.
- Chúng tôi không tìm thấy điều khoản dịch vụ riêng cho API (api.data.gov/terms/ không tồn tại). Chưa được xác minh.
  Xem [các chính sách của govinfo](https://www.govinfo.gov/about/policies) và
  [chính sách quyền riêng tư của data.gov](https://data.gov/privacy-policy/).
- Giữ khóa cho riêng bạn.

## Tòa án tiểu bang Hoa Kỳ: CourtListener (miễn phí)

CourtListener do [Free Law Project](https://free.law) vận hành, một tổ chức phi lợi nhuận đã thu thập các phán quyết của tòa án Hoa Kỳ từ năm 2010 và cung cấp miễn phí cho mọi người. Theo số liệu của chính họ, CourtListener có hơn chín triệu phán quyết. Đây không phải nguồn chính thức: các tòa án tự công bố phán quyết của mình, còn CourtListener thu thập chúng từ các trang web của tòa án và từ các tuyển tập án lệ được quét. Mọi câu trả lời của Fontes lấy từ nguồn này đều nêu rõ điều đó. Fontes không liên kết với Free Law Project.

1. Tạo tài khoản miễn phí tại [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Mở hồ sơ của bạn và sao chép API token của bạn.
3. Chạy **Add or change keys** và dán token vào làm khóa CourtListener.

Tóm tắt điều khoản ([điều khoản đầy đủ](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token chỉ thuộc về riêng bạn: không chia sẻ, không gộp chung hay bán lại, và không dùng nhiều tài khoản.
- Bạn chịu trách nhiệm về những gì một ứng dụng AI làm với token của bạn.
- Không trình bày phân tích dữ liệu của họ do AI thực hiện như thể do Free Law Project tạo ra, chấp thuận hoặc kiểm tra.
- Tài khoản miễn phí cho phép 5 yêu cầu mỗi phút, 50 mỗi giờ và 125 mỗi ngày. Một lần tìm kiếm là một yêu cầu; mở một phán quyết là hai yêu cầu. Tư cách thành viên của Free Law Project nâng các giới hạn này.
- CourtListener không đảm bảo tính chính xác. Hãy đối chiếu phán quyết với bản của tòa án trước khi dựa vào nó.

## Nơi lưu khóa

- **Trình cài đặt hoặc thủ công:** dưới dạng văn bản thuần trong tệp cấu hình MCP của từng ứng dụng, trong khối `env` của
  mục `fontes`. Bất kỳ ai đọc được các tệp người dùng của bạn đều đọc được các khóa.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` hoặc `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Tiện ích mở rộng Claude Desktop (.mcpb):** Claude lưu các trường này trong thiết lập của mình và bảo vệ chúng
  bằng kho lưu trữ bảo mật của hệ thống (Keychain trên Mac, Credential Manager trên Windows).

Trước mỗi thay đổi, trình cài đặt lưu một bản sao của tệp cấu hình bên cạnh tệp đó
(`<file>.fontes-backup-<time>`). Các bản sao được tạo sau khi bạn thêm khóa cũng chứa các khóa. Hãy xóa những bản
sao cũ bạn không cần.

## Thay đổi hoặc xóa khóa

- Chạy **Add or change keys**. Dán khóa mới để thay thế, hoặc gõ `-` để xóa.
- Hoặc sửa khối `env` thủ công và khởi động lại ứng dụng.
- Gỡ cài đặt Fontes sẽ xóa toàn bộ mục của Fontes, kể cả các khóa. Việc này không xóa các bản sao lưu.
- Nếu một khóa bị lộ, hãy thay khóa đó cả ở phía nguồn: trên PISTE, tạo thông tin xác thực mới cho ứng dụng của bạn;
  với api.data.gov, đăng ký một khóa mới.

## Các thông báo bạn có thể gặp

| Thông báo | Ý nghĩa |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Chưa có khóa cho Pháp. Hãy thêm khóa. |
| `Inactive: needs a free PISTE account. ...` (trong `list_jurisdictions`) | Như trên. |
| `PISTE refused the client credentials ...` | ID hoặc secret sai hoặc không còn hiệu lực. Sao chép lại cả hai từ thẻ Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Ứng dụng của bạn chưa đăng ký API đó, hoặc bạn chưa chấp nhận điều khoản của API. Xem bước 2 và 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Chưa có khóa cho Hoa Kỳ. Tìm kiếm hoạt động được vài lượt mỗi ngày. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Khóa demo đã hết lượt. Hãy thêm khóa riêng của bạn. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Khóa sai, hoặc chưa được xác nhận qua email. |

Giá trị rỗng được tính là không có khóa.

## Quyền cho phép (WLM_PERMITTED)

Đây không phải là khóa API, và trình cài đặt không đặt giá trị này. **Chỉ đặt nếu chính bạn có
sự cho phép đó.**

Một số nguồn mặc định bị tắt vì điều khoản hoặc robots.txt của chúng cấm sử dụng tự động khi chưa được
phép. Nếu bạn được bên công bố cho phép, hãy bật một nguồn bằng cách thêm mã của nguồn đó vào
`WLM_PERMITTED`, phân tách bằng dấu phẩy, trong khối `env`: `"WLM_PERMITTED": "in,de"`.

| Mã | Nguồn |
|---|---|
| `az` | Azerbaijan: e-qanun.az (Bộ Tư pháp) |
| `bh` | Bahrain: Ủy ban Pháp chế và Ý kiến Pháp lý (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (văn bản quy phạm pháp luật hợp nhất) |
| `de` | Đức: NeuRIS (cổng thông tin pháp luật liên bang, dịch vụ thử nghiệm) |
| `difc` | Tòa án Trung tâm Tài chính Quốc tế Dubai (difccourts.ae) |
| `gr` | Hy Lạp: Nhà in Quốc gia, tìm kiếm Công báo Chính phủ (search.et.gr) |
| `mu` | Mauritius: Tòa án Tối cao (supremecourt.govmu.org) |
| `sg` | Singapore: bản án của tòa án (elitigation.sg) |

Khi chưa được phép, Fontes thông báo: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
