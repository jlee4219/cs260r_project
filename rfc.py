from sklearn.ensemble import RandomForestClassifier
import csv
import numpy as np
from sklearn.externals import joblib
import cPickle
import sys

if len(sys.argv) < 2:
  sys.exit()
csvfile = sys.argv[1]
if len(sys.argv) > 2:
  pklfile = sys.argv[2]
else:
  pklfile = "decoding.pkl"

data = []
targets = []

def get_data(filename):
  with open(filename, 'rb') as fp:
    reader = csv.reader(fp, delimiter=',')
    for row in reader:
      row = map(int, row)
      targets.append(row[0])
      data.append(row[1:])
  with open(pklfile, 'rb') as fp:
    decoding = cPickle.load(fp)
  return decoding

def run():
  decoding = get_data(csvfile)
  count = len(targets)
  split = float(4)/8
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
  pos = 0
  neg = 0
  for i in range(len(y_test)):
    total += 1
    if y_test[i] == 0:
      pos += 1
    else:
      neg += 1
    if predictions[i] == 1:
      output = "Failure: "
      output += str(decoding[X_test[i,-2]]) + " read after "
      output += str(decoding[X_test[i,-1]]) + " wrote."
      print output
    if predictions[i] != y_test[i]:
      if predictions[i] == 1:
        false_pos += 1
      else:
        false_neg += 1
  print "False positives:", false_pos/float(pos)
  print "False negatives:", false_neg/float(neg)

def pickle():
  get_data('new_tests.csv')
  count = len(targets)
  split = 1
  X_train = np.array(data[:int(count*split)])
  y_train = np.array(targets[:int(count*split)])
  rfc = RandomForestClassifier()
  rfc.fit(X_train, y_train)
  joblib.dump(rfc, './pkl/rfc.pkl')

run()
