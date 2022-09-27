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
            self._obj=self.build_MultiIndex()
            self._nmin=self._obj.get_index("shg").unique(level='n').min()      
        return self._nmin
    
    @property
    def nmax(self):
        """ returns the maximum spherical harmonic degree associated with the shg coordinate"""
        if not self._nmax:
            self._obj=self.build_MultiIndex()
            self._nmax=self._obj.get_index("shg").unique(level='n').max()      
        return self._nmax
   
    def truncate(self,nmax=None,nmin=None):
        return SHAccessor._truncate(self._obj,nmax,nmin)

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
    def zeros(nmax,nmin=0,squeeze=False,name="cnm",auxcoords={}):
        """0-Initialize an spherical harmonic DataArray based on nmax and nmin"""
        return SHAccessor._initWithScalar(nmax,nmin,0,squeeze,name,auxcoords)
    
    @staticmethod
    def ones(nmax,nmin=0,squeeze=False,name="cnm",auxcoords={}):
        """1-Initialize an spherical harmonic DataArray based on nmax and nmin"""
        return SHAccessor._initWithScalar(nmax,nmin,1,squeeze,name,auxcoords)

    @staticmethod
    def _initWithScalar(nmax,nmin=0,scalar=0,squeeze=False,name="cnm",auxcoords={}):
        """Initialize an spherical harmonic DataArray based on nmax and nmin"""
        sz=SHAccessor.nsh(nmax,nmin,squeeze)
        coords={"shg":SHAccessor.nmt_mi(nmax,nmin,squeeze=squeeze)}
        dims=["shg"]
        shp=[sz]

        #possibly append coordinates
        for dim,coord in auxcoords.items():
            dims.append(dim)
            shp.append(len(coord))
            coords[dim]=coord


        if scalar == 0:
            return xr.DataArray(data=np.zeros(shp),dims=dims,name=name,coords=coords)
        elif scalar == 1:
            return xr.DataArray(data=np.ones(shp),dims=dims,name=name,coords=coords)
        else:
            return xr.DataArray(data=np.full(shp,scalar),dims=dims,name=name,coords=coords)

    
    @staticmethod
    def from_cnm(cnm,squeeze=True):
        """Create a xarray from a cnm array from shtools"""
        nmax=cnm.shape[1]-1
        #create a multiindex
        shgmi=SHAccessor.nmt_mi(nmax,squeeze=squeeze)
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
    def shg(nmax,nmin,squeeze=False,dim="shg"):
        """Convenience function which returns a dictionary which can be used as input for xarray constructors"""
        return {dim:(dim,SHAcessor.nmt_mi(nmax,nmin,squeeze))}


    @staticmethod
    def mi_fromtuples(nmt):
        return pd.MultiIndex.from_tuples(nmt,names=["n","m","t"])
    
    @staticmethod
    def mi_fromarrays(nmt):
        return pd.MultiIndex.from_arrays(nmt,names=["n","m","t"])
    
    def flatten_shg(self):
        """Serialize n,m,t multindex so it can be written to a file"""
        return SHAccessor._flatten_shg_obj(self._obj)
   
    def build_MultiIndex(self):
        return SHAccessor._build_multindex_obj(self._obj)

    @staticmethod
    def _flatten_shg_obj(obj):
        #temporaily not working see https://github.com/Ouranosinc/xscen/pull/67
        # ds=obj.reset_index("shg")
        nd=obj.get_index("shg").get_level_values("n")
        md=obj.get_index("shg").get_level_values("m")
        td=obj.get_index("shg").get_level_values("t")
        return obj.assign_coords(n=("shg",nd),m=("shg",md),t=("shg",td)).drop_vars("shg")
       # return ds.assign_coords(t=(["shg"],[t for t in ds.t.values]))
     
    @staticmethod
    def _build_multindex_obj(obj):
        if "shg" in obj.indexes:
            #already build, so don't bother
            return obj
        #either build from separate coordinate variables (n,m,t)
        if "n" in obj.coords and "m" in obj.coords and "t" in obj.coords:
            shgmi=pd.MultiIndex.from_tuples([(n,m,trig(t)) for n,m,t in zip(obj.n.values,obj.m.values,obj.t.values)],names=["n","m","t"])
            return obj.drop_vars(["n","m","t"]).assign_coords(shg=shgmi)
        elif "shg" in obj.coords:
            #rebuild multiindex from an array of "left-over" tuples
            shgmi=pd.MultiIndex.from_tuples(obj.shg.values,names=["n","m","t"])
            return obj.drop_vars(["shg"]).assign_coords(shg=shgmi)
    
    @staticmethod
    def _truncate(obj,nmax,nmin):
        if nmax is not None:
            indx=(obj.shg.n <= nmax)
        if nmin is not None:
            if indx:
                indx=indx*(obj.shg.n >= nmin)
            else:
                indx=(obj.shg.n >= nmin)
        
        return obj.isel(shg=indx) 

@xr.register_dataset_accessor("sh")
class SHDSAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._nmin=None
        self._nmax=None

    
    def extend(self,nmax=None,nmin=None,fillvalue=0):
        """Extend minimum and /or maximum degree"""
        
        pass

    def truncate(self,nmax=None,nmin=None):
        return SHAccessor._truncate(self._obj,nmax,nmin)

    @staticmethod
    def nsh(nmax,nmin=0,squeeze=False):
        return SHAccessor.nsh(nmax,nmin,squeeze)

    @property
    def nmin(self):
        """ returns the maximum spherical harmonic degree associated with the shg coordinate"""
        if not self._nmin:
            self._obj=self.build_MultiIndex()
            self._nmin=self._obj.get_index("shg").unique(level='n').min()      
        return self._nmin
    
    @property
    def nmax(self):
        """ returns the maximum spherical harmonic degree associated with the shg coordinate"""
        if not self._nmax:
            self._obj=self.build_MultiIndex()
            self._nmax=self._obj.get_index("shg").unique(level='n').max()      
        return self._nmax

    @staticmethod
    def from_cnm(cnm):
        """Create a xarray dataset from a cnm array from shtools"""
        return SHAccessor.from_cnm(cnm).to_dataset()

    def flatten_shg(self):
        """Serialize n,m,t multindex so it can be written to a file"""
        return SHAccessor._flatten_shg_obj(self._obj)
   
    def build_MultiIndex(self):
        return SHAccessor._build_multindex_obj(self._obj)

