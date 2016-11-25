class Neuron:
  def __init__(self, name, x, y, z, threshold, vis_rep):
    self.__name = name
    self.__pos = (x, y, z)
    self.__threshold = threshold
    self.__vis_rep = vis_rep
    self.__id = -1


  def set_threshold(self, value):
    self.__threshold = value


  @property
  def name(self):
    return self.__name


  @property
  def position(self):
    return self.__pos


  @property
  def threshold(self):
    return self.__threshold


  @property
  def visual_representation(self):
    return self.__vis_rep
