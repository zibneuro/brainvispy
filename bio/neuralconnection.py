class NeuralConnection:
  def __init__(self, name, neuron1, neuron2, weight, visual_representation):
    self.__name = name
    self.__neuron1 = neuron1
    self.__neuron2 = neuron2
    self.__weight = weight
    self.__vis_rep = visual_representation


  def set_weight(self, weight):
    self.__weight = weight
    try:
      self.__vis_rep.on_weight_changed(self)
    except AttributeError:
      pass


  @property
  def name(self):
    return self.__name


  @property
  def weight(self):
    return self.__weight


  @property
  def visual_representation(self):
    return self.__vis_rep
