#!/usr/bin/env python3
"""
Setup script for PyFunc with optional C++ and Go backends.
"""

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from pybind11.setup_helpers import Pybind11Extension
import os
import subprocess
import shutil
import pybind11

# --- Custom Go Extension and Build Command ---

class GoExtension(Extension):
    """A custom Extension class for Go modules."""
    def __init__(self, name, go_source_dir, **kwargs):
        super().__init__(name, sources=[], **kwargs)
        self.go_source_dir = go_source_dir

class CustomBuildExt(build_ext):
    """
    Custom build_ext command to first compile the Go shared library,
    then configure the GoExtension to be built as a C++ wrapper by pybind11.
    """
    def build_extension(self, ext):
        if not isinstance(ext, GoExtension):
            super().build_extension(ext)
            return

        print("--- Building Go Extension ---")
        go_output_name = "native_go"
        go_source_dir = ext.go_source_dir

        # Define the output path for the Go build inside the source directory
        go_build_output = os.path.join(go_source_dir, go_output_name)
        
        # 1. Compile Go code into a shared library in its own source directory
        go_build_cmd = [
            "go", "build",
            "-o", f"{go_build_output}.{'dll' if os.name == 'nt' else 'so'}",
            "-buildmode=c-shared",
            "."
        ]
        
        print(f"Running Go build: {' '.join(go_build_cmd)}")
        try:
            subprocess.run(go_build_cmd, check=True, cwd=go_source_dir, capture_output=True, text=True)
            print("--- Go shared library built successfully. ---")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"--- WARNING: Go build failed. Skipping Go backend. ---")
            if hasattr(e, 'stderr'):
                print(f"Go compiler error: {e.stderr}")
            return

        # --- Manually create .lib file on Windows ---
        if os.name == 'nt':
            try:
                # Find vcvarsall.bat to set up the environment for MSVC tools
                vcvarsall_path = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
                if not vcvarsall_path:
                    raise FileNotFoundError("vcvarsall.bat not found. Please run this from a Visual Studio Command Prompt.")

                # Run dumpbin to get exports
                dumpbin_cmd = f'call "{vcvarsall_path}" x64 && dumpbin /EXPORTS "{os.path.abspath(f"{go_build_output}.dll")}"'
                exports_output = subprocess.check_output(dumpbin_cmd, cwd=go_source_dir, text=True, shell=True)

                # Write dumpbin output to a file
                dumpbin_output_file = os.path.join(go_source_dir, "dumpbin_exports.txt")
                with open(dumpbin_output_file, "w") as f:
                    f.write(exports_output)
                
                # Read dumpbin output from the file
                with open(dumpbin_output_file, "r") as f:
                    exports_output = f.read()
                print(f"--- dumpbin exports output: ---")
                print(exports_output)
                print(f"--- End of dumpbin exports output ---")

                # Create .def file
                def_file_path = os.path.join(go_source_dir, f"{go_output_name}.def")
                with open(def_file_path, "w") as f:
                    f.write("EXPORTS\n")
                    for line in exports_output.splitlines():
                        if ' go_' in line: # Filter for relevant Go exports
                            f.write(line.split()[-1] + '\n')
                f.close() # Explicitly close the file

                # Add a small delay to ensure the file is written
                import time
                time.sleep(0.1)

                # Debug: Read the created .def file
                print(f"--- Contents of {def_file_path}: ---")
                with open(def_file_path, "r") as f:
                    print(f.read())
                print(f"--- End of {def_file_path} ---")

                # Check if .def file exists
                if not os.path.exists(def_file_path):
                    raise FileNotFoundError(f"DEF file not created at {def_file_path}")

                # Run lib to create .lib file
                lib_cmd = f'call "{vcvarsall_path}" x64 && lib /def:"{os.path.abspath(def_file_path)}" /out:"{os.path.abspath(f"{go_build_output}.lib")}" /machine:x64'
                subprocess.run(lib_cmd, check=True, cwd=go_source_dir, shell=True)
                print("--- .lib file created successfully. ---")

            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"--- WARNING: Failed to create .lib file. Skipping Go backend. ---")
                print(f"Error: {e}")
                return

        # Copy the shared library to the final build directory for packaging
        build_lib_dir = os.path.join(self.build_lib, "pyfunc", "native_go")
        os.makedirs(build_lib_dir, exist_ok=True)
        shutil.copy(
            f"{go_build_output}.{'dll' if os.name == 'nt' else 'so'}",
            build_lib_dir
        )

        # 2. Generate the C++ wrapper content on the fly
        wrapper_cpp_content = f"""
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "native_go.h"

namespace py = pybind11;

// Wrapper functions to handle std::vector
std::vector<int> bitwise_and_wrapper(std::vector<int> data, int operand) {{
    bitwise_and_go(data.data(), data.size(), operand);
    return data;
}}
// ... other wrapper functions ...

PYBIND11_MODULE({go_output_name}, m) {{
    m.def("bitwise_and", &bitwise_and_wrapper);
    // ... other definitions ...
}}
"""
        
        # 3. Write the temporary wrapper file
        wrapper_path = os.path.join(self.build_temp, "go_wrapper.cpp")
        os.makedirs(self.build_temp, exist_ok=True)
        with open(wrapper_path, "w") as f:
            f.write(wrapper_cpp_content)

        # 4. Configure the GoExtension object for C++ build
        # The .h and .lib files are in the go_source_dir
        ext.sources = [wrapper_path]
        ext.include_dirs.append(go_source_dir)
        ext.library_dirs.append(go_source_dir)
        
        # 5. Now, call the original build_ext to compile the C++ wrapper
        print("--- Building Go C++ wrapper ---")
        super().build_extension(ext)

# --- Extension Modules ---

ext_modules = []

if os.environ.get('PYFUNC_BUILD_CPP', '1') == '1':
    cpp_module = Pybind11Extension(
        "pyfunc_native",
        sources=[
            "pyfunc/native/operations.cpp",
            "pyfunc/native/bindings.cpp",
        ],
        include_dirs=["pyfunc/native", pybind11.get_include()],
        language='c++',
        cxx_std=17,
    )
    ext_modules.append(cpp_module)

if os.environ.get('PYFUNC_BUILD_GO', '1') == '1':
    go_module = GoExtension(
        "pyfunc.native_go",
        go_source_dir="pyfunc/native_go",
        include_dirs=[pybind11.get_include()],
        language='c++',
        cxx_std=17,
    )
    ext_modules.append(go_module)

# --- Setup Configuration ---

setup(
    name="pyfunc-pipeline",
    version="0.4.0",
    ext_modules=ext_modules,
    cmdclass={"build_ext": CustomBuildExt},
    packages=find_packages(include=["pyfunc", "pyfunc.*"]),
    package_data={
        "pyfunc.native": ["*.hpp"],
        "pyfunc.native_go": ["*.h", "*.dll", "*.so"],
    },
    zip_safe=False,
)
