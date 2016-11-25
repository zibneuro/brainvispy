from vis.vtkpoly import VtkPolyModel
from core.filemodel import FileModel

class VisBrainRegion(VtkPolyModel, FileModel):
  def __init__(self, brain_region, vtk_poly_data, file_name):
    # Init the base classes
    VtkPolyModel.__init__(self, vtk_poly_data, brain_region.name)
    FileModel.__init__(self, file_name)
    # Save the neurons
    self.__brain_region = brain_region


  @property
  def brain_region(self):
    return self.__brain_region
