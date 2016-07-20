import abc

#============================================================================================================
# ProgressBar ===============================================================================================
#============================================================================================================
class ProgressBar(metaclass = abc.ABCMeta):
  """An interface to a GUI element which indicates the progress of some task currently being performed."""
 
  @abc.abstractmethod
  def init(self, range_min, range_max, description = None):
    """Initialize a range [range_min, range_max]. 'description' is an optional string argument which should
    be really short (the best would be one word) which will be put to the left of the loading bar."""
    pass
  
  @abc.abstractmethod
  def set_progress(self, k):
    """Call this method to indicate the progress. 'k' should be in the range used to call init."""
    pass
  
  @abc.abstractmethod
  def done(self):
    """This method is called when the loading is finished."""
    pass
