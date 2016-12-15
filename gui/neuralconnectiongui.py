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
    self.__spin_box_precision = 2

    self.__ignore_on_weight_changed_callback = False

    # CREATE THE GUI ELEMENTS
    # The weight label
    self.__weight_label = QtWidgets.QLabel("weight:")
    # The weight spin box
    self.__weight_spin_box = QtWidgets.QDoubleSpinBox()
    self.__weight_spin_box.setMinimum(-10000)
    self.__weight_spin_box.setMaximum(10000)
    self.__weight_spin_box.setSingleStep(1/(10**self.__spin_box_precision))
    self.__weight_spin_box.setDecimals(self.__spin_box_precision)
    self.__weight_spin_box.valueChanged.connect(self.__on_weight_spin_box_changed)

    # The [min, max] range for the weight
    # min
    self.__min_weight_spin_box = QtWidgets.QDoubleSpinBox()
    self.__min_weight_spin_box.setMinimum(-10000)
    self.__min_weight_spin_box.setMaximum(10000)
    self.__min_weight_spin_box.setValue(-1)
    self.__min_weight_spin_box.setSingleStep(1/(10**self.__spin_box_precision))
    self.__min_weight_spin_box.setDecimals(self.__spin_box_precision)
    self.__min_weight_spin_box.valueChanged.connect(self.__on_min_weight_spin_box_changed)
    # max
    self.__max_weight_spin_box = QtWidgets.QDoubleSpinBox()
    self.__max_weight_spin_box.setMinimum(-10000)
    self.__max_weight_spin_box.setMaximum(10000)
    self.__max_weight_spin_box.setValue(1)
    self.__max_weight_spin_box.setDecimals(self.__spin_box_precision)
    self.__max_weight_spin_box.setSingleStep(1/(10**self.__spin_box_precision))
    self.__max_weight_spin_box.valueChanged.connect(self.__on_max_weight_spin_box_changed)
    # The button to create the weights at random
    self.__set_random_weight_btn = QtWidgets.QPushButton("set randomly from range")
    self.__set_random_weight_btn.clicked.connect(self.__on_set_random_weight_btn_clicked)
    
    # ADD THE GUI ELEMENTS TO A LAYOUT
    layout = QtWidgets.QVBoxLayout()
    # The weight
    weight_layout = QtWidgets.QGridLayout()
    weight_layout.addWidget(self.__weight_label, 0, 0, 1, -1, QtCore.Qt.AlignLeft)
    weight_layout.addWidget(self.__weight_spin_box, 1, 0)
    weight_frame = QtWidgets.QFrame()
    weight_frame.setLayout(weight_layout)
    layout.addWidget(weight_frame)
    # Weight range
    weight_range_layout = QtWidgets.QGridLayout()
    weight_range_layout.addWidget(QtWidgets.QLabel("weight range:"), 0, 0, 1, -1, QtCore.Qt.AlignLeft)
    weight_range_layout.addWidget(QtWidgets.QLabel("min:"), 1, 0, 1, 1, QtCore.Qt.AlignRight)
    weight_range_layout.addWidget(self.__min_weight_spin_box, 1, 1, 1, -1, QtCore.Qt.AlignLeft)
    weight_range_layout.addWidget(QtWidgets.QLabel("max:"), 2, 0, 1, 1, QtCore.Qt.AlignRight)
    weight_range_layout.addWidget(self.__max_weight_spin_box, 2, 1, 1, -1, QtCore.Qt.AlignLeft)
    weight_range_frame = QtWidgets.QFrame()
    weight_range_frame.setLayout(weight_range_layout)
    layout.addWidget(weight_range_frame)
    # Select random weight button
    layout.addWidget(self.__set_random_weight_btn)
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

    # Set the text of the weight label
    if num_neural_connections == 1:
      self.__weight_label.setText("weight:")
    else:
      self.__weight_label.setText("average weight:")

    ignore_callback = self.__ignore_on_weight_changed_callback
    self.__ignore_on_weight_changed_callback = True
    # Show the average weight to the user
    self.__weight_spin_box.setValue(self.__compute_average_weight(neural_connections))
    self.__ignore_on_weight_changed_callback = ignore_callback

    # Show this GUI element to the user
    self.show()


  def __compute_average_weight(self, neural_connections):
    weight_sum = 0
    for nc in neural_connections:
      weight_sum += nc.weight
    return weight_sum / len(neural_connections)


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


  def __on_min_weight_spin_box_changed(self):
    min_value = self.__min_weight_spin_box.value()
    max_value = self.__max_weight_spin_box.value()
    if min_value > max_value:
      self.__max_weight_spin_box.setValue(min_value)


  def __on_max_weight_spin_box_changed(self):
    min_value = self.__min_weight_spin_box.value()
    max_value = self.__max_weight_spin_box.value()
    if max_value < min_value:
      self.__min_weight_spin_box.setValue(max_value)


  def __on_set_random_weight_btn_clicked(self):
    if not self.__neural_connections:
      return
    min_value = self.__min_weight_spin_box.value()
    max_value = self.__max_weight_spin_box.value()
    # Loop over the neural connections and assign random weights
    for nc in self.__neural_connections:
      nc.set_weight(random.uniform(min_value, max_value))
    # Update the data container
    self.__data_container.neural_connections_changed(list(self.__neural_connections))
