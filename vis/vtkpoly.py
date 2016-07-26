import vtk
from .vtkmodel import VtkModel

class VtkPolyModel(VtkModel):
  def __init__(self, file_name, name, poly_data):
    if not isinstance(poly_data, vtk.vtkPolyData):
      raise TypeError("input has to be vtkPolyData")

    super().__init__(file_name, name)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly_data)
    self.__actor = vtk.vtkActor()
    self.__actor.SetMapper(mapper)
    self.__actor.GetProperty().SetAmbient(0.05)


  def add_yourself(self, renderer, interactor):
    renderer.AddActor(self.actor)


  def visibility_on(self):
    self.prop_3d.VisibilityOn()


  def visibility_off(self):
    self.prop_3d.VisibilityOff()


  def toggle_visibility(self):
    self.prop_3d.SetVisibility(1 - self.prop_3d.GetVisibility())


  def highlight_on(self):
    self.__actor.GetProperty().SetAmbient(0.5)


  def highlight_off(self):
    self.__actor.GetProperty().SetAmbient(0.05)


  def set_transparency(self, value):
    """Sets the transparency of the model (0: non-transparent, i.e, not see-through,
    1: full transparent, i.e., invisible)."""
    self.__actor.GetProperty().SetOpacity(1.0 - value)


  def get_transparency(self):
    """Returns the transparency of the model (0: non-transparent, i.e, not see-through,
    1: full transparent, i.e., invisible)."""
    return 1.0 - self.__actor.GetProperty().GetOpacity()


  def get_color(self):
    return self.__actor.GetProperty().GetDiffuseColor()


  def set_color(self, r, g, b):
    self.__actor.GetProperty().SetDiffuseColor(r, g, b)
    self.__actor.GetProperty().SetAmbientColor(r, g, b)


  @property
  def actor(self):
    return self.__actor


  @property
  def prop_3d(self):
    return self.__actor
