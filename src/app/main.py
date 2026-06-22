import os
import sys
import tkinter as tk

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(BASE_DIR)

from ui.fruit_window import FruitWindow


def main():

    root = tk.Tk()

    FruitWindow(root)

    root.mainloop()


if __name__ == "__main__":
    main()