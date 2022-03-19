import os
import pickle
import subprocess
import tkinter as tk

from functools import wraps
from datetime import datetime
from tkinter import messagebox, filedialog

import meta
import dialogs


def load_obj(filename, folder=os.path.dirname(meta.pickle_path)):
    try:
        path = os.path.join(folder, filename)
        assert os.path.exists(path), f"<{filename}> dosn't exist in <{folder}>"
        with open(path, 'rb') as file:
            return pickle.load(file)

    except Exception as exp:
        raise exp


def save_obj(obj, obj_name, folder=os.path.dirname(meta.pickle_path)):
    try:
        path = os.path.join(folder, obj_name)
        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            os.mkdir(parent)

        with open(path, 'wb') as file:
            return pickle.dump(obj, file)

    except Exception as exp:
        raise exp


def path_checker(func):
    ''' it's a decorator function for check target path '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        app = args[0]
        target_path = app.path_var.get()

        if not target_path:
            messagebox.showerror('ERROR', 'The address field is empty!')

        elif os.path.exists(target_path):
            target_path = os.path.normpath(target_path)
            return func(*args, target_path, **kwargs)

        else:
            messagebox.showerror('ERROR', 'The target address is invalid')

    return wrapper


class App:
    def __init__(self, master):
        self.master = master
        self.master.config(menu=self.init_menu())

        self.meta = self.load_meta()
        self.check_hidden_files()
        self.logger = Logger(self.meta['log_file'])
        self.last_activity = 'You have not been active yet!'

        self.save_logs = tk.IntVar()
        self.save_logs.set(self.meta['save_logs'])
        self.path_var = tk.StringVar()
        self.path_var.trace('w', lambda *args: self.check_state())

        self.state_lbl = tk.Label(self.master)
        tk.Entry(self.master, width=50, textvariable=self.path_var).place(x=100, y=30)
        tk.Button(self.master, text='Copy', width=8, command=self.copy_path2clipboard).place(x=420, y=12)
        tk.Button(self.master, text='Browse', width=8, command=self.browse).place(x=420, y=42)
        tk.Button(self.master, text='Hide', width=8, command=self.hide_target).place(x=20, y=12)
        tk.Button(self.master, text='Show', width=8, command=self.show_target).place(x=20, y=42)

    @path_checker
    def show_target(self, path):
        self.remove_hidden_file(path)
        if self.check_hide(path):
            command = ['attrib', '-s', '-h', f"{path}"]
            subprocess.run(command, shell=True)
            self.check_state()

            self.last_activity = f"Show  {path}"
            if self.save_logs.get():
                self.logger.log(self.last_activity)
            messagebox.showinfo('File Hider', 'The target was successfully unvanished!')

        else:
            messagebox.showwarning('File Hider', 'The target is unvanished now!')

    @path_checker
    def hide_target(self, path):
        self.add_hidden_file(path)
        if not self.check_hide(path):
            command = ['attrib', '+s', '+h', f"{path}"]
            subprocess.run(command, shell=True)
            self.check_state()

            self.last_activity = f"Hide  {path}"
            if self.save_logs.get():
                self.logger.log(self.last_activity)
            messagebox.showinfo('File Hider', 'The target was successfully vanished!')

        else:
            messagebox.showwarning('File Hider', 'The target is vanished now!')

    def check_hide(self, path):
        result = subprocess.check_output(['attrib', f"{path}"], shell=True).decode().lower()
        result = result[:21]
        if 'h' in result:
            return True
        return False

    def check_hidden_files(self):
        for file in self.meta['hidden_files'].copy():
            if not self.check_hide(file):
                self.meta['hidden_files'].remove(file)

    def check_state(self):
        path = self.path_var.get()
        if os.path.exists(path):
            if self.check_hide(path):
                self.state_lbl.config(text='The file is vanished!', fg='green')
                self.state_lbl.place(x=220, y=5)

            else:
                self.state_lbl.config(text='The file is not vanished', fg='red')
                self.state_lbl.place(x=200, y=5)

        else:
            self.state_lbl.config(text='')

    def browse(self):
        new_path = filedialog.askopenfilename()
        if new_path:
            new_path = os.path.normpath(new_path)
            self.path_var.set(new_path)

    def load_meta(self):
        if not os.path.exists(meta.pickle_path):
            parent = os.path.dirname(meta.pickle_path)
            if not os.path.exists(parent):
                os.mkdir(parent)

            subprocess.run(['attrib', '+h', f"{parent}"])

            d = {
                'log_file': meta.logfile,
                'hidden_files': [],
                'save_logs': 1
                 }
            save_obj(d, meta.pickle_name)

        return load_obj(meta.pickle_name)

    def update_savelogs(self):
        if self.meta['save_logs'] != (new_state := self.save_logs.get()):
            self.meta['save_logs'] = new_state
            save_obj(self.meta, meta.pickle_name)

    def update_logfile(self, logfile):
        if not os.path.samefile(self.meta['log_file'], logfile):
            self.last_activity = f"Logfile moved to <{logfile}>"
            self.logger.log(self.last_activity)

            self.logger.set_logfile(logfile)
            self.logger.log(f"Logfile moved here from <{self.meta['log_file']}>")

            self.meta['log_file'] = logfile
            save_obj(self.meta, meta.pickle_name)

            messagebox.showinfo('Moving Logfile', f'Log file successfully moved to <{logfile}>')

        else:
            messagebox.showwarning('Moving Logfile', 'The file selected already is logfile!')

    def add_hidden_file(self, file):
        if file not in self.meta['hidden_files']:
            self.meta['hidden_files'].append(file)
            save_obj(self.meta, meta.pickle_name)

    def remove_hidden_file(self, file):
        if file in self.meta['hidden_files']:
            self.meta['hidden_files'].remove(file)
            save_obj(self.meta, meta.pickle_name)

    def copy_path2clipboard(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.path_var.get())
        messagebox.showinfo(meta.title, 'Path successfully copied!')

    def init_menu(self):
        menu = tk.Menu(self.master)
        menu.add_command(label="Open LogFile", command=lambda: os.startfile(self.meta['log_file']))
        menu.add_command(label="Scan directory", command=lambda: dialogs.ScanDirectoryDialog(self))
        menu.add_command(label="Last Activity", command=lambda: messagebox.showinfo('Last Activity', self.last_activity))
        menu.add_command(label="Hidden Files", command=lambda: dialogs.HiddensDialog(self))
        menu.add_command(label="Setting", command=lambda: dialogs.SettingDialog(self))
        menu.add_command(label="About us", command=lambda: dialogs.AboutDialog(self.master))

        return menu


class Logger:
    def __init__(self, file):
        self.file = file
        self.check_new_file()

    def log(self, msg, **kwargs):
        return self._write_log(msg, **kwargs)

    def set_logfile(self, file):
        self.file = file
        self.check_new_file()

    def get_logfile(self):
        return self.file

    def check_new_file(self):
        if not os.path.exists(self.file) or os.path.getsize(self.file) <= 2:
            self.log('Log file created!', mode='w')

    def _write_log(self, msg, mode='a'):
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.file, mode) as file:
            file.write(f'[{time}]  {msg}\n')
