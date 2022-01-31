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

from frommle2.core import BaseFwd
import xarray as xr
import numpy as np
class YnmFwd(BaseFwd):
    """Forward operator class which computes a spherical harmonic analysis on a set of geographical coordinates or grid"""
    isLinear=True
    def __init__(self,shg,lon=np.arange(-180.0,180.0),lat=np.arange(-90.0,90.0),force2d=False):
        """Initialize the output coordinates
        parameters:
        shg: spherical harmonic index as a list of (n,m,t) tuples,multindex or as xr.DataArray
        lon: longitude in degrees as arraylike, or xarray.DataArray
        lat: latitude in degrees as arraylikem or xarray.DataArray
        output: Linear operator mapping spherical harmonics to spatial locations (DataArray)
        """
        
        #setup the output and input coordinates
        
        if not force2d and len(lon) == len(lat): 
            coords={"lon":("npoints",lon),"lat":("npoints",lat)}
        else:
            coords={"lon":("lon",lon),"lat":("lat",lat)}
        if type(shg) == xr.DataArray:
            try:
                #extracting a multindex directly
                coords["shg"]=("shg",shg.get_index("srhg"))
            except KeyError:
                coords["shg"]=("shg",shg.data)

        else:
            coords["shg"]=("shg",shg)

        self.dsout=xr.Dataset(coords=coords)        


    def __call__(self,shxar):
        """Apply the spherical harmonic analysis"""
        
        if "npoints" in self.dsout.dims:
            #map to a set of points
            return self.analysis1d(shxar)
        else:
            #2d map to a grid
            return self.analysis2d(shxar)

    def analysis1d(self,shxar):
        pass

    def analysis2d(self,shxar):
       """Map the input to a 2d grid""" 
        shp=[len(self.dsout

        #precompute cosine  &  sine  trigonometric terms
        cosmlon=np.cos(m*
        #loop over (co) latitude
        
        # datout=np.zeros(
