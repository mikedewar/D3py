import pandas
import d3py
from d3py.deployable import FileSystem

import logging

"""
This example is based on d3py_bar.py but the goal is to highlight 
how to deploy the figure. For the initial release, deploy simple allows
one save the static files to the file system. One could imagine implemented
other versions to deploy to the cloud. 
"""

df = pandas.DataFrame(
    {
        "count" : [1,4,7,3,2,9],
        "apple_type": ["a", "b", "c", "d", "e", "f"],
    }
)

# by default the deploy method will save the static files to the file system.
with d3py.PandasFigure(df) as p:
    p += d3py.Bar(x = "apple_type", y = "count", fill = "MediumAquamarine")
    p += d3py.xAxis(x = "apple_type")
    # default = look for deploy directory in cwd.
    p.deploy() 
    # For a given call you can overide the default by providing an argument
    p.deploy(ephermeral_dir='/tmp/d3py') 


# if you want to change the default directory, set the dest_dir argument
# in the FileSystem constructor.  
p2 = d3py.PandasFigure(df, deploy=FileSystem(dest_dir="/tmp"))
