import abc

class VtkModel(metaclass = abc.ABCMeta):
  def __init__(self, name):
    self.__name = name

  def set_name(self, name):
    self.__name = name

  @property
  def name(self):
    return self.__name

  @abc.abstractmethod
  def add_yourself(self, renderer, interactor):
    pass

  @abc.abstractmethod
  def remove_yourself(self, renderer, interactor):
    pass

  @abc.abstractmethod
  def is_visible(self):
    pass

  @abc.abstractmethod
  def set_visibility(self, bool_value):
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
