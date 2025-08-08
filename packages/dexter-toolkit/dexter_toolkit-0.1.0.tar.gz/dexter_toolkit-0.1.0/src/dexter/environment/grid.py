import tkinter as tk
from tkinter import messagebox

class Grid:
    def __init__(self, nrows: int, ncolumns: int):
        self.nrows = nrows
        self.ncols = ncolumns
        self.grid = [['·' for _ in range(ncolumns)] for _ in range(nrows)]
        self.agent_pos = None

    def set_cell(self, x: int, y: int, value: str) -> None:
        self.grid[y][x] = value

    def __getitem__(self, pos):
        i, j = pos
        return self.grid[i][j]

    def set_agent(self, x: int, y: int) -> None:
        if self.agent_pos:
            self.set_cell(*self.agent_pos, '·')
        self.agent_pos = (x, y)
        self.set_cell(x, y, 'A')

    def __str__(self) -> str:
        # Top border
        top_border = '+' + '-' * (self.ncols * 2) + '+'
        # Middle rows with side borders
        middle_rows = ['|' + ' '.join(row) + ' |' for row in self.grid]
        # Bottom border
        bottom_border = '+' + '-' * (self.ncols * 2) + '+'
        # Combine all parts
        return '\n'.join([top_border] + middle_rows + [bottom_border])

class GridApp:
    def __init__(self, root, grid):
        self.root = root
        self.grid = grid
        self.root.title("Grid Display")

        self.text = tk.Text(root, font=("Courier", 12), width=grid.ncols * 2 + 2, height=grid.nrows + 2)
        self.text.pack()

        self.update_text()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.update_button = tk.Button(self.button_frame, text="Update", command=self.update_grid)
        self.update_button.pack(side=tk.LEFT)

        self.quit_button = tk.Button(self.button_frame, text="Quit", command=root.quit)
        self.quit_button.pack(side=tk.LEFT)

    def update_text(self):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, str(self.grid))

    def update_grid(self):
        # Example action: move the agent to a new position
        self.grid.set_agent(3, 3)
        self.update_text()
        messagebox.showinfo("Grid Updated", "The grid has been updated!")

if __name__ == "__main__":
    grid = Grid(10, 20)
    grid.set_cell(1, 1, '#')
    grid.set_cell(2, 2, '#')
    grid.set_agent(0, 0)

    root = tk.Tk()
    app = GridApp(root, grid)
    root.mainloop()
