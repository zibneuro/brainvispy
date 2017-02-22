import os
import vtk
import xml.etree.ElementTree as ET
from core.progress import ProgressBar
from core.datacontainer import DataContainer
from bio.brainregion import BrainRegion
from bio.neuron import Neuron
from bio.neuralconnection import NeuralConnection
from vis.visbrainregion import VisBrainRegion
from gui.vtkwidget import VtkWidget
from IO.vtkio import VtkIO

class CameraParameters:
  def __init__(self):
    self.position = None
    self.look_at = None
    self.view_up = None


class BrainRegionParameters:
  def __init__(self, name = "brain region", abs_file_name = None):
    self.name = name
    self.abs_file_name = abs_file_name
    self.rel_file_name = None
    self.visibility = 1
    self.see_inside = 0
    self.transparency = 0
    self.rgb_color = VisBrainRegion.generate_random_rgb_color()


class NeuronParameters:
  def __init__(self):
    self.name = "neuron"
    self.index = -1
    self.position = (0, 0, 0)
    self.threshold = 0.0


class ConnectionParameters:
  def __init__(self):
    self.name = "connection"
    self.neuron_indices = (-1, -1)
    self.weight = -1


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


  @property
  def file_name(self):
    return self.__project_file_name


  def load_files(self, file_names, data_container, vtk_widget):
    vtk_io = VtkIO()
    brain_regions = list()

    # Let the user know we are doing something    
    self.__progress_bar.init(1, len(file_names), "Loading files: ")
    counter = 0

    for file_name in file_names:
      # Update the progress bar
      counter += 1
      self.__progress_bar.set_progress(counter)

      # Load the file
      vtk_poly_data = vtk_io.load(file_name)
      if not vtk_poly_data:
        continue

      # Create and save the brain region
      if isinstance(vtk_poly_data, vtk.vtkPolyData):
        brain_regions.append(self.__create_brain_region(vtk_poly_data, BrainRegionParameters(self.__extract_name(file_name), file_name)))

    # We are done with loading
    self.__progress_bar.done()
    # Now, add the brain regions to the data container
    data_container.add_data(brain_regions)
    # Make sure all models are visible
    vtk_widget.reset_view()


  def open_project(self, project_file_name, data_container, brain, vtk_widget):
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

    # Load the brain regions (i.e., the meshes from disk)
    self.__load_brain_regions(brain_region_parameters, data_container, error_messages)
    # Create the neurons (note that they are not loaded but the visual representation is generated on the fly)
    data_container.add_data(brain.create_neurons(neuron_parameters))
    # Create the connections (note that they are not loaded but the visual representation is generated on the fly)
    self.__create_neural_connections(connection_parameters, data_container, brain)

    # Setup the VTK widget based on what we parsed
    vtk_widget.set_camera_position(camera_parameters.position)
    vtk_widget.set_camera_look_at(camera_parameters.look_at)
    vtk_widget.set_camera_view_up(camera_parameters.view_up)
    vtk_widget.reset_clipping_range()

    return error_messages


  def __parse_xml_project_file(self, project_file_name, camera_parameters, brain_region_parameters, neuron_parameters, connection_parameters):
    # Parse the XML file
    project = ET.parse(project_file_name).getroot()

    for element in project:
      if   element.tag == "camera_parameters": self.__parse_camera(element, camera_parameters)
      elif element.tag == "brain_region": brain_region_parameters.append(self.__parse_brain_region(element))
      elif element.tag == "neuron": neuron_parameters.append(self.__parse_neuron(element))
      elif element.tag == "neural_connection": connection_parameters.append(self.__parse_neural_connection(element))


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
    # Read all elements of 'xml_input'
    for element in xml_input:
      if   element.tag == "name": brain_region.name = element.text
      elif element.tag == "abs_file_name": brain_region.abs_file_name = element.text
      elif element.tag == "rel_file_name": brain_region.rel_file_name = element.text
      elif element.tag == "visibility": brain_region.visibility = int(element.text)
      elif element.tag == "see_inside": brain_region.see_inside = int(element.text)
      elif element.tag == "transparency": brain_region.transparency = float(element.text)
      elif element.tag == "rgb_color":
        color_string = element.text.split(" ")
        brain_region.rgb_color = (float(color_string[0]), float(color_string[1]), float(color_string[2]))
    # Return what we have parsed
    return brain_region


  def __parse_neuron(self, xml_input):
    # Create a new object to store the parsed elements
    neuron_params = NeuronParameters()
    # Read all elements of 'xml_input'
    for element in xml_input:
      if   element.tag == "name": neuron_params.name = element.text
      elif element.tag == "index": neuron_params.index = int(element.text)
      elif element.tag == "position":
        pos_string = element.text.split(" ")
        neuron_params.position = (float(pos_string[0]), float(pos_string[1]), float(pos_string[2]))
      elif element.tag == "threshold": neuron_params.threshold = float(element.text)
    # Return what we have parsed
    return neuron_params


  def __parse_neural_connection(self, xml_input):
    # Create a new object to store the parsed elements
    connection = ConnectionParameters()
    # Read all elements of 'xml_input'
    for element in xml_input:
      if   element.tag == "name": connection.name = element.text
      elif element.tag == "neuron_indices":
        indices_string = element.text.split(" ")
        connection.neuron_indices = (int(indices_string[0]), int(indices_string[1]))
      elif element.tag == "weight": connection.weight = float(element.text)
    # Return what we have parsed
    return connection


  def __load_brain_regions(self, brain_region_parameters, data_container, error_messages):
    vtk_io = VtkIO()
    brain_regions = list()

    # Get the project folder (only used for the relative file paths below)
    if self.__project_file_name:
      project_folder = os.path.split(self.__project_file_name)[0]
    else:
      project_folder = ""

    # Let the user know we are doing something    
    self.__progress_bar.init(1, len(brain_region_parameters), "Loading files: ")
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
        parameters.abs_file_name = os.path.join(project_folder, parameters.rel_file_name)
        vtk_poly_data = vtk_io.load(parameters.abs_file_name)

      # Check for errors
      if not vtk_poly_data:
        error_messages.append("Couldn't load brain region '" + parameters.name + "'")
      elif not isinstance(vtk_poly_data, vtk.vtkPolyData):
        error_messages.append("Brain region '" + parameters.name + "' has to be a polygon mesh.")
      else: # we are fine -> create a brain region based on the loaded geometry
        brain_regions.append(self.__create_brain_region(vtk_poly_data, parameters))

    # We are done with loading
    self.__progress_bar.done()
    # Add the new data to the container
    data_container.add_data(brain_regions)


  def __create_brain_region(self, vtk_poly_data, parameters):
    # Create the visual representation of the brain region
    vis_brain_region = VisBrainRegion(parameters.name, vtk_poly_data, parameters.abs_file_name)
    vis_brain_region.set_color(parameters.rgb_color[0], parameters.rgb_color[1], parameters.rgb_color[2])
    vis_brain_region.set_visibility(parameters.visibility)
    vis_brain_region.set_see_inside(parameters.see_inside)
    vis_brain_region.set_transparency(parameters.transparency)
    # Create and return the brain region
    brain_region = BrainRegion(parameters.name, None, vis_brain_region)
    return brain_region


  def __create_neural_connections(self, connection_parameters, data_container, brain):
    return
    connections = list()
    # Create the neurons
    for ps in connection_parameters:
      connection = brain.create_neural_connection(ps.name, ps.neuron_indices, ps.weight)
      if connection:
        connections.append(connection)
    # Add the connections to the data container
    data_container.add_data(connections)


  def __extract_name(self, file_name):
    file_name_no_path = os.path.split(file_name)[1]
    return os.path.splitext(file_name_no_path)[0]


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
    self.__save_camera_parameters(vtk_widget, ET.SubElement(xml_project, "camera_parameters"))

    # Save the data of each model to the XML file
    for model in data_container.get_models():
      if isinstance(model, BrainRegion):
        self.__save_brain_region(model, project_folder, ET.SubElement(xml_project, "brain_region"))
      elif isinstance(model, Neuron):
        self.__save_neuron(model, ET.SubElement(xml_project, "neuron"))
      elif isinstance(model, NeuralConnection):
        self.__save_neural_connection(model, ET.SubElement(xml_project, "neural_connection"))

    # Write the whole XML tree to file
    ET.ElementTree(xml_project).write(self.__project_file_name)


  def __save_camera_parameters(self, vtk_widget, xml_element):
    """This method adds all camera parameters to the provided xml element."""
    position = vtk_widget.get_camera_position()
    ET.SubElement(xml_element, "position").text = str(position[0]) + " " + str(position[1]) + " " + str(position[2])
    look_at = vtk_widget.get_camera_look_at()
    ET.SubElement(xml_element, "look_at").text = str(look_at[0]) + " " + str(look_at[1]) + " " + str(look_at[2])
    view_up = vtk_widget.get_camera_view_up()
    ET.SubElement(xml_element, "view_up").text = str(view_up[0]) + " " + str(view_up[1]) + " " + str(view_up[2])


  def __save_brain_region(self, brain_region, project_folder, xml_element):
    ET.SubElement(xml_element, "name").text = brain_region.name
    vis_rep = brain_region.visual_representation
    ET.SubElement(xml_element, "abs_file_name").text = vis_rep.file_name
    ET.SubElement(xml_element, "rel_file_name").text = self.__compute_relative_file_name(vis_rep.file_name, project_folder)
    ET.SubElement(xml_element, "visibility").text = str(vis_rep.get_visibility())
    ET.SubElement(xml_element, "transparency").text = str(vis_rep.get_transparency())
    ET.SubElement(xml_element, "see_inside").text = str(vis_rep.see_inside)
    c = vis_rep.get_color()
    ET.SubElement(xml_element, "rgb_color").text = str(c[0]) + " " + str(c[1]) + " " + str(c[2])


  def __save_neuron(self, neuron, xml_element):
    ET.SubElement(xml_element, "name").text = neuron.name
    ET.SubElement(xml_element, "index").text = str(neuron.index)
    p = neuron.position
    ET.SubElement(xml_element, "position").text = str(p[0]) + " " + str(p[1]) + " " + str(p[2])
    ET.SubElement(xml_element, "threshold").text = str(neuron.threshold)


  def __save_neural_connection(self, connection, xml_element):
    ET.SubElement(xml_element, "name").text = connection.name
    ET.SubElement(xml_element, "neuron_indices").text = str(connection.neuron1.index) + " " + str(connection.neuron2.index)
    ET.SubElement(xml_element, "weight").text = str(connection.weight)


  def __compute_relative_file_name(self, abs_file_name, project_folder):
    abs_path, file_name = os.path.split(abs_file_name)
    rel_path = os.path.relpath(abs_path, project_folder)
    return os.path.join(rel_path, file_name)
