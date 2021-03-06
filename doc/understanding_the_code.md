# Understanding the code

## Main strategy

The software is roughly based on the observer software design pattern. There is one main object of type [DataContainer](../core/datacontainer.py) that stores all the data, which is loaded in the program. The data items, we call them models, are the brain regions (represented by meshes), the neurons (represented by spheres) and the synaptic connections between the neurons (represented by arrows). Other classes (e.g., GUI elements) that operate on the models register themselves as observer of the data container and get notified when it is modified. For example, if a new mesh is loaded, all observers get notified that new data has arrived. The following diagram provides an illustration of the main classes and how they interact.

<img src="diagram/diagram.png" width="600"/>

## Module and class description

In the following, we briefly discuss the most important modules and classes of the project.

### IO

The [ProjectIO](../IO/project.py) is responsible for loading brain regions (meshes in OBJ or PLY format - better use PLY) as well as for opening/saving project files. All meshes are added to the data container which notifies its observers about the new data items. The information defining the neurons and neural connections is parsed by this class and passed to the [Brain](../bio/brain.py) class which creates the objects and adds them to the data container. The project files are saved in ASCII XML format containing all project information and links to the mesh files associated with the project.

The [ConnectivityMatrixIO](../IO/conmat.py) is responsible for loading connectivity matrices (from CSV files) which define the neurons and the synaptic connections between neurons. Note that importing the same connectivity matrix multiple times leads to different neuron positions since they are generated randomly.

The file formats used in this project are described [here](./file_formats.md).

### bio

The [Brain](../bio/brain.py) class creates the neurons and neural connections and adds them to the data container. The [BrainRegion](../bio/brainregion.py), [Neuron](../bio/neuron.py) and [NeuralConnection](../bio/neuralconnection.py) store information specific to the corresponding entity and a reference to an appropriate visual representation (see **vis** module) which is rendered in the 3D viewer [VtkWidget](../gui/vtkwidget.py).

### core

The main classes in this module are the [DataContainer](../core/datacontainer.py) (explained above) and the [Controller](../core/controller.py). The [Controller](../core/controller.py) manages user input from the 3D viewer [VtkWidget](../gui/vtkwidget.py) and modifies the data container accordingly which, in turn, notifies its observers about the changes.

### generators

The [SymmetricPointsGenerator](../generators/symmetricpoints.py) is the one that generates random points inside the meshes. It can either generate single points or point pairs consisting of a point and a copy of it mirrored along the x, y or z axis. This class is used by the [Brain](../bio/brain.py) class to embed the neurons in the brain regions. The [UniformPointCloud](../generators/uniformpointcloud.py) is used by the [SymmetricPointsGenerator](../generators/symmetricpoints.py) to create the points according to a random distribution in which no two points are too close to each other (similar to blue noise).

### gui

The [MainWindow](../gui/mainwin.py) consists of three parts: the [data panel](../gui/datapanel.py) on the left (consisting of the search field and the list with the names of the loaded brain regions), the 3D viewer [VtkWidget](../gui/vtkwidget.py) in the middle (showing the 3D content) and the [properties panel](../gui/propspanel.py) on the right (that displays properties of the selected models, like color, transparency, ...).

Furthermore, this module contains specialized GUI classes that display the properties of [BrainRegion](../bio/brainregion.py), [Neuron](../bio/neuron.py) and [NeuralConnection](../bio/neuralconnection.py).

### vis

[VtkPolyModel](../vis/vtkpoly.py) and [VtkVolumeModel](../vis/vtkvol.py) are wrappers for the VTK-based visualization and representation of polygonal and volumetric data sets (the latter are currently not used). Furthermore, this module contains specialized classes to display [BrainRegion](../bio/brainregion.py), [Neuron](../bio/neuron.py) and [NeuralConnection](../bio/neuralconnection.py) in the 3D viewer.

## Where to start reading the code?

Start with [main.py](../main.py) and move on to [mainwin.py](../gui/mainwin.py).

