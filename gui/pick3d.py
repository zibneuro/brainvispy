import vtk
from core.datacontainer import DataContainer

class ModelPicker:
  def __init__(self, data_container, interactor):
    # Init all members
    self.__data_container = data_container
    self.__data_container.add_observer(self)
    self.__interactor_style = vtk.vtkInteractorStyleTrackballCamera()
    self.__picker = vtk.vtkPropPicker()
    self.__interactor = interactor   
    self.__interactor.SetInteractorStyle(self.__interactor_style)
    self.__interactor.SetPicker(self.__picker)
    self.__perform_picking = True

    # Here we keep the selected models in a (vtkProp3D, model) dictionary
    self.__selected_prop3d_to_model = dict()
    # Here we keep ALL models in a (vtkProp3D, model) dictionary
    self.__prop3d_to_model = dict()

    self.__interactor_style.AddObserver("LeftButtonPressEvent", self.__on_left_button_pressed)
    self.__interactor_style.AddObserver("LeftButtonReleaseEvent", self.__on_left_button_released)
    self.__interactor_style.AddObserver("MouseMoveEvent", self.__on_mouse_move)


  def delete_selected_models(self):
    self.__data_container.delete_models(list(self.__selected_prop3d_to_model.values()))


  def observable_changed(self, change, data):
    if change == DataContainer.change_is_new_brain_regions or change == DataContainer.change_is_new_neurons:
      self.__add_models(data)
    elif change == DataContainer.change_is_deleted_models:
      self.__delete_models(data)
    elif change == DataContainer.change_is_new_selection:
      self.__set_selection(data)


  def __on_left_button_pressed(self, obj, event):
    self.__perform_picking = True
    self.__interactor_style.OnLeftButtonDown()


  def __on_left_button_released(self, obj, event):
    if self.__perform_picking:
      renderer = self.__interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()
      xy_pick_pos = self.__interactor.GetEventPosition()
      self.__pick(xy_pick_pos, renderer)
    self.__interactor_style.OnLeftButtonUp()


  def __on_mouse_move(self, obj, event):
    self.__perform_picking = False
    self.__interactor_style.OnMouseMove()


  def __pick(self, xy_pos, renderer):
    # Perform the picking
    self.__picker.Pick(xy_pos[0], xy_pos[1], 0, renderer)
    # Get what you picked
    picked_prop3d = self.__picker.GetProp3D()

    # Does the user hold the ctrl. key?
    if self.__interactor.GetControlKey():
      # Check if she picked the same model twice
      twice_picked_model = self.__selected_prop3d_to_model.get(picked_prop3d)
      if twice_picked_model:
        # Remove the already picked model from the selection
        self.__data_container.remove_from_selection(twice_picked_model)
      else:
        # Add the newly picked model or None to the selection
        self.__data_container.add_to_selection(self.__prop3d_to_model.get(picked_prop3d))
    # The user doesn't hold the ctrl. key
    else:
      self.__data_container.set_model_selection(self.__prop3d_to_model.get(picked_prop3d))


  def __add_models(self, data):
    for model in data:
      try: # we can handle only data items that are pickable, i.e., that have a prop3d attribute
        prop3d = model.visual_representation.prop3d
        self.__prop3d_to_model[prop3d] = model
      except AttributeError:
        pass


  def __delete_models(self, data):
    for model in data:
      try: # we can handle only data items that are pickable, i.e., that have a prop3d attribute
        prop3d = model.visual_representation.prop3d
        self.__prop3d_to_model.pop(prop3d, None)
        self.__selected_prop3d_to_model.pop(prop3d, None)
      except AttributeError:
        pass


  def __set_selection(self, data):
    self.__selected_prop3d_to_model = dict()
    for model in data:
      try: # we can handle only data items that are pickable, i.e., that have a prop3d attribute
        prop3d = model.visual_representation.prop3d
        self.__selected_prop3d_to_model[prop3d] = model
      except AttributeError:
        pass
