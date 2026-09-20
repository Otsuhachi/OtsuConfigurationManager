__all__ = [
    "PBaseCM",
    "PSupportJsonDump",
]


from typing import Any, NoReturn, Protocol, Self

from otsutil import StrPath


class PBaseCM(Protocol):
    """設定管理クラス（BaseCM）のインターフェースを定義するプロトコル。

    Args:
        file: 設定ファイルの保存先パス。
        export_default_config: コンテキスト終了時にデフォルト設定も出力するかどうか。
    """

    def __init__(self, file: StrPath, export_default_config: bool = False) -> None: ...

    def __enter__(self) -> Self:
        """コンテキストマネージャの開始処理。

        Returns:
            Self: 自身のインスタンス。
        """
        ...

    def __exit__(self, *ex) -> bool:
        """コンテキストマネージャの終了処理。スコープ脱出時に自動で設定を保存します。

        Args:
            *ex: 例外情報。

        Returns:
            bool: 例外を抑制する場合はTrue、それ以外はFalse。
        """
        ...

    def __getattr__(self, key: str) -> NoReturn:
        """未定義属性へのアクセス時に呼び出されます。

        Args:
            key: 属性名。

        Returns:
            NoReturn: 常にAttributeErrorを発生させます。
        """
        ...

    def __setattr__(self, name: str, value: Any) -> None:
        """属性値の設定時に呼び出されます。

        Args:
            name: 属性名。
            value: 設定する値。
        """
        ...

    @property
    def attributes_cm(self) -> set[str]:
        """設定項目として定義されている属性名の集合を取得します。

        Returns:
            set[str]: 属性名のセット。
        """
        ...

    @property
    def key_place_cm(self) -> dict[str, list[str] | None]:
        """各設定属性の辞書内における階層構造（キーの配置）を取得します。

        Returns:
            dict[str, list[str] | None]: 属性名をキー、階層パスのリスト（またはNone）を値とする辞書。
        """
        ...

    def cfg_to_str_cm(self, all_: bool = False) -> str:
        """現在の設定内容をJSON形式の文字列に変換します。

        Args:
            all_: Trueの場合、デフォルト値とユーザー設定値の両方を含めた文字列を生成します。

        Returns:
            str: JSONフォーマットされた設定文字列。
        """
        ...

    def load_cm(self, **kwargs) -> None:
        """設定ファイルから設定値を読み込みます。

        Args:
            **kwargs: load_jsonに渡す追加の引数。
        """
        ...

    def save_cm(self, export_default_config: bool = False, **kwargs) -> None:
        """現在の設定値をファイルに保存します。

        Args:
            export_default_config: デフォルト値と同じ設定も出力に含めるかどうか。
            **kwargs: save_jsonに渡す追加の引数。
        """
        ...

    def reset_cm(self) -> None:
        """すべての設定項目を初期値（デフォルト値）に戻します。"""
        ...

    def defaults_cm(self) -> dict[str, Any]:
        """定義されている初期値（デフォルト設定）の辞書を取得します。

        Returns:
            dict[str, Any]: デフォルト設定の辞書。
        """
        ...

    def user_cm(self, include_default_config: bool = False) -> dict[str, Any]:
        """ユーザーによって変更された設定値の辞書を取得します。

        Args:
            include_default_config: 変更されていない初期値も含めるかどうか。

        Returns:
            dict[str, Any]: ユーザー設定値の辞書。
        """
        ...


class PSupportJsonDump(Protocol):
    """JSONシリアライズに対応したオブジェクトのプロトコル。"""

    def to_json(self) -> Any:
        """オブジェクトをJSONシリアライズ可能な表現に変換します。

        Returns:
            Any: JSONシリアライズ可能な値。
        """
        ...
