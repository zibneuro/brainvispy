from core.datacontainer import DataContainer
from core.controller import Controller
from anatomy.region import BrainRegion
from PyQt5 import QtGui, QtWidgets, QtCore

class BrainRegionGUI(QtWidgets.QGroupBox):
  """This is the dock widget for the properties of a selected data item(s)"""
  def __init__(self, data_container, controller):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has the wrong type")

    super().__init__("BRAIN REGION")

    # Register yourself as an observer
    self.__data_container = data_container
    self.__data_container.add_observer(self)
    # Save the controller - we need this guy
    self.__controller = controller

    # This list keeps the models (objects) we have
    self.__brain_regions = list()

    # The neutral color for the color button (when the selected objects have different colors)
    self.__neutral_btn_color = "#a0a0a0"
    # This one is used in a callback
    self.__ignore_transparency_slider_value_changed_callback = False

    # APPEARANCE GUI elements
    # The see inside checkbox
    self.__see_inside_checkbox = QtWidgets.QCheckBox("see inside region")
    self.__see_inside_checkbox.setTristate(False)
    self.__see_inside_checkbox.clicked.connect(self.__on_see_inside_checkbox_clicked)
    # The color button
    self.__select_color_btn = QtWidgets.QPushButton()
    self.__select_color_btn.clicked.connect(self.__on_color_button_clicked)
    self.__select_color_btn.setStyleSheet("background-color: " + self.__neutral_btn_color)
    self.__select_color_btn.setFixedSize(40, 40)
    # The transparency slider
    self.__transparency_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    self.__transparency_slider.setMinimum(0)
    self.__transparency_slider.setMaximum(100)
    self.__transparency_slider.setSingleStep(1)
    self.__transparency_slider.valueChanged.connect(self.__on_transparency_slider_value_changed)
    
    # NEURON GENERATION GUI elements
    # The [min, max] range for the threshold potential
    # min
    self.__threshold_potential_min_spin_box = QtWidgets.QDoubleSpinBox()
    self.__threshold_potential_min_spin_box.setMinimum(-10000)
    self.__threshold_potential_min_spin_box.setMaximum(10000)
    self.__threshold_potential_min_spin_box.setValue(-1)
    self.__threshold_potential_min_spin_box.setSingleStep(0.01)
    self.__threshold_potential_min_spin_box.setDecimals(2)
    self.__threshold_potential_min_spin_box.valueChanged.connect(self.__on_threshold_potential_min_spin_box_changed)
    # max
    self.__threshold_potential_max_spin_box = QtWidgets.QDoubleSpinBox()
    self.__threshold_potential_max_spin_box.setMinimum(-10000)
    self.__threshold_potential_max_spin_box.setMaximum(10000)
    self.__threshold_potential_max_spin_box.setValue(1)
    self.__threshold_potential_max_spin_box.setDecimals(2)
    self.__threshold_potential_max_spin_box.setSingleStep(0.01)
    self.__threshold_potential_max_spin_box.valueChanged.connect(self.__on_threshold_potential_max_spin_box_changed)
    # The box where the user enters the number of neurons to create
    self.__num_neurons_spin_box = QtWidgets.QSpinBox()
    self.__num_neurons_spin_box.setMinimum(1)
    self.__num_neurons_spin_box.setMaximum(100)
    self.__num_neurons_spin_box.setValue(10)
    self.__num_neurons_spin_box.setSingleStep(1)
    # The create neurons button
    self.__create_neurons_btn = QtWidgets.QPushButton("create neuron(s)")
    self.__create_neurons_btn.clicked.connect(self.__on_create_neurons_button_clicked)
    
    # Add the GUI elements to a layout
    layout = QtWidgets.QVBoxLayout()
    # SURFACE APPEARANCE
    layout.addWidget(QtWidgets.QLabel("<b>surface appearance</b>"), 0, QtCore.Qt.AlignLeft)
    appearance_layout = QtWidgets.QGridLayout()
    appearance_layout.addWidget(QtWidgets.QLabel("color"), 0, 0, QtCore.Qt.AlignLeft)
    appearance_layout.addWidget(QtWidgets.QLabel("transparency"), 0, 1, QtCore.Qt.AlignHCenter)
    appearance_layout.addWidget(self.__select_color_btn, 1, 0)
    appearance_layout.addWidget(self.__transparency_slider, 1, 1)
    appearance_layout.addWidget(self.__see_inside_checkbox, 2, 0, 1, -1)
    appearance_frame = QtWidgets.QFrame()
    appearance_frame.setLayout(appearance_layout)
    layout.addWidget(appearance_frame)
    # NEURONS
    layout.addWidget(QtWidgets.QLabel("<b>neuron creation</b>"), 0, QtCore.Qt.AlignLeft)
    # Threshold potential
    threshold_potential_layout = QtWidgets.QGridLayout()
    threshold_potential_layout.addWidget(QtWidgets.QLabel("threshold potential range:"), 0, 0, 1, -1, QtCore.Qt.AlignLeft)
    threshold_potential_layout.addWidget(QtWidgets.QLabel("min:"), 1, 0, 1, 1, QtCore.Qt.AlignRight)
    threshold_potential_layout.addWidget(self.__threshold_potential_min_spin_box, 1, 1, 1, -1, QtCore.Qt.AlignLeft)
    threshold_potential_layout.addWidget(QtWidgets.QLabel("max:"), 2, 0, 1, 1, QtCore.Qt.AlignRight)
    threshold_potential_layout.addWidget(self.__threshold_potential_max_spin_box, 2, 1, 1, -1, QtCore.Qt.AlignLeft)
    threshold_potential_frame = QtWidgets.QFrame()
    threshold_potential_frame.setLayout(threshold_potential_layout)
    layout.addWidget(threshold_potential_frame)
    # Number of neurons
    create_neurons_layout = QtWidgets.QHBoxLayout()
    create_neurons_layout.addWidget(QtWidgets.QLabel("num. neurons:"), 0, QtCore.Qt.AlignLeft)
    create_neurons_layout.addWidget(self.__num_neurons_spin_box)
    create_neurons_frame = QtWidgets.QFrame()
    create_neurons_frame.setLayout(create_neurons_layout)
    layout.addWidget(create_neurons_frame)
    layout.setSpacing(1)
    # Create neurons button
    layout.addWidget(self.__create_neurons_btn)

    # Group the GUI elements together
    self.setLayout(layout)
    self.hide()


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__update(data)
    elif change == DataContainer.change_is_color:
      self.__update_color_selection_button()
    elif change == DataContainer.change_is_transparency:
      self.__update_transparency_slider()


  def __update(self, models):
    self.__brain_regions = list()

    # Get the poly models only
    for model in models:
      if isinstance(model, BrainRegion):
        self.__brain_regions.append(model)

    if self.__brain_regions:
      self.__update_see_inside_checkbox()
      self.__update_color_selection_button()
      self.__update_transparency_slider()
      self.show()
    else:
      self.hide()


  def __update_see_inside_checkbox(self):
    see_inside_counter = 0
    
    for model in self.__brain_regions:
      see_inside_counter += model.see_inside

    if see_inside_counter == 0:
      self.__see_inside_checkbox.setCheckState(QtCore.Qt.Unchecked)
    elif see_inside_counter == len(self.__brain_regions):
      self.__see_inside_checkbox.setCheckState(QtCore.Qt.Checked)
    else:
      self.__see_inside_checkbox.setCheckState(QtCore.Qt.PartiallyChecked)


  def __update_color_selection_button(self):
    """Update the button which shows the color of the selected model(s)."""
    color_strings = set()
    # Get all colors
    for model in self.__brain_regions:
      color_strings.add(self.__rgb_tuple_to_hex_string(model.get_color()))
    # Update the button depending on whether we have a single or multiple colors
    if len(color_strings) == 1:
      self.__select_color_btn.setStyleSheet("background-color: " + next(iter(color_strings)))
    else:
      self.__select_color_btn.setStyleSheet("background-color: " + self.__neutral_btn_color)


  def __update_transparency_slider(self):
    if not self.__brain_regions:
      return

    transparency_sum = 0.0
    # Compute the average transparency of all models and set the slider to this value
    for model in self.__brain_regions:
      transparency_sum += model.get_transparency()
   
    # The line after the next ones would call the transparency slider callback. We do not want that => that's why the folloling lines
    ignore_transparency_slider_value_changed_callback = self.__ignore_transparency_slider_value_changed_callback
    self.__ignore_transparency_slider_value_changed_callback = True
    
    # Update the button depending on whether we have a single or multiple colors
    self.__transparency_slider.setValue(100*transparency_sum / len(self.__brain_regions))

    # Restore the state
    self.__ignore_transparency_slider_value_changed_callback = ignore_transparency_slider_value_changed_callback


  def __rgb_tuple_to_hex_string(self, rgb):
    """Assumes that the first three values in the 'rgb' tuple (or list) are in the range [0, 1]. Returns a hex color in the form #xyzuvw."""
    hex_color = "#"
    for k in range(3):
      hex_color += hex(int(255.0*rgb[k]))[2:].zfill(2) # scale to range [0, 255], convert to hex, remove the "0x" and fill with zeroes
    return hex_color


  def __on_see_inside_checkbox_clicked(self):
    # Shall we see inside each model?
    see_inside = 1 if self.__see_inside_checkbox.checkState() == QtCore.Qt.Checked else 0
    self.__see_inside_checkbox.setTristate(False)
    # Update the "see inside" property of each model
    for model in self.__brain_regions:
      model.set_see_inside(see_inside)
    # Update the container
    self.__data_container.update_see_inside()


  def __on_color_button_clicked(self):
    if not self.__brain_regions:
      return

    # Get the current color of the button
    current_color = self.__select_color_btn.palette().color(QtGui.QPalette.Window)
    # Open a color chooser with the current color as default
    selected_color = QtWidgets.QColorDialog.getColor(current_color)
    # Make sure that the user clicked on OK (i.e., that she selected a color)
    if not selected_color.isValid():
      return

    # Scale the color to the range [0, 1] (that's what VTK needs)
    r = selected_color.red() / 255.0
    g = selected_color.green() / 255.0
    b = selected_color.blue() / 255.0

    # Loop over the models and assign them the selected color
    for model in self.__brain_regions:
      model.set_color(r, g, b)

    # Notify the data container that some of its data changed (this will call this objects)
    self.__data_container.update_color()


  def __on_transparency_slider_value_changed(self):
    if self.__ignore_transparency_slider_value_changed_callback or not self.__brain_regions:
      return

    transparency = self.__transparency_slider.value() / 100.0

    # Loop over the models and assign them the selected color
    for model in self.__brain_regions:
      model.set_transparency(transparency)

    # Notify the data container that some of its data changed (this will call this objects)
    self.__data_container.update_transparency()


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


  def __on_create_neurons_button_clicked(self):
    threshold_range = (self.__threshold_potential_min_spin_box.value(), self.__threshold_potential_max_spin_box.value())
    self.__controller.generate_neurons(self.__num_neurons_spin_box.value(), self.__brain_regions, threshold_range)
