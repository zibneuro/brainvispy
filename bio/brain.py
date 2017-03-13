from generators.neurongenerator import NeuronGenerator
from generators.neuralconnectiongenerator import NeuralConnectionGenerator
from generators.randompoints import RandomPointsGenerator
from core.datacontainer import DataContainer
from bio.brainregion import BrainRegion
from bio.neuron import Neuron
from bio.neuralconnection import NeuralConnection
from geom.connectedcomponents import ConnectedComponents

class Brain:
  def __init__(self, data_container):
    self.__name_to_brain_region = dict()
    self.__idx_to_neuron = dict()
    self.__name_to_neuron = dict()
    self.__name_to_neural_connection = dict()

    self.__data_container = data_container
    self.__data_container.add_observer(self)


  def observable_changed(self, change, data):
    # Decide what to do depending on what changed
    if change == DataContainer.change_is_new_data:
      self.__add_brain_regions(data)
    elif change == DataContainer.change_is_deleted_models:
      self.__delete_data(data)


  def __add_brain_regions(self, data):
    for model in data:
      if isinstance(model, BrainRegion):
        self.__name_to_brain_region[model.name] = model


  def __delete_data(self, data_items):
    for item in data_items:
      if isinstance(item, BrainRegion): # delete the brain region
        try:
          del self.__name_to_brain_region[item.name]
        except KeyError:
          pass
      elif isinstance(item, NeuralConnection): # delete the neural connection
        try:
          del self.__name_to_neural_connection[item.name]
        except KeyError:
          pass
      elif isinstance(item, Neuron): # delete the neuron
        self.__delete_neuron(item)


  def __delete_neuron(self, neuron):
    try:
      del self.__idx_to_neuron[neuron.index]
    except KeyError:
      pass

    try:
      del self.__name_to_neuron[neuron.name]
    except KeyError:
      pass


  def create_neurons(self, neuron_parameters):
    if not neuron_parameters:
      return []

    # Delete the existing neurons
    self.__data_container.delete_models(list(self.__idx_to_neuron.values()))

    split_brain_regions = dict()
    brain_region_to_neurons = dict()
    neuro_gen = NeuronGenerator()
    new_neurons = list()

    missing_brain_regions = set()

    for np in neuron_parameters:
      # Create a new neuron
      try: # to get its position
        p = np.position
      except AttributeError:
        # No position is provided
        try: # to get a brain region name
          brain_region_name = np.brain_region_name
        except AttributeError:
          # Neither position nor brain region => cannot create the neuron
          continue
        else:
          # Make sure we have the desired brain region
          try:
            brain_region = self.__name_to_brain_region[brain_region_name]
          except KeyError:
            missing_brain_regions.add(brain_region_name)
            continue

          # Shall we split the brain region?
          if np.brain_side:
            brain_side = np.brain_side[0].lower()
            if brain_side == "l" or brain_side == "r":
              if brain_region_name not in split_brain_regions:
                split_brain_regions[brain_region_name] = self.__split_brain_region(brain_region)
              brain_region = split_brain_regions[brain_region_name][brain_side]

          # Save the brain region for latter neuron generation
          if brain_region not in brain_region_to_neurons:
            brain_region_to_neurons[brain_region] = list()
          # Save the neuron parameters
          brain_region_to_neurons[brain_region].append(np)
      else:
        # We got position -> create the neuron
        neuron = neuro_gen.create_neuron(np.name, np.index, p, np.threshold)
        self.__add_neuron(neuron)
        new_neurons.append(neuron)

    # Now generate the neurons inside the brain regions
    for brain_region in brain_region_to_neurons:
      # Get the neuron parameters
      neuron_parameters = brain_region_to_neurons[brain_region]
      # Generate the neuron positions
      rnd_pts_gen = RandomPointsGenerator(brain_region)
      neuron_positions = rnd_pts_gen.generate_points_inside_mesh(len(neuron_parameters))

      for i in range(len(neuron_parameters)):
        np = neuron_parameters[i]
        neuron = neuro_gen.create_neuron(np.name, np.index, neuron_positions[i], np.threshold)
        self.__add_neuron(neuron)
        new_neurons.append(neuron)

    # Add the new neurons to the data container
    self.__data_container.add_data(new_neurons)
    
    # Inform the user about missing brain regions
    if missing_brain_regions:
      error_message = "Missing brain region(s):\n"
      for name in missing_brain_regions:
        error_message += "  " + name + "\n"
      return [error_message]

    # everything is fine
    return []
    

  def __split_brain_region(self, brain_region):
    cc = ConnectedComponents()
    components = cc.extract_connected_components(brain_region)
    if len(components) == 1:
      return {"l": components[0], "r": components[0]}
    # Sort the components according to their center of mass' projection along the x axis
    sorted_meshes = cc.sort_meshes(0, components[0], components[1])
    return {"l": sorted_meshes[1], "r": sorted_meshes[0]}


  def create_neural_connections(self, connection_parameters):
    if not connection_parameters:
      return []

    # Delete existing neural connections
    self.__data_container.delete_models(list(self.__name_to_neural_connection.values()))

    nc_gen = NeuralConnectionGenerator()
    new_neural_connections = list()

    for cp in connection_parameters:
      # Get the neurons we are supposed to connect
      src_neuron = self.__name_to_neuron.get(cp.src_neuron_name)
      tar_neuron = self.__name_to_neuron.get(cp.tar_neuron_name)
      if not src_neuron or not tar_neuron:
        continue
      # Create the name of the neural connection
      nc_name = self.__compute_neural_connection_name(src_neuron.name, tar_neuron.name)
      # Create a new neural connection and save it
      nc = nc_gen.create_neural_connection(nc_name, src_neuron.name, tar_neuron.name, src_neuron.p, tar_neuron.p, cp.weight)
      self.__name_to_neural_connection[nc_name] = nc
      new_neural_connections.append(nc)

    # Add the new connections to the data container
    self.__data_container.add_data(new_neural_connections)
    # No error messages
    return []


  def __delete_existing_neural_connections(self, connection_parameters):
    connections_to_delete = list()
    # Collect the existing connections
    for cp in connection_parameters:
      connection_name = self.__compute_neural_connection_name(cp.src_neuron_name, cp.tar_neuron_name)
      connection = self.__name_to_neural_connection.get(connection_name)
      if connection:
        connections_to_delete.append(connection)
    # Delete the existing connections
    if connections_to_delete:
      self.__data_container.delete_models(connections_to_delete)


  def __compute_neural_connection_name(self, src_neuron_name, tar_neuron_name):
    return src_neuron_name + " -> " + tar_neuron_name


  def __add_neuron(self, neuron):
    self.__idx_to_neuron[neuron.index] = neuron
    self.__name_to_neuron[neuron.name] = neuron
