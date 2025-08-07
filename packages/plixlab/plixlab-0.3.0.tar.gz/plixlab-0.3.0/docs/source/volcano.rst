Volcano Plots
===============

Volcano plots can be embedded via `Dash-bio`_ , which creates ``plotly`` figures. Example:

.. code-block:: python

  from plixlab import Slide
  import dash_bio as dashbio
  import pandas as pd

  df = pd.read_csv('https://git.io/volcano_data1.csv')
  
  fig=dashbio.VolcanoPlot(dataframe=df)

  Slide().plotly(fig).show()

.. import_example:: volcano


.. _Dash-bio: https://dash.plotly.com/dash-bio
