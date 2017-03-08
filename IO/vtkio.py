import vtk
import os
import os.path
from vis.vtkpoly import VtkPolyModel
from vis.vtkvol import VtkVolumeModel
from IO.obj import OBJReader

class VtkIO:
  def __get_reader(self, file_extension):
    '''Returns a reader that can read the file type having the provided extension. Returns None if no such reader.'''
    lower_file_ext = file_extension.lower()
    #if (lower_file_ext == ".tiff" or lower_file_ext == ".tif"):
    #  return vtk.vtkTIFFReader()
    if (lower_file_ext == ".vtk"):
      return vtk.vtkPolyDataReader()
    if (lower_file_ext == ".ply"):
      return vtk.vtkPLYReader()
    if (lower_file_ext == ".obj"):
      return OBJReader()
    return None


  def load(self, file_name):
    """Loads the data from the file 'file_name' and returns it. Returns None if the file type is not supported."""
    # Make sure the file exists
    if not file_name or not os.path.isfile(file_name):
      return None

    # Get the right data reader depending on the file extension
    data_reader = self.__get_reader(os.path.splitext(file_name)[1])
    if not data_reader:
      return None

    data_reader.SetFileName(file_name)
    data_reader.Update()
    return data_reader.GetOutput()
