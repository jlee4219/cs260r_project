import operator

def get_last(filename):
  with open(filename, 'rb') as f:
    f.seek(-2, 2)
    while f.read(1) != '\n':
      f.seek(-2, 1)
    last = f.readline()
  return last

def buggy_freq_ratio(outdir, N):
  counts = {}
  buggy = 0
  nonbuggy = 0
  for i in range(N):
    bad = 0
    filename = outdir + "/trace" + str(i) + ".out"
    if len(get_last(filename).split()) < 2:
      bad = 1
      buggy += 1
    else:
      nonbuggy += 1 
    with open(filename, 'rb') as f:
      for line in f:
        words = line.split()
        source = words[:2]+words[3:4]
        sinks = words[4:]
        for i in range(len(sinks)/4):
          key = str(source)+" "+str(sinks[4*i:4*i+2]+sinks[4*i+3:4*(i+1)])
          if key in counts:
            counts[key][bad] += 1
          else:
            vals = [0, 0]
            vals[bad] += 1
            counts[key] = vals
  for key, value in counts.iteritems():
    frac_n = float(value[0])/nonbuggy
    frac_b = float(value[1])/buggy
    if frac_n == 0:
      frac_n = float(1)/(nonbuggy+1)
    bfr = frac_b / frac_n
    counts[key] = bfr
  sorted_by_bfr = sorted(counts.items(), key=operator.itemgetter(1))
  return sorted_by_bfr[-5:]

def build_recon(edge, outdir, N):
  for i in range(N):
    bad = 0
    filename = outdir + "/trace" + str(i) + ".out"
    if len(get_last(filename).split()) < 2:
      bad = 1
      buggy += 1
    else:
      nonbuggy += 1 
    # with open(filename, 'rb') as f: 

# for edge in buggy_freq_ratio("./test1_traces", 200):
  # print edge
