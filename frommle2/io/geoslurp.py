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
import geopandas as gpd
import shapely.wkb
from rasterio.io import MemoryFile

def wkb2shapely(entry):
    return shapely.wkb.loads(str(entry),hex=True)

def gdal2rasterio(entry):
    return MemoryFile(entry.tobytes())




def readDataFrame(eng,qry):
    """Reads a dataframe from a database engine and convert to GeoDataFrame when a geometry column is present"""
    #read from the database engine as a query
    df=pd.read_sql(qry,eng,parse_dates=["time","tstart","tend"])

    if "geom" in df:
        #convert normal data frame to geopandas dataframe
        df["geom"]=df["geom"].apply(wkb2shapely)
        df=gpd.GeoDataFrame(df,geometry="geom")
    
    if "rast" in df:
        #create an additional column which contains rasterio objects
        df["rast"]=df["rast"].apply(gdal2rasterio)

    return df
