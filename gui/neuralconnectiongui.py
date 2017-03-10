from core.datacontainer import DataContainer
from bio.neuralconnection import NeuralConnection
from PyQt5 import QtGui, QtWidgets, QtCore

class NeuralConnectionGUI(QtWidgets.QGroupBox):
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has the wrong type")

    super().__init__("NEURAL CONNECTION")

    # Register yourself as an observer
    self.__data_container = data_container
    self.__data_container.add_observer(self)

    # CREATE THE GUI ELEMENTS
    self.__name_label = QtWidgets.QLabel("name:")
    self.__name_value = QtWidgets.QLabel("")
    self.__weight_label = QtWidgets.QLabel("weight:")
    self.__weight_value = QtWidgets.QLabel("")

    # ADD THE GUI ELEMENTS TO A LAYOUT
    layout = QtWidgets.QGridLayout()
    layout.addWidget(self.__name_label, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
    layout.addWidget(self.__name_value, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
    layout.addWidget(self.__weight_label, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
    layout.addWidget(self.__weight_value, 1, 1, 1, 1, QtCore.Qt.AlignLeft)
    self.setLayout(layout)
    self.hide()


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__update(data)


  def __update(self, data):
    naural_connections = list()

    # Collect the neural connections
    for item in data:
      if isinstance(item, NeuralConnection):
        naural_connections.append(item)
    
    # We can deal with a single neural connection
    if len(naural_connections) != 1:
      self.hide()
      return

    # Update the GUI elements
    self.__name_value.setText(naural_connections[0].name)
    self.__weight_value.setText(str(naural_connections[0].weight))

    # Show this GUI element to the user
    self.show()
