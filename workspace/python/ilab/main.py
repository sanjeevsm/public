import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
from app.config import get_config
from app import theme
from app.ui.app_window import AppWindow


def main():
    cfg = get_config()
    mode = cfg.get("appearance_mode", "dark")
    theme.set_mode(mode)
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("iLab+ | AI Interview Simulator")
    root.geometry("1340x780")
    root.minsize(1100, 660)

    AppWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
