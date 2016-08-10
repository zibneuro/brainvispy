import os
import xml.etree.ElementTree as ET
from core.progress import ProgressBar
from core.datacontainer import DataContainer
from vis.vtkpoly import VtkPolyModel
from vis.vtkvol import VtkVolumeModel
from gui.vtkwidget import VtkWidget
from .obj import OBJReader
from .vtkio import VtkIO

class CameraParameters:
  def __init__(self):
    self.position = None
    self.look_at = None
    self.view_up = None

  def print(self):
    print("pos:", self.position)
    print("look at:", self.look_at)
    print("view up:", self.view_up)


class ModelElements:
  def __init__(self):
    self.name = "unknown"
    self.file_name = ""
    self.relative_file_name = ""
    self.visibility = 1 # visible by default
    self.rgb_color = 0.8, 0.8, 0.8 # gray by default
    self.transparency = 0 # non-transparent by default
    self.slice_index = 0 # the first slice index by default


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

    # Parse the XML project file and return the info in our own format
    try:
      camera_parameters, model_data = self.__parse_xml_project_file(project_file_name)
    except Exception as error:
      error_msg = list()
      error_msg.append(str(error))
      return error_msg

    # Setup the VTK widget based on what we parsed
    vtk_widget.reset_view()
    vtk_widget.set_camera_position(camera_parameters.position)
    vtk_widget.set_camera_look_at(camera_parameters.look_at)
    vtk_widget.set_camera_view_up(camera_parameters.view_up)

    # Make sure that the VTK widget doesn't reset the view after the models are loaded below (since this would mess up the camera parameters we just set)
    reset_view = vtk_widget.reset_view_after_adding_models
    vtk_widget.do_reset_view_after_adding_models(False)

    # Now, do the real data loading (i.e., load the mesh/volume data), create the models and add them to the
    # container. Return a list of errors if any (e.g., which files could not be loaded, etc..)
    error_messages = self.__load_models(model_data, data_container)

    # Make sure we see all models
    vtk_widget.reset_clipping_range()

    # Restore the state of the VTK widget
    vtk_widget.do_reset_view_after_adding_models(reset_view)

    return error_messages


  def __parse_xml_project_file(self, project_file_name):
    # Parse the XML file
    project = ET.parse(project_file_name).getroot()

    # This list stores all the info per model
    models = list()

    # Load the attributes of each model
    for element in project:
      if   element.tag == "camera_parameters": camera_parameters = self.__parse_camera_parameters(element)
      elif element.tag == "model": models.append(self.__parse_model(element))

    # We are done with the XML file, return the parsed stuff
    return camera_parameters, models


  def __parse_camera_parameters(self, xml_camera):
    camera_parameters = CameraParameters()
    # Get the parameters from the XML element
    for element in xml_camera:
      if element.tag == "position":
        p = element.text.split(" ")
        camera_parameters.position = float(p[0]), float(p[1]), float(p[2])
      elif element.tag == "look_at":
        p = element.text.split(" ")
        camera_parameters.look_at = float(p[0]), float(p[1]), float(p[2])
      elif element.tag == "view_up":
        p = element.text.split(" ")
        camera_parameters.view_up = float(p[0]), float(p[1]), float(p[2])
    # Return the camera parameters
    return camera_parameters


  def __parse_model(self, xml_model):
    # Create a new object to store the elements of the current model
    model_elements = ModelElements()
    # Read all the elements of 'xml_model'
    for element in xml_model:
      if   element.tag == "name": model_elements.name = element.text
      elif element.tag == "file_name": model_elements.file_name = element.text
      elif element.tag == "relative_file_name": model_elements.relative_file_name = element.text
      elif element.tag == "properties":
        for prop in element:
          if   prop.tag == "visibility": model_elements.visibility = float(prop.text)
          elif prop.tag == "transparency": model_elements.transparency = float(prop.text)
          elif prop.tag == "slice_index": model_elements.slice_index = float(prop.text)
          elif prop.tag == "rgb_color":
           color_string = prop.text.split(" ")
           model_elements.rgb_color = (float(color_string[0]), float(color_string[1]), float(color_string[2]))
    # Return what we have parsed
    return model_elements


  def __load_models(self, model_data, data_container):
    """Using the model data from the list 'model_data' this method loads the mesh/volume data from disk,
    creates the models and adds them to the 'data_container'. Returns a list of errors if any (e.g., file
    cound not be loaded etc...)"""
    vtk_io = VtkIO()
    models = list()
    error_messages = list()

    # Get the project folder
    if self.__project_file_name:
      project_folder = os.path.split(self.__project_file_name)[0]
    else:
      project_folder = ""

    # Let the user know we are doing something    
    self.__progress_bar.init(1, len(model_data), "Loading files: ")
    counter = 0
    
    # Load the data from disk and initialize the model attributes
    for attributes in model_data:
      # Update the progress bar
      counter += 1
      self.__progress_bar.set_progress(counter)

      # Try with the relative path first
      rel_file_name = os.path.join(project_folder, attributes.relative_file_name)
      model = vtk_io.load(rel_file_name)
      if model:
        self.__initialize_model(model, attributes)
        models.append(model)
        continue

      # Obviously, we failed to load the model using the relative path
      final_error_message = "Couldn't load '" + attributes.name + "'. Tried with\n" + rel_file_name

      # Try with the absolute path
      model = vtk_io.load(attributes.file_name)
      if model:
        self.__initialize_model(model, attributes)
        models.append(model)
        continue

      # Failed with the absolute path too
      final_error_message += "\n" + attributes.file_name + "\n"
      error_messages.append(final_error_message)

    # We are done with model loading
    self.__progress_bar.done()
    # Now let the container adopt the new models
    data_container.add_models(models)
    # Return the error messages (if any)
    return error_messages


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

    # Get the project folder
    project_folder = os.path.split(self.__project_file_name)[0]

    # Create an XML object for the whole project
    xml_project = ET.Element("BrainVisPy_Project")

    # Save some camera parameters
    self.__add_camera_parameters_to_xml_element(vtk_widget, ET.SubElement(xml_project, "camera_parameters"))

    # Save the data of each model to the XML file
    for model in data_container.get_models():
      self.__add_model_data_to_xml_element(model, project_folder, ET.SubElement(xml_project, "model"))

    # Write the whole XML tree to file
    ET.ElementTree(xml_project).write(self.__project_file_name)


  def __add_camera_parameters_to_xml_element(self, vtk_widget, xml_element):
    """This method adds all camera parameters to the provided xml element."""
    position = vtk_widget.get_camera_position()
    ET.SubElement(xml_element, "position").text = str(position[0]) + " " + str(position[1]) + " " + str(position[2])
    look_at = vtk_widget.get_camera_look_at()
    ET.SubElement(xml_element, "look_at").text = str(look_at[0]) + " " + str(look_at[1]) + " " + str(look_at[2])
    view_up = vtk_widget.get_camera_view_up()
    ET.SubElement(xml_element, "view_up").text = str(view_up[0]) + " " + str(view_up[1]) + " " + str(view_up[2])


  def __add_model_data_to_xml_element(self, model, project_folder, xml_element):
    """This method adds all model data to the provided xml element."""
    ET.SubElement(xml_element, "name").text = model.name
    ET.SubElement(xml_element, "file_name").text = model.file_name
    ET.SubElement(xml_element, "relative_file_name").text = self.__compute_relative_file_name(model.file_name, project_folder)
    properties = ET.SubElement(xml_element, "properties")
    if isinstance(model, VtkPolyModel):
      self.__add_poly_properties_to_xml_element(model, properties)
    elif isinstance(model, VtkVolumeModel):
      self.__add_volume_properties_to_xml_element(model, properties)


  def __compute_relative_file_name(self, abs_file_name, project_folder):
    abs_path, file_name = os.path.split(abs_file_name)
    rel_path = os.path.relpath(abs_path, project_folder)
    return os.path.join(rel_path, file_name)


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
