# Understanding the Code

## Main Strategy

The software is roughly based on the observer software design pattern. 
There is one main object of type [DataContainer](../core/datacontainer.py) that stores all the data, which is loaded in the program. The data items, we call them models, are the brain regions (represented by meshes), the neurons (represented by spheres) and the synaptic connections between the neurons (represented by arrows). Other classes (e.g., GUI elements) that operate on the models register themselves as observer of the data container and get notified when it is modified. For example, if a new mesh is loaded, all observers get notified that new data has arrived.

There is one additional central class, the [Controller](../core/controller.py), that manages user input and modifies the data container accordingly which, in turn, notifies its observers about the changes.

## Where to Start Reading the Code

Start with [main.py](../main.py) and move on to [mainwin.py](../gui/mainwin.py).

### GUI

The main GUI window consists of three parts: the [data panel](../gui/datapanel.py) on the left (showing the names of the loaded brain regions), the [3D viewer](../gui/vtkwidget.py) in the middle (showing the 3D content) and the [properties panel](../gui/propspanel.py) on the right (that displays properties of the selected models, like color, transparency, ...).
