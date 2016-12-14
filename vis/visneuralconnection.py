import vtk
import math
import vis.visutils
from vis.vtkpoly import VtkPolyModel

class VisNeuralConnection(VtkPolyModel):
  def __init__(self, name, p1, p2, cylinder_radius):
    VtkPolyModel.__init__(self, self.__create_vtk_rep(p1, p2, cylinder_radius), name)
    self.__cylinder_radius = cylinder_radius
    #self.set_off_ambient(0.4)
    #self.set_on_ambient(0.8)


  def on_weight_changed(self, neural_connection):
    rgb = vis.visutils.map_to_blue_red_rgb(neural_connection.weight)
    self.set_color(rgb[0], rgb[1], rgb[2])


  @property
  def cylinder_radius(self):
    return self.__cylinder_radius


  def __create_vtk_rep(self, p1, p2, cylinder_radius):
    line_source = vtk.vtkLineSource()
    line_source.SetPoint1(p1)
    line_source.SetPoint2(p2)
    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputConnection(line_source.GetOutputPort())
    tube_filter.SetRadius(cylinder_radius)
    tube_filter.SetNumberOfSides(24)
    tube_filter.Update()
    return tube_filter.GetOutput()
