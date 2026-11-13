# NotebookLM Prompt Templates

Dùng các prompt này trong NotebookLM chat sau khi upload PDF sách.

---

## Template 1 — Extract Core Concepts

```
Hãy liệt kê 5 khái niệm khoa học quan trọng nhất trong tài liệu này.
Với mỗi khái niệm hãy cung cấp:
1. Giải thích đơn giản cho học sinh lớp 10 (không dùng công thức toán học)
2. Một ví dụ thực tế trong cuộc sống hàng ngày
3. Hiểu lầm phổ biến nhất mà người học thường mắc phải

Format đầu ra: danh sách có đánh số, mỗi khái niệm có 3 mục con rõ ràng.
```

---

## Template 2 — Find the Discovery Moment

```
Trong tài liệu này, thí nghiệm hoặc phát hiện nào gây bất ngờ nhất?
Hãy mô tả:
- Tên thí nghiệm / phát hiện
- Ai thực hiện và khi nào
- Điều gì xảy ra (kết quả cụ thể)
- Tại sao nó bất ngờ so với suy nghĩ thông thường
- Ứng dụng của phát hiện này trong cuộc sống hiện đại

Ưu tiên những thí nghiệm có thể mô tả bằng hình ảnh đơn giản, không cần thiết bị phức tạp.
```

---

## Template 3 — Extract Misconceptions

```
Hiểu lầm phổ biến nhất về chủ đề trong tài liệu này là gì?
Hãy liệt kê 2-3 hiểu lầm, mỗi cái bao gồm:
- Điều người ta thường nghĩ sai
- Tại sao điều đó có vẻ hợp lý (tại sao lại dễ nhầm)
- Sự thật đúng là gì
- Cách đơn giản nhất để chứng minh / giải thích sự thật đó

Đây sẽ là xung đột trung tâm của bộ phim — cần chọn hiểu lầm nào thú vị và trực quan nhất.
```

---

## Template 4 — Export Brief for Claude

Sau khi có đủ thông tin từ 3 template trên, dùng prompt này để tổng hợp:

```
Hãy tổng hợp các thông tin trên thành một story brief theo format YAML sau:

topic: "[tên chủ đề]"
source_book: "[tên sách]"
concepts:
  - "[khái niệm 1]"
  - "[khái niệm 2]"
  - "[khái niệm 3]"
  - "[khái niệm 4]"
  - "[khái niệm 5]"
discovery_moment: "[mô tả thí nghiệm / phát hiện bất ngờ nhất — 1-2 câu]"
common_misconception: "[hiểu lầm phổ biến nhất — 1-2 câu]"
real_world_examples:
  - "[ví dụ 1]"
  - "[ví dụ 2]"
  - "[ví dụ 3]"

Chỉ trả về YAML, không thêm text khác.
```

Paste output này vào Claude với skill `science-story` để bắt đầu Stage 2.
