from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext

__version__ = "0.5.post"

ext_modules = [
    Pybind11Extension(
        "pyEulerCurves._compute_local_EC_cubical",
        ["pyEulerCurves/src/compute_local_EC_cubical.cpp"],
        define_macros=[("VERSION_INFO", __version__)],
        include_dirs=["pyEulerCurves/src"],
    ),
    Pybind11Extension(
        "pyEulerCurves._compute_local_EC_VR",
        ["pyEulerCurves/src/compute_local_EC_VR.cpp"],
        define_macros=[("VERSION_INFO", __version__)],
        include_dirs=["pyEulerCurves/src"],
    ),
]

setup(
    name="pyEulerCurves",
    version=__version__,
    author="Davide Gurnari",
    author_email="davide.gurnari@gmail.com",
    url="https://github.com/dgurnari/pyEulerCurves",
    description="A python package to compute Euler Characteristic Curves",
    long_description="",
    packages=find_packages(),  # Automatically find packages
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
    package_data={
        "pyEulerCurves": [
            "*.py",
            "src/*.h",
            "src/*.cpp",
        ],  # Include header and source files
    },
    install_requires=[
        "numpy",
        "matplotlib",
        "scikit-learn",
        "pybind11>=2.10.0",
        "gudhi",
        "numba",
    ],
)
