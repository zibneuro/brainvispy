# Bundle everything to a single executable file

This is a short version of this tutorial: https://mborgerson.com/creating-an-executable-from-a-python-script. We are using **PyInstaller** to create the executable.

* Install **PyInstaller**. Open a command line tool and type in `pip install pyinstaller` (put `sudo` in front if you need to).
* **Bundle the code**. Navigate to the folder which contains **invipy.py** and run: `pyinstaller --onefile --windowed invipy.py`. This creates (among other things) a **dist** folder which contains the executable.

Actually, we call `pyinstaller` from a folder different than the one which contains **invipy.py** in order not to get all the binary stuff in the source code folder.
