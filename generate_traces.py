from subprocess import call

for i in range(50):
  ret = call("../../../pin -t obj-intel64/read_write.dylib -- ./example", shell=True)
  s = "cp ./read_write.out ./data/test" + str(i) + ".out"
  call(s, shell=True)
  if ret != 0:
    f = open('./data/test' + str(i) + '.out', 'a')
    f.write('1\n')
    f.close()
    print("failed")