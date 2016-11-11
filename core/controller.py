from anatomy.neuron_generator import NeuronGenerator

class Controller:
  def __init__(self, data_container):
    self.__data_container = data_container
    self.__neuron_generator = NeuronGenerator()


  def generate_neurons(self, brain_regions):
    print("Yo, generating neurons ...")
    #neurons = self.__neuron_generator.generate_neurons(brain_regions)
    #self.__data_container.add_models(neurons)
