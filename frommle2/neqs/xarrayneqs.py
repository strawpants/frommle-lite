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


@xr.register_dataset_accessor("neq")
class NEQAccessor:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    
    def reduce(self,variables=None):
        """Reduce (implicitly solve) certain variables in the normal equation system"""
        return self._obj


    def fix(self,variables=None):
        """Fix the indicated variables to its a apriori values"""
        return self._obj

    def set_apriori(self,da):
        """Change the a priori values of the system"""
        return self._obj


    def add(self,other):
        """Add one normal equation system to another. Common parameters will be added, the system will be extended with unique parameters of the other system"""
        return self._obj


