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


class NeuronParameters:
  def __init__(self, name, index, brain_region_name, threshold):
    self.name = name
    self.index = index
    self.brain_region_name = brain_region_name
    self.threshold = threshold


class NeuralConnectionParameters:
  def __init__(self, src_neuron_name, tar_neuron_name, weight):
    self.src_neuron_name = src_neuron_name
    self.tar_neuron_name = tar_neuron_name
    self.weight = weight


class ConnectivityMatrixIO:
  def __init__(self):
    pass


  def load_neurons(self, connectivity_matrix_file_name, brain):
    res = self.__load_csv_file(connectivity_matrix_file_name)
    return list()


  def __load_csv_file(self, file_name):
    file_lines = list()

    # Open the file and read in the lines    
    try:
      f = open(file_name, "r")
    except:
      return None
    file_lines = f.readlines()

    # Make sure we got enough lines
    if len(file_lines) < 1:
      return None

    # These two lists will be filled below and returned
    neurons = list()
    neural_connections = list()

    # First, get rid of all white spaces
    neuron_names = "".join(file_lines[0].split())

    # These is a (column id, neuron name) dictionary
    col_id_to_neuron_name = dict()

    # Populate the (column id, neuron name) dictionary
    col_id = 0
    for neuron_name in neuron_names.split(","):
      if neuron_name == "":
        continue
      col_id_to_neuron_name[col_id] = neuron_name
      col_id += 1
 
    # How many neurons are there
    num_neurons = len(col_id_to_neuron_name)
    neuron_id = -1

    # Now, loop over the other table lines and create the neurons and neural connections
    for file_line in file_lines[1:]:
      neuron_id += 1
      # The current line contains the cells separated by a ","
      cells = file_line.split(",")

      if len(cells) < 1:
        continue
        
      # Get the name of the current neuron
      neuron_name = cells[0]

      # Create the connections using the cells 1 to #neurons + 1
      connections = self.__create_neural_connections(neuron_name, cells[1:num_neurons+1], col_id_to_neuron_name)
      # Save the connections
      if connections:
        neural_connections.extend(connections)

      # Create a new neuron
      neuron = self.__create_neuron(neuron_name, neuron_id, cells[num_neurons+1:])
      # Save the neuron
      if neuron:
        neurons.append(neuron)

    print("neurons:")
    for n in neurons:
      print("neuron " + n.name + " (@" + str(n.threshold) + ") in " + n.brain_region_name)

    print("neural connections:")
    for c in neural_connections:
      print(c.src_neuron_name + " -> " + c.tar_neuron_name + ": " + str(c.weight))

    return (neurons, neural_connections)


  def __create_neural_connections(self, src_neuron_name, cells, col_id_to_neuron_name):
    neural_connections = list()
    col_id = -1

    # Loop over the cells. Each one contains the weight of the neural connection
    for cell in cells:
      col_id += 1
      try:
        tar_neuron_name = col_id_to_neuron_name[col_id]
      except KeyError:
        continue

      if cell == "":
        continue

      try:
        weight = float(cell)
      except ValueError:
        continue

      if weight == 0:
        continue

      neural_connections.append(NeuralConnectionParameters(src_neuron_name, tar_neuron_name, weight))

    return neural_connections


  def __create_neuron(self, neuron_name, neuron_id, cells):
    if len(cells) < 2:
      return None

    try:
      threshold = float(cells[1])
    except ValueError:
      return None

    return NeuronParameters(neuron_name, neuron_id, cells[0], threshold)
