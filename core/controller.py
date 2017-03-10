from core.datacontainer import DataContainer
from bio.neuron import Neuron
from bio.neuralconnection import NeuralConnection
from bio.brain import Brain

class Controller:
  def __init__(self, data_container, brain):
    self.__data_container = data_container
    self.__data_container.add_observer(self)
    self.__brain = brain
    self.__viewer3d = None

    self.__perform_prop3d_picking = True

    # Here we keep the models in a (vtkProp3D, model) dictionary
    self.__prop3d_to_model = dict()
    # Here we keep the selected models in a (vtkProp3D, model) dictionary
    self.__prop3d_to_selected_model = dict()

  
  @property
  def data_container(self):
    return self.__data_container


  @property
  def brain(self):
    return self.__brain


  def set_viewer3d(self, viewer3d):
    self.__viewer3d = viewer3d
    self.__viewer3d.add_observer(self)


  def on_key_released(self, viewer3d, key):
    if key == "Delete":
      models_to_delete = list()
      # Collect all models except neurons and neural connections
      for model in self.__prop3d_to_selected_model.values():
        if not isinstance(model, Neuron) and not isinstance(model, NeuralConnection):
          models_to_delete.append(model)
      # Delete the collected models
      self.__data_container.delete_models(models_to_delete)


  def on_left_button_pressed(self, viewer3d):
    self.__perform_prop3d_picking = True


  def on_left_button_released(self, viewer3d):
    if self.__perform_prop3d_picking:
      self.__process_picked_prop3d(viewer3d, viewer3d.pick())


  def on_mouse_moved(self, viewer3d):
    self.__perform_prop3d_picking = False


  def __process_picked_prop3d(self, viewer3d, prop3d):
    if viewer3d.is_ctrl_key_pressed():
      # Check if she picked the same model twice
      twice_picked_model = self.__prop3d_to_selected_model.get(prop3d)
      if twice_picked_model:
        # Remove the already picked model from the selection
        self.__data_container.remove_from_selection(twice_picked_model)
      else:
        # Add the newly picked model or None to the selection
        self.__data_container.add_to_selection(self.__prop3d_to_model.get(prop3d))
    # The user doesn't hold the ctrl. key
    else:
      self.__data_container.set_selection(self.__prop3d_to_model.get(prop3d))


  def observable_changed(self, change, data):
    # Decide what to do depending on what changed
    if change == DataContainer.change_is_new_data:
      self.__add_data_items(data)
    elif change == DataContainer.change_is_new_selection:
      self.__set_selection(data)
    elif change == DataContainer.change_is_deleted_models:
      self.__delete_models(data)
    elif self.__viewer3d:
      self.__viewer3d.reset_clipping_range()


  def __add_data_items(self, data_items):
    if not data_items:
      return

    # Add the data items to the internal dictionary
    for data_item in data_items:
      # We need a data item with a prop3d
      try:
        prop3d = data_item.visual_representation.prop3d
      except AttributeError:
        pass
      else:
        self.__prop3d_to_model[prop3d] = data_item

    # Add the items to the 3d viewer
    if self.__viewer3d:
      self.__viewer3d.add_models(data_items)


  def __set_selection(self, models):
    # First, un-highlight all models
    for model in self.__prop3d_to_model.values():
      model.visual_representation.highlight_off()

    # Clear the selection
    self.__prop3d_to_selected_model = dict()

    # Now, highligh the ones we want to highlight
    for model in models:
      # Make sure that the current model has a visual representation with a prop3d
      try:
        vis_rep = model.visual_representation
        prop3d = vis_rep.prop3d
      except AttributeError:
        continue

      # Make sure we have that model
      if prop3d not in self.__prop3d_to_model:
        continue

      # Highlight the model
      vis_rep.highlight_on()
      # Save it in the selection dictionary
      self.__prop3d_to_selected_model[prop3d] = model

    # Update the view
    if self.__viewer3d:
      self.__viewer3d.render()


  def __delete_models(self, models):
    for model in models:
      try: # we can handle only data items that are pickable, i.e., that have a visual representation with a prop3d
        prop3d = model.visual_representation.prop3d
      except AttributeError:
        pass
      else: # silently delete the models (no exception even if they are not in the dictionary)
        self.__prop3d_to_model.pop(prop3d, None)
        self.__prop3d_to_selected_model.pop(prop3d, None)
    # Update the 3d view
    if self.__viewer3d:
      self.__viewer3d.delete_models(models)
