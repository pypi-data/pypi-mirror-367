import os
import platform
import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import subprocess

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        try:
            import pybind11
            pybind11_cmake_dir = pybind11.get_cmake_dir()
        except ImportError:
            pybind11_cmake_dir = ""

        for ext in self.extensions:
            self.build_extension(ext, pybind11_cmake_dir)

    def build_extension(self, ext, pybind11_cmake_dir):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
            f'-DCMAKE_PREFIX_PATH={pybind11_cmake_dir}'
        ]

        build_args = ['--config', 'Release']

        build_dir = os.path.join(self.build_temp, ext.name)
        os.makedirs(build_dir, exist_ok=True)
        
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=build_dir)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=build_dir)

setup(
    ext_modules=[CMakeExtension('arx_r5_sdk/lib/arx_r5_python', sourcedir='py/ARX_R5_python'), 
                 CMakeExtension('arx_r5_sdk/lib/kinematic_solver', sourcedir='py/ARX_R5_python')],
    cmdclass={'build_ext': CMakeBuild},
    zip_safe=False,
    package_dir={'': 'py/ARX_R5_python/src'},
    packages=['arx_r5_sdk', 'arx_r5_sdk.lib'],
    package_data={
        'arx_r5_sdk': [
            '*.urdf',
            'lib/*.so*',
        ]
    },
)
