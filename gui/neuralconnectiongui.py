import random
from core.datacontainer import DataContainer
from bio.neuralconnection import NeuralConnection
from PyQt5 import QtGui, QtWidgets, QtCore

class NeuralConnectionGUI(QtWidgets.QGroupBox):
  """This is the dock widget for the properties of a selected data item(s)"""
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has the wrong type")

    super().__init__("NEURAL CONNECTION")

    # Register yourself as an observer
    self.__data_container = data_container
    self.__data_container.add_observer(self)

    # These are the neural connections whose properties we are going to display
    self.__neural_connections = list()
    self.__spin_box_precision = 3

    self.__ignore_on_weight_changed_callback = False

    # CREATE THE GUI ELEMENTS
    # The weight label
    self.__weight_label = QtWidgets.QLabel("threshold potential:")
    # The threshold potential spin box
    self.__weight_spin_box = QtWidgets.QDoubleSpinBox()
    self.__weight_spin_box.setMinimum(-10000)
    self.__weight_spin_box.setMaximum(10000)
    self.__weight_spin_box.setSingleStep(1/(10**self.__spin_box_precision))
    self.__weight_spin_box.setDecimals(self.__spin_box_precision)
    self.__weight_spin_box.valueChanged.connect(self.__on_weight_spin_box_changed)

    # ADD THE GUI ELEMENTS TO A LAYOUT
    layout = QtWidgets.QVBoxLayout()
    # The threshold potential
    threshold_potential_layout = QtWidgets.QGridLayout()
    threshold_potential_layout.addWidget(self.__weight_label, 0, 0, 1, -1, QtCore.Qt.AlignLeft)
    threshold_potential_layout.addWidget(self.__weight_spin_box, 1, 0)
    threshold_potential_frame = QtWidgets.QFrame()
    threshold_potential_frame.setLayout(threshold_potential_layout)
    layout.addWidget(threshold_potential_frame)
    # Group the GUI elements together
    layout.setSpacing(1)
    self.setLayout(layout)
    self.hide()


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__neural_connections = self.__get_neural_connections(data)
      self.__update(self.__neural_connections)
    elif change == DataContainer.change_is_modified_neural_connections:
      self.__update(self.__neural_connections)


  def __get_neural_connections(self, data_items):
    neural_connections = list()
    for item in data_items:
      if isinstance(item, NeuralConnection):
        neural_connections.append(item)
    return neural_connections


  def __update(self, neural_connections):
    # How many neural connections do we have:
    num_neural_connections = len(neural_connections)

    # Make sure there are some to show
    if num_neural_connections == 0:
      self.hide()
      return

    # Set the text of the threshold potential label
    if num_neural_connections == 1:
      self.__weight_label.setText("weight:")
    else:
      self.__weight_label.setText("average weight:")

    ignore_callback = self.__ignore_on_weight_changed_callback
    self.__ignore_on_weight_changed_callback = True
    # Show it to the user
    self.__weight_spin_box.setValue(self.__compute_average_weight(neural_connections))
    self.__ignore_on_weight_changed_callback = ignore_callback

    # Show this GUI element to the user
    self.show()


  def __compute_average_weight(self, neural_connections):
    avg_weight = 0
    for nc in neural_connections:
      avg_weight += nc.weight
    return avg_weight / len(neural_connections)


  def __on_weight_spin_box_changed(self):
    if self.__ignore_on_weight_changed_callback:
      return

    if len(self.__neural_connections) == 0:
      return

    avg_weight = self.__compute_average_weight(self.__neural_connections)
    difference = self.__weight_spin_box.value() - avg_weight

    for nc in self.__neural_connections:
      nc.set_weight(nc.weight + difference)

    self.__data_container.neural_connections_changed(list(self.__neural_connections))
