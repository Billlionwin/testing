import tkinter as tk
from tkinter import messagebox
import os
from collections import deque
from itertools import permutations

GRID_SIZE = 6  
CELL_SIZE = 600//GRID_SIZE
SCREEN_SIZE = 600

BLACK = "#000000"
COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#FFA500", "#00FFFF", "#583927", "#808080", "#F5F5DC", "#000000"]

LEVELS = [
    {COLORS[0]: [(0, 0), (5, 0)], COLORS[1]: [(1, 1), (4, 4)], COLORS[2]: [(3, 2), (5, 1)], COLORS[3]: [(0, 1), (2, 2)], COLORS[5]: [(1, 2), (1, 4)]},
    {COLORS[0]: [(0, 0), (3, 2)], COLORS[1]: [(1, 5), (5, 1)], COLORS[2]: [(0, 5), (5, 0)], COLORS[3]: [(1, 2), (4, 4)]},
    {COLORS[0]: [(0, 0), (0, 2)], COLORS[1]: [(0, 1), (4, 4)], COLORS[2]: [(3, 4), (1, 4)], COLORS[3]: [(2, 4), (2, 3)]},
    {COLORS[0]: [(1, 1), (4, 4)], COLORS[1]: [(0, 5), (0, 0)], COLORS[2]: [(0, 4), (0, 1)], COLORS[3]: [(2, 3), (0, 3)]},
    {COLORS[0]: [(2, 2), (5, 2)], COLORS[1]: [(2, 3), (5, 1)], COLORS[2]: [(4, 1), (4, 4)], COLORS[3]: [(1, 1), (3, 4)]},
    {COLORS[0]: [(0, 0), (4, 5)], COLORS[1]: [(3, 5), (4, 2)], COLORS[2]: [(5, 0), (1, 4)], COLORS[3]: [(4, 3), (4, 4)]},
    {COLORS[0]: [(3, 2), (5, 5)], COLORS[1]: [(3, 3), (4, 4)], COLORS[2]: [(5, 4), (1, 4)], COLORS[3]: [(1, 5), (5, 2)]},
    {COLORS[0]: [(0, 0), (4, 3)], COLORS[1]: [(4, 0), (5, 3)], COLORS[2]: [(1, 1), (0, 5)], COLORS[3]: [(2, 1), (1, 5)], COLORS[4]: [(3, 2), (4, 5)], COLORS[5]: [(3, 4), (5, 5)]},
    {COLORS[0]: [(2, 2), (3, 4)], COLORS[1]: [(2, 3), (5, 5)], COLORS[2]: [(4, 4), (0, 5)], COLORS[3]: [(0, 4), (5, 4)]},
    {COLORS[0]: [(1, 0), (4, 4)], COLORS[1]: [(1, 4), (2, 0)], COLORS[2]: [(2, 2), (3, 1)], COLORS[3]: [(3, 0), (5, 0)], COLORS[4]: [(5, 1), (2, 4)], COLORS[5]: [(5, 2), (4, 5)]},
]

class ConnectingDotsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Connecting dots game")
        self.setup_window()
        self.canvas = tk.Canvas(root, width=SCREEN_SIZE, height=SCREEN_SIZE + 50)
        self.canvas.pack()
        self.level = 0
        self.paths = {}
        self.selected_color = None
        self.current_path = []
        self.in_menu = True
        self.menu_state = "main"
        self.custom_level = {}
        self.custom_level_name = ""
        self.draw_menu()
        self.bind_events()

    def setup_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_x = (screen_width // 2) - (SCREEN_SIZE // 2)
        position_y = (screen_height // 2) - (SCREEN_SIZE // 2)
        self.root.geometry(f"{SCREEN_SIZE}x{SCREEN_SIZE + 50}+{position_x}+{position_y}")
    
    def draw_menu(self):
        self.canvas.delete("all")
        if self.menu_state == "main":
            self.canvas.create_text(SCREEN_SIZE // 2, 50, text="Connecting dots game", font=("Avenir", 24))
            self.create_button(SCREEN_SIZE // 2, 150, "Select Level", lambda: self.change_menu_state("select_level"))
            self.create_button(SCREEN_SIZE // 2, 200, "Create Your Own Level", lambda: (self.change_menu_state("create_level"), self.clear_custom_level()))
            self.create_button(SCREEN_SIZE // 2, 250, "Load Saved Level", lambda: self.handle_load_button_click())
            self.create_button(SCREEN_SIZE // 2, 300, "How to Play", lambda: self.change_menu_state("how_to_play"))
        elif self.menu_state == "select_level":
            self.canvas.create_text(SCREEN_SIZE // 2, 50, text="Select Level", font=("Avenir", 24))
            self.create_button(60, 50, "Back", lambda: self.change_menu_state("main"))
            for i in range(len(LEVELS)):
                self.create_button(SCREEN_SIZE // 2, 150 + i * 50, f"Level {i + 1}", lambda i=i: self.select_level(i))
        elif self.menu_state == "load_level":
            self.canvas.create_text(SCREEN_SIZE // 2, 50, text="Select Saved Level", font=("Avenir", 24))
            self.create_button(60, 50, "Back", lambda: self.change_menu_state("main"))
            home_dir = os.path.expanduser("~") # Get the user's home directory
            save_dir = os.path.join(home_dir, "ConnectingDotsLevels") # Create a directory called ConnectingDotsLevels in the user's home directory
            saved_levels = [f[:-4] for f in os.listdir(save_dir) if f.endswith(".txt")]
            for i, level in enumerate(saved_levels):
                self.create_button(SCREEN_SIZE // 2 - 50, 150 + i * 50, level, lambda level=level: self.load_level(level + ".txt"))
                self.create_button(SCREEN_SIZE // 2 + 100, 150 + i * 50, "Delete", lambda level=level: self.delete_level(level + ".txt"))
        elif self.menu_state == "how_to_play":
            self.canvas.create_text(SCREEN_SIZE // 2, 50, text="How to Play", font=("Avenir", 24))
            self.create_button(60, 50, "Back", lambda: self.change_menu_state("main"))
            self.canvas.create_text(SCREEN_SIZE // 2-40, SCREEN_SIZE // 2+10, text="""
            Solving a level:
            Connect all the dots of the same
            color with a single line by dragging
            the mouse. The line should not
            intersect with other lines or dots. 
            
            Creating a custom level:
            Click on the grid to place dots.  
            To remove a dot, click on the dot.
            Click "Solve" to check if the level
            is solvable.

            """, font=("Avenir", 24), anchor="center")
    
    def draw_level(self): # Draw the dots for the current level
        if self.level == -1: # Custom level
            current_level = self.custom_level
        else:
            current_level = LEVELS[self.level]
        for color, positions in current_level.items():
            for pos in positions:
                x, y = pos
                self.canvas.create_oval(x * CELL_SIZE + 25, y * CELL_SIZE + 75, x * CELL_SIZE + 75, y * CELL_SIZE + 125, fill=color, outline=color)
    
    def bind_events(self):
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<B1-Motion>", self.handle_game_drag)

    def draw_grid(self):
        for x in range(0, SCREEN_SIZE, CELL_SIZE):
            self.canvas.create_line(x, 50, x, SCREEN_SIZE + 50, fill=BLACK)
        for y in range(50, SCREEN_SIZE + 50, CELL_SIZE):
            self.canvas.create_line(0, y, SCREEN_SIZE, y, fill=BLACK)

    def draw_paths(self):
        for color, path in self.paths.items():
            if len(path) > 1:
                for i in range(len(path) - 1):
                    x1, y1 = path[i]
                    x2, y2 = path[i + 1]
                    self.canvas.create_line(x1 * CELL_SIZE + 50, y1 * CELL_SIZE + 100, x2 * CELL_SIZE + 50, y2 * CELL_SIZE + 100, fill=color, width=CELL_SIZE/4, capstyle="round")

    def create_button(self, x, y, text, callback):
        button = self.canvas.create_text(x, y, text=text, font=("Avenir", 24), fill=BLACK)
        self.canvas.tag_bind(button, "<Enter>", lambda _: self.canvas.itemconfig(button, fill="grey"))
        self.canvas.tag_bind(button, "<Leave>", lambda _: self.canvas.itemconfig(button, fill=BLACK))
        self.canvas.tag_bind(button, "<Button-1>", lambda _: callback())

    
    def handle_click(self, event):
        if self.in_menu:
            self.handle_menu_button_click(event)
        else:
            if self.menu_state == "create_level":
                self.handle_custom_level_click(event)
            else:
                self.handle_game_click(event)
            self.handle_menu_button_click(event)

    def handle_game_click(self, event):
        x, y = event.x // CELL_SIZE, (event.y - 50) // CELL_SIZE
        if self.level == -1:
            current_level = self.custom_level
        else:
            current_level = LEVELS[self.level]
        for color, positions in current_level.items():
            if (x, y) in positions:
                if color in self.paths:
                    del self.paths[color]
                self.selected_color = color
                self.current_path = [(x, y)]
                self.paths[color] = [(x, y)]
                self.draw_game()
                return
            
    def handle_game_drag(self, event):
        if self.selected_color:
            x, y = event.x // CELL_SIZE, (event.y - 50) // CELL_SIZE
            if (x, y) in self.current_path:
                # Truncate the path up to the current position
                index = self.current_path.index((x, y))
                self.current_path = self.current_path[:index + 1]
                self.paths[self.selected_color] = self.current_path
                self.draw_game()
            # Add the current position to the path if it's a valid move
            elif (x, y) not in self.current_path and 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and not any((x, y) in path for path in self.paths.values()) and (len(self.current_path) == 0 or (abs(x - self.current_path[-1][0]) == 0 and abs(y - self.current_path[-1][1]) == 1 or abs(x - self.current_path[-1][0]) == 1 and abs(y - self.current_path[-1][1]) == 0)) and not any((x, y) in positions for color, positions in (self.custom_level if self.level == -1 else LEVELS[self.level]).items() if color != self.selected_color):
                self.current_path.append((x, y))
                self.paths[self.selected_color] = self.current_path
                self.draw_game()
                if self.level == -1 and self.check_win():
                    messagebox.showinfo("Congratulations", "Level completed!")
                    self.change_menu_state("load_level")
                elif self.check_win():
                    messagebox.showinfo("Congratulations", "Level completed!")
                    self.change_menu_state("select_level")
            # Disable dragging for the color once the path is completed
            if len(self.current_path) > 1 and self.current_path[0] in (self.custom_level if self.level == -1 else LEVELS[self.level])[self.selected_color] and self.current_path[-1] in (self.custom_level if self.level == -1 else LEVELS[self.level])[self.selected_color]:
                self.selected_color = None
                
    def check_win(self):
        if self.level == -1:
            current_level = self.custom_level
        else:
            current_level = LEVELS[self.level]
        
        for color, positions in current_level.items():
            path = self.paths.get(color, [])
            if not path or positions[0] not in path or positions[-1] not in path:
                return False
        return True
            
    def change_menu_state(self, state):
        self.menu_state = state
        if state == "create_level":
            self.in_menu = False
            self.paths.clear()
            self.draw_game()
            self.canvas.unbind("<Button-1>")
            self.root.after(100, self.bind_events)  # Rebind events after 0.1 second
        elif state == "load_level":
            self.in_menu = True # Prevents the game from being drawn
            self.draw_menu()
        elif state == "select_level":
            self.in_menu = True # Prevents the game from being drawn
            self.draw_menu()
        else:
            self.draw_menu()
    def select_level(self, level):
        self.level = level
        self.in_menu = False
        self.paths.clear()
        self.draw_game()

    def handle_load_button_click(self):
        home_dir = os.path.expanduser("~")
        save_dir = os.path.join(home_dir, "ConnectingDotsLevels")
        
        if not os.path.exists(save_dir) or not os.listdir(save_dir):
            messagebox.showerror("Error", "No saved levels found.")
            return

        self.menu_state = "load_level"
        self.draw_menu()

    def delete_level(self, level_name):
        home_dir = os.path.expanduser("~")
        save_dir = os.path.join(home_dir, "ConnectingDotsLevels")
        level_path = os.path.join(save_dir, level_name)
        if messagebox.askokcancel("Confirm", f"Delete level '{level_name[:-4]}'?"):
            os.remove(level_path)
            self.draw_menu()

    def load_level(self, level_name):
        home_dir = os.path.expanduser("~")
        save_dir = os.path.join(home_dir, "ConnectingDotsLevels")
        level_path = os.path.join(save_dir, level_name)
        try:
            with open(level_path, "r") as file:
                self.custom_level = eval(file.read())
            self.level = -1  # Use -1 to indicate a custom level
            self.custom_level_name = level_name.rsplit('.', 1)[0]  # Remove file extension for display
            self.in_menu = False
            self.paths.clear()
            self.draw_game()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load level: {e}")
    def draw_level_number(self):
        if self.level == -1:
            level_text = f"Level: {self.custom_level_name}"  # Display the custom level name
        else:
            level_text = f"Level: {self.level + 1}"
        self.canvas.create_text(SCREEN_SIZE - 90, 25, text=level_text, fill=BLACK, font=("Avenir", 24))

    def handle_menu_button_click(self, event):
        if 10 <= event.x <= 110 and 10 <= event.y <= 40: # Click on the menu button
            self.in_menu = True
            self.menu_state = "main"
            self.draw_menu()

    def draw_custom_level(self):
        drawn_positions = set()
        for color, positions in self.custom_level.items():
            for pos in positions:
                if pos not in drawn_positions:
                    x, y = pos
                    self.canvas.create_oval(x * CELL_SIZE + 25, y * CELL_SIZE + 75, x * CELL_SIZE + 75, y * CELL_SIZE + 125, fill=color, outline=color)
                    drawn_positions.add(pos)

    def draw_game(self):
        self.canvas.delete("all")
        self.draw_grid()
        if self.menu_state == "create_level":
            self.draw_custom_level()
            self.create_button(SCREEN_SIZE - 55, 25, "Clear", lambda: self.clear_custom_level())
            self.create_button(SCREEN_SIZE * 1/3+10, 25, "Save", lambda: self.save_custom_level())
            self.create_button(SCREEN_SIZE * 2/3, 25, "Solve", lambda: self.solve_button())
        else:
            self.draw_level()
            self.draw_paths()
            self.draw_level_number()
        self.create_button(60, 25, "Menu", lambda e: self.handle_menu_button_click(e))
    
   
    def solve_button(self):
        if self.custom_level:
            success = self.solve_custom_level()
        else:
            messagebox.showerror("Error", "Please create a custom level first.")
            
    def handle_custom_level_click(self, event):
        x, y = event.x // CELL_SIZE, (event.y - 50) // CELL_SIZE # Convert the click coordinates to grid coordinates
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE: # Check if the click is within the grid
            for color, positions in self.custom_level.items(): 
                if (x, y) in positions: # if user clicks on a dot, remove the dot
                    positions.remove((x, y))
                    if not positions:
                        del self.custom_level[color] # Remove the color from the custom level if there are no more dots
                    self.draw_game()
                    return

            if not self.selected_color: # If no color is selected
                for color in COLORS: # Loop through the colors
                    if color not in self.custom_level or len(self.custom_level[color]) < 2: # Check if the color is not in the custom level or if the color has less than 2 dots
                        self.selected_color = color # Set the selected color to the current color
                        break

            if self.selected_color: # If a color is selected
                if self.selected_color not in self.custom_level: 
                    self.custom_level[self.selected_color] = [(x, y)] # Add the first dot to the color's positions
                elif len(self.custom_level[self.selected_color]) == 1: # If the color has one dot
                    self.custom_level[self.selected_color].append((x, y)) # Add the second dot to the color's positions
                    self.selected_color = None
            self.draw_game()
                
    def solve_custom_level(self):
        temp_paths = {}
        pairs = list(self.custom_level.items())

        for perm in permutations(pairs): # Try all permutations of the pairs
            if not self.custom_level: # If the custom level is empty or user clicks clear
                break
            temp_paths.clear()
            self.canvas.delete("path")
            for color, path in perm:
                if len(path) == 2:
                    x1, y1 = path[0]
                    x2, y2 = path[1]
                    temp_path = self.find_paths(x1, y1, x2, y2, temp_paths)

                    if temp_path:
                        temp_paths[color] = temp_path
                        for i in range(len(temp_path) - 1):
                            x1, y1 = temp_path[i]
                            x2, y2 = temp_path[i + 1]
                            self.canvas.create_line(x1 * CELL_SIZE + 50, y1 * CELL_SIZE + 100, x2 * CELL_SIZE + 50, y2 * CELL_SIZE + 100, fill=color, width=CELL_SIZE/4, capstyle="round", tag="path")
                        self.canvas.update()
                    else:
                        break
            else:
                self.paths.update(temp_paths)
                return True

        messagebox.showinfo("Alert", "The level is unsolvable.")
        self.canvas.delete("path")
        return False

    def find_paths(self, x1, y1, x2, y2, temp_paths):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        queue = deque([(x1, y1, [])]) # (x, y, path)
        visited = set() # Visited positions

        while queue:
            x, y, path = queue.popleft() 
            if (x, y) in visited: 
                continue
            visited.add((x, y))
            path = path + [(x, y)]

            if (x, y) == (x2, y2):
                return path

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited and not any((nx, ny) in p for p in temp_paths.values()) and ((nx, ny) == (x2, y2) or not any((nx, ny) in positions for positions in self.custom_level.values())):
                    queue.append((nx, ny, path))
        return None

    def clear_custom_level(self):
        self.custom_level.clear()
        self.draw_game()

    def save_custom_level(self):
        #if no dots are placed, or odd number of dots are placed
        if not self.custom_level or any(len(positions) % 2 == 1 for positions in self.custom_level.values()):
            messagebox.showerror("Error", "Invalid dots placement. Cannot save level.")
            return
        save_window = tk.Toplevel(self.root)
        save_window.title("Save Custom Level")
        save_window.geometry(f"300x150+{self.root.winfo_screenwidth() // 2 - 150}+{self.root.winfo_screenheight() // 2 - 75}")

        label = tk.Label(save_window, text="Enter level name:", font=("Avenir", 18))
        label.pack(pady=10)

        entry = tk.Entry(save_window, font=("Avenir", 18))
        entry.pack(pady=5)

        save_button = tk.Label(save_window, text="Save", font=("Avenir", 18))
        save_button.pack(pady=10)

        def save_level():
            level_name = entry.get()
            if level_name:
                home_dir = os.path.expanduser("~")# Get the user's home directory
                save_dir = os.path.join(home_dir, "ConnectingDotsLevels")# Create a directory called ConnectingDotsLevels in the user's home directory
                os.makedirs(save_dir, exist_ok=True)
                filename = os.path.join(save_dir, f"{level_name}.txt")
                if os.path.exists(filename):
                    if messagebox.askokcancel("Confirm", f"Level '{level_name}' already exists. Replace with new one?"):
                        with open(filename, "w") as file:
                            file.write(str(self.custom_level))
                            messagebox.showinfo("Alert", f"Custom level '{level_name}' saved!")
                        save_window.destroy()
                else:
                    with open(filename, "w") as file:
                        file.write(str(self.custom_level))
                        messagebox.showinfo("Alert", f"Custom level '{level_name}' saved!")
                    save_window.destroy()
            else:
                messagebox.showerror("Error", "Please enter a level name.")

        save_button.bind("<Button-1>", lambda e: save_level())
        save_button.bind("<Enter>", lambda e: save_button.config(fg="grey"))
        save_button.bind("<Leave>", lambda e: save_button.config(fg="black"))
        entry.bind("<Return>", lambda e: save_level()) # Press enter to save the level
if __name__ == "__main__":
    root = tk.Tk()
    game = ConnectingDotsGame(root)
    root.mainloop()
