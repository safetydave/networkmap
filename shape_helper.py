"""Utility methods to help work with shapeRecords from shapefiles"""

import numpy as np


def all_srs(sf):
    return sf.shapeRecords()


def get_attrs(srs, attr):
    return [sr.record[attr] for sr in srs]


def get_attr_vals(srs, attr):
    return np.unique(get_attrs(srs, attr), return_counts=True)


def matching_srs(srs, attr, val):
    return [sr for sr in srs if sr.record[attr] == val]


def get_geom(sr):
    return np.array(sr.shape.points)


def get_geoms(srs):
    return [get_geom(sr) for sr in srs]
