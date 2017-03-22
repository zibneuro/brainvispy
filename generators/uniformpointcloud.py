import vtk
import numpy as np
from core.settings import Settings

class UPoint:
  def __init__(self, p, dist_to_closest_point):
    self.p = p
    self.dist_to_closest_point = dist_to_closest_point
    
  def compute_energy(self):
    diff = self.dist_to_closest_point - Settings.inter_neuron_distance
    if diff >= 0:
      return diff
    return -5*diff


class UniformPointCloud:
  def __init__(self, target_point):
    self.__target_point = np.array([target_point[0], target_point[1], target_point[2]])

    self.__points = vtk.vtkPolyData()
    self.__points.SetPoints(vtk.vtkPoints())

    self.__point_locator = vtk.vtkPointLocator()
    self.__point_locator.SetDataSet(self.__points)


  def insert_point(self, point_candidates):
    if self.__points.GetNumberOfPoints() <= 0:
      point = self.__select_point_closest_to_target(point_candidates)
    else:
      point = self.__select_best_point(point_candidates)
      
    self.__points.GetPoints().InsertNextPoint(point)
    self.__points.Modified()
    self.__point_locator.Update()

    return point


  def __select_point_closest_to_target(self, points):
    closest_point = points[0]
    min_dist = self.__compute_distance_to_target(closest_point)

    for p in points[1:]:
      dist = self.__compute_distance_to_target(p)
      if dist < min_dist:
        min_dist = dist
        closest_point = p

    return closest_point


  def __select_best_point(self, points):
    evaluated_points = list()
    for p in points:
      evaluated_points.append(UPoint(p, self.__compute_distance_to_closest_point(p)))

    evaluated_points.sort(key = lambda point: point.compute_energy())
    
    min_dist_to_target = self.__compute_distance_to_target(evaluated_points[0].p)
    best_point = evaluated_points[0].p

    list_end = max(len(evaluated_points)//10, 1)

    for evaluated_point in evaluated_points[1:list_end]:
      dist_to_target = self.__compute_distance_to_target(evaluated_point.p)
      if dist_to_target < min_dist_to_target:
        min_dist_to_target = dist_to_target
        best_point = evaluated_point.p

    return best_point


  def __compute_distance_to_target(self, p):
    return np.linalg.norm(p - self.__target_point)


  def __compute_distance_to_closest_point(self, p):
    # Make sure there are points in the point cloud
    if self.__points.GetNumberOfPoints() <= 0:
      return float("inf")

    # Find the point closest to 'p'
    ids = vtk.vtkIdList()
    self.__point_locator.FindClosestNPoints(1, p, ids)
    closest_point = self.__points.GetPoint(ids.GetId(0))

    # Return the distance between 'p' and the closest point
    return np.linalg.norm(p - closest_point)
