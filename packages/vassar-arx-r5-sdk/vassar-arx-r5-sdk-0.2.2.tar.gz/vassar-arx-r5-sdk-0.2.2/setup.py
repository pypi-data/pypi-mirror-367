"""Setup script for ARX R5 SDK."""
import os
import sys
import platform
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import subprocess


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        # Create build directory
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        
        # CMake arguments
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
            '-DCMAKE_BUILD_TYPE=Release'
        ]
        
        # Build arguments
        build_args = ['--config', 'Release', '--', '-j4']
        
        # Configure and build
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
        
        # Copy the built modules to the package directory
        import shutil
        
        # The modules are installed to api/arx_r5_python/ by CMake
        api_dir = os.path.join(ext.sourcedir, 'api', 'arx_r5_python')
        if os.path.exists(api_dir):
            # Copy all .so files from the api directory
            dst_dir = os.path.join(extdir, 'bimanual', 'api', 'arx_r5_python')
            os.makedirs(dst_dir, exist_ok=True)
            
            for filename in os.listdir(api_dir):
                if filename.endswith('.so'):
                    src = os.path.join(api_dir, filename)
                    dst = os.path.join(dst_dir, filename)
                    shutil.copy2(src, dst)
        
        # In manylinux environment, also copy the pre-built .so files
        # These are needed because they're pre-compiled ARM libraries
        lib_dir = os.path.join(ext.sourcedir, 'lib')
        if os.path.exists(lib_dir):
            dst_lib_dir = os.path.join(extdir, 'bimanual', 'lib')
            os.makedirs(dst_lib_dir, exist_ok=True)
            
            # Copy lib/*.so files
            for filename in os.listdir(lib_dir):
                if filename.endswith('.so'):
                    src = os.path.join(lib_dir, filename)
                    dst = os.path.join(dst_lib_dir, filename)
                    shutil.copy2(src, dst)
            
            # Copy lib/arx_r5_src/*.so files
            arx_src_dir = os.path.join(lib_dir, 'arx_r5_src')
            if os.path.exists(arx_src_dir):
                dst_arx_dir = os.path.join(dst_lib_dir, 'arx_r5_src')
                os.makedirs(dst_arx_dir, exist_ok=True)
                for filename in os.listdir(arx_src_dir):
                    if filename.endswith('.so'):
                        src = os.path.join(arx_src_dir, filename)
                        dst = os.path.join(dst_arx_dir, filename)
                        shutil.copy2(src, dst)


# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="vassar-arx-r5-sdk",
    version="0.2.2",
    author="ARXrobotics",
    author_email="contact@arx-x.com",
    maintainer="Vassar",
    description="Python SDK for ARX R5 Robot Arm Control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ARXroboticsX/R5",
    packages=find_packages(include=['vassar_arx_r5_sdk', 'vassar_arx_r5_sdk.*']),
    package_data={
        'vassar_arx_r5_sdk': [
            'bimanual/script/*.urdf',
            'bimanual/lib/*.so',
            'bimanual/lib/*.hpp',
            'bimanual/lib/arx_r5_src/*.so',
            'bimanual/lib/arx_r5_src/include/**/*',
            'bimanual/lib/arx_hardware_interface/include/**/*',
            'bimanual/src/*.cpp',
            'bimanual/CMakeLists.txt',
            'bimanual/build.sh',
            'setup.sh',
            'build.sh',
        ]
    },
    include_package_data=True,
    ext_modules=[CMakeExtension('vassar_arx_r5_sdk.bimanual', 'vassar_arx_r5_sdk/bimanual')],
    cmdclass=dict(build_ext=CMakeBuild),
    python_requires=">=3.10",  # Ubuntu 22.04 LTS and newer
    install_requires=[
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pybind11>=2.6.0",
            "cmake>=3.18",
        ]
    },
    classifiers=[],
    keywords="robotics, robot arm, ARX, R5, control",
    project_urls={
        "Bug Reports": "https://github.com/ARXroboticsX/R5/issues",
        "Source": "https://github.com/ARXroboticsX/R5",
    },
)