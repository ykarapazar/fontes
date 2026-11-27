> Đây là bản dịch có sự hỗ trợ của máy. Bản tiếng Anh là bản có giá trị quyết định.

# Thông báo về quyền riêng tư của Fontes

Fontes chạy trên máy tính của bạn. Các tìm kiếm của bạn và các tài liệu bạn mở chỉ ở giữa
máy tính của bạn, các nguồn bạn tìm kiếm (các nguồn chính thức, cùng CourtListener và Lexifina khi bạn dùng chúng, xem bên dưới), và ứng dụng AI bạn dùng (theo điều khoản riêng của
ứng dụng đó). Bản thân Fontes **theo mặc định không gửi gì** cho các nhà phát triển Fontes.

## Những gì có thể rời khỏi máy tính của bạn, và khi nào

**1. Kiểm tra cập nhật (bật theo mặc định).** Mỗi ngày một lần, Fontes hỏi PyPI, kho gói Python
công khai, phiên bản nào là mới nhất. Yêu cầu này không mang thông tin gì về bạn hay công việc của bạn; PyPI
thấy địa chỉ IP của bạn, như với mọi lượt tải xuống. Để tắt, hãy đặt `FONTES_NO_UPDATE_CHECK=1`
(thông báo trong ứng dụng) và `FONTES_NO_AUTO_UPDATE=1` (cập nhật tự động của trình cài đặt).

**2. Số liệu sử dụng (tắt trừ khi bạn bật).** Nếu bạn chọn tham gia, mỗi ngày một lần Fontes gửi:

- phiên bản Fontes và họ hệ điều hành của bạn (macOS, Windows, Linux);
- theo từng ngày, mỗi công cụ đã được dùng bao nhiêu lần cho mỗi mã phạm vi tài phán, ví dụ
  "2026-11-10, nl, search_caselaw, 12".

Đó là toàn bộ nội dung. Nội dung này không bao giờ bao gồm các tìm kiếm của bạn, mã tài liệu hay mã vụ việc, nội dung
tài liệu, tên của bạn, tài khoản, hay bất kỳ mã định danh nào của bạn hoặc máy tính của bạn. Số liệu được lưu chờ trên máy tính của bạn
(trong thư mục bộ nhớ đệm của Fontes, `stats.json`) cho đến khi được gửi; nếu gửi không thành công, chúng chờ tới
ngày hôm sau.

- **Chọn tham gia**: trả lời "y" khi trình cài đặt hỏi, hoặc đặt `FONTES_STATS=1` cho máy chủ Fontes.
- **Chọn không tham gia**: chạy lại trình cài đặt và nhấn Enter ở câu hỏi đó, hoặc xóa
  `FONTES_STATS`. Xóa `stats.json` sẽ hủy mọi số liệu chưa được gửi.

**3. Báo cáo lỗi (chỉ khi bạn gửi).** Khi bạn yêu cầu một báo cáo (`fontes report-bug`, hoặc đề nghị
ứng dụng AI của bạn báo cáo một lỗi của Fontes), Fontes cho bạn xem toàn bộ báo cáo trước và chỉ gửi nếu
bạn xác nhận. Báo cáo gồm phiên bản Fontes, họ hệ điều hành của bạn, mã phạm vi tài phán, tên công cụ và
thông báo lỗi của lệnh gọi công cụ thất bại gần nhất (đã loại bỏ từ khóa tìm kiếm và các mã định danh của bạn), và
một ghi chú nếu bạn viết. Không đưa thông tin về khách hàng vào ghi chú. Để hỗ trợ việc này, Fontes lưu
lỗi gần nhất trên máy tính của bạn (`last-error.json` trong thư mục bộ nhớ đệm, được thay thế mỗi lần);
tệp này không bao giờ được gửi riêng.

**4. Lexifina (bật theo mặc định).** `get_law_on_date`, `get_law_history`, 91 quốc gia và các Acts của Ấn Độ được đọc qua hồ sơ pháp luật của Lexifina, nên được gửi tới Lexifina cùng với hoặc thay cho trang chính thức. Từ khóa tìm kiếm, trích dẫn và ngày tháng của bạn được gửi tới máy chủ miễn phí của Lexifina, `global-law.lexifina.com`. Máy chủ này do Lexifina vận hành, không phải do các nhà phát triển Fontes vận hành. Lexifina ghi trong tài liệu rằng máy chủ của họ ghi lại tên công cụ được gọi và thời gian chạy, không bao giờ ghi nội dung được hỏi; Fontes không thể kiểm chứng điều này, và điều khoản riêng của Lexifina được áp dụng. Lexifina thấy địa chỉ IP của bạn, như mọi máy chủ web. Để tắt hẳn Lexifina, đặt `WLM_LEXIFINA=0`; khi đó hai công cụ và các quốc gia nói trên ngừng hoạt động và không có gì được gửi tới đó.

## Dữ liệu được gửi tới đâu và được lưu giữ bao lâu

Số liệu sử dụng và báo cáo lỗi được gửi tới một máy chủ nhỏ do nhà phát triển Fontes vận hành
(`relay.kinetra.fit`). Máy chủ này không lưu địa chỉ IP: địa chỉ IP chỉ được dùng trong bộ nhớ, trong thời gian ngắn, để
ngăn chặn lưu lượng tràn ngập, và máy chủ web không lưu nhật ký truy cập cho dịch vụ này. Số liệu được cộng dồn vào tổng số
hằng ngày; từng lượt gửi riêng lẻ không được lưu giữ. Tổng số được lưu giữ tối đa 2 năm, báo cáo lỗi tối đa
1 năm, sau đó bị xóa. Không có gì được bán hay chia sẻ.

Nếu không kết nối được tới máy chủ đó, sẽ không có gì được gửi: số liệu vẫn nằm trên máy tính của bạn và báo cáo lỗi
sẽ hướng bạn tới hệ thống theo dõi vấn đề (issue tracker) thay thế.

## Ai chịu trách nhiệm, và trên cơ sở nào

Bên kiểm soát dữ liệu đối với số liệu sử dụng và báo cáo lỗi là Yüce Karapazar, nhà phát triển
Fontes. Liên hệ: fontesmcp@proton.me.

Cơ sở pháp lý là sự đồng ý của bạn (Điều 6(1)(a) của UK GDPR và EU GDPR). Số liệu sử dụng
chỉ được gửi nếu bạn chọn tham gia, và một báo cáo lỗi chỉ được gửi sau khi bạn xác nhận. Bạn có thể rút lại
sự đồng ý bất cứ lúc nào bằng cách chọn không tham gia như mô tả ở trên; việc này không ảnh hưởng tới những gì đã được gửi
trước đó.

## Liên hệ

Câu hỏi hoặc yêu cầu: gửi email tới fontesmcp@proton.me, hoặc mở một issue tại
<https://github.com/ykarapazar/fontes/issues>.
