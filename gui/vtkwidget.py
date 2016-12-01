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
    self.__model_picker = ModelPicker(self)

    # Here we keep the selected models in a (vtkProp3D, model) dictionary
    self.__prop3d_to_selected_model = dict()
    # Here we keep ALL models in a (vtkProp3D, model) dictionary
    self.__prop3d_to_model = dict()

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
      self.__set_selection(data)
    elif change == DataContainer.change_is_deleted_models:
      self.__delete_models(data)
    else:
      self.render()


  def on_picked_prop3d(self, prop3d):
    # Does the user hold the ctrl. key?
    if self.__model_picker.is_ctrl_key_pressed():
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
        self.__data_container.delete_models(list(self.__prop3d_to_selected_model.values()))
        self.render()


  def __add_data_items(self, data_items, reset_view_after_adding_models):
    if not data_items:
      return

    # Tell the user we are busy
    self.__progress_bar.init(1, len(data_items), "Adding models to 3D renderer: ")
    counter = 0

    # Add data to the renderer and to the internal dictionary
    for data_item in data_items:
      counter += 1
      # We need a data item with a prop3d
      try:
        prop3d = data_item.visual_representation.prop3d
      except AttributeError:
        pass
      else:
        self.__prop3d_to_model[prop3d] = data_item
        self.renderer.AddActor(prop3d)

      # Update the progress bar
      self.__progress_bar.set_progress(counter)
      
    # Make sure that we see all the new data
    if reset_view_after_adding_models:
      self.reset_view()
    else:
      self.reset_clipping_range()
    # We are done
    self.__progress_bar.done()


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
    self.render()


  def __delete_models(self, models):
    for model in models:
      try: # we can handle only data items that are pickable, i.e., that have a visual representation with a prop3d
        prop3d = model.visual_representation.prop3d
      except AttributeError:
        pass
      else:
        self.renderer.RemoveActor(prop3d)
        # silently delete the models (no exception even if they are not in the dictionary)
        self.__prop3d_to_model.pop(prop3d, None)
        self.__prop3d_to_selected_model.pop(prop3d, None)
    # Update the 3d view
    self.reset_clipping_range()
