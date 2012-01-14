import d3py
from pandas import DataFrame
import numpy as np

T = 5*np.pi
x = np.linspace(-T,T,100)
a = 0.05
y = np.exp(-a*x) * np.sin(x)
df = DataFrame({
    'time':x,
    'value':y
    })

fig = d3py.Figure(df, name="point_line_example", width=600, height=300, port=8000)

fig += d3py.geoms.Line('time','value')
fig += d3py.geoms.Point('time','value')
fig.show()
