from numpy import get_include as np_get_include
from distutils.core import setup,Extension
from Cython.Build import cythonize

extGameClass = Extension(name="gameClassOffline", sources=["gameClassOffline.py"],
                include_dirs=[np_get_include()]
                )

extClient = Extension(name="client", sources=["client.py"],
                include_dirs=[np_get_include()]
                )

extServer = Extension(name="server", sources=["server.py"],
                include_dirs=[np_get_include()]
                )

setup(ext_modules=cythonize(extGameClass))
setup(ext_modules=cythonize(extClient))
setup(ext_modules=cythonize(extServer))