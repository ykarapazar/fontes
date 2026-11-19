> Đây là bản dịch có sự hỗ trợ của máy. Bản tiếng Anh là bản có giá trị quyết định.

# Cài đặt Fontes

Fontes cho phép ứng dụng AI của bạn tra cứu bản án và văn bản quy phạm pháp luật trực tiếp trên các trang web của tòa án
và cơ quan nhà nước ở hơn 120 phạm vi tài phán. Mọi kết quả đều dẫn liên kết tới bản gốc. Đây là một máy chủ MCP chuẩn,
nên hoạt động trong mọi ứng dụng có thể chạy máy chủ MCP cục bộ: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline và các ứng dụng khác.

Hãy chọn ứng dụng của bạn, làm theo các bước, rồi [kiểm tra xem đã hoạt động chưa](#kiểm-tra-xem-đã-hoạt-động-chưa).

## Claude Desktop

1. Tải tệp `.mcpb` của Fontes từ
   [bản phát hành mới nhất](https://github.com/ykarapazar/fontes/releases/latest).
2. Nhấp đúp vào tệp. Claude Desktop sẽ mở tệp.
3. Nhấp **Install**.

## Codex

Trong cửa sổ terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI và tiện ích mở rộng Codex cho IDE dùng chung thiết lập này (`~/.codex/config.toml`).
Bạn cần [uv](#bạn-cần-uv).

## Claude Code

Trong cửa sổ terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Bạn cần [uv](#bạn-cần-uv).

## Các ứng dụng khác

Mỗi ứng dụng sau đây đều cần [uv](#bạn-cần-uv). Thêm mục cấu hình, lưu lại, rồi thoát và mở lại ứng dụng.

**Cursor:** trong `~/.cursor/mcp.json` (mọi dự án) hoặc `.cursor/mcp.json` (một dự án):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** chạy **MCP: Add Server** từ Command Palette, chọn
**Command (stdio)**, nhập `uvx fontes-mcp` và đặt tên máy chủ là `fontes`. Hoặc thêm phần sau vào
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Các thiết lập VS Code cũ hơn dùng `.vscode/mcp.json`, trong đó khóa cấp cao nhất là `servers` thay vì
`mcpServers`.

**Gemini CLI:** trong cửa sổ terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Hoặc thêm phần sau vào
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** mở tệp thiết lập của bạn (**zed: open settings file**) và thêm:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** ở thanh bên phải, mở thẻ **Program**, nhấp **Install → Edit
mcp.json**, và thêm:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** nhấp biểu tượng **MCP Servers**, mở thẻ **Configure**, nhấp **Configure MCP
Servers**, và thêm cùng mục `mcpServers` như với LM Studio.

**Claude Desktop, thủ công** (thay cho tệp `.mcpb`): thêm cùng mục `mcpServers` vào
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Bất kỳ ứng dụng MCP nào khác** (Windsurf và các ứng dụng khác): tài liệu của chính ứng dụng đó cho biết nơi lưu các máy chủ MCP.
Phần lớn dùng cùng một mục cấu hình: lệnh `uvx`, đối số `fontes`.

Nếu ứng dụng không tìm thấy `uvx`, hãy dùng đường dẫn đầy đủ của nó (trên macOS và Linux, `which uvx` sẽ in ra đường dẫn).

## Bạn cần uv

Codex, Claude Code và các ứng dụng khác khởi chạy Fontes bằng `uvx`, đi kèm với **uv**, một công cụ nhỏ
miễn phí của Astral. Để cài đặt, xem
[hướng dẫn của Astral](https://docs.astral.sh/uv/getting-started/installation/), hoặc chạy:

- macOS hoặc Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Khóa

Một số nguồn cần khóa miễn phí: xem [KEYS.md](KEYS.md).

## Kiểm tra xem đã hoạt động chưa

Trong một cuộc trò chuyện mới, hãy hỏi: *"Fontes có thể tìm kiếm ở những phạm vi tài phán nào?"* Ứng dụng sẽ trả lời bằng
một danh sách các quốc gia. Nếu không, hãy thoát và mở lại ứng dụng thêm một lần nữa.

## Trình cài đặt một lần nhấp (Mac và Windows)

Trình cài đặt thiết lập Fontes trong tất cả ứng dụng của bạn cùng lúc: Claude Desktop, Codex, Claude Code,
Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio và Cline.
**Trước khi bắt đầu:** hãy thoát hẳn từng ứng dụng này. Điều này quan trọng nhất với Claude Code:
trong khi chạy, Claude Code ghi lại `~/.claude.json` và có thể hoàn tác thay đổi của trình cài đặt. Nếu bạn không thể
thoát Claude Code, hãy thêm Fontes vào đó bằng `claude mcp add` (xem [Claude Code](#claude-code)).

**Mac**

1. Tải trình cài đặt cho Mac (`Fontes-Installer-…-mac.zip`) từ
   [bản phát hành mới nhất](https://github.com/ykarapazar/fontes/releases/latest) và nhấp đúp vào tệp để giải nén.
2. Nhấp đúp vào **Fontes Installer**. Nếu máy Mac hỏi có mở một ứng dụng tải về từ internet hay không,
   hãy nhấp **Mở**.
3. Chọn **Cài đặt** và nhấp **OK**. Quá trình thiết lập mất khoảng một phút.
4. Một thông báo liệt kê các ứng dụng đã được thiết lập. Nhấp **Xong**, rồi mở lại các ứng dụng đó. Để thêm
   các khóa miễn phí tùy chọn trước, hãy nhấp **Thêm khóa** thay vào đó; xem [Bước thêm khóa](#bước-thêm-khóa).

**Windows**

1. Tải trình cài đặt Windows (`Fontes-Setup-….exe`) từ [bản phát hành mới nhất](https://github.com/ykarapazar/fontes/releases/latest) và nhấp đúp vào tệp.
   - Nếu Windows hiện "Windows protected your PC": nhấp **More info**, rồi **Run anyway**.
2. Nhấp **Install**. Một cửa sổ mở ra và thiết lập Fontes.
3. Khi được hỏi có gửi số liệu sử dụng ẩn danh hay không, nhấn Enter để chọn không.
4. Trình cài đặt hỏi có thêm khóa ngay bây giờ hay không. Nhấn Enter để bỏ qua; xem [Bước thêm khóa](#bước-thêm-khóa).
5. Khi trình cài đặt báo **Done**, hãy mở lại các ứng dụng AI của bạn. Nếu có ứng dụng vẫn đang chạy, hãy đóng hẳn ứng dụng đó
   (kể cả ở khay hệ thống, gần đồng hồ) rồi mở lại.

Cuối cùng, trình cài đặt liệt kê các ứng dụng đã được thiết lập.

### Trình cài đặt thiết lập những ứng dụng nào

Trình cài đặt chỉ thiết lập một ứng dụng nếu thư mục thiết lập của ứng dụng đó đã có trên máy tính của bạn. Claude Code
chỉ được thiết lập nếu `~/.claude.json` tồn tại. Claude Desktop luôn được thiết lập. Mỗi ứng dụng nhận một
mục, `fontes`, trong tệp sau:

| Ứng dụng | Tệp (Mac và Linux) | Tệp (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, và bản sao riêng của phiên bản Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, hoặc `~/.codeium/windsurf/mcp_config.json` ở các phiên bản cũ hơn | `%APPDATA%\devin\mcp_config.json`, hoặc `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code được thiết lập nếu `~/.copilot` hoặc thư mục thiết lập riêng của VS Code tồn tại.

Hai ứng dụng cần thêm một bước:

- **Windsurf:** sau khi mở lại, nhấn làm mới (refresh) trong Cascade.
- **Cline bên trong tiện ích mở rộng VS Code phiên bản cũ:** thêm Fontes thủ công (xem [Cline](#các-ứng-dụng-khác)).

### Bước thêm khóa

Ngay sau khi cài đặt, trình cài đặt đề nghị thêm các khóa miễn phí của Pháp và Hoa Kỳ. Để thêm hoặc
thay đổi chúng sau này:

- **Mac:** mở lại **Fontes Installer** và chọn **Thêm hoặc đổi khóa**.
- **Windows:** mở menu Start, rồi chọn **Fontes** → **Thêm hoặc đổi khóa**.

Nội dung bạn gõ sẽ bị ẩn. Các khóa được đưa vào mọi ứng dụng đã có Fontes. Sau đó hãy thoát và mở lại các ứng dụng.
Nơi lấy khóa và những gì khóa mở ra: [KEYS.md](KEYS.md).

### Bản sao lưu, chạy lại và gỡ bỏ

Trình cài đặt chỉ thay đổi mục `fontes`. Mọi thiết lập và chú thích khác vẫn giữ nguyên.
Trước khi thay đổi một tệp, trình cài đặt lưu một bản sao bên cạnh tệp đó, với tên `<file>.fontes-backup-<date>`. Các bản sao
được tạo sau khi bạn thêm khóa sẽ chứa các khóa đó: hãy xóa những bản bạn không còn cần. Trình cài đặt cũng
cài đặt uv. Chạy lại trình cài đặt là an toàn: nó sửa lại phần thiết lập và không thay đổi gì khác.

Để gỡ Fontes, mở **Fontes Installer** và chọn **Gỡ bỏ** (Mac), hoặc gỡ cài đặt **Fontes** trong Cài đặt → Ứng dụng (Windows). Thao tác này gỡ mục `fontes`, kể cả các khóa, khỏi mọi ứng dụng. Các thiết lập khác của bạn
và các bản sao lưu vẫn được giữ lại.

## Cập nhật

- **Trình cài đặt và tệp `.mcpb`:** bạn không cần làm gì. Mỗi ngày một lần, khi ứng dụng
  khởi động, Fontes kiểm tra phiên bản mới hơn ở chế độ nền và chuẩn bị sẵn; lần tới khi
  ứng dụng khởi động, phiên bản đó sẽ được dùng. Nếu không tải được bản cập nhật hoặc bản cập nhật không hoạt động, Fontes tiếp tục
  dùng phiên bản đã hoạt động.
- **`uvx`:** Fontes báo cho bạn khi có phiên bản mới hơn, ở đầu danh sách các phạm vi
  tài phán. Để luôn chạy phiên bản mới nhất, hãy dùng `fontes-mcp@latest` thay cho `fontes-mcp`.

Việc này không gửi bất kỳ thông tin nào về bạn hay các tìm kiếm của bạn tới bất kỳ đâu.

## Quyền riêng tư

Theo mặc định, Fontes không gửi gì về bạn hay các tìm kiếm của bạn. Số liệu sử dụng chỉ được gửi khi bạn chọn tham gia, và một báo cáo
lỗi chỉ được gửi sau khi bạn xem và xác nhận. Chi tiết: [PRIVACY.md](PRIVACY.md).

## Gỡ bỏ Fontes

Xóa mục `fontes` khỏi thiết lập MCP của ứng dụng (trong Claude Code:
`claude mcp remove fontes`), rồi thoát và mở lại ứng dụng.

## Điều nên biết

Fontes đọc các nguồn công khai, chủ yếu là trang web của tòa án và cơ quan nhà nước. Fontes đánh dấu các nguồn không chính thức trong
câu trả lời. Luôn mở liên kết nguồn trước khi dựa vào một bản án hoặc một điều khoản.

Nếu có sự cố, hãy gửi email mô tả những gì bạn đã làm và thông báo lỗi bạn thấy tới fontesmcp@proton.me.

## Trước khi bạn dựa vào Fontes

- Fontes là công cụ nghiên cứu, không phải tư vấn pháp lý. Việc sử dụng Fontes không khiến bất kỳ ai trở thành luật sư của bạn.
- Fontes được cung cấp "nguyên trạng", không có bảo đảm, và các tác giả không chịu trách nhiệm về cách Fontes được sử dụng,
  trong phạm vi pháp luật cho phép. Toàn bộ điều khoản nằm trong [giấy phép](../../../LICENSE) (Apache 2.0).
