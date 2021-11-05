# This file is part of Frommle2
# Frommle is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.

# Frommle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with Frommle; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# Author Roelof Rietbroek (r.rietbroek@utwente.nl), 2021
import struct
import numpy as np
import sparse

def getBDcoords(ddict):

    if not ddict['type'] in ["BDFULLV0","BDFULLVN"]:
        raise RuntimeError("cannot get coordinates for this type of matrix (yet)")

    mxblk=np.max(np.diff(ddict['blockind']))
    mshx,mshy=np.meshgrid([x for x in range(mxblk)],[y for y in range(mxblk)])
    # mshx=mshx.reshape([mshx.size])
    # mshy=mshy.reshape([mshy.size])

    #initialize coords array
    coords=np.full([2,ddict['pval1']*ddict['pval2']],np.nan,dtype=np.int32)

    blkstrt=0
    nshift=0
    for blkend in ddict['blockind']:
        blklen=(blkend-blkstrt)
        sz=blklen**2
        coords[0,nshift:nshift+sz]=mshx[0:blklen,0:blklen].reshape([sz])+blkstrt
        coords[1,nshift:nshift+sz]=mshy[0:blklen,0:blklen].reshape([sz])+blkstrt
        # import pdb;pdb.set_trace()
        #update blockstart
        blkstrt=blkend
        nshift+=sz
    return coords


def readBINV(filename,unpack=False):
    """Reads in a binary file written using the fortran RLFTlbx.
    Pretty slow currenlty so a cpp version is foreseen"""
    dictout={}
    #default to assuming the file is in little endian
    endianness='<'
    #open filename in binary mode
    with open(filename,'rb') as fid:
        #read the endianess checker
        (endian,)=struct.unpack(endianness+"H", fid.read(2))
        #compare the magic number (should be 18754 on a system with the same endiannes of the file)
        if endian != 18754:
            #switch to big endian
            endianness='>'

        dictout['version']='BI'+fid.read(6).decode('utf-8')
        vnum=float(dictout['version'][4:7])

        #read type, description etc

        dictout['type']=fid.read(8).decode('utf-8')
        dictout['description']=fid.read(80).decode('utf-8')

        #read integer meta information
        (nints,ndbls,nval1,nval2)=struct.unpack(endianness+'IIII',fid.read(4*4))

        if vnum < 2.4:
            (pval1,pval2)=struct.unpack(endianness+'II',fid.read(4*2))
        else:
            (pval1,pval2)=struct.unpack(endianness+'LL',fid.read(8*2))


        if vnum <= 2.1:
            if dictout["type"] in ['SYMV0___','BDFULLV0','BDSYMV0','BDFULLVN']:
                nvec=0
                pval2=1
            elif dictout["type"] == "SYMV1___":
                nvec=1
                pval2=1
            elif dictout["type"] == "SYMV2___":
                nvec=2
                pval2=1
            elif dictout["type"] == "FULLSQV0":
                nvec=0
                pval2=pval1

            nread=0
            nval2=nval1
        else:
            (nvec,nread)=struct.unpack(endianness+"II",fid.read(4*2))

        dictout["nval1"]=nval1
        dictout["nval2"]=nval2
        dictout["pval1"]=pval1
        dictout["pval2"]=pval2

        #read type dependent index data
        if dictout['type'] in ["BDSYMV0_","BDSYMVN_","BDFULLV0","BDFULLVN"]:
            (nblocks,)=struct.unpack(endianness+'I',fid.read(4))
            dictout["nblocks"]=nblocks

        if nread >0:
            dictout["readme"]=fid.read(nread*80).decode('utf-8')

        names=[]
        vals=[]
        if nints > 0:
            inames=np.fromfile(fid,dtype='|S24',count=nints).astype('|U24')
            names.extend(list(inames))
            if vnum <= 2.4:
                ivals=np.fromfile(fid,dtype=endianness+'I',count=nints)
            else:
                ivals=np.fromfile(fid,dtype=endianness+'L',count=nints)
            vals.extend(ivals)
        if ndbls >0:
            dnames=np.fromfile(fid,dtype='|S24',count=ndbls).astype('|U24')
            names.extend(list(dnames))
            dvals=np.fromfile(fid,dtype=endianness+'d',count=ndbls)
            vals.extend(dvals)

        if names:
            dictout["meta"]={ky.strip():val for ky,val in zip(names,vals)}

        #read side description data
        dictout["side1_d"]=np.fromfile(fid,dtype='|S24',count=nval1).astype('|U24')

        if dictout["type"] in ['BDSYMV0_','BDFULLV0','BDSYMVN_','BDFULLVN']:
            dictout["blockind"]=np.fromfile(fid,dtype=endianness+'I',count=nblocks)
            #also add coordinates in the full matrix
            dictout["coords"]=getBDcoords(dictout)


        #possibly read second side description
        if dictout['type'] in ['BDFULLV0','BDFULLVN','FULLSQV0','FULLSQVN']:
            if vnum <= 2.2:
                dictout["side2_d"]=dictout["side1_d"]
            else:
                dictout["side2_d"]=np.fromfile(fid,dtype='|S24',count=nval1).astype('|U24')

        elif dictout["type"] == "FULL2DVN":
            dictout["side2_d"]=np.fromfile(fid,dtype='|S24',count=nval2).astype('|U24')


        # read vectors
        if nvec >0:
            dictout["vec"]=np.fromfile(fid,dtype=endianness+"d",count=nvec*nval1).reshape((nval1,nvec),'F')

        # read packed matrix
        pack=np.fromfile(fid,dtype=endianness+'d',count=pval1*pval2)


    if not unpack:
        dictout["pack"]=pack
    else:

        if dictout["type"] in ['BDSYMV0_','BDFULLV0','BDSYMVN_','BDFULLVN']:
            #unpack in sparse matrix
            dictout['mat'] = sparse.COO(dictout['coords'], pack, shape=(dictout['nval1'], dictout['nval1']))
        else: 
            raise Exception("Unpacking of this type not yet supported")






    return dictout
