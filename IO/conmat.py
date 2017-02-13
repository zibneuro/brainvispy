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


  def load_csv_file(self, file_name):
    file_lines = list()

    # Open the file and read in the lines    
    try:
      f = open(file_name, "r")
    except:
      return None
    file_lines = f.readlines()

    # Make sure we got at least one line
    if len(file_lines) < 1:
      return None

    neuron_params = dict()

    # Get the neuron names
    for neuron_name in file_lines[0].split(","):
      if neuron_name != "":
        neuron_params[neuron_name] = ConnectionParameters(name)

    # Get the neuron parameters
    #for file_line in file_lines:
    #  for neuron_name in split()
