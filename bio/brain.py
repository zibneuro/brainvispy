from generators.neurongenerator import NeuronGenerator
from generators.neuralconnectiongenerator import NeuralConnectionGenerator
from generators.symmetricpoints import SymmetricPointsGenerator
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
    # Delete the existing neurons
    self.__data_container.delete_models(list(self.__idx_to_neuron.values()))

    if not neuron_parameters:
      return []

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

          # Save the brain region and the corresponding neuron parameters for latter neuron generation
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
      # This is the guy who generates the random neuron positions
      points_generator = SymmetricPointsGenerator(brain_region, axis=0)

      for params in neuron_parameters:
        neuron_position = points_generator.generate_point_inside_mesh(params.brain_side)
        neuron = neuro_gen.create_neuron(params.name, params.index, neuron_position, params.threshold)
        self.__add_neuron(neuron)
        new_neurons.append(neuron)

    self.__data_container.add_data(new_neurons)
    
    # Inform the user about missing brain regions
    if missing_brain_regions:
      error_message = "Missing brain region(s):\n"
      for name in missing_brain_regions:
        error_message += "  " + name + "\n"
      return [error_message]

    # everything is fine
    return []


  def __add_neuron(self, neuron):
    self.__idx_to_neuron[neuron.index] = neuron
    self.__name_to_neuron[neuron.name] = neuron


  def create_neural_connections(self, connection_parameters):
    # Delete existing neural connections
    self.__data_container.delete_models(list(self.__name_to_neural_connection.values()))

    if not connection_parameters:
      return []

    nc_gen = NeuralConnectionGenerator()
    new_neural_connections = list()

    for cp in connection_parameters:
      # Get the neurons we are supposed to connect
      src_neuron = self.__name_to_neuron.get(cp.src_neuron_name)
      tar_neuron = self.__name_to_neuron.get(cp.tar_neuron_name)
      if not src_neuron or not tar_neuron:
        continue
      # Create the name of the neural connection
      nc_name = src_neuron.name + " -> " + tar_neuron.name
      # Create a new neural connection and save it
      nc = nc_gen.create_neural_connection(nc_name, src_neuron.name, tar_neuron.name, src_neuron.p, tar_neuron.p, cp.weight)
      self.__name_to_neural_connection[nc_name] = nc
      new_neural_connections.append(nc)

    # Add the new connections to the data container
    self.__data_container.add_data(new_neural_connections)
    # No error messages
    return []
