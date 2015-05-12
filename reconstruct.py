import features
from subprocess import check_output as qx

def reconstruct(edge, filename, outdir, N):
  output = edge[0].split()
  source = output[0][2:-2]
  sink = output[3][2:-2]
  source_line = get_line(filename, source)
  sink_line = get_line(filename, sink)
  for node, write in get_body(edge, outdir, N, 1).iteritems():
    print_node(filename, node, write)
  print "Write from", source_line
  for node, write in get_body(edge, outdir, N, 0).iteritems():
    print_node(filename, node, write)
  print "Read from", sink_line
  for node, write in get_body(edge, outdir, N, -1).iteritems():
    print_node(filename, node, write)

def print_node(filename, node, write):
  if write != 1:
    text = "W"
  else:
    text = "R"
  line = get_line(filename, node)
  if line[0] != '?':
    print text, line

def get_line(filename, address):
  return qx(['addr2line', '-e', filename, address])

def get_body(edge, outdir, N, get_prev):
  body = {}
  confs = {}
  max_conf = 0
  for i in range(N):
    filename = outdir + "/trace" + str(i) + ".out"
    with open(filename, 'rb') as f:
      file_body = get_body_for_file(edge, f, get_prev)
      for key in file_body:
        body[key] = file_body[key]
        if key in confs:
          confs[key] += float(1)/N
          max_conf = max(confs[key], max_conf)
        else:
          confs[key] = float(1)/N
  with_cutoff = {}
  for key, value in body.iteritems():
    if value > 0.5 * max_conf:
      with_cutoff[key] = body[key]
  return with_cutoff

def get_body_for_file(edge, f, get_prev):
  edge_src_time = None
  edge_snk_time = None
  max_time = 0
  times = {}
  body = {}
  prev = {}
  suff = {}
  for line in f:
    words = line.split()
    if len(words) > 4:
      source = words[:4]
      sinks = words[4:]
      src_time = source[2]
      max_time = max(max_time, src_time)
      if src_time in times:
        times[src_time].append((source[0], 0))
      else:
        times[src_time] = [(source[0], 0)]
      for i in range(len(sinks)/4):
        src = source[:2]+source[3:]
        snk = sinks[4*i:4*i+2]+sinks[4*i+3:4*(i+1)]
        snk_time = sinks[4*i+2]
        max_time = max(max_time, snk_time)
        key = str(src)+" "+str(snk)
        if key == edge[0]:
          edge_src_time = src_time
          edge_snk_time = snk_time
        if snk_time in times:
          times[snk_time].append((sinks[4*i],1))
        else:
          times[snk_time] = [(sinks[4*i],1)]
  if edge_src_time != None and edge_snk_time != None:
    for i in range(int(edge_src_time)+1, int(edge_snk_time)):
      if str(i) in times:
        for node in times[str(i)]:
          body[node[0]] = node[1]
    if get_prev == 1:
      prev_count = 0
      time = int(edge_src_time) - 1
      while(time > 0 and prev_count < 5):
        if str(time) in times:
          for node in times[str(time)]:
            prev[node[0]] = node[1]
            prev_count += 1
        time -= 1
    if get_prev == -1:
      suff_count = 0
      time = int(edge_snk_time) + 1
      while(time <= max_time and suff_count < 5):
        if str(time) in times:
          for node in times[str(time)]:
            suff[node[0]] = node[1]
            suff_count += 1
        time -= 1
  if get_prev == 1:
    return prev
  elif get_prev == -1:
    return suff
  else:
    return body

# reconstruct(features.buggy_freq_ratio("./test1_traces",200)[-1], "test1")
