# Understanding the Code

## Main Strategy

The software is roughly based on the observer software design pattern. 
There is one main object of type [DataContainer](../core/datacontainer.py) that stores all the data, which is loaded in the program. The data items, we call them models, are the brain regions (represented by meshes), the neurons (represented by spheres) and the synaptic connections between the neurons (represented by arrows). All other classes (e.g., IO objects, GUI elements, ...) that operate on the models register themselves as observer of the data container and get notified when it is modified (get changed). For example, if a new mesh is loaded, all observers get notified that new data has arrived.

There is one additional central class, the [Controller](../core/controller.py), that manages user input and modifies the data container accordingly which, in turn, notifies its observers about the changes.

## Where to Start Reading the Code

Start with the [main.py](../main.py) and move on to [mainwin.py](../gui/mainwin.py).
