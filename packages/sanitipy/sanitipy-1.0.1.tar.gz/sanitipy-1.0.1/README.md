# SanitiPy - Automatic Data Cleaner
<!-- Badges go here -->

**SanitiPy automates the data cleaning process for your data science projects using Python.**

```zsh
pip install sanitipy
```

After running the install command, run:

```zsh
pip list
```

On ran, verify the following packages are installed as well:
* Pandas
* NumPy
* Scikit-Learn
* Matplotlib

## Command to generate the package
```zsh
python setup.py sdist bdist_wheel
```

## Command to upload dist folder to PyPi
```zsh
twine upload dist/*
```
