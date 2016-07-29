import xml.etree.ElementTree as ET
from core.progress import ProgressBar
from vis.vtkpoly import VtkPolyModel
from vis.vtkvol import VtkVolumeModel
from .obj import OBJReader

class ProjectIO:
  def __init__(self):
    self.__project_file_name = None


  def set_file_name(self, file_name):
    self.__project_file_name = file_name


  def has_file_name(self):
    return self.__project_file_name != None


  def get_file_name(self):
    return self.__project_file_name


  def save(self, data_container):
    '''Saves all models in the 'data_container' in an XML file whose name you have to set with set_file_name().'''
    if not self.has_file_name():
      raise Exception("Error in " + self.__class__.__name__ + ": file name not set")

    # First, create an XML object
    xml_project = ET.Element("brain_vis_py_project")
    
    # Loop over all models in the data container
    for model in data_container.get_models():
      xml_model = ET.SubElement(xml_project, "model")
      ET.SubElement(xml_model, "name").text = model.name
      ET.SubElement(xml_model, "file_name").text = model.file_name
      self.add_model_properties_to_xml_element(model, ET.SubElement(xml_model, "properties"))

    # Write the whole XML tree to file
    ET.ElementTree(xml_project).write(self.__project_file_name)


  def add_model_properties_to_xml_element(self, model, xml_element):
    """This method adds the volume or poly properties (depending of what kind of 'model' we have) to the
    provided xml element."""
    if isinstance(model, VtkPolyModel):
      self.add_poly_properties_to_xml_element(model, xml_element)
    elif isinstance(model, VtkVolumeModel):
      self.add_volume_properties_to_xml_element(model, xml_element)


  def add_poly_properties_to_xml_element(self, model, xml_element):
    """This method adds the poly properties of 'model' to the provided xml element."""
    if not isinstance(model, VtkPolyModel):
      return
    # Add the properties
    ET.SubElement(xml_element, "visibility").text = "1" if model.is_visible() else "0"
    c = model.get_color()
    ET.SubElement(xml_element, "rgb_color").text = str(c[0]) + " " + str(c[1]) + " " + str(c[2])
    ET.SubElement(xml_element, "transparency").text = str(model.get_transparency())


  def add_volume_properties_to_xml_element(self, model, xml_element):
    """This method adds the volume properties of 'model' to the provided xml element."""
    if not isinstance(model, VtkVolumeModel):
      return
    # Add the properties
    ET.SubElement(xml_element, "slice_index").text = str(model.get_slice_index())
