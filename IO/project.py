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


class BrainRegionParameters:
  def __init__(self):
    self.name = "brain region"
    self.abs_file_name = None
    self.rel_file_name = None
    self.visibility = 1
    self.rgb_color = (0.8, 0.8, 0.8)
    self.transparency = 0


class NeuronParameters:
  def __init__(self):
    self.name = "neuron"
    self.index = -1
    self.sphere_radius = 0.5
    self.position = (0, 0, 0)    
    self.rgb_color = (0.8, 0.1, 0.0)


class ConnectivityParameters:
  def __init__(self):
    self.name = "connection"
    self.cylinder_radius = 0.5
    self.neuron_indices = (-1, -1)
    self.rgb_color = (0.1, 0.8, 0.0)


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

    error_messages = list()
    camera_parameters = CameraParameters()
    brain_region_parameters = list()
    neuron_parameters = list()
    connection_parameters = list()

    # Parse the XML project file and return the info in our own format
    try:
      self.__parse_xml_project_file(project_file_name, camera_parameters, brain_region_parameters, neuron_parameters, connection_parameters)
    except Exception as error:
      error_messages.append(str(error))
      return error_messages

    # Setup the VTK widget based on what we parsed
    vtk_widget.reset_view()
    vtk_widget.set_camera_position(camera_parameters.position)
    vtk_widget.set_camera_look_at(camera_parameters.look_at)
    vtk_widget.set_camera_view_up(camera_parameters.view_up)

    # Make sure that the VTK widget doesn't reset the view after the models are loaded below (since this would mess up the camera parameters we just set)
    reset_view = vtk_widget.reset_view_after_adding_models
    vtk_widget.do_reset_view_after_adding_models(False)

    # Load the brain regions (i.e., the meshes from disk)
    self.__load_brain_regions(brain_region_parameters, data_container, error_messages)
    # Create the neurons
    self.__add_neurons(neuron_parameters, data_container, error_messages)
    # Create the connections
    self.__add_connections(connection_parameters, data_container, error_messages)

    # Make sure we see all models
    vtk_widget.reset_clipping_range()
    # Restore the state of the VTK widget
    vtk_widget.do_reset_view_after_adding_models(reset_view)

    return error_messages


  def __parse_xml_project_file(self, project_file_name, camera_parameters, brain_region_parameters, neuron_parameters, connection_parameters):
    # Parse the XML file
    project = ET.parse(project_file_name).getroot()

    for element in project:
      if   element.tag == "camera_parameters": self.__parse_camera(element, camera_parameters)
      elif element.tag == "brain_region": brain_region_parameters.append(self.__parse_brain_region(element))
      elif element.tag == "neuron": neuron_parameters.append(self.__parse_neuron(element))
      elif element.tag == "connection": connection_parameters.append(self.__parse_connection(element))


  def __parse_camera(self, xml_input, camera_parameters):
    # Get the parameters from the XML element
    for element in xml_input:
      if element.tag == "position":
        p = element.text.split(" ")
        camera_parameters.position = float(p[0]), float(p[1]), float(p[2])
      elif element.tag == "look_at":
        p = element.text.split(" ")
        camera_parameters.look_at = float(p[0]), float(p[1]), float(p[2])
      elif element.tag == "view_up":
        p = element.text.split(" ")
        camera_parameters.view_up = float(p[0]), float(p[1]), float(p[2])


  def __parse_brain_region(self, xml_input):
    # Create a new object to store the parsed elements
    brain_region = BrainRegionParameters()
    # Read all the elements of 'xml_input'
    for element in xml_input:
      if   element.tag == "name": brain_region.name = element.text
      elif element.tag == "abs_file_name": brain_region.abs_file_name = element.text
      elif element.tag == "rel_file_name": brain_region.rel_file_name = element.text
      elif element.tag == "visibility": brain_region.visibility = float(element.text)
      elif element.tag == "transparency": brain_region.transparency = float(element.text)
      elif element.tag == "rgb_color":
        color_string = element.text.split(" ")
        brain_region.rgb_color = (float(color_string[0]), float(color_string[1]), float(color_string[2]))
    # Return what we have parsed
    return brain_region


  def __parse_neuron(self, xml_input):
    # Create a new object to store the parsed elements
    neuron = NeuronParameters()
    # Read all the elements of 'xml_input'
    for element in xml_input:
      if   element.tag == "name": neuron.name = element.text
      elif element.tag == "index": neuron.index = int(element.text)
      elif element.tag == "sphere_radius": neuron.sphere_radius = float(element.text)
      elif element.tag == "position":
        pos_string = element.text.split(" ")
        neuron.position = (float(pos_string[0]), float(pos_string[1]), float(pos_string[2]))
      elif element.tag == "rgb_color":
        color_string = element.text.split(" ")
        neuron.rgb_color = (float(color_string[0]), float(color_string[1]), float(color_string[2]))
    # Return what we have parsed
    return neuron


  def __parse_connection(self, xml_input):
    # Create a new object to store the parsed elements
    connection = ConnectionParameters()
    # Read all the elements of 'xml_input'
    for element in xml_input:
      if   element.tag == "name": connection.name = element.text
      elif element.tag == "cylinder_radius": connection.cylinder_radius = float(element.text)
      elif element.tag == "neuron_indices":
        indices_string = element.text.split(" ")
        connection.neuron_indices = (int(indices_string[0]), int(indices_string[1]))
      elif element.tag == "rgb_color":
        color_string = element.text.split(" ")
        connection.rgb_color = (float(color_string[0]), float(color_string[1]), float(color_string[2]))
    # Return what we have parsed
    return connection


  def __load_brain_regions(self, brain_region_parameters, data_container):
    vtk_io = VtkIO()
    brain_regions = list()
    error_messages = list()

    # Get the project folder
    if self.__project_file_name:
      project_folder = os.path.split(self.__project_file_name)[0]
    else:
      project_folder = ""

    # Let the user know we are doing something    
    self.__progress_bar.init(1, len(model_data), "Loading files: ")
    counter = 0
    
    # Load the VTK files from disk and create the brain regions
    for parameters in brain_region_parameters:
      # Update the progress bar
      counter += 1
      self.__progress_bar.set_progress(counter)

      vtk_poly_data = None

      # Try with the absolute file name
      if parameters.abs_file_name:
        vtk_poly_data = vtk_io.load(parameters.abs_file_name)

      # Try with the relative file name
      if not vtk_poly_data:
        rel_file_name = os.path.join(project_folder, parameters.rel_file_name)
        vtk_poly_data = vtk_io.load(rel_file_name)

      if vtk_poly_data:
        brain_regions.append(self.__create_brain_region(vtk_poly_data, parameters))
      else:
        error_messages.append("Couldn't load brain region '" + parameters.name + "'\n")

    # We are done with loading
    self.__progress_bar.done()
    # Add the new data to the container
    data_container.add_brain_regions(brain_regions)
    # Return the error messages (if any)
    return error_messages


  def __add_neurons(neuron_parameters, data_container, error_messages):
    pass


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

      # If an error occurs, be prepared
      error_message = "Couldn't load '" + attributes.name + "'. Tried with\n"

      # Try with the relative path first
      if attributes.relative_file_name:
        rel_file_name = os.path.join(project_folder, attributes.relative_file_name)
        model = vtk_io.load(rel_file_name)
        if model:
          self.__initialize_model(model, attributes)
          models.append(model)
          continue
        # Failed
        error_message += rel_file_name + "\n"

      # Try with the absolute file name
      if attributes.file_name:
        model = vtk_io.load(attributes.file_name)
        if model:
          self.__initialize_model(model, attributes)
          models.append(model)
          continue
        # Failed with the absolute path too
        error_message += attributes.file_name + "\n"
        error_messages.append(error_message)

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
