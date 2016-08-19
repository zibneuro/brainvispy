from core.datacontainer import DataContainer
from vis.vtkpoly import VtkPolyModel
from vis.vtkvol import VtkVolumeModel
from .polygui import VtkPolyModelGUI
from .volgui import VtkVolumeModelGUI
from PyQt5 import QtCore, QtWidgets

class PropsPanel(QtWidgets.QDockWidget):
  """This is the dock widget for the properties of a selected models(s). It has a list showing the
  selected models and specialized GUI elements which show the properties of polygonal and volume
  models."""
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has the wrong type")

    super().__init__("properties panel")
    self.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)

    # Register yourself as an observer
    self.__data_container = data_container;
    self.__data_container.add_observer(self)

    # The selection list with its label
    self.__selection_list_label = QtWidgets.QLabel("no selected objects")
    self.__qt_list_widget = QtWidgets.QListWidget()
    self.__qt_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
    self.__qt_list_widget.setFocusPolicy(QtCore.Qt.NoFocus)
    dock_layout = QtWidgets.QVBoxLayout()
    dock_layout.addWidget(self.__selection_list_label)
    dock_layout.addWidget(self.__qt_list_widget)
    dock_layout.setAlignment(self.__selection_list_label, QtCore.Qt.AlignTop)
    dock_layout.setAlignment(self.__qt_list_widget, QtCore.Qt.AlignTop)
    dock_layout.setAlignment(QtCore.Qt.AlignTop)

    # The GUIs for the volume and poly and models
    dock_layout.addWidget(VtkVolumeModelGUI(self.__data_container))
    dock_layout.addWidget(VtkPolyModelGUI(self.__data_container))    

    # Group everything in a frame
    dock_frame = QtWidgets.QFrame()
    dock_frame.setLayout(dock_layout)
    # Setup the dock
    self.setWidget(dock_frame)


  def observable_changed(self, change, data):
    # Decide what to the depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__update(data)


  def __update(self, models):
    # Update the label above the qt list widget
    num_models = len(models)
    if num_models <= 0: self.__selection_list_label.setText("no selected objects")
    elif num_models == 1: self.__selection_list_label.setText("1 selected object:")
    else: self.__selection_list_label.setText(str(num_models) + " selected objects:")

    self.__qt_list_widget.clear()

    # Insert the volume models on top and the poly models at the bottom of the list
    for model in models:
      if isinstance(model, VtkVolumeModel):
        self.__qt_list_widget.insertItem(0, QtWidgets.QListWidgetItem(model.name))  
      elif isinstance(model, VtkPolyModel):
        self.__qt_list_widget.insertItem(self.__qt_list_widget.count(), QtWidgets.QListWidgetItem(model.name))
