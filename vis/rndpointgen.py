import vtk
import random
from copy import deepcopy

class RandomMeshPointsGenerator:
  def __init__(self, vtk_mesh):
    if not isinstance(vtk_mesh, vtk.vtkPolyData):
      raise TypeError("input argument 'vtk_mesh' has to be a vtkPolyData")

    if not vtk_mesh.GetPolys():
      raise ValueError("input argument 'vtk_mesh' has no triangles")

    self.__vtk_mesh = vtk_mesh

    # This is the guy who does an efficient line-surface intersection
    self.__obb_tree = vtk.vtkOBBTree()
    self.__obb_tree.SetDataSet(vtk_mesh)
    self.__obb_tree.BuildLocator()


  def generate_points_inside_mesh(self, num_points):
    points = list()
    for i in range(num_points):
      points.append(self.sample_mesh_surface())
    return points


  def sample_mesh_surface(self):
    """Returns a point on the mesh surface."""
    
    if self.__vtk_mesh.GetNumberOfCells() != self.__vtk_mesh.GetNumberOfPolys():
      print("RandomMeshPointsGenerator.sample_mesh_surface: #cells != #polys")
    
    # Make 100 attempts to get a triangle. If all fail, throw an exception
    for i in range(100):
      # Get a random triangle
      cell_id = random.randint(0, self.__vtk_mesh.GetNumberOfCells() - 1)
      vertex_ids = vtk.vtkIdList()
      self.__vtk_mesh.GetCellPoints(cell_id, vertex_ids)
      # Make sure the polygon we got has at least 3 vertices
      if vertex_ids.GetNumberOfIds() >= 3:
        return self.__sample_triangle(self.__vtk_mesh.GetPoints(), vertex_ids)

    # We couldn't get a single triangle in 100 attempts => throw an exception
    raise ValueError("input argument 'vtk_mesh' seems to have no triangles")


  def __sample_triangle(self, vtk_points, vertex_ids):
    # Get the triangle points
    a = deepcopy(vtk_points.GetPoint(vertex_ids.GetId(0)))
    b = deepcopy(vtk_points.GetPoint(vertex_ids.GetId(1)))
    c = deepcopy(vtk_points.GetPoint(vertex_ids.GetId(2)))
   
    # Get the random weights
    u = random.uniform(0, 1)
    v = random.uniform(0, 1)
    # Make sure that we stay within the triangle
    if u + v > 1:
      u = 1 - u
      v = 1 - v

    # Return the point
    return (
      a[0] + u*(b[0] - a[0]) + v*(c[0] - a[0]),
      a[1] + u*(b[1] - a[1]) + v*(c[1] - a[1]),
      a[2] + u*(b[2] - a[2]) + v*(c[2] - a[2]))
