# File formats

## Project files

The project files are saved in ASCII XML format containing all project information and links to the mesh files associated with the project. The format is easy to understand - save a project and have a look at the file.

## Connectivity matrices

The matrices are saved in a CSV format. There are two types of connectivity matrices: symmetric and asymmetric. In the following, both are explained using simple examples.

### Asymmetric

### Symmetric

Importing the matrix below will generate 4 neuron pairs: one for each A, B, C and D. Each neuron pair consists of two neurons which will be placed symmetrically in the specified brain region. The left 4x4 sub-matrix defines the ipsilateral connections (connecting neurons on the same side of the brain). In this example, the C neurons are connected to the D neurons on the same side of the brain by a connection with strength of -0.8. The second 4x4 sub-matrix defines the contralateral connections (connecting neurons on opposite brain sides). The column after the one containing the brain regions contains the threshold for each neuron (not used in the current software version).

![symmetric connectivity matrix](symmetric_connectivity_matrix.png "")
![imported symmetric connectivity matrix](symmetric_connectivity_matrix_imported.png "")
