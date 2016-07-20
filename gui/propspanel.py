from core.modelview import Observer
from core.datacontainer import DataContainer
from vis.vtkpoly import VtkPolyModel
from vis.vtkvol import VtkVolumeModel
from .polygui import VtkPolyModelGUI
from PyQt5 import QtCore, QtWidgets

class PropsPanel(Observer):
  """This is the dock widget for the properties of a selected data item(s)"""
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has the wrong type")

    # Register yourself as an observer
    self.__data_container = data_container;
    self.__data_container.add_observer(self)

    # These lists keep the models (objects) we have
    self.__poly_models = list()
    self.__volume_models = list()

    # The selection list with its label
    self.__selection_list_label = QtWidgets.QLabel("no selected objects")
    self.__qt_list_widget = QtWidgets.QListWidget()
    self.__qt_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
    dock_layout = QtWidgets.QVBoxLayout()
    dock_layout.addWidget(self.__selection_list_label)
    dock_layout.addWidget(self.__qt_list_widget)
    dock_layout.setAlignment(self.__selection_list_label, QtCore.Qt.AlignTop)
    dock_layout.setAlignment(self.__qt_list_widget, QtCore.Qt.AlignTop)
    dock_layout.setAlignment(QtCore.Qt.AlignTop)

    # The GUI for the poly models
    self.__poly_models_gui = VtkPolyModelGUI(self.__data_container)
    self.__poly_models_gui.hide()
    dock_layout.addWidget(self.__poly_models_gui.gui_widget)

    # Group everything in a frame
    dock_frame = QtWidgets.QFrame()
    dock_frame.setLayout(dock_layout)
    # Create the dock widget
    self.dock_widget = QtWidgets.QDockWidget("properties panel")
    self.dock_widget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
    self.dock_widget.setWidget(dock_frame)


  def observable_changed(self, change, data):
    # Decide what to the depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__set_models(data)


  def __set_models(self, models):
    self.__poly_models = list()
    self.__volume_models = list()
    
    # Get the poly and volume models in separate lists
    for model in models:
      if isinstance(model, VtkPolyModel):
        self.__poly_models.append(model)
      elif isinstance(model, VtkVolumeModel):
        self.__volume_models.append(model)

    self.__update_qt_list_widget()

    # Update the GUI for the poly models
    self.__poly_models_gui.set_models(self.__poly_models)
    if len(self.__poly_models) > 0:
      self.__poly_models_gui.show()
    else:
      self.__poly_models_gui.hide()


  def __update_qt_list_widget(self):
    # Update the label above the qt list widget
    num_models = len(self.__poly_models) + len(self.__volume_models)
    if num_models <= 0: self.__selection_list_label.setText("no selected objects")
    elif num_models == 1: self.__selection_list_label.setText("1 selected object:")
    else: self.__selection_list_label.setText(str(num_models) + " selected objects:")

    # Update the qt list widget
    self.__qt_list_widget.clear()
    for model in self.__poly_models:
      self.__qt_list_widget.insertItem(0, QtWidgets.QListWidgetItem(model.name))
    for model in self.__volume_models:
      self.__qt_list_widget.insertItem(0, QtWidgets.QListWidgetItem(model.name))
