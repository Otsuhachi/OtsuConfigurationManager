- [otsucfgmng](#otsucfgmng)
  - [主な特徴](#主な特徴)
  - [インストール](#インストール)
  - [基本的な使い方](#基本的な使い方)
    - [1. 設定クラスの定義](#1-設定クラスの定義)
    - [2. コンテキストマネージャによる自動保存](#2-コンテキストマネージャによる自動保存)
    - [3. 設定のリセットとデフォルト値の参照](#3-設定のリセットとデフォルト値の参照)
  - [APIリファレンス（`BaseCM`主要メソッド）](#apiリファレンスbasecm主要メソッド)
  - [ライセンス](#ライセンス)

---

# otsucfgmng
`otsucfgmng`は、Pythonアプリケーションにおける設定ファイル（JSON）の読み書き・バリデーション・永続化を直感的に扱うためのライブラリです。  
  
クラス定義として設定項目と初期値を記述するだけで、ネストされたJSON設定ファイルの読み込み、型チェック / バリデーション、デフォルト値からの最小保存、コンテキストマネージャによる自動保存などの機能を一元管理できます。  

---

## 主な特徴

- **クラスベースの宣言型設定:** `BaseCM`を継承し、メタデータや初期値（`__defaults__`）を記述するだけで簡単に設定クラスを作成できます。
- **バリデータとの連携:** `otsuvalidator`などのディスクリプタ(`CPath`, `CInt`, `CString`, `CBool`等)と組み合わせることで、設定値の設定時に自動でバリデーションや型変換が行われます。
- **ネストされたJSONの自動ハンドリング:** 多層構造の辞書（セクション）も自動的に平坦な属性としてマッピングし、出力時には元の構造へ復元します。
- **差分のみの最小保存:** 初期値から変更されたユーザ設定のみをJSONファイルに書き出すため、設定ファイルが冗長になりません（非表示オプションや全出力の制御も可能）。
- **コンテキストマネージャ対応:** `with`構文を利用することで、スコープ脱出時に設定変更を自動でファイルへ保存します。
- **型補完（Protocol）のサポート:** IDEでの保管や静的型チェック（mypy / pyright）用に`PBaseCM`プロトコルを提供しています。

---

## インストール

依存ライブラリとして`otsutil`および`otsuvalidator`が必要です。

```bash
pip install otsucfgmng
```

## 基本的な使い方

最終的なコードは`./sample_code.py`を参照してください。

### 1. 設定クラスの定義

`BaseCM`を継承し、`__defaults__`に初期値の辞書を定義します。各設定項目には`otsuvalidator`等のバリデータ属性を割り当てます。

```python

from pathlib import Path
from typing import Any

from otsuvalidator import CBool, CInt, CPath, CString, VChoice

from otsucfgmng import BaseCM, PBaseCM


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
```

### 2. コンテキストマネージャによる自動保存

`with`スコープ内で値を変更すると、スコープを抜ける際に変更内容が自動的にJSONファイルへ保存されます。

```python

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
```

### 3. 設定のリセットとデフォルト値の参照

各設定項目には、自動的に上書き不可の初期値参照属性（`default_<属性名>_cm`）が生成されます。  
また、`reset_cm()`を呼び出すことでいつでも全設定を初期値に戻せます。

```python

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
```

## APIリファレンス（`BaseCM`主要メソッド）

メソッド / 属性|説明
:--:|:--:
`load_cm(**kwargs)`|設定ファイルからJSONデータを読み込み、各属性へ値を反映します。
`save_cm(export_default_config=False, **kwargs)`|現在の設定状況をJSONファイルに保存します。
`reset_cm()`|すべての設定属性を定義時のデフォルト値に初期化します。
`defaults_cm()`|定義されているデフォルト値の辞書（ディープコピー）を取得します。
`user_cm(include_default_config=False)`|ユーザが変更した設定項目のみの辞書構造を取得します。
`cfg_to_str_cm(all_=False)`|現在の設定を整形されたJSON文字列として返します（デバッグ・表示用）。
`attributes_cm`|（プロパティ）設定項目として登録されている属性名のセットを取得します。
`key_places_cm`|（プロパティ）各属性が辞書のどの階層セクションに属しているかのマップを取得します。

## ライセンス

`MIT License`
