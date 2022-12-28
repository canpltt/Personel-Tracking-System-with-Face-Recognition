import cx_Freeze
import sys

base=None

if sys.platform=='win32':
    base="Win32GUI"
executables=[cx_Freeze.Executable("main.py",base=base)]

cx_Freeze.setup(
    name="Personel Takip Sistemi",
    options={"build.exe":{"packages":["tkinter,"],"include_files":["Logfile.log","cameras.pkl","face_enc"]}},
    version="0.1",
    description="Yüz Tanıma Algoritması ile Personel Takip Sistemi",
    executables=executables
)






