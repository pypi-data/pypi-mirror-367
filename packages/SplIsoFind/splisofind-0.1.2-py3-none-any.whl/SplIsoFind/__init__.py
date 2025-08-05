from importlib.metadata import version
__version__ = version(__name__)  

from . import spatially_variable as sv
from . import plotting as pl
from . import preprocess as pp

__all__ = ["sv", "pl", "pp"]