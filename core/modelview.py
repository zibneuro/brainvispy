import abc

#======================================================================================================
# Observer ============================================================================================
#======================================================================================================
class Observer(metaclass = abc.ABCMeta):
  @abc.abstractmethod
  def observable_changed(self, change, data):
    pass

#======================================================================================================
# Observable ==========================================================================================
#======================================================================================================
class Observable:
  def __init__(self):
    # These will be the guys observing this objects
    self.observers = list()

  def add_observer(self, observer):
    """'observer' will start observing this object which means that it will get notified when the Observable changes by calling the appropriate methods in Observer."""
    # Make sure that the observer is an instance of Observer
    if not isinstance(observer, Observer):
      raise TypeError("input has to be an instance of Observer")

    # Make sure that 'observer' is not already in the list (we add each observer only once)
    try:
      self.observers.index(observer)
    except:
      self.observers.append(observer)


  def notify_observers_abount_change(self, change, data):
    """The model should call this method when it changed and pass the specific change (should be one of the self.change_is_XXX members) and some data.
    This method then calls the observable_changed method of all registered observers passing 'change' and 'data' to each one."""
    for observer in self.observers:
      observer.observable_changed(change, data)
