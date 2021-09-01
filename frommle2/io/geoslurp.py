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
from sqlalchemy import create_engine, func
from sqlalchemy.event import listen
from sqlalchemy.types import LargeBinary
import os

from geoslurp.db import GeoslurpConnector
from geoslurp.dataset import PandasBase
from geoalchemy2 import Raster

import shutil

def wkb2shapely(entry):
    return shapely.wkb.loads(str(entry),hex=True)

def gdal2rastio(entry):
    return MemoryFile(entry.tobytes())



def readDataFrame(eng,qry,index_col=None):
    """Reads a dataframe from a database engine and convert to GeoDataFrame when a geometry column is present"""
    #try reading as spatially aware database (postgis, spatialite)
    try:
        df=gpd.read_postgis(qry,eng,index_col=index_col)
    except ValueError:
        #possible failure when this is not a table which has a geometry column, so try again with reading a non-postgis sql query
        df=pd.read_sql_query(qry,eng,index_col=index_col)

    return df


def saveDataFrame(gsconn,df,name,schema="public",overwrite=False):
    """Saves a (geo) dataframe to a database engine"""
    TableClass=type(name,(PandasBase,),{"scheme":schema})
    Table=TableClass(gsconn)
    if overwrite:
        zarrar=Table.outdbArchiveName()
        if os.path.exists(zarrar):
            shutil.rmtree(zarrar)
        Table.dropTable()

    Table.register(df=df)





# def load_spatialite(dbapi_conn, connection_record):
        # dbapi_conn.enable_load_extension(True)
        # #ok below is not really portable and only works for linux
        # # dbapi_conn.load_extension('/usr/lib/mod_spatialite.so')

        # dbapi_conn.execute("SELECT load_extension('mod_spatialite');")

# def createSpatialiteEngine(filename,overwrite=False):
    # """Creates a spatialite engine"""
    # if overwrite and os.path.exists(filename):
        # os.remove(filename)
    # engine = create_engine(f"sqlite:///{filename}", echo=True)
    # listen(engine, 'connect', load_spatialite)
    # if overwrite:
        # engine.execute("SELECT InitSpatialMetaData(1);")
    # return engine


