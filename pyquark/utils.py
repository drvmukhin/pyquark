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