import vtk
import random
from vis.visneuralconnection import VisNeuralConnection
from bio.neuralconnection import NeuralConnection

class NeuralConnectionGenerator:
  def connect_neurons(self, name, n1, n2):
    r1 = n1.visual_representation.sphere_radius
    r2 = n2.visual_representation.sphere_radius
    cylinder_radius = 0.3*min(r1, r2)

    vis_rep = VisNeuralConnection(name, n1.position, n2.position, cylinder_radius)
    return NeuralConnection(name, n1, n2, random.uniform(-1.0, 1.0), vis_rep)


  def create_neural_connection(self, name, n1, n2, weight, cylinder_radius, color):
    vis_rep = VisNeuralConnection(name, n1.position, n2.position, cylinder_radius)
    return NeuralConnection(name, n1, n2, weight, vis_rep)
