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

import xarray as xr
from dask.array.core import einsum_lookup
import sparse
from frommle2.core import BaseFwd
class LinearSparseFwd(BaseFwd):
    isLinear=True #linear operator so their is no need to linearize relative to a apriori state
    def __init__(self,dasparse:xr.DataArray,dim):
        """Base class which contains a linear forward operator which is described by a sparse matrix
        parameter: 
            dasparse: matrix containing the observation equations (xr.DataArray)
            dim: Dimension name over which will be multiplied (str)"""
        
        if not isinstance(dasparse,xr.DataArray):
            raise TypeError("LinearSparseFwd expects a xr.DataArray")
        elif type(dasparse.data) != sparse.COO:
            raise TypeError("LinearSparseFwd expects a xr.DataArray with sparse.COO data")
        #possibly allow dask dataArrays? (before being chunked)
        self.dasparse=dasparse
        self.dim=dim
        
        #do explicit chunking (set this matrix as a single chunk dask array)
        self.dasparse=self.dasparse.chunk(self.dasparse.shape)

        #also register the einsum functions which are needed to do the sparse dot functions
        einsum_lookup.register(sparse.COO,LinearSparseFwd.einsumReplace)
        
    def __call__(self,rhs:xr.DataArray):
        """Executes the forward operator
        parameters:
            rhs: right hand side (xarray dataArray)"""        
        #compute the dot product 
        return self.dasparse.dot(rhs,dims=self.dim) 
        
        
    def dot(self,otherfwd):
        # chain another operator as the right hand side and return a new forward operator
        pass

    @staticmethod
    def einsumReplace(subscripts, *operands, out=None, dtype=None, order='K', casting='safe', optimize=False):
        """Mimics the interface of https://numpy.org/doc/stable/reference/generated/numpy.einsum.html, but uses the sparse.COO dot function"""
        
        if subscripts == "ab,cb->ac":
            return operands[0].dot(operands[1].T)
        elif subscripts == "ab,ca->bc":
            return operands[0].T.dot(operands[1].T)
        elif subscripts == "ab,bc->ac":
            return operands[0].dot(operands[1])
        else:
            raise NotImplementedError(f"Don't know (yet) how to handle this einsum: {subscripts} with sparse.dot operations")
