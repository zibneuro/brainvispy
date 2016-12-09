import vtk
from vis.vtkpoly import VtkPolyModel

class VisNeuralConnection(VtkPolyModel):
  def __init__(self, name, p1, p2, cylinder_radius):
    VtkPolyModel.__init__(self, self.__create_vtk_rep(p1, p2, cylinder_radius), name)
    self.__cylinder_radius = cylinder_radius


  def on_weight_changed(self, neural_connection):
    print("changing the color according to the new weight")


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
