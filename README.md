- [概要](#概要)
  - [インストール](#インストール)
  - [使い方](#使い方)
  - [メソッド一覧](#メソッド一覧)
  - [Q\&A](#qa)


# 概要

このライブラリはjson形式の設定ファイルの読み書きを補助するための基底クラスです。  
`BaseCM`クラスを継承し、`__defaults__`, `<attributes>`を定義するだけで必要な操作を行えるようになります。  

~~現在~~違うセクションに同じキーを持つような設定ファイルには対応していません。  
**対応しないことに決定しました。**([理由はこちら](#なぜ異なるセクションで同名キーを持てないようにしましたか？))  

このライブラリは以下の環境で作成されています。
`Windows10(64bit)`, `Python3.11.1`

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
   - 自作クラスなどを使用したい場合には[OtsuValidator](https://github.com/Otsuhachi/OtsuValidator#%E7%B6%99%E6%89%BF%E8%A6%8F%E5%89%87)や実際のコードを参考に定義する([参考例](#自作クラスを使用する場合に必要なバリデータとコンバータをどう用意すればいいですか？))
1. `otsucfgmng`をインポートし、`BaseCM`を使用できるようにする
1. `BaseCM`を継承したクラスを定義する
   1. 属性`__defaults__`に辞書形式で利用する属性名とその初期値を与える
   1. `__hidden_options__`で隠しオプションを設定する (必要に応じて)
   1. `__defaults__`で宣言した属性名に1.で用意したコンバータを与える
1. 設定ファイルのパスを与えてインスタンスを作成する
1. インスタンスの属性を書き換えて編集を行う
1. `save_cm`を呼び出せば設定ファイルが出力される

<!-- omit in toc -->
### 実行例-設定ファイル管理クラス

<!-- no toc -->
- [作成](#作成-設定ファイル管理クラス)
- [読み込み](#読み込み-設定ファイル管理クラス)

<!-- omit in toc -->
### 作成-設定ファイル管理クラス


[実行例](#実行例-設定ファイル管理クラス)に戻る  

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

    # 3.3.
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

```json

{
    "app": {},
    "audio": {
        "bgm": 99,
        "bgs": 50
    }
}
```

<!-- omit in toc -->
### 読み込み-設定ファイル管理クラス
[実行例](#実行例-設定ファイル管理クラス)に戻る  

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
### 出力は以下のようになります ###
{'app': {}, 'audio': {'bgs': 50, 'bgm': 99}}
{'app': {'fullscreen': True}, 'audio': {'bgs': 50, 'bgm': 99}}
```


上記の処理で作成された`cfg.json`の中身は以下の通りです。  


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

<!-- omit in toc -->
### 隠しオプション

[先ほどのコード](#読み込み-設定ファイル管理クラス)に隠しオプションを追加します。  
方法はシンプルで、`__hidden_options__`に対象の属性名のタプルを渡すだけです。  
今回は`fullscreen`と`me`属性を隠しオプションにしてみます。


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
    __hidden_options__ = ('fullscreen', 'me')  # この行を追加
    library = CPath('dll')
    scripts = CPath('scrpt')
    title = CString(1, checker=str.istitle)
    fullscreen = CBool()
    bgm = CInt(0, 100)
    bgs = CInt(0, 100)
    se = CInt(0, 100)
    me = CInt(0, 100)


with ConfigurationManager('cfg.json') as cm:
    print(cm.cfg_to_str_cm(True))

```

出力

```json

{
    "defaults": {
        "app": {
            "fullscreen": false,
            "library": "SampleLibrary.dll",
            "scripts": "SampleScripts.scrpt",
            "title": "Sample Program"
        },
        "audio": {
            "bgm": 100,
            "bgs": 100,
            "se": 100
        }
    },
    "user": {
        "app": {
            "fullscreen": true
        },
        "audio": {
            "bgm": 99,
            "bgs": 50
        }
    }
}
```

`cfg.json`は[ここ](#読み込み-設定ファイル管理クラス)で作成されたものが存在する前提になります。  
隠しオプションに設定した`me`は表示されていませんが、`fullscreen`は表示されていることがわかるかと思います。  
これは`fullscreen`が変更可能であることを知っている場合には隠す意味がないからです。


## メソッド一覧

`argparse`や`GUI`などで設定項目を編集するための補助を想定しています。  
`show`コマンドを作成して`cfg_to_str_cm`を制御するなど、自身のUIに合うように紐づけて使ってください。

名前|概要|戻り値|戻り値型
:--:|:--|:--:|:--:
cfg_to_str_cm|設定を`json.dumps`して返す<br>`all`を`True`にしている場合は標準設定も表示される<br>ユーザが変更していない`__hidden_options__`は表示されない<br>ユーザに設定を見せる場合にはこのメソッドを使って出力する|設定|str
load_cm|設定ファイルを読み込む<br>`__init__`から勝手に呼び出されるので、基本的に使用する必要はない||None
save_cm|現在の設定を書き出す<br>コンテキストマネージャを使用していれば勝手に呼び出される||None
reset_cm|各属性を初期値に戻す||None
defaults_cm|`__defaults__`のコピーを返す|初期設定|dict
user_cm|ユーザが変更した属性の辞書を返す|変更された設定|dict
key_place_cm|各属性がどのセクションに属するかを記録した辞書を返す<br>ユーザにアクセスを許すと`__hidden_options__`が意味をなくす|属性の所属先|dict
attributes_cm|設定項目の一覧を返す<br>ユーザにアクセスを許すと`__hidden_options__`が意味をなくす|設定項目の一覧|set



## Q&A

以下の説明で`cm`が登場した場合、ユーザが定義した設定ファイル管理クラスのインスタンスだと解釈してください。

- [なぜ異なるセクションで同名キーを持てないようにしましたか？](#なぜ異なるセクションで同名キーを持てないようにしましたか？)
- [自作クラスを使用する場合に必要なバリデータとコンバータをどう用意すればいいですか？](#自作クラスを使用する場合に必要なバリデータとコンバータをどう用意すればいいですか？)



<!-- omit in toc -->
### なぜ異なるセクションで同名キーを持てないようにしましたか？

1. 残念ながらライブラリ作成者の技術的な面も大きいです。
1. 後述する理由を克服、緩和する方法が追加、あるいは理解できれば異なるセクションでの同名キーを持てるようになる可能性も**なくはないです**。

ロガーの設定ファイルなど、異なるセクションで同名キーを持ちたい状況はありますが、それに対応する場合、アクセスが複雑になりすぎる恐れがあります。  

例えば、現在の属性へのアクセス`cm.<key>`に加えて、辞書を持つキーを`Section`クラスとして変換すれば`cm.<section>.<key>`, `cm.<sectionA>.<sectionB>.~.<key>`というように管理することは技術的に可能になります。

しかしそうなると、[実行例](#実行例)で使用したような構造の設定ではアクセスが煩雑になるデメリットもあります。  
`cm.fullscreen`でアクセスしていたものが`cm.app.fullscreen`となる等。  
また、動的にクラスを生成する都合上、コード入力支援が受けられず、ヒューマンエラーのリスクも上がってしまいます。

<!-- omit in toc -->
### 自作クラスを使用する場合に必要なバリデータとコンバータをどう用意すればいいですか？

1. `otsuvalidator.bases`から`Converter`, `Validator`をインポートし、使用できるようにする
   1. その他必要なライブラリをインポート
1. 自作クラスを定義する
   1. 好きなようにクラスを設計する (`__eq__`メソッドを定義していない場合`__hidden_options__`が正常に機能しない場合があります)
   1. `__str__`か`to_json`メソッドを定義する
1. 自作クラスに対応した`Validator`を定義する(以下そのValidatorを`VMyClass`とする)
1. `VMyClass`と`Converter`を継承した`CMyClass`を定義する
1. [使い方](#使い方)どおり


<!-- omit in toc -->
#### 実行例-自作クラスの使用

<!-- no toc -->
- [作成](#作成-自作クラスの使用)
- [読み込み](#読み込み-自作クラスの使用)


<!-- omit in toc -->
##### 作成-自作クラスの使用

[実行例](#実行例-自作クラスの使用)に戻る  

`my_company.json`という設定ファイルを作成していきます。  

`ConfigurationManager`では`json.dump`できない属性は`otsucfgmng.funcs.support_json_dump`関数で変換を試みます(※独自に指定しない限り)  
この関数では`to_json`を持つクラスを`cls.to_json`で、それ以外のクラスを`str(cls)`で変換します。  
なので、`cls.to_json`で返る値を`cls`に復元できるような`Converter`を定義すれば読み込み時に復元されます。

```python

# 1. & 1.1.
from typing import Any

from otsuvalidator import CNoneable
from otsuvalidator.bases import Converter, Validator

from otsucfgmng import BaseCM


# 2.
class Person:
    # 2.1.
    def __init__(self, name: str, age: int, gender: str):
        self.name = name
        self.age = age
        self.gender = gender

    def show_profile(self):
        print(self)

    # 2.2.
    def __str__(self) -> str:
        data = (
            ('名前', self.name),
            ('年齢', self.age),
            ('性', self.gender),
        )
        prof = []
        for k, v in data:
            prof.append(f'{k}\t: {v}')
        prof = '\n'.join(prof)
        return prof

    def to_json(self) -> dict:
        data = {'name': self.name, 'age': self.age, 'gender': self.gender}
        return data


# 3.
class VPerson(Validator):
    def validate(self, value: Any) -> Person:
        if type(value) is not Person:
            msg = self.ERRMSG('Person型である必要があります', value)
            raise TypeError(msg)
        return value


# 4.
class CPerson(VPerson, Converter):
    def validate(self, value: Any) -> Person:
        if type(value) is not Person:
            try:
                if isinstance(value, dict):
                    value = Person(**value)
                else:
                    raise TypeError
            except:
                msg = self.ERRMSG('Person型として扱える必要があります。', value)
                raise TypeError(msg)
        return super().validate(value)

    def super_validate(self, value: Any) -> Person:
        return super().super_validate(value)


# 5.
class ConfigurationManager(BaseCM):
    __defaults__ = {
        'president': Person('山田太郎', 28, '男'),
        'employee': {
            'director': Person('部長花子', 28, '女'),
            'manager': Person('課長夢', 28, '女'),
            'chief': Person('係長次郎', 28, '男')
        }
    }
    president = CPerson()
    director = CNoneable(CPerson())
    manager = CNoneable(CPerson())
    chief = CNoneable(CPerson())


with ConfigurationManager('my_company.json') as cm:
    cm.president = Person('乙八', 28, '男')
    cm.director = Person('部長夢', 28, '女')
    cm.manager = None
    cm.chief = None
```

上記の処理で作成された`my_company.json`の中身は以下の通りです。  


```json

{
    "employee": {
        "chief": null,
        "manager": null,
        "director": {
            "name": "部長夢",
            "age": 28,
            "gender": "女"
        }
    },
    "president": {
        "name": "乙八",
        "age": 28,
        "gender": "男"
    }
}
```

定義通り`Person`クラスは`person.to_json`を通して辞書形式に変換されていることがわかります。

<!-- omit in toc -->
##### 読み込み-自作クラスの使用

[実行例](#実行例-自作クラスの使用)に戻る  

```python

# 1. & 1.1.
from typing import Any

from otsuvalidator import CNoneable
from otsuvalidator.bases import Converter, Validator

from otsucfgmng import BaseCM


# 2.
class Person:
    # 2.1.
    def __init__(self, name: str, age: int, gender: str):
        self.name = name
        self.age = age
        self.gender = gender

    def show_profile(self):
        print(self)

    # 2.2.
    def __str__(self) -> str:
        data = (
            ('名前', self.name),
            ('年齢', self.age),
            ('性', self.gender),
        )
        prof = []
        for k, v in data:
            prof.append(f'{k}\t: {v}')
        prof = '\n'.join(prof)
        return prof

    def to_json(self) -> dict:
        data = {'name': self.name, 'age': self.age, 'gender': self.gender}
        return data


# 3.
class VPerson(Validator):
    def validate(self, value: Any) -> Person:
        if type(value) is not Person:
            msg = self.ERRMSG('Person型である必要があります', value)
            raise TypeError(msg)
        return value


# 4.
class CPerson(VPerson, Converter):
    def validate(self, value: Any) -> Person:
        if type(value) is not Person:
            try:
                if isinstance(value, dict):
                    value = Person(**value)
                else:
                    raise TypeError
            except:
                msg = self.ERRMSG('Person型として扱える必要があります。', value)
                raise TypeError(msg)
        return super().validate(value)

    def super_validate(self, value: Any) -> Person:
        return super().super_validate(value)


# 5.
class ConfigurationManager(BaseCM):
    __defaults__ = {
        'president': Person('山田太郎', 28, '男'),
        'employee': {
            'director': Person('部長花子', 28, '女'),
            'manager': Person('課長夢', 28, '女'),
            'chief': Person('係長次郎', 28, '男')
        }
    }
    president = CPerson()
    director = CNoneable(CPerson())
    manager = CNoneable(CPerson())
    chief = CNoneable(CPerson())


with ConfigurationManager('my_company.json') as cm:
    for i, key in enumerate(('president', 'director', 'manager', 'chief')):
        if i:
            print('-' * 75)
        print(f'{key}\n{getattr(cm,key)}')

```

```console

### 出力は以下のようになります ###
president
名前    : 乙八
年齢    : 28
性      : 男
---------------------------------------------------------------------------
director
名前    : 部長夢
年齢    : 28
性      : 女
---------------------------------------------------------------------------
manager
None
---------------------------------------------------------------------------
chief
None
```
