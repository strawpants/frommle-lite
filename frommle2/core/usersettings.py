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
        self.settings={"User":user,"Contact":user+"@unknown","Defaultdb":"geoslurp","Authstore":"keyring","geoslurp":{"host":"hostname","port":5432,"user":user,"dbname":"geoslurp"}}

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

    def setAuth(self,key,secret):
        if self.settings["Authstore"] == "keyring":
            keyring.set_password("frommle",key,secret)
        else:
            logger.warning("Note passwords will be stored unencrypted, consider using Authstore='keyring'")
            if not "Auth" in self.settings:
                self.settings["Auth"]={}
            self.settings["Auth"][key][secret]
    
    def getAuth(self,key,message=None):
        secret=None
        if self.settings["Authstore"] == "keyring":
            secret=keyring.get_password("frommle",key)
        elif "Auth" in self.settings:
            if key in self.settings["Auth"]:
                secret=self.settings["Auth"][key]
            
        if secret == None:
            if not message:
                message="Please enter secret/password for alias %s"%key
            secret=getpass.getpass(prompt="%s\n"%(message))
            self.setAuth(key,secret)
        
        return secret

    def dbUri(self,alias=None):
        if alias == None:
            alias=self.settings["Defaultdb"]
        user=self.settings[alias]["user"]
        host=self.settings[alias]["host"]
        port=self.settings[alias]["port"]
        dbname=self.settings[alias]["dbname"]
        secret=self.getAuth(alias,"Please enter password for user %s at database %s on host %s"%(user,dbname,host))
            
        return  "postgresql+psycopg2://"+user+":"+secret+"@"+host+":"+str(port)+"/"+dbname

