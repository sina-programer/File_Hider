import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox, filedialog
from datetime import datetime
import webbrowser
import winsound
import os

import meta


class AboutDialog(simpledialog.Dialog):
    def __init__(self, parent):
        winsound.MessageBeep()
        super().__init__(parent, 'About us')

    def body(self, frame):
        kwargs = {'padx': 10, 'pady': 5}

        tk.Label(frame, text='This program made by Sina.f').grid(column=1, row=1, **kwargs)
        tk.Button(frame, text='GitHub', width=9, command=lambda: webbrowser.open(meta.links['github'])).grid(column=2, row=1, **kwargs)
        tk.Button(frame, text='Telegram', width=9, command=lambda: webbrowser.open(meta.links['telegram'])).grid(column=2, row=2, **kwargs)

        self.geometry('300x90')
        self.resizable(False, False)

        return frame

    def buttonbox(self):
        pass


class SettingDialog(simpledialog.Dialog):
    def __init__(self, app):
        self.app = app
        self.path_var = tk.StringVar()
        self.path_var.set(self.app.meta['log_file'])
        winsound.MessageBeep()
        super().__init__(self.app.master, 'Log setting')

    def body(self, frame):
        tk.Entry(self, width=45, textvariable=self.path_var, state='readonly').place(x=20, y=45)
        tk.Checkbutton(self, text='Save logs', variable=self.app.save_logs,
                       onvalue=1, offvalue=0, command=self.app.update_savelogs).place(x=15, y=10)
        tk.Button(self, text='Copy', width=10, command=self.copy2clipboard).place(x=310, y=10)
        tk.Button(self, text='Change', width=10, command=self.change_logfile).place(x=310, y=40)

        self.geometry('400x80')
        self.resizable(False, False)

        return frame

    def change_logfile(self):
        new_path = filedialog.askopenfilename(filetypes=meta.file_types)
        if new_path:
            new_path = os.path.normpath(new_path)
            self.path_var.set(new_path)
            self.app.update_logfile(new_path)

    def copy2clipboard(self):
        self.app.master.clipboard_clear()
        self.app.master.clipboard_append(self.app.log_path.get())
        messagebox.showinfo(meta.title, 'Log path successfully copied!')

    def buttonbox(self):
        pass


class ScanDirectoryDialog(simpledialog.Dialog):
    def __init__(self, app):
        winsound.MessageBeep()
        self.app = app
        self.total_items = 0
        self.folder_var = tk.StringVar()
        super().__init__(self.app.master, 'Scan Directory')

    def body(self, frame):
        tk.Entry(self, width=45, textvariable=self.folder_var, state='readonly').place(x=20, y=45)
        self.progressbar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=272)
        self.progressbar.place(x=20, y=10)

        self.start_btn = tk.Button(self, text='Start', width=9, command=self.scan_directory, state='disable')
        self.start_btn.place(x=310, y=10)
        tk.Button(self, text='Browse', width=9, command=self.browse).place(x=310, y=40)

        self.geometry('400x80')
        self.resizable(False, False)

        return frame

    def scan_directory(self):
        self.progressbar.config(maximum=self.total_items)
        folder = self.folder_var.get()
        folder_name = os.path.basename(folder)
        now = datetime.now().strftime('%Y-%m-%d')
        filename = f"scan_{folder_name}_{now}.txt"
        filepath = os.path.join(os.path.dirname(meta.pickle_path), filename)

        hidden_files = []
        for r, d, f in os.walk(folder):
            for item in d + f:
                self.progressbar['value'] += 1
                self.progressbar.update_idletasks()
                item_path = os.path.join(r, item)
                if self.app.check_hide(item_path):
                    hidden_files.append(item_path)

        if hidden_files:
            content = '\n\n'.join(hidden_files)
            content = f"Hidden files in <{folder_name}>: \n\n\n{content}"

            with open(filepath, 'w') as f:
                f.write(content)
                
            os.startfile(filepath)

        else:
            messagebox.showinfo('Hidden Files', 'There is no any hidden file in the folder!')

    def browse(self):
        new_path = filedialog.askdirectory()
        if new_path:
            new_path = os.path.normpath(new_path)
            self.folder_var.set(new_path)
            self.progressbar.config(value=0)
            self.start_btn.config(state='normal')
            self.total_items = sum(len(d + f) for r, d, f in os.walk(new_path))

    def buttonbox(self):
        pass


class HiddensDialog(simpledialog.Dialog):
    def __init__(self, app):
        self.app = app
        winsound.MessageBeep()
        super().__init__(self.app.master, 'Hidden Files')

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
