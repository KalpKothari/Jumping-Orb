import tkinter as tk
import random

# Game Constants
WIDTH = 400
HEIGHT = 500
GRAVITY = 1
JUMP_STRENGTH = -12
PIPE_SPEED = 5
PIPE_WIDTH = 50
GAP_HEIGHT = 130
PIPE_DISTANCE = 170  
PIPE_SPAWN_TIME = 1800  

SHIELD_SIZE = 30  
SHIELD_SPEED = 2  
SHIELD_APPEAR_TIME = 25000  
SHIELD_IMMUNITY_DURATION = 7000  

CLOUD_SPEED = 1  
NUM_CLOUDS = 3  

class JumpingOrb:
    def __init__(self, root):
        self.root = root
        self.root.title("Jumping Orb")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="skyblue")
        self.canvas.pack()

        self.game_running = False
        self.pipes = []
        self.score = 0
        self.shield = None
        self.shield_active = False
        self.last_pipe_x = WIDTH 
        self.is_night = False 

        self.clouds = []  
        self.create_clouds()

        self.root.bind("<space>", self.start_game)
        self.root.bind("<r>", self.restart_game)

        self.show_start_screen()

    def show_start_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH//2, HEIGHT//2 - 50, text="JUMPING ORB", font=("Arial", 24, "bold"), fill="yellow")
        self.canvas.create_text(WIDTH//2, HEIGHT//2, text="Press SPACE to Start", font=("Arial", 14, "bold"), fill="black")

    def start_game(self, event):
        if not self.game_running:
            self.game_running = True
            self.init_game()
            self.root.bind("<space>", self.flap)

    def init_game(self):
        self.canvas.delete("all")  # Clear canvas
        self.create_clouds()  # Recreate clouds
        self.ball_velocity = 0
        self.pipes.clear()
        self.shield_active = False  
        self.score = 0
        self.night_mode_active = False

        # **Ensure ball exists before calling restore_day_mode**
        self.ball = self.canvas.create_oval(50, HEIGHT//2 - 15, 80, HEIGHT//2 + 15, fill="yellow", outline="black")
        self.score_text = self.canvas.create_text(WIDTH//2, 30, text="Score: 0", font=("Arial", 16, "bold"), fill="black")

        self.restore_day_mode()  # Now it's safe to call this

        self.update_game()
        self.schedule_pipes()
        self.spawn_shield()
        self.move_clouds()

    def create_clouds(self):
        self.clouds.clear()
        for _ in range(NUM_CLOUDS):
            x = random.randint(WIDTH // 2, WIDTH)
            y = random.randint(20, 100)
            cloud = self.canvas.create_oval(x, y, x + 40, y + 20, fill="white", outline="white")
            self.clouds.append(cloud)

    def move_clouds(self):
        if not self.game_running:
            return

        for cloud in self.clouds:
            self.canvas.move(cloud, -CLOUD_SPEED, 0)
            x1, _, x2, _ = self.canvas.coords(cloud)

            if x2 < 0:
                new_x = WIDTH + random.randint(20, 50)
                new_y = random.randint(20, 100)
                self.canvas.coords(cloud, new_x, new_y, new_x + 40, new_y + 20)

        self.root.after(50, self.move_clouds)


    def schedule_pipes(self):
        if self.game_running:
            if self.pipes and self.canvas.coords(self.pipes[-1][0])[0] > WIDTH - PIPE_DISTANCE:
                self.root.after(PIPE_SPAWN_TIME, self.schedule_pipes)
                return  
            
            self.create_pipe()
            self.root.after(PIPE_SPAWN_TIME, self.schedule_pipes)

    def create_pipe(self):
        gap_start = random.randint(50, HEIGHT - GAP_HEIGHT - 50)
        top_pipe = self.canvas.create_rectangle(WIDTH, 0, WIDTH + PIPE_WIDTH, gap_start, fill="green")
        bottom_pipe = self.canvas.create_rectangle(WIDTH, gap_start + GAP_HEIGHT, WIDTH + PIPE_WIDTH, HEIGHT, fill="green")

        self.pipes.append((top_pipe, bottom_pipe))
        self.last_pipe_x = WIDTH  

    def spawn_shield(self):
      if not self.game_running:
        return

      if self.shield:
        self.canvas.delete(self.shield)

      y_position = random.randint(100, HEIGHT - 100)

    # Set shield color based on the current mode
      shield_color = "white" if self.night_mode_active else "blue"
      self.shield = self.canvas.create_text(WIDTH, y_position, text="🛡️", font=("Arial", 25), fill=shield_color)

      self.move_shield()
      self.root.after(SHIELD_APPEAR_TIME, self.spawn_shield)


    def move_shield(self):
        if not self.shield or not self.game_running:
            return

        self.canvas.move(self.shield, -SHIELD_SPEED, 0)

        x1, y1, x2, y2 = self.canvas.bbox(self.shield)
        bx1, by1, bx2, by2 = self.canvas.coords(self.ball)

        if bx1 < x2 and bx2 > x1 and by1 < y2 and by2 > y1:
            self.activate_shield()

        if x2 < 0:
            self.canvas.delete(self.shield)
            self.shield = None

        self.root.after(30, self.move_shield)

    def activate_shield(self):
     self.shield_active = True
     self.canvas.delete(self.shield)
     self.shield = None  

    # Set ball color based on the current mode
     ball_color = "black" if self.night_mode_active else "blue"
     self.canvas.itemconfig(self.ball, fill=ball_color, outline="cyan")

     self.root.after(SHIELD_IMMUNITY_DURATION, self.deactivate_shield)



    def deactivate_shield(self):
      self.shield_active = False

    # Restore ball color based on mode
      ball_color = "white" if self.night_mode_active else "yellow"
      self.canvas.itemconfig(self.ball, fill=ball_color, outline="black")


    def flap(self, event):
        if self.game_running:
            self.ball_velocity = JUMP_STRENGTH

    def update_game(self):
        if not self.game_running:
            return

        self.ball_velocity += GRAVITY
        self.canvas.move(self.ball, 0, self.ball_velocity)
        bx1, by1, bx2, by2 = self.canvas.coords(self.ball)

        if by2 >= HEIGHT or by1 <= 0:
            if not self.shield_active:
                self.game_over()
                return

        for pipe in self.pipes[:]:  
            self.canvas.move(pipe[0], -PIPE_SPEED, 0)
            self.canvas.move(pipe[1], -PIPE_SPEED, 0)

            px1, _, px2, _ = self.canvas.coords(pipe[0])
            if not self.shield_active and (bx2 > px1 and bx1 < px2 and (by1 < self.canvas.coords(pipe[0])[3] or by2 > self.canvas.coords(pipe[1])[1])):
                self.game_over()
                return

            if px2 <= 0:
                self.canvas.delete(pipe[0])
                self.canvas.delete(pipe[1])
                self.pipes.remove(pipe)
                self.score += 1
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                if self.score == 10:
                    self.trigger_night_mode()

        self.root.after(30, self.update_game)

    def trigger_night_mode(self):
      self.night_mode_active = True
      self.canvas.configure(bg="darkblue")

      for cloud in self.clouds:
        self.canvas.itemconfig(cloud, fill="gray", outline="gray")

    # If the shield is active, make the ball black; otherwise, make it white
      ball_color = "black" if self.shield_active else "white"
      self.canvas.itemconfig(self.ball, fill=ball_color, outline="white")

    # Change the shield to white in night mode
      if self.shield:
        self.canvas.itemconfig(self.shield, fill="white")

    # Score color from black to white
      self.canvas.itemconfig(self.score_text, fill="white")

    # Restore day mode after 15 seconds
      self.root.after(15000, self.restore_day_mode)

    # Increase game speed during night mode
      global PIPE_SPEED, GRAVITY, SHIELD_SPEED, CLOUD_SPEED
      PIPE_SPEED += 2.5
      GRAVITY += 0.1  
      SHIELD_SPEED += 1  
      CLOUD_SPEED += 1.2
 

    def restore_day_mode(self):
      self.night_mode_active = False
      self.canvas.configure(bg="skyblue")

      for cloud in self.clouds:
        self.canvas.itemconfig(cloud, fill="white", outline="white")

    # If the shield is active, make the ball blue; otherwise, make it yellow
      ball_color = "blue" if self.shield_active else "yellow"
      self.canvas.itemconfig(self.ball, fill=ball_color, outline="black")
 
    # Change the shield back to blue in day mode
      if self.shield:
        self.canvas.itemconfig(self.shield, fill="blue")

     # Score color from white to black
      self.canvas.itemconfig(self.score_text, fill="black")

    # Reset game speed to normal
      global PIPE_SPEED, GRAVITY, SHIELD_SPEED, CLOUD_SPEED
      PIPE_SPEED = 5
      GRAVITY = 1
      SHIELD_SPEED = 2  
      CLOUD_SPEED = 1



    def game_over(self):
        self.game_running = False
        self.canvas.create_text(WIDTH//2, HEIGHT//2, text="GAME OVER!", font=("Arial", 24, "bold"), fill="red")
        self.canvas.create_text(WIDTH//2, HEIGHT//2 + 40, text="Press 'R' to Restart", font=("Arial", 14, "bold"), fill="black")

    def restart_game(self, event):
        self.start_game(None)

root = tk.Tk()
game = JumpingOrb(root)
root.mainloop()