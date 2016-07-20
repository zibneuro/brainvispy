# Install VTK on Windows

We build VTK from source using CMake and a Windows compiler (here, we employ the freely available Visual Studio Express 2013 for desktop).

* Install CMake and VS Express 2013 for desktop (this is trivial).
* Download the latest stable VTK source code (at the time of writing it is 7.0.0) from http://www.vtk.org/download/.
* Unzip the file, enter the main directory and create a new folder (usually) called **build**.
* Open CMake and fill in the first two lines as shown in the screenshot (you should change **C:\Users\papazov\Software** to the folder where you downloaded VTK):

![Cmake Windows screenshot 1](cmake_win_screenshot_1.PNG "")

* Hit **Configure** and set up the dialog which pops up as shown here:

![Cmake Windows screenshot 1](cmake_win_screenshot_2.PNG "")

* Hit **Finish**. CMake starts the configuration process. Once it is done, change the blue marked entries to the shown vaules:

![Cmake Windows screenshot 3](cmake_win_screenshot_3.PNG "")

* Hit **Configure** again and when it's done hit **Generate**. Close CMake when the generating is done.
* Go to the **build** directory and open the **VTK.sln** file with VS Express 2013 (eventually as admin).
* Right-click on **INSTALL** and select **Build**:

![VS Express Windows screenshot 1](vs_express_win_screenshot_1.PNG "")

* It takes a while to build VTK. At the end, it should be in **C:\Program Files\VTK\7.0.0**.
