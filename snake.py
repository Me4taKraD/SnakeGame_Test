import tkinter as tk
import random

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
SPEED = 150

COLOR_BG = "#1a2e1a"
COLOR_BODY = "#3d8b37"
COLOR_BODY_DARK = "#2d6b28"
COLOR_HEAD = "#5cb85c"
COLOR_APPLE = "#e53935"
COLOR_APPLE_DARK = "#c62828"
COLOR_LEAF = "#43a047"
COLOR_STEM = "#4d362e"
COLOR_EYE_WHITE = "#ffffff"
COLOR_EYE_PUPIL = "#1a1a1a"
COLOR_ROCK = "#3f3f3f"
COLOR_SCORE = "#e8f5e9"

ROCK_COUNT = 5

class SnakeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Змейка")
        self.window.resizable(False, False)

        self.score_label = tk.Label(
            self.window,
            text="Очки: 0",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_BG,
            fg=COLOR_SCORE,
            pady=6,
        )
        self.score_label.pack(fill="x")

        self.canvas = tk.Canvas(
            self.window,
            bg=COLOR_BG,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.rocks = []
        
        self.high_score = self.load_high_score()
        
        self.reset_game()
        self.window.bind("<KeyPress>", self.on_key_press)
        self.game_loop()

    def reset_game(self):
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = self.spawn_food()
        self.spawn_rocks()
        self.game_over = False
        self.score = 0
        self.update_score_label()

    def update_score_label(self):
        self.score_label.config(text=f"Очки: {self.score}")

    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                return pos
            
    def spawn_rocks(self):
        self.rocks = []
        for _ in range(ROCK_COUNT):
            while True:
                pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
                if pos not in self.snake and pos not in self.rocks and pos != self.food:
                    self.rocks.append(pos)
                    break

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))

    def on_key_press(self, event):
        key = event.keysym
        if key == "Up" and self.direction != "Down":
            self.next_direction = "Up"
        elif key == "Down" and self.direction != "Up":
            self.next_direction = "Down"
        elif key == "Left" and self.direction != "Right":
            self.next_direction = "Left"
        elif key == "Right" and self.direction != "Left":
            self.next_direction = "Right"
        elif key == "Return" and self.game_over:
            self.reset_game()

    def cell_rect(self, x, y, margin=1):
        px = x * CELL_SIZE + margin
        py = y * CELL_SIZE + margin
        return px, py, (x + 1) * CELL_SIZE - margin, (y + 1) * CELL_SIZE - margin

    def cell_center(self, x, y):
        return x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2

    def move_snake(self):
        if self.game_over:
            return
        self.direction = self.next_direction
        head = self.snake[0]
        if self.direction == "Up":
            new_head = (head[0], head[1] - 1)
        elif self.direction == "Down":
            new_head = (head[0], head[1] + 1)
        elif self.direction == "Left":
            new_head = (head[0] - 1, head[1])
        else:
            new_head = (head[0] + 1, head[1])

        if new_head[0] < 0:
            new_head = (GRID_WIDTH - 1, new_head[1])
        elif new_head[0] >= GRID_WIDTH:
            new_head = (0, new_head[1])
        elif new_head[1] < 0:
            new_head = (new_head[0], GRID_HEIGHT - 1)
        elif new_head[1] >= GRID_HEIGHT:
            new_head = (new_head[0], 0)

        if new_head in self.snake:
            self.game_over = True
            return

        if new_head in self.rocks:  # ← добавить после проверки змейки
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.update_score_label()
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw_body_segment(self, x, y, index):
        x1, y1, x2, y2 = self.cell_rect(x, y)
        fill = COLOR_BODY if index % 2 == 0 else COLOR_BODY_DARK
        self.canvas.create_oval(x1, y1, x2, y2, fill=fill, outline="#256325", width=1)
        cx, cy = self.cell_center(x, y)
        r = CELL_SIZE // 6
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=COLOR_BODY_DARK, outline="")

    def draw_head(self, x, y):
        x1, y1, x2, y2 = self.cell_rect(x, y, margin=0)
        self.canvas.create_oval(x1, y1, x2, y2, fill=COLOR_HEAD, outline="#256325", width=2)

        cx, cy = self.cell_center(x, y)
        eye_offset = CELL_SIZE // 4
        eye_r = CELL_SIZE // 5
        pupil_r = eye_r // 2

        if self.direction == "Right":
            e1 = (cx + eye_offset // 2, cy - eye_offset)
            e2 = (cx + eye_offset // 2, cy + eye_offset)
        elif self.direction == "Left":
            e1 = (cx - eye_offset // 2, cy - eye_offset)
            e2 = (cx - eye_offset // 2, cy + eye_offset)
        elif self.direction == "Up":
            e1 = (cx - eye_offset, cy - eye_offset // 2)
            e2 = (cx + eye_offset, cy - eye_offset // 2)
        else:
            e1 = (cx - eye_offset, cy + eye_offset // 2)
            e2 = (cx + eye_offset, cy + eye_offset // 2)

        for ex, ey in (e1, e2):
            self.canvas.create_oval(
                ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r,
                fill=COLOR_EYE_WHITE, outline=COLOR_EYE_PUPIL, width=1,
            )
            if self.direction == "Right":
                px, py = ex + pupil_r // 2, ey
            elif self.direction == "Left":
                px, py = ex - pupil_r // 2, ey
            elif self.direction == "Up":
                px, py = ex, ey - pupil_r // 2
            else:
                px, py = ex, ey + pupil_r // 2
            self.canvas.create_oval(
                px - pupil_r, py - pupil_r, px + pupil_r, py + pupil_r,
                fill=COLOR_EYE_PUPIL, outline="",
            )

        if self.direction == "Right":
            tx, ty = x2 - 2, cy
        elif self.direction == "Left":
            tx, ty = x1 + 2, cy
        elif self.direction == "Up":
            tx, ty = cx, y1 + 2
        else:
            tx, ty = cx, y2 - 2
        self.canvas.create_line(tx, ty, tx, ty, fill="#c62828", width=3, capstyle=tk.ROUND)

    def draw_apple(self, x, y):
        cx, cy = self.cell_center(x, y)
        r = CELL_SIZE // 2 - 3
        self.canvas.create_oval(
            cx - r, cy - r + 2, cx + r, cy + r,
            fill=COLOR_APPLE, outline=COLOR_APPLE_DARK, width=2,
        )
        self.canvas.create_oval(
            cx - r // 3, cy - r // 2, cx + r // 4, cy,
            fill="#ef5350", outline="",
        )
        self.canvas.create_rectangle(
            cx - 1, cy - r - 4, cx + 1, cy - r + 2,
            fill=COLOR_STEM, outline="",
        )
        self.canvas.create_polygon(
            cx, cy - r - 6,
            cx + 6, cy - r - 1,
            cx - 2, cy - r,
            fill=COLOR_LEAF, outline="#2e7d32",
        )

    def draw_rocks(self):
        for x, y in self.rocks:
            x1 = x * CELL_SIZE
            y1 = y * CELL_SIZE
            x2 = (x + 1) * CELL_SIZE
            y2 = (y + 1) * CELL_SIZE
            points = [x1 + CELL_SIZE//4, y1, x2 - CELL_SIZE//4, y1, x2, y2, x1, y2]
            self.canvas.create_polygon(points, fill=COLOR_ROCK, outline="#1b1b1b")

    def draw(self):
        self.canvas.delete("all")
        for i in range(GRID_WIDTH):
            for j in range(GRID_HEIGHT):
                if (i + j) % 2 == 0:
                    shade = "#1e331e"
                else:
                    shade = "#1a2e1a"
                self.canvas.create_rectangle(
                    i * CELL_SIZE, j * CELL_SIZE,
                    (i + 1) * CELL_SIZE, (j + 1) * CELL_SIZE,
                    fill=shade, outline="",
                )

        fx, fy = self.food
        self.draw_apple(fx, fy)
        self.draw_rocks()

        for i, (x, y) in enumerate(reversed(self.snake)):
            segment_index = len(self.snake) - 1 - i
            if segment_index == 0:
                self.draw_head(x, y)
            else:
                self.draw_body_segment(x, y, segment_index)

        if self.game_over:
            self.canvas.create_rectangle(
                0, 0, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE,
                fill="#000000", stipple="gray50",
            )
            self.canvas.create_text(
                GRID_WIDTH * CELL_SIZE // 2,
                GRID_HEIGHT * CELL_SIZE // 2,
                text=f"Игра окончена!\nОчки: {self.score}\nEnter — заново",
                fill="white",
                font=("Segoe UI", 16, "bold"),
                justify="center",
            )

    def game_loop(self):
        self.move_snake()
        self.draw()
        self.window.after(SPEED, self.game_loop)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    SnakeGame().run()
