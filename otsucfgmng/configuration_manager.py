__all__ = ("BaseCM",)


import copy
import json
from pathlib import Path
from typing import Any, NoReturn, Self

from otsuvalidator import CPath, VBool, VTuple

from otsutil import OtsuNone, StrPath, load_json, save_json

from .funcs import get_dict_keys_places, support_json_dump


class __MetaCM(type):
    def __new__(cls, name: str, bases: tuple, attrs: dict):
        excludes = {
            "__module__",
            "__qualname__",
            "__defaults__",
            "__hidden_options__",
            "__annotations__",
            "__doc__",
        }
        attr_keys = set(attrs.keys()) - excludes
        if isinstance(dflt := attrs.get("__defaults__", None), dict):
            kp = {}
            for k, _, places in get_dict_keys_places(dflt):
                if k not in attr_keys:
                    msg = f"'{k}'属性は宣言されていません。"
                    raise AttributeError(msg)
                if kp.get(k, OtsuNone) is not OtsuNone:
                    msg = f"'{k}'属性は異なるセクションで宣言されています。"
                    raise AttributeError(msg)
                kp[k] = places
            if undefined := attr_keys - set(kp.keys()):
                msg = "属性の初期値が設定されていません（{}）".format(", ".join(undefined))
                raise AttributeError(msg)
            attrs["__attr_keys__"] = attr_keys
            attrs["__key_place__"] = kp
        return super().__new__(cls, name, bases, attrs)


