from vis.vtkpoly import VtkPolyModel
from core.filemodel import FileModel

class VisBrainRegion(VtkPolyModel, FileModel):
  def __init__(self, name, vtk_poly_data, file_name):
    # Init the base classes
    VtkPolyModel.__init__(self, vtk_poly_data, name)
    FileModel.__init__(self, file_name)
