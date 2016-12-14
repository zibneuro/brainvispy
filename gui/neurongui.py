import random
from core.datacontainer import DataContainer
from bio.neuron import Neuron
from PyQt5 import QtGui, QtWidgets, QtCore

class NeuronGUI(QtWidgets.QGroupBox):
  """This is the dock widget for the properties of a selected data item(s)"""
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has the wrong type")

    super().__init__("NEURONS")

    # Register yourself as an observer
    self.__data_container = data_container
    self.__data_container.add_observer(self)

    # These are the neurons whose properties we are going to display
    self.__neurons = list()
    self.__spin_box_precision = 2
    
    self.__ignore_on_threshold_changed_callback = False

    # CREATE THE GUI ELEMENTS
    # The threshold label
    self.__threshold_label = QtWidgets.QLabel("threshold:")
    # The threshold spin box
    self.__threshold_spin_box = QtWidgets.QDoubleSpinBox()
    self.__threshold_spin_box.setMinimum(-10000)
    self.__threshold_spin_box.setMaximum(10000)
    self.__threshold_spin_box.setSingleStep(1/(10**self.__spin_box_precision))
    self.__threshold_spin_box.setDecimals(self.__spin_box_precision)
    self.__threshold_spin_box.valueChanged.connect(self.__on_threshold_spin_box_changed)

    # The [min, max] range for the threshold
    # min
    self.__min_threshold_spin_box = QtWidgets.QDoubleSpinBox()
    self.__min_threshold_spin_box.setMinimum(-10000)
    self.__min_threshold_spin_box.setMaximum(10000)
    self.__min_threshold_spin_box.setValue(-1)
    self.__min_threshold_spin_box.setSingleStep(1/(10**self.__spin_box_precision))
    self.__min_threshold_spin_box.setDecimals(self.__spin_box_precision)
    self.__min_threshold_spin_box.valueChanged.connect(self.__on_min_threshold_spin_box_changed)
    # max
    self.__max_threshold_spin_box = QtWidgets.QDoubleSpinBox()
    self.__max_threshold_spin_box.setMinimum(-10000)
    self.__max_threshold_spin_box.setMaximum(10000)
    self.__max_threshold_spin_box.setValue(1)
    self.__max_threshold_spin_box.setDecimals(self.__spin_box_precision)
    self.__max_threshold_spin_box.setSingleStep(1/(10**self.__spin_box_precision))
    self.__max_threshold_spin_box.valueChanged.connect(self.__on_max_threshold_spin_box_changed)
    # The button to create the thresholds at random
    self.__set_random_threshold_btn = QtWidgets.QPushButton("set randomly from range")
    self.__set_random_threshold_btn.clicked.connect(self.__on_set_random_threshold_btn_clicked)

    # ADD THE GUI ELEMENTS TO A LAYOUT
    layout = QtWidgets.QVBoxLayout()
    # The threshold
    threshold_layout = QtWidgets.QGridLayout()
    threshold_layout.addWidget(self.__threshold_label, 0, 0, 1, -1, QtCore.Qt.AlignLeft)
    threshold_layout.addWidget(self.__threshold_spin_box, 1, 0)
    threshold_frame = QtWidgets.QFrame()
    threshold_frame.setLayout(threshold_layout)
    layout.addWidget(threshold_frame)
    # Threshold range
    threshold_range_layout = QtWidgets.QGridLayout()
    threshold_range_layout.addWidget(QtWidgets.QLabel("threshold range:"), 0, 0, 1, -1, QtCore.Qt.AlignLeft)
    threshold_range_layout.addWidget(QtWidgets.QLabel("min:"), 1, 0, 1, 1, QtCore.Qt.AlignRight)
    threshold_range_layout.addWidget(self.__min_threshold_spin_box, 1, 1, 1, -1, QtCore.Qt.AlignLeft)
    threshold_range_layout.addWidget(QtWidgets.QLabel("max:"), 2, 0, 1, 1, QtCore.Qt.AlignRight)
    threshold_range_layout.addWidget(self.__max_threshold_spin_box, 2, 1, 1, -1, QtCore.Qt.AlignLeft)
    threshold_range_frame = QtWidgets.QFrame()
    threshold_range_frame.setLayout(threshold_range_layout)
    layout.addWidget(threshold_range_frame)
    # Select random threshold button
    layout.addWidget(self.__set_random_threshold_btn)
    # Group the GUI elements together
    layout.setSpacing(1)
    self.setLayout(layout)
    self.hide()


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__neurons = self.__get_neurons(data)
      self.__update(self.__neurons)
    elif change == DataContainer.change_is_modified_neurons:
      self.__update(self.__neurons)


  def __get_neurons(self, models):
    neurons = list()
    for model in models:
      if isinstance(model, Neuron):
        neurons.append(model)
    return neurons


  def __update(self, neurons):
    num_neurons = len(neurons)

    # Make sure there are neurons to show
    if num_neurons == 0:
      self.hide()
      return

    # Set the text of the threshold label
    if num_neurons == 1:
      self.__threshold_label.setText("threshold:")
    else:
      self.__threshold_label.setText("average threshold:")

    ignore_callback = self.__ignore_on_threshold_changed_callback
    self.__ignore_on_threshold_changed_callback = True
    # Show the average neuron threshold to the user
    self.__threshold_spin_box.setValue(self.__compute_average_threshold(neurons))
    self.__ignore_on_threshold_changed_callback = ignore_callback

    # Show this GUI element to the user
    self.show()


  def __compute_average_threshold(self, neurons):
    threshold_sum = 0
    for neuron in neurons:
      threshold_sum += neuron.threshold
    return threshold_sum / len(neurons)


  def __on_threshold_spin_box_changed(self):
    if self.__ignore_on_threshold_changed_callback:
      return

    if not self.__neurons:
      return

    avg_threshold = self.__compute_average_threshold(self.__neurons)
    difference = self.__threshold_spin_box.value() - avg_threshold

    for neuron in self.__neurons:
      neuron.set_threshold(neuron.threshold + difference)

    self.__data_container.neurons_changed(list(self.__neurons))


  def __on_min_threshold_spin_box_changed(self):
    min_value = self.__min_threshold_spin_box.value()
    max_value = self.__max_threshold_spin_box.value()
    if min_value > max_value:
      self.__max_threshold_spin_box.setValue(min_value)


  def __on_max_threshold_spin_box_changed(self):
    min_value = self.__min_threshold_spin_box.value()
    max_value = self.__max_threshold_spin_box.value()
    if max_value < min_value:
      self.__min_threshold_spin_box.setValue(max_value)


  def __on_set_random_threshold_btn_clicked(self):
    if not self.__neurons:
      return
    min_value = self.__min_threshold_spin_box.value()
    max_value = self.__max_threshold_spin_box.value()
    # Loop over the neurons and assign random thresholds
    for neuron in self.__neurons:
      neuron.set_threshold(random.uniform(min_value, max_value))
    # Update the data container
    self.__data_container.neurons_changed(list(self.__neurons))
