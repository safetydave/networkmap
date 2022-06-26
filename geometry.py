"""Utility methods to work with spatial geometry"""

import numpy as np

COINCIDENCE_PRECISION = 0.01


def geom_bb(g):
    return np.array([np.min(g, axis=0), np.max(g, axis=0)])


def clipped_geom_ids(geoms, bb):
    geom_bbs = np.stack([geom_bb(g) for g in geoms])
    bb_deltas = geom_bbs - bb
    in_bb_bl = np.min(bb_deltas[:, 0, :] >= 0, axis=1)
    in_bb_tr = np.min(bb_deltas[:, 1, :] < 0, axis=1)
    in_bb = np.logical_and(in_bb_bl, in_bb_tr)
    return np.argwhere(in_bb).flatten()


def geom_length(g):
    deltas = g[1:] - g[:-1]
    segment_lengths = np.hypot(deltas[:, 0], deltas[:, 1])
    return np.sum(segment_lengths)


def distance(p0, p1):
    d = p1 - p0
    return np.linalg.norm(d)


def norm_dir(p0, p1):
    d = p1 - p0
    return d / np.linalg.norm(d)


def angle(d0, d1=np.array((0, 1))):
    cross = np.cross(d0, d1)
    dot = np.matmul(d0, d1.T)
    return (np.sign(cross) + (cross == 0)) * np.arccos(dot)


def order_from(geom, p0):
    og = geom
    if not distance(geom[0], p0) < COINCIDENCE_PRECISION:
        og = np.flip(geom, axis=0)
    return og


def order_to(geom, p1):
    og = geom
    if not distance(geom[-1], p1) < COINCIDENCE_PRECISION:
        og = np.flip(geom, axis=0)
    return og


def start_direction(geom, p0):
    og = order_from(geom, p0)
    return norm_dir(og[0, :], og[1, :])


def end_direction(geom, p1):
    og = order_to(geom, p1)
    return norm_dir(og[-2, :], og[-1, :])