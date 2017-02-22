from generators.neurongenerator import NeuronGenerator
from generators.neuralconnectiongenerator import NeuralConnectionGenerator
from generators.randompoints import RandomPointsGenerator
from core.datacontainer import DataContainer
from bio.brainregion import BrainRegion
from bio.neuron import Neuron

class Brain:
  def __init__(self, data_container):
    self.__idx_to_neuron = dict()
    self.__name_to_neuron = dict()
    self.__name_to_neural_connection = dict()
    self.__name_to_brain_region = dict()
    data_container.add_observer(self)


  def observable_changed(self, change, data):
    # Decide what to do depending on what changed
    if change == DataContainer.change_is_new_data:
      self.__add_brain_regions(data)
    elif change == DataContainer.change_is_deleted_models:
      self.__delete_neurons(data)


  def __delete_neurons(self, data):
    for neuron in data:
      if not isinstance(neuron, Neuron):
        continue
      try:
        del self.__idx_to_neuron[neuron.index]
      except KeyError:
        pass

      try:
        del self.__name_to_neuron[neuron.name]
      except KeyError:
        pass


  def create_neurons(self, neuron_parameters):
    brain_region_name_to_neurons = dict()
    neuro_gen = NeuronGenerator()
    new_neurons = list()

    for n in neuron_parameters:
      # If we already have that neuron, just update it
      if n.name in self.__name_to_neuron or n.index in self.__idx_to_neuron:
        self.__update_neuron(n)
      else:
        # We have to create a new neuron
        try: # to get its position
          p = n.position
        except AttributeError:
          # No position is provided
          try: # to get a brain region name
            brain_region_name = n.brain_region_name
          except AttributeError:
            # Neither position no brain region => cannot create the neuron
            pass
          else:
            # We have the brain region that should contain the neuron. Save it for later generation
            if brain_region_name not in brain_region_name_to_neurons:
              brain_region_name_to_neurons[brain_region_name] = list()
            brain_region_name_to_neurons[brain_region_name].append(n)
        else:
          # We got position -> create the neuron
          neuron = neuro_gen.create_neuron(n.name, n.index, p, n.threshold)
          self.__add_neuron(neuron)
          new_neurons.append(neuron)

    # Now generate the neurons inside the provided brain regions
    for brain_region_name in brain_region_name_to_neurons:
      try: # to get a brain region
        brain_region = self.__name_to_brain_region[brain_region_name]
      except KeyError:
        continue

      # Get the neuron parameters
      neuron_parameters = brain_region_name_to_neurons[brain_region_name]
      # Generate the neuron positions
      rnd_pts_gen = RandomPointsGenerator(brain_region)
      neuron_positions = rnd_pts_gen.generate_points_inside_mesh(len(neuron_parameters))

      for i in range(len(neuron_parameters)):
        np = neuron_parameters[i]
        neuron = neuro_gen.create_neuron(np.name, np.index, neuron_positions[i], np.threshold)
        self.__add_neuron(neuron)
        new_neurons.append(neuron)

    return new_neurons


  def create_neural_connections(self, connection_parameters):
    nc_gen = NeuralConnectionGenerator()
    neural_connections = list()
    
    for cp in connection_parameters:
      # No connections from a neuron to itself
      if cp.src_neuron_name == cp.tar_neuron_name:
        continue
      # Get the neurons we are supposed to connect
      src_neuron = self.__get_neuron_by_name(cp.src_neuron_name)
      tar_neuron = self.__get_neuron_by_name(cp.tar_neuron_name)
      if not src_neuron or not tar_neuron:
        continue
      # Create the name of the neural connection
      nc_name = self.__compute_neural_connection_name(src_neuron.name, tar_neuron.name)
      # If there already is a neural connection with this name - delete it
      try:
        del self.__name_to_neural_connection[nc_name]
      except KeyError:
        pass
      # Create a new neural connection and save it
      nc = nc_gen.create_neural_connection(nc_name, src_neuron.name, tar_neuron.name, src_neuron.p, tar_neuron.p, cp.weight)
      self.__name_to_neural_connection[nc_name] = nc
      neural_connections.append(nc)

    # Return the neural connections
    return neural_connections


  def __compute_neural_connection_name(self, src_neuron_name, tar_neuron_name):
    return src_neuron_name + " -> " + tar_neuron_name


  def __add_neuron(self, neuron):
    self.__idx_to_neuron[neuron.index] = neuron
    self.__name_to_neuron[neuron.name] = neuron


  def __update_neuron(self, neuron_parameters):
    neuron = self.__get_neuron(neuron_parameters.index, neuron_parameters.name)
    if not neuron:
      return

    self.__delete_neuron(neuron_parameters.index, neuron_parameters.name)
    
    neuron.set_index(neuron_parameters.index)
    neuron.set_name(neuron_parameters.name)

    self.__idx_to_neuron[neuron.index] = neuron
    self.__name_to_neuron[neuron.name] = neuron
    
    print("updated " + neuron.name + " " + str(neuron.index))


  def __get_neuron(self, index, name):
    neuron = self.__idx_to_neuron.get(index)
    if not neuron:
      neuron = self.__name_to_neuron.get(name)
    return neuron


  def __get_neuron_by_name(self, name):
    return self.__name_to_neuron.get(name)


  def __delete_neuron(self, index, name):
    try:
      del self.__idx_to_neuron[index]
    except KeyError:
      pass

    try:
      del self.__name_to_neuron[name]
    except KeyError:
      pass


  def __add_brain_regions(self, data):
    for model in data:
      if isinstance(model, BrainRegion):
        self.__name_to_brain_region[model.name] = model
