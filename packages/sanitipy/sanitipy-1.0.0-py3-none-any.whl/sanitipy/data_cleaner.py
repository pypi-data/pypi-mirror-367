import pandas as pd
from .validator import Validator
from .preprocessor import Preprocessor

class DataCleaner:
  def __init__(self, data: pd.DataFrame):
    self.data = data
    self.validator = Validator(data)
    self.preprocessor = Preprocessor(data)
  
  def remove_duplicates(self):
    self.data = self.data.drop_duplicates()

    return self.data
  
  def remove_na(self):
    self.data = self.data.dropna()

    return self.data
  
  def clean_data(self):
    self.validator.check_missing_values()
    
    self.data = self.preprocessor.normalize_data()

    return self.data
