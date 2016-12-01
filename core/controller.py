from generators.neurongenerator import NeuronGenerator

class Controller:
  def __init__(self, data_container):
    self.__data_container = data_container
    self.__neuron_generator = NeuronGenerator()


  def generate_neurons(self, number_of_neurons_per_region, brain_regions, threshold_potential_range):
    neurons = self.__neuron_generator.generate_random_neurons(number_of_neurons_per_region, brain_regions, threshold_potential_range)
    self.__data_container.add_neurons(neurons)


  def define_connectivity(self):
    pass#square_weight_matrix = SquareNumericTable()
