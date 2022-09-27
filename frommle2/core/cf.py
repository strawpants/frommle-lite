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
import os
from datetime import datetime
from frommle2.core.usersettings import UserConfig
import requests
from xml.dom import minidom
userconf=UserConfig()

def cf_register_standard_names(uconf):
    if "cf" in uconf:
        #quick return if already there
        return
        
    resp=requests.get("https://cfconventions.org/Data/cf-standard-names/79/src/cf-standard-name-table.xml")
    cf=minidom.parseString(resp.text)
    uconf["cf"]={un.parentNode.getAttribute("id"):{"units":un.firstChild.data} for un in cf.getElementsByTagName('canonical_units')if un.firstChild is not None}
    uconf.write()
    


def cfadd_global(ds,title=None,comment="Auto generated",references="",update=False):
    if not update:
        ds.attrs={}
    ds.attrs['Conventions'] = 'CF-1.9'
    if title:
        ds.attrs['title'] = title

    ds.attrs['institution'] = userconf["Institution"]
    ds.attrs['source'] = userconf['Contact']
    ds.attrs['history'] = str(datetime.utcnow()) + ' frommle2'
    ds.attrs['references'] = references
    ds.attrs['comment'] = comment


def cfadd_standard_name(dsvar,standard_name,units=None,long_name=None):
    cf_register_standard_names(userconf) # only done when needed

    if standard_name in userconf["cf"]:
        dsvar.attrs=userconf["cf"][standard_name]
        dsvar.attrs["standard_name"]=standard_name
    else:
        raise keyError("requested CF standard_name not found")

    if units:
        #overwrite unit
        dsvar.attrs['units']=units

    if long_name:
        dsvar.attrs["long_name"]=long_name

def cfadd_var(dsvar,units=None,long_name=None):
    if units:
        #overwrite unit
        dsvar.attrs['units']=units

    if long_name:
        dsvar.attrs["long_name"]=long_name

def cfadd_coord(dsvar,xyzt,standard_name=None,units=None,long_name=None):
    if xyzt not in "XYZT":
        raise keyError(f"requested axis is not one of 'X','Y','Z','T'")
    
    if standard_name is not None:
        cfadd_standard_name(dsvar,standard_name,units=units,long_name=long_name)
    else:
        cfadd_var(dsvar,units=units,long_name=long_name)

    #add the axis attribute
    dsvar.attrs["axis"]=xyzt


