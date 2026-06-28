import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
from base_algorithm import BaseAlgorithm, State
from heuristic import heuristic

class Minimax(BaseAlgorithm):
    """
    Thuật toán Đối kháng Minimax.
    Được xây dựng cho trò chơi zero-sum có tổng lợi ích bằng 0. 
    Hệ thống SAM-2 đóng vai trò MAX (cố gắng tối đa hóa điểm số, tức là áp sát để tiêu diệt mục tiêu).
    Hệ máy bay B-52 đóng vai trò MIN (cố gắng giảm thiểu điểm số của MAX, tức là bay tránh ra xa).
    """
    def run_adversarial(self, environment, start, initial_target):
        history = []
        sam_pos = start
        b52_pos = initial_target
        current_path = [sam_pos]
        
        def minimax(s_pos, b_pos, depth, is_max):
            """
            Hàm đệ quy phân tích cây trò chơi Minimax.
            Khám phá luân phiên giữa lượt đi của SAM và lượt phản ứng của B-52.
            """
            # Trạng thái kết thúc: Duyệt tới độ sâu tối đa hoặc mục tiêu bị tiêu diệt
            if depth == 0 or s_pos == b_pos:
                # Điểm số đánh giá là nghịch đảo của khoảng cách. Khoảng cách càng ngắn, SAM càng có lợi (giá trị càng lớn)
                return -heuristic(s_pos, b_pos), None
                
            if is_max:
                best_val = -float('inf')
                best_moves = [s_pos]
                for move in environment.get_neighbors(s_pos[0], s_pos[1]):
                    # MAX gọi MIN (Đến lượt B-52 chạy)
                    val, _ = minimax(move, b_pos, depth - 1, False)
                    if val > best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)
                return best_val, random.choice(best_moves)
            else:
                best_val = float('inf')
                best_moves = [b_pos]
                for move in environment.get_neighbors(b_pos[0], b_pos[1]):
                    # MIN gọi MAX (Đến lượt SAM đi)
                    val, _ = minimax(s_pos, move, depth - 1, True)
                    if val < best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)
                return best_val, random.choice(best_moves)

        step = 0
        while sam_pos != b52_pos and step < 100:
            # Bước 1: Lượt của SAM-2 (Đóng vai trò MAX - tối đa hóa điểm số)
            _, best_sam_move = minimax(sam_pos, b52_pos, depth=3, is_max=True)
            sam_pos = best_sam_move
            current_path.append(sam_pos)
            
            history.append(State(
                frontier=[b52_pos], 
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={"Current Algorithm": "Minimax", "Turn": "SAM-2", "Distance": str(heuristic(sam_pos, b52_pos))},
                action_description=f"SAM-2 đi tới {sam_pos}. Đang dùng Minimax (depth=3) đuổi theo B-52 tại {b52_pos}."
            ))
            
            if sam_pos == b52_pos:
                break
                
            # Bước 2: Lượt của B-52 (Đóng vai trò MIN - cực tiểu hóa điểm số của SAM-2)
            _, best_b52_move = minimax(sam_pos, b52_pos, depth=3, is_max=False)
            b52_pos = best_b52_move
            
            history.append(State(
                frontier=[b52_pos],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={"Current Algorithm": "Minimax", "Turn": "B-52", "Distance": str(heuristic(sam_pos, b52_pos))},
                action_description=f"B-52 né tránh sang {b52_pos}. Khoảng cách hiện tại: {heuristic(sam_pos, b52_pos)}."
            ))
            step += 1
            
        history.append(State(
            frontier=[],
            explored=set(current_path),
            current_path=list(current_path),
            hud_metrics={"Current Algorithm": "Minimax", "Status": "Game Over"},
            action_description="Trò chơi kết thúc! SAM-2 đã tiêu diệt B-52." if sam_pos == b52_pos else "B-52 đã trốn thoát!"
        ))
        return history

