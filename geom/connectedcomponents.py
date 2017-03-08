import vtk

class ConnectedComponents:
  def extract_connected_components(self, mesh):
    if not isinstance(mesh, vtk.vtkPolyData):
      # Maybe 'mesh' has a VtkPolyModel as a visual representation that has a vtkPolyData
      try:
        mesh = mesh.visual_representation.vtk_poly_data
      except AttributeError:
        raise

    cc_filter = vtk.vtkPolyDataConnectivityFilter()
    cc_filter.SetInputData(mesh)
    cc_filter.SetExtractionModeToSpecifiedRegions()
    
    components = list()
    idx = 0
    
    while True:
      cc_filter.AddSpecifiedRegion(idx)
      cc_filter.Update()

      # Make sure we got something
      if cc_filter.GetOutput().GetNumberOfCells() <= 0:
        break

      cleaner = vtk.vtkCleanPolyData()
      cleaner.SetInputData(cc_filter.GetOutput())
      cleaner.Update()
      
      components.append(cleaner.GetOutput())
      cc_filter.DeleteSpecifiedRegion(idx)
      idx += 1

    return components


  def sort_meshes(self, axis, mesh0, mesh1):
    c0 = 0
    for i in range(mesh0.GetNumberOfPoints()):
      c0 += mesh0.GetPoint(i)[axis]
    c0 /= mesh0.GetNumberOfPoints()

    c1 = 0
    for i in range(mesh1.GetNumberOfPoints()):
      c1 += mesh1.GetPoint(i)[axis]
    c1 /= mesh1.GetNumberOfPoints()

    if c0 < c1:
      return [mesh0, mesh1]

    return [mesh1, mesh0]
