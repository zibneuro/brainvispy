Invipy is written in **Python3** and uses **PyQt5**,  **python-qt5-gl** and **VTK**.

# Install and Run

In the following, we describe how to install and run invipy on Windows and Linux.

## Windows

We use 64bit Windows 8.

* **Install PyQt5 and python-qt5-gl.** Check on google.

* **Install VTK.** Follow [these](doc/install_vtk_win.md) instructions.

* **Set up environment variables.** We assume that VTK is installed in **C:\Program Files\VTK\7.0.0**.
  * Add **C:\Program Files\VTK\7.0.0\bin** to the **Path** environment variable.
  * Add **C:\Program Files\VTK\7.0.0\lib\python3.5\site-packages\vtk;C:\Program Files\VTK\7.0.0\lib\python3.5\site-packages** to the **PYTHONPATH** environment variable (create one if it does not exist).

* **Run invipy.**
  * Check out this repository or download the code. Open a command prompt and go to the directory containing **invipy.py**. Run `python invipy.py`
  * Alternatively, read [here](doc/single_executable_file.md) how to create a single executable file.


## Linux

We use 64bit Ubuntu 14.

* **Install PyQt5 and python-qt5-gl.** Check on google.

* **Install VTK.** Follow [these](doc/install_vtk_linux.md) instructions.

* **Set up environment variables.** We assume that VTK is installed in **/local/usr/vtk-7.0.0**.
  * Add **/local/usr/vtk-7.0.0/lib** to the **LD_LIBRARY_PATH** environment variable.
  * Add **/local/usr/vtk-7.0.0/lib/python3.5/site-packages:/local/usr/vtk-7.0.0/lib/python3.5/site-packages/vtk** to the **PYTHONPATH** environment variable.

* **Run invipy.**
  * Check out this repository or download the code. Open a command prompt and go to the directory containing **invipy.py**. Run `python invipy.py`
  * Alternatively, read [here](doc/single_executable_file.md) how to create a single executable file.
