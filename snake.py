"""
Тесируюем пул-реквесты
"""

import tkinter as tk
import random

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
SPEED = 150

class SnakeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Змейка")
        self.canvas = tk.Canvas(self.window, bg="red", width=GRID_WIDTH*CELL_SIZE, height=GRID_HEIGHT*CELL_SIZE)
        self.canvas.pack()
        self.reset_game()
        self.window.bind("<KeyPress>", self.on_key_press)
        self.game_loop()

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
            self.reset_game()

    def move_snake(self):
        if self.game_over:
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
            return
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.canvas.delete("all")
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
                                   text=f"Game Over! Score: {self.score}\nPress Enter to restart",
                                   fill="white", font=("Arial", 16))

    def game_loop(self):
        self.move_snake()
        self.draw()
        self.window.after(SPEED, self.game_loop)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    SnakeGame().run()