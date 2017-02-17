from generators.neurongenerator import NeuronGenerator
from generators.neuralconnectiongenerator import NeuralConnectionGenerator
from core.datacontainer import DataContainer
from bio.neuron import Neuron

class Brain:
  def __init__(self, data_container):
    self.__id_to_neuron = dict()
    data_container.add_observer(self)
    self.__name_to_neuron = dict()
    self.__name_to_brain_region = dict()


  def observable_changed(self, change, data):
    # Decide what to do depending on what changed
    if change == DataContainer.change_is_deleted_models:
      self.__delete_neurons(data)


  def __delete_neurons(self, data):
    for neuron in data:
      if not isinstance(neuron, Neuron):
        continue
      try:
        del self.__id_to_neuron[neuron.index]
      except KeyError:
        pass


  def create_neurons(self, neuron_parameters):
    neurons = list()
    neuro_gen = NeuronGenerator()
    brain_region_to_neurons = dict()

    for n in neuron_parameters:
      # If we already have that neuron, just update it
      if n.name in self.__name_to_neuron:
        self.__name_to_neuron[n.name].set_threshold(n.threshold)
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
            if brain_region_name not in brain_region_to_neurons:
              brain_region_to_neurons[brain_region_name] = list()
            brain_region_to_neurons[brain_region_name].apend(n)
        else:
          # We can create the neuron
          neurons.append(neuron_gen.create_neuron(n.name, p[0], p[1], p[2], n.threshold))

    # Now generate the guys inside the provided brain regions
  
    # Setup the ids of the new neurons
    num_neurons = len(self.__name_to_neuron)
    for n in neurons:
      n.set_index(num_neurons)
      num_neurons += 1
    

  def create_neuron(self, name, index, position, threshold, sphere_radius):
    # Make sure that the neuron indices are uniue
    if index in self.__id_to_neuron:
      return None

    # Generate the neuron
    neuro_gen = NeuronGenerator()
    neuron = neuro_gen.create_neuron(name, index, position, threshold, sphere_radius)
    # Save it in the (index, neuron) dictionary
    self.__id_to_neuron[index] = neuron
    return neuron


  def create_neurons(self, number_of_neurons_per_region, brain_regions, threshold_potential_range):
    neuro_gen = NeuronGenerator()
    # Generate new neurons in the provided brain region
    new_neurons = neuro_gen.generate_random_neurons(number_of_neurons_per_region, brain_regions, threshold_potential_range)

    # Set the indices of the new neurons and save them
    for neuron in new_neurons:
      neuron_id = self.__generate_valid_neuron_id()
      neuron.set_index(neuron_id)
      neuron.set_name("neuron " + str(neuron_id))
      self.__id_to_neuron[neuron.index] = neuron

    return new_neurons


  def create_neural_connection(self, name, neuron_indices, weight, cylinder_radius):
    n1 = self.get_neuron(neuron_indices[0])
    n2 = self.get_neuron(neuron_indices[1])
    if (not n1) or (not n2) or (n1 == n2):
      return None

    con_gen = NeuralConnectionGenerator()
    return con_gen.create_neural_connection(name, n1, n2, weight, cylinder_radius)


  def connect_neurons(self, n1, n2):
    con_gen = NeuralConnectionGenerator()
    return con_gen.connect_neurons(n1.name + " -> " + n2.name, n1, n2)


  def get_neuron(self, neuron_id):
    return self.__id_to_neuron.get(neuron_id)


  def __generate_valid_neuron_id(self):
    neuron_id = 0
    while neuron_id in self.__id_to_neuron:
      neuron_id += 1
    return neuron_id    


  @property
  def coordinates(self):
    return self.__coords


  @property
  def threshold(self):
    return self.__threshold
