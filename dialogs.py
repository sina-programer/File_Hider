from tkinter import simpledialog, messagebox, filedialog
from tkinter import ttk
import tkinter as tk

import datetime as dt
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

        tk.Label(frame, text='This program made by Sina.f').grid(column=1, row=1, rowspan=2, **kwargs)
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
        self.path_var.set(self.app.config['log_file'])
        winsound.MessageBeep()
        super().__init__(self.app.master, 'Log setting')

    def body(self, frame):
        frame = tk.Frame(self)
        frame.pack(pady=8)
        padding = {'pady': 3, 'padx': 8}
        tk.Checkbutton(frame, text='Save logs', variable=self.app.save_logs,
                       onvalue=1, offvalue=0, command=self.app.update_savelogs).grid(column=1, row=1, sticky=tk.W, **padding)
        tk.Entry(frame, width=45, textvariable=self.path_var, state='readonly').grid(column=1, row=2, **padding)
        tk.Button(frame, text='Copy', width=10, command=self.copy2clipboard).grid(column=2, row=1, **padding)
        tk.Button(frame, text='Change', width=10, command=self.change_logfile).grid(column=2, row=2, **padding)

        self.geometry('400x80')
        self.resizable(False, False)

        return frame

    def change_logfile(self):
        new_path = filedialog.askopenfilename(filetypes=meta.logfile_types)
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
        self.total_items = -1
        self.hidden_files = []
        self.hiddens_file_path = ''
        self.folder_var = tk.StringVar()
        self.current_var = tk.StringVar()
        self.current_var.set('Current:')
        super().__init__(self.app.master, 'Scan Directory')

    def body(self, frame):
        frame = tk.Frame(self)
        frame.pack(pady=8)
        padding = {'pady': 3, 'padx': 8}
        tk.Entry(frame, width=45, textvariable=self.current_var, state='readonly', bd=0).grid(column=1, row=1, sticky=tk.W, **padding)
        self.total_lbl = tk.Label(frame, text='Total:')
        self.total_lbl.grid(column=2, row=1, sticky=tk.W, **padding)
        tk.Entry(frame, width=45, textvariable=self.folder_var, state='readonly').grid(column=1, row=3, **padding)
        self.progressbar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=272)
        self.progressbar.grid(column=1, row=2, **padding)

        self.start_btn = tk.Button(frame, text='Start', width=9, command=self.start_scan, state='disable')
        self.start_btn.grid(column=2, row=2, **padding)
        tk.Button(frame, text='Browse', width=9, command=self.browse).grid(column=2, row=3, **padding)

        menu = tk.Menu(self)
        menu.add_command(label='Show hiddens', command=self.show_hiddens_file)
        self.config(menu=menu)

        self.geometry('400x110')
        self.resizable(False, False)

        return frame

    def start_scan(self):
        self.hidden_files = []
        self.progressbar.config(value=0, maximum=self.total_items)
        folder = self.folder_var.get()

        for r, d, f in os.walk(folder):
            for item in d + f:
                self.progressbar['value'] += 1
                self.progressbar.update_idletasks()
                item_path = os.path.join(r, item)
                self.current_var.set(f"Current: {item_path.replace(folder, '')}")
                if self.app.check_hide(item_path):
                    self.hidden_files.append(item_path)

        if self.hidden_files:
            self.create_hiddens_file()
            os.startfile(self.hiddens_file_path)
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
            self.total_lbl.config(text=f"Total: {self.total_items}")
            self.current_var.set("Current:")
            self.hiddens_file_path = ''
            self.hidden_files = []

    def create_hiddens_file(self):
        folder = self.folder_var.get()
        folder_name = os.path.basename(folder)
        now = dt.datetime.now().strftime('%Y-%m-%d')
        filename = f"scan_{folder_name}_{now}.txt"
        self.hiddens_file_path = os.path.join(os.path.dirname(meta.config_path), filename)
        content = '\n\n'.join(self.hidden_files)
        content = f"Hidden files in <{folder_name}>: \n\n\n{content}"

        with open(self.hiddens_file_path, 'w') as file:
            file.write(content)

    def show_hiddens_file(self):
        if self.progressbar['value'] == self.total_items:
            if self.hidden_files:
                os.startfile(self.hiddens_file_path)
            else:
                messagebox.showinfo(meta.title, "There is no any hidden file in the folder")
        else:
            messagebox.showinfo(meta.title, "You havn't started scan!")

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

        for file in self.app.config['hidden_files']:
            files_box.insert(tk.END, file)

        files_box.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=files_box.yview)

        self.geometry('350x150')
        self.resizable(False, False)

        return frame

    def buttonbox(self):
        pass
