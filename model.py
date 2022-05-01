from tkinter import messagebox, filedialog
import tkinter as tk

from datetime import datetime
from functools import wraps

import subprocess
import pickle
import os

import dialogs
import meta


def get_geometry(scr_width, scr_height, width=500, height=80):
    scr_width = int(scr_width)
    scr_height = int(scr_height)
    start_width = int((scr_width / 2) - 250)
    start_height = int((scr_height / 2) - 150)

    return f"{width}x{height}+{start_width}+{start_height}"


def save_config(obj):
    try:
        parent = os.path.dirname(meta.config_path)
        if not os.path.exists(parent):
            os.mkdir(parent)

        with open(meta.config_path, 'wb') as file:
            return pickle.dump(obj, file)

    except Exception:
        messagebox.showerror('ERROR', "Can't save new setting!")


def load_config():
    if not os.path.exists(meta.config_path):
        parent = os.path.dirname(meta.config_path)
        if not os.path.exists(parent):
            os.mkdir(parent)

        subprocess.run(['attrib', '+h', f"{parent}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        save_config(meta.default_config)

    try:
        with open(meta.config_path, 'rb') as file:
            return pickle.load(file)

    except Exception:
        pass


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

        self.config = load_config()
        self.logger = Logger(self.config['log_file'])
        self.last_activity = 'You have not been active yet!'
        self.check_hidden_files()

        self.save_logs = tk.IntVar()
        self.save_logs.set(self.config['save_logs'])
        self.path_var = tk.StringVar()
        self.path_var.trace('w', lambda *args: self.check_state())

        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(pady=8)
        padding = {'pady': 3, 'padx': 8}
        self.state_lbl = tk.Label(self.main_frame)
        self.state_lbl.grid(column=2, row=1, **padding)
        tk.Entry(self.main_frame, width=50, textvariable=self.path_var).grid(column=2, row=2, **padding)
        tk.Button(self.main_frame, text='Copy', width=8, command=self.copy_path2clipboard).grid(column=3, row=1, **padding)
        tk.Button(self.main_frame, text='Browse', width=8, command=self.browse).grid(column=3, row=2, **padding)
        tk.Button(self.main_frame, text='Hide', width=8, command=self.hide_target).grid(column=1, row=1, **padding)
        tk.Button(self.main_frame, text='Show', width=8, command=self.show_target).grid(column=1, row=2, **padding)

    @path_checker
    def show_target(self, path):
        self.remove_hidden_file(path)
        if self.check_hide(path):
            command = ['attrib', '-s', '-h', f"{path}"]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            self.check_state()

            self.last_activity = f"Show  {path}"
            if self.save_logs.get():
                self.logger.info(self.last_activity)
            messagebox.showinfo('File Hider', 'The target was successfully non-vanished!')

        else:
            messagebox.showwarning('File Hider', 'The target is non-vanished now!')

    @path_checker
    def hide_target(self, path):
        self.add_hidden_file(path)
        if not self.check_hide(path):
            command = ['attrib', '+s', '+h', f"{path}"]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            self.check_state()

            self.last_activity = f"Hide  {path}"
            if self.save_logs.get():
                self.logger.info(self.last_activity)
            messagebox.showinfo('File Hider', 'The target was successfully vanished!')

        else:
            messagebox.showwarning('File Hider', 'The target is vanished now!')

    def check_hide(self, path):
        result = subprocess.check_output(['attrib', f"{path}"], stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL).decode().lower()
        result = result[:21]
        if 'h' in result:
            return True
        return False

    def check_hidden_files(self):
        for file in self.config['hidden_files'].copy():
            if not self.check_hide(file):
                self.config['hidden_files'].remove(file)

    def check_state(self):
        path = self.path_var.get()
        if os.path.exists(path):
            if self.check_hide(path):
                self.state_lbl.config(text='The file is vanished!', fg='green')
            else:
                self.state_lbl.config(text='The file is non-vanished', fg='red')
        else:
            self.state_lbl.config(text='')

    def browse(self):
        new_path = filedialog.askopenfilename()
        if new_path:
            new_path = os.path.normpath(new_path)
            self.path_var.set(new_path)

    def update_savelogs(self):
        if self.config['save_logs'] != (new_state := self.save_logs.get()):
            self.config['save_logs'] = new_state
            save_config(self.config)

    def update_logfile(self, logfile):
        if not os.path.samefile(self.config['log_file'], logfile):
            self.last_activity = f"Logfile moved to <{logfile}>"
            self.logger.info(self.last_activity)

            self.logger.set_logfile(logfile)
            self.logger.info(f"Logfile moved here from <{self.config['log_file']}>")

            self.config['log_file'] = logfile
            save_config(self.config, self.logger)

            messagebox.showinfo('Moving Logfile', f'Log file successfully moved to <{logfile}>')

        else:
            messagebox.showwarning('Moving Logfile', 'The file selected already is logfile!')

    def add_hidden_file(self, file):
        if file not in self.config['hidden_files']:
            self.config['hidden_files'].append(file)
            save_config(self.config)

    def remove_hidden_file(self, file):
        if file in self.config['hidden_files']:
            self.config['hidden_files'].remove(file)
            save_config(self.config)

    def copy_path2clipboard(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.path_var.get())
        messagebox.showinfo(meta.title, 'Path successfully copied!')

    def init_menu(self):
        menu = tk.Menu(self.master)
        menu.add_command(label="Open LogFile", command=lambda: os.startfile(self.config['log_file']))
        menu.add_command(label="Scan directory", command=lambda: dialogs.ScanDirectoryDialog(self))
        menu.add_command(label="Last Activity", command=lambda: messagebox.showinfo('Last Activity', self.last_activity))
        menu.add_command(label="Hidden Files", command=lambda: dialogs.HiddensDialog(self))
        menu.add_command(label="Setting", command=lambda: dialogs.SettingDialog(self))
        menu.add_command(label="About us", command=lambda: dialogs.AboutDialog(self.master))

        return menu


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]


class Logger(metaclass=MetaSingleton):
    levels = {
        1: 'INFO',
        2: 'WARNING',
        3: 'ERROR',
        4: 'BUG',
        5: 'CRITICAL'
    }

    def __init__(self, file, level=1):
        self.file = file
        self.level = level
        self.check_is_new_file()

    def log(self, msg, level=1):
        return self._write_log(msg, level=level)

    def info(self, msg):
        return self._write_log(msg, level=1)

    def warning(self, msg):
        return self._write_log(msg, level=2)

    def error(self, msg):
        return self._write_log(msg, level=3)

    def bug(self, msg):
        return self._write_log(msg, level=4)

    def critical(self, msg):
        return self._write_log(msg, level=5)

    def set_logfile(self, file):
        self.file = file
        self.check_is_new_file()

    def get_logfile(self):
        return self.file

    def change_level(self, level):
        if 1 <= level <= 5:
            self.level = level

    def check_is_new_file(self):
        if not os.path.exists(self.file) or os.path.getsize(self.file) <= 1:
            self.info('Log file created!')

    def _write_log(self, msg, level):
        if level >= self.level:
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.file, 'a') as file:
                file.write(f'[{Logger.levels[level]:<8}] [{time}]  {msg}\n')
