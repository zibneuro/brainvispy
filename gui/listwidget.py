from vis.vtkvol import VtkVolumeModel
from core.modelview import Observer
from core.datacontainer import DataContainer
from PyQt5 import QtCore, QtWidgets

#============================================================================================================
# ListWidgetItem ============================================================================================
#============================================================================================================
class ListWidgetItem(QtWidgets.QListWidgetItem):
  def __init__(self, model):
    super().__init__(model.name)

    self.model = model
    self.is_hidden = False
    self.setSelected(False)

  def update_model_visibility(self):
    if self.__is_checked(): self.model.visibility_on()
    else: self.model.visibility_off()

  def __is_checked(self):
    return self.checkState() == QtCore.Qt.Checked

  def set_checked(self):
    if not self.__is_checked(): self.setCheckState(QtCore.Qt.Checked)
    self.model.visibility_on()

  def set_unchecked(self):
    if self.__is_checked(): self.setCheckState(QtCore.Qt.Unchecked)
    self.model.visibility_off()

  def toggle_check_state(self):
    if self.__is_checked():
      self.set_unchecked()
    else:
      self.set_checked()


#============================================================================================================
# ListWidget ================================================================================================
#============================================================================================================
class ListWidget(Observer):
  def __init__(self, data_container):
    self.__data_container = data_container
    # Make sure that the data container has the right type
    if not isinstance(self.__data_container, DataContainer):
      raise TypeError("the data container has the wrong type")
    # Register itself as an observer to the data_container
    self.__data_container.add_observer(self)

    self.__model_to_item = dict()
    self.__ordered_items = list()
    self.__model_to_selected_item = dict()

    # The following ones are used in some of the callbacks
    self.__update_data_container_visibility = True
    self.__ignore_selection_callback = False

    self.__qt_list_widget = QtWidgets.QListWidget()
    self.__qt_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    self.__qt_list_widget.itemSelectionChanged.connect(self.__on_item_selection)
    self.__qt_list_widget.itemChanged.connect(self.__on_item_changed)


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_data:
      self.__add_data_items(data)
    elif change == DataContainer.change_is_new_selection:
      self.__update_selection(data)


  def show_items_containing_text(self, text):
    """Loop over the loaded models and show only those which contain 'text' in the name."""
    # The following lines cause Qt to call __on_item_selection which we don't want
    ignore_selection_callback = self.__ignore_selection_callback
    self.__ignore_selection_callback = True
    
    # First, remove all elements from the list (don't call self.__qt_list_widget.clear() since the items are destroyed!)
    for i in range(self.__qt_list_widget.count()):
      self.__qt_list_widget.takeItem(0)

    # Insert all elements whose names contain 'text'
    for item in self.__ordered_items:
      if text in item.model.name.lower():
        item.is_hidden = False
        self.__qt_list_widget.insertItem(self.__qt_list_widget.count(), item)
      else:
        item.is_hidden = True

    # Mark all selected items as such in the QListWidget
    for selected_item in self.__model_to_selected_item.values():
      selected_item.setSelected(True)

    # Restore the state
    self.__ignore_selection_callback = ignore_selection_callback


  def update_visibility(self, state):
    """Updates the visibility of all items that are NOT hidden.
    state ==  1: make all visible
    state ==  0: make all invisible
    state == -1: switch visibility"""
    # The problem is that the following loop triggers __on_item_changed() which would cause the
    # data container to update its visibility in each iteration. It is better to do this once at the
    # end of this function. That's why the following two lines:
    update_data_container_visibility = self.__update_data_container_visibility # save the current state
    self.__update_data_container_visibility = False
    
    # Update all QList items but not the data container
    for item in self.__ordered_items:
      if item.is_hidden:
        continue
      
      if state == 1: item.set_checked()
      elif state == 0: item.set_unchecked()
      elif state == -1: item.toggle_check_state()

    # Now, update the data container visibility
    self.__update_data_container_visibility = update_data_container_visibility
    self.__data_container.update_visibility()


  def make_selected_visible(self):
    # The problem is that the following loop triggers __on_item_changed() which would cause the
    # data container to update its visibility in each iteration. It is better to do this once at the
    # end of this function. That's why the following two lines:
    update_data_container_visibility = self.__update_data_container_visibility # save the current state
    self.__update_data_container_visibility = False

    # Make all invisible
    for item in self.__ordered_items:
      item.set_unchecked()
    # Make only the selected visible
    for selected_model in self.__model_to_selected_item.values():
      selected_model.set_checked()

    # Now, update the data container visibility
    self.__update_data_container_visibility = update_data_container_visibility
    self.__data_container.update_visibility()


  def __on_item_selection(self):
    if self.__ignore_selection_callback:
      return
    
    selected_models = list()
    
    # Collect the models selected by the user
    for item in self.__qt_list_widget.selectedItems():
        selected_models.append(item.model)

    # If the user holds the ctrl. key, add the hidden selected items to the current ones
    if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
      for sel_item in self.__model_to_selected_item.values():
        if sel_item.is_hidden:
          selected_models.append(sel_item.model)

    # Update the selection in the data container
    self.__data_container.set_model_selection(selected_models)


  def __on_item_changed(self, item):
    item.update_model_visibility()
    # Shall we update the data container and thus notify all its observers?
    if self.__update_data_container_visibility:
      self.__data_container.update_visibility()


  def __add_data_items(self, models):
    # Add one checkable list item per model
    for model in models:
      # First, create the Qt list item
      #qt_list_item = QtWidgets.QListWidgetItem(model.name) # Better not to pass the Qt List as second argument. When passing it, itemChanged gets triggered.
      #qt_list_item.setFlags(qt_list_item.flags() | QtCore.Qt.ItemIsUserCheckable)
      #qt_list_item.setCheckState(QtCore.Qt.Checked)
      # Create our own data item
      item = ListWidgetItem(model)
      item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
      item.setCheckState(QtCore.Qt.Checked)
      # Save the item in the dictionaries
      self.__model_to_item[model] = item
      # Save the item in the ordered list
      if isinstance(model, VtkVolumeModel):
        self.__ordered_items.insert(0, item)
        self.__qt_list_widget.insertItem(0, item)
      else:
        self.__ordered_items.append(item)
        self.__qt_list_widget.insertItem(self.__qt_list_widget.count(), item)


  def __update_selection(self, data):
    # Save the current state before changing it
    ignore_selection_callback = self.__ignore_selection_callback
    # The following for-loop makes Qt call the self.__on_item_selection callback which would update the data container selection. However, we do not want that,
    # since this would make the data container inform all its observers (including this one) about the change, which would again lead to this method -> endless loop.
    # That's why the following line:
    self.__ignore_selection_callback = True

    # First, unselect all
    self.__qt_list_widget.clearSelection()
    self.__model_to_selected_item.clear()

    item = None

    # Select only those in 'data'
    for model in data:
      item = self.__model_to_item.get(model)
      if item:
        item.setSelected(True)
        self.__model_to_selected_item[model] = item

    # If there was only one item => scroll to it
    if len(data) == 1 and item:
      self.__qt_list_widget.scrollToItem(item)

    # Restore the state
    self.__ignore_selection_callback = ignore_selection_callback


  @property
  def qt_list_widget(self):
    return self.__qt_list_widget
