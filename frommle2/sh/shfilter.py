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
from copy import copy
from frommle2.core.logger import logger
from dask.array.core import einsum_lookup
import sparse

class SHfilter:
    def __init__(self,ffile,transpose=False):
        ddkdict=readBINV(ffile,unpack=True)
        #create a multindex from the side description
        nmt=[(int(tag[4:7]),int(tag[7:11]),int(tag[1:2] == 'S')) for tag in ddkdict['side1_d']]
        shmi=xr.DataArray.sh.mi_fromtuples(nmt)
        if transpose:
            # create an xarray object with a  multindex for the spherical hamronics
            self.dsfilt=xr.DataArray(ddkdict['mat'],coords={"shg":("shg",shmi)},dims=["shg","shg_t"],name="ddk")
        else:
            # create an xarray object with a  multindex for the spherical hamronics
            self.dsfilt=xr.DataArray(ddkdict['mat'],coords={"shg":("shg",shmi)},dims=["shg_t","shg"],name="ddk")
        
        #do explicit chunking (set this matrix as a one chunk dask array)
        n=self.dsfilt.sizes["shg"]
        self.dsfilt=self.dsfilt.chunk((n,n))

        #also register the einsum functions which are needed to do the sparse dot functions
        einsum_lookup.register(sparse.COO,SHfilter.einsumReplace)

    def __call__(self,shxar):
        
        nmin=shxar.sh.nmin
        nmax=shxar.sh.nmax

        nminf=self.dsfilt.sh.nmin
        nmaxf=self.dsfilt.sh.nmax


        #compute the dot product 
        dsfiltered=self.dsfilt.dot(shxar,dims="shg") 
        
        

        #fix the multindex coordinate
        dsfiltered=dsfiltered.rename({"shg_t":"shg"}).assign_coords(shg=("shg",self.dsfilt.get_index('shg')))
        #add back in non-filtered elements and take out coefficients with degrees higher than nmax input
        if nmin < nminf:
            logger.info(f"Restoring original coefficients below {nminf}")
            dsfiltered=xr.concat([shxar.where(shxar.shg.n < nminf,drop=True),dsfiltered],dim="shg")
        return dsfiltered.where(dsfiltered.shg.n <= nmax,drop=True)


    @staticmethod
    def einsumReplace(subscripts, *operands, out=None, dtype=None, order='K', casting='safe', optimize=False):
        """Mimics the interface of https://numpy.org/doc/stable/reference/generated/numpy.einsum.html, but uses the sparse.COO dot function"""
        
        if subscripts == "ab,cb->ac":
            return operands[0].dot(operands[1].T)
        elif subscripts == "ab,ca->bc":
            return operands[0].T.dot(operands[1].T)
        else:
            raise NotImplementedError(f"Don't know (yet) how to handle this einsum: {subscripts} with sparse.dot operations")

