import importlib.metadata

__version__ = importlib.metadata.version("eodc")

from eodc_connect.settings import settings  # noqa

from . import auth, dask  # noqa
