# cx_freeze script to generate a executable
# to run it, type in a command-line interface
# python setup.py build

import sys
import matplotlib
from cx_Freeze import setup, Executable

# replace base by None if a debug console is required
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {"includes":["matplotlib.backends.backend_qt4agg","scipy.special._ufuncs_cxx",
                                 "scipy.integrate","scipy.integrate.vode",
                                 "scipy.integrate.lsoda","scipy.sparse.csgraph._validation"],
                     "include_files":[(matplotlib.get_data_path(), "mpl-data"),
                                      ('application_edit.ico','application_edit.ico'),
                                      ('trad.txt','trad.txt'),
                                      ('settings.ini','settings.ini')],
                     "excludes":[]}

setup(
    name = "TopoPyGUI",
    options = {"build_exe": build_exe_options},
    version = "8.1",
    description = "Draw topographic maps",
    executables = [Executable("TopoPyGUI.py", base = base)],
)

