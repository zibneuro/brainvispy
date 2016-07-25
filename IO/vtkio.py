import vtk
import sys
import os
import os.path
from core.progress import ProgressBar
from .obj import OBJReader

class VtkIO:
  def get_reader(self, file_extension):
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


  def load_file(self, file_name):
    '''Loads and returns the provided file. Returns None uppon failure.'''
    # Get the right data reader depending on the file extension
    data_reader = self.get_reader(os.path.splitext(file_name)[1])
    if not data_reader:
      return None

    data_reader.SetFileName(file_name)
    data_reader.Update()
    return data_reader.GetOutput()


  def load_files(self, file_names, progress_bar = None):
    """Returns the loaded data (the ones that could be loaded) in a list of pairs (file name, data)."""
    # Make sure that 'progress_bar' has the right type
    if progress_bar and not isinstance(progress_bar, ProgressBar):
      progress_bar = None
    
    # Inform the user that the loading begins
    if progress_bar:
      progress_bar.init(1, len(file_names), "Loading files: ")

    file_name_data_pairs = list()
    counter = 0

    # Load the files
    for file_name in file_names:
      counter += 1
      # Make sure we have a file
      if os.path.isfile(file_name):
        data = self.load_file(file_name)
        if data:
          file_name_data_pairs.append((file_name, data))

      # Update the progress bar
      if progress_bar:
        progress_bar.set_progress(counter)

    # Done with loading
    if progress_bar:
      progress_bar.done()

    return file_name_data_pairs
