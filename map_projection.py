"""Project between different map coordinate systems"""

from pyproj import CRS
from pyproj import Transformer


CRS_WEB = CRS.from_epsg(4326)
CRS_VIC = CRS.from_epsg(7899)
WEB2VIC = Transformer.from_crs(CRS_WEB, CRS_VIC)
VIC2WEB = Transformer.from_crs(CRS_VIC, CRS_WEB)


def web2vic(lat, lng):
    return WEB2VIC.transform(lat, lng)


def vic2web(east, north):
    return VIC2WEB.transform(east, north)
