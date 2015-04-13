import csv 

data = []
for i in range(50):
  print i
  # find the lowest valued instruction
  vals = sorted([int(line.split()[0][:-1], 0) for line in open('./data/test' + str(i) + '.out', 'r') if len(line.split()) == 3 and line.count('x') == 2])
  # dictionaries to keep track of the last written
  d = {}
  dependencies = []
  failed = False
  for line in open('./data/test' + str(i) + '.out', 'r'):
    # instruction pointer, R/W, location
    ins = line.split()
    if len(ins) >= 1 and ins[0] == '1':
      failed = True
      print "Failed"
    elif len(ins) != 3 or line.count('x') != 2:
      continue
    else:
      if ins[1] == 'W':
        d[ins[2]] = vals.index(int(ins[0][:-1], 0)) + 1
      else:
        if ins[2] in d:
          if ins[0][:-1] == '':
            print ins
          dependencies.append([vals.index(int(ins[0][:-1], 0)) + 1, d[ins[2]]])

  # get the last 5 dependencies
  for i in range(4,len(dependencies)):
    state = dependencies[(i-4):(i+1)]
    status = 0
    if failed:
      status = 1
    row = [status] + [ins for dependency in state for ins in dependency]
    data.append(row)

with open('results.csv', 'wb') as fp:
  a = csv.writer(fp, delimiter=',')
  a.writerows(data)
