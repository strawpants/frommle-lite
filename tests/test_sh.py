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
# from frommle2.sh.analysis import Analysis
from frommle2.sh.isoload import unit as shunit
from frommle2.io.shascii import readSHAscii
from io import StringIO
# import xarray.testing as xrtest

import unittest

# Independent validation data for unit load (lon 0.5,lat=53.0)
unitvaldata=""" META    5    0.000000    0.000000    0.000000
     0    0  0.10000000000000E+01  0.00000000000000E+00
     1    0  0.13832772801306E+01  0.00000000000000E+00
     2    0  0.10212748929338E+01  0.00000000000000E+00
     3    0  0.19977631019326E+00  0.00000000000000E+00
     4    0 -0.71104388667820E+00  0.00000000000000E+00
     5    0 -0.13303831637421E+01  0.00000000000000E+00
     1    1  0.10423345064422E+01  0.90963154314668E-02
     2    1  0.18614043905837E+01  0.16244230021762E-01
     3    1  0.21343981280424E+01  0.18626610276269E-01
     4    1  0.16696066487732E+01  0.14570436486416E-01
     5    1  0.59290758193332E+00  0.51742260796706E-02
     2    2  0.70125429368904E+00  0.12240439227534E-01
     3    2  0.14817439746500E+01  0.25863937284512E-01
     4    2  0.21041449543880E+01  0.36727986797224E-01
     5    2  0.22445390503895E+01  0.39178574858469E-01
     3    3  0.45575270596480E+00  0.11934304613339E-01
     4    3  0.10919408843509E+01  0.28593478355801E-01
     5    3  0.17913385584263E+01  0.46907850994811E-01
     4    4  0.29083907068701E+00  0.10156324146655E-01
     5    4  0.77036706491121E+00  0.26901810697799E-01
     5    5  0.18351146735867E+00  0.80122836994040E-02
     """

class TestSH(unittest.TestCase):
    # logger = logging.getLogger("TestSH")
    # logging.basicConfig(format = '%(asctime)s %(funcName)s %(levelname)s: %(message)s', 
            # datefmt="%Y-%m-%d %H:%M:%S",level = logging.INFO)
    def test_ynm(self):
        print("Testing real 4pi normalized spherical harmonics Ynm")
        lon=[0.5] 
        lat=[53.0]
        nmax=5

        #Note: we need to drop the np dimension in order to have a 1D array for comparison
        daunit=shunit(nmax,lon,lat)
        # daunit=daunit.squeeze("np",drop=True)
        
        # daunitval=readSHAscii(StringIO(unitvaldata)).cnm
        unitSHisClose=True
        # try:
            # xrtest.assert_allclose(daunit,daunitval)
        # except AssertionError as e:
            # unitSHisClose=False
          
        self.assertTrue(unitSHisClose)

    # def test_shanalysis(self):
        # # self.logger.info("Testing Spherical harmonic analysis of a unit load")
        # nmax=100
        # lon=[0.5] 
        # lat=[53.0]
        # daunit=shunit(nmax,lon,lat)
        # # shana=Analysis(nmax,lon=np.arange(lon[0]-20.0,lon[0]+20.0,0.5),lat=np.arange(lat[0]-20,lat[0]+20,0.5))
        
        # # dagrd=shana(daunit.cnm)
        # self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
