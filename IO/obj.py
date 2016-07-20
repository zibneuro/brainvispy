import vtk

class OBJReader:
  """This guy can load triangular meshes saved as OBJ. It can only read the triangles, i.e., no normals,
  textures, materials etc..."""
  def __init__(self):
    self.file_name = ""


  def SetFileName(self, file_name):
    """The file you want to load."""
    self.file_name = str(file_name)

  
  def Update(self):
    """Does nothing. It is included in order to use the object as a VTK reader (they all have an Update method)."""
    pass


  def GetOutput(self):
    """Reads the file (the one whose name was provided to the SetFileName method) and returns a vtkPolyData object."""
    try:
      with open(self.file_name, "r") as obj_file:
        return self.__load_content(obj_file)
    except Exception as error:
      print("Error in OBJReader.GetOutput(): " + str(error))
      return vtk.vtkPolyData()


  def __load_content(self, obj_file):
    """This method loads the content from the provided 'obj_file', builds a vtkPolyData object and returns it.
    Note that 'obj_file' has to be a ready-to-read-from file and not a file name."""
    vtk_points = vtk.vtkPoints()
    vtk_trias = vtk.vtkCellArray()

    # Loop over all lines in the file
    for line in obj_file:
      # Remove leading white spaces from the line
      line = line.lstrip()

      try:
        # What kind of line do we have?
        if line.startswith("v "): # vertex coordinates
          self.__insert_vertex_coordinates(line, vtk_points)
        elif line.startswith("f "): # triangle (vertex ids)
          self.__insert_triangle(line, vtk_trias)
      except:
        return vtk.vtkPolyData()

    # Now that we are done with the file, build the vtkPolyData object and return it
    vtk_poly_data = vtk.vtkPolyData()
    vtk_poly_data.SetPoints(vtk_points)
    vtk_poly_data.SetPolys(vtk_trias)

    return vtk_poly_data


  def __insert_vertex_coordinates(self, vertex_line, vtk_points):
    p = list()
    # Get the first three numbers in 'vertex_line' and save them in 'p'
    for number in vertex_line.split():
      try:
        p.append(float(number))
        # Return if we got three numbers
        if len(p) == 3:
          vtk_points.InsertNextPoint(p[0], p[1], p[2])
          return
      except ValueError:
        pass # this is fine - it could mean that we got the 'v' at the beginning of the line
      except Exception as err:
        print("Error in OBJReader.__insert_vertex_coordinates(): " + str(err))
        raise err

    # Bad if we got here
    raise ValueError("Error in OBJReader.__insert_vertex_coordinates(): invalid vertex line: " + vertex_line)


  def __insert_triangle(self, triangle_line, vtk_cells):
    tria = list()
    # Get the first three ids in 'triangle_line' and save them in 'tria'
    for id_group in triangle_line.split():
      # 'id_group' is a tring of the form v1/vt1/vn1, where the v1, vt1 and vn1 are numbers. We want v1 only.
      # vt1, vn1 or some of the / may be missing.
      try:
        # Get v1 as a number
        tria.append(int(id_group.split("/")[0]) - 1) # minus 1 since in OBJ the ids start at 1
        # Return if we got three ids
        if len(tria) == 3:
          ids = vtk.vtkIdList()
          ids.InsertNextId(tria[0])
          ids.InsertNextId(tria[1])
          ids.InsertNextId(tria[2])
          vtk_cells.InsertNextCell(ids)
          return
      except ValueError:
        pass # this is fine - it could mean that we got the 'f' at the beginning of the line
      except Exception as err:
        print("Error in OBJReader.__insert_triangle(): " + str(err))
        raise err
    
    # Bad if we got here
    raise ValueError("Error in OBJReader.__insert_triangle(): invalid triangle line: " + triangle_line)
