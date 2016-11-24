import random
from core.datacontainer import DataContainer
from anatomy.neuron import Neuron
from PyQt5 import QtGui, QtWidgets, QtCore

class NeuronsGUI(QtWidgets.QGroupBox):
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
    self.__spin_box_precision = 3

    # CREATE THE GUI ELEMENTS
    # The threshold potential label
    self.__threshold_potential_label = QtWidgets.QLabel("threshold potential:")
    # The threshold potential spin box
    self.__threshold_potential_spin_box = QtWidgets.QDoubleSpinBox()
    self.__threshold_potential_spin_box.setMinimum(-10000)
    self.__threshold_potential_spin_box.setMaximum(10000)
    self.__threshold_potential_spin_box.setSingleStep(1/(10**self.__spin_box_precision))
    self.__threshold_potential_spin_box.setDecimals(self.__spin_box_precision)
    self.__threshold_potential_spin_box.valueChanged.connect(self.__update_set_potential_threshold_btn)
    # The button which the user have to select in order to modify the threshold
    self.__set_potential_threshold_btn = QtWidgets.QPushButton("set")
    self.__set_potential_threshold_btn.setEnabled(False)
    self.__set_potential_threshold_btn.clicked.connect(self.__on_set_potential_threshold_btn_clicked)

    # The [min, max] range for the threshold potential
    # min
    self.__threshold_potential_min_spin_box = QtWidgets.QDoubleSpinBox()
    self.__threshold_potential_min_spin_box.setMinimum(-10000)
    self.__threshold_potential_min_spin_box.setMaximum(10000)
    self.__threshold_potential_min_spin_box.setValue(-1)
    self.__threshold_potential_min_spin_box.setSingleStep(1/(10**self.__spin_box_precision))
    self.__threshold_potential_min_spin_box.setDecimals(self.__spin_box_precision)
    self.__threshold_potential_min_spin_box.valueChanged.connect(self.__on_threshold_potential_min_spin_box_changed)
    # max
    self.__threshold_potential_max_spin_box = QtWidgets.QDoubleSpinBox()
    self.__threshold_potential_max_spin_box.setMinimum(-10000)
    self.__threshold_potential_max_spin_box.setMaximum(10000)
    self.__threshold_potential_max_spin_box.setValue(1)
    self.__threshold_potential_max_spin_box.setDecimals(self.__spin_box_precision)
    self.__threshold_potential_max_spin_box.setSingleStep(1/(10**self.__spin_box_precision))
    self.__threshold_potential_max_spin_box.valueChanged.connect(self.__on_threshold_potential_max_spin_box_changed)
    # The button to create the threshold potentials at random
    self.__select_random_threshold_potential_btn = QtWidgets.QPushButton("select randomly from range")
    self.__select_random_threshold_potential_btn.clicked.connect(self.__on_select_random_threshold_potential_btn_clicked)

    # ADD THE GUI ELEMENTS TO A LAYOUT
    layout = QtWidgets.QVBoxLayout()
    # The threshold potential
    threshold_potential_layout = QtWidgets.QGridLayout()
    threshold_potential_layout.addWidget(self.__threshold_potential_label, 0, 0, 1, -1, QtCore.Qt.AlignLeft)
    threshold_potential_layout.addWidget(self.__threshold_potential_spin_box, 1, 0)
    threshold_potential_layout.addWidget(self.__set_potential_threshold_btn, 1, 1)
    threshold_potential_frame = QtWidgets.QFrame()
    threshold_potential_frame.setLayout(threshold_potential_layout)
    layout.addWidget(threshold_potential_frame)
    # Threshold potential range
    threshold_potential_layout = QtWidgets.QGridLayout()
    threshold_potential_layout.addWidget(QtWidgets.QLabel("threshold potential range:"), 0, 0, 1, -1, QtCore.Qt.AlignLeft)
    threshold_potential_layout.addWidget(QtWidgets.QLabel("min:"), 1, 0, 1, 1, QtCore.Qt.AlignRight)
    threshold_potential_layout.addWidget(self.__threshold_potential_min_spin_box, 1, 1, 1, -1, QtCore.Qt.AlignLeft)
    threshold_potential_layout.addWidget(QtWidgets.QLabel("max:"), 2, 0, 1, 1, QtCore.Qt.AlignRight)
    threshold_potential_layout.addWidget(self.__threshold_potential_max_spin_box, 2, 1, 1, -1, QtCore.Qt.AlignLeft)
    threshold_potential_frame = QtWidgets.QFrame()
    threshold_potential_frame.setLayout(threshold_potential_layout)
    layout.addWidget(threshold_potential_frame)
    # Select random threshold potential button
    layout.addWidget(self.__select_random_threshold_potential_btn)
    # Group the GUI elements together
    layout.setSpacing(1)
    self.setLayout(layout)
    self.hide()


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__get_neurons(data)
      self.__update()


  def __get_neurons(self, models):
    self.__neurons = list()
    # Get the neurons only
    for model in models:
      if isinstance(model, Neuron):
        self.__neurons.append(model)


  def __update(self):
    num_neurons = len(self.__neurons)

    # Make sure there are neurons to show
    if num_neurons == 0:
      self.hide()
      return
      
    # Set the text of the threshold potential label
    if num_neurons == 1:
      self.__threshold_potential_label.setText("threshold potential:")
    else:
      self.__threshold_potential_label.setText("average threshold potential:")

    # Compute the average threshold potential
    avg_threshold = 0
    for neuron in self.__neurons:
      avg_threshold += neuron.threshold
    avg_threshold /= num_neurons

    # Show it to the user
    self.__threshold_potential_spin_box.setValue(avg_threshold)
    # Update the threshold potential set button
    self.__update_set_potential_threshold_btn()

    # Show this GUI element to the user
    self.show()


  def __update_set_potential_threshold_btn(self):
    threshold_potential_value = self.__threshold_potential_spin_box.value()
    eps = 5/(10**(self.__spin_box_precision + 1))

    for neuron in self.__neurons:
      if abs(neuron.threshold - threshold_potential_value) > eps:
        self.__set_potential_threshold_btn.setEnabled(True)
        break
    else:
      self.__set_potential_threshold_btn.setEnabled(False)


  def __on_set_potential_threshold_btn_clicked(self):
    # Set the threshold of each neuron
    for neuron in self.__neurons:
      neuron.set_threshold(self.__threshold_potential_spin_box.value())
    # Update the GUI
    self.__update()


  def __on_threshold_potential_min_spin_box_changed(self):
    min_value = self.__threshold_potential_min_spin_box.value()
    max_value = self.__threshold_potential_max_spin_box.value()
    if min_value > max_value:
      self.__threshold_potential_max_spin_box.setValue(min_value)


  def __on_threshold_potential_max_spin_box_changed(self):
    min_value = self.__threshold_potential_min_spin_box.value()
    max_value = self.__threshold_potential_max_spin_box.value()
    if max_value < min_value:
      self.__threshold_potential_min_spin_box.setValue(max_value)


  def __on_select_random_threshold_potential_btn_clicked(self):
    min_value = self.__threshold_potential_min_spin_box.value()
    max_value = self.__threshold_potential_max_spin_box.value()
    # Loop over the neurons and assign random potential thresholds
    for neuron in self.__neurons:
      neuron.set_threshold(random.uniform(min_value, max_value))
    # Update the GUI
    self.__update()
