import vtk
from core.progress import ProgressBar
from core.datacontainer import DataContainer
from .vtkqgl import VTKQGLWidget
from .pick3d import ModelPicker

class VtkWidget:
  def __init__(self, parent_qt_frame, data_container, progress_bar):
    self.test_1 = 2
    # Make sure that the data container has the right type
    if not isinstance(data_container, DataContainer):
      raise TypeError("the data container has to be of type DataContainer")
    # Register itself as an observer to the data_container
    self.__data_container = data_container
    self.__data_container.add_observer(self)

    if not isinstance(progress_bar, ProgressBar):
      raise TypeError("the progress bar has to be of type ProgressBar")
    self.__progress_bar = progress_bar

    # The render window
    self.__vtk_widget = VTKQGLWidget(parent_qt_frame)
    self.__vtk_widget.renderer.SetBackground(0.4, 0.41, 0.42)
    self.__vtk_widget.enable_depthpeeling()

    self.__vtk_widget.render_window_interactor.AddObserver("KeyReleaseEvent", self.__on_key_released)

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


  def __on_key_released(self, interactor, data):
    if data == "KeyReleaseEvent":
      key = interactor.GetKeySym()
      if key == "Delete":
        self.__data_container.delete_selected_models()


  def observable_changed(self, change, data):
    # Decide what to do depending on what changed
    if change == DataContainer.change_is_new_data:
      self.__add_data_items(data)
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


  @property
  def widget(self):
    return self.__vtk_widget


  @property
  def render_window(self):
    return self.widget.render_window


  @property
  def render_window_interactor(self):
    return self.widget.render_window_interactor


  @property
  def renderer(self):
    return self.widget.renderer


  def __add_data_items(self, data_items):
    if not data_items:
      return
    # Tell the user we are busy
    self.__progress_bar.init(1, len(data_items), "Adding models to 3D renderer: ")
    counter = 0
    # Add all the data to the renderer
    for data_item in data_items:
      counter += 1
      #self.renderer.AddViewProp(data_item.prop_3d)
      data_item.add_yourself(self.renderer, self.render_window_interactor)
      self.__progress_bar.set_progress(counter)
    # Make sure that we see all the new data
    if self.__reset_view_after_adding_models:
      self.reset_view()
    # We are done
    self.__progress_bar.done()


  def __highlight_models(self, models):
    # First un-highlight all models
    for model in self.__data_container.get_models():
      model.highlight_off()
    # Now highligh the ones we want to highlight
    for model in models:
      model.highlight_on()
    # Update the view
    self.render()


  def __delete_models(self, models):
    for model in models:
      model.remove_yourself(self.renderer, self.render_window_interactor)
    self.reset_clipping_range()
