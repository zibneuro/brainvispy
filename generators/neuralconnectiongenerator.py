from vis.visneuralconnection import VisNeuralConnection
from bio.neuralconnection import NeuralConnection

class NeuralConnectionGenerator:
  def create_neural_connection(self, name, src_neuron_name, tar_neuron_name, src_pos, tar_pos, weight):
    vis_rep = VisNeuralConnection(name, src_pos, tar_pos, src_neuron_name == tar_neuron_name)
    return NeuralConnection(name, src_neuron_name, tar_neuron_name, weight, vis_rep)
