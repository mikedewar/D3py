import numpy as np
import pandas

import d3py
import util

n = 400

df = pandas.DataFrame({
    'd1': np.arange(0,n),
    'd2': np.random.normal(0, 1, n)
})

fig = d3py.PandasFigure(df, "example scatter plot using d3py", width=400, height=400)
fig += d3py.Point("d1", "d2", fill="DodgerBlue")
fig += d3py.xAxis('d1', label="Random")
fig += d3py.yAxis('d2', label="Also random")
util.display(fig)
