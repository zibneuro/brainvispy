import csv
import random


class SymmetricNeuron:
  def __init__(self, name, brain_region_name, threshold):
    self.name = name
    self.brain_region_name = brain_region_name
    self.threshold = threshold


class NeuronParameters:
  def __init__(self, name, index, brain_region_name, brain_side, threshold):
    self.name = name
    self.index = index
    self.brain_region_name = brain_region_name
    self.brain_side = brain_side
    self.threshold = threshold


class NeuralConnectionParameters:
  def __init__(self, src_neuron_name, tar_neuron_name, weight):
    self.src_neuron_name = src_neuron_name
    self.tar_neuron_name = tar_neuron_name
    self.weight = weight


class ConnectivityMatrixIO:
  def load_matrix(self, connectivity_matrix_file_name, brain):
    # Load the neuron and neural connection parameters from file
    neuron_params, conn_params, load_errors = self.__load_csv_file(connectivity_matrix_file_name)
    # Add them to the brain and the data container
    neuron_errors = brain.create_neurons(neuron_params)
    nc_errors = brain.create_neural_connections(conn_params)
    # Return all the error messages
    return load_errors + neuron_errors + nc_errors


  def __load_csv_file(self, file_name):
    # Open the file and read in the lines    
    try:
      f = open(file_name, "r")
    except:
      return (None, None, ["Could not open '" + file_name + "'"])
    csv_reader = csv.reader(f)

    names_set = set()
    neuron_names = list()

    # Get the neuron names
    for row in csv_reader:
      for cell in row:
        if cell.strip():
          names_set.add(cell)
          neuron_names.append(cell)
      break

    if len(neuron_names) == len(names_set):
      return self.__load_general_matrix(file_name)
    elif len(neuron_names) == 2*len(names_set):
      return self.__load_symmetric_matrix(neuron_names, csv_reader)
    else:
      return (None, None, ["invalid matrix format"])

    return (None, None, [])


  def __load_general_matrix(self, file_name):
    file_lines = list()

    # Open the file and read in the lines    
    try:
      f = open(file_name, "r")
    except:
      return (None, None, ["Could not open '" + file_name + "'"])
    file_lines = f.readlines()

    # Make sure we got enough lines
    if len(file_lines) <= 1:
      return (None, None, ["Too few lines in the matrix file"])

    # These two lists will be filled below and returned
    neurons = list()
    neural_connections = list()

    # Process the first line (it contains the neuron names). First, get rid of all white spaces.
    neuron_names = "".join(file_lines[0].split())

    # This is a (column id, neuron name) dictionary
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
    neuron_idx = -1

    # Now, loop over the other table lines and create the neurons and neural connections
    for file_line in file_lines[1:]:
      neuron_idx += 1
      # The current line contains the cells separated by a ","
      cells = file_line.split(",")

      if len(cells) < 1:
        continue

      # Get the name of the current neuron
      neuron_name = cells[0]

      # Create a new neuron using the cells which contain the neuron parameters
      neuron = self.__create_neuron(neuron_name, neuron_idx, cells[num_neurons+1:])
      if neuron: # save the neuron
        neurons.append(neuron)
      else:
        continue # we couldn't create the neuron => we cannot create neural connections from/to it

      # Create the connections using the cells which contain the connection weights
      connections = self.__create_neural_connections(neuron_name, cells[1:num_neurons+1], col_id_to_neuron_name)
      # Save the connections
      if connections:
        neural_connections.extend(connections)

    return (neurons, neural_connections, [])


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


  def __create_neuron(self, neuron_name, neuron_idx, cells):
    if len(cells) < 3:
      return None

    brain_region_name = cells[0]
    # Make sure there is a brain region name
    if brain_region_name == "":
      return None

    # Get the side of the brain (left or right) which contains the neuron
    if cells[1] != "":
      brain_side = cells[1]
    else:
      brain_side = None

    # Get the threshold for this neuron
    try:
      threshold = float(cells[2])
    except ValueError:
      return None

    return NeuronParameters(neuron_name, neuron_idx, brain_region_name, brain_side, threshold)


  def __load_symmetric_matrix(self, neuron_names, csv_reader):
    neurons = list()
    neural_connections = list()
    index = 0

    for row in csv_reader:
      try:
        neuron_name = row[0].strip()
      except IndexError:
        continue
      else:
        if not neuron_name:
          continue

      neuron = self.__extract_neuron(neuron_name, row[len(neuron_names)+1:])
      if neuron:
        neurons.append(neuron)
        neural_connections.extend(self.__extract_neural_connections(neuron_names, row))

      index += 1
      if index >= len(neuron_names) // 2:
        break

    print(neuron_names)
    for n in neurons:
      print(n.name + " in " + n.brain_region_name + " @ " + str(n.threshold))
    for c in neural_connections:
      print(c.src_neuron_name + " -> " + c.tar_neuron_name + " @ " + str(c.weight))

    #return (neurons, neural_connections, [])
    return (None, None, [])


  def __extract_neuron_names(self, row):
    neuron_names = list()
    for cell in row:
      if cell.strip():
        neuron_names.append(cell)
    return neuron_names


  def __extract_neuron(self, neuron_name, cells):
    try:
      brain_region = cells[0]
    except IndexError:
      return None

    try:
      threshold = float(cells[1])
    except (IndexError, ValueError): # the index may be out of bounds and/or the conversion to float may fail
      threshold = random.uniform(-1, 1)

    return SymmetricNeuron(neuron_name, brain_region, threshold)


  def __extract_neural_connections(self, target_neuron_names, row):
    try:
      src_neuron_name = row[0]
    except IndexError:
      return []

    end = len(target_neuron_names) // 2
    neural_connections = list()

    # The first half of the table (the ipsilateral connections)
    for cell, tar_neuron_name in zip(row[1:], target_neuron_names[0:end]):
      try:
        weight = float(cell)
      except ValueError:
        continue
      neural_connections.append(NeuralConnectionParameters(src_neuron_name + "_L", tar_neuron_name + "_L", weight))
      neural_connections.append(NeuralConnectionParameters(src_neuron_name + "_R", tar_neuron_name + "_R", weight))

    # The second half of the table (the contralateral connections)
    for cell, tar_neuron_name in zip(row[end+1:], target_neuron_names[end:2*end]):
      try:
        weight = float(cell)
      except ValueError:
        continue
      neural_connections.append(NeuralConnectionParameters(src_neuron_name + "_L", tar_neuron_name + "_R", weight))
      neural_connections.append(NeuralConnectionParameters(src_neuron_name + "_R", tar_neuron_name + "_L", weight))

    return neural_connections
