import vtk
import math
import random
import numpy as np

class RandomMeshPointsGenerator:
  def __init__(self, vtk_mesh):
    if not isinstance(vtk_mesh, vtk.vtkPolyData):
      raise TypeError("input argument 'vtk_mesh' has to be a vtkPolyData")

    if not vtk_mesh.GetPolys():
      raise ValueError("input argument 'vtk_mesh' has no triangles")

    self.__vtk_mesh = vtk_mesh

    # Compute the bounding box of the mesh
    vtk_mesh.ComputeBounds()
    self.__bounding_box = b = vtk_mesh.GetBounds()
    self.__bounding_box_diag = math.sqrt((b[1]-b[0])**2 + (b[3]-b[2])**2 + (b[5]-b[4])**2)

    # This is the guy who does an efficient line-surface intersection
    self.__obb_tree = vtk.vtkOBBTree()
    self.__obb_tree.SetDataSet(vtk_mesh)
    self.__obb_tree.BuildLocator()


  def generate_points_inside_mesh(self, num_points):
    points = list()
    for i in range(num_points):
      # Randomly pick a triangle from the mesh and randomly pick a point on it
      (x, y, z) = self.__get_random_mesh_triangle()
      p_on = self.__sample_point_on_triangle(x, y, z)
      # Based on this, generate a point inside the mesh
      p_in = self.__generate_random_point_in_mesh(x, y, z, p_on)
      points.append(p_in)
    return points


  def __get_random_mesh_triangle(self):
    """Returns a point on the mesh surface."""
    if self.__vtk_mesh.GetNumberOfCells() != self.__vtk_mesh.GetNumberOfPolys():
      print("RandomMeshPointsGenerator.sample_mesh_surface: #cells != #polys")
    
    vtk_points = self.__vtk_mesh.GetPoints()
    
    # Make 100 attempts to get a triangle. If all fail, throw an exception
    for i in range(100):
      # Get a random triangle
      cell_id = random.randint(0, self.__vtk_mesh.GetNumberOfCells() - 1)
      vertex_ids = vtk.vtkIdList()
      self.__vtk_mesh.GetCellPoints(cell_id, vertex_ids)

      # Make sure the polygon has at least 3 vertices
      if vertex_ids.GetNumberOfIds() >= 3:
        a = vtk_points.GetPoint(vertex_ids.GetId(0))
        a = np.array([a[0], a[1], a[2]]) # numpy array
        b = vtk_points.GetPoint(vertex_ids.GetId(1))
        b = np.array([b[0], b[1], b[2]]) # numpy array
        c = vtk_points.GetPoint(vertex_ids.GetId(2))
        c = np.array([c[0], c[1], c[2]]) # numpy array
        return (a, b, c)

    # We couldn't get a single triangle in 100 attempts => throw an exception
    raise ValueError("input argument 'vtk_mesh' seems to have no triangles")


  def __sample_point_on_triangle(self, x, y, z):
    # Get the random weights
    u = random.uniform(0, 1)
    v = random.uniform(0, 1)
    # Make sure that we stay within the triangle
    if u + v > 1:
      u = 1 - u
      v = 1 - v

    # Return the point
    return x + u*(y - x) + v*(z - x)


  def __generate_random_point_in_mesh(self, x, y, z, tria_point):
    # Get the triangle normal
    n = np.cross(y - x, z - x)
    n /= np.linalg.norm(n)
    
    # Generate two points, a and b, for which we now for sure are outside the mesh
    a = tria_point + n*self.__bounding_box_diag
    b = tria_point - n*self.__bounding_box_diag
    
    # Cut the mesh by the line which connects a to b
    intersection_points = vtk.vtkPoints()
    self.__obb_tree.IntersectWithLine(a, b, intersection_points, None)
    
    if intersection_points.GetNumberOfPoints() < 2:
      print("RandomMeshPointsGenerator.__generate_random_point_in_mesh: line-mesh intersection went wrong. We return a surface point.")
      return tria_point

    # Return a random point between the first two intersection points
    p = intersection_points.GetPoint(0)
    p = np.array([p[0], p[1], p[2]])
    q = intersection_points.GetPoint(1)
    q = np.array([q[0], q[1], q[2]])
    t = random.uniform(0.1, 0.9)
    
    return p + t*(q - p)



