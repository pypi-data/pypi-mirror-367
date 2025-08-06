from setuptools import setup, find_packages

setup(
  name='sanitipy',
  description='Sanitipy is a user-friendly Python library designed for data cleaning and preprocessing. It provides essential utilities to streamline the process of preparing datasets for analysis or modeling. With features such as duplicate removal, handling missing values, and automatic data type inference, sanitipy simplifies the data cleaning workflow, making it a useful tool for data scientists and analysts.',
  author='Adam Ben-Aamr',
  author_email='adambenaamr@gmail.com',

  # Note: Always update the version number
  version='1.0.1',
  packages=find_packages(),
  install_requires=[
    # Add dependencies here.
    'pandas',
    'numpy',
    'scikit-learn',
    'matplotlib',
  ],
  url='https://github.com/yestab335/sanitipy',
  download_url='',
  keywords=[
    'data',
    'data cleaning',
    'missing data',
    'data science',
    'pandas',
    'python'
  ],
)
