from vis.vtkpoly import VtkPolyModel

class Neuron(VtkPolyModel):
  def __init__(self, x, y, z, threshold):
    self.__coords = (x, y, z)
    self.__threshold = threshold


  @property
  def coordinates(self):
    return self.__coords


  @property
  def threshold(self):
    return self.__threshold
