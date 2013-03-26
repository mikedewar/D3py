import d3py
import util 
import networkx as nx

import logging
logging.basicConfig(level=logging.DEBUG)

G=nx.Graph()
G.add_edge(1,2)
G.add_edge(1,3)
G.add_edge(3,2)
G.add_edge(3,4)
G.add_edge(4,2)

fig = d3py.NetworkXFigure(G, width=500, height=500)
fig += d3py.ForceLayout() 

util.display(fig)
# util.deploy(fig)
