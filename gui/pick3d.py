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
    
    # Here we keep the selected models (by props)
    self.__selected_vtk_properties = set()

    self.__interactor_style.AddObserver("LeftButtonPressEvent", self.__on_left_button_pressed)
    self.__interactor_style.AddObserver("LeftButtonReleaseEvent", self.__on_left_button_released)
    self.__interactor_style.AddObserver("MouseMoveEvent", self.__on_mouse_move)


  def __pick(self, xy_pos, renderer):
    # Perform the picking
    self.__picker.Pick(xy_pos[0], xy_pos[1], 0, renderer)
    # Get what you picked
    picked_vtk_property = None    
    if self.__picker.GetProp3D():
      picked_vtk_property = self.__picker.GetProp3D().GetProperty()

    if not self.__interactor.GetControlKey(): # the user doesn't hold ctrl. key
      self.__selected_vtk_properties.clear()
    elif picked_vtk_property in self.__selected_vtk_properties: # the user holds ctrl. and selects the same model twice
      self.__selected_vtk_properties.remove(picked_vtk_property)
      picked_vtk_property = None # unselected the already selected model

    if picked_vtk_property:
      self.__selected_vtk_properties.add(picked_vtk_property)

    # Update the container which then notifies all observers (including this one that new selection was made)
    self.__data_container.set_model_selection_by_vtk_properties(list(self.__selected_vtk_properties))


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
    if change == DataContainer.change_is_new_selection:
      self.__selected_vtk_properties.clear()
      for model in data:
        self.__selected_vtk_properties.add(model.vtk_property)
