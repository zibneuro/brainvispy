import vtk
import random
from .randompoints import RandomPointsGenerator
from vis.visneuron import VisNeuron
from bio.brainregion import BrainRegion
from bio.neuron import Neuron

class NeuronGenerator:
  def generate_random_neurons(self, num_neurons_per_brain_region, brain_regions, threshold_potential_range):
    # Make sure the range is legal
    thresh_min = threshold_potential_range[0]
    thresh_max = threshold_potential_range[1]
    if thresh_min > thresh_max:
      thresh_min = threshold_potential_range[1]
      thresh_max = threshold_potential_range[0]

    # We will save the neurons in this list
    neurons = list()

    # Generate neurons in each brain region
    for brain_region in brain_regions:
      new_neurons = self.__generate_random_neurons_in_brain_region(num_neurons_per_brain_region, brain_region, thresh_min, thresh_max)
      neurons.extend(new_neurons)

    # Return the generated neurons
    return neurons


  def create_neuron(self, name, index, p, threshold, sphere_radius):
    # Create and return the neuron
    neuron = Neuron(name, p[0], p[1], p[2], threshold, VisNeuron(name, p, sphere_radius))
    neuron.set_index(index)
    return neuron


  def __generate_random_neurons_in_brain_region(self, num_neurons_per_brain_region, brain_region, thresh_min, thresh_max):
    if not isinstance(brain_region, BrainRegion):
      return list()

    # Compute the bounding box of the brain region, in order to compute the radius of the sphere which represents the neurons
    vtk_poly_data = brain_region.visual_representation.vtk_poly_data
    vtk_poly_data.ComputeBounds()
    b = vtk_poly_data.GetBounds()
    sphere_radius = 0.02*min(b[1]-b[0], b[3]-b[2], b[5]-b[4])

    # Generate the neuron positions in the brain region
    rand_points_gen = RandomPointsGenerator(vtk_poly_data)
    neuron_positions = rand_points_gen.generate_points_inside_mesh(num_neurons_per_brain_region)

    neurons = list()

    # Now, generate the neurons
    for p in neuron_positions:
      # Generate the neuron potential threshold
      potential_threshold = random.uniform(thresh_min, thresh_max)
      # Generate and save the neuron
      neurons.append(self.create_neuron("neuron", -1, p, potential_threshold, sphere_radius))

    print("generated", len(neuron_positions), "neurons in '" + brain_region.name + "'")
    return neurons
