> Đây là bản dịch có sự hỗ trợ của máy. Bản tiếng Anh là bản có giá trị quyết định.

# Fontes: hỏi và đáp

## Fontes là gì?

Một máy chủ MCP miễn phí, mã nguồn mở (Apache 2.0). Fontes cho phép mọi ứng dụng hỗ trợ Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI và các ứng dụng khác) tìm kiếm bản án và
văn bản quy phạm pháp luật trực tiếp trên các trang web của tòa án và cơ quan nhà nước ở hơn 120 phạm vi tài phán và các tòa án
quốc tế (124 adapter). Mọi kết quả đều nêu tên nguồn và dẫn liên kết tới bản gốc.

## Các văn bản có phải là bản chính thức không?

Phần lớn là có, nhưng không phải lúc nào cũng vậy.

- Phần lớn các nguồn do một tòa án, một bộ hoặc một công báo chính thức vận hành.
- Một số văn bản hợp nhất do cơ quan nhà nước công bố nhưng được nêu rõ là không chính thức: chỉ
  công báo chính thức mới là bản xác thực.
- Một số ít nguồn hoàn toàn không phải trang web của nhà nước (ví dụ LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes thêm thông báo "Nguồn không chính thức" vào mọi câu trả lời lấy từ một trong các nguồn này. Trước khi
bạn trích dẫn bất cứ điều gì, hãy kiểm tra bản công bố chính thức. Bảng phạm vi bao quát trong
[README](README.md#phạm-vi-bao-quát) và `list_jurisdictions` nêu tên nguồn của từng phạm vi tài phán.

## Fontes bao quát những phạm vi tài phán nào, và ở mức độ nào?

124 adapter: 108 quốc gia thành viên Liên Hợp Quốc, Hồng Kông, Kosovo, Palestine, Đài Loan, Tòa án DIFC và
11 tòa án và cơ quan quốc tế (như Tòa án Nhân quyền châu Âu, EU, Tòa án Công lý
Quốc tế (ICJ) và WTO).

Phạm vi bao quát khác nhau rất nhiều. Theo một tiêu chí chặt chẽ (các án lệ của tòa án chung cấp cao nhất, hoặc
hiến pháp và các đạo luật chính, được truy cập đầy đủ), 72 trên 124 được tính là đã bao quát.
[COVERAGE.md](../../COVERAGE.md) liệt kê, với từng phạm vi tài phán, những gì Fontes truy cập được, những gì không,
và lý do.

## Tôi có cần khóa API không?

Với hầu hết mọi phạm vi tài phán, không. Một số nguồn cần khóa miễn phí: xem [KEYS.md](KEYS.md).

- **Pháp:** có. Pháp bị tắt cho đến khi bạn đặt `WLM_FR_PISTE_CLIENT_ID` và
  `WLM_FR_PISTE_CLIENT_SECRET`. Các giá trị này lấy từ một tài khoản PISTE miễn phí (piste.gouv.fr) với một
  ứng dụng đã đăng ký Judilibre và Légifrance.
- **Hoa Kỳ:** tùy chọn. Tìm kiếm án lệ hoạt động không cần khóa, nhưng khóa demo dùng chung
  chỉ cho phép khoảng 10 lượt tìm kiếm mỗi ngày cho mỗi địa chỉ IP. Một khóa api.data.gov miễn phí trong
  `WLM_US_GOVINFO_KEY` sẽ nâng giới hạn này.

Hãy đặt chúng làm biến môi trường cho máy chủ Fontes trong thiết lập MCP của ứng dụng. Các
trình cài đặt hỏi các khóa này sau khi cài đặt, và trình khởi chạy **Add or change keys** của chúng
dùng để thay đổi chúng về sau.

Ngoài ra, một số ít nguồn nêu trong điều khoản rằng việc truy cập tự động cần sự cho phép của bên công bố.
Các nguồn này được đánh dấu OFF và vẫn tắt. Khóa không thay đổi điều đó; chỉ sự cho phép của bên công bố
mới thay đổi được (khi đó hãy đặt `WLM_PERMITTED=<codes>`).

## Những gì rời khỏi máy tính của tôi?

Các tìm kiếm của bạn chỉ được gửi tới nguồn đang được tìm kiếm. Fontes không lưu giữ cơ sở dữ liệu và không cần
tài khoản.

Ngoài các nguồn, mỗi ngày một lần Fontes hỏi PyPI xem có phiên bản mới hơn không (tắt
bằng `FONTES_NO_UPDATE_CHECK=1`). Số liệu sử dụng tắt trừ khi bạn bật, và một báo cáo lỗi
chỉ được gửi sau khi bạn đã xem và xác nhận. Ứng dụng AI của bạn thấy cuộc trò chuyện của bạn theo
điều khoản riêng của ứng dụng đó.

Chi tiết đầy đủ: [PRIVACY.md](PRIVACY.md).

## Đây có phải là tư vấn pháp lý không?

Không. Fontes là công cụ nghiên cứu. Fontes tìm văn bản; Fontes không cho bạn biết ý nghĩa của văn bản đối với
vụ việc của bạn, và việc sử dụng Fontes không tạo ra quan hệ luật sư – khách hàng với bất kỳ ai. Ứng dụng AI có thể
đọc sai một văn bản, vì vậy hãy đọc toàn văn bản án hoặc điều khoản trước khi dựa vào. Để được tư vấn, hãy hỏi
một luật sư có đủ tư cách hành nghề tại nơi phát sinh câu hỏi của bạn.

## Ai duy trì Fontes? Fontes có tiếp tục hoạt động không?

Một người: Yüce Karapazar. Không có công ty nào đứng sau Fontes, không có hợp đồng hỗ trợ và không có
cam kết về mức độ dịch vụ. Không cung cấp dịch vụ pháp lý.

Các nguồn được kiểm tra mỗi ngày một lần và kết quả được công bố trên
[trang trạng thái](https://ykarapazar.github.io/fontes/status/). Trang web của tòa án và cơ quan nhà nước
thay đổi mà không báo trước, nên một nguồn có thể ngừng hoạt động bất cứ lúc nào. Không có bảo đảm nào rằng bất kỳ nguồn nào,
hay chính Fontes, sẽ tiếp tục hoạt động. Fontes được cung cấp "nguyên trạng", không có bảo đảm (mục 7
và 8 của [LICENSE](../../../LICENSE)).

## Một văn bản bị sai, lỗi thời hoặc một nguồn bị hỏng. Tôi báo cáo bằng cách nào?

- Mở một issue bằng biểu mẫu "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Nêu rõ phạm vi tài phán nào, bạn đã
  hỏi gì, bạn nhận được gì, và trang chính thức thể hiện văn bản đúng.
- Hoặc đề nghị ứng dụng AI của bạn "báo cáo một lỗi của Fontes" (hoặc chạy `fontes report-bug`). Bạn xem báo cáo trước khi
  bất cứ thứ gì được gửi đi.
- Hoặc gửi email tới fontesmcp@proton.me.

Không đưa thông tin về khách hàng hoặc tình tiết bảo mật vào báo cáo.

**Nếu bạn vận hành một trong các nguồn** và có điều gì sai (điều khoản của bạn, robots.txt của bạn, giới hạn tần suất
của bạn), hãy gửi email tới fontesmcp@proton.me. Nguồn đó sẽ được sửa hoặc bị tắt.

## Fontes khác gì so với các công cụ nghiên cứu pháp lý trực tuyến (hosted)?

- **Fontes chạy trên máy tính của bạn.** Không có máy chủ Fontes và không có tài khoản. Điều đó cũng có nghĩa là Fontes
  chỉ hoạt động trong các ứng dụng có thể khởi chạy máy chủ MCP cục bộ (Claude Desktop, Codex, Cursor, VS Code
  và tương tự), không hoạt động trong các ứng dụng chỉ chạy trên web vốn chỉ chấp nhận connector được lưu trữ trên máy chủ.
- **Fontes không có cơ sở dữ liệu.** Mỗi lượt tìm kiếm được gửi trực tiếp tới chính trang web hoặc API của bên công bố, nên
  kết quả cập nhật đúng như nguồn, và chất lượng tìm kiếm là chất lượng của chính nguồn đó. Không có tìm kiếm
  ngữ nghĩa trên một chỉ mục được tuyển chọn.
- **Fontes không đặt giới hạn sử dụng.** Fontes không có giới hạn số lượt gọi hằng tháng. Fontes giãn cách các yêu cầu tới từng
  trang web, và một số nguồn giới hạn tốc độ hoặc tần suất truy vấn.
- **Fontes là mã nguồn mở.** Bạn có thể đọc mọi adapter và thấy chính xác mỗi văn bản đến từ đâu.
- **Không có nhà cung cấp nào đứng sau.** Không có hợp đồng, bộ phận hỗ trợ hay cam kết thời gian hoạt động (xem "Ai
  duy trì Fontes?").

## Fontes hoạt động với những ứng dụng và hệ thống nào?

Mọi ứng dụng MCP có thể chạy máy chủ cục bộ (stdio), ví dụ Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio và Cline. Fontes
chạy trên macOS, Windows và Linux, ở bất kỳ đâu uv chạy được (Python 3.13+). Trên máy Mac hoặc PC Windows, một trình cài đặt một lần nhấp thiết lập
Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio và
Cline trong một lần. Các bước cho từng ứng dụng: [INSTALL.md](INSTALL.md).

## Tôi có thể đóng góp mã không?

Hiện tại thì không. Các issue, báo cáo về nguồn và đề xuất phạm vi tài phán đều được hoan nghênh. Xem
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
