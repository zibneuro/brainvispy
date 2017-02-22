class NeuralConnection:
  def __init__(self, name, src_neuron_name, tar_neuron_name, weight, visual_representation):
    self.__name = name
    self.__src_neuron_name = src_neuron_name
    self.__tar_neuron_name = tar_neuron_name
    self.__weight = weight
    self.__vis_rep = visual_representation
    # This is just to update the visual representation
    self.set_weight(weight)


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
  def src_neuron_name(self):
    return self.__src_neuron_name


  @property
  def tar_neuron_name(self):
    return self.__tar_neuron_name


  @property
  def weight(self):
    return self.__weight


  @property
  def visual_representation(self):
    return self.__vis_rep
