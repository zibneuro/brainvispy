import os
from .listwidget import ListWidget
from core.modelview import Observer
from core.datacontainer import DataContainer
from PyQt5 import QtWidgets, QtCore, QtWidgets


#==================================================================================================
# DataPanel =======================================================================================
#==================================================================================================
class DataPanel(Observer):
  """This is the dock widget for the loaded models. It will have: (1) a line edit where the user
  can search for a model among the loaded ones, (2) a button to delete the selected models, (3) a
  list with the loaded models, (4) buttons to control the model visibility."""
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the input data container has the wrong type")

    self.__data_container = data_container
    self.__data_container.add_observer(self)

    # (1)
    self.__data_search = QtWidgets.QLineEdit()
    self.__data_search.textChanged.connect(self.__on_search_text_changed)
    # (2)
    self.__btn_delete_selected_models = QtWidgets.QPushButton("delete selected")
    self.__btn_delete_selected_models.clicked.connect(self.__on_delete_selected_models)
    self.__btn_delete_selected_models.setEnabled(False)
    # (3)
    self.__list_widget = ListWidget(data_container)
    # (4)
    btn_make_all_visible = QtWidgets.QPushButton("all")
    btn_make_all_visible.clicked.connect(self.__on_make_all_visible)
    btn_make_all_invisible = QtWidgets.QPushButton("none")
    btn_make_all_invisible.clicked.connect(self.__on_make_all_invisible)
    btn_invert_visibility = QtWidgets.QPushButton("invert")
    btn_invert_visibility.clicked.connect(self.__on_invert_visibility)
    self.__btn_selection_visibility = QtWidgets.QPushButton("selected")
    self.__btn_selection_visibility.clicked.connect(self.__on_make_selected_visible)
    self.__btn_selection_visibility.setEnabled(False)
    visibility_group_layout = QtWidgets.QHBoxLayout()
    visibility_group_layout.addWidget(btn_make_all_visible)
    visibility_group_layout.addWidget(btn_make_all_invisible)
    visibility_group_layout.addWidget(btn_invert_visibility)
    visibility_group_layout.addWidget(self.__btn_selection_visibility)
    visibility_group = QtWidgets.QGroupBox("visibility")
    visibility_group.setLayout(visibility_group_layout)

    # Put all the stuff in a box layout
    #dock_layout = QtWidgets.QVBoxLayout()
    dock_layout = QtWidgets.QGridLayout()
    dock_layout.addWidget(QtWidgets.QLabel("search:"), 0, 0, 1, -1)
    dock_layout.addWidget(self.__data_search, 1, 0, 1, -1)
    dock_layout.addWidget(QtWidgets.QLabel("loaded data:"), 2, 0, 1, -1)
    dock_layout.addWidget(self.__btn_delete_selected_models, 2, 1, 1, 1)
    dock_layout.addWidget(self.__list_widget.qt_list_widget, 3, 0, 1, -1)
    dock_layout.addWidget(visibility_group, 4, 0, 1, -1)
    # Group everything in a frame
    dock_frame = QtWidgets.QFrame()
    dock_frame.setLayout(dock_layout)
    # Create the dock widget
    self.dock_widget = QtWidgets.QDockWidget("data panel")
    self.dock_widget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
    self.dock_widget.setWidget(dock_frame)


  def observable_changed(self, change, data):
    if change == DataContainer.change_is_new_selection:
      self.__update_buttons_according_to_selection(data)


  def __update_buttons_according_to_selection(self, data):
    if len(data) > 0:
      self.__btn_delete_selected_models.setEnabled(True)
      self.__btn_selection_visibility.setEnabled(True)
    else:
      self.__btn_delete_selected_models.setEnabled(False)
      self.__btn_selection_visibility.setEnabled(False)


  def __on_search_text_changed(self, search_text):
    self.__list_widget.show_items_containing_text(search_text.lower())


  def __on_delete_selected_models(self):
    self.__data_container.delete_selected_models()
    

  def __on_make_all_visible(self):
    self.__list_widget.update_visibility(1)


  def __on_make_all_invisible(self):
    self.__list_widget.update_visibility(0)


  def __on_invert_visibility(self):
    self.__list_widget.update_visibility(-1)


  def __on_make_selected_visible(self):
    self.__list_widget.make_selected_visible()
