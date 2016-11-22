import vtk
from vis.vtkpoly import VtkPolyModel

class Neuron(VtkPolyModel):
  def __init__(self, x, y, z, vtk_poly_data_representation, threshold):
    VtkPolyModel.__init__(self, vtk_poly_data_representation, r"Neuron @ " + str(threshold))
    self.__coords = (x, y, z)
    self.__threshold = threshold
    self.__id = -1


  @property
  def coordinates(self):
    return self.__coords


  @property
  def threshold(self):
    return self.__threshold
