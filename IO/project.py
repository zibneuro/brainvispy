import os
import xml.etree.ElementTree as ET
from core.progress import ProgressBar
from core.datacontainer import DataContainer
from vis.vtkpoly import VtkPolyModel
from vis.vtkvol import VtkVolumeModel
from gui.vtkwidget import VtkWidget
from .obj import OBJReader
from .vtkio import VtkIO

class ModelElements:
  def __init__(self):
    self.name = None
    self.file_name = None
    self.visibility = None
    self.rgb_color = None
    self.transparency = None
    self.slice_index = None

  def print(self):
    print("model:")
    print("  name:         " + self.name)
    print("  file_name:    " + self.file_name)
    print("  visibility:  ", self.visibility)
    print("  rgb color:   ", self.rgb_color)
    print("  transparency:", self.transparency)
    print("  slice index: ", self.slice_index)


class ProjectIO:
  def __init__(self, progress_bar):
    if not isinstance(progress_bar, ProgressBar):
      raise TypeError("the progress bar has to be of type ProgressBar")
    self.__progress_bar = progress_bar
    self.__project_file_name = None


  def set_file_name(self, file_name):
    self.__project_file_name = file_name


  def has_file_name(self):
    return self.__project_file_name != None


  def get_file_name(self):
    return self.__project_file_name


  def load_files(self, file_names, data_container):
    model_data = list()
    # Create a ModelElements object for each file
    for file_name in file_names:
      model = ModelElements()
      model.name = os.path.split(file_name)[1]
      model.file_name = file_name
      model.visibility = 1
      model.rgb_color = VtkPolyModel.generate_random_rgb_color()
      model.transparency = 0
      model.slice_index = 0
      model_data.append(model)
    # Call the method which now does the loading using the data generated above
    self.__load_models(model_data, data_container)


  def open_project(self, project_file_name, data_container, vtk_widget):
    if not isinstance(data_container, DataContainer):
      raise TypeError("input has to be of type DataContainer")
    # This is the new project file name
    self.__project_file_name = project_file_name

    # Remove everything from the data container
    data_container.clear()

    # Parse the XML file, i.e., read all the elements (name, file name, color, ...) of the models saved in
    # the XML project file
    try:
      model_data = self.__parse_xml_project_file(project_file_name)
    except Exception as error:
      error_msg = list()
      error_msg.append(str(error))
      return error_msg

    # Now, do the real data loading (i.e., load the mesh/volume data), create the models and add them to the
    # container. Return a list of errors if any (e.g., which files cound not be loaded, etc..)
    return self.__load_models(model_data, data_container)


  def __parse_xml_project_file(self, project_file_name):
    # Parse the XML file
    project = ET.parse(project_file_name).getroot()

    # This list stores all the info per model
    models = list()

    # Load the attributes of each model
    for model in project:
      # Make sure we really have a model
      if model.tag != "model":
        continue

      # Create a new object to store the elements of the current model
      model_elements = ModelElements()

      # Read all the elements of 'model'
      for element in model:
        if   element.tag == "name": model_elements.name = element.text
        elif element.tag == "file_name": model_elements.file_name = element.text
        elif element.tag == "properties":
          for prop in element:
            if   prop.tag == "visibility": model_elements.visibility = float(prop.text)
            elif prop.tag == "transparency": model_elements.transparency = float(prop.text)
            elif prop.tag == "slice_index": model_elements.slice_index = float(prop.text)
            elif prop.tag == "rgb_color":
              color_string = prop.text.split(" ")
              model_elements.rgb_color = (float(color_string[0]), float(color_string[1]), float(color_string[2]))
      # Save all the elements for that model
      models.append(model_elements)
    # We are done with the XML file, return the loaded model data
    return models


  def __load_models(self, model_data, data_container):
    """Using the model data from the list 'model_data' this method loads the mesh/volume data from disk,
    creates the models and adds them to the 'data_container'. Returns a list of errors if any (e.g., file
    cound not be loaded etc...)"""
    vtk_io = VtkIO()
    models = list()

    # Let the user know we are doing something    
    self.__progress_bar.init(1, len(model_data), "Loading files: ")
    counter = 0
    
    # Load the data from disk and initialize the model attributes
    for attributes in model_data:
      # Do the heavy job: load the file from disk
      model = vtk_io.load(attributes.file_name)
      if model:
        self.__initialize_model(model, attributes)
        models.append(model)
      # Update the progress bar
      counter += 1
      self.__progress_bar.set_progress(counter)

    # We are done here
    self.__progress_bar.done()
    # Now let the container adopt the new models
    data_container.add_models(models)


  def __initialize_model(self, model, attributes):
    model.set_name(attributes.name)
    if attributes.visibility: model.visibility_on()
    else: model.visibility_off()

    if isinstance(model, VtkVolumeModel):
      model.set_slice_index(attributes.slice_index)
    elif isinstance(model, VtkPolyModel):
      model.set_transparency(attributes.transparency)
      model.set_color(attributes.rgb_color[0], attributes.rgb_color[1], attributes.rgb_color[2])


  def save_project(self, data_container, vtk_widget):
    '''Saves all models in the 'data_container' in an XML file whose name you have to set with set_file_name().'''
    if not isinstance(data_container, DataContainer):
      raise TypeError("the input data container has to be of type DataContainer")

    if not isinstance(vtk_widget, VtkWidget):
      raise TypeError("the input vtk widget has to be of type VtkWidget")

    if not self.has_file_name():
      raise Exception("Error in " + self.__class__.__name__ + ": file name not set")

    # First, create an XML object for the whole project
    xml_project = ET.Element("BrainVisPy_Project")

    # Save some camera parameters
    xml_camera_parameters = ET.SubElement(xml_project, "camera_parameters")
    ET.SubElement(xml_camera_parameters, "position").text = "pos"
    ET.SubElement(xml_camera_parameters, "look_at").text = "look_at"
    ET.SubElement(xml_camera_parameters, "view_up").text = "view_up"

    # Loop over all models in the data container
    for model in data_container.get_models():
      xml_model = ET.SubElement(xml_project, "model")
      ET.SubElement(xml_model, "name").text = model.name
      ET.SubElement(xml_model, "file_name").text = model.file_name
      self.__add_model_properties_to_xml_element(model, ET.SubElement(xml_model, "properties"))

    # Write the whole XML tree to file
    ET.ElementTree(xml_project).write(self.__project_file_name)


  def __add_model_properties_to_xml_element(self, model, xml_element):
    """This method adds the volume or poly properties (depending of what kind of 'model' we have) to the
    provided xml element."""
    if isinstance(model, VtkPolyModel):
      self.__add_poly_properties_to_xml_element(model, xml_element)
    elif isinstance(model, VtkVolumeModel):
      self.__add_volume_properties_to_xml_element(model, xml_element)


  def __add_poly_properties_to_xml_element(self, model, xml_element):
    """This method adds the poly properties of 'model' to the provided xml element."""
    if not isinstance(model, VtkPolyModel):
      return
    # Add the properties
    ET.SubElement(xml_element, "visibility").text = "1" if model.is_visible() else "0"
    c = model.get_color()
    ET.SubElement(xml_element, "rgb_color").text = str(c[0]) + " " + str(c[1]) + " " + str(c[2])
    ET.SubElement(xml_element, "transparency").text = str(model.get_transparency())


  def __add_volume_properties_to_xml_element(self, model, xml_element):
    """This method adds the volume properties of 'model' to the provided xml element."""
    if not isinstance(model, VtkVolumeModel):
      return
    # Add the properties
    ET.SubElement(xml_element, "slice_index").text = str(model.get_slice_index())
