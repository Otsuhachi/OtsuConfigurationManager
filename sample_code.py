from pathlib import Path

from otsuvalidator import CBool, CInt, CPath, CString, VChoice

from otsucfgmng import BaseCM


class AppConfig(BaseCM):
    # 1. デフォルト設定の定義（ネスト構造に対応）
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

    # 2. 保存時に無視・非表示にするオプション（任意）
    __hidden_options__ = ("fullscreen", "me")

    # 3. 各属性に対するバリデータ・型コンバータの設定
    library = CPath("dll")
    scripts = CPath(".scrpt")
    title = CString(1, checker=str.istitle)
    fullscreen = CBool()
    bgm = CInt(0, 100)
    bgs = CInt(0, 100)
    se = CInt(0, 100)
    me = CInt(0, 100)
    quality = VChoice(("high", "low"))


# 2. コンテキストマネージャによる自動保存
pf_cfg = Path("./cfg.json")

# コンテキストマネージャで開く
with AppConfig(pf_cfg) as cfg:
    # 属性としてアクセス可能
    print(cfg.bgm)  # => 100（初期値）

    cfg.bgm = 92
    cfg.library = "./dll/TestLibrary.dll"
# スコープ脱出時に`cfg.json`が自動更新される
# 差分（デフォルトと異なる値）のみがJSONに出力されます

# 3. 設定のリセットとデフォルト値の参照
with AppConfig(pf_cfg) as cfg:
    cfg.bgm = 10
    print(cfg.bgm)  # => 10
    print(cfg.default_bgm_cm)  # => 100（初期値）

    # 初期属性値への直接代入はエラーになります
    # cfg.default_bgm_cm = 50  # AttributeError

    # 初期値へリセット
    cfg.reset_cm()
    print(cfg.bgm)  # => 100
