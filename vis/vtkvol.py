import vtk
from .vtkmodel import VtkModel

class VtkVolumeModel(VtkModel):
  def __init__(self, file_name, name, image_data):
    if not isinstance(image_data, vtk.vtkImageData):
      raise TypeError("input has to be vtkImageData")

    super().__init__(file_name, name)

    # The slicer for the volume data
    self.__image_slicer = vtk.vtkImagePlaneWidget()
    self.__image_slicer.SetResliceInterpolateToCubic()
    self.__image_slicer.SetInputData(image_data)
    self.__image_slicer.SetPlaneOrientationToZAxes()


  def add_yourself(self, renderer, interactor):
    self.__image_slicer.SetInteractor(interactor)
    self.__image_slicer.On()
    self.__image_slicer.InteractionOff()


  def visibility_on(self):
    self.__image_slicer.On()


  def visibility_off(self):
    self.__image_slicer.Off()


  def toggle_visibility(self):
    self.__image_slicer.SetEnabled(1 - self.__image_slicer.GetEnabled())


  def highlight_on(self):
    pass


  def highlight_off(self):
    pass


  @property
  def prop_3d(self):
    return self.__image_slicer.GetProp3D()
