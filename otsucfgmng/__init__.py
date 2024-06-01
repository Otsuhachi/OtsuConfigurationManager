"""設定ファイルの生成、管理を補助するライブラリ。
"""

__all__ = (
    "BaseCM",
    "PBaseCM",
    "get_dict_keys_places",
    "support_json_dump",
)

from .configuration_manager import BaseCM
from .funcs import get_dict_keys_places, support_json_dump
from .protocol import PBaseCM
