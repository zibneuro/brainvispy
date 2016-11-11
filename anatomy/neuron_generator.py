class NeuronGenerator:
  def generate_neurons(self, brain_regions):
    neurons = list()
    for brain_region in brain_regions:
      self.__generate_neurons_in_brain_region(brain_region)


  def __generate_neurons_in_brain_region(self, brain_region):
    pass