class BaseCM(metaclass=__MetaCM):
    """設定ファイルを管理するベースクラス。

    メタクラス `__MetaCM` によって宣言された属性と `__defaults__` の不整合を検証し、
    バリデーション・自動保存・ロード機能を統合管理します。

    Args:
        file: 設定ファイルの保存先パス。
        export_default_config: コンテキスト終了時にデフォルト設定も出力するかどうか。
    """

    __file__ = CPath(path_type=Path.is_file)
    __hidden_options__ = VTuple(str)
    __export_default_config__ = VBool()

    def __init__(self, file: StrPath, export_default_config: bool = False) -> None:
        """BaseCMのインスタンスを初期化し、初期値の設定およびファイルの読み込みを行います。

        Args:
            file: 設定ファイルの保存先パス。
            export_default_config: コンテキスト終了時にデフォルト設定も出力するかどうか。
        """
        setattr(self, "__file__", file)
        self.__export_default_config__ = export_default_config
        dflt = self.defaults_cm()
        self.__user__ = cfu = {}
        kp = self.key_place_cm
        for k in self.attributes_cm:
            d = dflt
            u = cfu
            if (place := kp[k]) is not None:
                for p in place:
                    d = d[p]
                    if u.get(p, OtsuNone) is OtsuNone:
                        u[p] = {}
                    u = u[p]
            setattr(self, k, d[k])
            validated_val = getattr(self, k)
            setattr(self, f"default_{k}_cm", validated_val)
            d[k] = validated_val
        self.__defaults__ = dflt
        self.load_cm()

    def __enter__(self) -> Self:
        """コンテキストマネージャの開始処理。

        Returns:
            Self: 自身のインスタンス。
        """
        return self

    def __exit__(self, *ex) -> bool:
        """コンテキストマネージャの終了処理。設定をファイルに書き出します。

        Args:
            *ex: 例外情報。

        Returns:
            bool: 例外なく処理が完了したか、例外が処理された場合はTrue。
        """
        try:
            self.save_cm(self.__export_default_config__)
            if any(ex):
                return False
            return True
        except Exception:
            return False

    def __getattr__(self, key: str) -> NoReturn:
        """未定義の属性にアクセスした場合にAttributeErrorを発生させます。

        Args:
            key: アクセスを試みた属性名。

        Returns:
            NoReturn: 常にAttributeErrorを発生させます。

        Raises:
            AttributeError: 指定された属性が存在しない場合。
        """
        msg = f"'{key}'属性は存在しません。"
        raise AttributeError(msg)

    def __setattr__(self, name: str, value: Any) -> None:
        """属性値の設定を行います。`default_<属性名>_cm` 形式の初期値属性への直接上書きを制御します。

        Args:
            name: 属性名。
            value: 設定する値。

        Raises:
            AttributeError: 上書き禁止の初期値属性を変更しようとした場合、または無効な初期値属性へアクセスした場合。
        """
        nsp = name.split("_")
        if nsp[0] == "default" and nsp[-1] == "cm":
            _, *n, _ = nsp
            n_str = "_".join(n)
            if getattr(self, n_str, OtsuNone) is not OtsuNone:
                if self.__dict__.get(name, OtsuNone) is not OtsuNone:
                    msg = f"'{name}'属性は上書きできません。"
                    raise AttributeError(msg)
            else:
                msg = f"'{n_str}'属性が存在しないため、その初期値を表す'{name}'属性も存在しません。"
                raise AttributeError(msg)
        super().__setattr__(name, value)

    @property
    def attributes_cm(self) -> set[str]:
        """設定項目として定義されている属性名の集合のディープコピーを取得します。

        Returns:
            set[str]: 属性名のセット。
        """
        return copy.deepcopy(getattr(self, "__attr_keys__", set()))

    @property
    def key_place_cm(self) -> dict[str, list[str] | None]:
        """各設定属性の辞書構造における階層パス情報を取得します。

        Returns:
            dict[str, list[str] | None]: 属性名をキー、階層パスのリスト（またはNone）を値とする辞書。
        """
        return copy.deepcopy(getattr(self, "__key_place__", {}))

    def cfg_to_str_cm(self, all_: bool = False) -> str:
        """現在の設定内容を整形されたJSON文字列に変換します。

        Args:
            all_: Trueの場合、デフォルト値とユーザー変更値の両方を含んだ文字列を返します。

        Returns:
            str: JSONフォーマット文字列。
        """
        if all_:
            tmp = {
                "defaults": copy.deepcopy(self.defaults_cm()),
                "user": self.user_cm(),
            }
            kp = self.key_place_cm
            if isinstance(ho := getattr(self, "__hidden_options__", None), tuple):
                ho = set(ho)
                for key in ho:
                    if not isinstance(place := kp.get(key, OtsuNone), list):
                        continue
                    dflt = tmp["defaults"]
                    user = tmp["user"]
                    if place is not None:
                        for p in place:
                            dflt = dflt[p]
                            user = user[p]
                    if user.get(key, OtsuNone) is OtsuNone:
                        del dflt[key]
        else:
            tmp = self.user_cm()
        return json.dumps(
            tmp,
            indent=4,
            ensure_ascii=False,
            default=support_json_dump,
            sort_keys=True,
        )

    def load_cm(self, **kwargs) -> None:
        """設定ファイルからデータを読み込み、対応する属性へ値を反映します。

        Args:
            **kwargs: load_jsonに引き渡すオプション引数。

        Raises:
            TypeError: 読み込んだJSONが辞書形式でない場合。
            KeyError: 必要なセクション（階層構造）がJSON内に存在しない場合。
        """
        if not (file := self.__file__).exists():
            return
        kwargs["file"] = file
        jsn = load_json(**kwargs)
        if not isinstance(jsn, dict):
            msg = f"'{file}'は対応していない形式です。"
            raise TypeError(msg)
        for key, places in self.key_place_cm.items():
            d = jsn
            if places is not None:
                for p in places:
                    if (d := d.get(p, OtsuNone)) is OtsuNone:
                        jsctn = "->".join(places)
                        msg = f"{jsctn}が発見できませんでした。'{file}'が正しい形式の設定ファイルか確認してください。"
                        raise KeyError(msg)
            if (dk := d.get(key, OtsuNone)) is OtsuNone:
                continue
            setattr(self, key, dk)

    def save_cm(self, export_default_config: bool | None = None, **kwargs) -> None:
        """現在の設定状況をJSONファイルとして保存します。

        Args:
            export_default_config: デフォルト値と同じ設定もファイルに書き出すかどうか。
            **kwargs: save_jsonに引き渡すオプション引数。
        """
        if export_default_config is None:
            export_default_config = self.__export_default_config__
        user = self.user_cm(export_default_config)
        kwargs["data"] = user
        set_kwargs = (
            ("file", self.__file__),
            ("indent", 4),
            ("ensure_ascii", False),
            ("default", support_json_dump),
            ("sort_keys", True),
        )
        for k, v in set_kwargs:
            if kwargs.get(k, OtsuNone) is OtsuNone:
                kwargs[k] = v
        save_json(**kwargs)

    def reset_cm(self) -> None:
        """すべての設定属性を定義時の初期値（デフォルト値）へとリセットします。"""

        def get_dflt(x: str) -> str:
            return f"default_{x}_cm"

        for key in self.attributes_cm:
            setattr(self, key, getattr(self, get_dflt(key)))

    def defaults_cm(self) -> dict[str, Any]:
        """設定されているデフォルト値辞書のディープコピーを取得します。

        Returns:
            dict[str, Any]: デフォルト設定の辞書。
        """
        return copy.deepcopy(getattr(self, "__defaults__", {}))

    def user_cm(self, include_default_config: bool = False) -> dict[str, Any]:
        """ユーザーによって変更された設定項目の辞書構造を取得します。

        Args:
            include_default_config: デフォルト値のままの項目も含めて抽出するかどうか。

        Returns:
            dict[str, Any]: 階層構造が維持された設定値辞書。
        """
        user = self.__user__
        kp = self.key_place_cm
        ho = getattr(self, "__hidden_options__", OtsuNone)

        def checker(x) -> bool:
            return x in ho if ho is not OtsuNone else False

        for k in self.attributes_cm:
            uv = getattr(self, k)
            dv = getattr(self, f"default_{k}_cm")
            places = kp[k]
            u = user
            if places is not None:
                for p in places:
                    u = u[p]
            if (not include_default_config or checker(k)) and uv == dv:
                if u.get(k, OtsuNone) is not OtsuNone:
                    del u[k]
            else:
                u[k] = uv
        return user
