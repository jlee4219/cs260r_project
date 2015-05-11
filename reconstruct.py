import features
from subprocess import check_output as qx

def reconstruct(edge, filename):
  output = edge[0].split()
  source = output[0][2:-2]
  sink = output[3][2:-2]
  source_line = qx(['addr2line', '-e', filename, source])
  sink_line = qx(['addr2line', '-e', filename, sink])
  print source_line
  print sink_line

def get_body(edge, outdir, N):
  for i in range(N):
    filename = outdir + "/trace" + str(i) + ".out"
    with open(filename, 'rb') as f:
      get_body_for_file(edge, f)

def get_body_for_file(edge, f):
  edge_src_time = None
  edge_snk_time = None
  times = {}
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
        for i in range(int(edge_src_time), int(edge_snk_time)):
          if str(i) in times:
            print times[str(i)]    
        

# reconstruct(features.buggy_freq_ratio("./test1_traces",200)[-1], "test1")
