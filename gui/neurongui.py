from core.datacontainer import DataContainer
from bio.neuron import Neuron
from PyQt5 import QtGui, QtWidgets, QtCore

class NeuronGUI(QtWidgets.QGroupBox):
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has the wrong type")

    super().__init__("NEURON")

    # Register yourself as an observer
    self.__data_container = data_container
    self.__data_container.add_observer(self)

    # CREATE THE GUI ELEMENTS
    self.__name_label = QtWidgets.QLabel("name:")
    self.__name_value = QtWidgets.QLabel("")
    self.__threshold_label = QtWidgets.QLabel("threshold:")
    self.__threshold_value = QtWidgets.QLabel("")

    # ADD THE GUI ELEMENTS TO A LAYOUT
    layout = QtWidgets.QGridLayout()
    layout.addWidget(self.__name_label, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
    layout.addWidget(self.__name_value, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
    layout.addWidget(self.__threshold_label, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
    layout.addWidget(self.__threshold_value, 1, 1, 1, 1, QtCore.Qt.AlignLeft)
    self.setLayout(layout)
    self.hide()


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__update(data)


  def __update(self, data):
    neurons = list()

    # Collect the neuron(s)    
    for item in data:
      if isinstance(item, Neuron):
        neurons.append(item)
    
    # We can deal with a single neuron
    if len(neurons) != 1:
      self.hide()
      return

    # Update the GUI elements
    self.__name_value.setText(neurons[0].name)
    self.__threshold_value.setText(str(round(neurons[0].threshold, 3)))

    # Show this GUI element to the user
    self.show()
