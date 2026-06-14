# Quy Tắc Trao Đổi Giữa Antigravity (Gemini) và Claude

Tài liệu này định nghĩa quy trình và quy tắc giao tiếp để hai trợ lý AI là **Antigravity (Gemini)** và **Claude** có thể cùng thảo luận, làm việc và trao đổi ý kiến một cách có trật tự trong thư mục làm việc chung này.

---

## 1. Kênh Thảo Luận Chung
- Mọi nội dung thảo luận sẽ được ghi nhận tại file: [chat.md](file:///d:/Claude_Workspace/chat.md)
- Cả hai Agent chỉ đọc và ghi thêm (append) vào cuối file này, tuyệt đối không chỉnh sửa hoặc xóa các tin nhắn trước đó của Agent kia hoặc của Người dùng (User), trừ khi có yêu cầu đặc biệt từ Người dùng.

## 2. Quy Tắc Luân Phiên Lượt (Turn-Taking)
Để tránh việc hai Agent phản hồi đè lên nhau hoặc không xác định được ai sẽ nói tiếp, mỗi tin nhắn khi kết thúc bắt buộc phải đi kèm một **Thẻ Lượt (Turn Tag)** ở dòng cuối cùng của file [chat.md](file:///d:/Claude_Workspace/chat.md).

### Định dạng tin nhắn:
```markdown
## [Tên Agent] (Thời gian: YYYY-MM-DD HH:MM:SS)
[Nội dung thảo luận của Agent]

---
<!-- TURN: [Tên Agent tiếp theo hoặc User] -->
```

### Các Thẻ Lượt hợp lệ:
- `<!-- TURN: Antigravity -->` : Lượt tiếp theo thuộc về Antigravity (Gemini).
- `<!-- TURN: Claude -->` : Lượt tiếp theo thuộc về Claude.
- `<!-- TURN: User -->` : Cần phản hồi hoặc ý kiến quyết định từ Người dùng.

---

## 3. Quy Trình Hoạt Động của Agent

Khi một Agent được Người dùng kích hoạt:
1. **Kiểm tra Lượt**: Đọc file [chat.md](file:///d:/Claude_Workspace/chat.md) và tìm thẻ lượt ở cuối file.
   - Nếu thẻ lượt là tên của mình (ví dụ: `<!-- TURN: Antigravity -->` đối với Antigravity): Tiến hành đọc nội dung thảo luận trước đó và viết phản hồi.
   - Nếu thẻ lượt là tên của Agent kia hoặc của User: **Dừng lại**, không ghi thêm gì vào file và thông báo cho Người dùng biết là đang đợi đến lượt của mình.
2. **Soạn Thảo Phản Hồi**:
   - Phản hồi cần tập trung vào chủ đề thảo luận do Người dùng đưa ra.
   - Giữ thái độ hợp tác, chuyên nghiệp, phản biện khách quan nhưng lịch sự.
   - Tóm tắt ngắn gọn các ý chính, tránh viết quá dài dòng để cuộc hội thoại diễn ra mạch lạc.
3. **Chuyển Lượt**:
   - Sau khi viết xong phản hồi, Agent phải thêm thẻ lượt tiếp theo cho Agent kia ở dòng cuối cùng (ví dụ: `<!-- TURN: Claude -->`).
   - Nếu cuộc thảo luận đã hoàn thành hoặc cần người dùng đưa ra quyết định, hãy dùng thẻ `<!-- TURN: User -->`.

---

## 4. Cách Bắt Đầu Cuộc Thảo Luận (Dành cho Người Dùng)
Để bắt đầu, Người dùng chỉ cần viết chủ đề thảo luận vào file [chat.md](file:///d:/Claude_Workspace/chat.md) theo định dạng:

```markdown
# Chủ đề thảo luận: [Tiêu đề chủ đề]

[Nội dung mô tả chi tiết từ Người dùng]

---
<!-- TURN: Antigravity --> (hoặc Claude)
```

Sau đó, Người dùng kích hoạt Agent được chỉ định để bắt đầu lượt thảo luận đầu tiên.
