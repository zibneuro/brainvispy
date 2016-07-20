import vtk
from core.modelview import Observer
from core.datacontainer import DataContainer

class ModelPicker(Observer):
  def __init__(self, data_container, interactor):
    self.__data_container = data_container
    # Make sure that the data container has the right type
    if not isinstance(self.__data_container, DataContainer):
      raise TypeError("the data container has the wrong type")
    self.__data_container.add_observer(self)
    self.__interactor_style = vtk.vtkInteractorStyleTrackballCamera()
    self.__interactor = interactor   
    self.__interactor.SetInteractorStyle(self.__interactor_style)
    self.__picker = self.__interactor.GetPicker()
    self.__perform_picking = True
    
    self.__ignore_observable_change = False

    # Here we keep the selected models (by props)
    self.__selected_props = set()

    self.__interactor_style.AddObserver("LeftButtonPressEvent", self.__on_left_button_pressed)
    self.__interactor_style.AddObserver("LeftButtonReleaseEvent", self.__on_left_button_released)
    self.__interactor_style.AddObserver("MouseMoveEvent", self.__on_mouse_move)


  def __pick(self, xy_pos, renderer):
    # Perform the picking
    self.__picker.Pick(xy_pos[0], xy_pos[1], 0, renderer)
    # Get what you picked
    picked_prop = self.__picker.GetProp3D()
    # Make sure we really picked something
    if picked_prop:
      # Remove the selected model if the user holds the ctrl key and selects it for the second time
      if self.__interactor.GetControlKey() and picked_prop in self.__selected_props:
        self.__selected_props.remove(picked_prop)
        picked_prop = None

    # Clear the current selection if the user doesn't hold the ctrl. key
    if not self.__interactor.GetControlKey():
      self.__selected_props.clear()

    if picked_prop:
      self.__selected_props.add(picked_prop)

    # We will notify the data container to update its selection. This would call this object's
    # observable_changed method. We are not interested in that since we are initiating the change.
    # That's why the following lines:
    ignore_observable_change = self.__ignore_observable_change # svae the current state
    self.__ignore_observable_change = True

    # Update the container which then notifies all observers (including this one that new selection was made)
    self.__data_container.set_model_selection_by_props(list(self.__selected_props))
    
    # Restore the state
    self.__ignore_observable_change = ignore_observable_change


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


  def observable_changed(self, change, data):
    if self.__ignore_observable_change:
      return
    if change == DataContainer.change_is_new_selection:
      self.__selected_props.clear()
      for model in data:
        self.__selected_props.add(model.prop_3d)
