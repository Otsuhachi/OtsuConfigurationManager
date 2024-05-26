pipenv run py .\setup.py bdist_wheel
twine upload dist/*
Remove-Item ./build/ -Recurse -Force
Remove-Item ./dist/ -Recurse -Force
Remove-Item ./otsucfgmng.egg-info/ -Recurse -Force
