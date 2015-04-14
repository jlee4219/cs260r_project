import csv
import cPickle as pickle

data = []
encoding = {}
val = 0

for i in range(100):
  print i
  # dictionaries to keep track of the last written
  d = {}
  dependencies = []
  failed = False
  for line in open('./data/test' + str(i) + '.out', 'r'):
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
    row = [status] + [ins for dependency in state for ins in dependency]
    data.append(row)

decoding = {}
for k, v in encoding.iteritems():
  decoding[v] = k

with open('results.csv', 'wb') as fp:
  a = csv.writer(fp, delimiter=',')
  a.writerows(data)

with open('decoding.pkl', 'wb') as fp:
  pickle.dump(decoding, fp)

print decoding
