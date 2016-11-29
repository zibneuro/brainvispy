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
    # All models
    self.__models = set()
    # This guy keeps the selected models
    self.__selected_models = set()


  def is_empty(self):
    return len(self.__models) == 0


  def clear(self):
    """Removes everything from the container leaving it empty. The observers get notified."""
    # Notify the observers about the changes
    self.notify_observers_about_change(DataContainer.change_is_new_selection, list())
    self.notify_observers_about_change(DataContainer.change_is_deleted_models, list(self.__models))
    # Now, clear everything
    self.__models = set()
    self.__selected_models = set()


  def add_neurons(self, neurons):
    self.__add_models(neurons, DataContainer.change_is_new_neurons)


  def add_brain_regions(self, brain_regions):
    self.__add_models(brain_regions, DataContainer.change_is_new_brain_regions)


  def get_models(self):
    """Returns a list of all models."""
    return list(self.__models)


  def get_selected_models(self):
    """Returns a list of the selected models."""
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


  def set_model_selection(self, models):
    self.__selected_models = set()
    try:
      for model in models:
        if model in self.__models:
          self.__selected_models.add(model)
    except TypeError: # seems that 'models' is a single model, (i.e., not iterable)
      if models in self.__models:
        self.__selected_models.add(models)

    # Notify the observers about the new selection
    self.notify_observers_about_change(DataContainer.change_is_new_selection, self.__selected_models)


  def invert_model_selection(self):
    # Remove the selected and add the non-selected models to the selection
    for model in self.__models:
      try:
        self.__selected_models.remove(model)
      except KeyError:
        self.__selected_models.add(model)

    # Notify the observers about the new selection
    self.notify_observers_about_change(DataContainer.change_is_new_selection, self.__selected_models)
        

  def delete_selected_models(self):
    # Delete all selected models from the set of models
    for model in self.__selected_models:
      try:
        self.__models.remove(model)
      except KeyError:
        pass
    # Notify the observers about the changes
    self.notify_observers_about_change(DataContainer.change_is_deleted_models, self.__selected_models)
    self.notify_observers_about_change(DataContainer.change_is_new_selection, list())


  def __add_models(self, models, what_changed):
    for model in models:
      self.__models.add(model)
    # Notify the observers about the new models
    self.notify_observers_about_change(what_changed, models);
