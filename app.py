import tkinter as tk
from controller.main_controller import MainController

def main():
    root = tk.Tk()
    app = MainController(root)
    root.mainloop()

if __name__ == "__main__":
    main()