import vtk

class VisNeuron(VtkModel):
  def __init__(self, name, position, sphere_radius):
    VtkPolyModel.__init__(self, self.__create_vtk_rep(position, sphere_radius), name)


  def __create_vtk_rep(self, p, sphere_radius):
    vtk_sphere_source = vtk.vtkSphereSource()
    vtk_sphere_source.SetThetaResolution(12)
    vtk_sphere_source.SetPhiResolution(12)
    vtk_sphere_source.SetRadius(sphere_radius)
    vtk_sphere_source.SetCenter(p[0], p[1], p[2])
    vtk_sphere_source.Update()
    return vtk_sphere_source.GetOutput()
