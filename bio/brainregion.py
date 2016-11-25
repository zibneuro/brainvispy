class BrainRegion:
  def __init__(self, name, neurons, visual_representation):
    self.__name = name
    self.__neurons = neurons
    self.__vis_rep = visual_representation


  @property
  def name(self):
    return self.__name


  @property
  def neurons(self):
    return self.__neurons


  @property
  def visual_representation(self):
    return self.__vis_rep
