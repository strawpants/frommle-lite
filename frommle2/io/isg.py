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
import re
def read_isg(fid):
    """Reads a ISGi geoid grid format (https://www.isgeoid.polimi.it/Geoid/format_specs.html) into a xarray DataArray"""
    
    regexstrhead=re.compile('^.+:.+')
    regexflthead=re.compile('^.+=.+')
    regexdata=re.compile('^ +[0-9]')
    grid=[]
    meta={}
    for ln in fid:
        if regexdata.search(ln):
            #add a new row    
            grid.append([float(val) for val in ln.split()])
        elif regexstrhead.search(ln):
            name,val=ln.replace("\n","").split(":")
            meta[name.strip()]=val.strip()
        elif regexflthead.search(ln):

            if ln.find('of_head') > 0:
                continue
            name,val=ln.split("=")
            meta[name.strip()]=float(val)

    #create longitude and latitude vectors
    lon=np.arange(meta["lon min"]+meta['delta lon']/2,meta["lon max"],meta["delta lon"])

    lat=np.arange(meta["lat min"]+meta['delta lat']/2,meta["lat max"],meta["delta lat"])
    
    da=xr.DataArray(grid,coords={"lat":lat,"lon":lon},dims=["lat","lon"],attrs=meta,name="geoid")
    da.lon.attrs.update(long_name="Longitude")
    da.lat.attrs.update(long_name="Latitude")
    return da.where(da != meta["nodata"])

