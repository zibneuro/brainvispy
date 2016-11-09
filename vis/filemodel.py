class FileModel:
  def __init__(self, file_name):
    self.__file_name = file_name


  def set_file_name(self, file_name):
    self.__file_name = file_name


  @property
  def file_name(self):
    return self.__file_name
