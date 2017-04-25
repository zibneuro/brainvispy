import vtk
import math
import random
import numpy as np
from generators.uniformpointcloud import UniformPointCloud

class OrientedPoint:
  def __init__(self, p, n):
    self.p = p
    self.n = n


class SymmetricPointsGenerator:
  def __init__(self, vtk_mesh, axis):
    if not isinstance(vtk_mesh, vtk.vtkPolyData):
      try:
        vtk_mesh = vtk_mesh.visual_representation.vtk_poly_data
      except AttributeError:
        raise

    if not vtk_mesh.GetPoints() or not vtk_mesh.GetPolys():
      raise ValueError("input argument 'vtk_mesh' has no points and/or triangles")

    self.__vtk_mesh = vtk_mesh

    # Compute the bounding box of the mesh
    vtk_mesh.ComputeBounds()
    self.__bounding_box = b = vtk_mesh.GetBounds()
    self.__bounding_box_diag = math.sqrt((b[1]-b[0])**2 + (b[3]-b[2])**2 + (b[5]-b[4])**2)

    # Populate the lists which contain the point ids
    self.__build_point_id_lists(axis)

    self.__left_point_cloud = UniformPointCloud(self.__left_target)
    self.__right_point_cloud = UniformPointCloud(self.__right_target)
    self.__central_point_cloud = UniformPointCloud(self.__central_target)

    # This is the guy who does an efficient line-surface intersection
    self.__obb_tree = vtk.vtkOBBTree()
    self.__obb_tree.SetDataSet(vtk_mesh)
    self.__obb_tree.BuildLocator()


  def __build_point_id_lists(self, axis):
    self.__left_point_ids = list()
    self.__left_target = np.array([0.0, 0.0, 0.0])
    self.__right_point_ids = list()
    self.__right_target = np.array([0.0, 0.0, 0.0])
    self.__all_point_ids = list()
    self.__central_target = np.array([0.0, 0.0, 0.0])
    middle = 0.5*(self.__bounding_box[2*axis] + self.__bounding_box[2*axis + 1])

    for i in range(self.__vtk_mesh.GetNumberOfPoints()):
      p = self.__vtk_mesh.GetPoint(i)
      self.__central_target += p
      self.__all_point_ids.append(i)
      if p[axis] > middle:
        self.__left_point_ids.append(i)
        self.__left_target += p
      else:
        self.__right_point_ids.append(i)
        self.__right_target += p

    if self.__left_point_ids: self.__left_target /= len(self.__left_point_ids)
    if self.__right_point_ids: self.__right_target /= len(self.__right_point_ids)
    self.__central_target /= self.__vtk_mesh.GetNumberOfPoints()


  def generate_point_inside_mesh(self, side):
    if side:
      side = side[0].lower()

    # Which side?
    if side == "l": # 'l' for left
      surface_point_ids = self.__left_point_ids
      target_point = self.__left_target
      point_cloud = self.__left_point_cloud
    elif side == "r": # 'r' for right
      surface_point_ids = self.__right_point_ids
      target_point = self.__right_target
      point_cloud = self.__right_point_cloud
    else: # make it central
      surface_point_ids = self.__all_point_ids
      target_point = self.__central_target
      point_cloud = self.__central_point_cloud

    candidate_points = list()

    # Generate some candidate points from which we will select (the best) one
    for i in range(100):
      random_id = surface_point_ids[random.randint(0, len(surface_point_ids) - 1)]
      p = self.__vtk_mesh.GetPoint(random_id)
      p = np.array([p[0], p[1], p[2]])
      candidate_points.append(self.__generate_random_point_in_mesh(p))

    return point_cloud.insert_point(candidate_points)


  def generate_mirrored_points_inside_mesh(self):
    candidate_points = list()
    # Generate some candidate points from which we will select (the best) one
    for i in range(100):
      random_id = self.__all_point_ids[random.randint(0, len(self.__all_point_ids) - 1)]
      p = self.__vtk_mesh.GetPoint(random_id)
      p = np.array([p[0], p[1], p[2]])
      candidate_points.append(self.__generate_random_point_in_mesh(p))

    p1 = self.__left_point_cloud.insert_point(candidate_points)
    p2 = self.__right_point_cloud.insert_point(candidate_points)
    return (p1, p2)

    # Compute the probability to select the left side
    #p_L = len(self.__left_point_ids) / (len(self.__left_point_ids) + len(self.__right_point_ids))
    # Randomly select a side
    #if random.random() < p_L:
      #surface_point_ids = self.__left_point_ids
      #target_point = self.__left_target
      #point_cloud = self.__left_point_cloud
    #else:
      #surface_point_ids = self.__right_point_ids
      #target_point = self.__right_target
      #point_cloud = self.__right_point_cloud


  def __generate_random_point_in_mesh(self, surface_point):
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
    return p + random.uniform(0.4, 0.6)*(q - p)
