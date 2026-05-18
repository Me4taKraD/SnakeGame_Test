import tkinter as tk
import random
from collections import deque

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
SPEED = 150
LOOKAHEAD_DEPTH = 3
TRAP_PENALTY = -10000
FOOD_DISTANCE_WEIGHT = 120
MAX_GRID_DIST = GRID_WIDTH * GRID_HEIGHT

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

ROCK_COUNT = 20

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

        self.auto_mode = True
        self.controls_frame = tk.Frame(self.window, bg=COLOR_BG)
        self.controls_frame.pack(fill="x", pady=(0, 4))
        self.auto_button = tk.Button(
            self.controls_frame,
            text="Авто: ВЫКЛ",
            font=("Segoe UI", 11, "bold"),
            bg="#2d4a2d",
            fg=COLOR_SCORE,
            activebackground="#3d6b3d",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=4,
            command=self.toggle_auto_mode,
        )
        self.auto_button.pack()
        self._update_auto_button()

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
        self.auto_mode = True
        self._update_auto_button()
        self.update_score_label()

    def toggle_auto_mode(self):
        self.auto_mode = not self.auto_mode
        self._update_auto_button()

    def _update_auto_button(self):
        if self.auto_mode:
            self.auto_button.config(text="Авто: ВКЛ", bg="#2e7d32", fg="white")
        else:
            self.auto_button.config(text="Авто: ВЫКЛ", bg="#2d4a2d", fg=COLOR_SCORE)

    def update_score_label(self):
        self.score_label.config(text=f"Очки: {self.score}")

    def _free_cells(self, include_rocks=True):
        blocked = set(self.snake)
        if include_rocks:
            blocked.update(self.rocks)
        return [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in blocked
        ]

    def spawn_food(self):
        free_cells = self._free_cells(include_rocks=True)
        if not free_cells:
            free_cells = [
                (x, y)
                for x in range(GRID_WIDTH)
                for y in range(GRID_HEIGHT)
                if (x, y) not in self.snake
            ]
        if not free_cells:
            return None
        return random.choice(free_cells)
            
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
        if key in ("a", "A"):
            self.toggle_auto_mode()
            return
        if self.auto_mode and not self.game_over:
            return
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

    def _wrap(self, pos):
        x, y = pos
        if x < 0:
            x = GRID_WIDTH - 1
        elif x >= GRID_WIDTH:
            x = 0
        if y < 0:
            y = GRID_HEIGHT - 1
        elif y >= GRID_HEIGHT:
            y = 0
        return (x, y)

    def _neighbors(self, pos):
        x, y = pos
        return [
            self._wrap((x, y - 1)),
            self._wrap((x, y + 1)),
            self._wrap((x - 1, y)),
            self._wrap((x + 1, y)),
        ]

    def _opposite(self, direction):
        return {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}[direction]

    def _valid_directions(self, current_dir):
        all_dirs = ["Up", "Down", "Left", "Right"]
        if current_dir:
            opp = self._opposite(current_dir)
            return [d for d in all_dirs if d != opp]
        return all_dirs

    def _head_from_direction(self, head, direction):
        x, y = head
        if direction == "Up":
            return self._wrap((x, y - 1))
        if direction == "Down":
            return self._wrap((x, y + 1))
        if direction == "Left":
            return self._wrap((x - 1, y))
        return self._wrap((x + 1, y))

    def _direction_from_to(self, a, b):
        ax, ay = a
        bx, by = b
        if bx == ax:
            return "Up" if by < ay else "Down"
        return "Left" if bx < ax else "Right"

    def _blocked_cells(self, snake, rocks, will_eat=False):
        blocked = set(rocks)
        body = snake if will_eat else snake[:-1] if len(snake) > 1 else snake
        blocked.update(body)
        return blocked

    def _bfs_path(self, start, goal, blocked):
        if start == goal:
            return [start]
        if goal in blocked:
            return None
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            pos, path = queue.popleft()
            for nb in self._neighbors(pos):
                if nb in visited or nb in blocked:
                    continue
                new_path = path + [nb]
                if nb == goal:
                    return new_path
                visited.add(nb)
                queue.append((nb, new_path))
        return None

    def _bfs_distances(self, start, blocked):
        dist = {start: 0}
        queue = deque([start])
        while queue:
            pos = queue.popleft()
            for nb in self._neighbors(pos):
                if nb in blocked or nb in dist:
                    continue
                dist[nb] = dist[pos] + 1
                queue.append(nb)
        return dist

    def _reachable_count(self, start, blocked):
        if start in blocked:
            return 0
        visited = {start}
        queue = deque([start])
        while queue:
            pos = queue.popleft()
            for nb in self._neighbors(pos):
                if nb not in visited and nb not in blocked:
                    visited.add(nb)
                    queue.append(nb)
        return len(visited)

    def _food_distance(self, head, food, blocked):
        return self._bfs_distances(head, blocked).get(food, MAX_GRID_DIST)

    def _food_distance_after_move(self, snake, direction, food, rocks):
        result = self._simulate_step(list(snake), direction, food, rocks)
        if result is None:
            return MAX_GRID_DIST
        new_snake, _, ate = result
        head = new_snake[0]
        blocked = self._blocked_cells(new_snake, rocks, will_eat=ate)
        return self._food_distance(head, food, blocked)

    def _is_move_safe(self, snake, direction, food, rocks):
        result = self._simulate_step(list(snake), direction, food, rocks)
        if result is None:
            return False
        new_snake, _, ate = result
        head = new_snake[0]
        blocked = self._blocked_cells(new_snake, rocks, will_eat=ate)
        return self._reachable_count(head, blocked) >= len(new_snake)

    def _first_steps_to_goal(self, snake, goal, rocks):
        head = snake[0]
        blocked = self._blocked_cells(snake, rocks, will_eat=False)
        if goal in blocked:
            return []
        dist = self._bfs_distances(head, blocked)
        if goal not in dist:
            return []
        directions = []
        seen = set()
        for nb in self._neighbors(head):
            if nb in blocked or dist.get(nb) != 1:
                continue
            next_blocked = set(blocked)
            next_blocked.add(head)
            if self._bfs_path(nb, goal, next_blocked):
                direction = self._direction_from_to(head, nb)
                if direction not in seen:
                    seen.add(direction)
                    directions.append(direction)
        return directions

    def _simulate_step(self, snake, direction, food, rocks):
        head = snake[0]
        new_head = self._head_from_direction(head, direction)
        if new_head in snake or new_head in rocks:
            return None
        ate = new_head == food
        if ate:
            new_snake = [new_head] + list(snake)
        else:
            new_snake = [new_head] + list(snake[:-1])
        return new_snake, food, ate

    def _evaluate_state(self, snake, food, rocks):
        head = snake[0]
        blocked = self._blocked_cells(snake, rocks, will_eat=False)
        reachable = self._reachable_count(head, blocked)
        dist_food = self._food_distance(head, food, blocked)
        score = (MAX_GRID_DIST - dist_food) * FOOD_DISTANCE_WEIGHT
        score += min(reachable, len(snake) * 3)
        if reachable < len(snake):
            score += TRAP_PENALTY
        if dist_food == 0:
            score += 5000
        elif self._bfs_path(head, food, blocked):
            score += 400
        if len(snake) > 1 and self._bfs_path(head, snake[-1], blocked):
            score += 80
        return score

    def _score_moves(self, snake, food, rocks, depth, current_dir=None):
        if depth == 0:
            return self._evaluate_state(snake, food, rocks)
        best = float("-inf")
        for direction in self._valid_directions(current_dir):
            result = self._simulate_step(snake, direction, food, rocks)
            if result is None:
                continue
            new_snake, new_food, _ = result
            child = self._score_moves(new_snake, new_food, rocks, depth - 1, direction)
            best = max(best, child)
        return best if best > float("-inf") else TRAP_PENALTY

    def _score_first_move(self, snake, food, rocks, direction, current_dir):
        result = self._simulate_step(snake, direction, food, rocks)
        if result is None:
            return TRAP_PENALTY
        new_snake, new_food, _ = result
        remaining = LOOKAHEAD_DEPTH - 1
        if remaining <= 0:
            return self._evaluate_state(new_snake, new_food, rocks)
        return self._score_moves(new_snake, new_food, rocks, remaining, direction)

    def _pick_best_direction(self, snake, food, rocks, directions, fallback, prefer_food=True):
        safe_dirs = [d for d in directions if self._is_move_safe(snake, d, food, rocks)]
        if not safe_dirs:
            safe_dirs = list(directions)

        def sort_key(direction):
            dist = self._food_distance_after_move(snake, direction, food, rocks)
            lookahead = self._score_first_move(list(snake), food, rocks, direction, fallback)
            if prefer_food:
                return (dist, -lookahead)
            return (-lookahead, dist)

        return min(safe_dirs, key=sort_key)

    def choose_auto_direction(self):
        snake = self.snake
        food = self.food
        if food is None:
            return self.direction
        rocks = self.rocks
        current = self.direction
        all_dirs = self._valid_directions(current)
        head = snake[0]
        blocked = self._blocked_cells(snake, rocks, will_eat=False)

        path = self._bfs_path(head, food, blocked)
        if path and len(path) >= 2:
            direct = self._direction_from_to(head, path[1])
            if direct in all_dirs and self._is_move_safe(snake, direct, food, rocks):
                return direct

        food_steps = self._first_steps_to_goal(snake, food, rocks)
        if food_steps:
            safe_food = [d for d in food_steps if self._is_move_safe(snake, d, food, rocks)]
            if safe_food:
                return self._pick_best_direction(
                    snake, food, rocks, safe_food, current, prefer_food=True
                )

        safe_any = [d for d in all_dirs if self._is_move_safe(snake, d, food, rocks)]
        if safe_any:
            return self._pick_best_direction(
                snake, food, rocks, safe_any, current, prefer_food=True
            )

        return self._pick_best_direction(
            snake, food, rocks, all_dirs, current, prefer_food=True
        )

    def move_snake(self):
        if self.game_over:
            return
        if self.food is None:
            self.food = self.spawn_food()
        if self.auto_mode:
            self.next_direction = self.choose_auto_direction()
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
        if self.food is not None and new_head == self.food:
            self.score += 1
            self.update_score_label()
            new_food = self.spawn_food()
            if new_food is not None:
                self.food = new_food
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

        if self.food is not None:
            fx, fy = self.food
            self.draw_apple(fx, fy)
        self.draw_rocks()

        for i, (x, y) in enumerate(reversed(self.snake)):
            segment_index = len(self.snake) - 1 - i
            if segment_index == 0:
                self.draw_head(x, y)
            else:
                self.draw_body_segment(x, y, segment_index)

        if self.auto_mode and not self.game_over:
            self.canvas.create_text(
                8, 8,
                text="АВТО",
                fill="#81c784",
                font=("Segoe UI", 10, "bold"),
                anchor="nw",
            )

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
