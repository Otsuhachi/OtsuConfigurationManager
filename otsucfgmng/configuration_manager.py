"""設定ファイルの生成、管理を助けるクラスを定義したモジュールです。
"""

__all__ = ("BaseCM",)


import copy
import json

from pathlib import Path
from typing import Any, NoReturn, Self, cast

from otsutil import OtsuNone, load_json, pathLike, save_json
from otsuvalidator import CPath
from otsuvalidator.validators import VBool, VTuple

from .funcs import get_dict_keys_position, support_json_dump


class __MetaCM(type):
    def __new__(cls, name: str, bases: tuple, attrs: dict) -> Self:
        excludes = {
            "__module__",
            "__qualname__",
            "__defaults__",
            "__hidden_options__",
            "__annotations__",
            "__doc__",
        }
        attr_keys = set(attrs.keys()) - excludes
        if (dflt := attrs.get("__defaults__", OtsuNone)) is not OtsuNone:
            dflt = cast(dict, dflt)
            kp: dict = {}
            for k, v, position in get_dict_keys_position(dflt):
                if k not in attr_keys:
                    msg = f'属性"{k}"は宣言されていません。'
                    raise AttributeError(msg)
                if kp.get(k, OtsuNone) is not OtsuNone:
                    msg = f'属性"{k}"は異なるセクションに存在しています。'
                    raise AttributeError(msg)
                kp[k] = position
            if undefined := attr_keys - set(kp.keys()):
                msg = f"これらの属性の初期値が設定されていません。{undefined}"
                raise AttributeError(msg)
            attrs["__attr_keys__"] = attr_keys
            attrs["__key_place__"] = kp
            attrs["__user__"] = {}
        return type.__new__(cls, name, bases, attrs)


