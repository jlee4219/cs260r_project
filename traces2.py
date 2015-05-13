import sys
import platform
from subprocess import call

def gen_traces(outdir, filetype, obj, N):
  count = 0
  for i in range(N):
    if (i % (N/5) == 0):
      print "Generated", i, "traces."
    ret = call("../../../pin -t "+ obj +"/recon" + filetype +" -- ./" + sys.argv[1], shell=True)
    outfile = "./" + outdir + "/trace" + str(i) + ".out"
    s = "cp read_write.out " + outfile
    call(s, shell=True)
    if ret != 0:
      f1 = open(outfile, "a")
      count += 1
      f1.write('1\n')
      print("failed")
      f1.close()
  print count

# gen_traces(outdir, N)
