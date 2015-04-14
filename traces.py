from subprocess import call

count = 0
for i in range(100):
  ret = call("../../../pin -t obj-ia32/new_read_write.so -- ./test1", shell=True)
  s = "cp ./read_write.out ./data/test" + str(i) + ".out"
  call(s, shell=True)
  if ret != 0:
    count += 1
    f = open('./data/test' + str(i) + '.out', 'a')
    f.write('1\n')
    f.close()
    print("failed")
print count
