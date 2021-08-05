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
from frommle2.core.guide import FrGuide
from enum import Enum
from functools import total_ordering

@total_ordering
class trig(Enum):
    c=0
    s=1
    def __lt__(self,other):
        return self.value < other.value

    def __int__(self):
        return self.value

class ShGuide(FrGuide):
    """ A spherical harmonic index which contains tuples of degree,order and trigonemetric type"""
    def __init__(self,nmt):
        super().__init__(nmt,names=("n","m","t"))
        self.nmax=self.unique(level='n').max()      
        self.nmin=self.unique(level='n').min()

    @staticmethod
    def nmt(nmax,nmin=0,squeeze=False):
        """ create a multindex guide which varies with n, then m, and than trigonometric sign"""
        if squeeze:
            nmt=[(n,m,t) for t in [trig.c,trig.s] for n in range(nmin,nmax+1) for m in range(n+1) if not (m == 0 and t == trig.s) ]
        else:
            nmt=[(n,m,t) for t in [trig.c,trig.s] for n in range(nmin,nmax+1) for m in range(n+1)]
        return ShGuide(nmt)
