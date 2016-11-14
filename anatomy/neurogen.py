import vtk
from anatomy.region import BrainRegion

class NeuronGenerator:
  def generate_neurons(self, brain_regions):
    neurons = list()
    for brain_region in brain_regions:
      if isinstance(brain_region, BrainRegion):
        self.__generate_neurons_in_brain_region(brain_region, neurons)
    # Return the generated neurons
    return neurons


  def __generate_neurons_in_brain_region(self, brain_region, neurons):
    vtk_poly_data = brain_region.vtk_poly_data
    connectivity_filer = vtk.vtkPolyDataConnectivityFilter()
    connectivity_filer.SetInputData(vtk_poly_data)
    connectivity_filer.SetExtractionModeToAllRegions()
    connectivity_filer.Update()
    num_regions = connectivity_filer.GetNumberOfExtractedRegions()
    
    for i in range(num_regions):
      cf = vtk.vtkPolyDataConnectivityFilter()
      cf.SetInputData(connectivity_filer.GetOutput())
      cf.SetExtractionModeToAllRegions()
      cf.AddSpecifiedRegion(i)
      cf.Update()
      print("region " + str(i) + " has " + str(cf.GetOutput().GetNumberOfPoints()) + " points")

    #print("got " + str(num_regions) + " region(s)")
