# heuristic.py


def heuristic(a: tuple, b: tuple) -> int:
    """
    Hàm lượng giá heuristic sử dụng khoảng cách Manhattan.
    Khoảng cách này đặc biệt phù hợp và tối ưu admissible trên lưới dạng ô vuông
    (chỉ di chuyển ngang/dọc) để định hướng thuật toán tìm kiếm về phía mục tiêu.

    Args:
        a: Tọa độ (x, y) của điểm đầu.
        b: Tọa độ (x, y) của điểm đích.

    Returns:
        int: Khoảng cách Manhattan giữa hai điểm.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
