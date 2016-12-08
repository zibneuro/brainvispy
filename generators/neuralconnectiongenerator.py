import vtk
import random
from vis.visneuralconnection import VisNeuralConnection
from bio.neuralconnection import NeuralConnection

class NeuralConnectionGenerator:
  def create_neural_connection(self, name, neuron_1, neuron_2):
    r1 = neuron_1.visual_representation.sphere_radius
    r2 = neuron_2.visual_representation.sphere_radius
    cylinder_radius = 0.3*min(r1, r2)

    vis_rep = VisNeuralConnection(name, neuron_1.position, neuron_2.position, cylinder_radius)
    return NeuralConnection(name, neuron_1, neuron_2, random.uniform(-1.0, 1.0), vis_rep)
