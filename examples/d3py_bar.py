import pandas
import d3py
import util 

import logging
logging.basicConfig(level=logging.DEBUG)

df = pandas.DataFrame(
    {
        "count" : [1,4,7,3,2,9],
        "apple_type": ["a", "b", "c", "d", "e", "f"],
    }
)

fig = d3py.PandasFigure(df)
fig += d3py.Bar(x = "apple_type", y = "count", fill = "MediumAquamarine")
fig += d3py.xAxis(x = "apple_type")
util.display(fig)

