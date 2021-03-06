import vtk
import random
from .vtkmodel import VtkModel

class VtkPolyModel(VtkModel):
  def __init__(self, vtk_poly_data, name = "VtkPolyModel"):
    if not isinstance(vtk_poly_data, vtk.vtkPolyData):
      raise TypeError("vtk_poly_data has to be vtkPolyData")

    VtkModel.__init__(self, name)

    self.__off_ambient = 0.05
    self.__on_ambient = 0.3

    self.__mapper = vtk.vtkPolyDataMapper()
    self.__mapper.SetInputData(vtk_poly_data)
    self.__actor = vtk.vtkActor()
    self.__actor.SetMapper(self.__mapper)
    self.__actor.GetProperty().SetAmbient(self.__off_ambient)
    self.__actor.GetProperty().BackfaceCullingOff()


  @staticmethod
  def generate_random_rgb_color():
    return vtk.vtkMath.HSVToRGB((random.uniform(0.0, 0.6), 0.8, 1.0))


  def set_point(self, point_index, coords):
    self.vtk_points.SetPoint(point_index, coords)


  def add_yourself(self, renderer, interactor):
    renderer.AddActor(self.actor)


  def remove_yourself(self, renderer, interactor):
    renderer.RemoveActor(self.actor)


  def set_visibility(self, bool_value):
    self.actor.SetVisibility(bool_value)


  def visibility_on(self):
    self.actor.VisibilityOn()


  def visibility_off(self):
    self.actor.VisibilityOff()


  def toggle_visibility(self):
    self.actor.SetVisibility(1 - self.actor.GetVisibility())


  def is_visible(self):
    return self.actor.GetVisibility() == 1


  def get_visibility(self):
    return self.actor.GetVisibility()


  def highlight_on(self):
    self.__actor.GetProperty().SetAmbient(self.__on_ambient)


  def highlight_off(self):
    self.__actor.GetProperty().SetAmbient(self.__off_ambient)


  def set_off_ambient(self, value):
    self.__off_ambient = value


  def set_on_ambient(self, value):
    self.__on_ambient = value


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
  def vtk_poly_data(self):
    return self.__mapper.GetInput()


  @property
  def vtk_points(self):
    return self.__mapper.GetInput().GetPoints()


  @property
  def prop3d(self):
    return self.__actor
