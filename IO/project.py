import xml.etree.ElementTree as ET
from core.progress import ProgressBar
from .obj import OBJReader

class ProjectIO:
  def __init__(self):
    pass

  def save(self, file_name, data_container):
    '''Saves all models in the 'data_container' in an XML file named 'file_name'. Returns a boolean which
    indicates success or failure.'''
    # First, create an XML object
    xml_bvpy_project = ET.Element("bvpy_project")
    
    # Loop over all models in the data container
    for model in data_container.get_models():
      xml_model = ET.SubElement(xml_bvpy_project, "model")
      ET.SubElement(xml_model, "file_name").text = model.file_name

    tree = ET.ElementTree(xml_bvpy_project)
    tree.write(file_name)
