import xml.etree.ElementTree as ET
from core.progress import ProgressBar
from core.datacontainer import DataContainer
from vis.vtkpoly import VtkPolyModel
from vis.vtkvol import VtkVolumeModel
from .obj import OBJReader

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
  def __init__(self):
    self.__project_file_name = None


  def set_file_name(self, file_name):
    self.__project_file_name = file_name


  def has_file_name(self):
    return self.__project_file_name != None


  def get_file_name(self):
    return self.__project_file_name


  def open(self, project_file_name, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("input has to be of type DataContainer")
    # This is the new project file name
    self.__project_file_name = project_file_name

    # Remove everything from the data container
    data_container.clear()

    # Load the data from the project and return the error messages (if any)
    model_data = self.__load_model_data_from_project_file(project_file_name, data_container)
    
    for model in model_data:
      model.print()
    
    return list()


  def __load_model_data_from_project_file(self, project_file_name, data_container):
    # Parse the XML file
    project = ET.parse(project_file_name).getroot()

    # This list stores all the info per model
    model_data = list()

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
      model_data.append(model_elements)
    # We are done with the XML file, return the loaded model data
    return model_data


  def save(self, data_container):
    '''Saves all models in the 'data_container' in an XML file whose name you have to set with set_file_name().'''
    if not isinstance(data_container, DataContainer):
      raise TypeError("input has to be of type DataContainer")

    if not self.has_file_name():
      raise Exception("Error in " + self.__class__.__name__ + ": file name not set")

    # First, create an XML object
    xml_project = ET.Element("BrainVisPy_Project")

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
