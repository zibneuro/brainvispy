class Neuron:
  def __init__(self, name, x, y, z, threshold, visual_representation):
    self.__name = name
    self.__index = -1
    self.__pos = (x, y, z)
    self.__threshold = threshold
    self.__vis_rep = visual_representation


  def set_index(self, idx):
    self.__index = idx


  def set_threshold(self, value):
    self.__threshold = value


  @property
  def name(self):
    return self.__name


  @property
  def index(self):
    return self.__index


  @property
  def position(self):
    return self.__pos


  @property
  def threshold(self):
    return self.__threshold


  @property
  def visual_representation(self):
    return self.__vis_rep
