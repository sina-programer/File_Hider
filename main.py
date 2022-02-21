import tkinter as tk
import os

import model
import meta


if __name__ == "__main__":
    root = tk.Tk()
    meta.Geometry.set_screen_geometry(
        root.winfo_screenwidth(), root.winfo_screenheight())

    root.title(meta.title)
    root.geometry(meta.Geometry.get_geometry())
    root.resizable(False, False)

    if os.path.exists(meta.icon):
        root.iconbitmap(default=meta.icon)

    app = model.App(root)

    root.mainloop()
