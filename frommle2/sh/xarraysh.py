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

# Author Roelof Rietbroek (r.rietbroek@utwente.nl), 2021




import xarray as xr
import numpy as np
import pandas as pd
from enum import IntEnum
from functools import total_ordering


@total_ordering
class trig(IntEnum):
    c=0
    s=1
    # def __lt__(self,other):
        # return self.value < other.value

    # def __int__(self):
        # return self.value


@xr.register_dataarray_accessor("sh")
class SHAccessor:
    _nmax=None
    _nmin=None
    def __init__(self, xarray_obj):
        self._obj = xarray_obj
    
    @property
    def nmin(self):
        """ returns the maximum spherical harmonic degree associated with the shg coordinate"""
        if not self._nmin:
            self._nmin=self._obj.get_index("shg").unique(level='n').min()      
        return self._nmin
    
    @property
    def nmax(self):
        """ returns the maximum spherical harmonic degree associated with the shg coordinate"""
        if not self._nmax:
            self._nmax=self._obj.get_index("shg").unique(level='n').max()      
        return self._nmax
    
    @staticmethod
    def nsh(nmax,nmin=0,squeeze=False):
        assert nmax>=nmin

        sz=(nmax+1)*(nmax+1)
        if not squeeze:
            sz+=nmax+1

        if nmin > 0:
            #possibly remove the number of coefficients which have n < nmin (calls this function itself)
            sz-=SHAccessor.nsh(nmin-1,0,squeeze=squeeze)

        return sz

    @staticmethod
    def zeros(nmax,nmin=0,squeeze=False,name="cnm"):
        """Initialize an spherical harmonic DataArray based on nmax and nmin"""
        sz=SHAccessor.nsh(nmax,nmin,squeeze)
        coords={"shg":SHAccessor.nmt_mi(nmax,nmin,squeeze=squeeze)}
        return xr.DataArray(data=np.zeros([sz]),dims=["shg"],name=name,coords=coords)


    @staticmethod
    def from_cnm(cnm):
        """Create a xarray from a cnm array from shtools"""
        nmax=cnm.shape[1]-1
        #create a multiindex
        shgmi=SHAccessor.nmt_mi(nmax,squeeze=True)
        #indexing vectors so the sh coeffients match the index
        i_n=shgmi.get_level_values(level='n').astype(int)
        i_m=shgmi.get_level_values(level='m').astype(int)
        i_t=shgmi.get_level_values(level='t').astype(int)
        coords={"shg":shgmi}
        dims=["shg"]
        return xr.DataArray(data=cnm[i_t,i_n,i_m],dims=dims,name="cnm",coords=coords)


    @staticmethod
    def nmt_mi(nmax,nmin=0,squeeze=False):
        """ create a multindex guide which varies with n, then m, and than trigonometric sign"""
        if squeeze:
            nmt=[(n,m,t) for t in [trig.c,trig.s] for n in range(nmin,nmax+1) for m in range(n+1) if not (m == 0 and t == trig.s) ]
        else:
            nmt=[(n,m,t) for t in [trig.c,trig.s] for n in range(nmin,nmax+1) for m in range(n+1)]
        return SHAccessor.mi_fromtuples(nmt)
    
    @staticmethod
    def mi_fromtuples(nmt):
        return pd.MultiIndex.from_tuples(nmt,names=["n","m","t"])
    
    def flatten_shg(self):
        """Serialize n,m,t multindex so it can be written to a file"""
        return SHAccessor._flatten_shg_obj(self._obj)
   
    def build_multindex(self):
        return SHAccessor._build_multindex_obj(self._obj)

    @staticmethod
    def _flatten_shg_obj(obj):
        ds=obj.reset_index("shg")
        return ds.assign_coords(t=(["shg"],[t for t in ds.t.values]))
    
    @staticmethod
    def _build_multindex_obj(obj):
        shgmi=pd.MultiIndex.from_tuples([(n,m,trig(t)) for n,m,t in zip(obj.n.values,obj.m.values,obj.t.values)],names=["n","m","t"])
        return obj.drop(["n","m","t"]).assign_coords(shg=shgmi)

@xr.register_dataset_accessor("sh")
class SHDSAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._nmin=None
        self._nmax=None

    
    def extend(self,nmax=None,nmin=None,fillvalue=0):
        """Truncate minimum and /or maximum degree"""
        
        pass


    def truncate(self,nmax=None,nmin=None):
        """Truncate minimum and /or maximum degree"""

        pass

    @staticmethod
    def nsh(nmax,nmin=0,squeeze=False):
        return SHAccessor.nsh(nmax,nmin,squeeze)

    @property
    def nmin(self):
        """ returns the maximum spherical harmonic degree associated with the shg coordinate"""
        if not self._nmin:
            self._nmin=self._obj.get_index("shg").unique(level='n').min()      
        return self._nmin
    
    @property
    def nmax(self):
        """ returns the maximum spherical harmonic degree associated with the shg coordinate"""
        if not self._nmax:
            self._nmax=self._obj.get_index("shg").unique(level='n').max()      
        return self._nmax

    @staticmethod
    def from_cnm(cnm):
        """Create a xarray dataset from a cnm array from shtools"""
        return SHAccessor.from_cnm(cnm).to_dataset()

    def flatten_shg(self):
        """Serialize n,m,t multindex so it can be written to a file"""
        return SHAccessor._flatten_shg_obj(self._obj)
   
    def build_multindex(self):
        return SHAccessor._build_multindex_obj(self._obj)

