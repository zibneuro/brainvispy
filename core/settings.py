class Settings:
  # Each neuron is represented by a sphere. This is its radius:
  neuron_sphere_radius = 3.0
  # A synaptic connection (between two neurons) is represented by a line with a cone at the end (arrow).
  # These are the paremeters.
  neural_connection_cone_length = 5.0
  neural_connection_cone_radius = 1.8
  # Each loop (connection from a neuron to itself) is represented by a circle. This is its radius:
  loop_radius = 6.0
  # When importing a neuron connectivity matrix (the one that defines which neuron is connected to which),
  # the neuron positions are determined randomly within the brain regions. The following parameter defines
  # the rough distance between neurons in the same brain region. Note that the current algorithm does not
  # guarantee that the neurons will have exactly this distance.
  inter_neuron_distance = 15
