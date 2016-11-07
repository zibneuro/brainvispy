from core.datacontainer import DataContainer
from vis.vtkpoly import VtkPolyModel
from PyQt5 import QtGui, QtWidgets, QtCore

class CreateNeuronsGUI(QtWidgets.QGroupBox):
  """This is the dock widget for the properties of a selected data item(s)"""
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has the wrong type")

    super().__init__("neurons")

    # Register yourself as an observer
    self.__data_container = data_container
    self.__data_container.add_observer(self)

    self.__poly_models = list()

    # The box where the user enters the number of neurons to create
    self.__num_neurons_spin_box = QtWidgets.QSpinBox()
    self.__num_neurons_spin_box.setMinimum(1)
    self.__num_neurons_spin_box.setMaximum(100)
    self.__num_neurons_spin_box.setValue(10)
    self.__num_neurons_spin_box.setSingleStep(1)
    # The create neurons button
    self.__create_neurons_btn = QtWidgets.QPushButton("create")
    self.__create_neurons_btn.clicked.connect(self.__on_create_neurons_button_clicked)

    # Add the GUI elements to a layout
    layout = QtWidgets.QGridLayout()
    layout.addWidget(self.__num_neurons_spin_box, 0, 0)
    layout.addWidget(self.__create_neurons_btn, 0, 1)
    # Group the GUI elements together
    self.setLayout(layout)
    self.hide()


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__update(data)


  def __update(self, models):
    self.__poly_models = list()

    # Get the poly models only
    for model in models:
      if isinstance(model, VtkPolyModel):
        self.__poly_models.append(model)

    if self.__poly_models:
      self.show()
    else:
      self.hide()


  def __on_create_neurons_button_clicked(self):
    if not self.__poly_models:
      return
