from anatomy.neurogen import NeuronGenerator
from anatomy.region import BrainRegion

class Controller:
  def __init__(self, data_container):
    self.__data_container = data_container
    self.__neuron_generator = NeuronGenerator()


  def generate_neurons(self, number_of_neurons_per_region, brain_regions):
    neurons = self.__neuron_generator.generate_neurons(number_of_neurons_per_region, brain_regions)
    self.__data_container.add_models(neurons)
