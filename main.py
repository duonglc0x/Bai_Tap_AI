import sys
import os
import random
import pygame

# Đảm bảo Python luôn tìm thấy các module trong cùng thư mục với main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment import Environment
from algorithms.greedy import GreedySearch
from algorithms.astar import AStar
from algorithms.idastar import IDAStar
from algorithms.alpha_beta import AlphaBeta
from algorithms.expectimax import Expectimax

from ui.renderer import UIRenderer
from ui.widgets import Button, ComboBox

ALGORITHMS = {
    "Informed Search": ["Greedy Search", "A*", "IDA*"],
    "Adversarial Search": ["Alpha-Beta Pruning", "Expectimax"],
}

def run_simulation(algo_name: str):
    """
    Hàm khởi tạo môi trường và chạy trước thuật toán để lấy lịch sử các bước.
    Trả về môi trường, lịch sử chạy và tọa độ của Thief (nếu cố định).
    """
    env = Environment()

    # Vị trí xuất phát của Police (trung tâm bản đồ)
    police_start = (env.width // 2, env.height // 2)

    # Vị trí xuất hiện ngẫu nhiên của Thief
    thief_start = (random.randint(0, env.width - 1), random.randint(0, env.height - 1))
    while thief_start == police_start:
        thief_start = (random.randint(0, env.width - 1), random.randint(0, env.height - 1))

    avoid_positions = [police_start, thief_start]

    # Sinh địa hình ngẫu nhiên
    env.generate_terrains(
        num_walls=30,
        num_rough=40,
        avoid_positions=avoid_positions
    )

    history = []
    if algo_name == "Greedy Search":
        history = GreedySearch().run(env, police_start, thief_start)
    elif algo_name == "A*":
        history = AStar().run(env, police_start, thief_start)
    elif algo_name == "IDA*":
        history = IDAStar().run(env, police_start, thief_start)
    elif algo_name == "Alpha-Beta Pruning":
        history = AlphaBeta().run(env, police_start, thief_start)
    elif algo_name == "Expectimax":
        history = Expectimax().run(env, police_start, thief_start)

    # Nếu là thuật toán tìm kiếm đơn (không đối kháng), Thief đứng im
    fixed_thief = None
    if algo_name in ALGORITHMS["Informed Search"]:
        fixed_thief = thief_start
        
    return env, history, fixed_thief


def main():
    """
    Vòng lặp sự kiện đồ họa chính (Main Game Loop).
    """
    # 1. Khởi tạo Pygame & Renderer
    renderer = UIRenderer(width=1600, height=900)
    clock = pygame.time.Clock()

    # 2. Định nghĩa cấu hình màu sắc & font cho Widget HUD
    font = renderer.font_body
    bg_color = (210, 205, 190)
    hover_color = (190, 180, 160)
    text_color = renderer.COLOR_TEXT_DARK

    # 3. Khởi tạo các Widgets điều khiển (nằm trên khu vực HUD góc phải trên cùng)
    btn_play  = Button(1100, 40, 110, 32, "Play", font, bg_color, text_color, hover_color)
    btn_pause = Button(1220, 40, 110, 32, "Pause", font, bg_color, text_color, hover_color)
    btn_prev  = Button(1340, 40, 110, 32, "< Prev", font, bg_color, text_color, hover_color)
    btn_next  = Button(1460, 40, 110, 32, "Next >", font, bg_color, text_color, hover_color)

    cat_list = list(ALGORITHMS.keys())
    combo_cat = ComboBox(1100, 90, 180, 32, cat_list, font, bg_color, text_color)
    combo_algo = ComboBox(1300, 90, 220, 32, ALGORITHMS[cat_list[0]], font, bg_color, text_color)
    
    # Nút chạy thuật toán màu xanh nổi bật
    btn_run = Button(1530, 90, 90, 32, "RUN", font, (100, 200, 100), (0, 0, 0), (80, 180, 80))

    # 4. Trạng thái chạy ứng dụng ban đầu
    current_algo = combo_algo.get_selected()
    env, history, fixed_thief = run_simulation(current_algo)
    
    current_step = 0
    total_steps = len(history)
    is_playing = False
    
    delay = 200  # Độ trễ giữa các khung hình (ms)
    last_update_time = pygame.time.get_ticks()

    running = True
    while running:
        # --- XỬ LÝ SỰ KIỆN (Event Handling) ---
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            # Xử lý Widget: Ưu tiên xử lý ComboBox trước (để bắt sự kiện click trong dropdown)
            cat_changed = False
            if combo_cat.is_expanded:
                cat_changed = combo_cat.handle_event(event)
            elif combo_algo.is_expanded:
                combo_algo.handle_event(event)
            else:
                cat_changed = combo_cat.handle_event(event)
                combo_algo.handle_event(event)

                # Nút bấm điều khiển quá trình (Playback Controls)
                if btn_play.handle_event(event):
                    is_playing = True
                if btn_pause.handle_event(event):
                    is_playing = False
                if btn_prev.handle_event(event):
                    is_playing = False
                    current_step = max(0, current_step - 1)
                if btn_next.handle_event(event):
                    is_playing = False
                    current_step = min(total_steps - 1, current_step + 1)
                
                # Chạy lại thuật toán được chọn
                if btn_run.handle_event(event):
                    current_algo = combo_algo.get_selected()
                    env, history, fixed_thief = run_simulation(current_algo)
                    current_step = 0
                    total_steps = len(history)
                    is_playing = True

            # Cập nhật thuật toán xổ xuống nếu thay đổi Danh mục (Category)
            if cat_changed:
                combo_algo.update_options(ALGORITHMS[combo_cat.get_selected()])

        # --- LOGIC PHÁT (Auto Play) ---
        current_time = pygame.time.get_ticks()
        if is_playing and current_time - last_update_time > delay:
            if current_step < total_steps - 1:
                current_step += 1
            else:
                is_playing = False # Dừng lại khi tới cuối lịch sử
            last_update_time = current_time

        # --- KẾT XUẤT ĐỒ HỌA (Rendering) ---
        if history and current_step < len(history):
            state = history[current_step]
            # Gọi hàm vẽ toàn bộ Grid, Terrain, Entity và Bảng số liệu HUD
            renderer.draw_frame(state, env.grid, current_step, total_steps, fixed_thief, history)
        else:
            renderer.screen.fill(renderer.COLOR_MAP_BG)

        # Vẽ đè các Widgets lên trên bảng HUD
        btn_play.draw(renderer.screen)
        btn_pause.draw(renderer.screen)
        btn_prev.draw(renderer.screen)
        btn_next.draw(renderer.screen)
        btn_run.draw(renderer.screen)

        # LƯU Ý: Vẽ ComboBox sau cùng. Cần vẽ ngược (từ trái qua phải, từ dưới lên trên) 
        # để danh sách dropdown của nó có thể đè đè lên các widget phía dưới.
        combo_algo.draw_main_box(renderer.screen)
        combo_algo.draw_dropdown(renderer.screen)

        combo_cat.draw_main_box(renderer.screen)
        combo_cat.draw_dropdown(renderer.screen)

        pygame.display.flip()
        clock.tick(60) # Khóa tốc độ ở 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    print("[INFO] Bắt đầu khởi động Giao diện Đồ họa...")
    main()
