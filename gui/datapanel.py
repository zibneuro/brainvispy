import os
from .listwidget import ListWidget
from core.datacontainer import DataContainer
from PyQt5 import QtWidgets, QtCore, QtWidgets


#==================================================================================================
# DataPanel =======================================================================================
#==================================================================================================
class DataPanel:
  """This is the dock widget for the loaded files. It will have: (1) a line edit where the user can
  search for a file among the loaded ones, (2) a list with the loaded files, (3) buttons to control
  the object visibility and (4) buttons to control the selection of items"""
  def __init__(self, data_container):
    if not isinstance(data_container, DataContainer):
      raise TypeError("the input data container has the wrong type")

    # (1)
    self.__data_search = QtWidgets.QLineEdit()
    self.__data_search.textChanged.connect(self.__on_search_text_changed)
    # (2)
    self.__list_widget = ListWidget(data_container)
    # (3)
    make_all_visible_btn = QtWidgets.QPushButton("all")
    make_all_visible_btn.clicked.connect(self.__on_make_all_visible)
    make_all_invisible_btn = QtWidgets.QPushButton("none")
    make_all_invisible_btn.clicked.connect(self.__on_make_all_invisible)
    invert_visibility_btn = QtWidgets.QPushButton("invert")
    invert_visibility_btn.clicked.connect(self.__on_invert_visibility)
    selection_visibility_btn = QtWidgets.QPushButton("selected")
    selection_visibility_btn.clicked.connect(self.__on_make_selected_visible)
    btn_layout = QtWidgets.QHBoxLayout()
    #btn_layout.addWidget(QtWidgets.QLabel("make visible"))
    btn_layout.addWidget(make_all_visible_btn)
    btn_layout.addWidget(make_all_invisible_btn)
    btn_layout.addWidget(invert_visibility_btn)
    btn_layout.addWidget(selection_visibility_btn)
    btn_frame = QtWidgets.QGroupBox("visibility")
    btn_frame.setLayout(btn_layout)
    # (4)
    select_all_btn = QtWidgets.QPushButton("all")
    select_none_btn = QtWidgets.QPushButton("none")
    invert_selection_btn = QtWidgets.QPushButton("invert")
    selection_btns_layout = QtWidgets.QHBoxLayout()
    selection_btns_layout.addWidget(QtWidgets.QLabel("select"))
    selection_btns_layout.addWidget(select_all_btn)
    selection_btns_layout.addWidget(select_none_btn)
    selection_btns_layout.addWidget(invert_selection_btn)
    selection_btns_group = QtWidgets.QGroupBox()
    selection_btns_group.setLayout(selection_btns_layout)

    # Put all the stuff in a box layout
    dock_layout = QtWidgets.QVBoxLayout()
    dock_layout.addWidget(QtWidgets.QLabel("search:"))
    dock_layout.addWidget(self.__data_search)
    dock_layout.addWidget(QtWidgets.QLabel("loaded data:"))
    dock_layout.addWidget(self.__list_widget.qt_list_widget)
    dock_layout.addWidget(btn_frame)
    #dock_layout.addWidget(selection_btns_group)
    # Group everything in a frame
    dock_frame = QtWidgets.QFrame()
    dock_frame.setLayout(dock_layout)
    # Create the dock widget
    self.dock_widget = QtWidgets.QDockWidget("data panel")
    self.dock_widget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
    self.dock_widget.setWidget(dock_frame)


  def __on_search_text_changed(self, search_text):
    self.__list_widget.show_items_containing_text(search_text.lower())


  def __on_make_all_visible(self):
    self.__list_widget.update_visibility(1)


  def __on_make_all_invisible(self):
    self.__list_widget.update_visibility(0)


  def __on_invert_visibility(self):
    self.__list_widget.update_visibility(-1)


  def __on_make_selected_visible(self):
    self.__list_widget.make_selected_visible()
