# 概要

このライブラリは設定ファイルの読み書きを補助するための基底クラスです。  
`BaseCM`クラスを継承し、`__defaults__`, `<attributes>`を定義するだけで必要な操作を行えるようになります。

**現在違うセクションに同じキーを持つような設定ファイルには対応していません。**
```python
# 違うセクションに同じキーを持つ例
{
    'app': {'name': 'Hello'},
    'default': {'name': 'Python'}
}
```

## インストール

インストール

`pip install otsucfgmng`

アップデート

`pip install -U otsucfgmng`

アンインストール

`pip uninstall otsucfgmng`

## 使い方

1. `otuvalidator`をインポートし、必要なバリデータ、コンバータを使用できるようにする
   - 自作クラスなどを使用したい場合には[OtsuValidator](https://github.com/Otsuhachi/OtsuValidator#%E7%B6%99%E6%89%BF%E8%A6%8F%E5%89%87)や実際のコードを参考に定義する
1. `otsucfgmng`をインポートし、`BaseCM`を使用できるようにする
1. `BaseCM`を継承したクラスを定義する
   1. 属性`__defaults__`に辞書形式で利用する属性名とその初期値を与える
   1. `__defaults__`で宣言した属性名に1.で用意したコンバータを与える
1. 設定ファイルのパスを与えてインスタンスを作成する
1. インスタンスの属性を書き換えて編集を行う
1. `save_cm`を呼び出せば設定ファイルが出力される

### 実行例

#### 作成

`cfg.json`という設定ファイルを作成していきます。

```python

# 1.
from otsuvalidator import CBool, CInt, CPath, CString

# 2.
from otsucfgmng import BaseCM


# 3.
class ConfigurationManager(BaseCM):
    # 3.1.
    __defaults__ = {
        'app': {
            'library': 'SampleLibrary.dll',
            'scripts': 'SampleScripts.scrpt',
            'title': 'Sample Program',
            'fullscreen': False
        },
        'audio': {
            'bgm': 100,
            'bgs': 100,
            'se': 100,
            'me': 85
        }
    }

    # 3.2.
    library = CPath('dll')
    scripts = CPath('scrpt')
    title = CString(1, checker=str.istitle)
    fullscreen = CBool()
    bgm = CInt(0, 100)
    bgs = CInt(0, 100)
    se = CInt(0, 100)
    me = CInt(0, 100)


# 4.
cm = ConfigurationManager('cfg.json')

# 5.
cm.bgm = 99
cm.bgs = 50

# 6.
cm.save_cm()
```

上記の処理で作成された`cfg.json`の中身は以下の通りです。  
**実行するたびにキーの並びは異なります。**

```json

{
    "app": {},
    "audio": {
        "bgm": 99,
        "bgs": 50
    }
}
```

#### 読み込み

正しい形式で出力された設定ファイルをインスタンスの生成時に与えると自動で設定を読み込みます。

```python

from otsuvalidator import CBool, CInt, CPath, CString

from otsucfgmng import BaseCM


class ConfigurationManager(BaseCM):
    __defaults__ = {
        'app': {
            'library': 'SampleLibrary.dll',
            'scripts': 'SampleScripts.scrpt',
            'title': 'Sample Program',
            'fullscreen': False
        },
        'audio': {
            'bgm': 100,
            'bgs': 100,
            'se': 100,
            'me': 85
        }
    }
    library = CPath('dll')
    scripts = CPath('scrpt')
    title = CString(1, checker=str.istitle)
    fullscreen = CBool()
    bgm = CInt(0, 100)
    bgs = CInt(0, 100)
    se = CInt(0, 100)
    me = CInt(0, 100)

# コンテキストマネージャを使用すると自動でsave_cmされます。
with ConfigurationManager('cfg.json') as cm:
    print(cm.user_cm())
    cm.fullscreen = 'yes'
    print(cm.user_cm())
```

```python
### 出力は以下のようになります (実行するたびにキーの並びは異なります) ###
{'app': {}, 'audio': {'bgs': 50, 'bgm': 99}}
{'app': {'fullscreen': True}, 'audio': {'bgs': 50, 'bgm': 99}}
```


上記の処理で作成された`cfg.json`の中身は以下の通りです。  
**実行するたびにキーの並びは異なります。**

```json

{
    "app": {
        "fullscreen": true
    },
    "audio": {
        "bgs": 50,
        "bgm": 99
    }
}
```
