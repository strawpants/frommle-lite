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
import pandas as pd

@pd.api.extensions.register_index_accessor("fr")
class FrGuide(pd.MultiIndex):
    """Base class which will be used for frommle specific guides, it inherits from pandas MultiIndex
    so it can be used as a substitute with additional functionality"""
    def __init__(self,tpls,names=None):
        self=pd.MultiIndex.from_tuples(tpls,names=names)

    # def __len__(self):
        # return len(self.mindx)
