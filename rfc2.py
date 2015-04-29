from sklearn.ensemble import RandomForestClassifier
import csv
import numpy as np
from sklearn.externals import joblib
import cPickle
import sys

if len(sys.argv) < 2:
  csvfile = None
else:
  csvfile = sys.argv[1]
if len(sys.argv) > 2:
  pklfile = sys.argv[2]
else:
  pklfile = "decoding.pkl"

data = []
targets = []

def gen_dependencies(dir, csvfile, pklfile, N, output=True):
  val = 0
  X = []
  encoding = {}
  index = 0
  for i in range(N):
    print i
    # dictionaries to keep track of the last written
    d = {}
    dependencies = []
    failed = False
    for line in open('./'+dir+'/trace' + str(i) + '.out', 'r'):
      # instruction pointer, R/W, location
      ins = line.split()
      if len(ins) == 1 and ins[0] == '1':
        failed = True
        print "Failed"
      else:
        ip = int(ins[0])
        ea = int(ins[2])
        if ip not in encoding:
          val += 1
          encoding[ip] = val
        index = encoding[ip]
        if ins[1] == 'W':
          d[ea] = index
        else:
          if ea in d:
            dependencies.append([index, d[ea]])

    # get the last 5 dependencies
    for i in range(4,len(dependencies)):
      state = dependencies[(i-4):(i+1)]
      status = 0
      if failed:
        status = 1
      X.append([ins for dependency in state for ins in dependency])
      targets.append(status)

  decoding = {}
  for k, v in encoding.iteritems():
    decoding[v] = k

  if output:
    with open(csvfile, 'wb') as fp:
      a = csv.writer(fp, delimiter=',')
      a.writerows(X)

    with open(pklfile, 'wb') as fp:
      pickle.dump(decoding, fp)
  return X, decoding

def get_data(filename):
  if filename:
    with open(filename, 'rb') as fp:
      reader = csv.reader(fp, delimiter=',')
      for row in reader:
        row = map(int, row)
        targets.append(row[0])
        data.append(row[1:])
    with open(pklfile, 'rb') as fp:
      decoding = cPickle.load(fp)
  else:
    gen_dependencies("traces", None, None, 10, False)

def run():
  X, decoding = gen_dependencies("traces", None, None, 10, False)
  count = len(targets)
  split = float(1)/2
  X_train = np.array(X[:int(count*split)])
  y_train = np.array(targets[:int(count*split)])
  X_test = np.array(X[int(count*split):])
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
