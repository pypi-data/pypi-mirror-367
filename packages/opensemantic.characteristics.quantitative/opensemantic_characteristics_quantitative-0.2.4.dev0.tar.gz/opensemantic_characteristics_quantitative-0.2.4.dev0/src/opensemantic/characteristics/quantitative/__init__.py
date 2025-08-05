from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "opensemantic.characteristics.quantitative"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from opensemantic.characteristics.quantitative._model import *  # noqa
from opensemantic.characteristics.quantitative._static import (  # noqa
    QuantityValue,
    TabularData,
)
