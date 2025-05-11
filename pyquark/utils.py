import os
import time


def get_parent_path(path, levels_up):
    # Get parent path
    parent_path = path
    for _ in range(levels_up):
        parent_path = os.path.dirname(parent_path)
    return parent_path


def exec_time(func):
    """Apply as decorator to any method to measure its exec time"""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time:.6f} seconds")
        return result
    return wrapper


def find_parent_path(path, target_folder, logger=None):
    # Find the parent path that contains the target folder
    current_path = path
    max_level = 50
    nCount = 0
    while True:
        if os.path.basename(current_path) == target_folder:
            return current_path
        current_path = os.path.dirname(current_path)
        if not current_path:  # Reached the root directory
            break
        nCount += 1
        if nCount > max_level:
            if logger:
                logger.rprint(f"Max level {max_level} reached. Stopping search.")
            else:
                print(f"Max level {max_level} reached. Stopping search.")
            break
    return None


def __init__(self, name):
    self.name = name
    self.zones = []
    self.damage_size = 0.0
    self.is_damaged = False
    self.masks = {}  # Dictionary of masks
    self.damage_masks = {}  # Dictionary of damage masks
    self._numpy_arrays = []  # Track NumPy arrays
    self._custom_objects = []  # Track custom objects with __destroy__ method


def __destroy__(self, hard_destroy=False, calling_class=None):
    """
    Frees up memory by clearing all instance attributes

    Args:
        hard_destroy (bool): If True, removes all attributes using delattr
                            regardless of their type
    """
    # Create a list of all attributes
    attrs = list(self.__dict__.keys())

    if hard_destroy:
        # Get all attributes and delete them
        for attr_name in attrs:
            delattr(self, attr_name)
        return

    # Handle specific attribute types differently
    for attr_name in attrs:

        if (attr_value := getattr(self, attr_name, None)) is None:
            continue

        # Handle by type
        if isinstance(attr_value, dict):
            attr_value.clear()
        elif isinstance(attr_value, (list, tuple)):
            # Set to empty of the same type
            if isinstance(attr_value, list):
                setattr(self, attr_name, [])
            else:
                setattr(self, attr_name, ())
        elif getattr(attr_value.__class__, '__destroy__', None) and type(attr_value) != calling_class:
            # Call __destroy__ on objects that have that method
            attr_value.__destroy__()
            setattr(self, attr_name, None)
        elif 'numpy' in str(type(attr_value).__module__):
            # This handles NumPy arrays specifically
            delattr(self, attr_name)
        else:
            # For simple types, just set to None
            setattr(self, attr_name, None)