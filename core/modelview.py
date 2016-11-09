import inspect

#======================================================================================================
# Observable ==========================================================================================
#======================================================================================================
class Observable:
  def __init__(self):
    # These will be the guys observing this objects
    self.observers = list()

  def add_observer(self, observer):
    # This is the error to raise if 'observer' doesn't have the observable_changed method
    type_error = TypeError("the observer has to implement the method observable_changed(self, change, data)")

    try:
      arg_names = inspect.getargspec(observer.observable_changed)[0]
      if len(arg_names) != 3 or arg_names[0] != "self" or arg_names[1] != "change" or arg_names[2] != "data":
        raise type_error
    except:
      raise type_error

    # Make sure that 'observer' is not already in the list (we add each observer only once)
    try:
      self.observers.index(observer)
    except:
      self.observers.append(observer)


  def notify_observers_about_change(self, change, data):
    """The model should call this method when it changed and pass the specific change (should be one of the self.change_is_XXX members) and some data.
    This method then calls the observable_changed method of all registered observers passing 'change' and 'data' to each one."""
    for observer in self.observers:
      observer.observable_changed(change, data)
