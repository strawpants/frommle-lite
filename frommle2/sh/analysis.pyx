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

import xarray as xr
import cython
import numpy as np
cimport numpy as np
from frommle2.sh.ynm cimport Ynm
import frommle2.sh.xarraysh

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
        self.dskel.sh.build_MultiIndex()
        
    def __call__(self,xarin):
        # if xarin.ndim == 1:
            # raise NotImplementedError("can currently cope only with cnm vectors")
        #set up output dataarray
        return xarin #.drop_vars("shg").coords.update(self.dskel.drop_vars("shg").coords)  
        
