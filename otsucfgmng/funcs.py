"""設定ファイル管理クラスで使用する関数を纏めたモジュールです。"""
__all__ = (
    "get_dict_keys_position",
    "support_json_dump",
)

from typing import Any, Iterator


def get_dict_keys_position(dict_: dict, *, position: list | None = None) -> Iterator[tuple[Any, Any, list | None]]:
    """辞書のキー、値、辞書内の位置を返します。

    値が辞書の場合、positionにはキーの名前が格納され、階層を示します。
    値が辞書以外の場合、positionはNoneになります。

    Args:
        dict_ (dict): キーの階層を取得したい辞書。
        position (list | None, optional): 辞書内の階層。 Defaults to None.

    Yields:
        Iterator[tuple[Any, Any, list | None]]: (キー, 値, 階層)のタプル。

    Examples:
        >>> dict_ = {
        ...     'name': 'Otsuhachi',
        ...     'data': {
        ...         'age': 28,
        ...         'H_W': {
        ...             'height': 167,
        ...             'weight': 74
        ...         }
        ...     },
        ... }
        >>>
        >>> for kvp in get_dict_keys_position(dict_):
        ...     print(kvp)
        ...
        ('name', 'Otsuhachi', None)
        ('age', 28, ['data'])
        ('height', 167, ['data', 'H_W'])
        ('weight', 74, ['data', 'H_W'])
    """
    for k, v in dict_.items():
        if isinstance(v, dict):
            if position is None:
                position = []
            yield from get_dict_keys_position(v, position=position + [k])
        else:
            yield (k, v, position)


def support_json_dump(o: Any) -> str:
    """JSONで変換できないオブジェクトをstrとして返します。

    to_jsonメソッドを定義していればそちらを優先して使用します。

    Args:
        o (Any): JSONで変換できないオブジェクト。

    Returns:
        str: str(o)。
    """
    if hasattr(o, "to_json"):
        return o.to_json()
    return str(o)
