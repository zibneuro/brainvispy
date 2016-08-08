import vtk
import os
import os.path
from vis.vtkpoly import VtkPolyModel
from vis.vtkvol import VtkVolumeModel
from .obj import OBJReader

class VtkIO:
  def __get_reader(self, file_extension):
    '''Returns a reader that can read the file type having the provided extension. Returns None if no such reader.'''
    lower_file_ext = file_extension.lower()
    if (lower_file_ext == ".tiff" or lower_file_ext == ".tif"):
      return vtk.vtkTIFFReader()
    if (lower_file_ext == ".vtk"):
      return vtk.vtkPolyDataReader()
    if (lower_file_ext == ".ply"):
      return vtk.vtkPLYReader()
    if (lower_file_ext == ".obj"):
      return OBJReader()
    return None


  def load(self, file_name):
    """Loads the data from the file 'file_name' and returns either VtkVolumeModel, VtkPolyModel or None. It
    returns an error message (string) as a second argument (empty string if no error)."""
    # Make sure the file exists
    if not os.path.isfile(file_name):
      return None, "cannot open '" + file_name + "'"
    
    vtk_data = self.__load_data_from_file(file_name)

    # Make sure we got data we can handle
    if isinstance(vtk_data, vtk.vtkImageData):
      return VtkVolumeModel(vtk_data, file_name), "" # return the model and an empty error message
    elif isinstance(vtk_data, vtk.vtkPolyData):
      return VtkPolyModel(vtk_data, file_name), "" # return the model and an empty error message

    # We can not deal with the provided file
    return None, "we have no reader for this file type"


  def __load_data_from_file(self, file_name):
    # Get the right data reader depending on the file extension
    data_reader = self.__get_reader(os.path.splitext(file_name)[1])
    if not data_reader:
      return None

    data_reader.SetFileName(file_name)
    data_reader.Update()
    return data_reader.GetOutput()
