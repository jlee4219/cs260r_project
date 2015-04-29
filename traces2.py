import sys
import platform
from subprocess import call

if len(sys.argv) < 2:
  print "Please specify a file."
  sys.exit()
if len(sys.argv) > 2:
  outdir = sys.argv[2]
else:
  outdir = "data"
if len(sys.argv) > 3:
  N = sys.argv[3]
else:
  N = 100
if sys.platform == "darwin":
  filetype = ".dylib"
else:
  filetype = ".so"
if platform.architecture()[0] == '32bit':
  obj = "obj-ia32"
else:
  obj = "obj-intel64"


def gen_traces(outdir,N):
  count = 0
  for i in range(10):
    ret = call("../../../pin -t "+ obj +"/new_read_write" + filetype +" -- ./" + sys.argv[1], shell=True)
    outfile = "./" + outdir + "/trace" + str(i) + ".out"
    '''with open("read_write.out") as f:
      with open(outfile, "w") as f1:
        for line in f:
            f1.write(line)'''
    s = "cp read_write.out " + outfile
    call(s, shell=True)
    if ret != 0:
      f1 = open(outfile, "a")
      count += 1
      f1.write('1\n')
      print("failed")
      f1.close()
  print count

gen_traces(outdir, N)