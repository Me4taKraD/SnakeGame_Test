import tkinter as tk
import random

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
SPEED = 120

class SnakeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Змейка")
        self.canvas = tk.Canvas(self.window, bg="green", width=GRID_WIDTH*CELL_SIZE, height=GRID_HEIGHT*CELL_SIZE)
        self.canvas.pack()
        self.high_score = self.load_high_score()
        self.menu_frame = None
        self.score = 0
        self.game_over = False
        self.direction = "Right"
        self.next_direction = "Right"
        self.snake = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.food = (0, 0)
        self.show_menu()
        self.window.bind("<KeyPress>", self.on_key_press)
        self.game_loop()

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))

    def show_menu(self):
        self.menu_frame = tk.Frame(self.window, bg="green")
        
        title = tk.Label(self.menu_frame, text="ЗМЕЙКА", bg="green", fg="white", font=("Arial", 36, "bold"))
        title.pack(pady=50)
        
        play_btn = tk.Button(self.menu_frame, text="Играть", bg="green", fg="white", font=("Arial", 20),
                            width=12, command=self.start_game, relief=tk.FLAT, bd=0,
                            activebackground="gray", activeforeground="white", cursor="hand2")
        play_btn.pack(pady=10)
        
        record_btn = tk.Button(self.menu_frame, text=f"Рекорд: {self.high_score}", bg="green", fg="white", font=("Arial", 20),
                              width=12, command=self.show_record, relief=tk.FLAT, bd=0,
                              activebackground="gray", activeforeground="white", cursor="hand2")
        record_btn.pack(pady=10)
        
        exit_btn = tk.Button(self.menu_frame, text="Выйти", bg="green", fg="white", font=("Arial", 20),
                            width=12, command=self.window.destroy, relief=tk.FLAT, bd=0,
                            activebackground="gray", activeforeground="white", cursor="hand2")
        exit_btn.pack(pady=10)
        
        self.menu_frame.pack()

    def hide_menu(self):
        if self.menu_frame:
            self.menu_frame.pack_forget()

    def start_game(self):
        self.hide_menu()
        self.reset_game()

    def show_record(self):
        pass

    def reset_game(self):
        self.snake = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = self.spawn_food()
        self.game_over = False
        self.score = 0

    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if pos not in self.snake:
                return pos

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
            self.show_menu()

    def move_snake(self):
        if self.game_over or (self.menu_frame and self.menu_frame.winfo_viewable()):
            return
        self.direction = self.next_direction
        head = self.snake[0]
        if self.direction == "Up":
            new_head = (head[0], head[1]-1)
        elif self.direction == "Down":
            new_head = (head[0], head[1]+1)
        elif self.direction == "Left":
            new_head = (head[0]-1, head[1])
        else:
            new_head = (head[0]+1, head[1])
        if (new_head[0] < 0):
            new_head = (GRID_WIDTH-1, new_head[1])
        elif (new_head[0] >= GRID_WIDTH):
            new_head = (0, new_head[1])
        elif (new_head[1] < 0):
            new_head = (new_head[0], GRID_HEIGHT-1)
        elif (new_head[1] >= GRID_HEIGHT):
            new_head = (new_head[0], 0)
        if new_head in self.snake:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.canvas.delete("all")
        
        if self.menu_frame and self.menu_frame.winfo_viewable():
            return
        
        for x in range(0, GRID_WIDTH*CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(x, 0, x, GRID_HEIGHT*CELL_SIZE, fill="#333333")
        for y in range(0, GRID_HEIGHT*CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(0, y, GRID_WIDTH*CELL_SIZE, y, fill="#333333")
        
        for x, y in self.snake:
            self.canvas.create_rectangle(x*CELL_SIZE, y*CELL_SIZE, 
                                        (x+1)*CELL_SIZE, (y+1)*CELL_SIZE, 
                                        fill="white", outline="")
        fx, fy = self.food
        self.canvas.create_oval(fx*CELL_SIZE+2, fy*CELL_SIZE+2,
                               (fx+1)*CELL_SIZE-2, (fy+1)*CELL_SIZE-2,
                               fill="white", outline="")
        if self.game_over:
            self.canvas.create_text(GRID_WIDTH*CELL_SIZE//2, GRID_HEIGHT*CELL_SIZE//2,
                                   text=f"Game Over! Score: {self.score}\nPress Enter for menu",
                                   fill="white", font=("Arial", 16))

    def game_loop(self):
        self.move_snake()
        self.draw()
        self.window.after(SPEED, self.game_loop)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    SnakeGame().run()