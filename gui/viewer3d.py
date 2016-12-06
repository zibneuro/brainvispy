import vtk
from vis.vtkpoly import VtkPolyModel
from gui.vtkwidget import VtkWidget
from core.datacontainer import DataContainer

class Viewer3d(VtkWidget):
  def __init__(self, parent_qt_frame, data_container, progress_bar):
    super().__init__(parent_qt_frame, progress_bar)
    # Register itself as an observer to the data_container
    self.__data_container = data_container
    self.__data_container.add_observer(self)

    self.__create_line_segment()


  def __create_line_segment(self):
    # This line can be positioned in 3D to indicate a connection between neurons
    vtk_line_points = vtk.vtkPoints()
    vtk_line_points.SetNumberOfPoints(2)
    vtk_line_points.SetPoint(0, 0.0, 0.0, 0.0)
    vtk_line_points.SetPoint(1, 0.0, 0.0, 0.0)

    vtk_line = vtk.vtkCellArray()
    vtk_line.InsertNextCell(2, [0, 1])

    vtk_poly_data = vtk.vtkPolyData()
    vtk_poly_data.SetPoints(vtk_line_points)
    vtk_poly_data.SetLines(vtk_line)

    self.__line_segment = VtkPolyModel(vtk_poly_data, "line segment")
    self.__line_segment.visibility_off()
    self.add_actor(self.__line_segment.prop3d)


  def observable_changed(self, change, data):
    self.reset_clipping_range()


  def show_edge(self, a, b):
    self.__line_segment.set_point(0, a)
    self.__line_segment.set_point(1, b)
    self.__line_segment.vtk_poly_data.Modified()
    self.__line_segment.visibility_on()
    self.render()


  def hide_edge(self):
    self.__line_segment.visibility_off()
    self.render()
