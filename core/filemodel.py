class FileModel:
  """This class is supposed to represent a model (e.g., a mesh) which has a file name."""
  def __init__(self, file_name):
    self.__file_name = file_name


  def set_file_name(self, file_name):
    self.__file_name = file_name


  @property
  def file_name(self):
    return self.__file_name
