# Gravity functionals
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

from frommle2.core import LinearSparseFwd
import xarray as xr
import frommle2.sh.xarraysh
from frommle2.constants.earth import a_earth,rho_water,rho_earth
from sparse import diagonalize

class EquivalentWater(LinearSparseFwd):
    """Forward operator which computes equivalent water heights (sh coefficients in meter) from Stokes coefficients"""
    def __init__(self,knlove:xr.DataArray,nmax):
        if not isinstance(knlove,xr.DataArray):
            raise TypeError("Expecting Kn load Love numbers as a xarray Datarray")
        #extract the maximum degree from the input
        self.nmax=nmax
        #create a spherical harmonic multindex (which is the same for both re in and output coordinats)
        incoords=xr.DataArray.sh.nmt_mi(self.nmax)
        degrees=incoords.get_level_values(level='n').astype(int)
        #create a sparse diagonal array with the conversion factors from Stokes to eqh in meter
        kn=knlove.interp(degree=degrees).values
        diagdat=(degrees*2+1)*a_earth*rho_earth/(3*rho_water*(kn+1))
        dia=diagonalize(diagdat.values)

        super().__init__(xr.DataArray(dia,coords={"shg":("shg",incoords)},dims=["shg_t","shg"],name='eqhconv'),"shg")

        
    def __call__(self,shxar):
        
        nmin=shxar.sh.nmin
        nmax=shxar.sh.nmax

        nminf=self.dasparse.sh.nmin
        nmaxf=self.dasparse.sh.nmax

        
        #compute the dot product 
        daout=super().__call__(shxar) 
    
        #fix the multindex coordinate so that the original SHG index is linked to the output coordinates (they are the same after the dot product)
        daout=daout.rename({"shg_t":"shg"}).assign_coords(shg=("shg",self.dasparse.get_index('shg')))
        return daout

