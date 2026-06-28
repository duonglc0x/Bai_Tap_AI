import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import heapq
from base_algorithm import BaseAlgorithm, State
from heuristic import heuristic


class GreedySearch(BaseAlgorithm):
    """
    Thuật toán Tìm kiếm Tham lam (Greedy Best-First Search).
    Thuật toán này chỉ xem xét chi phí ước tính h(n) từ nút hiện tại đến đích để quyết định nút tiếp theo.
    Police luôn chọn bước đi trông có vẻ gần Thief nhất — nhanh nhưng không đảm bảo đường đi là tối ưu nhất.
    """
    def run(self, environment, start: tuple, target: tuple):
        history = []

        # Hàng đợi ưu tiên (Priority Queue) sẽ luôn bật ra phần tử có giá trị h(n) thấp nhất trước tiên.
        pq = [(heuristic(start, target), [start])]
        explored = set([start])

        while pq:
            h_cost, path = heapq.heappop(pq)
            node = path[-1]

            history.append(State(
                frontier=[p[-1] for _, p in pq],
                explored=explored.copy(),
                current_path=path,
                hud_metrics={
                    "Current Algorithm": "Greedy Search",
                    "h(n)": f"{h_cost:.1f}",
                    "Nodes Explored": str(len(explored))
                },
                action_description=f"Duyệt tọa độ {node} với h(n) = {h_cost:.1f}."
            ))

            if node == target:
                history.append(State(
                    frontier=[],
                    explored=explored.copy(),
                    current_path=path,
                    hud_metrics={
                        "Current Algorithm": "Greedy Search",
                        "h(n)": "0.0",
                        "Nodes Explored": str(len(explored))
                    },
                    action_description=f"Police đã bắt được Thief tại {target}!"
                ))
                break

            for neighbor in environment.get_neighbors(node[0], node[1]):
                if neighbor not in explored:
                    explored.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    heapq.heappush(pq, (heuristic(neighbor, target), new_path))

        return history
