"""Render spatial data and path geometries"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import nav_graph as ng
import networkx as nx
import random
import shape_helper as sh

cat_colors = mpl.cm.tab10_r


def plot_srs(ax, srs, limit=4096, decay=2, lw=1):
    class_limit = limit
    for i in range(9):
        class_limit = class_limit // decay
        msrs = sh.matching_srs(srs, 'CLASS_CODE', i)
        plot_geoms(ax, sh.get_geoms(msrs), limit=class_limit, c=cat_colors(i), lw=lw)


def plot_geoms(ax, gs, limit=1024, c='tab:cyan', z=0, lw=1):
    gs_lim = gs if len(gs) < limit else random.sample(gs, limit)
    for g in gs_lim:
        ax.plot(g[:,0], g[:,1], color=c, zorder=z, lw=lw)


def init_fig(width=12, height=9):
    fig, ax = plt.subplots()
    fig.set_figwidth(width)
    fig.set_figheight(height)
    fig.set_facecolor('w')
    return fig, ax


def fig_srs(srs, title='', limit=4096, decay=2):
    fig, ax = init_fig()
    plot_srs(ax, srs, limit, decay)
    plt.axis('off')
    plt.title(title)
    plt.show()


def draw_graph(ngraph, w_labels=False):
    nx.draw(ngraph.g, pos=ngraph.np_dict, with_labels=w_labels,
            node_size=10, node_color='grey', edge_color='lightgrey')


def draw_path(npath, color='tab:orange'):
    nx.draw(npath.ng.g, pos=npath.ng.np_dict, nodelist=npath.path, edgelist=npath.edges,
            node_size=20, width=3, node_color=color, edge_color=color)


def draw_path_geoms(ax, npath, limit=None, from_start=True, color='tab:blue'):
    srs = npath.edge_srs
    if limit is not None:
        srs = srs[:limit] if from_start else srs[-limit:]
    plot_geoms(ax, sh.get_geoms(srs), limit=2048, c=color, z=100, lw=3)