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
    brain_region_name_to_neurons = dict()
    neuro_gen = NeuronGenerator()
    neuron_index = len(self.__name_to_neuron)
    new_neurons = list()

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
            if brain_region_name not in brain_region_name_to_neurons:
              brain_region_name_to_neurons[brain_region_name] = list()
            brain_region_name_to_neurons[brain_region_name].append(n)
        else:
          # We got position -> create the neuron
          neuron = neuro_gen.create_neuron(n.name, neuron_index, p, n.threshold)
          neuron_index += 1
          self.__name_to_neuron[neuron.name] = neuron
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
        neuron = neuro_gen.create_neuron(np.name, neuron_index, neuron_positions[i], np.threshold)
        neuron_index += 1
        self.__name_to_neuron[neuron.name] = neuron
        new_neurons.append(neuron)

    return new_neurons

#  def create_neural_connection(self, name, neuron_indices, weight, cylinder_radius):
#    n1 = self.get_neuron(neuron_indices[0])
#    n2 = self.get_neuron(neuron_indices[1])
#    if (not n1) or (not n2) or (n1 == n2):
#      return None

#    con_gen = NeuralConnectionGenerator()
#    return con_gen.create_neural_connection(name, n1, n2, weight, cylinder_radius)


  def get_neuron(self, neuron_id):
    return self.__id_to_neuron.get(neuron_id)


  def __generate_valid_neuron_id(self):
    neuron_id = 0
    while neuron_id in self.__id_to_neuron:
      neuron_id += 1
    return neuron_id    
