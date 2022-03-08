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
# cython: profile=False

import cython
from frommle2.sh.legendre cimport Legendre_nm,Legendre

from cython.operator cimport dereference as deref
import numpy as np 
cimport numpy as np


# Cython wrapper class
cdef class Pn:
    """Double precision Legendre polynomial wrapper"""
    cdef Legendre[double]*leg_ptr  # Pointer to the wrapped C++ class
    def __cinit__(self, int nmax):
        self.leg_ptr = new Legendre[double](nmax)
    
    def __dealloc__(self):
        del self.leg_ptr

    def __call__(self,double costheta):
        #set the new colatitude
        return deref(self.leg_ptr).get(costheta)
        

cdef class Pnm:
    """Double precision Legendre polynomial wrapper"""
    cdef Legendre_nm[double]*legnm_ptr  # Pointer to the wrapped C++ class
    def __cinit__(self, int nmax):
        self.legnm_ptr = new Legendre_nm[double](nmax)
    
    def __dealloc__(self):
        del self.legnm_ptr

    def __call__(self,double costheta):
        cdef np.ndarray[np.double_t, ndim=1] pnmdata = np.zeros([deref(self.legnm_ptr).size()],dtype=np.double)
        cdef double[::1] mview = pnmdata
        deref(self.legnm_ptr).set(costheta,&mview[0])
        return pnmdata
    def __len__(self):
        return deref(self.legnm_ptr).size()
    def nmax(self):
        return deref(self.legnm_ptr).nmax()

    def idx(self,int n,int m):
        return deref(self.legnm_ptr).i_from_nm(n,m,deref(self.legnm_ptr).nmax())

    def nm(self,cython.size_t idx):
        return deref(self.legnm_ptr).nm_from_i(idx,deref(self.legnm_ptr).nmax())

    def index(self):
        nmax=deref(self.legnm_ptr).nmax()
        sz=deref(self.legnm_ptr).size()
        nm_from_i=deref(self.legnm_ptr).nm_from_i
        return [nm_from_i(idx,nmax) for idx in range(sz)] 
