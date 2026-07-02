# Mô Phỏng Thuật Toán AI với Bài Toán 15-Puzzle

Ứng dụng desktop viết bằng thư viện Tkinter trực quan hóa các thuật toán tìm kiếm và trí tuệ nhân tạo (AI) kinh điển qua bài toán 15-Puzzle (bảng số 4x4).

## Các nhóm thuật toán hỗ trợ

Dự án chia làm 6 nhóm thuật toán tương ứng với các chủ đề trong môn học Trí tuệ Nhân tạo:

### Nhóm 1: Tìm kiếm mù (Uninformed Search)
Tìm kiếm đường đi trên không gian trạng thái từ điểm bắt đầu đến trạng thái đích mà không dùng hàm đánh giá (heuristic).
* **BFS (Breadth-First Search):** Tìm kiếm theo chiều rộng, tìm ra đường đi ngắn nhất về số bước nhưng tiêu tốn bộ nhớ cho tập biên (frontier).
* **DFS (Depth-First Search):** Tìm kiếm theo chiều sâu bằng Stack. Bộ nhớ sử dụng thấp hơn BFS nhưng không đảm bảo tìm được đường đi ngắn nhất.
* **UCS (Uniform Cost Search):** Tìm kiếm với chi phí đồng nhất bằng Priority Queue, ưu tiên mở rộng trạng thái có chi phí tích lũy thấp nhất.

### Nhóm 2: Tìm kiếm có thông tin (Informed Search)
Sử dụng hàm đánh giá khoảng cách Manhattan (Manhattan distance) từ trạng thái hiện tại tới trạng thái đích để định hướng tìm kiếm.
* **Greedy Search:** Tìm kiếm tham lam, ưu tiên chọn trạng thái có khoảng cách ước lượng đến đích ngắn nhất.
* **A* Search:** Tìm kiếm tối ưu dựa trên tổng chi phí thực tế g(n) và chi phí ước lượng h(n).
* **IDA* (Iterative Deepening A*):** Kết hợp DFS với giới hạn chi phí f(n) tăng dần để tiết kiệm bộ nhớ so với A*.

### Nhóm 3: Tìm kiếm cục bộ (Local Search)
Tìm kiếm lời giải tối ưu bằng cách di chuyển sang các trạng thái lân cận tốt hơn trạng thái hiện tại. Hàm mục tiêu đánh giá dựa trên số ô sai vị trí so với trạng thái đích (Misplaced Tiles).
* **Simple Hill Climbing:** Chọn ngay trạng thái con đầu tiên tốt hơn trạng thái hiện tại. Dễ rơi vào cực trị địa phương (local optima).
* **Steepest-Ascent Hill Climbing:** Đánh giá tất cả các trạng thái con và chọn trạng thái cải tiến tốt nhất.
* **Stochastic Hill Climbing:** Chọn ngẫu nhiên trong số các trạng thái con tốt hơn trạng thái hiện tại.

### Nhóm 4: Môi trường phức tạp (Complex Environments)
Giải quyết bài toán trong điều kiện không xác định hoặc thiếu thông tin quan sát.
* **AND-OR Search:** Tìm kiếm kế hoạch hành động dạng cây khi một hành động có thể dẫn đến các kết quả ngẫu nhiên khác nhau.
* **No Observation:** Tìm kiếm không quan sát, dùng thuật toán tìm kiếm trên không gian tập niềm tin (Belief State) để tìm ra một chuỗi hành động đưa mọi trạng thái khởi đầu khả dĩ về trạng thái đích duy nhất.
* **Partially Observable:** Quan sát một phần, trạng thái bàn cờ bị che khuất và chỉ quan sát được vùng 2x2 ở trung tâm. Thuật toán kết hợp dự báo Belief State và đối chiếu quan sát thực tế sau mỗi bước đi để lọc các trạng thái không phù hợp.

