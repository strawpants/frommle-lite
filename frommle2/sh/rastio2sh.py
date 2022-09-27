# This file is part of Frommle
# Frommle is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.

# Frommle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with Frommle; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# Author Roelof Rietbroek (roelof@wobbly.earth), 2021


from pyshtools.expand import SHExpandDH
import numpy as np
import xarray as xr

import frommle2.sh.xarraysh

def rastio2shDH(rio,nmax=100,squeeze=True):
    """Converts an equidistant (sub) grid to spherical harmonic 4-pi normalized coefficients, using the Driscoll Healy approach using shtools"""

    if rio.crs.to_epsg() != 4326:
        raise NotImplementedError("Cannot yet handle non crs-4326 projections")

    if rio.transform[1] != 0 or rio.transform[3] != 0:
        raise NotImplementedError("Cannot yet handle skewed transforms")

    ddist=rio.transform[0]

    if abs(rio.transform[4]) != ddist:
        raise NotImplementedError("Cannot yet handle non equidistant rasters")

    # we need to check whether the grid is correctly aligned
    x0,y0=rio.xy(0,0)

    if x0 < 0:
        shft=-180.0
    else:
        shft=0

    if x0%ddist != 0 or y0%ddist != 0:
        raise NotImplementedError("rasterio is not correctly aligned for global gridline registered grid")

    ithPixFromLeft=int((x0-shft)/ddist)
    ithPixFrom90N=int((90-y0)/ddist)


    gheight=int(180/ddist)
    gwidth=2*gheight
    #construct a global numpy grid (extend the grid to 0,360 and -90,90)
    globrast=rio.read(1,window=((-ithPixFrom90N,gheight-ithPixFrom90N),(-ithPixFromLeft,gwidth-ithPixFromLeft)),boundless=True)
    if shft  == -180.0:
        #shift the array to 0 360 (which is what SHExpandDH expects)
        globrast=np.roll(globrast,int(gwidth/2),axis=1)


    clm=SHExpandDH(globrast,sampling=2,lmax_calc=nmax)

    return xr.DataArray.sh.from_cnm(clm,squeeze=squeeze)
    

