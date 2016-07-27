import os
import vtk
import random
from .modelview import Observable
from IO.vtkio import VtkIO
from vis.vtkpoly import VtkPolyModel
from vis.vtkvol import VtkVolumeModel

class DataContainer(Observable):
  # These are the possible changes that can happen to an Observable
  change_is_new_data = 1
  change_is_new_selection = 2
  change_is_data_visibility = 3
  change_is_color = 4
  change_is_transparency = 5
  change_is_slice_index = 6

  def __init__(self):
    Observable.__init__(self)
    # The models indexed by file names
    self.__file_name_to_models = dict()
    # The same models indexed by vtkProperty (necessary for picking in the 3D window)
    self.__vtk_property_to_models = dict()

    # This one saves how many times a name has been used (in order to give unique names)
    self.__name_histogram = dict()

    # Initialize the random number generator
    random.seed()


  def load_files(self, file_names, progress_bar = None):
    """Loads the (supported) data files and notifies the observers about the new data."""
    unique_file_names = list()
    for file_name in file_names:
      if not self.has_data(file_name): # we do not want to load the same file twice
        unique_file_names.append(file_name)

    vtk_io = VtkIO()
    self.__add_data_items(vtk_io.load_files(unique_file_names, progress_bar))


  def get_models(self):
    """Returns a list of all models (volume and poly)."""
    return list(self.__file_name_to_models.values())


  def update_visibility(self):
    """Call this one if the visibility of (some of) the objects in this container has changed.
    This method notifies all observers about that."""
    self.notify_observers_abount_change(DataContainer.change_is_data_visibility, None)


  def update_color(self):
    self.notify_observers_abount_change(DataContainer.change_is_color, None)


  def update_transparency(self):
    self.notify_observers_abount_change(DataContainer.change_is_transparency, None)


  def update_slice_index(self):
    self.notify_observers_abount_change(DataContainer.change_is_slice_index, None)


  def set_model_selection_by_vtk_properties(self, props):
    existing_selected_models = list()
    for prop in props:
      model = self.get_model_by_vtk_property(prop)
      if model:
        existing_selected_models.append(model)
    # Norify the observers about the new selection
    self.notify_observers_abount_change(DataContainer.change_is_new_selection, existing_selected_models)


  def set_model_selection(self, models):
    existing_selected_models = list()
    for model in models:
      model = self.get_model_by_file_name(model.file_name)
      if model:
        existing_selected_models.append(model)
    # Norify the observers about the new selection
    self.notify_observers_abount_change(DataContainer.change_is_new_selection, existing_selected_models)


  def get_model_by_file_name(self, file_name):
    """Returns the model which has the provided name or None if no such model exists."""
    return self.__file_name_to_models.get(file_name)


  def get_model_by_vtk_property(self, vtk_property):
    if not isinstance(vtk_property, vtk.vtkProperty):
      raise TypeError("the input has to be a vtkProperty")
    """Returns the model which has the provided vtkProperty or None."""
    return self.__vtk_property_to_models.get(vtk_property)


  def has_data(self, file_name):
    """Returns True if the data from 'file_name' is already in this container and False otherwise."""
    return self.__file_name_to_models.get(file_name) != None


  def __create_unique_name(self, file_name):
    # Take the file name without the path as a base for the new name
    name = os.path.split(file_name)[1]
    # How many times has this name been used
    used_n_times = self.__name_histogram.get(name)
    
    if used_n_times: # We will use 'name' once more => increment the counter
      self.__name_histogram[name] = used_n_times + 1
      return name + " (" + str(used_n_times) + ")"
    else: # 'name' has never been used before
      self.__name_histogram[name] = 1
      return name


  def __add_data_items(self, file_name_data_pairs):
    # These will be the new data items (we do not want the same data twice)
    new_models = list()

    # Add the data to the containers
    for file_name_data_pair in file_name_data_pairs:
      # For better readability
      file_name = file_name_data_pair[0]
      data = file_name_data_pair[1]

      # We want new data only
      if self.has_data(file_name):
        continue

      # Save the model to the internal containers
      new_model = self.__create_and_save_model(file_name, data)
      if new_model:
        new_models.append(new_model)

    # Notify the observers about the new data
    self.notify_observers_abount_change(DataContainer.change_is_new_data, new_models)


  def __create_and_save_model(self, file_name, data):
    """Create and save a model of the right type. Returns the new model if the data type is known and None otherwise."""
    model = None
    # Decide what to do with the data according to its type
    if isinstance(data, vtk.vtkImageData):
      model = VtkVolumeModel(file_name, self.__create_unique_name(file_name), data)
    elif isinstance(data, vtk.vtkPolyData):
      model = VtkPolyModel(file_name, self.__create_unique_name(file_name), data)
      rgb = self.__compute_random_rgb_color()
      model.set_color(rgb[0], rgb[1], rgb[2])
    else:
      # Unknown data type
      return None

    # Save the model
    self.__file_name_to_models[file_name] = model
    self.__vtk_property_to_models[model.vtk_property] = model

    # Unknown data type
    return model

  def __compute_random_rgb_color(self):
    return vtk.vtkMath.HSVToRGB((random.uniform(0.0, 0.6), 0.8, 1.0))
