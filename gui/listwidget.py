from vis.vtkvol import VtkVolumeModel
from core.datacontainer import DataContainer
from PyQt5 import QtCore, QtWidgets

#============================================================================================================
# ListWidgetItem ============================================================================================
#============================================================================================================
class ListWidgetItem(QtWidgets.QListWidgetItem):
  def __init__(self, model):
    super().__init__(model.name)
    # Save the model
    self.model = model

    # Shall it be checked (i.e., is the model visible)
    if self.model.visual_representation.is_visible(): self.setCheckState(QtCore.Qt.Checked)
    else: self.setCheckState(QtCore.Qt.Unchecked)

    # Per default the item is not hidden and not selected
    self.is_hidden = False
    self.setSelected(False)


  def update_model_visibility(self):
    if self.__is_checked(): self.model.visual_representation.visibility_on()
    else: self.model.visual_representation.visibility_off()


  def __is_checked(self):
    return self.checkState() == QtCore.Qt.Checked


  def set_checked(self):
    if not self.__is_checked(): self.setCheckState(QtCore.Qt.Checked)
    self.model.visual_representation.visibility_on()


  def set_unchecked(self):
    if self.__is_checked(): self.setCheckState(QtCore.Qt.Unchecked)
    self.model.visual_representation.visibility_off()


  def set_hidden(self, hidden):
    self.is_hidden = hidden


  def toggle_check_state(self):
    if self.__is_checked():
      self.set_unchecked()
    else:
      self.set_checked()


#============================================================================================================
# ListWidget ================================================================================================
#============================================================================================================
class ListWidget(QtWidgets.QListWidget):
  def __init__(self, data_container):
    super().__init__()
    self.__data_container = data_container
    # Make sure that the data container has the right type
    if not isinstance(self.__data_container, DataContainer):
      raise TypeError("the data container has the wrong type")
    # Register itself as an observer to the data_container
    self.__data_container.add_observer(self)

    self.__model_to_item = dict()
    self.__model_to_selected_item = dict()
    self.__ordered_items = list()    
 
    self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    self.itemSelectionChanged.connect(self.__on_item_selection)
    self.itemChanged.connect(self.__on_item_changed)

    # The following ones are used in some of the callbacks
    self.__update_data_container_visibility = True
    self.__ignore_selection_callback = False


  def observable_changed(self, change, data):
    # Decide what to do depending on the change
    if change == DataContainer.change_is_new_brain_regions:
      self.__add_data_items(data)
    elif change == DataContainer.change_is_new_selection:
      self.__update_selection(data)
    elif change == DataContainer.change_is_deleted_models:
      self.__delete_models(data)


  def show_items_containing_text(self, text):
    """Loop over the loaded models and show only those which contain 'text' in the name."""
    # The following lines cause Qt to call __on_item_selection which we don't want
    ignore_selection_callback = self.__ignore_selection_callback
    self.__ignore_selection_callback = True
    
    # First, remove all elements from the list (don't call self.clear() since the items are destroyed!)
    for i in range(self.count()):
      self.takeItem(0)

    # Insert all elements whose names contain 'text'
    for item in self.__ordered_items:
      if text in item.model.name.lower():
        item.is_hidden = False
        self.insertItem(self.count(), item)
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


  def keyPressEvent(self, event):
    # Do the default Qt stuff
    super().keyPressEvent(event)
    if event.key() == QtCore.Qt.Key_Delete:
      self.__data_container.delete_selected_models()


  def __on_item_selection(self):
    if self.__ignore_selection_callback:
      return
    
    selected_models = list()
    
    # Collect the models selected by the user
    for item in self.selectedItems():
        selected_models.append(item.model)

    # If the user holds the ctrl. key, add the hidden selected items to the current ones
    if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
      for sel_item in self.__model_to_selected_item.values():
        if sel_item.is_hidden:
          selected_models.append(sel_item.model)

    # Update the selection in the data container
    self.__data_container.set_selection(selected_models)


  def __on_item_changed(self, item):
    item.update_model_visibility()
    # Shall we update the data container and thus notify all its observers?
    if self.__update_data_container_visibility:
      self.__data_container.update_visibility()


  def __add_data_items(self, models):
    # Add one checkable list item per model
    for model in models:
      # Create our own data item
      item = ListWidgetItem(model)
      item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
      # Save the item in the dictionaries
      self.__model_to_item[model] = item
      # Save the item in the ordered list
      if isinstance(model, VtkVolumeModel):
        self.__ordered_items.insert(0, item)
        self.insertItem(0, item)
      else:
        self.__ordered_items.append(item)
        self.insertItem(self.count(), item)


  def __update_selection(self, data):
    # Save the current state before changing it
    ignore_selection_callback = self.__ignore_selection_callback
    # The following for-loop makes Qt call the self.__on_item_selection callback which would update the data container selection. However, we do not want that,
    # since this would make the data container inform all its observers (including this one) about the change, which would again lead to this method -> endless loop.
    # That's why the following line:
    self.__ignore_selection_callback = True

    # First, unselect all
    self.clearSelection()
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
      self.scrollToItem(item)

    # Restore the state
    self.__ignore_selection_callback = ignore_selection_callback


  def __delete_models(self, models):
    for model in models:
      self.__delete_model(model)


  def __delete_model(self, model):
    ignore_selection_callback = self.__ignore_selection_callback
    self.__ignore_selection_callback = True

    # Get the list item corresponding to the model
    item = self.__model_to_item.get(model)
    
    # Remove the model from the dictionaries
    try:
      del self.__model_to_item[model]
      del self.__model_to_selected_item[model]
    except KeyError:
      pass
    # Remove the corresponding item from the QListWidget and another internal list
    if item:
      self.takeItem(self.row(item))
      try:
        self.__ordered_items.remove(item)
      except KeyError:
        pass

    self.__ignore_selection_callback = ignore_selection_callback
