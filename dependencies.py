import csv
import cPickle as pickle
import sys

if len(sys.argv) < 2:
  print "Please specify a directory."
  sys.exit()

data = []
encoding = {}
dir = sys.argv[1]
if len(sys.argv) > 2:
  csvfile = sys.argv[2]
else:
  csvfile = "dependencies.csv"
if len(sys.argv) > 3: 
  pklfile = sys.argv[3]
else:
  pklfile = "decoding.pkl"
if len(sys.argv) > 4:
  N = sys.argv[4]
else:
  N = 100

def gen_dependencies(csvfile, pklfile, N, output=True):
  val = 0
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
            # read, write
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

  if output:
    with open(csvfile, 'wb') as fp:
      a = csv.writer(fp, delimiter=',')
      a.writerows(data)

    with open(pklfile, 'wb') as fp:
      pickle.dump(decoding, fp)
  return data, decoding

gen_dependencies(csvfile, pklfile, 1, True)