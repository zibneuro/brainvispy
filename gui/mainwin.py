import os
import vtk
from PyQt5 import QtCore, QtWidgets
import xml.etree.ElementTree as ET
from gui.vtkwidget import VtkWidget
from gui.progress import ProgressBarFrame
from gui.datapanel import DataPanel
from gui.propspanel import PropsPanel
from core.datacontainer import DataContainer
from IO.project import ProjectIO


#==================================================================================================
# MainWindow ======================================================================================
#==================================================================================================
class MainWindow(QtWidgets.QMainWindow):
  def __init__(self, qt_app):
    QtWidgets.QMainWindow.__init__(self)

    # This guy is used by several classes to indicate the progress of the heavy work
    self.__file_load_progress_bar = ProgressBarFrame(self, qt_app)

    # This is the main guy. Almost all GUI elements are observers of this guy. It stores the data
    # and triggers events (e.g., when new data is loaded/deleted and much more). The observers react
    # to these events.
    self.__data_container = DataContainer()

    # This guy handles the file/project IO
    self.__project_io = ProjectIO(self.__file_load_progress_bar)

    self.__add_menus()
    self.__setup_main_frame()

    # Load some info from a config file (like the folder where the user saved her last project)
    self.__config_file_name = "./brainvispy_config.xml"
    self.__load_config_file()

    # Change the title of the main window
    self.setWindowTitle("BrainVisPy")
    # Make sure that the main window appears (maximized) on the primary screen
    desktop_widget = QtWidgets.QDesktopWidget()
    rect = desktop_widget.availableGeometry(desktop_widget.primaryScreen())
    self.move(rect.x(), rect.y())
    self.showMaximized()


  def __add_menus(self):
    # Open project
    open_project_action = QtWidgets.QAction('Open project', self)
    open_project_action.setShortcut('Ctrl+O')
    open_project_action.triggered.connect(self.__on_open_project)
    # Load file(s)
    load_files_action = QtWidgets.QAction('Load file(s)', self)
    load_files_action.setShortcut('Ctrl+L')
    load_files_action.triggered.connect(self.__on_load_files)
    # Load folder
    load_folder_action = QtWidgets.QAction('Import folder', self)
    load_folder_action.setShortcut('Ctrl+I')
    load_folder_action.triggered.connect(self.__on_import_folder)
    # Save project
    save_project_action = QtWidgets.QAction('Save project', self)
    save_project_action.setShortcut('Ctrl+S')
    save_project_action.triggered.connect(self.__on_save_project)
    # Save as project
    save_project_as_action = QtWidgets.QAction('Save project as', self)
    save_project_as_action.setShortcut('Ctrl+Shift+S')
    save_project_as_action.triggered.connect(self.__on_save_project_as)
    # Quit
    quit_action = QtWidgets.QAction('Quit', self)
    quit_action.setShortcut('Ctrl+Q')
    quit_action.triggered.connect(self.close)

    file_menu = self.menuBar().addMenu("FILE")
    file_menu.addAction(open_project_action)
    file_menu.addAction(save_project_action)
    file_menu.addAction(save_project_as_action)
    file_menu.addSeparator()    
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
    self.__props_panel = PropsPanel(self.__data_container)
    self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__props_panel.dock_widget)


  def __on_open_project(self):
    project_file_name = QtWidgets.QFileDialog.getOpenFileName(self, "Open a BrainVisPy project", self.__open_project_folder, r"XML Files (*.xml)")
    if project_file_name[0]:
      # Save the folder the user loaded the project from
      self.__open_project_folder = os.path.split(project_file_name[0])[0]
      # Open the project
      errors = self.__project_io.open_project(project_file_name[0], self.__data_container, self.__vtk_widget)
      if not errors:
        print("All 6")


  def __on_load_files(self):
    # Let the user select the files (file_names[0] will be the list with the file names)
    file_names = QtWidgets.QFileDialog.getOpenFileNames(self, "Load file(s)", self.__load_files_folder, r"All files (*.*)")
    # Load the files. The data_container will notify its observers that new data was loaded.
    if file_names[0]:
      # Take the first file name and extract the folder from it
      self.__load_files_folder = os.path.split(file_names[0][0])[0]
      # Load the files
      self.__project_io.load_files(file_names[0], self.__data_container)


  def __on_import_folder(self):
    folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Import folder (load all files from a folder)", self.__import_folder)
    # Make sure we got an existing directory
    if os.path.isdir(folder_name):
      self.__import_folder = folder_name
      full_file_names = list()
      # Get the *full* file names
      for file_name in os.listdir(folder_name):
        full_file_names.append(folder_name + "/" + file_name) # works on Windows too
      # Load the files. The data_container will notify its observers that new data was loaded.
      self.__project_io.load_files(full_file_names, self.__data_container)


  def __on_save_project(self):
    # Ask the user to specify a project name if necessary
    if self.__project_io.has_file_name():
      self.__save_project()
    else:
      self.__on_save_project_as()


  def __on_save_project_as(self):
    # Ask the user to specify a project name if necessary
    project_file_name = QtWidgets.QFileDialog.getSaveFileName(self, "Save project as", self.__save_project_folder, r"XML Files (*.xml)")
    if project_file_name[0]:
      ext = os.path.splitext(project_file_name[0])[1].lower()
      if ext and ext == ".xml":
        project_file_name = project_file_name[0]
      else:
        project_file_name = project_file_name[0] + ".xml"
      # Now that we have the right file name, save the project
      self.__project_io.set_file_name(project_file_name)
      self.__save_project()


  def __save_project(self):
    try:
      self.__save_project_folder = os.path.split(self.__project_io.get_file_name())[0]
      self.__project_io.save_project(self.__data_container, self.__vtk_widget)
      print("saved '" + self.__project_io.get_file_name() + "'")
    except Exception as err:
      print(err)


  def __load_config_file(self):
    # First set these default names (in case we fail to open the config file)
    self.__open_project_folder = "./"
    self.__save_project_folder = "./"
    self.__import_folder = "./"
    self.__load_files_folder = "./"
    # Now try to open the file and read the true folder names
    try:
      config = ET.parse(self.__config_file_name).getroot()
      for element in config:
        if element.tag == "open_project_folder": self.__open_project_folder = element.text
        elif element.tag == "save_project_folder": self.__save_project_folder = element.text
        elif element.tag == "import_folder": self.__import_folder = element.text
        elif element.tag == "load_files_folder": self.__load_files_folder = element.text
    except Exception as exception:
      print("Could not load config stuff: " + str(exception))


  def __update_config_file(self):
    try:
      # First, create an XML object for the whole project
      xml_config = ET.Element("BrainVisPy_Config_File")
      # Save the current config stuff
      ET.SubElement(xml_config, "open_project_folder").text = self.__open_project_folder
      ET.SubElement(xml_config, "save_project_folder").text = self.__save_project_folder
      ET.SubElement(xml_config, "import_folder").text = self.__import_folder
      ET.SubElement(xml_config, "load_files_folder").text = self.__load_files_folder
      # Write the whole XML tree to file
      ET.ElementTree(xml_config).write(self.__config_file_name)
    except Exception as exception:
      print("Could not save the current config stuff: " + str(exception))


  def closeEvent(self, event):
    reply = QtWidgets.QMessageBox.question(self, "Question", "Quit?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
    if reply == QtWidgets.QMessageBox.Yes:
      # Save some info (like the folder of the current project and other stuff) to a config file (to have it for next time)
      self.__update_config_file()
      event.accept()
    else:
      event.ignore()
