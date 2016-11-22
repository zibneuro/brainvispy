from .modelview import Observable

class DataContainer(Observable):
  # These are the possible changes that can happen to an Observable
  change_is_new_brain_regions = 1
  change_is_new_neurons = 2
  change_is_new_selection = 10
  change_is_data_visibility = 11
  change_is_color = 12
  change_is_transparency = 13
  change_is_slice_index = 14
  change_is_deleted_models = 15
  change_is_see_inside = 16


  def __init__(self):
    Observable.__init__(self)
    # The models indexed by vtkProperty (we need a unique vtkProperty for each model for the picking in the 3D window)
    self.__vtk_property_to_models = dict()
    # This guy keeps the selected models
    self.__selected_models = set()


  def is_empty(self):
    return len(self.__vtk_property_to_models) == 0


  def clear(self):
    """Removes everything from the container leaving it empty. The observers get notified."""
    # Notify the observers about the changes
    self.notify_observers_about_change(DataContainer.change_is_new_selection, list())
    self.notify_observers_about_change(DataContainer.change_is_deleted_models, list(self.__vtk_property_to_models.values()))
    # Now, clear everything
    self.__vtk_property_to_models = dict()
    self.__selected_models = set()


  def add_neurons(self, neurons):
    self.__add_models(neurons, DataContainer.change_is_new_neurons)


  def add_brain_regions(self, brain_regions):
    self.__add_models(brain_regions, DataContainer.change_is_new_brain_regions)


  def get_models(self):
    """Returns a list of all models."""
    return list(self.__vtk_property_to_models.values())


  def get_selected_models(self):
    return list(self.__selected_models)


  def update_visibility(self):
    """Call this one if the visibility of (some of) the objects in this container has changed.
    This method notifies all observers about that."""
    self.notify_observers_about_change(DataContainer.change_is_data_visibility, list())


  def update_color(self):
    self.notify_observers_about_change(DataContainer.change_is_color, list())


  def update_transparency(self):
    self.notify_observers_about_change(DataContainer.change_is_transparency, list())


  def update_slice_index(self):
    self.notify_observers_about_change(DataContainer.change_is_slice_index, list())


  def update_see_inside(self):
    self.notify_observers_about_change(DataContainer.change_is_see_inside, list())


  def set_model_selection_by_vtk_properties(self, props):
    self.__selected_models = set()
    for prop in props:
      model = self.__get_model_by_vtk_property(prop)
      if model:
        self.__selected_models.add(model)
    # Notify the observers about the new selection
    self.notify_observers_about_change(DataContainer.change_is_new_selection, self.__selected_models)


  def set_model_selection(self, models):
    self.__selected_models = set()
    for model in models:
      model = self.__get_model_by_vtk_property(model.vtk_property)
      if model:
        self.__selected_models.add(model)
    # Notify the observers about the new selection
    self.notify_observers_about_change(DataContainer.change_is_new_selection, self.__selected_models)


  def invert_model_selection(self):
    # Remove the selected and add the non-selected models to the selection
    for model in self.__vtk_property_to_models.values():
      try:
        self.__selected_models.remove(model)
      except KeyError:
        self.__selected_models.add(model)

    # Notify the observers about the new selection
    self.notify_observers_about_change(DataContainer.change_is_new_selection, self.__selected_models)
        

  def delete_selected_models(self):
    if not self.__selected_models:
      return
    # Make a copy of the list of selected models since we are going to modify it in the next loop
    selected_models = list(self.__selected_models)
    for model in selected_models:
      self.__delete_model(model)
    # Notify the observers about the changes
    self.notify_observers_about_change(DataContainer.change_is_deleted_models, selected_models)
    self.notify_observers_about_change(DataContainer.change_is_new_selection, list())


  def __add_models(self, models, what_changed):
    new_models = list()
    for model in models:
      # Every model has to have a unique vtkProperty
      if not self.__get_model_by_vtk_property(model.vtk_property):
        self.__vtk_property_to_models[model.vtk_property] = model
        new_models.append(model)
    # Notify the observers about the new models
    self.notify_observers_about_change(what_changed, new_models);


  def __get_model_by_vtk_property(self, vtk_property):
    """Returns the model which has the provided vtkProperty or None."""
    return self.__vtk_property_to_models.get(vtk_property)


  def __delete_model(self, model):
    try:
      del self.__vtk_property_to_models[model.vtk_property]
      self.__selected_models.remove(model)
    except KeyError:
      pass
