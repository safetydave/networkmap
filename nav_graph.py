"""Convert spatial data into graph representation for navigation"""

import networkx as nx
import numpy as np
from scipy.spatial import KDTree
import shape_helper as sh


def terminal_points(gs):
    return np.concatenate([[g[0] for g in gs], [g[-1] for g in gs]])


def coincident_terminal_points(srs):
    tps = terminal_points(sh.get_geoms(srs))
    coincident_ids = list(KDTree(tps).query_pairs(0.01))
    sorted_ids = np.array(sorted(coincident_ids))
    return tps, (sorted_ids[:, 0], sorted_ids[:, 1])


def canonical_map(pairs, num_ids):
    aggregate_js, first_instances = np.unique(pairs[1], return_index=True)
    aggregate_is = pairs[0][first_instances]
    c_map = np.arange(num_ids)
    c_map[aggregate_js] = aggregate_is
    return c_map


def edges_from_coincident(coincident_ids, num_ids):
    c_map = canonical_map(coincident_ids, num_ids)
    num_edges = num_ids // 2
    return np.stack((c_map[:num_edges], c_map[num_edges:])).T


def make_ugraph(srs):
    tps, coincident_ids = coincident_terminal_points(srs)
    geom_edges = edges_from_coincident(coincident_ids, tps.shape[0])
    G = nx.Graph()
    g_edges = list(zip(geom_edges[:,0], geom_edges[:,1]))
    G.add_edges_from(g_edges)
    nx.set_node_attributes(G, {n: tps[n, 0] for n in G.nodes()}, 'x')
    nx.set_node_attributes(G, {n: tps[n, 1] for n in G.nodes()}, 'y')
    nx.set_edge_attributes(G, {g_edges[i]: {'gid': i} for i in range(len(srs))})
    return G


def make_digraph(srs):
    tps, coincident_ids = coincident_terminal_points(srs)
    geom_edges = edges_from_coincident(coincident_ids, tps.shape[0])
    dir_codes = np.array(sh.get_attrs(srs, 'DIR_CODE'))
    # making directed edges
    f_codes = np.logical_or(dir_codes == 'F', dir_codes == 'B')
    r_codes = np.logical_or(dir_codes == 'R', dir_codes == 'B')
    f_gids = np.argwhere(f_codes).flatten()
    r_gids = np.argwhere(r_codes).flatten()
    f_edges = geom_edges[f_gids,:]
    r_edges = np.flip(geom_edges[r_gids,:], axis=1)
    uf_edges, f_edge_uids = np.unique(f_edges, return_index=True, axis=0)
    ur_edges, r_edge_uids = np.unique(r_edges, return_index=True, axis=0)
    u_edges = np.concatenate((uf_edges, ur_edges), axis=0)
    u_gids = np.concatenate((f_gids[f_edge_uids], r_gids[r_edge_uids]), axis=0)
    # making graph
    G = nx.DiGraph()
    tu_edges = list(zip(u_edges[:,0], u_edges[:,1]))
    G.add_edges_from(tu_edges)
    nx.set_node_attributes(G, {n: tps[n, 0] for n in G.nodes()}, 'x')
    nx.set_node_attributes(G, {n: tps[n, 1] for n in G.nodes()}, 'y')
    edge_gid_dict = {e: {'gid': u_gids[j]} for j, e in enumerate(tu_edges)}
    nx.set_edge_attributes(G, edge_gid_dict)
    return G


def node_positions(graph):
    return np.stack([np.array((graph.nodes[n]['x'],
                               graph.nodes[n]['y'])) for n in graph])


class NavGraph:

    def __init__(self, srs, directed=True):
        self.srs = srs
        if directed:
            self.g = make_digraph(srs)
        else:
            self.g = make_ugraph(srs)
        self.node_ids = {i: n for i, n in enumerate(self.g)}
        np_list = [np.array((self.g.nodes[n]['x'], self.g.nodes[n]['y'])) for n in self.g]
        self.np_dict = dict(zip(self.g, np_list))
        self.np_tree = KDTree(np.stack(np_list))

    def node_position(self, n):
        return np.array((self.g.nodes[n]['x'], self.g.nodes[n]['y']))

    def nearest_node(self, pos):
        _, i = self.np_tree.query(pos)
        return self.node_ids[i]

    def edge_gid(self, e):
        return self.g.edges[e]['gid']

    def edge_sr(self, e):
        return self.srs[self.edge_gid(e)]

    def set_edge_attributes(self, attribute_function, label):
        attr_list = attribute_function(self.g, self.srs)
        edge_attr = {e: {label: attr_list[i]} for i, e in enumerate(self.g.edges)}
        nx.set_edge_attributes(self.g, edge_attr)

    def shortest_path(self, start_node, end_node, weight=None):
        path = nx.shortest_path(self.g, start_node, end_node, weight=weight)
        return NavPath(self, path)


def path_edges(path):
    return list(zip(path[:-1], path[1:]))


class NavPath:

    def __init__(self, ngraph, path):
        self.ng = ngraph
        self.path = path
        self.edges = path_edges(path)
        self.edge_gids = [self.ng.g.edges[e]['gid'] for e in self.edges]
        self.edge_srs = [self.ng.srs[gid] for gid in self.edge_gids]

    def node(self, i):
        return self.path[i]

    def edge(self, i):
        return self.edges[i]

    def pivot(self, i):
        return self.egde(i - 1), self.node(i), self.edge(i)

    def pivot_attr(self, i):
        return self.edge_srs[i - 1],\
               self.ng.node_position(self.node(i)),\
               self.edge_srs[i]

#def node_position(G, n):
#    return np.array((G.nodes[n]['x'], G.nodes[n]['y']))


#def edge_gid(G, e):
#    return G.edges[e]['gid']


#def set_edge_attributes(G, srs, attribute_function, label):
#    attr_list = attribute_function(G, srs)
#    edge_attr = {e: {label: attr_list[i]} for i, e in enumerate(G.edges)}
#    nx.set_edge_attributes(G, edge_attr)




def path_edge_gids(G, path_edges):
    return [G.edges[pe]['gid'] for pe in path_edges]
