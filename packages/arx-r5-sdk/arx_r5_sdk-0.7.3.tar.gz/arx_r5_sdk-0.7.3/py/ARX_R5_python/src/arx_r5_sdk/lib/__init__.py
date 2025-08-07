import os

# Get the absolute path to the directory containing this file
_lib_dir = os.path.dirname(os.path.abspath(__file__))

# Prepend our library directory to LD_LIBRARY_PATH
# This is for Linux. A similar approach would be needed for other OSes.
if "LD_LIBRARY_PATH" in os.environ:
    os.environ["LD_LIBRARY_PATH"] = f"{_lib_dir}:{os.environ['LD_LIBRARY_PATH']}"
else:
    os.environ["LD_LIBRARY_PATH"] = _lib_dir

# Now we can import the modules
from . import arx_r5_python
from . import kinematic_solver
