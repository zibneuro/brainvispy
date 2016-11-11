from core.filemodel import FileModel
from vis.vtkpoly import VtkPolyModel

class BrainRegion(VtkPolyModel, FileModel):
  def __init__(self, vtk_poly_data, file_name, name, neurons):
    # Init the base classes
    VtkPolyModel.__init__(self, vtk_poly_data, name)
    FileModel.__init__(self, file_name)
    # Save the neurons
    self.__neurons = neurons
