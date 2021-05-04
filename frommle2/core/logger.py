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


import logging
# frommle wide logger
logger=logging.getLogger("Frommle2")

ch = logging.StreamHandler()

# create formatter
formatter = logging.Formatter('%(name)s-%(levelname)s: %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def debugging():
    return logger.getEffectiveLevel() == logging.DEBUG

def setInfoLevel():
    """Set logging level for both python and c++ to INFO severity"""
    logger.setLevel(logging.INFO)

def setDebugLevel():
    """Set logging level for both python and c++ to DEBUG severity"""
    logger.setLevel(logging.DEBUG)


def setWarningLevel():
    """Set logging level for both python and c++ to WARNING severity"""
    logger.setLevel(logging.WARNING)

def setErrorLevel():
    """Set logging level for both python and c++ to WARNING severity"""
    logger.setLevel(logging.ERROR)
