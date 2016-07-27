import abc

class VtkModel(metaclass = abc.ABCMeta):
  def __init__(self, file_name, name):
    self._file_name = file_name
    self._name = name

  @property
  def file_name(self):
    return self._file_name

  @property
  def name(self):
    return self._name

  @abc.abstractmethod
  def add_yourself(self, renderer, interactor):
    pass

  @abc.abstractmethod
  def visibility_on(self):
    pass

  @abc.abstractmethod
  def visibility_off(self):
    pass

  @abc.abstractmethod
  def toggle_visibility(self):
    pass


  @abc.abstractmethod
  def highlight_on(self):
    pass

  @abc.abstractmethod
  def highlight_off(self):
    pass

  @property
  @abc.abstractmethod
  def vtk_property(self):
    pass
