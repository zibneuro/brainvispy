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

  def __init__(self):
    Observable.__init__(self)
    # The data sorted according to file names
    self.file_name_to_volume_models = dict()
    self.file_name_to_poly_models = dict()
    # The same data sorted according to 3D props
    self.prop_3d_to_volume_models = dict()
    self.prop_3d_to_poly_models = dict()

    # This one saves how many times a name has been used (in order to give unique names)
    self.__name_histogram = dict()

    # Initialize the random number generator
    random.seed()

  def compute_random_rgb_color(self):
    hsv = list()
    hsv.append(random.uniform(0.0, 0.6))
    hsv.append(0.8)
    hsv.append(1.0)
    return vtk.vtkMath.HSVToRGB(hsv)


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
    return list(self.file_name_to_volume_models.values()) + list(self.file_name_to_poly_models.values())


  def update_visibility(self):
    """Call this one if the visibility of (some of) the objects in this container has changed.
    This method notifies all observers about that."""
    self.notify_observers_abount_change(DataContainer.change_is_data_visibility, None)


  def update_color(self):
    self.notify_observers_abount_change(DataContainer.change_is_color, None)


  def update_transparency(self):
    self.notify_observers_abount_change(DataContainer.change_is_transparency, None)


  def set_model_selection_by_props(self, props):
    existing_selected_models = list()
    for prop in props:
      model = self.get_model_by_prop(prop)
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


  def get_model_by_file_name(self, model_name):
    """Returns the model which has the provided name or None if no such model exists."""
    model = self.file_name_to_volume_models.get(model_name)
    if model:
      return model
    return self.file_name_to_poly_models.get(model_name)


  def get_model_by_prop(self, prop):
    """Returns the model which has the provided name or None if no such model exists."""
    model = self.prop_3d_to_volume_models.get(prop)
    if model:
      return model
    return self.prop_3d_to_poly_models.get(prop)


  def has_data(self, file_name):
    """Returns True if the data from 'file_name' is already in this container and False otherwise."""
    return self.file_name_to_volume_models.get(file_name) != None or self.file_name_to_poly_models.get(file_name) != None


  def create_unique_name(self, file_name):
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
    """Creates and save a model of the right type. Returns the new model if the data type is known and None otherwise."""
    # Decide what to do with the data according to its type
    if isinstance(data, vtk.vtkImageData):
      # Create a new volume model and save it
      volume_model = VtkVolumeModel(file_name, self.create_unique_name(file_name), data)
      self.file_name_to_volume_models[file_name] = volume_model
      self.prop_3d_to_volume_models[volume_model.prop_3d] = volume_model
      return volume_model
    elif isinstance(data, vtk.vtkPolyData):
      # Create a new poly-data model and save it
      poly_model = VtkPolyModel(file_name, self.create_unique_name(file_name), data)
      rgb = self.compute_random_rgb_color()
      poly_model.set_diffuse_color(rgb[0], rgb[1], rgb[2])
      self.file_name_to_poly_models[file_name] = poly_model
      self.prop_3d_to_poly_models[poly_model.prop_3d] = poly_model
      return poly_model

    # Unknown data type
    return None
