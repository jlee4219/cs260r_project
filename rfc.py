from sklearn.ensemble import RandomForestClassifier
import csv
import numpy as np
from sklearn.externals import joblib

data = []
targets = []
def get_data(filename):
  with open(filename, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
      row = map(int, row)
      targets.append(row[0])
      data.append(row[1:])


def run():
  get_data('results3.csv')
  count = len(targets)
  split = float(1)/2
  X_train = np.array(data[:int(count*split)])
  y_train = np.array(targets[:int(count*split)])
  X_test = np.array(data[int(count*split):])
  y_test = targets[int(count*split):]
  rfc = RandomForestClassifier()
  rfc.fit(X_train, y_train)
  predictions = rfc.predict(X_test)
  total = 0
  false_pos = 0
  false_neg = 0
  for i in range(len(y_test)):
    total += 1
    if predictions[i] != y_test[i]:
      if predictions[i] == 1:
        false_pos += 1
      else:
        false_neg += 1
  print false_pos, false_neg, total

def pickle():
  get_data('results3.csv')
  count = len(targets)
  split = 1
  X_train = np.array(data[:int(count*split)])
  y_train = np.array(targets[:int(count*split)])
  rfc = RandomForestClassifier()
  rfc.fit(X_train, y_train)
  joblib.dump(rfc, 'rfc.pkl')

pickle()