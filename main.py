import tkinter as tk
import random

# =========================================================
# 1. CẤU HÌNH THÔNG SỐ HỆ THỐNG VÀ VẬT LÝ GAME
# =========================================================
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.35          # Tốc độ tăng vận tốc rơi tự do (Trọng lực)
JUMP_STRENGTH = -7.0    # Lực bật nhảy ngược trục Y khi ấn phím Space

class FlappyBirdGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Flappy Bird - Đào Văn Tú - TH30.10")
        
        # Tạo màn hình Canvas hiển thị đồ họa nền bầu trời xanh
        self.canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="#4ec0ca", highlightthickness=0)
        self.canvas.pack()

        # Khởi tạo các biến quản lý trạng thái vật lý
        self.bird_y = SCREEN_HEIGHT // 2
        self.bird_velocity = 0
        self.score = 0
        self.game_active = True
        self.pipes = []

        # Khởi tạo các thực thể hình học đồ họa theo thiết kế
        self.create_game_objects()

        # Đăng ký sự kiện lắng nghe tương tác từ phím Space
        self.root.bind("<space>", self.jump)
        
        # Kích hoạt vòng lặp xử lý Game Loop chính
        self.game_loop()

    # =========================================================
    # 2. KHỞI TẠO ĐỒ HỌA VECTOR (THEO THIẾT KẾ ĐỐI TƯỢNG)
    # =========================================================
    def create_game_objects(self):
        # Vẽ đối tượng Nền đất cố định ở đáy màn hình
        self.canvas.create_rectangle(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, SCREEN_HEIGHT, fill="#ded895", outline="")
        self.canvas.create_rectangle(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, SCREEN_HEIGHT - 50, fill="#5cba5e", outline="")

        # Dựng đối tượng Chú chim bằng sự kết hợp các khối hình học hệ thống
        self.bird_body = self.canvas.create_oval(90, self.bird_y - 15, 120, self.bird_y + 15, fill="#f8d135", outline="#3f3f3f", width=2)
        self.bird_eye = self.canvas.create_oval(108, self.bird_y - 10, 116, self.bird_y - 2, fill="white", outline="#3f3f3f", width=1)
        self.bird_pupil = self.canvas.create_oval(112, self.bird_y - 8, 115, self.bird_y - 5, fill="black", outline="")
        self.bird_beak = self.canvas.create_polygon(118, self.bird_y - 4, 128, self.bird_y, 118, self.bird_y + 6, fill="#f27d14", outline="#3f3f3f", width=1)
        self.bird_wing = self.canvas.create_oval(92, self.bird_y - 3, 106, self.bird_y + 7, fill="#ffffff", outline="#3f3f3f", width=1)

        # Sinh ra các cặp chướng ngại vật ống nước ban đầu bên ngoài màn hình
        self.spawn_pipe(SCREEN_WIDTH + 100)
        self.spawn_pipe(SCREEN_WIDTH + 340)

        # Khởi tạo giao diện chữ hiển thị điểm số ở trung tâm phía trên
        self.score_id = self.canvas.create_text(SCREEN_WIDTH // 2, 40, text="0", fill="white", font=("Helvetica", 32, "bold"))
        self.game_over_text = None
        self.game_over_bg = None

    def spawn_pipe(self, x_pos):
        gap = 140  # Khoảng cách khe hở cố định giữa ống trên và ống dưới
        top_height = random.randint(80, 320)  # Thuật toán ngẫu nhiên độ cao ống nước
        bottom_y = top_height + gap
        pipe_width = 70
        
        # Thiết kế cấu trúc khối Vector cho Ống nước phía trên
        top_body = self.canvas.create_rectangle(x_pos, 0, x_pos + pipe_width, top_height, fill="#73bf2e", outline="#3f3f3f", width=2)
        top_lip = self.canvas.create_rectangle(x_pos - 4, top_height - 25, x_pos + pipe_width + 4, top_height, fill="#73bf2e", outline="#3f3f3f", width=2)
        
        # Thiết kế cấu trúc khối Vector cho Ống nước phía dưới
        bot_body = self.canvas.create_rectangle(x_pos, bottom_y, x_pos + pipe_width, SCREEN_HEIGHT - 60, fill="#73bf2e", outline="#3f3f3f", width=2)
        bot_lip = self.canvas.create_rectangle(x_pos - 4, bottom_y, x_pos + pipe_width + 4, bottom_y + 25, fill="#73bf2e", outline="#3f3f3f", width=2)
        
        # Thêm các thành phần của cặp ống nước vào danh sách quản lý
        self.pipes.append({
            "items": [top_body, top_lip, bot_body, bot_lip],
            "x": x_pos, "top_h": top_height, "bot_y": bottom_y, "passed": False
        })

    # =========================================================
    # 3. SỰ KIỆN TƯƠNG TÁC VÀ ĐIỀU KHIỂN VẬT LÝ
    # =========================================================
    def jump(self, event):
        if self.game_active:
            self.bird_velocity = JUMP_STRENGTH
        else:
            self.reset_game()

    def check_collision(self, pipe):
        bird_left = 90
        bird_right = 120
        
        # Hiện thực thuật toán va chạm hình hộp AABB với chướng ngại vật
        if pipe["x"] < bird_right and (pipe["x"] + 70) > bird_left:
            if self.bird_y - 13 < pipe["top_h"] or self.bird_y + 13 > pipe["bot_y"]:
                return True
                
        # Thuật toán va chạm với biên trần và nền đất trò chơi
        if self.bird_y > SCREEN_HEIGHT - 73 or self.bird_y < 12:
            return True
        return False

    # =========================================================
    # 4. GAME LOOP - VÒNG LẶP ĐIỀU KHIỂN CHÍNH (60 FPS)
    # =========================================================
    def game_loop(self):
        if self.game_active:
            # 4.1 Cập nhật vật lý rơi tự do cho chú chim
            self.bird_velocity += GRAVITY
            self.bird_y += self.bird_velocity
            
            # Đồng bộ tọa độ đồ họa mới cho toàn bộ các khối bộ phận của chim
            self.canvas.coords(self.bird_body, 90, self.bird_y - 15, 120, self.bird_y + 15)
            self.canvas.coords(self.bird_eye, 108, self.bird_y - 10, 116, self.bird_y - 2)
            self.canvas.coords(self.bird_pupil, 112, self.bird_y - 8, 115, self.bird_y - 5)
            self.canvas.coords(self.bird_beak, 118, self.bird_y - 4, 128, self.bird_y, 118, self.bird_y + 6)
            self.canvas.coords(self.bird_wing, 92, self.bird_y - 3, 106, self.bird_y + 7)

            # 4.2 Cập nhật di chuyển tịnh tiến sang trái của các cặp ống nước
            for pipe in self.pipes:
                pipe["x"] -= 3
                for item in pipe["items"]:
                    self.canvas.move(item, -3, 0)

                # Thuật toán tính toán và cập nhật điểm số thời gian thực
                if not pipe["passed"] and pipe["x"] + 70 < 90:
                    pipe["passed"] = True
                    self.score += 1
                    self.canvas.itemconfig(self.score_id, text=str(self.score))

                # Kích hoạt kiểm tra va chạm liên tục từng khung hình
                if self.check_collision(pipe):
                    self.game_active = False

            # 4.3 Quản lý vùng nhớ: Giải phóng ống nước cũ, tái sinh ống nước mới tiếp nối
            if self.pipes[0]["x"] < -80:
                for item in self.pipes[0]["items"]:
                    self.canvas.delete(item)
                self.pipes.pop(0)
                self.spawn_pipe(self.pipes[-1]["x"] + 240)

            # Đệ quy lặp lại sau đúng 16 mili-giây để duy trì tốc độ ~60 FPS
            self.root.after(16, self.game_loop)
        else:
            # 4.4 Hiển thị bảng thông báo Game Over khi va chạm kết thúc trò chơi
            if not self.game_over_text:
                self.game_over_bg = self.canvas.create_rectangle(60, SCREEN_HEIGHT//2 - 60, SCREEN_WIDTH - 60, SCREEN_HEIGHT//2 + 60, fill="#f5eedc", outline="#3f3f3f", width=3)
                self.game_over_text = self.canvas.create_text(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                    text="GAME OVER\n\nPress SPACE to Restart",
                    justify="center", fill="#d9534f", font=("Helvetica", 16, "bold")
                )

    # =========================================================
    # 5. KHỞI TẠO LẠI MÀN CHƠI MỚI (RESET GAME)
    # =========================================================
    def reset_game(self):
        # Làm sạch toàn bộ thực thể chướng ngại vật cũ trên màn hình Canvas
        for pipe in self.pipes:
            for item in pipe["items"]:
                self.canvas.delete(item)
        self.pipes.clear()

        # Xóa bỏ bảng menu thông báo Game Over cũ
        if self.game_over_text:
            self.canvas.delete(self.game_over_text)
            self.canvas.delete(self.game_over_bg)
            self.game_over_text = None
            self.game_over_bg = None

        # Đặt lại các thông số logic về trạng thái ban đầu
        self.bird_y = SCREEN_HEIGHT // 2
        self.bird_velocity = 0
        self.score = 0
        self.game_active = True
        
        self.canvas.itemconfig(self.score_id, text="0")
        self.spawn_pipe(SCREEN_WIDTH + 100)
        self.spawn_pipe(SCREEN_WIDTH + 340)
        
        # Tái khởi động vòng lặp game
        self.game_loop()

if __name__ == "__main__":
    root = tk.Tk()
    game = FlappyBirdGame(root)
    root.mainloop()