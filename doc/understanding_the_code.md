# Understanding the code

## Main strategy

The software is roughly based on the observer software design pattern. 
There is one main object of type [DataContainer](../core/datacontainer.py) that stores all the data, which is loaded in the program. The data items, we call them models, are the brain regions (represented by meshes), the neurons (represented by spheres) and the synaptic connections between the neurons (represented by arrows). Other classes (e.g., GUI elements) that operate on the models register themselves as observer of the data container and get notified when it is modified. For example, if a new mesh is loaded, all observers get notified that new data has arrived.

There is one additional central class, the [Controller](../core/controller.py), that manages user input from the 3D viewer and modifies the data container accordingly which, in turn, notifies its observers about the changes.

## Where to start reading the code?

Start with [main.py](../main.py) and move on to [mainwin.py](../gui/mainwin.py).

## Module and class description

In the following, we briefly discuss the most important modules and classes of the project.

### IO

The [ProjectIO](../IO/project.py) is responsible for loading brain regions (meshes in OBJ or PLY format - better use PLY) as well as for opening/saving project files. All meshes are added to the data container which notifies its observers about the new data items. The neurons and neural connections are created by the [Brain](../bio/brain.py) object which adds them to the data container which, again, notifies its observer about the new data. The project files are saved in ASCII XML format containing all project information and links to the mesh files associated with the project.

The [ConnectivityMatrixIO](../IO/conmat.py) is responsible for parsing connectivity matrices which define the synaptic connections between neurons as well as their strength. Note that importing the same connectivity matrix multiple times leads to different neuron positions since they are generated randomly.

### bio

The [Brain](../bio/brain.py) class creates the neurons and neural connections and adds them to the data container.

The [BrainRegion](../bio/brainregion.py), [Neuron](../bio/neuron.py) and [NeuralConnection](../bio/neuralconnection.py) store information specific to the corresponding entity and a reference to an appropriate visual representation which is rendered in the 3D viewer.

### gui

The main GUI window consists of three parts: the [data panel](../gui/datapanel.py) on the left (showing the names of the loaded brain regions), the [3D viewer](../gui/vtkwidget.py) in the middle (showing the 3D content) and the [properties panel](../gui/propspanel.py) on the right (that displays properties of the selected models, like color, transparency, ...).

