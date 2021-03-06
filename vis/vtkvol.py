import vtk
from .vtkmodel import VtkModel

class VtkVolumeModel(VtkModel):
  """This one is not used right now."""
  def __init__(self, vtk_image_data, name = "VtkVolumeModel"):
    if not isinstance(vtk_image_data, vtk.vtkImageData):
      raise TypeError("input has to be vtkImageData")

    VtkModel.__init__(self, name)

    self.__vtk_image_data = vtk_image_data

    # The slicer for the volume data
    self.__image_slicer = vtk.vtkImagePlaneWidget()
    self.__image_slicer.SetResliceInterpolateToCubic()
    self.__image_slicer.SetInputData(vtk_image_data)
    self.__image_slicer.SetPlaneOrientationToZAxes()


  def add_yourself(self, renderer, interactor):
    self.__image_slicer.SetInteractor(interactor)
    self.__image_slicer.On()
    self.__image_slicer.InteractionOff()


  def remove_yourself(self, renderer, interactor):
    self.__image_slicer.Off()


  def get_number_of_slices(self):
    return 1 + self.__vtk_image_data.GetExtent()[5]


  def get_slice_index(self):
    return self.__image_slicer.GetSliceIndex()


  def set_slice_index(self, index):
    return self.__image_slicer.SetSliceIndex(index)


  def set_visibility(self, bool_value):
    self.actor.SetEnabled(bool_value)


  def visibility_on(self):
    self.__image_slicer.On()


  def visibility_off(self):
    self.__image_slicer.Off()


  def toggle_visibility(self):
    self.__image_slicer.SetEnabled(1 - self.__image_slicer.GetEnabled())


  def is_visible(self):
    return self.__image_slicer.GetEnabled() == 1


  def highlight_on(self):
    pass


  def highlight_off(self):
    pass


  @property
  def vtk_property(self):
    return self.__image_slicer.GetTexturePlaneProperty()
