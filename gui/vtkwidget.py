import vtk
from core.progress import ProgressBar
from core.datacontainer import DataContainer
from core.modelview import Observer
from .vtkqgl import VTKQGLWidget
from .pick3d import ModelPicker

class VtkWidget(Observer):
  def __init__(self, parent_qt_frame, data_container, progress_bar = None):
    self.__data_container = data_container
    # Make sure that the data container has the right type
    if not isinstance(self.__data_container, DataContainer):
      raise TypeError("the data container has the wrong type")
    # Register itself as an observer to the data_container
    self.__data_container.add_observer(self)

    self.__progress_bar = None
    if progress_bar and isinstance(progress_bar, ProgressBar):
      self.__progress_bar = progress_bar

    # The render window
    self.__vtk_widget = VTKQGLWidget(parent_qt_frame)
    self.__vtk_widget.renderer.SetBackground(0.4, 0.41, 0.42)
    self.__vtk_widget.enable_depthpeeling()

    # This guy is very important: it handles all the model selection in the 3D view
    self.__model_picker = ModelPicker(self.__data_container, self.render_window_interactor)

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
    # Tell the user we are busy
    if self.__progress_bar:
      self.__progress_bar.init(1, len(data_items), "Adding models to 3D renderer: ")

    counter = 0

    # Add all the data to the renderer
    for data_item in data_items:
      counter += 1
      #self.renderer.AddViewProp(data_item.prop_3d)
      data_item.add_yourself(self.renderer, self.render_window_interactor)
      if self.__progress_bar:
        self.__progress_bar.set_progress(counter)

    # Make sure that we see all the new data
    if len(data_items) > 0:
      self.reset_view()

    # We are done
    if self.__progress_bar:
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
