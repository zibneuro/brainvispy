import vtk
import random
from vis.rndpointgen import RandomMeshPointsGenerator
from anatomy.region import BrainRegion
from anatomy.neuron import Neuron

class NeuronGenerator:
  def generate_neurons(self, num_neurons_per_brain_region, brain_regions, threshold_potential_range):
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
      new_neurons = self.__generate_neurons_in_brain_region(num_neurons_per_brain_region, brain_region, thresh_min, thresh_max)
      neurons.extend(new_neurons)

    # Return the generated neurons
    return neurons


  def __generate_neurons_in_brain_region(self, num_neurons_per_brain_region, brain_region, thresh_min, thresh_max):
    if not isinstance(brain_region, BrainRegion):
      return list()

    # Compute the bounding box of the brain region, in order to compute the radius of the sphere which represents the neurons
    vtk_poly_data = brain_region.vtk_poly_data
    vtk_poly_data.ComputeBounds()
    b = vtk_poly_data.GetBounds()
    sphere_radius = 0.02*min(b[1]-b[0], b[3]-b[2], b[5]-b[4])

    # Generate the neuron positions in the brain region
    rand_points_gen = RandomMeshPointsGenerator(brain_region.vtk_poly_data)
    neuron_positions = rand_points_gen.generate_points_inside_mesh(num_neurons_per_brain_region)

    neurons = list()

    # Now, generate the neurons
    for p in neuron_positions:
      # Create a VTK mesh to visually represent the neuron
      vtk_neuron_representation = self.__create_spherical_neuron_representation(p, sphere_radius)
      # Generate the neuron potential threshold
      potential_threshold = random.uniform(thresh_min, thresh_max)
      # Finally, generate the neuron
      neurons.append(Neuron(p[0], p[1], p[2], vtk_neuron_representation, potential_threshold))

    print("generated", len(neuron_positions), "neurons in '" + brain_region.name + "'")
    return neurons


  def __create_spherical_neuron_representation(self, position, sphere_radius):
    vtk_sphere_source = vtk.vtkSphereSource()
    vtk_sphere_source.SetThetaResolution(12)
    vtk_sphere_source.SetPhiResolution(12)
    vtk_sphere_source.SetRadius(sphere_radius)
    vtk_sphere_source.SetCenter(position[0], position[1], position[2])
    vtk_sphere_source.Update()
    return vtk_sphere_source.GetOutput()
