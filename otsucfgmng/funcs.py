"""設定ファイル管理クラスで使用する関数を纏めたモジュール。"""

__all__ = (
    "get_dict_keys_places",
    "support_json_dump",
)

from typing import Any, Iterator


def get_dict_keys_places(dict_: dict[str, Any], *, position: list[str] | None = None) -> Iterator[tuple[str, Any, list[str] | None]]:
    """辞書のキー、値、辞書内の位置を返す。

    値が辞書の場合、positionにはキーの名前が格納され、階層を示します。
    値が辞書以外の場合、positionはNoneになります。

    Args:
        dict_ (dict[str, Any]): 辞書。
        position (list[str] | None, optional): 辞書内の階層。 Defaults to None.

    Yields:
        Iterator[tuple[str, Any, list[str] | None]]: (キー, 値, 階層)のタプル。

    Examples:
        >>> dict_ = {
        ...     "name": "Otsuhachi",
        ...     "data": {
        ...         "age": 28,
        ...         "H_W": {
        ...             "height": 167,
        ...             "weight": 81,
        ...         },
        ...     },
        ... }
        >>> for kvp in get_dict_keys_places(dict_):
        ...     print(kvp)
        ...
        ("name", "Otsuhachi", None)
        ("age", 28, ["data"])
        ("height", 167, ["data", "H_W"])
        ("weight", 81, ["data", "H_W"])
    """
    for k, v in dict_.items():
        if isinstance(v, dict):
            if position is None:
                position = []
            yield from get_dict_keys_places(v, position=position + [k])
        else:
            yield (k, v, position)


def support_json_dump(o: Any) -> str:
    """JSONで変換できないオブジェクトをstrとして返す。

    to_jsonメソッドを定義していればそちらを優先して使用します。

    Args:
        o (Any): JSONで変換できないオブジェクト。

    Returns:
        str: str(o)。
    """
    if hasattr(o, "to_json"):
        return o.to_json()
    return str(o)
