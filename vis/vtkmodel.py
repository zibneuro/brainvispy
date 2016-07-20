import abc

class VtkModel(metaclass = abc.ABCMeta):
  def __init__(self, file_name, name):
    self._file_name = file_name
    self._name = name

  def visibility_on(self):
    self.prop_3d.VisibilityOn()

  def visibility_off(self):
    self.prop_3d.VisibilityOff()

  def toggle_visibility(self):
    self.prop_3d.SetVisibility(1 - self.prop_3d.GetVisibility())

  @property
  def file_name(self):
    return self._file_name

  @property
  def name(self):
    return self._name

  @property
  @abc.abstractmethod
  def prop_3d(self):
    pass

  @abc.abstractmethod
  def highlight_on(self):
    pass

  @abc.abstractmethod
  def highlight_off(self):
    pass
