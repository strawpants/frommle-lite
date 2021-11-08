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

from frommle2.io.binv_legacy import readBINV
import xarray as xr

class SHfilter:
    def __init__(self,ffile):
        ddkdict=readBINV(ffile,unpack=True)
        #create a multindex from the side description
        nmt=[(int(tag[4:7]),int(tag[7:11]),int(tag[1:2] == 'S')) for tag in ddkdict['side1_d']]
        shmi=xr.DataArray.sh.mi_fromtuples(nmt)

        # create an xarray object with a  multindex for the spherical hamronics
        self.dsfilt=xr.DataArray(ddkdict['mat'],coords={"shg":("shg",shmi)},dims=["shg","shg"],name="ddk")


    def __call__(self,shxar):
        

        return 1

