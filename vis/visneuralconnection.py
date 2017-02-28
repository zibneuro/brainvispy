import vtk
import math
import vis.visutils
import numpy as np
from vis.vtkpoly import VtkPolyModel
from core.settings import Settings

class VisNeuralConnection(VtkPolyModel):
  def __init__(self, name, p1, p2, cylinder_radius, is_loop):
    # First, create the visual representation
    if is_loop:
      vtk_rep = self.__create_vtk_loop_rep(p1)
    else:
      vtk_rep = self.__create_vtk_rep(p1, p2, cylinder_radius)

    # Init the rest
    VtkPolyModel.__init__(self, vtk_rep, name)
    self.__cylinder_radius = cylinder_radius
    self.actor.GetProperty().SetLineWidth(3)


  def on_weight_changed(self, neural_connection):
    rgb = vis.visutils.map_to_blue_red_rgb(neural_connection.weight)
    self.set_color(rgb[0], rgb[1], rgb[2])


  @property
  def cylinder_radius(self):
    return self.__cylinder_radius


  def __create_vtk_loop_rep(self, p):
    n = (0, -1/math.sqrt(2), 1/math.sqrt(2))
    r = Settings.loop_radius
    vtk_circle_src = vtk.vtkRegularPolygonSource()
    vtk_circle_src.SetCenter(p[0] + r*n[0], p[1] - r*n[1], p[2] + r*n[2])
    vtk_circle_src.SetNormal(n)
    vtk_circle_src.SetRadius(r)
    vtk_circle_src.GeneratePolygonOff()
    vtk_circle_src.SetNumberOfSides(40)
    vtk_circle_src.Update()
    return vtk_circle_src.GetOutput()


  def __create_vtk_rep(self, p1, p2, cylinder_radius):
    cone = self.__create_cone(p1, p2)
    line = self.__create_connecting_line(p1, p2)

    append_filter = vtk.vtkAppendPolyData()
    append_filter.AddInputData(cone);
    append_filter.AddInputData(line);
    append_filter.Update()
    return append_filter.GetOutput()


  def __create_connecting_line(self, p1, p2):
    # The positions of the two neurons
    vtk_points = vtk.vtkPoints()
    vtk_points.InsertNextPoint(p1[0], p1[1], p1[2])
    vtk_points.InsertNextPoint(p2[0], p2[1], p2[2])
    # The VTK ids of the two positions
    vtk_point_ids = (0, 1)
    # The connecting line
    vtk_line = vtk.vtkCellArray()
    vtk_line.InsertNextCell(2, vtk_point_ids)
    # Add everything together to a vtkPolyData object
    vtk_poly_data = vtk.vtkPolyData()
    vtk_poly_data.SetPoints(vtk_points)
    vtk_poly_data.SetLines(vtk_line)
    # Return the connecing line
    return vtk_poly_data


  def __create_cone(self, p1, p2):
    a = np.array([p1[0], p1[1], p1[2]])
    b = np.array([p2[0], p2[1], p2[2]])
    d = b - a
    neuron_dist = np.linalg.norm(d)

    # The distance from 'a' to the base (start) of the cone
    dist_to_cone_mid = neuron_dist - 0.95*Settings.neuron_sphere_radius - 0.5*Settings.neural_connection_cone_length
    dist_to_cone_mid = max(0, dist_to_cone_mid)

    d /= neuron_dist
    
    cone_source = vtk.vtkConeSource()
    cone_source.SetCenter(a + dist_to_cone_mid*d)
    cone_source.SetResolution(24)
    cone_source.SetHeight(Settings.neural_connection_cone_length)
    cone_source.SetDirection(d)
    cone_source.SetRadius(Settings.neural_connection_cone_radius)
    cone_source.Update()

    return cone_source.GetOutput()

"""
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
"""
