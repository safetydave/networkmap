"""Process a route (path through a graph) to generate directions"""

import geometry as gm
import math
import numpy as np
import shape_helper as sh


COMPASS_SECTOR_CW = ['north', 'north east', 'east', 'south east', 'south']
COMPASS_SECTOR_CCW = ['north', 'north west', 'west', 'south west', 'south']
TURN_SECTOR_CW = ['go straight', 'slight right', 'turn right', 'hard right', 'right u-turn']
TURN_SECTOR_CCW = ['go straight', 'slight left', 'turn left', 'hard left', 'left u-turn']


def sector(angle, sectors=8):
    hsa = math.pi / sectors
    return int((abs(angle) + hsa) / (2 * hsa))


def compass_description(angle):
    desc = COMPASS_SECTOR_CW if angle >= 0 else COMPASS_SECTOR_CCW
    return desc[sector(angle)]


def turn_description(angle):
    desc = TURN_SECTOR_CW if angle >= 0 else TURN_SECTOR_CCW
    return desc[sector(angle)]


def significant_distance(distance):
    log_sig = int(math.log10(distance))
    sig_den = 10 ** (log_sig - 1)
    sig = round(distance / sig_den) * sig_den
    return max(sig, 1)


def road_name(sr):
    return sr.record['EZIRDNMLBL']


def depart_instruction(npath):
    sr = npath.edge_srs[0]
    dep_dir = gm.start_direction(sh.get_geom(sr), npath.node(0))
    return 'depart', gm.angle(dep_dir), road_name(sr)


def continue_instruction(npath, i):
    sr = npath.edge_srs[i]
    length = gm.geom_length(sh.get_geom(sr))
    return 'continue', length, road_name(sr)


def pivot_instruction(npath, i):
    in_sr, node_pos, out_sr = npath.pivot_attr(i)
    in_dir = gm.end_direction(sh.get_geom(in_sr), node_pos)
    out_dir = gm.start_direction(sh.get_geom(out_sr), node_pos)
    turn_angle = gm.angle(out_dir, in_dir)
    return 'pivot', turn_angle, road_name(out_sr)


def is_continuation_pivot(turn_angle, curr_road_name, prev_road_name):
    return sector(turn_angle) == 0 and curr_road_name == prev_road_name


def arrive_instruction(npath):
    sr = npath.edge_srs[-1]
    arr_dir = gm.end_direction(sh.get_geom(sr), npath.node(-1))
    return 'arrive', gm.angle(arr_dir), road_name(sr)


def navigation_instructions(npath):
    steps = [depart_instruction(npath), continue_instruction(npath, 0)]
    for i in range(1, len(npath.path) - 1):
        steps.append(pivot_instruction(npath, i))
        steps.append(continue_instruction(npath, i))
    steps.append(arrive_instruction(npath))
    return steps


def consolidated_instructions(steps):
    consolidated = []
    i = 0
    while i < len(steps):
        s = steps[i]
        if s[0] == 'pivot' and is_continuation_pivot(s[1], s[2], steps[i - 1][2]):
            consolidated[-1] = (consolidated[-1][0],
                                consolidated[-1][1] + steps[i + 1][1],
                                consolidated[-1][2])
            i = i + 2
        else:
            consolidated.append(s)
            i = i + 1
    return consolidated


def navigation_summary(steps):
    start = steps[0][2]
    end = steps[-1][2]
    turn_count = len([s[1] for s in steps if s[0] == 'pivot'])
    total_distance = sum([s[1] for s in steps if s[0] == 'continue'])
    return start, end, total_distance, turn_count