import sys
from sys import platform
from platform import machine
import ctypes
import os

system = sys.platform
arch = machine()


if system == "darwin":
    # macOS (arm64 = Apple Silicon, x86_64 = Intel)
    file_ext = "-arm64.dylib" if arch == "arm64" else "-amd64.dylib"

elif system in ("win32", "cygwin"):
    # Windows (32 ou 64 bits)
    file_ext = "-amd64.dll" if ctypes.sizeof(ctypes.c_voidp) == 8 else "-386.dll"

else:
    # Linux e outras
    if arch == "aarch64":
        file_ext = "-arm64.so"
    elif arch == "armv7l":
        file_ext = "-arm-7.so"
    elif arch == "armv6l":
        file_ext = "-arm-6.so"
    elif arch == "armv5tel":
        file_ext = "-arm-5.so"
    elif arch in ("i386", "i686"):
        file_ext = "-386.so"
    elif arch == "x86_64":
        file_ext = "-amd64.so"
    else:
        raise RuntimeError(f"Arquitetura desconhecida: {arch}")

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
