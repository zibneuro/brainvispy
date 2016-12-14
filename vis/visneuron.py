import vtk
import vis.visutils
from vis.vtkpoly import VtkPolyModel

class VisNeuron(VtkPolyModel):
  def __init__(self, name, position, sphere_radius):
    VtkPolyModel.__init__(self, self.__create_vtk_rep(position, sphere_radius), name)
    self.__sphere_radius = sphere_radius


  def on_threshold_changed(self, neuron):
    rgb = vis.visutils.map_to_blue_red_rgb(neuron.threshold)
    self.set_color(rgb[0], rgb[1], rgb[2])


  @property
  def sphere_radius(self):
    return self.__sphere_radius


  def __create_vtk_rep(self, p, sphere_radius):
    vtk_sphere_source = vtk.vtkSphereSource()
    vtk_sphere_source.SetThetaResolution(12)
    vtk_sphere_source.SetPhiResolution(12)
    vtk_sphere_source.SetRadius(sphere_radius)
    vtk_sphere_source.SetCenter(p[0], p[1], p[2])
    vtk_sphere_source.Update()
    return vtk_sphere_source.GetOutput()
