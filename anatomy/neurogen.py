import vtk
import random
from anatomy.region import BrainRegion

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
      raise TypeError("input argument 'brain_region' has to be a BrainRegion")

    # First, generate the neuron positions in the brain region
    neuron_positions = self.__generate_random_points_inside_mesh(brain_region.vtk_poly_data,
      num_neurons_per_brain_region)

    neurons = list()
    print("generated", len(neuron_positions), "neurons in " + brain_region.name)

    return neurons


  def __generate_random_points_inside_mesh(self, vtk_mesh, num_points):
    if not isinstance(vtk_mesh, vtk.vtkPolyData):
      raise TypeError("input argument 'vtk_mesh' has to be a vtkPolyData")

    # Compute the volume of the brain region
    volume_computer = vtk.vtkMassProperties()
    volume_computer.SetInputData(vtk_mesh)
    volume_computer.Update()
    region_volume = volume_computer.GetVolume()

    # Compute the volume of the bounding box
    vtk_mesh.ComputeBounds()
    b = vtk_mesh.GetBounds()
    bbox_volume = (b[1] - b[0])*(b[3] - b[2])*(b[5] - b[4])

    # Compute the expected number of random samples needed to achive the desired
    # number of neurons (accepted samples)
    overhead = bbox_volume/region_volume
    num_samples = int(overhead*num_points + 1)

    print("Will generate", num_samples, "samples. Overhead of", overhead)

    # This is the point which will be tested whether it is inside or outside the mesh
    vtk_sample = vtk.vtkPoints()
    vtk_sample.SetNumberOfPoints(1)
    vtk_sample_pd = vtk.vtkPolyData()
    vtk_sample_pd.SetPoints(vtk_sample)

    # This guy will do the containment tests
    point_tester = vtk.vtkSelectEnclosedPoints()
    point_tester.SetInputData(vtk_sample_pd)
    point_tester.SetSurfaceData(vtk_mesh)

    num_accepted_samples = 0
    accepted_points = list()

    # Generate the random points
    for i in range(num_samples):
      p = random.uniform(b[0], b[1]), random.uniform(b[2], b[3]), random.uniform(b[4], b[5])
      vtk_sample.SetPoint(0, p)
      vtk_sample_pd.Modified()
      point_tester.Update()
      if point_tester.IsInside(0):
        accepted_points.append(p)
        num_accepted_samples += 1
        if num_accepted_samples >= num_points:
          break

    # Return the result
    return accepted_points
