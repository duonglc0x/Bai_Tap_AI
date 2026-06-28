# Hệ Thống Mô Phỏng Thuật Toán AI - Giải Bài Toán 15-Puzzle

Dự án này là một ứng dụng mô phỏng trực quan các thuật toán Trí tuệ Nhân tạo (AI) để giải quyết trò chơi ô số trượt **15-Puzzle**. Ứng dụng cung cấp giao diện đồ họa trực quan (GUI) được viết bằng thư viện Tkinter của Python, giúp người dùng theo dõi chi tiết từng bước tìm kiếm, các lựa chọn nhánh (node con), danh sách các trạng thái đã đi qua và giải thích thuật toán tương ứng.

---

## 1. Ý tưởng và Mô hình hóa Thuật toán

Dưới đây là mô tả chi tiết về cách mô hình hóa bài toán 15-Puzzle đối với hai nhóm thuật toán chính trong hệ thống:

### NHÓM 1: TÌM KIẾM KHÔNG CÓ THÔNG TIN (UNINFORMED SEARCH)

*   **Không gian trạng thái (State Space):** Tập hợp tất cả các cấu hình vị trí của 15 ô số và 1 ô trống trên bảng kích thước $4 \times 4$.
*   **Trạng thái đầu (Initial State):** Cấu hình bàn cờ ban đầu do hệ thống sinh ra hoặc do người dùng tự nhập thủ công.
*   **Trạng thái đích (Goal State):** Ô trống nằm ở góc dưới cùng bên phải, các ô từ 1 đến 15 được xếp thứ tự tăng dần từ trái qua phải, từ trên xuống dưới.
*   **Hành động (Actions):** Di chuyển ô trống sang các hướng $\{\text{Lên, Xuống, Trái, Phải}\}$ (tương đương với việc trượt ô số lân cận theo hướng ngược lại $\{\text{Xuống, Lên, Phải, Trái}\}$).

#### 3 Thuật toán chính:

| Thuật toán | Mô tả hoạt động |
| :--- | :--- |
| **BFS (Breadth-First Search)** | Sử dụng hàng đợi **Queue (FIFO)** để quản lý biên (Frontier). Duyệt qua tất cả các trạng thái ở độ sâu hiện tại trước khi xuống sâu hơn. Đảm bảo tìm ra đường đi ngắn nhất (tối ưu). |
| **DFS (Depth-First Search)** | Sử dụng ngăn xếp **Stack (LIFO)**. Đi sâu nhất có thể trên một nhánh trước khi quay lui. Bản mô phỏng sử dụng tìm kiếm sâu dần **IDDFS** (Iterative Deepening DFS) để khắc phục nhược điểm nhánh vô hạn của DFS truyền thống và đảm bảo tìm ra đường đi ngắn nhất. |
| **UCS (Uniform Cost Search)** | Sử dụng hàng đợi ưu tiên **Priority Queue** sắp xếp các trạng thái dựa trên chi phí đường đi $g(n)$. Với bài toán 15-Puzzle có chi phí mỗi bước đi bằng 1, UCS hoạt động tương đương BFS nhưng chuẩn hóa và tổng quát hóa tốt hơn. |

---

### NHÓM 5: THỎA MÃN RÀNG BUỘC (CSP - CONSTRAINT SATISFACTION PROBLEM)

Thay vì tìm kiếm đường đi thông thường, bài toán 15-Puzzle được chuyển đổi và mô hình hóa dưới dạng một bài toán thỏa mãn ràng buộc:
*   **Biến (Variables):** Chuỗi các quyết định di chuyển liên tiếp $X_1, X_2, \dots, X_n$ từ trạng thái ban đầu đến đích.
*   **Miền giá trị (Domains):** Các hướng di chuyển hợp lệ của ô trống tại mỗi bước $\{\text{Lên, Xuống, Trái, Phải}\}$ (biểu diễn trực quan bằng hướng trượt của ô số tương ứng $\{\uparrow, \downarrow, \leftarrow, \rightarrow\}$).
*   **Ràng buộc (Constraints):** Trạng thái bàn cờ sau mỗi bước gán giá trị cho biến $X_i$ không được phép trùng lặp với bất kỳ trạng thái nào trước đó trên đường đi hiện tại nhằm đảm bảo tính phi chu trình (no-loop constraint).

#### 3 Thuật toán chính:

| Thuật toán | Mô tả hoạt động |
| :--- | :--- |
| **Backtracking Search** | Thử gán hướng đi cho biến hiện tại, nếu vi phạm ràng buộc (lặp trạng thái) thì quay lui. Miền giá trị được sắp xếp theo Heuristic khoảng cách Manhattan để tối ưu hóa thứ tự thử nghiệm giá trị. |
| **Forward Checking (FC)** | Tương tự Backtracking kết hợp nhìn trước (look-ahead): Tại mỗi bước đi, thuật toán kiểm tra trước miền giá trị của bước tiếp theo. Nếu bước tiếp theo không còn hướng đi nào hợp lệ (miền giá trị tương lai bị rỗng), thuật toán thực hiện **cắt nhánh sớm** ngay lập tức. |
| **Min-Conflicts** | Thuật toán tìm kiếm cục bộ cho CSP. Định nghĩa số xung đột (conflicts) là số ô số bị đặt sai vị trí so với trạng thái đích. Tại mỗi bước lặp, thuật toán chọn hướng di chuyển giúp làm giảm số lượng ô sai vị trí nhiều nhất để nhanh chóng hội tụ về đích. |

---

## 2. Hướng dẫn chạy chương trình

1.  **Yêu cầu hệ thống:** Python phiên bản 3.x trở lên.
2.  **Chạy ứng dụng:**
    ```bash
    python main.py
    ```
3.  **Cách sử dụng trên GUI:**
    *   Nhấp vào nút nhóm thuật toán mong muốn (Nhóm 1 hoặc Nhóm 5).
    *   Chọn một trong ba thuật toán hiển thị ở góc trên bên phải.
    *   Sử dụng nút **"📝 Nhập tay"** để thiết lập trạng thái 15-puzzle ban đầu (hệ thống sẽ tự động kiểm tra xem trạng thái đó có giải được hay không trước khi chấp nhận).
    *   Nhấp **"▶ Giải"** để chạy thuật toán tìm kiếm lời giải.
    *   Sau khi giải xong, sử dụng các nút điều hướng **"◀◀ Bước trước"**, **"Bước sau ▶▶"** hoặc nhấn **"▶ Tự chạy"** để xem mô phỏng chuyển động từng bước của ô số mà không bị nhảy cóc.
