from .modelview import Observable

class DataContainer(Observable):
  # These are the possible changes that can happen to an Observable
  change_is_new_data = 1
  change_is_modified_neural_connections = 10
  change_is_modified_neurons = 11
  change_is_new_selection = 20
  change_is_data_visibility = 21
  change_is_color = 22
  change_is_transparency = 23
  change_is_slice_index = 24
  change_is_deleted_models = 25
  change_is_see_inside = 26
  change_is_update = 26


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


  def add_data(self, data_items):
    for data_item in data_items:
      if data_item: self.__models.add(data_item)
    # Notify the observers about the new models
    self.notify_observers_about_change(DataContainer.change_is_new_data, data_items)


  def get_models(self):
    """Returns a list of all models."""
    return list(self.__models)


  def get_selected_models(self):
    """Returns a list of the selected models."""
    return list(self.__selected_models)

  
  def neural_connections_changed(self, neural_connections):
    self.notify_observers_about_change(DataContainer.change_is_modified_neural_connections, neural_connections)


  def neurons_changed(self, neurons):
    self.notify_observers_about_change(DataContainer.change_is_modified_neurons, neurons)


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


  def update(self):
    self.notify_observers_about_change(DataContainer.change_is_update, list())


  def add_to_selection(self, item):
    if item in self.__models:
      self.__selected_models.add(item)
      self.notify_observers_about_change(DataContainer.change_is_new_selection, self.__selected_models)


  def remove_from_selection(self, item):
    try:
      self.__selected_models.remove(item)
    except ValueError:
      pass
    else:
      self.notify_observers_about_change(DataContainer.change_is_new_selection, self.__selected_models)


  def set_selection(self, items):
    self.__selected_models = set()
    try:
      for item in items:
        if item in self.__models:
          self.__selected_models.add(item)
    except TypeError: # it seems that 'items' is not iterable, i.e., it is a single item
      if items in self.__models:
        self.__selected_models.add(items)

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
        

  def delete_models(self, models):
    # Delete all selected models from the set of models
    for model in models:
      # Delete the model from the set of ALL models
      try:
        self.__models.remove(model)
      except KeyError:
        pass
      # Delete the model from the selection
      try:
        self.__selected_models.remove(model)
      except KeyError:
        pass
    # Notify the observers about the changes
    self.notify_observers_about_change(DataContainer.change_is_deleted_models, models)
    self.notify_observers_about_change(DataContainer.change_is_new_selection, self.__selected_models)
