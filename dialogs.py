from tkinter import simpledialog, messagebox, filedialog
from tkinter import ttk
import tkinter as tk

import datetime as dt
import webbrowser
import threading
import winsound
import time
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


class QuickScanDialog(simpledialog.Dialog):
    def __init__(self, app):
        winsound.MessageBeep()
        self.app = app
        self.total_items = -1
        self.hidden_files = []
        self.hiddens_file_path = ''
        self.folder_var = tk.StringVar()
        self.current_var = tk.StringVar()
        self.current_var.set('Current:')
        super().__init__(self.app.master, 'Quick Scan Directory')

    def body(self, frame):
        frame = tk.Frame(self)
        frame.pack(pady=8)
        padding = {'pady': 3, 'padx': 8}

        tk.Entry(frame, width=45, bd=0, textvariable=self.current_var, state='readonly').grid(column=1, row=1, sticky=tk.W, **padding)
        self.total_lbl = tk.Label(frame, text='Total:')
        self.total_lbl.grid(column=2, row=1, sticky=tk.W, **padding)

        self.progressbar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=272)
        self.progressbar.grid(column=1, row=2, **padding)
        self.start_btn = tk.Button(frame, text='Start', width=9, state='disable')
        self.start_btn['command'] = lambda: threading.Thread(target=self.scan).start()
        self.start_btn.grid(column=2, row=2, **padding)

        tk.Entry(frame, width=45, textvariable=self.folder_var, state='readonly').grid(column=1, row=3, **padding)
        tk.Button(frame, text='Browse', width=9, command=self.browse).grid(column=2, row=3, **padding)

        menu = tk.Menu(self)
        menu.add_command(label='Show hiddens', command=self.show_hiddens_file)
        self.config(menu=menu)

        self.geometry('400x110')
        self.resizable(False, False)

        return frame

    def scan(self):
        self.hidden_files = []
        self.progressbar.config(value=0, maximum=self.total_items)
        folder = self.folder_var.get()

        for r, d, f in os.walk(folder):
            for item in d + f:
                self.progressbar['value'] += 1
                self.progressbar.update_idletasks()
                item_path = os.path.join(r, item)
                self.current_var.set(f"Current:  {item_path.replace(folder, '')}")
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
            if self.start_btn['state'] != 'normal':
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
        if self.progressbar['value']:
            if self.progressbar['value'] == self.total_items:
                if self.hidden_files:
                    os.startfile(self.hiddens_file_path)
                else:
                    messagebox.showinfo(meta.title, "There is no any hidden file in the folder")
            else:
                messagebox.showerror(meta.title, "Please wait untill scan finish!")
        else:
            messagebox.showerror(meta.title, "You havn't started scan!")

    def buttonbox(self):
        pass


class SuperScanDialog(simpledialog.Dialog):
    def __init__(self, app):
        self.app = app
        self.set_default_vars()
        self.folder_var = tk.StringVar()
        self.total_items_var = tk.IntVar()
        self.scaned_items_var = tk.IntVar()

        winsound.MessageBeep()
        super().__init__(self.app.master, 'Super Scan Directory')

    def body(self, frame):
        main_frame = tk.Frame(self)
        main_frame.pack(pady=15)
        padding = {'pady': 5, 'padx': 10}

        total_frame = tk.Frame(main_frame)
        total_frame.grid(row=1, column=1, **padding)
        scaned_frame = tk.Frame(main_frame)
        scaned_frame.grid(row=1, column=2, **padding)

        tk.Label(total_frame, text='Total items:').pack(side=tk.LEFT)
        tk.Label(total_frame, textvariable=self.total_items_var).pack(side=tk.RIGHT)

        tk.Label(scaned_frame, text='Scaned items:').pack(side=tk.LEFT)
        tk.Label(scaned_frame, textvariable=self.scaned_items_var).pack(side=tk.RIGHT)

        self.start_btn = tk.Button(main_frame, text='Start', width=9, command=self.start_scan, state=tk.DISABLED)
        self.start_btn.grid(row=1, column=3, **padding)

        tk.Button(main_frame, text='Browse', width=9, command=self.browse).grid(row=2, column=3, **padding)
        tk.Entry(main_frame, width=34, textvariable=self.folder_var, state='readonly').grid(row=2, column=1, columnspan=2, **padding)


        menu = tk.Menu(self)
        menu.add_command(label='Show hiddens', command=self.show_hiddens_file)
        self.config(menu=menu)

        self.geometry('370x100')
        self.resizable(False, False)

        return frame

    def start_scan(self):
        self.hidden_files = []
        self.scaned_items = 0
        self.scaned_items_var.set(0)

        for part in self.organized_files:
            threading.Thread(target=self.scan, args=(part,)).start()

    def scan(self, files):
        """
        This function scan a part of files and count scaned files
        then merge hidden files founded with main hidden files
        """

        hidden_files = []

        for file in files:
            self.scaned_items += 1
            self.scaned_items_var.set(self.scaned_items_var.get() + 1)
            if self.app.check_hide(file):
                hidden_files.append(file)

        self.scaned_items_var.set(self.scaned_items)
        self.hidden_files.extend(hidden_files)

    def browse(self):
        """
        This function open dialog for ask which directory will scan
        then organize files and count them
        """

        new_path = filedialog.askdirectory()
        if new_path:
            new_path = os.path.normpath(new_path)
            self.folder_var.set(new_path)
            if self.start_btn['state'] != 'normal':
                self.start_btn.config(state='normal')
            self.set_default_vars()

            for r, d, f in os.walk(new_path):
                for item in d + f:
                    item_path = os.path.join(r, item)
                    self.all_files.append(item_path)

            self.total_items_var.set(len(self.all_files))
            self.scaned_items_var.set(0)
            self.organized_files = self.organize_files(self.all_files)

    @staticmethod
    def organize_files(files, limit=100):
        """
        This function organize <files> to a list so that
        each item in result is a list with maximum <limit> item from <files>
        """

        result = []

        for i in range((len(files) // limit) + 1):
            sample = files[i * limit : (i+1) * limit]
            if sample:
                result.append(sample)

        return result

    def set_default_vars(self):
        """ This function reset all variables """

        self.all_files = []
        self.organized_files = []
        self.hidden_files = []
        self.hiddens_file_path = ''
        self.scaned_items = 0

    def create_hiddens_file(self):
        """ This function create a report(*.txt) for hidden files """

        folder = self.folder_var.get()
        folder_name = os.path.basename(folder)
        now = dt.datetime.now().strftime('%Y-%m-%d')
        filename = f"superscan_{folder_name}_{now}.txt"
        self.hiddens_file_path = os.path.join(os.path.dirname(meta.config_path), filename)
        content = '\n\n'.join(self.hidden_files)
        content = f"Hidden files in <{folder_name}>: \n\n\n{content}"

        with open(self.hiddens_file_path, 'w') as file:
            file.write(content)

    def show_hiddens_file(self):
        """ This function open report file(*.txt) if possible """

        if self.scaned_items:
            if  self.scaned_items == len(self.all_files):
                if self.hidden_files:
                    if not self.hiddens_file_path:
                        self.create_hiddens_file()
    
                    os.startfile(self.hiddens_file_path)
                else:
                    messagebox.showinfo(meta.title, "There is no any hidden file in the folder")
            else:
                messagebox.showerror(meta.title, "Please wait untill scan finish!")
        else:
            messagebox.showerror(meta.title, "You havn't started scan!")

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
