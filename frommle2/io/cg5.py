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

import re
import pandas as pd
import geopandas as gpd
from dateutil import parser
from shapely.geometry import Point
from datetime import timedelta,datetime
from copy import copy
class DataConverter:
    """Helper class which parses a data line and returns a dictionary
    A data line is expected to have the following format:
    /-------LAT--------LONG-----ALT.------GRAV.---SD.--TILTX--TILTY-TEMP---TIDE---DUR-REJ-----TIME----DEC.TIME+DATE--TERRAIN---DATE"""
    
    regexData=re.compile('^[0-9]')
    dtold=datetime.min
    sesid=-1
    def __call__(self,ln):
        if not self.regexData.search(ln):
            return None
        
        spl=ln.split()
        if len(spl) != 15:
            raise IOError(f"Don't know how to interpret this data line:\n {ln}")
        #create timestamp from entry
        lat=float(spl[0])
        lon=float(spl[1])
        entry={"sessionid":None}
        entry["alt"]=float(spl[2])
        entry["grav"]=float(spl[3])
        entry["sd"]=float(spl[4])
        entry["tiltx"]=float(spl[5])
        entry["tilty"]=float(spl[5])
        entry["temp"]=float(spl[7])
        entry["cgtide"]=float(spl[8])
        entry["dur"]=int(spl[9])
        entry["rej"]=int(spl[10])
        entry["terrain"]=float(spl[13])
        entry["time"]=parser.parse(f"{spl[14]} {spl[11]}")
        entry["geom"]=Point(lon,lat)

        #check whether a time jump was detected (wrt to the expected duration)
        dt=entry["time"]-self.dtold
        if dt > timedelta(seconds=entry["dur"])*2:
            self.sesid+=1

        entry["sessionid"]=self.sesid
        self.dtold=entry["time"]

        return entry

class MetaConverter:
    """Helper class which parses a metadata line """
    regexMeta=re.compile('^/.+:')
    def __call__(self,ln):
        if not self.regexMeta.search(ln):
            return None
        name,value=ln.replace(":","|",1).replace("/","").replace("\t"," ").replace("\n","").split("|")
        return {name.lstrip():value.lstrip()}

def readCG5Ascii(filename):
    """"Function which takes a CG-5 ascii dump and puts the data and metadata in geopandas dataframe and the dataframe respectively"""
    
    dconv=DataConverter()
    mconv=MetaConverter()
    with open(filename,'rt') as fid:
        entries=[]
        mentry={"sessionid":-2}
        metaentries=[]
        for ln in fid:
            dataentry=dconv(ln)
            if dataentry:
                entries.append(dataentry)
                
                if dataentry["sessionid"] != mentry["sessionid"]:
                    #trigger a new meta entry with incremented sessionid
                    mentry["sessionid"]=dataentry["sessionid"]
                    metaentries.append(copy(mentry))
            else:
                tmpentry=mconv(ln)
                if tmpentry:
                    mentry.update(tmpentry)
    
    return pd.DataFrame(data=metaentries),gpd.GeoDataFrame(data=entries,geometry="geom")
