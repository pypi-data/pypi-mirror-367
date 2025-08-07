"""
PlixLab Utilities Module
"""

import sys
import string
import random
import os
from typing import Any, Dict


def normalize_dict(data: Any) -> Any:
    """
    Recursively normalize a dictionary, list, or tuple for serialization.

    This function ensures that complex nested data structures can be properly
    serialized by converting them to basic Python types.

    Args:
        data: Data structure to normalize (dict, list, tuple, or other)

    Returns:
        Normalized data structure with the same content but serializable types
    """
    if isinstance(data, dict):
        return {k: normalize_dict(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [normalize_dict(v) for v in data]
    else:
        return data


def process_bokeh(fig: Any) -> None:
    """
    Apply PlixLab styling to a Bokeh figure for consistent presentation appearance.

    Configures the figure with white text on transparent background to match
    the PlixLab presentation theme.

    Args:
        fig: Bokeh figure object to style

    Note:
        Modifies the figure in-place
    """
    fig.xaxis.major_tick_line_color = "white"
    fig.xaxis.major_label_text_color = "white"
    fig.yaxis.major_tick_line_color = "white"
    fig.yaxis.major_label_text_color = "white"
    fig.xaxis.axis_label_text_color = "white"
    fig.yaxis.axis_label_text_color = "white"
    fig.background_fill_color = None
    fig.border_fill_color = None
    fig.sizing_mode = "stretch_both"


def process_plotly(fig: Any) -> Any:
    """
    Apply PlixLab styling to a Plotly figure for consistent presentation appearance.

    Configures the figure with white text on transparent background and disables
    interaction features to match the PlixLab presentation theme.

    Args:
        fig: Plotly figure object to style

    Returns:
        Plotly figure object: The styled figure
    """
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        autosize=True,
        legend=dict(font=dict(color="white")),
        xaxis=dict(title=dict(font=dict(color="white")), tickfont=dict(color="white")),
        yaxis=dict(title=dict(font=dict(color="white")), tickfont=dict(color="white")),
        dragmode=None,
    )

    return fig


def convert(value: float) -> str:
    """
    Convert a decimal value to a CSS percentage string.

    Args:
        value (float): Decimal value between 0 and 1

    Returns:
        str: CSS percentage string (e.g., "50%")
    """
    return str(value * 100) + "%"


def get_style(**options: Any) -> Dict[str, str]:
    """
    Generate CSS style dictionary for slide components based on positioning options.

    This function converts high-level positioning parameters into CSS styles
    that can be applied to slide components. It supports multiple positioning
    modes and automatic layout inference.

    Args:
        **options: Styling options including:
            - mode (str): Positioning mode ('manual', 'full', 'hCentered', 'vCentered')
            - x (float): Horizontal position (0-1, left to right)
            - y (float): Vertical position (0-1, bottom to top)
            - w (float): Width (0-1, fraction of slide width)
            - h (float): Height (0-1, fraction of slide height)
            - color (str): Text color
            - align (str): Text alignment

    Returns:
        dict: CSS style properties as key-value pairs

    Notes:
        - If both x and y are provided, mode defaults to 'manual'
        - If only x is provided, mode defaults to 'vCentered'
        - If only y is provided, mode defaults to 'hCentered'
        - Default mode is 'full' if no position is specified
    """
    style = {"position": "absolute"}

    # Apply color if specified
    if "color" in options:
        style["color"] = options["color"]

    # Infer positioning mode based on provided coordinates
    if "x" in options and "y" in options:
        options["mode"] = "manual"
    elif "x" in options and "y" not in options:
        options["mode"] = "vCentered"
    elif "x" not in options and "y" in options:
        options["mode"] = "hCentered"

    mode = options.setdefault("mode", "full")

    if mode == "manual":
        # Manual positioning with explicit coordinates
        style.update(
            {
                "left": convert(options.setdefault("x", 0)),
                "bottom": convert(options.setdefault("y", 0)),
            }
        )

        if "w" in options:
            style["width"] = convert(options["w"])
        if "h" in options:
            style["height"] = convert(options["h"])

    elif mode == "full":
        # Full-screen mode with optional width/height
        w = options.setdefault("w", 1)
        h = options.setdefault("h", 1)
        style.update(
            {
                "left": convert((1 - w) / 2),
                "bottom": convert((1 - h) / 2),
                "width": convert(w),
                "height": convert(h),
            }
        )

    elif mode == "hCentered":
        # Horizontally centered at specified y position
        style.update(
            {
                "bottom": convert(options["y"]),
                "textAlign": "center",
                "alignItems": "center",
                "justifyContent": "center",
            }
        )

        if "w" in options:
            style["width"] = convert(options["w"])
        if "h" in options:
            style["height"] = convert(options["h"])

    elif mode == "vCentered":
        # Vertically centered at specified x position
        style.update(
            {
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "height": convert(options.setdefault("h", 1)),
                "left": convert(options.setdefault("x", 0)),
            }
        )

        if "w" in options:
            style["width"] = convert(options["w"])

    # Apply text alignment if specified
    if "align" in options:
        style["text-align"] = options["align"]
        style["transform"] = "translateX(-50%)"

    return style
