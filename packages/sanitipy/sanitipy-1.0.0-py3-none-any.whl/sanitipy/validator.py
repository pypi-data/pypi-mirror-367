class Validator:
  def validate_data_types(self) -> bool:
    # Check for consistent data types
    if self.empty: # type: ignore
      return True
    
    data_types = self.dtypes # type: ignore

    if data_types.nunique() == 1:
      return True
    else:
      return False
    
  def check_missing_values(self, data) -> int:
    data = data

    # Identify missing values in the dataset
    return data.isnull().sum()
