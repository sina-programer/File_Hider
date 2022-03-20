import tkinter as tk
import os

import model
import meta


if __name__ == "__main__":
    root = tk.Tk()
    root.title(meta.title)
    root.geometry(meta.get_geometry(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.resizable(False, False)

    if os.path.exists(meta.icon_path):
        root.iconphoto(True, tk.PhotoImage(file=meta.icon_path))

    app = model.App(root)

    root.mainloop()
