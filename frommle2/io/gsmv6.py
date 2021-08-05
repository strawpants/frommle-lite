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
from io import BytesIO
import yaml
import numpy as np

def readGSMv6(fileobj,nmaxstop=sys.maxsize):
    needsClosing=False
    if type(fileobj) == str:
        needsClosing=True
        if fileobj.endswith('.gz'):
            fileobj=gzip.open(fileobj,'rb')
        else:
            fileobj=open(fileobj,'rb')

    #first read the yaml header 
    buf=BytesIO()
    for ln in fileobj:
        if b'# End of YAML header' in ln:
            break
        else:
            buf.write(ln)
    hdr=yaml.safe_load(buf.getvalue())["header"]
    
    #setup global attributes
    attr={}
    attr["nmaxfile"]=hdr["dimensions"]["degree"]
    if not "nmax" in attr:
        attr["nmax"]=attr["nmaxfile"]

    attr["tstart"]=hdr["global_attributes"]["time_coverage_start"]
    attr["tend"]=hdr["global_attributes"]["time_coverage_end"]

    nonstand=hdr["non-standard_attributes"]

    attr["gm"]=nonstand["earth_gravity_param"]["value"]
    attr["re"]=nonstand["mean_equator_radius"]["value"]
    

    nmax=attr["nmax"]

    nsh=xr.DataArray.sh.nsh(nmax,squeeze=True)
    
    cnm=np.zeros([nsh])
    sigcnm=np.zeros([nsh])
    ncount=0
    nmt=[]
    #continue reading the data
    dataregex=re.compile(b'^GRCOF2')
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
