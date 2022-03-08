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


# distutils: language = c++
import cython
from frommle2.sh.legendre cimport Legendre_nm

cdef class Ynm:
    cdef int nmax
    cdef double[::1] pnmcache
    cdef double[:,::1] trigcache
    cdef double[::1] ynm
    cdef double latprev;
    cdef cython.size_t sz
    cdef Legendre_nm[double]*legnm_ptr
