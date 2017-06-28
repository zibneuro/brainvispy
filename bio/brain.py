from generators.symmetricpoints import SymmetricPointsGenerator
from core.settings import Settings
from core.datacontainer import DataContainer
from bio.brainregion import BrainRegion
from bio.neuron import Neuron
from bio.neuralconnection import NeuralConnection
from vis.visneuralconnection import VisNeuralConnection
from vis.visneuron import VisNeuron

class Brain:
  def __init__(self, data_container):
    self.__name_to_brain_region = dict()
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
      del self.__name_to_neuron[neuron.name]
    except KeyError:
      pass


  def create_neurons(self, neuron_parameters, progress_bar = None):
    """Create neurons according to the specifications in 'neuron_parameters'. Modifies the data container
    by adding the new neurons to it. Thus, all observers of the data container get notified about the new
    data. Returns a list with error messages that tell what went wrong or an empty list if everything is
    fine. For example, an error message lists the names of the brain regions that are supposed to
    contain neurons but are not loaded yet."""
    try:
      progress_bar.init(0, 2, "Generating the Neurons:")
      progress_bar.set_progress(0)
    except:
      pass

    # Delete the existing neurons
    self.__data_container.delete_models(list(self.__name_to_neuron.values()))

    if not neuron_parameters:
      return []

    brain_region_to_neurons = dict()
    new_neurons = list()

    missing_brain_regions = set()

    for np in neuron_parameters:
      try: # to get the neuron's position
        p = np.position
      except AttributeError:
        # No position is provided
        try: # to get a brain region name
          brain_region_name = np.brain_region_name
        except AttributeError:
          # Neither position nor brain region => cannot create the neuron
          continue
        else:
          # Make sure the desired brain region exists
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
        neuron = self.__create_neuron(np.name, p, np.threshold)
        self.__add_neuron(neuron)
        new_neurons.append(neuron)

    try:
      progress_bar.init(1, len(brain_region_to_neurons), "Generating the Neurons:")
      counter = 1
    except:
      pass

    # Now generate the neurons inside the brain regions
    for brain_region in brain_region_to_neurons:
      try:
        progress_bar.set_progress(counter)
        counter += 1
      except:
        pass

      # Get the neuron parameters
      neuron_parameters = brain_region_to_neurons[brain_region]
      # This is the guy who generates the random neuron positions
      points_generator = SymmetricPointsGenerator(brain_region, axis=0)

      for params in neuron_parameters:
        # Mirrored or "standard" neuron
        if params.brain_side and params.brain_side[0].lower() == "m": # "m" for mirrored
          p1, p2 = points_generator.generate_mirrored_points_inside_mesh()
          n1 = self.__create_neuron(params.name + "_L", p1, params.threshold)
          n2 = self.__create_neuron(params.name + "_R", p2, params.threshold)
          self.__add_neuron(n1)
          self.__add_neuron(n2)
          new_neurons.append(n1)
          new_neurons.append(n2)
        else:
          neuron_position = points_generator.generate_point_inside_mesh(params.brain_side)
          neuron = self.__create_neuron(params.name, neuron_position, params.threshold)
          self.__add_neuron(neuron)
          new_neurons.append(neuron)

    try:
      progress_bar.done()
    except:
      pass

    self.__data_container.add_data(new_neurons)

    # Inform the user about missing brain regions
    if missing_brain_regions:
      error_message = "Missing brain region(s):\n"
      for name in missing_brain_regions:
        error_message += "  " + name + "\n"
      return [error_message]

    # everything is fine
    return []


  def __create_neuron(self, name, p, threshold):
    vis_neuron = VisNeuron(name, p, Settings.neuron_sphere_radius)
    return Neuron(name, p[0], p[1], p[2], threshold, vis_neuron)


  def __add_neuron(self, neuron):
    self.__name_to_neuron[neuron.name] = neuron


  def create_neural_connections(self, connection_parameters):
    """Create neural connections according to the specifications in 'connection_parameters'. Modifies the
    data container by adding the new connections to it. Thus, all observers of the data container get
    notified about the new data. Returns a list with error messages that tell what went wrong or an empty
    list if everything is fine. The current version always returns an empty list (no errors can occur)."""
    # Delete existing neural connections
    self.__data_container.delete_models(list(self.__name_to_neural_connection.values()))

    if not connection_parameters:
      return []

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
      nc = self.__create_neural_connection(nc_name, src_neuron.name, tar_neuron.name, src_neuron.p, tar_neuron.p, cp.weight)
      self.__name_to_neural_connection[nc_name] = nc
      new_neural_connections.append(nc)

    # Add the new connections to the data container
    self.__data_container.add_data(new_neural_connections)
    # No error messages
    return []


  def __create_neural_connection(self, name, src_neuron_name, tar_neuron_name, src_pos, tar_pos, weight):
    vis_rep = VisNeuralConnection(name, src_pos, tar_pos, src_neuron_name == tar_neuron_name)
    return NeuralConnection(name, src_neuron_name, tar_neuron_name, weight, vis_rep)
