"""設定ファイルの生成、管理を助けるクラスを定義したモジュール。
"""

__all__ = ("BaseCM",)
import copy
import json

from pathlib import Path
from typing import Any, NoReturn, Self

from otsutil import OtsuNone, load_json, pathLike, save_json
from otsuvalidator import CPath, VBool, VTuple

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
                    msg = f'"{k}"属性は宣言されていません。'
                    raise AttributeError(msg)
                if kp.get(k, OtsuNone) is not OtsuNone:
                    msg = f'"{k}"属性は異なるセクションで宣言されています。'
                    raise AttributeError(msg)
                kp[k] = places
            if undefined := attr_keys - set(kp.keys()):
                msg = "属性の初期値が設定されていません。({})".format(", ".join(undefined))
                raise AttributeError(msg)
            attrs["__attr_keys__"] = attr_keys
            attrs["__key_place__"] = kp
            attrs["__user__"] = {}
        return super().__new__(cls, name, bases, attrs)


class BaseCM(metaclass=__MetaCM):
    """設定ファイル管理クラス用の基底クラス。

    このクラスを継承したクラスに__defaults__, <attribute>を定義するだけで、設定ファイルの読み書きに必要な処理を行えるようになります。

    拡張子に制約はありませんが、読み込んだ際に辞書形式のjsonである必要があります。
    """

    __file__ = CPath(path_type=Path.is_file)
    __hidden_options__ = VTuple(str)
    __export_default_config__ = VBool()

    def __init__(self, file: pathLike, export_default_config: bool = False) -> None:
        """設定ファイルを指定して扱えるようにする。

        Args:
            file (pathLike): 設定ファイルのパス。
            export_default_config (bool, optional): 設定ファイルを書き出す際、デフォルトと同じ値も書き出すかどうか。 Defaults to False.
        """
        self.__file__ = file
        self.__export_default_config__ = export_default_config
        dflt = self.defaults_cm()
        cfu: dict = self.__user__
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
            setattr(self, f"default_{k}_cm", getattr(self, k))
        self.load_cm()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *ex) -> bool:
        try:
            self.save_cm(self.__export_default_config__)
            if any(ex):
                return False
            return True
        except:
            return False

    def __getattr__(self, key: str) -> NoReturn:
        msg = f'"{key}"属性は存在しません。'
        raise AttributeError(msg)

    def __setattr__(self, name: str, value: Any) -> None:
        nsp = name.split("_")
        if nsp[0] == "default" and nsp[-1] == "cm":
            _, *n, _ = nsp
            n = "_".join(n)
            if getattr(self, n, OtsuNone) is not OtsuNone:
                if self.__dict__.get(name, OtsuNone) is not OtsuNone:
                    msg = f'"{name}"属性は上書きできません。'
                    raise AttributeError(msg)
            else:
                msg = f'"{n}"属性が存在しないため、その初期値を表す"{name}"属性も存在しません。'
                raise AttributeError(msg)
        super().__setattr__(name, value)

    @property
    def attributes_cm(self) -> set:
        """クラス定義の属性名セット。"""
        return copy.deepcopy(self.__attr_keys__)

    @property
    def key_place_cm(self) -> dict[str, list[str] | None]:
        """各属性の保存先を記録する辞書。"""
        return copy.deepcopy(self.__key_place__)

    def cfg_to_str_cm(self, all: bool = False) -> str:
        """設定をjson.dumpsして返す。

        self.__hidden_options__に登録されている属性はユーザが変更している場合のみ表示されます。

        allが有効の場合、defaults, userという二つのセクションからなる辞書として扱われます。

        Args:
            all (bool, optional): 標準設定を含めるか。 Defaults to False.

        Returns:
            str: 設定の文字列。
        """
        if all:
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
        """設定ファイルを読み込む。

        読み込んだ設定を基にインスタンスの属性を更新します。

        Raises:
            TypeError: self.__file__が辞書形式のjsonでない場合。
            KeyError: 必要な階層が存在しない場合。
        """
        if not self.__file__.exists():  # type: ignore
            return
        kwargs["file"] = self.__file__
        try:
            jsn = load_json(**kwargs)
        except:
            return
        if not isinstance(jsn, dict):
            msg = f'"{self.__file__}"は対応していない形式です。'
            raise TypeError(msg)
        for key, places in self.key_place_cm.items():
            d = jsn
            if places is not None:
                for p in places:
                    if (d := d.get(p, OtsuNone)) is OtsuNone:
                        jsctn = "->".join(places)
                        msg = f"{jsctn}が発見できませんでした。{self.__file__}が正しい形式の設定ファイル化確認してください。"
                        raise KeyError(msg)
            if (dk := d.get(key, OtsuNone)) is OtsuNone:
                continue
            setattr(self, key, dk)

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
        user = self.user_cm(export_default_config)
        kwargs["file"] = self.__file__
        kwargs["data"] = user
        set_kwargs = (
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
        """各属性を初期値に戻します。"""
        dflt = lambda x: f"default_{x}_cm"
        for key in self.attributes_cm:
            setattr(self, key, getattr(self, dflt(key)))

    def defaults_cm(self) -> dict[str, Any]:
        """各属性の初期値の辞書を返す。

        Returns:
            dict[str, Any]: 各属性の初期値の辞書。
        """
        return copy.deepcopy(self.__defaults__)

    def user_cm(self, include_default_config: bool = False) -> dict[str, Any]:
        """ユーザが設定した属性の辞書を返す。

        Args:
            include_default_config (bool, optional): デフォルト値と同じ値も含めるか。 Defaults to False.

        Returns:
            dict[str, Any]: ユーザが設定した属性の辞書。
        """
        user: dict = self.__user__
        kp = self.key_place_cm
        ho = getattr(self, "__hidden_options__", OtsuNone)
        checker = lambda x: x in ho if ho is not OtsuNone else False
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
