import shutil
import unittest
from pathlib import Path
from typing import cast

from otsucfgmng import BaseCM
from otsutil import load_json
from otsuvalidator import CBool, CInt, CPath, CString, VChoice


class SampleConfig(BaseCM):
    __defaults__ = {
        "app": {
            "library": "SampleLibrary.dll",
            "scripts": "SampleScripts.scrpt",
            "title": "Sample Program",
            "fullscreen": False,
        },
        "other": {
            "audio": {
                "bgm": 100,
                "bgs": 100,
                "se": 100,
                "me": 85,
            },
            "graphic": {
                "quality": "high",
            },
        },
    }
    __hidden_options__ = (
        "fullscreen",
        "me",
    )
    library = CPath("dll")
    scripts = CPath(".scrpt")
    title = CString(1, checker=str.istitle)
    fullscreen = CBool()
    bgm = CInt(0, 100)
    bgs = CInt(0, 100)
    se = CInt(0, 100)
    me = CInt(0, 100)
    quality = VChoice(("high", "low"))


class TestCase(unittest.TestCase):
    def delete_file(self) -> None:
        if not (file := self.file).exists():
            return
        if file.is_file():
            file.unlink()
        else:
            shutil.rmtree(file)

    def check_exists(self) -> None:
        self.assertEqual(self.file.exists(), True)

    def check_not_exists(self) -> None:
        self.assertEqual(self.file.exists(), False)

    def setUp(self) -> None:
        self.file = Path("./cfg.json")
        self.delete_file()

    def test_init(self) -> None:
        file = self.file
        cm = SampleConfig(file)
        self.check_not_exists()

        # with文で呼び出すと終了時にsave_cm()が実行される。
        with cm:
            pass
        self.check_exists()

    def test_library(self) -> None:
        cm = SampleConfig(self.file)
        self.assertEqual(str(cm.library.relative_to("./")), "SampleLibrary.dll")
        with self.assertRaisesRegex(ValueError, "'library'の拡張子は.dllのいずれかである必要があります"):
            cm.library = "./dll/TestLibrary.d"
        cm.library = cast("Path", "./dll/TestLibrary.dll")
        self.assertEqual(str(cm.library.relative_to("./")), "dll\\TestLibrary.dll")

    def test_bgm(self) -> None:
        cm = SampleConfig(self.file)
        self.assertEqual(cm.bgm, 100)
        cm.bgm = "92"
        self.assertEqual(cm.bgm, 92)

    def test_save(self) -> None:
        expect_cfg = {
            "app": {
                "fullscreen": True,  # __hidden_options__対象だが、設定が変更されているので出力される
                "library": "dll\\TestLibrary.dll",
                "scripts": "SampleScripts.scrpt",
                "title": "Sample Program",
            },
            "other": {
                "audio": {
                    "bgm": 92,
                    "bgs": 100,
                    # "me": 85,  # デフォルト設定値かつ__hidden_options__対象なので出力されない
                    "se": 100,
                },
                "graphic": {
                    "quality": "high",
                },
            },
        }
        file = self.file
        cm = SampleConfig(file)
        cm.library = "./dll/TestLibrary.dll"
        cm.bgm = 92
        cm.fullscreen = "yes"
        self.check_not_exists()
        cm.save_cm(True)  # デフォルト設定も出力する
        self.check_exists()
        self.assertEqual(load_json(file), expect_cfg)

        self.delete_file()
        self.check_not_exists()
        # with文利用＆デフォルト設定を出力しない
        expect_cfg = {
            "app": {
                "library": "dll\\TestLibrary.dll",
            },
            "other": {
                "audio": {
                    "bgm": 92,
                },
                "graphic": {},
            },
        }
        with SampleConfig(file) as cm:
            cm.library = "./dll/TestLibrary.dll"
            cm.bgm = 92
        self.check_exists()
        self.assertEqual(load_json(file), expect_cfg)

    def test_load(self) -> None:
        file = self.file
        self.check_not_exists()
        with SampleConfig(file) as cm:
            cm.library = "./dll/TestLibrary.dll"
            cm.bgm = 92

        self.check_exists()
        json = load_json(file)
        if not isinstance(json, dict):
            msg = "test_load実行中に予期せぬエラーが発生しました。"
            raise TypeError(msg)
        cm2 = SampleConfig(file)
        pf = json["app"]["library"]
        self.assertEqual(cm2.library, Path(pf))
        self.assertEqual(type(cm.library) is type(pf), False)
        self.assertNotEqual(cm2.bgm, 100)

    def test_user_cm(self) -> None:
        file = self.file
        with SampleConfig(file) as cm:
            expect = {
                "app": {},
                "other": {
                    "audio": {},
                    "graphic": {},
                },
            }
            self.assertEqual(cm.user_cm(), expect)

            expect = {
                "app": {
                    # "fullscreen": False,  # __hidden_options__ and default_value
                    "library": Path("SampleLibrary.dll"),
                    "scripts": Path("SampleScripts.scrpt"),
                    "title": "Sample Program",
                },
                "other": {
                    "audio": {
                        "bgm": 100,
                        # "me": 85,  # __hidden_options__ and default_value
                        "se": 100,
                        "bgs": 100,
                    },
                    "graphic": {
                        "quality": "high",
                    },
                },
            }
            self.assertEqual(cm.user_cm(True), expect)

    def test_default_attributes_cm(self) -> None:
        cm = SampleConfig(self.file)
        cm.bgm = 92.0
        self.assertEqual(cm.bgm, 92)
        self.assertEqual(cm.default_bgm_cm, 100)
        self.assertEqual(str(cm.default_library_cm), "SampleLibrary.dll")

        # 上書き禁止のテスト
        with self.assertRaisesRegex(AttributeError, "'default_bgm_cm'属性は上書きできません"):
            cm.default_bgm_cm = 50

        # 存在しないdefault_xxx_cmへのアクセス
        with self.assertRaisesRegex(AttributeError, "'dummy'属性が存在しないため、その初期値を表す'default_dummy_cm'属性も存在しません"):
            cm.default_dummy_cm = 10

    def test_reset_cm(self) -> None:
        cm = SampleConfig(self.file)

        # 値を変更
        cm.bgm = 10
        cm.quality = "low"
        cm.fullscreen = "y"

        self.assertEqual(cm.bgm, 10)
        self.assertEqual(cm.quality, "low")
        self.assertEqual(cm.fullscreen, True)

        # リセット
        cm.reset_cm()

        self.assertEqual(cm.bgm, 100)
        self.assertEqual(cm.quality, "high")
        self.assertEqual(cm.fullscreen, False)

    def test_defaults_cm(self) -> None:
        cm = SampleConfig(self.file)
        dflt = cm.defaults_cm()
        expect = {
            "app": {
                "library": Path("SampleLibrary.dll"),
                "scripts": Path("SampleScripts.scrpt"),
                "title": "Sample Program",
                "fullscreen": False,
            },
            "other": {
                "audio": {
                    "bgm": 100,
                    "bgs": 100,
                    "se": 100,
                    "me": 85,
                },
                "graphic": {
                    "quality": "high",
                },
            },
        }
        self.assertEqual(dflt, expect)

        # copy.deepcopyで返されているかの確認（元の__defaults__が汚染されていないか）
        dflt["other"]["audio"]["bgm"] = 50
        self.assertEqual(cm.default_bgm_cm, 100)
        self.assertNotEqual(cm.defaults_cm()["other"]["audio"]["bgm"], dflt["other"]["audio"]["bgm"])


if __name__ == "__main__":
    unittest.main()
