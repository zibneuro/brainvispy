class BrainRegion:
  def __init__(self, name, visual_representation):
    self.__name = name
    self.__vis_rep = visual_representation


  @property
  def name(self):
    return self.__name


  @property
  def visual_representation(self):
    return self.__vis_rep