class BaseCM(metaclass=__MetaCM):
    """設定ファイル管理クラス用の基底クラスです。

    このクラスを継承したクラスに__defaults__, <attribute>を定義するだけで、設定ファイルの読み書きに必要な処理を行えるようになります。

    拡張子に制約はありませんが、読み込んだ際に辞書形式のjsonである必要があります。
    """

    __file__ = CPath(path_type=Path.is_file)
    __hidden_options__ = VTuple(str)
    __export_default_config__ = VBool()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *ex) -> bool:
        try:
            self.save_cm(self.__export_default_config__)
            if Any(ex):
                return False
            return True
        except:
            return False

    def __init__(self, file: pathLike, export_defautlt_config: bool = False) -> None:
        """設定ファイルを指定して、扱えるようにします。

        Args:
            file (pathLike): 設定ファイルのパス。
            export_defautlt_config (bool, optional): 設定ファイルを書き出す際、デフォルトと同じ値も書き出すかどうか。 Defaults to False.
        """
        self.__file__ = cast(Path, file)
        self.__export_default_config__ = export_defautlt_config
        dflt = self.defaults_cm()
        cfu = cast(dict, self.__user__)
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

    def __getattr__(self, key) -> NoReturn:
        msg = f'属性"{key}"は存在しません。'
        raise AttributeError(msg)

    def __setattr__(self, name: str, value: Any) -> None:
        nsp = name.split("_")
        if nsp[0] == "default" and nsp[-1] == "cm":
            _, *n, _ = nsp
            n = "_".join(n)
            if getattr(self, n, OtsuNone) is not OtsuNone:
                if self.__dict__.get(name, OtsuNone) is not OtsuNone:
                    msg = f'属性"{name}"は上書きできません。'
                    raise AttributeError(msg)
            else:
                msg = f'属性"{n}"が存在しないため、その初期値を表す属性"{name}"も存在しません。'
                raise AttributeError(msg)
        super().__setattr__(name, value)

    def cfg_to_str_cm(self, all: bool = False) -> str:
        """設定をjson.dumpsして返します。

        self.__hidden_options__はユーザが変更している場合のみ表示されます。

        allが有効の場合、defaults, userという2つのセクションからなる辞書として扱われます。

        Args:
            all (bool, optional): 標準設定を表示するかどうか。

        Returns:
            str: 設定の文字列。
        """
        if all:
            tmp = {"defaults": copy.deepcopy(self.defaults_cm()), "user": self.user_cm()}
            kp = cast(dict, self.key_place_cm)
            if (ho := getattr(self, "__hidden_options__", OtsuNone)) is not OtsuNone:
                ho = set(cast(tuple, ho))
                for key in ho:
                    if (place := kp.get(key, OtsuNone)) is OtsuNone:
                        continue
                    dflt = tmp["defaults"]
                    user = tmp["user"]
                    if place is not None:
                        place = cast(list[str], place)
                        for p in place:
                            dflt = dflt[p]
                            user = user[p]
                    if user.get(key, OtsuNone) is OtsuNone:
                        del dflt[key]
        else:
            tmp = self.user_cm()
        return json.dumps(tmp, indent=4, ensure_ascii=False, default=support_json_dump, sort_keys=True)

    def load_cm(self, **kwargs) -> None:
        """設定ファイルを読み込みます。

        読み込んだ設定を基にインスタンスの属性を更新します。

        Raises:
            TypeError: 設定ファイルが既定の形式ではない場合に投げられます。
        """
        if not self.__file__.exists():
            return
        kwargs["file"] = self.__file__
        try:
            jsn = load_json(**kwargs)
        except:
            return
        if not isinstance(jsn, dict):
            msg = f"{self.__file__}は対応していない形式です。"
            raise TypeError(msg)
        jsn = cast(dict, jsn)
        for key, places in self.key_place_cm.items():
            d = jsn
            if places is not None:
                for p in places:
                    d = d.get(p, OtsuNone)  # type: ignore
                    if d is OtsuNone:
                        jsctn = "->".join(places)
                        msg = f"{jsctn}が発見できませんでした。{self.__file__}が正しい形式の設定ファイルか確認してください。"
                        raise KeyError(msg)
            if (dk := d.get(key, OtsuNone)) is OtsuNone:  # type: ignore
                continue
            setattr(self, key, dk)

    def save_cm(self, export_defautlt_config: bool = False, **kwargs) -> None:
        """設定ファイルを書き出します。

        書き出す項目はユーザが変更を行ったもののみになり、クラス既定の初期設定が書き出されることはありません。

        キーワード引数にはjson.dumpで使用できる引数を与えることができます。
        一部引数は指定しなかった場合以下の値が使用されます。
        またfpはself.__file__固定になります。

        indent: 4
        encoding: utf-8
        ensure_ascii: False
        default: support_json_dump
        sort_keys: True

        Args:
            export_defautlt_config (bool, optional): 設定ファイルを書き出す際、デフォルトと同じ値も書き出すかどうか。 Defaults to False.
        """
        user = self.user_cm(export_defautlt_config)
        kwargs["file"] = self.__file__
        kwargs["data"] = user
        set_kwargs = (("indent", 4), ("ensure_ascii", False), ("default", support_json_dump), ("sort_keys", True))
        for k, v in set_kwargs:
            if kwargs.get(k, OtsuNone) is OtsuNone:
                kwargs[k] = v
        save_json(**kwargs)

    def reset_cm(self) -> None:
        """各属性を初期値に戻します。"""
        dflt = lambda x: f"default_{x}_cm"
        for key in self.attributes_cm:
            setattr(self, key, getattr(self, dflt(key)))

    def defaults_cm(self) -> dict:
        """各属性の初期値の辞書を返します。

        Returns:
            dict: 各属性の初期値です。
        """
        return copy.deepcopy(cast(dict, self.__defaults__))

    def user_cm(self, include_default_config: bool = False) -> dict:
        """ユーザが変更した属性の辞書を返します。

        Args:
            include_default_config (bool, optional): デフォルト値と同じ値も含めるか。 Defaults to False.

        Returns:
            dict: ユーザが変更した属性の辞書。
        """
        user = cast(dict, self.__user__)
        place = self.key_place_cm
        for k in self.attributes_cm:
            uv = getattr(self, k)
            dv = getattr(self, f"default_{k}_cm")
            position = place[k]
            u = user
            if position is not None:
                for p in position:
                    u = u[p]
            if not include_default_config and uv == dv:
                if u.get(k, OtsuNone) is not OtsuNone:
                    del u[k]
            else:
                u[k] = uv
        return user

    @property
    def key_place_cm(self) -> dict:
        """各属性の保存先を記録する辞書です。"""
        return copy.deepcopy(self.__key_place__)

    @property
    def attributes_cm(self) -> set:
        """クラス定義の属性名セットです。"""
        return copy.deepcopy(self.__attr_keys__)
