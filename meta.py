import os


class Geometry:
    width = 500
    height = 80

    scr_width = 0
    scr_height = 0

    start_width = 0
    start_height = 0

    @staticmethod
    def set_screen_geometry(w, h):
        Geometry.scr_width = int(w)
        Geometry.start_width = int((Geometry.scr_width / 2) - 250)
        Geometry.scr_height = int(h)
        Geometry.start_height = int((Geometry.scr_height / 2) - 150)

    @staticmethod
    def get_geometry():
        return f"{Geometry.width}x{Geometry.height}+{Geometry.start_width}+{Geometry.start_height}"


title = 'File Hider'
main_root = os.getcwd()
USER = os.getlogin()

pickle_name = 'meta'
pickle_path = rf'C:\Users\{USER}\.File_Hider\{pickle_name}'
pickle_parent = os.path.dirname(pickle_path)

icon_name = 'icon.ico'
icon = os.path.join(main_root, 'files', icon_name)

logfile_name = 'File_Hider.log'
logfile = os.path.join(main_root, logfile_name)


file_types = (('Log File', '*.log'),
              ('Plain Text File', '*.txt'), ('Plain Text File', '*.text'))


links = {
    'github': 'https://github.com/sina-programer',
    'instagram': 'https://www.instagram.com/sina.programer',
    'telegram': 'https://t.me/sina_programer'
}


help_msg = ''' This Windows program converts your files and folders
    into system files so that they cannot be displayed.\n
1_ You can use the browse button to select your target\nor enter the target address manually
2_ Just click hide or show button to complete the process
3_ and all your activities are recorded in a log file in the current directory'''
