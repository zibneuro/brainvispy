import vtk

class ModelPicker:
  def __init__(self, model_picker_user):
    # Init all members
    self.__model_picker_user = model_picker_user
    #self.__interactor_style = vtk.vtkInteractorStyleTrackballCamera()
    self.__picker = vtk.vtkPropPicker()
    self.__interactor = model_picker_user.interactor
    #self.__interactor.SetInteractorStyle(self.__interactor_style)
    self.__interactor.SetPicker(self.__picker)
    self.__perform_picking = True

    #self.__interactor_style.AddObserver("LeftButtonPressEvent", self.__on_left_button_pressed)
    #self.__interactor_style.AddObserver("LeftButtonReleaseEvent", self.__on_left_button_released)
    #self.__interactor_style.AddObserver("MouseMoveEvent", self.__on_mouse_move)


  def __on_left_button_pressed(self, obj, event):
    self.__perform_picking = True
    self.__interactor_style.OnLeftButtonDown()


  def __on_left_button_released(self, obj, event):
    if self.__perform_picking:
      prop3d = self.__get_prop3d_under_mouse_pointer()
      self.__model_picker_user.on_picked_prop3d(prop3d)
    # Do what you normally do
    self.__interactor_style.OnLeftButtonUp()


  def __on_mouse_move(self, obj, event):
    self.__perform_picking = False
    prop3d = self.__get_prop3d_under_mouse_pointer()
    if prop3d:
      self.__model_picker_user.on_mouse_over_prop3d(prop3d)
    self.__interactor_style.OnMouseMove()


  def __get_prop3d_under_mouse_pointer(self):
    # Get the first renderer assuming that the event took place there
    renderer = self.__interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()
    # Where did the user click with the mouse
    xy_pick_pos = self.__interactor.GetEventPosition()
    # Perform the picking
    self.__picker.Pick(xy_pick_pos[0], xy_pick_pos[1], 0, renderer)
    # Call the user with the picked prop
    return self.__picker.GetProp3D()
