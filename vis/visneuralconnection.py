import vtk
import math
import vis.visutils
from vis.vtkpoly import VtkPolyModel

class VisNeuralConnection(VtkPolyModel):
  def __init__(self, name, p1, p2, cylinder_radius):
    VtkPolyModel.__init__(self, self.__create_vtk_rep(p1, p2, cylinder_radius), name)
    self.__cylinder_radius = cylinder_radius


  def on_weight_changed(self, neural_connection):
    rgb = vis.visutils.map_to_blue_red_rgb(neural_connection.weight)
    self.set_color(rgb[0], rgb[1], rgb[2])


  @property
  def cylinder_radius(self):
    return self.__cylinder_radius


  def __create_vtk_rep(self, p1, p2, cylinder_radius):
    # Create the arrow (a cone)
    normalized_dir = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]
    length = vtk.vtkMath.Norm(normalized_dir)
    cone_height = 0.1*length

    normalized_dir[0] /= length
    normalized_dir[1] /= length
    normalized_dir[2] /= length

    direction = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]
    direction[0] /= length
    direction[1] /= length
    direction[2] /= length
    
    length -= cone_height/2
    direction[0] *= length
    direction[1] *= length
    direction[2] *= length
    cone_end = (p1[0] + direction[0], p1[1] + direction[1], p1[2] + direction[2])
    
    cone_source = vtk.vtkConeSource()
    cone_source.SetCenter(cone_end)
    cone_source.SetResolution(24)
    cone_source.SetHeight(cone_height)
    cone_source.SetDirection(direction)
    cone_source.SetRadius(2*cylinder_radius)
    cone_source.Update()

    length -= cone_height/2
    normalized_dir[0] *= length
    normalized_dir[1] *= length
    normalized_dir[2] *= length
    cone_end = (p1[0] + normalized_dir[0], p1[1] + normalized_dir[1], p1[2] + normalized_dir[2])

    line_source = vtk.vtkLineSource()
    line_source.SetPoint1(p1)
    line_source.SetPoint2(cone_end)
    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputConnection(line_source.GetOutputPort())
    tube_filter.SetRadius(cylinder_radius)
    tube_filter.SetNumberOfSides(24)
    tube_filter.Update()
    
    
    append_filter = vtk.vtkAppendPolyData()
    append_filter.AddInputData(tube_filter.GetOutput());
    append_filter.AddInputData(cone_source.GetOutput());
    append_filter.Update()
    return append_filter.GetOutput()
