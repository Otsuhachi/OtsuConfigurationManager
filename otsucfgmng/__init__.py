"""設定ファイルの生成、管理を補助するライブラリです。
"""

__all__ = (
    "BaseCM",
    "get_dict_keys_position",
    "support_json_dump",
)

from .configuration_manager import BaseCM
from .funcs import get_dict_keys_position, support_json_dump
