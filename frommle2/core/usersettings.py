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

# Author Roelof Rietbroek (roelof@wobbly.earth), 2021
import yaml
import os
from datetime import datetime
import keyring
from frommle2.core.logger import logger
import getpass

class UserConfig:
    def __init__(self, confFile=None):
        if confFile == None:
            self.confFile=os.path.join(os.path.expanduser('~'),'.frommle2.yaml')
        else:
            self.confFile=confFile
        self.read()
    
    def setDefault(self):
        user=os.environ["USER"]
        self.settings={"User":user,"Contact":user+"@unknown","Institution":"unknown"}

    def write(self):
        self.settings["lastupdate"]=datetime.now()
        with open(self.confFile,'wt') as fid:
            fid.write(yaml.dump(self.settings))

    def read(self):
        #read last used settings
        if os.path.exists(self.confFile):
            #Read parameters from yaml file
            with open(self.confFile, 'r') as fid:
                self.settings=yaml.safe_load(fid)
        else:
            #set defaults 
            self.setDefault()


    def __getitem__(self,key):
        return self.settings[key]

    def __setitem__(self,key,value):
        self.settings[key]=value
    
    def __contains__(self,ky):
        return ky in self.settings
    def keys(self):
        return self.settings.keys()
