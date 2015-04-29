import sys
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

def gen_traces(outdir,N)
  count = 0
  for i in range(100):
    ret = call("../../../pin -t obj-ia32/new_read_write.so -- ./" + sys.argv[1], shell=True)
    s = "cp ./read_write.out ./" + outdir + "/trace" + str(i) + ".out"
    call(s, shell=True)
    if ret != 0:
      count += 1
      f = open('./' + outdir + '/trace' + str(i) + '.out', 'a')
      f.write('1\n')
      f.close()
      print("failed")
  print count