class AlphaBeta(BaseAlgorithm):
    """
    Thuật toán Tỉa nhánh Alpha-Beta (Alpha-Beta Pruning).
    Là phiên bản tối ưu của Minimax. Nó duy trì 2 biến `alpha` và `beta` để theo dõi những giá trị xấu nhất
    mà MAX và MIN chắc chắn sẽ phải nhận. Nếu nhận thấy có một nhánh nào đó dẫn đến một kết quả "chắc chắn tệ hơn"
    những phương án đã tìm được, nó sẽ từ chối duyệt sâu xuống nhánh đó để tiết kiệm tài nguyên.

    Police đóng vai trò MAX (tối đa hóa điểm số — áp sát để bắt Thief).
    Thief đóng vai trò MIN (cực tiểu hóa điểm số của MAX — chạy trốn càng xa càng tốt).
    """
    def run(self, environment, start: tuple, target: tuple):
        return self.run_adversarial(environment, start, target)

    def run_adversarial(self, environment, start: tuple, initial_target: tuple):
        history = []
        police_pos = start
        thief_pos = initial_target
        current_path = [police_pos]

        def alphabeta(p_pos, t_pos, depth, alpha, beta, is_max):
            """
            Hàm đệ quy phân tích cây trò chơi với kỹ thuật tỉa nhánh Alpha-Beta.
            Khám phá luân phiên giữa lượt đi của Police (MAX) và lượt phản ứng của Thief (MIN).
            """
            # Trạng thái kết thúc: Duyệt tới độ sâu tối đa hoặc Police đã bắt được Thief
            if depth == 0 or p_pos == t_pos:
                # Điểm số đánh giá là nghịch đảo khoảng cách. Khoảng cách càng ngắn, Police càng có lợi.
                return -heuristic(p_pos, t_pos), None

            if is_max:
                best_val = -float('inf')
                best_moves = [p_pos]
                for move in environment.get_neighbors(p_pos[0], p_pos[1]):
                    # MAX gọi MIN (đến lượt Thief chạy trốn)
                    val, _ = alphabeta(move, t_pos, depth - 1, alpha, beta, False)
                    if val > best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)

                    # Cập nhật chặn dưới của MAX
                    alpha = max(alpha, best_val)

                    # Beta cut-off: Nhánh này đã đưa cho MAX một giá trị quá lớn,
                    # do đó MIN ở nút cha chắc chắn sẽ không bao giờ để MAX đi vào nhánh này.
                    # Ngừng quét!
                    if beta <= alpha:
                        break
                return best_val, random.choice(best_moves)
            else:
                best_val = float('inf')
                best_moves = [t_pos]
                for move in environment.get_neighbors(t_pos[0], t_pos[1]):
                    # MIN gọi MAX (đến lượt Police truy đuổi)
                    val, _ = alphabeta(p_pos, move, depth - 1, alpha, beta, True)
                    if val < best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)

                    # Cập nhật chặn trên của MIN
                    beta = min(beta, best_val)

                    # Alpha cut-off: Nhánh này đã dồn MIN tới giá trị tồi tệ,
                    # do đó MAX ở nút cha chắc chắn sẽ không bao giờ chọn con đường đến đây.
                    # Ngừng quét!
                    if beta <= alpha:
                        break
                return best_val, random.choice(best_moves)

        step = 0
        while police_pos != thief_pos and step < 100:
            # Bước 1: Lượt của Police (đóng vai trò MAX — tối đa hóa điểm số)
            _, best_police_move = alphabeta(police_pos, thief_pos, 3, -float('inf'), float('inf'), True)
            police_pos = best_police_move
            current_path.append(police_pos)

            history.append(State(
                frontier=[thief_pos],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={
                    "Current Algorithm": "Alpha-Beta Pruning",
                    "Turn": "Police",
                    "Distance": str(heuristic(police_pos, thief_pos))
                },
                action_description=f"Police đi tới {police_pos}. Dùng Alpha-Beta (depth=3) với bộ tỉa nhanh hơn."
            ))

            if police_pos == thief_pos:
                break

            # Bước 2: Lượt của Thief (đóng vai trò MIN — cực tiểu hóa điểm số của Police)
            _, best_thief_move = alphabeta(police_pos, thief_pos, 3, -float('inf'), float('inf'), False)
            thief_pos = best_thief_move

            history.append(State(
                frontier=[thief_pos],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={
                    "Current Algorithm": "Alpha-Beta Pruning",
                    "Turn": "Thief",
                    "Distance": str(heuristic(police_pos, thief_pos))
                },
                action_description=f"Thief né tránh khôn ngoan sang {thief_pos}."
            ))
            step += 1

        history.append(State(
            frontier=[],
            explored=set(current_path),
            current_path=list(current_path),
            hud_metrics={"Current Algorithm": "Alpha-Beta Pruning", "Status": "Game Over"},
            action_description="Trò chơi kết thúc! Police đã bắt được Thief." if police_pos == thief_pos else "Thief đã trốn thoát!"
        ))
        return history
        
