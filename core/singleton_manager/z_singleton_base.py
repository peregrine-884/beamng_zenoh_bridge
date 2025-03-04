class SingletonBase:
  _instances = {}

  def __new__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super().__new__(cls)
      cls._instances[cls].initialize(*args, **kwargs)  # Each subclass should define `initialize()`
    return cls._instances[cls]

  def initialize(self, *args, **kwargs):
    """
    Subclasses should override this method for initialization.
    """
    pass