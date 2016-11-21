import vtk
import random
from vis.rndpointgen import RandomMeshPointsGenerator
from anatomy.region import BrainRegion
from anatomy.neuron import Neuron

class NeuronGenerator:
  def generate_neurons(self, num_neurons_per_brain_region, brain_regions):
    neurons = list()
    for brain_region in brain_regions:
      new_neurons = self.__generate_neurons_in_brain_region(num_neurons_per_brain_region, brain_region)
      neurons.extend(new_neurons)
    # Return the generated neurons
    return neurons


  def __generate_neurons_in_brain_region(self, num_neurons_per_brain_region, brain_region):
    if not isinstance(brain_region, BrainRegion):
      return list()

    # First, generate the neuron positions in the brain region
    rand_points_gen = RandomMeshPointsGenerator(brain_region.vtk_poly_data)
    neuron_positions = rand_points_gen.generate_points_inside_mesh(num_neurons_per_brain_region)

    neurons = list()

    # Now, generate the geometric neuron representations
    for p in neuron_positions:
      # Create a VTK mesh to visually represent the neuron
      vtk_neuron_representation = self.__create_spherical_neuron_representation(p)
      neurons.append(Neuron(p[0], p[1], p[2], vtk_neuron_representation, -1, 0.5))

    print("generated", len(neuron_positions), "neurons in " + brain_region.name)
    return neurons


  def __create_spherical_neuron_representation(self, position):
    vtk_sphere_source = vtk.vtkSphereSource()
    vtk_sphere_source.SetThetaResolution(12)
    vtk_sphere_source.SetPhiResolution(12)
    vtk_sphere_source.SetRadius(2.0)
    vtk_sphere_source.SetCenter(position[0], position[1], position[2])
    vtk_sphere_source.Update()
    return vtk_sphere_source.GetOutput()
