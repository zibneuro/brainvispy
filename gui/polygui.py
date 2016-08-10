from core.datacontainer import DataContainer
from vis.vtkpoly import VtkPolyModel
from PyQt5 import QtGui, QtWidgets, QtCore

class VtkPolyModelGUI:
  """This is the dock widget for the properties of a selected data item(s)"""
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has the wrong type")

    # Register yourself as an observer
    self.__data_container = data_container
    self.__data_container.add_observer(self)

    # This list keeps the models (objects) we have
    self.__poly_models = list()

    # The neutral color for the color button (when the selected objects have different colors)
    self.__neutral_btn_color = "#a0a0a0"
    
    # This one is used in a callback
    self.__ignore_transparency_slider_value_changed_callback = False

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
    # Add the GUI elements to a layout
    layout = QtWidgets.QGridLayout()
    layout.addWidget(QtWidgets.QLabel("color"), 0, 0)
    layout.addWidget(self.__select_color_btn, 1, 0)
    layout.addWidget(QtWidgets.QLabel("transparency"), 0, 1)
    layout.addWidget(self.__transparency_slider, 1, 1)
    layout.setHorizontalSpacing(10)
    # Group the GUI elements together
    self.gui_widget = QtWidgets.QGroupBox("surface properties")
    self.gui_widget.setLayout(layout)
    self.__hide()


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__update(data)
    elif change == DataContainer.change_is_color:
      self.__update_color_selection_button()
    elif change == DataContainer.change_is_transparency:
      self.__update_transparency_slider()


  def __update(self, models):
    self.__poly_models = list()

    # Get the poly models only
    for model in models:
      if isinstance(model, VtkPolyModel):
        self.__poly_models.append(model)

    if self.__poly_models:
      self.__update_color_selection_button()
      self.__update_transparency_slider()
      self.__show()
    else:
      self.__hide()


  def __update_color_selection_button(self):
    """Update the button which shows the color of the selected model(s)."""
    color_strings = set()
    # Get all colors
    for model in self.__poly_models:
      color_strings.add(self.__rgb_tuple_to_hex_string(model.get_color()))
    # Update the button depending on whether we have a single or multiple colors
    if len(color_strings) == 1:
      self.__select_color_btn.setStyleSheet("background-color: " + next(iter(color_strings)))
    else:
      self.__select_color_btn.setStyleSheet("background-color: " + self.__neutral_btn_color)


  def __update_transparency_slider(self):
    if not self.__poly_models:
      return

    transparency_sum = 0.0
    # Compute the average transparency of all models and set the slider to this value
    for model in self.__poly_models:
      transparency_sum += model.get_transparency()
   
    # The line after the next ones would call the transparency slider callback. We do not want that => that's why the folloling lines
    ignore_transparency_slider_value_changed_callback = self.__ignore_transparency_slider_value_changed_callback
    self.__ignore_transparency_slider_value_changed_callback = True
    
    # Update the button depending on whether we have a single or multiple colors
    self.__transparency_slider.setValue(100*transparency_sum / len(self.__poly_models))

    # Restore the state
    self.__ignore_transparency_slider_value_changed_callback = ignore_transparency_slider_value_changed_callback


  def __rgb_tuple_to_hex_string(self, rgb):
    """Assumes that the first three values in the 'rgb' tuple (or list) are in the range [0, 1]. Returns a hex color in the form #xyzuvw."""
    hex_color = "#"
    for k in range(3):
      hex_color += hex(int(255.0*rgb[k]))[2:].zfill(2) # scale to range [0, 255], convert to hex, remove the "0x" and fill with zeroes
    return hex_color


  def __on_color_button_clicked(self):
    if not self.__poly_models:
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
    for model in self.__poly_models:
      model.set_color(r, g, b)

    # Notify the data container that some of its data changed (this will call this objects)
    self.__data_container.update_color()


  def __on_transparency_slider_value_changed(self):
    if self.__ignore_transparency_slider_value_changed_callback or not self.__poly_models:
      return

    transparency = self.__transparency_slider.value() / 100.0

    # Loop over the models and assign them the selected color
    for model in self.__poly_models:
      model.set_transparency(transparency)

    # Notify the data container that some of its data changed (this will call this objects)
    self.__data_container.update_transparency()


  def __hide(self):
    self.gui_widget.hide()


  def __show(self):
    self.gui_widget.show()
