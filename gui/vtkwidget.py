import vtk
from core.progress import ProgressBar
from core.datacontainer import DataContainer
from .vtkqgl import VTKQGLWidget
from .pick3d import ModelPicker

class VtkWidget(VTKQGLWidget):
  def __init__(self, parent_qt_frame, controller, data_container, progress_bar):
    super().__init__(parent_qt_frame)
    # Save a reference to the controller
    self.__controller = controller
    # Register itself as an observer to the data_container
    self.__data_container = data_container
    self.__data_container.add_observer(self)
    # This one indicates the progress of computationally heavy tasks
    self.__progress_bar = progress_bar

    # The observers of this guy
    self.__observers = list()

    # The render window
    self.renderer.SetBackground(0.4, 0.41, 0.42)
    self.enable_depthpeeling()
    #self.render_window_interactor.AddObserver("KeyReleaseEvent", self.__on_key_released)
    #self.render_window_interactor.AddObserver("LeftButtonPressEvent", self.__on_left_button_pressed)
    #self.render_window_interactor.AddObserver("LeftButtonReleaseEvent", self.__on_left_button_released)
    #self.render_window_interactor.AddObserver("MouseMoveEvent", self.__on_mouse_moved)
    
    self.__interactor_style = vtk.vtkInteractorStyleTrackballCamera()
    self.interactor.SetInteractorStyle(self.__interactor_style)
    self.__interactor_style.AddObserver("KeyReleaseEvent", self.__on_key_released)
    self.__interactor_style.AddObserver("LeftButtonPressEvent", self.__on_left_button_pressed)
    self.__interactor_style.AddObserver("LeftButtonReleaseEvent", self.__on_left_button_released)
    self.__interactor_style.AddObserver("MouseMoveEvent", self.__on_mouse_moved)

    # This guy is very important: it handles all the model selection in the 3D view
    #self.__model_picker = ModelPicker(self)
    self.__prop3d_picker = vtk.vtkPropPicker()
    self.interactor.SetPicker(self.__prop3d_picker)
    self.__perform_prop3d_picking = True

    # We might or might not want to reset the view after new models have been added
    self.__reset_view_after_adding_models = True

    # We want to see xyz axes in the lower left corner of the window
    lower_left_axes_actor = vtk.vtkAxesActor()
    lower_left_axes_actor.SetXAxisLabelText("X")
    lower_left_axes_actor.SetYAxisLabelText("Y")
    lower_left_axes_actor.SetZAxisLabelText("Z")
    lower_left_axes_actor.SetTotalLength(1.5, 1.5, 1.5)
    self.__lower_left_axes_widget = vtk.vtkOrientationMarkerWidget()
    self.__lower_left_axes_widget.SetOrientationMarker(lower_left_axes_actor)
    self.__lower_left_axes_widget.KeyPressActivationOff()
    self.__lower_left_axes_widget.SetInteractor(self.render_window_interactor)
    self.__lower_left_axes_widget.SetViewport(0.0, 0.0, 0.2, 0.2)
    self.__lower_left_axes_widget.SetEnabled(1)
    self.__lower_left_axes_widget.InteractiveOff()


  def add_observer(self, observer):
    self.__observers.append(observer)


  def __on_key_released(self, interactor, data):
    if data == "KeyReleaseEvent":
      key = self.interactor.GetKeySym()
      for observer in self.__observers:
        try:
          observer.on_key_released(self, key)
        except AttributeError:
          pass


  def __on_left_button_pressed(self, interactor, data):
    for observer in self.__observers:
      try:
        observer.on_left_button_pressed(self)
      except AttributeError:
        pass
    # Forward the event
    self.__interactor_style.OnLeftButtonDown()


  def __on_left_button_released(self, interactor, data):
    # First, report the left button release event
    for observer in self.__observers:
      try:
        observer.on_left_button_released(self)
      except AttributeError:
        pass
    # Forward the event
    self.__interactor_style.OnLeftButtonUp()


  def __on_mouse_moved(self, interactor, data):
    for observer in self.__observers:
      try:
        observer.on_mouse_moved(self)
      except AttributeError:
        pass
    # Forward the event
    self.__interactor_style.OnMouseMove()


  def pick(self):
    # Get the first renderer assuming that the event took place there
    renderer = self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()
    # Where did the user click with the mouse
    xy_pick_pos = self.interactor.GetEventPosition()
    # Perform the picking
    self.__prop3d_picker.Pick(xy_pick_pos[0], xy_pick_pos[1], 0, renderer)
    # Call the user with the picked prop
    return self.__prop3d_picker.GetProp3D()


  def is_ctrl_key_pressed(self):
    return self.interactor.GetControlKey() != 0


  def observable_changed(self, change, data):
    # Decide what to do depending on what changed
    if change == DataContainer.change_is_data_visibility or change == DataContainer.change_is_slice_index:
      self.reset_clipping_range()
    else:
      self.render()


  def on_mouse_over_prop3d(self, prop3d):
    try:
      model = self.__prop3d_to_model[prop3d]
    except KeyError:
      return

    # Let the controller handle the case
    self.__controller.on_mouse_over_model(model, self)


  def connect_points(self, a, b):
    print("connecting", a, "to", b)


  def add_models(self, models):
    if not models:
      return

    # Tell the user we are busy
    self.__progress_bar.init(1, len(models), "Adding models to 3D renderer: ")
    counter = 0

    # Add data to the renderer and to the internal dictionary
    for model in models:
      counter += 1
      # We need a data item with a prop3d
      try:
        prop3d = model.visual_representation.prop3d
      except AttributeError:
        pass
      else:
        self.renderer.AddActor(prop3d)

      # Update the progress bar
      self.__progress_bar.set_progress(counter)
      
    # Make sure that we see all models
    self.reset_view()
    # We are done
    self.__progress_bar.done()


  def delete_models(self, models):
    for model in models:
      try: # we can handle only data items that are pickable, i.e., that have a visual representation with a prop3d
        prop3d = model.visual_representation.prop3d
      except AttributeError:
        pass
      else:
        self.renderer.RemoveActor(prop3d)
    # Update the 3d view
    self.reset_clipping_range()


  def get_camera_position(self):
    return self.renderer.GetActiveCamera().GetPosition()

  def set_camera_position(self, position):
    return self.renderer.GetActiveCamera().SetPosition(position)


  def get_camera_look_at(self):
    return self.renderer.GetActiveCamera().GetFocalPoint()

  def set_camera_look_at(self, look_at):
    return self.renderer.GetActiveCamera().SetFocalPoint(look_at)


  def get_camera_view_up(self):
    return self.renderer.GetActiveCamera().GetViewUp()

  def set_camera_view_up(self, view_up):
    return self.renderer.GetActiveCamera().SetViewUp(view_up)


  def render(self):
    """Renders the scene"""
    self.render_window_interactor.Render()


  def reset_clipping_range(self):
    """Resets the clipping range of the camera and renders the scene"""
    self.renderer.ResetCameraClippingRange()
    self.render_window_interactor.Render()


  def reset_view(self):
    """Modifies the camera such that all (visible) data items are in the viewing frustum."""
    self.renderer.ResetCamera()
    self.renderer.ResetCameraClippingRange()
    self.render_window_interactor.Render()
