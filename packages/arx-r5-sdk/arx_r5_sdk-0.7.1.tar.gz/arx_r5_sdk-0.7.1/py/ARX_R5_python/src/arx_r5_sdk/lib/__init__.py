import os
import ctypes

# Get the absolute path to the directory containing this file
_lib_dir = os.path.dirname(os.path.abspath(__file__))

# Add this directory to the dynamic linker's search path
# This is for Linux. A similar approach would be needed for other OSes.
try:
    # This is a bit of a hack, but it's the most reliable way to do this
    # without requiring the user to set LD_LIBRARY_PATH.
    ctypes.CDLL(f'libdl.so.2').dlopen(_lib_dir, ctypes.RTLD_GLOBAL)
except (OSError, AttributeError):
    # If dlopen is not available, we can't do much.
    # This will likely fail on non-Linux systems.
    pass

# Now we can import the modules
from . import arx_r5_python
from . import kinematic_solver
