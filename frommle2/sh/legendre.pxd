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


cimport cython
from libcpp.vector cimport vector
from libcpp.pair cimport pair
# C++ / Cython interface declaration 
cdef extern from "Legendre.hpp":
    cdef cppclass Legendre[T]:
        Legendre(int nmax) except +
        vector[T] get(T costheta) except+

# C++ associated Legendre functions
cdef extern from "Legendre_nm.hpp":
    cdef cppclass Legendre_nm[T]:
        Legendre_nm(int nmax) except +
        void set(T costheta, double arr[] ) except+
        @staticmethod
        cython.size_t i_from_nm(int n,int m, int nmax)
        cython.size_t idx(int n,int m)
        @staticmethod
        pair[int,int] nm_from_i(cython.size_t idx, int nmax)
        #cached version:
        pair[int,int] nm(cython.size_t idx)
        
        int nmax()
        cython.size_t size()
# End of interface declaration

