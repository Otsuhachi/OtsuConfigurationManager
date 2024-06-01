from typing import Any, NoReturn, Protocol, Self

from otsutil import pathLike


class PBaseCM(Protocol):
    """設定ファイル管理クラス用の基底クラス。

    このクラスを継承したクラスに__defaults__, <attribute>を定義するだけで、設定ファイルの読み書きに必要な処理を行えるようになります。

    拡張子に制約はありませんが、読み込んだ際に辞書形式のjsonである必要があります。
    """

    def __init__(self, file: pathLike, export_default_config: bool = False) -> None:
        """設定ファイルを指定して扱えるようにする。

        Args:
            file (pathLike): 設定ファイルのパス。
            export_default_config (bool, optional): 設定ファイルを書き出す際、デフォルトと同じ値も書き出すかどうか。 Defaults to False.
        """
        ...

    def __enter__(self) -> Self: ...

    def __exit__(self, *ex) -> bool: ...

    def __getattr__(self, key: str) -> NoReturn: ...

    def __setattr__(self, name: str, value: Any) -> None: ...

    @property
    def attributes_cm(self) -> set[str]:
        """クラス定義の属性名セット。"""
        ...

    @property
    def key_place_cm(self) -> dict[str, list[str] | None]:
        """各属性の保存先を記録する辞書。"""
        ...

    def cfg_to_str_cm(self, all: bool = False) -> str:
        """設定をjson.dumpsして返す。

        self.__hidden_options__に登録されている属性はユーザが変更している場合のみ表示されます。

        allが有効の場合、defaults, userという二つのセクションからなる辞書として扱われます。

        Args:
            all (bool, optional): 標準設定を含めるか。 Defaults to False.

        Returns:
            str: 設定の文字列。
        """
        ...

    def load_cm(self, **kwargs) -> None:
        """設定ファイルを読み込む。

        読み込んだ設定を基にインスタンスの属性を更新します。

        Raises:
            TypeError: self.__file__が辞書形式のjsonでない場合。
            KeyError: 必要な階層が存在しない場合。
        """
        ...

    def save_cm(self, export_default_config: bool = False, **kwargs) -> None:
        """設定ファイルを書き出す。

        キーワード引数にはjson.dumpで使用できる引数を与えることができます。
        一部引数は指定しなかった場合以下の値が使用されます。
        またfpはself.__file__固定になります。

        indent: 4
        encoding: utf-8
        ensure_ascii: False
        default: support_json_dump
        sort_keys: True

        Args:
            export_default_config (bool, optional): 設定ファイルを書き出す際、デフォルトと同じ値も書き出すかどうか。 Defaults to False.
        """
        ...

    def reset_cm(self) -> None:
        """各属性を初期値に戻します。"""
        ...

    def defaults_cm(self) -> dict[str, Any]:
        """各属性の初期値の辞書を返す。

        Returns:
            dict[str, Any]: 各属性の初期値の辞書。
        """
        ...

    def user_cm(self, include_default_config: bool = False) -> dict[str, Any]:
        """ユーザが設定した属性の辞書を返す。

        Args:
            include_default_config (bool, optional): デフォルト値と同じ値も含めるか。 Defaults to False.

        Returns:
            dict[str, Any]: ユーザが設定した属性の辞書。
        """
        ...
