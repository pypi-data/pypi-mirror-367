python3 setup.py check


rm  build/
rm  dist/

python -m build
twine upload dist/*