import vtk
from core.progress import ProgressBar
from core.datacontainer import DataContainer
from .vtkqgl import VTKQGLWidget
from .pick3d import ModelPicker

class VtkWidget(VTKQGLWidget):
  def __init__(self, parent_qt_frame, data_container, progress_bar):
    super().__init__(parent_qt_frame)
    # Register itself as an observer to the data_container
    self.__data_container = data_container
    self.__data_container.add_observer(self)
    # This one indicates the progress of computationally heavy tasks
    self.__progress_bar = progress_bar

    # The render window
    self.renderer.SetBackground(0.4, 0.41, 0.42)
    self.enable_depthpeeling()
    self.render_window_interactor.AddObserver("KeyReleaseEvent", self.__on_key_released)

    # This guy is very important: it handles all the model selection in the 3D view
    self.__model_picker = ModelPicker(self.__data_container, self.render_window_interactor)

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


  def observable_changed(self, change, data):
    # Decide what to do depending on what changed
    if change == DataContainer.change_is_new_brain_regions:
      self.__add_data_items(data, self.__reset_view_after_adding_models)
    elif change == DataContainer.change_is_new_neurons:
      self.__add_data_items(data, False)
    elif change == DataContainer.change_is_data_visibility or change == DataContainer.change_is_slice_index:
      self.reset_clipping_range()
    elif change == DataContainer.change_is_new_selection:
      self.__highlight_models(data)
    elif change == DataContainer.change_is_deleted_models:
      self.__delete_models(data)
    else:
      self.render()


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


  @property
  def reset_view_after_adding_models(self):
    return self.__reset_view_after_adding_models


  def do_reset_view_after_adding_models(self, value):
    self.__reset_view_after_adding_models = value


  def __on_key_released(self, interactor, data):
    if data == "KeyReleaseEvent":
      key = interactor.GetKeySym()
      if key == "Delete":
        self.__model_picker.delete_selected_models()


  def __add_data_items(self, data_items, reset_view_after_adding_models):
    if not data_items:
      return

    # Tell the user we are busy
    self.__progress_bar.init(1, len(data_items), "Adding models to 3D renderer: ")
    counter = 0
    # Add all the data to the renderer
    for data_item in data_items:
      counter += 1
      # Add the visual representation of the data item to the renderer
      try:
        self.renderer.AddActor(data_item.visual_representation.actor)
      except AttributeError:
        pass
      self.__progress_bar.set_progress(counter)
    # Make sure that we see all the new data
    if reset_view_after_adding_models:
      self.reset_view()
    else:
      self.reset_clipping_range()
    # We are done
    self.__progress_bar.done()


  def __highlight_models(self, models):
    # First un-highlight all models
    for model in self.__data_container.get_models():
      try:
        model.visual_representation.highlight_off()
      except AttributeError:
        pass
    # Now highligh the ones we want to highlight
    for model in models:
      try:
        model.visual_representation.highlight_on()
      except AttributeError:
        pass
    # Update the view
    self.render()


  def __delete_models(self, models):
    for model in models:
      model.remove_yourself(self.renderer, self.render_window_interactor)
    self.reset_clipping_range()
