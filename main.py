import sys
import platform
import traces2
import features
import reconstruct
import os
from subprocess import call

if len(sys.argv) < 2:
  print "Please specify a file."
  sys.exit()
else:
  filename = sys.argv[1]
if len(sys.argv) > 2:
  outdir = sys.argv[2]
else:
  outdir = "./" + filename + "_traces"
if len(sys.argv) > 3:
  N = sys.argv[3]
else:
  N = 50
if sys.platform == "darwin":
  filetype = ".dylib"
else:
  filetype = ".so"
if platform.architecture()[0] == '32bit':
  obj = "obj-ia32"
else:
  obj = "obj-intel64"

def run():
  print outdir 
  os.mkdir(outdir)
  print "Generating traces..."
  traces2.gen_traces(outdir, filetype, obj, N)
  print "Calculating features..."
  edges = features.buggy_freq_ratio(outdir, N)
  print "Reconstructing..."
  reconstruct.reconstruct(edges[-1], filename)

def test():
  print "Calculating features..."
  edges = features.buggy_freq_ratio(outdir, N)
  print "Reconstructing..."
  reconstruct.reconstruct(edges[-1], filename)
  reconstruct.get_body(edges[-1], outdir, N)

# run()
test()
