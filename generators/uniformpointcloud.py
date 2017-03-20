import vtk
import numpy as np

class UniformPointCloud:
  def __init__(self, target_point):
    self.__target_point = np.array([target_point[0], target_point[1], target_point[2]])

    self.__points = vtk.vtkPolyData()
    self.__points.SetPoints(vtk.vtkPoints())

    self.__point_locator = vtk.vtkPointLocator()
    self.__point_locator.SetDataSet(self.__points)


  def insert_point(self, point_candidates):
    best_point = point_candidates[0]
    best_fitness = self.__compute_point_fitness(best_point)
    
    for p in point_candidates[1:]:
      fitness = self.__compute_point_fitness(p)
      if fitness > best_fitness:
        best_fitness = fitness
        best_point = p

    self.__points.GetPoints().InsertNextPoint(best_point)
    self.__points.Modified()
    self.__point_locator.Update()

    return best_point


  def __compute_point_fitness(self, p):
    # The first component of the fitness is the negative of the distance to the target point
    dist_to_target = np.linalg.norm(p - self.__target_point)
    
    # Make sure there are points in the point cloud
    if self.__points.GetNumberOfPoints() <= 0:
      return -dist_to_target

    # Find the point closest to 'p'
    ids = vtk.vtkIdList()
    self.__point_locator.FindClosestNPoints(1, p, ids)
    closest_point = self.__points.GetPoint(ids.GetId(0))

    # The second component of the fitness is the distance between 'p' and the closest point
    dist_to_closest_point = np.linalg.norm(p - closest_point)
    
    #return dist_to_closest_point - 1.2*dist_to_target
    #return -dist_to_target
    #return dist_to_closest_point
    return -(abs(dist_to_closest_point - 15) + abs(dist_to_target - 15))
