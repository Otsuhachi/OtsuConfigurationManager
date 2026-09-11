import re
from pathlib import Path

from setuptools import find_packages, setup

pd_this = Path(__file__).parent

with (pd_this / "README.md").open("r", encoding="utf-8") as f:
    readme = f.read()

with (pd_this / "LICENSE.txt").open("r", encoding="utf-8") as f:
    lcs = f.read()

with (pd_this / "otsucfgmng/__init__.py").open("r", encoding="utf-8") as f:
    for line in (ln.rstrip() for ln in f):
        if (find := re.fullmatch(r'__VERSION__ = "([^"]+)"', line)) is None:
            continue
        __VERSION__ = find.groups()[0]
        break
    else:
        msg = "`otsucfgmng`バージョン情報を取得できませんでした。"
        raise ValueError(msg)

setup(
    name="otsucfgmng",
    version=__VERSION__,
    url="https://github.com/Otsuhachi/OtsuConfigurationManager.git",
    description="設定ファイルを扱うクラスを生成するライブラリです。",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Otsuhachi",
    author_email="agequodagis.tufuiegoeris@gmail.com",
    packages=find_packages(where=".", include=["otsucfgmng*"]),
    include_package_data=True,
    license=lcs,
    keywords="Python ConfigurationManager Configure json",
    install_requires=[
        "otsuvalidator",
        "otsutil",
    ],
    python_requires=">=3.12",
)
