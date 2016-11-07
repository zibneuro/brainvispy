class AnatomicRegion:
  def __init__(self, vtk_poly_data, file_name, name, neurons):
    super().__init__(vtk_poly_data, file_name, name)
    self.__file_name = file_name
    self.__poly_model = poly_model
    self.__neurons = neurons
