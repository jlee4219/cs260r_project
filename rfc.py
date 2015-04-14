from sklearn.ensemble import RandomForestClassifier
import csv
import numpy as np
from sklearn.externals import joblib
import cPickle

data = []
targets = []

def get_data(filename):
  with open(filename, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
      row = map(int, row)
      targets.append(row[0])
      data.append(row[1:])
  with open('decoding.pkl', 'rb') as fp:
    decoding = cPickle.load(fp)
  return decoding

def run():
  decoding = get_data('results.csv')
  count = len(targets)
  split = float(1)/3
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
        # print "Failure! ", [decoding[ins] for ins in X_test[i,:]]
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
