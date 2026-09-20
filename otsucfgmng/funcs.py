__all__ = [
    "get_dict_keys_places",
    "is_support_json_dump",
    "support_json_dump",
]


from collections.abc import Iterator
from typing import Any, TypeGuard

from .protocol import PSupportJsonDump


def get_dict_keys_places(
    dict_: dict[str, Any],
    *,
    position: list[str] | None = None,
) -> Iterator[tuple[str, Any, list[str] | None]]:
    """ネストされた辞書を走査し、キー、値、およびその階層パスをジェネレータとして返します。

    Args:
        dict_: 走査対象の辞書。
        position: 現在の階層パスを示す文字列リスト。内部計算用。

    Yields:
        Iterator[tuple[str, Any, list[str] | None]]: (キー, 値, 階層パスのリスト) のタプル。
    """
    position = position or []
    for k, v in dict_.items():
        if isinstance(v, dict):
            yield from get_dict_keys_places(v, position=[*position, k])
        else:
            yield (k, v, position or None)


def is_support_json_dump(value: Any) -> TypeGuard[PSupportJsonDump]:
    """指定された値が `to_json` メソッドを持つJSONシリアライズ可能オブジェクトか判定します。

    Args:
        value: 判定対象の値。

    Returns:
        TypeGuard[PSupportJsonDump]: `to_json` メソッドを保持し呼び出し可能な場合はTrue。
    """
    to_json = getattr(value, "to_json", None)
    if to_json is None:
        return False
    return callable(to_json)


def support_json_dump(o: Any) -> str | Any:
    """`json.dumps` の `default` 引数に渡すシリアライズ関数。

    Args:
        o: 変換対象のオブジェクト。

    Returns:
        str | Any: `to_json` を持つ場合はその実行結果、持たない場合は文字列化された値。
    """
    if is_support_json_dump(o):
        return o.to_json()
    return str(o)
