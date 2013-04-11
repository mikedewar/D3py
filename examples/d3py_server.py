import pandas
import d3py
from d3py.displayable import SimpleServer

import logging

"""
This example is based on d3py_bar.py but the goal is to highlight 
how to configure a server for your figure. For the initial release, 
we simple support Python's SimpleHTTPServer. Got you sights on a different
server? Look at the displayable module. 
"""

df = pandas.DataFrame(
    {
        "count" : [1,4,7,3,2,9],
        "apple_type": ["a", "b", "c", "d", "e", "f"],
    }
)

# by default point your browser to port 8000 at localhost
# This example changes the port. 
with d3py.PandasFigure(df,server=SimpleServer(port=7878)) as p:
    p += d3py.Bar(x = "apple_type", y = "count", fill = "MediumAquamarine")
    p += d3py.xAxis(x = "apple_type")    
    p.show() 
