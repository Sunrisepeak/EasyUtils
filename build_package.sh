###
 # @Author: SPeak
 # @Date: 2022-05-04 19:34:17
 # @LastEditors: SPeak
 # @LastEditTime: 2022-05-04 19:36:38
 # @FilePath: /EasyUtils/build_package.sh
###
rm dist/*
python3 -m build
python3 -m twine upload --repository pypi dist/*

