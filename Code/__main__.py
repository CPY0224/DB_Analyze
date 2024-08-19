# __main__.py
from UI import SimpleApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
