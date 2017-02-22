from bio.neuron import Neuron
from vis.visneuron import VisNeuron
from core.settings import Settings

class NeuronGenerator:
  def create_neuron(self, name, index, p, threshold):
    vis_neuron = VisNeuron(name, p, Settings.neuron_sphere_radius)
    neuron = Neuron(name, p[0], p[1], p[2], threshold, vis_neuron)
    neuron.set_index(index)
    return neuron
