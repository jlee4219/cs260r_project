import features
from subprocess import check_output as qx

def reconstruct(edge, filename, outdir, N):
  output = edge[0].split()
  source = output[0][2:-2]
  sink = output[3][2:-2]
  source_line = get_line(filename, source)
  sink_line = get_line(filename, sink)
  print source_line
  for address in get_body(edge, outdir, N):
    print get_line(filename, address)
  print sink_line

def get_line(filename, address):
  return qx(['addr2line', '-e', filename, address])

def get_body(edge, outdir, N):
  body = {}
  max_conf = 0
  for i in range(N):
    filename = outdir + "/trace" + str(i) + ".out"
    with open(filename, 'rb') as f:
      file_body = get_body_for_file(edge, f)
      for key in file_body:
        if key in body:
          body[key] += float(1)/N
          max_conf = max(body[key], max_conf)
        else:
          body[key] = 0
  with_cutoff = {}
  for key, value in body.iteritems():
    if value > 0.5 * max_conf:
      with_cutoff[key] = value
  return with_cutoff

def get_body_for_file(edge, f):
  edge_src_time = None
  edge_snk_time = None
  times = {}
  body = {}
  for line in f:
    words = line.split()
    if len(words) > 4:
      source = words[:4]
      sinks = words[4:]
      src_time = source[2]
      if src_time in times:
        times[src_time].append(source[0])
      else:
        times[src_time] = [source[0]]
      for i in range(len(sinks)/4):
        src = source[:2]+source[3:]
        snk = sinks[4*i:4*i+2]+sinks[4*i+3:4*(i+1)]
        snk_time = sinks[4*i+2]
        key = str(src)+" "+str(snk)
        if key == edge[0]:
          edge_src_time = src_time
          edge_snk_time = snk_time
        if snk_time in times:
          times[snk_time].append(sinks[4*i])
        else:
          times[snk_time] = [sinks[4*i]]
  if edge_src_time != None and edge_snk_time != None:
    for i in range(int(edge_src_time)+1, int(edge_snk_time)):
      if str(i) in times:
        for node in times[str(i)]:
          body[node] = str(i)
  return body

# reconstruct(features.buggy_freq_ratio("./test1_traces",200)[-1], "test1")
