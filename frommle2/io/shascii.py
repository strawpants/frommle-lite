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
import frommle2.sh.xarraysh
from frommle2.core.time import decyear2dt
import numpy as np
import sys


def writeSHAscii(fileobj,ds,cnmv='cnm',sigcnmv=None):
    """Writes a dataset array with sh data to an ascii file"""
    
    needsClosing=False

    if type(fileobj) == str:
        needsClosing=True
        if fileobj.endswith('.gz'):
            fileobj=gzip.open(fileobj,'wt')
        else:
            fileobj=open(fileobj,'wt')
    nmax=ds.sh.nmax

    #TODO extract time epochs in decimal years from the data
    tstart=0.0
    tcent=0.0
    tend=0.0

    fileobj.write(f" META    {nmax}    {tstart}   {tcent}   {tend}\n") 
    #loop over all coefficients (make sure to sort them appropriately)
    sortds=ds.sortby(['n','m','t'])
    cnmvals=np.zeros([2])
    ncoef=0
    for idx,el in zip(sortds.shg,sortds[cnmv].values):
        n,m,t=idx.data[()]
        cnmvals[t]=el

        if m == 0:
            #no need to wait for a sine coefficient
            ncoef=2
            cnmvals[1]=0.0
        else:
            ncoef+=1
        
        if ncoef == 2: 
            fileobj.write(f"{n:6d} {m:6d} {cnmvals[0]:17.10e} {cnmvals[1]:17.10e}\n")
            ncoef=0
            cnmvals[:]=0.0

    if needsClosing:
        fileobj.close()


def readSHAscii(fileobj,nmaxstop=sys.maxsize):
    #extract the maximum degree from the first line
    metaln=fileobj.readline().split()
    nmaxfile=int(metaln[1])

    if nmaxstop <= nmaxfile:
        nmax=nmaxstop
    else:
        nmax=nmaxfile

    #Extract time tags
    stime,ctime,etime=[decyear2dt(float(x)) for x in metaln[2:5]]
    attr={"nmax":nmax,"nmaxfile":nmaxfile,"CTime":ctime,"STime":stime,"ETime":etime}
    
    ln=fileobj.readline().split()
    nd=len(ln)
    if nd == 4:
        sigma=False
    elif nd == 6:
        sigma=True
    else:
        raise InputError(f"Unexpected amount of columns: {len(ln)}")
    nsh=xr.DataArray.sh.nsh(nmax,squeeze=False)

    ncount=0 
    n,m=[int(x) for x in ln[0:2]]
    nmt=[(n,m,0),(n,m,1)]
    cnm=[float(x) for x in ln[2:4]]
    ncount=2 
    if nd == 6:
        sigcnm=[float(x) for x in ln[4:6]]

    for lnstr in fileobj:
        ln=lnstr.split()
        if len(ln) == 0:
            break
        n,m=[int(x) for x in ln[0:2]]
        if n > nmaxstop and ncount > nsh:
            break
        
        nmt.extend([(n,m,0),(n,m,1)])
        cnm.extend([float(x) for x in ln[2:4]]) 
        if nd == 6:
            sigcnm.extend([float(x) for x in ln[4:6]])
        ncount+=2
    #create an xarray dataset
    if nd == 6:
        ds=xr.Dataset(data_vars=dict(cnm=(["shg"],cnm[0:ncount]),sigcnm=(["shg"],sigcnm[0:ncount])),coords={"shg":xr.DataArray.sh.mi_fromtuples(nmt)},attrs=attr)
    else:
        ds=xr.Dataset(data_vars=dict(cnm=(["shg"],cnm[0:ncount])),coords={"shg":xr.DataArray.sh.mi_fromtuples(nmt)},attrs=attr)
    ds.sh.build_MultiIndex()
    return ds
