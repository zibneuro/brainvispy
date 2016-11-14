from anatomy.neurogen import NeuronGenerator
from anatomy.region import BrainRegion

class Controller:
  def __init__(self, data_container):
    self.__data_container = data_container
    self.__neuron_generator = NeuronGenerator()


  def generate_neurons(self, brain_regions):
    selected_brain_regions = list()
    for model in self.__data_container.get_selected_models():
      if isinstance(model, BrainRegion):
        selected_brain_regions.append(model)
    
    neurons = self.__neuron_generator.generate_neurons(selected_brain_regions)
    #self.__data_container.add_models(neurons)
