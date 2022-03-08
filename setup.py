# setup.py  
# This file is part of geoslurp.
# geoslurp is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.

# geoslurp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with Frommle; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# Author Roelof Rietbroek (roelof@geod.uni-bonn.de), 2020
from setuptools import setup,find_packages,Extension
from Cython.Build import cythonize
import Cython.Compiler.Options
import os 
import numpy as np

with open("README.md", "r") as fh:
    long_description = fh.read()

#don't necessarily use cython
if "USE_CYTHON" in os.environ:
    useCython=True
    ext=".pyx"
    Cython.Compiler.Options.annotate = True
else:
    useCython=False
    ext=".cpp"


def listexts():
    names=["sh/legendre","sh/ynm","sh/analysis"]
    exts=[]
    for nm in names:
        exts.append(Extension("frommle2."+nm.replace("/","."),["frommle2/"+nm+ext],include_dirs=[np.get_include()]))
    return exts

extensions=listexts()
# [Extension("frommle2.sh.legendre",["frommle2-cython/sh/legendre"+ext],include_dirs=[np.get_include()])]


if useCython:
    #additionally cythonize pyx files before building
    extensions=cythonize(extensions,language_level=3,annotate=True)

setup(
    name="frommle2",
    author="Roelof Rietbroek",
    author_email="roelof@wobbly.earth",
    version="0.0.0",
    description="Python module to work with geodetic datasets and inverse problems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/strawpants/frommle2",
    packages=find_packages("."),
    package_dir={"":"."},
    # scripts=['clitools/geoslurper.py'],
    install_requires=['numpy','pyshtools','cython'],
    ext_modules=extensions,
    classifiers=["Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
        "Development Status :: 4 - Beta"]
    
)
