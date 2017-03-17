import vtk
import math
import random
import numpy as np

class OrientedPoint:
  def __init__(self, p, n):
    self.p = p
    self.n = n


class SymmetricPointsGenerator:
  def __init__(self, vtk_mesh, axis):
    if not isinstance(vtk_mesh, vtk.vtkPolyData):
      # Maybe 'vtk_mesh' has a VtkPolyModel as a visual representation that has a vtkPolyData
      try:
        vtk_mesh = vtk_mesh.visual_representation.vtk_poly_data
      except AttributeError:
        raise

    if not vtk_mesh.GetPolys():
      raise ValueError("input argument 'vtk_mesh' has no triangles")

    self.__vtk_mesh = vtk_mesh

    # Compute the bounding box of the mesh
    vtk_mesh.ComputeBounds()
    self.__bounding_box = b = vtk_mesh.GetBounds()
    self.__bounding_box_diag = math.sqrt((b[1]-b[0])**2 + (b[3]-b[2])**2 + (b[5]-b[4])**2)

    # Populate the lists which contain the oriented mesh surface points
    self.__build_point_lists(axis)

    # This is the guy who does an efficient line-surface intersection
    self.__obb_tree = vtk.vtkOBBTree()
    self.__obb_tree.SetDataSet(vtk_mesh)
    self.__obb_tree.BuildLocator()


  def __build_point_lists(self, axis):
    self.__left_points = list()
    self.__right_points = list()

    self.__vtk_mesh.BuildCells()

    # Compute the middle coordinate
    middle = 0.5*(self.__bounding_box[2*axis] + self.__bounding_box[2*axis + 1])

    vtk_point_ids = vtk.vtkIdList()

    for i in range(self.__vtk_mesh.GetNumberOfCells()):
      self.__vtk_mesh.GetCellPoints(i, vtk_point_ids)
      # Make sure we have a triangle
      if vtk_point_ids.GetNumberOfIds() == 3:
        p = self.__vtk_mesh.GetPoint(vtk_point_ids.GetId(0))
        #p = np.array([p[0], p[1], p[2]])
        self.__left_points.append(i) if p[axis] > middle else self.__right_points.append(i)
      # Prepare for the next iteration
      vtk_point_ids.Reset()

    """
    vtk_points = self.__vtk_mesh.GetPoints()
    vtk_trias = self.__vtk_mesh.GetPolys()
    vtk_trias.InitTraversal()
    vtk_vertex_ids = vtk.vtkIdList()

    while vtk_trias.GetNextCell(vtk_vertex_ids):
      # Make sure we get a triangle
      if vtk_vertex_ids.GetNumberOfIds() == 3:
        # Get the three triangle vertices
        a = vtk_points.GetPoint(vtk_vertex_ids.GetId(0))
        a = np.array([a[0], a[1], a[2]]) # numpy array      
        b = vtk_points.GetPoint(vtk_vertex_ids.GetId(1))
        b = np.array([b[0], b[1], b[2]]) # numpy array
        c = vtk_points.GetPoint(vtk_vertex_ids.GetId(2))
        c = np.array([c[0], c[1], c[2]]) # numpy array
        p = (a + b + c)/3
        n = self.__compute_triangle_normal(a, b, c)
        if p[axis] > middle:
          self.__left_points.append(OrientedPoint(p, n))
        else:
          self.__right_points.append(OrientedPoint(p, n))
      # Prepare for the next iteration
      vtk_vertex_ids.Reset()
    """


  def generate_point_inside_mesh(self, side = None):
    # Does the user provide a side
    if side:
      # Which side?
      if side == 0 or side[0].lower() == "l":
        surface_points = self.__left_points
      else:
        surface_points = self.__right_points
    else:
      # Chose the side probabilistically
      probability_left = len(self.__left_points) / (len(self.__left_points) + len(self.__right_points))
      if random.random() < probability_left:
        surface_points = self.__left_points
      else:
        surface_points = self.__right_points

    # Randomly select a cell
    random_id = surface_points[random.randint(0, len(surface_points) - 1)]
    vtk_point_ids = vtk.vtkIdList()
    self.__vtk_mesh.GetCellPoints(random_id, vtk_point_ids)
    # Compute a point on the triangle and its normal
    p, n = self.__compute_triangle_point_and_normal(vtk_point_ids)
    
    # Using the selected surface point, generate a point inside the mesh
    return self.__generate_random_point_in_mesh(p, n)


  def __compute_triangle_point_and_normal(self, point_ids):
    a = self.__vtk_mesh.GetPoint(point_ids.GetId(0))
    a = np.array([a[0], a[1], a[2]]) # numpy array      
    b = self.__vtk_mesh.GetPoint(point_ids.GetId(1))
    b = np.array([b[0], b[1], b[2]]) # numpy array
    c = self.__vtk_mesh.GetPoint(point_ids.GetId(2))
    c = np.array([c[0], c[1], c[2]]) # numpy array
    return (a + b + c)/3, self.__compute_triangle_normal(a, b, c)


  def __compute_triangle_normal(self, x, y, z):
    n = np.cross(y - x, z - x)
    return n / np.linalg.norm(n)


  def __generate_random_point_in_mesh(self, surface_point, normal):
    # Generate two points, a and b, for which we now for sure are outside the mesh
    #a = surface_point + normal*self.__bounding_box_diag
    #b = surface_point - normal*self.__bounding_box_diag
 
    # This is another possibility to generate a point inside the mesh
    a = np.array([surface_point[0], surface_point[1], self.__bounding_box[4] - 1])
    b = np.array([surface_point[0], surface_point[1], self.__bounding_box[5] + 1])

    # Cut the mesh by the line which connects a to b
    intersection_points = vtk.vtkPoints()
    self.__obb_tree.IntersectWithLine(a, b, intersection_points, None)
    
    if intersection_points.GetNumberOfPoints() < 2:
      print("RandomMeshPointsGenerator.__generate_random_point_in_mesh: line-mesh intersection went wrong. We return a surface point.")
      return surface_point

    # Return a random point between the first two intersection points
    p = intersection_points.GetPoint(0)
    p = np.array([p[0], p[1], p[2]])
    q = intersection_points.GetPoint(1)
    q = np.array([q[0], q[1], q[2]])
    t = random.uniform(0.4, 0.6)
    
    return p + t*(q - p)
