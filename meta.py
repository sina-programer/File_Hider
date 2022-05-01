import os


title = 'File Hider'
main_root = os.getcwd()

config_name = 'config'
config_path = os.path.expanduser(rf'~\.File_Hider\{config_name}')

icon_name = 'icon.png'
icon_path = os.path.join(main_root, 'files', icon_name)

logfile_name = 'File_Hider.log'
logfile = os.path.join(main_root, logfile_name)

logfile_types = (('Log File', '*.log'),
              ('Plain Text File', '*.txt'), ('Plain Text File', '*.text'))

links = {
    'github': 'https://github.com/sina-programer',
    'telegram': 'https://t.me/sina_programer'
}

default_config = {
    'log_file': logfile,
    'hidden_files': [],
    'save_logs': 1
}
