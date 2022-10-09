import pandas as pd
import json

class MoviesData:
  def __init__(self) -> None:
    self.load_dataset()
    pass

  def load_dataset(self):
    df = pd.read_csv('datasets/movies/movies_metadata.csv')
    print(df.head())
    print(df.iloc[0]['belongs_to_collection'])
    print(df.columns)
    y = self.json_dict(df.iloc[0]['belongs_to_collection'])
    print(y['name'])
    return 0
  
  def get_movies(self):
    return 0
  
  def json_dict(self, x):
    x = x.replace("\'", "\"")
    return json.loads(x)

MoviesData()