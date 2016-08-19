from core.datacontainer import DataContainer
from vis.vtkvol import VtkVolumeModel
from PyQt5 import QtGui, QtWidgets, QtCore

class VtkVolumeModelGUI(QtWidgets.QGroupBox):
  """This is the dock widget for the properties of a selected data item(s)"""
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has the wrong type")

    super().__init__("volume properties")

    # Register yourself as an observer
    self.__data_container = data_container
    self.__data_container.add_observer(self)

    # This list keeps the models (objects) we have
    self.__vol_models = list()

    # This one is used in a callback
    self.__ignore_slice_slider_value_changed_callback = False

    # The slice slider
    self.__slice_label = QtWidgets.QLabel("slice")
    self.__slice_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    self.__slice_slider.setSingleStep(1)
    self.__slice_slider.valueChanged.connect(self.__on_slice_slider_value_changed)
    # The label which says to the user that she must select only one volume model
    self.__single_model_label = QtWidgets.QLabel("Select only one volume model\n(you can edit only one at a time)\n")
    # Add the GUI elements to a layout
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.__slice_label)
    layout.addWidget(self.__slice_slider)
    layout.addWidget(self.__single_model_label)
    #layout.setHorizontalSpacing(10)
    # Group the GUI elements together
    self.setLayout(layout)
    self.hide()


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_selection:
      self.__update(data)
    elif change == DataContainer.change_is_slice_index and len(self.__vol_models) == 1:
      self.__update_slice_slider(self.__vol_models[0])


  def __update(self, models):
    self.__vol_models = list()

    # Get the volume models only
    for model in models:
      if isinstance(model, VtkVolumeModel):
        self.__vol_models.append(model)

    num_vol_models = len(self.__vol_models)
    
    if num_vol_models == 0:
      self.hide() # hide the whole stuff and exit
      return
    elif num_vol_models == 1:
      self.__update_slice_slider(self.__vol_models[0])
      self.__slice_label.show()
      self.__slice_slider.show()
      self.__single_model_label.hide()
    else:
      self.__slice_label.hide()
      self.__slice_slider.hide()
      self.__single_model_label.show()

    # Show the whole GUI
    self.show()


  def __update_slice_slider(self, vol_model):
    # The line after the next ones would call the slice slider callback. We do not want that => that's why the folloling lines
    ignore_slice_slider_value_changed_callback = self.__ignore_slice_slider_value_changed_callback
    self.__ignore_slice_slider_value_changed_callback = True
    
    self.__slice_slider.setMinimum(0)
    self.__slice_slider.setMaximum(vol_model.get_number_of_slices() - 1)
    self.__slice_slider.setValue(vol_model.get_slice_index())

    # Restore the state
    self.__ignore_slice_slider_value_changed_callback = ignore_slice_slider_value_changed_callback


  def __on_slice_slider_value_changed(self):
    if self.__ignore_slice_slider_value_changed_callback or len(self.__vol_models) != 1:
      return

    # Update the slice index of the selected model
    self.__vol_models[0].set_slice_index(self.__slice_slider.value())
    # Notify the data container that some of its data changed (this will call this objects)
    self.__data_container.update_slice_index()
