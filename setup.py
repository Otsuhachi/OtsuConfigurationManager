from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()
with open("LICENSE.txt", "r", encoding="utf-8") as f:
    lcs = f.read()

__VERSION__ = "1.3.2.37"

setup(
    name="otsucfgmng",
    version=__VERSION__,
    url="https://github.com/Otsuhachi/OtsuConfigurationManager.git",
    description="設定ファイルを扱うクラスを生成するライブラリです。",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Otsuhachi",
    author_email="agequodagis.tufuiegoeris@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    license=lcs,
    keywords="Python ConfigurationManager Configure json",
    install_requires=[
        "otsuvalidator",
        "otsutil",
    ],
    python_requires=">=3.7",
)
