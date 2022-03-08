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
from frommle2.sh.ynm import Ynm
import xarray as xr
import numpy as np
from frommle2.sh.xarraysh import *

def unit(nmax,lon,lat):
    """Create a unit load in spherical harmonics up to degree nmax, at the specified location"""
    ynm=Ynm(nmax)
    npoints=len(lon)
    if npoints != len(lat):
        raise RuntimeError("Number of longitude points is not consistent with latitude points")
    uload=np.zeros([len(ynm),npoints])
    for i,lonlat in enumerate(zip(lon,lat)):
        uload[:,i]=ynm(lonlat[0],lonlat[1])
    da=xr.DataArray(uload,coords={"lon":("np",lon),"lat":("np",lat),"shg":("shg",xr.DataArray.sh.mi_fromarrays(ynm.nmt().T))},dims=("shg","np"))
    return da.sh.build_MultiIndex()

