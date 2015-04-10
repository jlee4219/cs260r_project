import csv
import numpy as np

class CSVData():
  def __init__(self, filename):
    self.filename = filename
    self.cur_row = 0
    self.num_rows = 0
    X = []
    y = []
    with open('train.csv', 'rb') as csvfile:
      r = csv.reader(csvfile, delimiter=',')
      for row in r:
        X_i, y_i = self.row_to_data(row)
        self.num_rows += 1
        X.append(X_i)
        y.append(y_i)
    self.X = X
    self.y = y

  def get_data(self):
    if self.cur_row >= self.num_rows:
      return None, None
    else:
      self.cur_row += 1
      return self.X[self.cur_row-1], self.y[self.cur_row-1]

  def row_to_data(self, row):
    data = map(int, row)
    X = np.array(data[1:]).reshape(1, len(row) - 1)
    y = np.array(data[0]).reshape(1, 1)
    return X, y