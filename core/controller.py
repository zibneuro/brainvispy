from bio.neuron import Neuron
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


  def on_mouse_over_model(self, model, viewer):
    if not isinstance(model, Neuron):
      return
    self.__indicate_possible_neural_connection(model, viewer.get_selected_models(), viewer)


  def __indicate_possible_neural_connection(self, neuron, models, viewer):
    # Check if we have exactly one model in the selection
    if len(models) != 1:
      return

    # Is the selected model a neuron
    n2 = models[0]
    if not isinstance(n2, Neuron):
      return

    # Make sure we do not have the same neuron twice
    if neuron == n2:
      return

    viewer.connect_points(neuron.position, n2.position)
