import vtk
import random
from .vtkmodel import VtkModel

class VtkPolyModel(VtkModel):
  def __init__(self, poly_data, file_name, name = "VtkPolyModel"):
    if not isinstance(poly_data, vtk.vtkPolyData):
      raise TypeError("input has to be vtkPolyData")

    super().__init__(file_name, name)

    self.__off_ambient = 0.05
    self.__on_ambient = 0.3

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly_data)
    self.__actor = vtk.vtkActor()
    self.__actor.SetMapper(mapper)
    self.__actor.GetProperty().SetAmbient(self.__off_ambient)
    self.__actor.GetProperty().BackfaceCullingOff()


  @staticmethod
  def generate_random_rgb_color():
    return vtk.vtkMath.HSVToRGB((random.uniform(0.0, 0.6), 0.8, 1.0))


  def add_yourself(self, renderer, interactor):
    renderer.AddActor(self.actor)


  def remove_yourself(self, renderer, interactor):
    renderer.RemoveActor(self.actor)


  def visibility_on(self):
    self.actor.VisibilityOn()


  def visibility_off(self):
    self.actor.VisibilityOff()


  def toggle_visibility(self):
    self.actor.SetVisibility(1 - self.actor.GetVisibility())


  def is_visible(self):
    return self.actor.GetVisibility() == 1


  def highlight_on(self):
    self.__actor.GetProperty().SetAmbient(self.__on_ambient)


  def highlight_off(self):
    self.__actor.GetProperty().SetAmbient(self.__off_ambient)


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


  def set_see_inside(self, value):
    self.__actor.GetProperty().SetFrontfaceCulling(value)


  @property
  def see_inside(self):
    return self.__actor.GetProperty().GetFrontfaceCulling()


  @property
  def actor(self):
    return self.__actor


  @property
  def vtk_property(self):
    return self.actor.GetProperty()
