import os
import vtk
from PyQt5 import QtCore, QtWidgets
from gui.vtkwidget import VtkWidget
from gui.progress import ProgressBarFrame
from gui.datapanel import DataPanel
from gui.propspanel import PropsPanel
from core.datacontainer import DataContainer


#==================================================================================================
# MainWindow ======================================================================================
#==================================================================================================
class MainWindow(QtWidgets.QMainWindow):
  def __init__(self, qt_app):
    QtWidgets.QMainWindow.__init__(self)

    self.__qt_app = qt_app
    # This is the main guy. Almost all GUI elements are observers of this guy. It stores the data
    # and triggers events (e.g., when new data is loaded) to which its observers react.
    self.__data_container = DataContainer()

    self.__file_load_progress_bar = ProgressBarFrame(self, self.__qt_app)

    self.__add_menus()
    self.__setup_main_frame()

    # Setup the position and size of the main window
    desktop_widget = QtWidgets.QDesktopWidget()
    rect = desktop_widget.availableGeometry(desktop_widget.primaryScreen())
    self.move(rect.x(), rect.y())
    self.showMaximized()


  def __add_menus(self):
    # Load file(s)    
    load_files_action = QtWidgets.QAction('Load file(s)', self)
    load_files_action.setShortcut('Ctrl+L')
    load_files_action.triggered.connect(self.__on_load_files)
    # Load folder
    load_folder_action = QtWidgets.QAction('Load folder', self)
    load_folder_action.setShortcut('Ctrl+I')
    load_folder_action.triggered.connect(self.__on_load_folder)
    # Quit
    quit_action = QtWidgets.QAction('Quit', self)
    quit_action.setShortcut('Ctrl+Q')
    quit_action.triggered.connect(QtWidgets.qApp.quit)

    file_menu = self.menuBar().addMenu(r"&FILE")
    file_menu.addAction(load_files_action)
    file_menu.addAction(load_folder_action)
    file_menu.addSeparator()
    file_menu.addAction(quit_action)


  def __setup_main_frame(self):
    # Create the OpenGL-based VTK widget
    self.__vtk_widget = VtkWidget(self, self.__data_container, self.__file_load_progress_bar)
    self.setCentralWidget(self.__vtk_widget.widget)

    # Add the dock which shows the list of the loaded data (on the left in the main window)
    self.__data_panel = DataPanel(self.__data_container)
    self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.__data_panel.dock_widget)

    # Add the dock which shows the properties of the selected object (on the right in the main window)
    self.props_panel = PropsPanel(self.__data_container)
    self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.props_panel.dock_widget)


  def __on_load_files(self):
    #default_folder = r"C:\Users\papazov\Google Drive\research\data\models" # Windows
    default_folder = r"/local/data/zbrain/masks"

    # Let the user select the files (file_names[0] will be the list with the file names)
    file_names = QtWidgets.QFileDialog.getOpenFileNames(self, "Load file(s)", default_folder, r"All Files (*.*)")

    # Let the data_container load the files. The data_container will notify its observers that new data was loaded.
    self.__data_container.load_files(file_names[0], self.__file_load_progress_bar)


  def __on_load_folder(self):
    #default_folder = r"C:\Users\papazov\Google Drive\research\data\models" # Windows
    default_folder = r"/local/data/zbrain/masks/test_meshes"
  
    folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Load all files from a folder", default_folder)
    # Make sure we got an existing directory
    if not os.path.isdir(folder_name):
      return

    full_file_names = list()

    # Get the *full* file names
    for file_name in os.listdir(folder_name):
      full_file_names.append(folder_name + "/" + file_name) # works on Windows too

    # Let the data_container load the files. The data_container will notify its observers that new data was loaded.
    self.__data_container.load_files(full_file_names, self.__file_load_progress_bar)
