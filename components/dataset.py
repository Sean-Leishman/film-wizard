import pandas as pd
import json
import os

class MoviesData:
  def __init__(self) -> None:
    cwd = os.path.realpath(__file__)
    file_loc = '/'.join(cwd.split('/')[:-2]) + '/datasets/movies/movies_metadata.csv'
    self.load_dataset(file_loc)
    pass

  def load_dataset(self, file_loc):
    df = pd.read_csv(file_loc)
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