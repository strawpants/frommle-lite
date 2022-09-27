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
# cython: profile=True

import xarray as xr
import cython
import numpy as np
cimport numpy as np
from frommle2.sh.ynm cimport Ynm
import frommle2.sh.xarraysh
from warnings import warn
# Todo: improve speed by directly calling dgemv
#from scipy.linalg.cython_blas cimport dgemv

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef class Analysis:
    cdef np.ndarray lon
    cdef np.ndarray lat
    cdef Ynm ynm
    cdef public object dskel
    def __cinit__(self,int nmax, np.ndarray lon=np.arange(-180.0,180.0,1.0), np.ndarray lat=np.arange(-90.0,90.0,1.0)):
        self.ynm=Ynm(nmax)

        #create a xrray dataset which spans the in and output
        coords={"lon":("lon",lon),"lat":("lat",lat),"shg":("shg",xr.DataArray.sh.mi_fromarrays(self.ynm.nmt().T))}
        self.dskel=xr.Dataset(coords=coords)

        #add some CF attributes to the longitude and latitude so it will be understood by plotting software etc
        self.dskel.lon.attrs={"units":"degree_east","standard_name":"longitude","axis":"X"}
        self.dskel.lat.attrs={"units":"degree_north","standard_name":"latitude","axis":"Y"}


        self.dskel=self.dskel.sh.build_MultiIndex()
        
    def __call__(self,xarin):
        """Perform the spherical harmonic analysis""" 
        xarin=xarin.sh.build_MultiIndex()
        if xarin.sh.nmax > self.dskel.sh.nmax:
            warn(f"maximum degree of input dataset will be cut off to {self.dskel.sh.nmax}")
            xarin=xarin.sh.truncate(nmax=self.dskel.sh.nmax)

        if xarin.ndim == 1:
            #add a dummy dimension so the code below also works
            onedim=True
            xarin=xarin.expand_dims({"nexpand":[0]},axis=1)
        else:
            onedim=False


        coords={ky:val for ky,val in xarin.coords.items() if ky != "shg"}
        coords.update({ky:val for ky,val in self.dskel.coords.items() if ky != "shg"})
        dsout=xr.Dataset(coords=coords)
        shp=[len(dsout[dim]) for dim in dsout.sizes]
        dims=tuple(ky for ky,val in dsout.sizes.items())
        dsout["out"]=(dims,np.zeros(shp))
        
        self.dskel["xarin"]=xarin

        self.dskel=self.dskel.fillna(0.0)
        cdef double lon
        cdef double lat
        cdef int ilat
        cdef int ilon
        cdef int nlon=len(dsout.lon)
        cdef int nlat=len(dsout.lat)
        cdef double[::1] lonv=dsout.lon.values
        cdef double[::1] latv=dsout.lat.values
        cdef double[:,::1] xarintmp=self.dskel.xarin.values
        cdef double [:,:,::1] outv=dsout.out.values
        cdef double [::1] ynm
        # cdef:
            # double alpha=1.0
            # double beta=0.0
            # int m=
            # int n=
            # int lda=n
            # int incx=1
            # int incy=1
            # char *transa='T'

        cdef int overwrite_y=0
        for ilat in range(nlat):
            lat=latv[ilat]
            for ilon in range(nlon):
                lon=lonv[ilon]
                ynm=self.ynm.icall(lon,lat)
                # dgemv(transa,&m,&n,&alpha,&xarintmp[0,0],&lda,&ynm[0],&incx,&beta,&outv[0,ilon,ilat],&incy)
                outv[:,ilon,ilat]=np.dot(ynm,xarintmp)
    
        if onedim:
            #remove the dummy dimension again
            dsout=dsout.squeeze("nexpand",drop=True)

        return dsout.out
        
