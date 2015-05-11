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

reconstruct(features.buggy_freq_ratio("./test1_traces",200)[-1], "test1")
