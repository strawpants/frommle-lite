# This file is part of frommle2.
# frommle2 is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.

# frommle2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with Frommle; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# Author Roelof Rietbroek (r.rietbroek@utwente.nl), 2022

# distutils: language = c++

import cython
from libcpp.vector cimport vector
from cython.operator cimport dereference as deref

# C++ / Cython interface declaration (can be put in an pxd file if needed)
cdef extern from "Legendre.hpp":
    cdef cppclass Legendre[T]:
        Legendre(int nmax) except +
        vector[T] get(T costheta) except+
# End of interface declaration

# Cython wrapper class
cdef class Pn:
    """Double precision Legendre polynomial wrapper"""
    cdef Legendre[double]*leg_ptr  # Pointer to the wrapped C++ class

    def __cinit__(self, int nmax):
        self.leg_ptr = new Legendre[double](nmax)
    
    def __dealloc__(self):
        del self.leg_ptr

    def __call__(self,double costheta):
        return deref(self.leg_ptr).get(costheta)