class Expectimax(BaseAlgorithm):
    """
    Thuật toán Expectimax.
    Áp dụng cho môi trường có yếu tố ngẫu nhiên (hoặc đối thủ di chuyển hoàn toàn phi lý trí).
    Không giống như Minimax (giả định đối thủ luôn đưa ra lựa chọn thông minh nhất gây bất lợi cho ta),
    trong Expectimax, nút MIN được thay thế bằng nút CHANCE (Môi trường/Sự kiện ngẫu nhiên).
    Kết quả trả về không phải điểm tối thiểu mà là trung bình có trọng số của mọi khả năng.

    Police đóng vai trò MAX (dự đoán bằng mô hình kỳ vọng).
    Thief di chuyển hoàn toàn ngẫu nhiên (Chance Node) do hoảng loạn.
    """
    def run(self, environment, start: tuple, target: tuple):
        return self.run_adversarial(environment, start, target)

    def run_adversarial(self, environment, start: tuple, initial_target: tuple):
        history = []
        police_pos = start
        thief_pos = initial_target
        current_path = [police_pos]

        def expectimax(p_pos, t_pos, depth, is_max):
            """
            Hàm đệ quy phân tích cây Expectimax.
            Nút MAX đại diện cho lượt chọn hành động tối ưu của Police.
            Nút Chance đại diện cho lượt di chuyển ngẫu nhiên của Thief.
            """
            # Trạng thái kết thúc: Duyệt tới độ sâu tối đa hoặc Police đã bắt được Thief
            if depth == 0 or p_pos == t_pos:
                return -heuristic(p_pos, t_pos), None

            if is_max:
                best_val = -float('inf')
                best_moves = [p_pos]
                for move in environment.get_neighbors(p_pos[0], p_pos[1]):
                    # MAX gọi Chance (đến lượt Thief di chuyển ngẫu nhiên)
                    val, _ = expectimax(move, t_pos, depth - 1, False)
                    if val > best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)
                return best_val, random.choice(best_moves)
            else:
                # Nút Chance: Tính toán Giá trị Kỳ vọng (Expected Value) bằng trung bình cộng
                # (Vì mô phỏng tỷ lệ phần trăm xảy ra sự kiện là đồng đều giữa các lân cận).
                moves = environment.get_neighbors(t_pos[0], t_pos[1])
                if not moves:
                    return -heuristic(p_pos, t_pos), t_pos
                avg_val = 0
                for move in moves:
                    val, _ = expectimax(p_pos, move, depth - 1, True)
                    avg_val += val
                return avg_val / len(moves), None

        step = 0
        while police_pos != thief_pos and step < 100:
            # Lượt của Police (giả định rằng Thief sẽ chạy loạn xạ, không có chiến thuật)
            _, best_police_move = expectimax(police_pos, thief_pos, depth=3, is_max=True)
            police_pos = best_police_move
            current_path.append(police_pos)

            history.append(State(
                frontier=[thief_pos],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={
                    "Current Algorithm": "Expectimax",
                    "Turn": "Police",
                    "Distance": str(heuristic(police_pos, thief_pos))
                },
                action_description=f"Police đi tới {police_pos}. Đang dùng mô hình kỳ vọng (Expectimax) dự đoán."
            ))

            if police_pos == thief_pos:
                break

            # Lượt của Thief: di chuyển hoàn toàn ngẫu nhiên do hoảng loạn
            thief_pos = random.choice(environment.get_neighbors(thief_pos[0], thief_pos[1]))

            history.append(State(
                frontier=[thief_pos],
                explored=set(current_path),
                current_path=list(current_path),
                hud_metrics={
                    "Current Algorithm": "Expectimax",
                    "Turn": "Thief",
                    "Distance": str(heuristic(police_pos, thief_pos))
                },
                action_description=f"Thief di chuyển ngẫu nhiên (Chance Node) sang {thief_pos}."
            ))
            step += 1

        history.append(State(
            frontier=[],
            explored=set(current_path),
            current_path=list(current_path),
            hud_metrics={"Current Algorithm": "Expectimax", "Status": "Game Over"},
            action_description="Trò chơi kết thúc! Police đã bắt được Thief." if police_pos == thief_pos else "Thief đã trốn thoát!"
        ))
        return history
