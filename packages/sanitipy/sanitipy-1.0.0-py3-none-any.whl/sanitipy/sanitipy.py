import pandas as pd
from .validator import Validator
from .preprocessor import Preprocessor

class DataCleaner:
  def __init__(self):
    # Create an instance of the Validator
    self.validator = Validator()

    # Create an instance of the Preprocessor
    self.preprocessor = Preprocessor()

  def clean_data(self, data_frame: pd.DataFrame) -> pd.DataFrame:
    missing_values: int = self.validator.check_missing_values(data_frame)
    validate_data_types: bool = self.validator.validate_data_types()
    data_frame = self.preprocessor.remove_duplicates(data_frame)

    if missing_values > 0:
      data_frame = self.preprocessor.remove_na(data_frame)
      remaining_missing_values: int = self.validator.check_missing_values(data_frame)

      if remaining_missing_values != 0:
        raise ValueError(f'Data still contains {remaining_missing_values} missing values. Check the Data Set manually')

    if not validate_data_types:
      data_frame = self.preprocessor.infer_data_types(data_frame)

    data_frame = data_frame.reset_index(drop=True)

    return data_frame
