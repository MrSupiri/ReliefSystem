import os
import sys
from cx_Freeze import setup, Executable

os.environ['TCL_LIBRARY'] = r'C:\Users\isala\AppData\Local\Programs\Python\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\isala\AppData\Local\Programs\Python\Python36\tcl\tk8.6'

base = None

sys.argv.append('build')

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [Executable("Relief_System.py", base=base, icon="data/favicon.ico")]

setup(
    name='RCGAdmin',
    packages=[''],
    url='',
    license='',
    author='Isala Piyarisi',
    author_email='isalap99@gmail.com',
    description='',
    options={"build_exe": {"packages": ["tkinter", "os", "sqlite3", "logging", "sys", "datetime", "time",
                                        'urllib', 'json'],
                           "include_files": ["data", "tcl86t.dll", "tk86t.dll"]}},
    version="0.01",
    executables=executables
)
