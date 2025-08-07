Styling
===============================

Components share the same styling options, which include width and size. The width ``w``, ``x`` (from left to right) and ``y`` (from bottom to top) coordinates are all in fractional coordinates, normalized to the size of the slide. The width defaults to ``1`` and the height is computed automatically to preserve proportions. When both ``x`` and ``y`` are given, the component is anchored to its lower left corner (see left panel in the figure below). When ``x`` is not specified (middle panel), then the component is centered horizontally. Analogously, when ``y`` is not specified (right panel), the component is centered vertically. When neither of them is specified, the components is centered along both directions. Component-dependent options are listed in their corresponding doc. 

.. image:: _static/styling.png






