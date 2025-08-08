from sys import platform
from platform import machine
import ctypes
import os


if platform == 'darwin':
    file_ext = '-arm64.dylib' if machine() == "arm64" else '-x86.dylib'
elif platform in ('win32', 'cygwin'):
    file_ext = '-64.dll' if 8 == ctypes.sizeof(ctypes.c_voidp) else '-32.dll'
else:
    if machine() == "aarch64":
        file_ext = '-arm64.so'
    elif "x86" in machine():
        file_ext = '-x86.so'
    else:
        file_ext = '-amd64.so'

root_dir = os.path.abspath(os.path.dirname(__file__))
lib_dir = os.path.join(root_dir, "dependencies")
lib_path = None
# Encontre o primeiro arquivo que termina com o file_ext
for filename in os.listdir(lib_dir):
    if filename.endswith(file_ext):
        lib_path = os.path.join(lib_dir, filename)
        break

if not lib_path:
    raise FileNotFoundError(f"No shared library found in {lib_dir} with extension {file_ext}")

root_dir = os.path.abspath(os.path.dirname(__file__))
library = ctypes.cdll.LoadLibrary(lib_path)

# extract the exposed request function from the shared package
request = library.request
request.argtypes = [ctypes.c_char_p]
request.restype = ctypes.c_char_p

freeMemory = library.freeMemory
freeMemory.argtypes = [ctypes.c_char_p]
freeMemory.restype = ctypes.c_char_p

destroySession = library.destroySession
destroySession.argtypes = [ctypes.c_char_p]
destroySession.restype = ctypes.c_char_p
