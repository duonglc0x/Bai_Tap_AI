# environment.py
import random

# Kích thước lưới mặc định nếu không truyền tham số
GRID_SIZE = 20


class Environment:
    """
    Lớp Môi trường (Environment) chịu trách nhiệm quản lý không gian lưới 2D (Grid) ảo.
    Nó là đại diện cho bản đồ thành phố nơi Police truy đuổi và Thief bỏ trốn.
    Lớp này lưu trữ và quản lý cấu trúc liên kết của các chướng ngại vật (tường/vật cản cứng)
    và các khu vực đặc biệt (vùng địa hình khó di chuyển), đồng thời cung cấp các API để các thuật toán
    tìm kiếm đường đi có thể truy vấn thông tin lân cận (neighbors) và chi phí di chuyển (cost) tại mỗi tọa độ.
    """
    def __init__(self, width=None, height=None):
        self.width = width if width else GRID_SIZE
        self.height = height if height else GRID_SIZE

        # Ma trận không gian grid được biểu diễn dưới dạng mảng 2 chiều.
        # Quy ước giá trị của lưới:
        # 0: Đường trống (có thể đi qua an toàn, chi phí tiêu chuẩn).
        # 1: Tường/Vật cản cứng (không thể đi qua, thuật toán tìm đường phải né tránh hoàn toàn).
        # 2: Vùng địa hình khó (vũng bùn, ngõ hẹp... có thể đi qua nhưng chịu phạt chi phí cao, cost = 5).
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        # Vị trí xuất phát mặc định của hai nhân vật
        self.police_start = (self.width // 2, self.height // 2)
        self.thief_start = (0, 0)

    def generate_terrains(self, num_walls: int, num_rough: int, avoid_positions: list):
        """
        Khởi tạo ngẫu nhiên cấu hình địa hình trên lưới bản đồ.
        Đảm bảo tính toàn vẹn của trò chơi bằng cách không sinh vật cản đè lên
        các tọa độ nhạy cảm đã được bảo lưu (avoid_positions) như vị trí xuất phát của Police hoặc Thief.
        """
        avoid = set(avoid_positions)

        # Phân bổ các bức tường (vật cản tuyệt đối/cứng)
        placed_walls = 0
        while placed_walls < num_walls:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            # Kiểm tra tránh ghi đè lên các ô đã có địa hình hoặc vị trí cấm
            if (x, y) not in avoid and self.grid[y][x] == 0:
                self.grid[y][x] = 1
                placed_walls += 1

        # Phân bổ các vùng địa hình khó (vật cản tương đối/vùng chi phí cao)
        placed_rough = 0
        while placed_rough < num_rough:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (x, y) not in avoid and self.grid[y][x] == 0:
                self.grid[y][x] = 2
                placed_rough += 1

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """
        Trích xuất danh sách các node lân cận hợp lệ từ một tọa độ (x, y) cho trước.
        Chỉ cho phép di chuyển theo 4 hướng trực giao (Von Neumann neighborhood): Lên, Xuống, Trái, Phải.
        Hàm này là cốt lõi cho chức năng mở rộng nút (node expansion) trong mọi thuật toán tìm kiếm.
        Tự động loại bỏ các node lân cận nằm ngoài biên của ma trận (out of bounds) hoặc bị chặn bởi tường (giá trị = 1).
        """
        neighbors = []
        # Các vector chỉ hướng tương ứng với: [Phải, Dưới, Trái, Trên]
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            # Ràng buộc biên và ràng buộc vật lý
            if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] != 1:
                neighbors.append((nx, ny))
        return neighbors

    def get_cost(self, x: int, y: int) -> int:
        """
        Truy vấn chi phí di chuyển (g-cost) để tiến vào một tọa độ cụ thể.
        Được sử dụng bởi các thuật toán tìm kiếm có thông tin (Informed Search) như A*
        để ưu tiên các tuyến đường an toàn và tối ưu chi phí.

        Trả về:
            5: Nếu tọa độ là vùng địa hình khó (vũng bùn, ngõ hẹp...).
            1: Nếu tọa độ là không gian bình thường.
        """
        if self.grid[y][x] == 2:
            return 5
        return 1
