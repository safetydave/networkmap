# networkmap
Routing and navigation directions from geospatial data

## data requirements

Requires [Vicmap Transport](https://www.land.vic.gov.au/maps-and-spatial/spatial-data/vicmap-catalogue/vicmap-transport) or equivalent spatial data to be present in the `data` folder.

## from go to woah

See the notebook [networkmap_base](networkmap_base.ipynb) for a top-to-bottom walk through with module code replicated inline.

## modules

The core areas of functionality are also broken out into modules:

* [geometry](geometry.py) provides utility methods to work with spatial geometry
* [map_projection](map_projection.py) projects between different map coordinate systems
* [nav_graph](navgraph.py) converts spatial data into a graph representation for navigation and generates routes
* [navigation](navigation.py) process routes to generate turn-by-turn directions
* [renderer](renderer.py) renders/visualises spatial data and path geometries
* [shape_helper](shape_helper.py) provides utility methods to help work with shapeRecords from shapefiles

These modules are used by:

* [networkmap_route](networkmap_route.ipynb) notebook to demonstrate routing
* [networkmap_navigation](networkmap_navigation.ipynb) notebook to demonstrate navigation directions