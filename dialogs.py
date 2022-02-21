import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

import webbrowser
import winsound
import os

import meta


class AboutDialog(simpledialog.Dialog):
    def __init__(self, parent):
        winsound.MessageBeep()
        super().__init__(parent, 'About us')

    def body(self, frame):
        tk.Label(self, text='This program made by Sina.f').pack(pady=12)
        kwargs = {'row': 1, 'padx': 10, 'pady': 5}

        tk.Button(frame, text='GitHub', width=9, command=lambda: webbrowser.open(meta.links['github'])).grid(column=1, **kwargs)
        tk.Button(frame, text='Instagram', width=9, command=lambda: webbrowser.open(meta.links['instagram'])).grid(column=2, **kwargs)
        tk.Button(frame, text='Telegram', width=9, command=lambda: webbrowser.open(meta.links['telegram'])).grid(column=3, **kwargs)

        self.geometry('300x100')
        self.resizable(False, False)

        return frame

    def buttonbox(self):
        pass


class SettingDialog(simpledialog.Dialog):
    def __init__(self, parent, app):
        self.app = app
        winsound.MessageBeep()
        super().__init__(parent, 'Setting')

    def body(self, frame):
        tk.Checkbutton(self, text='Save logs', variable=self.app.save_logs,
                       onvalue=1, offvalue=0, command=self.app.update_savelogs).place(x=15, y=10)
        tk.Entry(self, width=45, textvariable=self.app.log_path, state='readonly').place(x=20, y=45)
        tk.Button(self, text='Copy', width=9, command=self.copy2clipboard).place(x=310, y=10)
        tk.Button(self, text='Change', width=9, command=self.change_logfile).place(x=310, y=40)

        self.geometry('400x80')
        self.resizable(False, False)

        return frame

    def change_logfile(self):
        new_path = filedialog.askopenfilename(filetypes=meta.file_types)
        if new_path:
            new_path = os.path.normpath(new_path)
            self.app.update_logfile(new_path)

    def copy2clipboard(self):
        self.app.master.clipboard_clear()
        self.app.master.clipboard_append(self.app.log_path.get())
        messagebox.showinfo(meta.title, 'Log path successfully copied!')

    def buttonbox(self):
        pass


class HiddensDialog(simpledialog.Dialog):
    def __init__(self, parent, app):
        self.app = app
        winsound.MessageBeep()
        super().__init__(parent, 'Hidden Files')

    def body(self, frame):
        files_box = tk.Listbox(self, width=50)
        files_box.pack(side=tk.LEFT, padx=15, pady=10)

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for file in self.app.meta['hidden_files']:
            files_box.insert(tk.END, file)

        files_box.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=files_box.yview)

        self.geometry('350x150')
        self.resizable(False, False)

        return frame

    def buttonbox(self):
        pass
