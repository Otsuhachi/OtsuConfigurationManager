import logging

from .configuration_manager import BaseCM
from .funcs import (
    get_dict_keys_places,
    is_support_json_dump,
    support_json_dump,
)
from .protocol import (
    PBaseCM,
    PSupportJsonDump,
)

__all__ = [
    "BaseCM",
    "PBaseCM",
    "PSupportJsonDump",
    "__version__",
    "get_dict_keys_places",
    "is_support_json_dump",
    "support_json_dump",
]


logging.getLogger(__name__).addHandler(logging.NullHandler())


__version__ = "2.0.0"