### Nhóm 5: Bài toán thỏa mãn ràng buộc (CSP)
Tìm kiếm một cấu hình bàn cờ 15-Puzzle hợp lệ và có thể giải được (solvable) thỏa mãn các ràng buộc cấu trúc:
* **Các ràng buộc thiết lập:** Các ô số từ 0 đến 15 xuất hiện duy nhất một lần; ô trống nằm ở góc dưới bên phải (V_3_3 = 0); các ô đối xứng qua tâm (trừ ô trống) có tổng bằng 16 (V_r_c + V_(3-r)_(3-c) = 16); trạng thái bàn cờ sinh ra phải giải được (solvable - có số lượng nghịch thế chẵn).
* **Thuật toán áp dụng:** Backtracking Search, Forward Checking và Min-Conflicts.

### Nhóm 6: Tìm kiếm đối kháng (Adversarial Search)
Chế độ chơi đối kháng giữa người (Human) và máy (AI) trên cùng một bảng số 15-Puzzle.
* **Luật chơi:** Người chơi tìm cách trượt các ô số để đưa bảng về trạng thái xuôi (GOAL 1: ô trống nằm cuối). Máy tính tìm cách đưa bảng về trạng thái ngược (GOAL 2: ô trống nằm đầu). Hai bên thay phiên nhau đi tối đa 50 lượt. Kết thúc lượt chơi, bên nào có ít ô sai vị trí hơn so với đích của mình sẽ giành chiến thắng.
* **Thuật toán của AI:** Minimax, Cắt tỉa Alpha-Beta (Alpha-Beta Pruning) và Expectimax.

## Yêu cầu hệ thống

* Python 3.9 trở lên (đã kiểm thử thành công trên Python 3.9 và Python 3.14).
* Ứng dụng chỉ sử dụng các thư viện chuẩn của Python: `tkinter`, `collections`, `heapq`, `random`, `copy`, `itertools`, `time`. Không cần cài thêm thư viện ngoài.
* Trên hệ điều hành Linux, nếu chưa cài đặt thư viện giao diện Tkinter, chạy lệnh:
  ```bash
  sudo apt-get install python3-tk
  ```

## Hướng dẫn chạy chương trình

Khởi chạy ứng dụng từ thư mục chứa mã nguồn bằng lệnh:
```bash
python main.py
```

Sau khi giao diện chính mở lên:
1. Nhấp chọn một trong các nhóm thuật toán ở hàng nút phía trên.
2. Danh sách các thuật toán thuộc nhóm đó sẽ hiện ra ở bảng phía dưới. Nhấp vào thuật toán cần xem để mở cửa sổ mô phỏng riêng.
3. Trong cửa sổ mô phỏng, bạn có thể nhập trạng thái tùy chỉnh hoặc xáo trộn (Shuffle) bàn cờ theo số bước mong muốn, sau đó chạy thuật toán và xem trực quan từng bước chuyển đổi trạng thái.

## Cấu trúc thư mục nguồn

* `main.py`: Điểm khởi chạy chương trình, chứa giao diện điều khiển chính để chọn thuật toán.
* `group1_uninformed.py`: Triển khai các thuật toán tìm kiếm mù (BFS, DFS, UCS) và giao diện trực quan hóa tương ứng.
* `group2_informed.py`: Triển khai các thuật toán tìm kiếm có thông tin (Greedy, A*, IDA*).
* `group3_local.py`: Triển khai các thuật toán tìm kiếm cục bộ (Hill Climbing).
* `group4_complex.py`: Triển khai AND-OR Search, Belief State Search cho trường hợp không quan sát và quan sát một phần.
* `group5_csp.py`: Triển khai các thuật toán CSP (Backtracking, Forward Checking, Min-Conflicts).
* `group6_adversarial.py`: Triển khai trò chơi đối kháng Human vs AI sử dụng Minimax, Alpha-Beta và Expectimax.
* `README.md`: Tài liệu hướng dẫn sử dụng dự án.

