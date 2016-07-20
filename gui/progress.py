from core.progress import ProgressBar
from PyQt5 import QtWidgets, QtCore

#==================================================================================================
# FileLoadProgressBar =============================================================================
#==================================================================================================
class ProgressBarFrame(ProgressBar):
  """Derived from ProgressBar, this is a particular implementation which shows a QProgressBar in
  its own frame."""
  def __init__(self, parent_window, qt_app):
    self.__parent_window = parent_window
    self.__qt_app = qt_app
    
    # The guy who indicates the progress
    self.__progress_bar = QtWidgets.QProgressBar()
    # The guy who explains what is going on
    self.__description_label = QtWidgets.QLabel("")

    # The layout
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(self.__description_label)
    layout.addWidget(self.__progress_bar)
    # The window to be shown
    self.__dialog = QtWidgets.QFrame(self.__parent_window, QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint)
    self.__dialog.setLayout(layout)


  def init(self, range_min, range_max, description = None):
    """Inherited from parent class."""
    self.__progress_bar.setRange(range_min, range_max)
    if description:
      self.__description_label.setText(description)

    # Compute the shape of this window:
    # First, get the shape of the parent window
    parent_rect = self.__parent_window.geometry()
    # Compute the width and height of this window
    width_frac = 0.6
    width = width_frac*parent_rect.width()
    height = 60
    # Compute the left and top coordinates of this window
    left = parent_rect.left() + 0.5*(1.0 - width_frac)*parent_rect.width()
    top = parent_rect.top() + 0.5*parent_rect.height() - 0.5*height

    self.__qt_app.processEvents()
    self.__dialog.setGeometry(left, top, width, height)
    self.__dialog.show()
    self.__qt_app.processEvents()


  def set_progress(self, k):
    """Inherited from parent class."""
    self.__progress_bar.setValue(k)
    self.__dialog.repaint()
    self.__qt_app.processEvents()


  def done(self):
    """Inherited from parent class."""
    self.__dialog.close()
    self.__description_label.setText("")
