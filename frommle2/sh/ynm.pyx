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
import numpy as np
cimport numpy as np
import xarray as xr
from frommle2.sh.legendre cimport Legendre_nm
from libc.math cimport sin,cos,pi
from cython.operator cimport dereference as deref
from libcpp.pair cimport pair
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef class Ynm:
    # cdef int nmax
    # cdef double[::1] pnmcache
    # cdef double[:,::1] trigcache
    # cdef double[::1] ynm
    # cdef double latprev;
    # cdef cython.size_t sz
    # cdef Legendre_nm[double]*legnm_ptr
    def __cinit__(self,int nmax):
        self.legnm_ptr=new Legendre_nm[double](nmax)
        self.latprev=-1000.0 #invalid initial value
        
        cdef cython.size_t sz_half=deref(self.legnm_ptr).size()
        #initialize cache
        self.pnmcache=np.zeros([sz_half])
        self.trigcache=np.zeros([nmax+1,2])
        self.ynm=np.zeros([2*sz_half])
        self.sz=sz_half*2
        self.nmax=nmax

    def __dealloc__(self):
        del self.legnm_ptr

    @property
    def nmax(self):
        return self.nmax
    
    def __len__(self):
        return self.sz
    def __call__(self,double lon, double lat):
        return self.icall(lon,lat)

    cdef double[::1] icall(self,double lon,double lat):
        cdef double costheta
        if (lat != self.latprev):
            #(re)compute associated Legendre functions
            costheta=sin(lat*pi/180.0)
            self.latprev=lat
            deref(self.legnm_ptr).set(costheta,&self.pnmcache[0])
        cdef double lonr=lon*pi/180.0
        #generate trigonometric cache
        cdef int m=0
        for m in range(self.nmax+1):
            self.trigcache[m,0]=cos(m*lonr)
            self.trigcache[m,1]=sin(m*lonr)

        cdef cython.size_t idx=0
        cdef pair[int,int] nm
        cdef cython.size_t sz_half=deref(self.legnm_ptr).size()
        for idx in range(sz_half):
            nm=deref(self.legnm_ptr).nm(idx)
            self.ynm[2*idx]=self.trigcache[nm.second,0]*self.pnmcache[idx]
            self.ynm[2*idx+1]=self.trigcache[nm.second,1]*self.pnmcache[idx]

        return self.ynm

    def nmt(self):
        cdef int[:,::1] nmt=np.empty([self.sz,3],dtype=np.int32)
        cdef cython.size_t idx
        cdef pair[int,int] nm
        cdef cython.size_t sz_half=deref(self.legnm_ptr).size()
        for idx in range(sz_half):
            nm=deref(self.legnm_ptr).nm(idx)
            nmt[2*idx,0]=nm.first
            nmt[2*idx,1]=nm.second
            nmt[2*idx,2]=0

            nmt[2*idx+1,0]=nm.first
            nmt[2*idx+1,1]=nm.second
            nmt[2*idx+1,2]=1

        return np.asarray(nmt)

