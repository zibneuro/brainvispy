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
  def __init__(self, name):
    self.name = name
    self.index = -1
    self.threshold = 0.0


class ConnectionParameters:
  def __init__(self):
    self.n1_name = "n1"
    self.n2_name = "n2"
    self.weight = -1


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
    if len(file_lines) < 2:
      return None

    # First, get rid of all white spaces
    neuron_names = "".join(file_lines[0].split())
    print("first line: '" + neuron_names + "'")

    # These is a (column id, neuron name) dictionary
    col_id_to_neuron_name = dict()

    # Get the column id of each neuron
    col_id = 0
    for neuron_name in neuron_names.split(","):
      if neuron_name == "":
        continue
      col_id_to_neuron_name[col_id] = neuron_name
      col_id += 1

    # How many neurons are there
    num_neurons = len(col_id_to_neuron_name)

    # Now, loop over the other table lines and create the neurons and neural connections
    for file_line in file_lines[1:]:
      # The current line contains the cells separated by a ","
      cells = file_line.split(",")
      # We need at least two cells per line
      if len(cells) < 2:
        continue

      neuron_name_1 = cells[0]
      col_id = -1
      
      # Loop over the cells. Each one contains the weight of the neural connection
      for cell in cells[1:num_neurons+1]:
        col_id += 1
        try:
          neuron_name_2 = col_id_to_neuron_name[col_id]
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
          
        # Get the second neuron
        print(neuron_name_1 + " -> " + neuron_name_2 + ": " + str(weight))
        

    # Get the neuron parameters
    #for file_line in file_lines:
    #  for neuron_name in split()
