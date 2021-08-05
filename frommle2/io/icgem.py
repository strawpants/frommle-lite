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

import gzip
import xarray as xr
from frommle2.sh.xarraysh import *
import re
import sys
import numpy as np

def readIcgem(fileobj,nmaxstop=sys.maxsize):
    needsClosing=False
    if type(fileobj) == str:
        needsClosing=True
        if fileobj.endswith('.gz'):
            fileobj=gzip.open(fileobj,'rb')
        else:
            fileobj=open(fileobj,'rb')

    #first read the icgem header 
    inheader=False
    hdr={}
    for ln in fileobj:
        if b'begin_of_head' in ln:
            inheader=True
            continue
        if b'end_of_head' in ln:
            break
        
        spl=ln.decode('utf-8').split()
        if len(spl) == 2:
            #insert name value pairs in the hdr dict
            hdr[spl[0]]=spl[1]
    
    #extract relevant parameters from the header
    attr={}
    try:
        nmaxsupp=int(hdr["max_degree"])
        attr["nmaxfile"]=nmaxsupp
        if nmaxsupp < nmaxstop:
            attr["nmax"]=nmaxsupp
        else:
            attr["nmax"]=nmaxstop
        nmax=attr["nmax"]

        if nmax > nmaxsupp:
            logging.warning("warning nmax requested larger than supported, higher degree coefficients will be set to zero")


        if 'format' in hdr:
            attr["format"]=hdr['format']
        else:
            attr["format"]="icgem"

        attr["gm"]=float(hdr["earth_gravity_constant"]),
        attr["re"]=float(hdr["radius"])
        attr["modelname"]=hdr["modelname"]
    except KeyError:
    #some values may not be present but that is ok
        pass

    nsh=xr.DataArray.sh.nsh(nmax,squeeze=True)
    cnm=np.zeros([nsh])
    sigcnm=np.zeros([nsh])
    ncount=0
    nmt=[]
    #continue reading the data
    dataregex=re.compile(b'^gfc')
    for ln in fileobj:
        if dataregex.match(ln):
            lnspl=ln.split()
            n=int(lnspl[1])
            if n> nmaxstop:
                if ncount > nsh:
                    #all required coefficients have been read (no need to read the file further)
                    break
                continue
                

            m=int(lnspl[2])

            cnm[ncount]=float(lnspl[3])
            sigcnm[ncount]=float(lnspl[5])
            nmt.append((n,m,trig.c))
            ncount+=1
            
            #possibly also add snm coefficients
            if m!=0:
                cnm[ncount]=float(lnspl[4])
                sigcnm[ncount]=float(lnspl[6])
                nmt.append((n,m,trig.s))
                ncount+=1

    if needsClosing:
        fileobj.close()
    
    ds=xr.Dataset(data_vars=dict(cnm=(["shg"],cnm[0:ncount]),sigcnm=(["shg"],sigcnm[0:ncount])),coords={"shg":xr.DataArray.sh.mi_fromtuples(nmt)},attrs=attr)
    return ds
