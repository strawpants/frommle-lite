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

class ForwardOpBase:
    """Base class for a forward operator which uses xarray/pandas style indices/coordinates to refer to the input/output"""
    
    def __init__(self,incoord,outcoord):
        #create an empty dataset with the column coordinates in place
        self.ds=xr.Dataset(coords={"in":incoord,"out":outcoord})
        pass 
    def __call__(self,dsin):
        """Takes an xarray dataset and compute the forward propagated values"""
        raise NotImplementedError("__call__ should be implemented")
        pass
