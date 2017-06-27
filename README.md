BrainVisPy is written in **Python3** and uses **PyQt5**,  **python-qt5-gl**, **numpy** and **VTK**.

# Install and Run

In the following, we describe how to install and run BrainVisPy on Windows, Linux and OS X.

## Windows

We use 64bit Windows 8.

* **Install PyQt5, python-qt5-gl and numpy.** Check on google.

* **Install VTK.** Follow [these](doc/install_vtk_win.md) instructions.

* **Set up environment variables.** We assume that VTK is installed in **C:\Program Files\VTK\7.0.0**.
  * Add **C:\Program Files\VTK\7.0.0\bin** to the **Path** environment variable.
  * Add **C:\Program Files\VTK\7.0.0\lib\python3.5\site-packages\vtk;C:\Program Files\VTK\7.0.0\lib\python3.5\site-packages** to the **PYTHONPATH** environment variable (create one if it does not exist).

* **Run BrainVisPy.**
  * Check out this repository or download the code. Open a command prompt and go to the directory containing **main.py**. Run `python3 main.py`
  * Alternatively, read [here](doc/single_executable_file.md) how to create a single executable file.


## Linux

We use 64bit Ubuntu 14.

* **Install PyQt5, python-qt5-gl and numpy.** Check on google.

* **Install VTK.** Follow [these](doc/install_vtk_linux.md) instructions.

* **Set up environment variables.** We assume that VTK is installed in **/local/usr/vtk-7.0.0**.
  * Add **/local/usr/vtk-7.0.0/lib** to the **LD_LIBRARY_PATH** environment variable.
  * Add **/local/usr/vtk-7.0.0/lib/python3.5/site-packages:/local/usr/vtk-7.0.0/lib/python3.5/site-packages/vtk** to the **PYTHONPATH** environment variable.

* **Run BrainVisPy.**
  * Check out this repository or download the code. Open a command prompt and go to the directory containing **main.py**. Run `python3 main.py`
  * Alternatively, read [here](doc/single_executable_file.md) how to create a single executable file.

## OS X

We use OS X El Capitan (Version 10.11.6).

* **Install PyQt5, python-qt5-gl and numpy.** Check on google.

* **Install VTK.** Follow [these](doc/install_vtk_osx.md) instructions.

* **Set up environment variables.** We assume that VTK is installed in **/usr/local/VTK/7.0**.
  * Add **/usr/local/VTK/7.0/lib** to the **DYLD_LIBRARY_PATH** environment variable.
  * Add **/usr/local/VTK/7.0/lib/python3/site-packages:/usr/local/VTK/7.0/lib/python3/site-packages/vtk** to the **PYTHONPATH** environment variable.

  You can do both by adding

      export DYLD_LIBRARY_PATH=/usr/local/VTK/7.0/lib:$DYLD_LIBRARY_PATH
      export PYTHONPATH=/usr/local/VTK/7.0/lib/python3/site-packages:/usr/local/VTK/7.0/lib/python3/site-packages/vtk

  to the file `.bash_profile` which is in your home directory (create it if it doesn't exist).

* **Run BrainVisPy.**
  * Check out this repository or download the code. Open a command prompt and go to the directory containing **main.py**. Run `python3 main.py`
  * Alternatively, read [here](doc/single_executable_file.md) how to create a single executable file.

# Understanding the Code

Check [this](doc/understanding_the_code.md) description.

