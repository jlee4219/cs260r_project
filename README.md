# cs260r_project

To use:

1. Download pin.
2. Move traces2.py, rfc2.py, and new_read_write.cpp to pin-.../source/tools/ManualExamples/

If on a 64-bit Mac:

make obj-intel64/new_read_write.dylib TARGET=intel64

On other 64-bit architectures:

make obj-intel64/new_read_write.so TARGET=intel64

If on a 32-bit architecture:

make obj-ia32/new_read_write.so TARGET=ia32

4. mkdir traces
5. python traces2.py program traces
6. python rfc2.py