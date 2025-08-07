"""
PlixLab Slide Module

This module contains the Slide class for creating individual presentation slides.
"""

import io
from typing import Any, Dict, List, Union, TYPE_CHECKING
import numpy as np
import plotly.io as pio
from .utils import get_style, process_plotly, process_bokeh
from .shape import run as shape
from . import Bibliography
from bokeh.embed import json_item
from .presentation import Presentation


class Slide:
    """
    Individual slide for presentations with various content types.

    A Slide can contain multiple components like text, images, plots, videos,
    3D models, and interactive elements. Each component can have custom animations.

    Args:
        background (str): Background color in hex format. Defaults to '#303030'.

    Attributes:
        content (list): List of components added to the slide
        style (dict): Slide styling including background color
        animation (list): Animation definitions for slide components
    """


    def __init__(self, background: str = "#303030") -> None:

        self._content: List[Dict[str, Any]] = []
        self._style: Dict[str, str] = {"backgroundColor": background}
        self._animation: List[Dict[str, Any]] = []


    def _get(self, slide_ID: str) -> Dict[str, Any]:
        """
        Generate slide data with the specified ID.

        Args:
            slide_ID: Unique identifier for this slide, provided by the Presentation class.

        Returns:
            Dictionary containing slide data with children, style, animation, and title
        """

        animation = self._process_animations()

        children = {slide_ID + "_" + str(k): tmp for k, tmp in enumerate(self._content)}

        data = {
            "children":  children,
            "style":     self._style,
            "animation": animation

        }

        return {slide_ID: data}
    

    def _add_animation(self, **argv: Any) -> None:
        """
        Add animation sequence to the current component.

        Args:
            **argv: Animation parameters including:
                - animation (list/int): Animation sequence definition
        """

        animation = argv.setdefault("animation", [1])
        self._animation.append(animation)

    def _process_animations(self) -> List[Dict[str, bool]]:
        """
        Process animation sequences for this slide.

        Converts animation definitions into event sequences that control
        component visibility during slide transitions.

        Returns:
            list: List of animation events for each click/transition
        """

        # Convert animation numbers to lists
        tmp = []
        for x in self._animation:
            if not isinstance(x, list):
                # Convert number to animation sequence
                a = []
                if isinstance(x, int):
                    for i in range(x):
                        a.append(0)
                    a.append(1)
                else:
                    # Handle non-integer, non-list case
                    a.append(1)
                tmp.append(a)
            else:
                tmp.append(x)

        # Expand animations to same length
        tmp2 = [len(i) for i in tmp]
        if len(tmp2) > 0:
            n_events = max(tmp2)
            for k, i in enumerate(tmp):
                for j in range(n_events - len(i)):
                    # tmp[k] is guaranteed to be a list at this point
                    assert isinstance(tmp[k], list)
                    tmp[k].append(1)

        # Create animation events
        animation = np.array(tmp).T

        slide_events = []
        for idx, click in enumerate(animation):
            event = {}
            for c, status in enumerate(click):
                C_id = f"{c}"
                value = not (bool(status))
                event.update({C_id: value})
            slide_events.append(event)

        return slide_events

    def cite(self, key: Union[str, List[str]], **argv: Any) -> 'Slide':
        """
        Add citation(s) to the slide.

        Args:
            key (str or list): Citation key(s) to format and display
            **argv: Styling options including:
                - fontsize (float): Font size for citations. Defaults to 0.03.
                - animation (list/int): Animation sequence for this component

        Returns:
            Slide: Returns self for method chaining
        """

        if not isinstance(key, list):
            keys = [key]
        else:
            keys = key

        for i, key in enumerate(keys):
            text = Bibliography.format(key, **argv)

            print(f"{i * 4 + 1}%")

            style: Dict[str, str] = {}
            style.setdefault("color", "#DCDCDC")
            style.update(
                {"position": "absolute", "left": "1%", "bottom": f"{i * 4 + 1}%"}
            )

            tmp = {
                "type": "Markdown",
                "text": text,
                "fontsize": argv.setdefault("fontsize", 0.03),
                "style": style,
            }

            self._content.append(tmp)
            self._add_animation(**argv)

        return self

    def text(self, text: str, **argv: Any) -> 'Slide':
        """
        Add text content to the slide.

        Adds markdown-formatted text with customizable styling and positioning.

        Args:
            text: Text content (supports markdown formatting)
            **argv: Styling options including:
                - mode (str): Positioning mode ('center', 'left', 'right', etc.)
                - fontsize (float): Font size as fraction of screen. Defaults to 0.05.
                - animation (list/int): Animation sequence for this component
                - Additional CSS styling options

        Returns:
            Returns self for method chaining.
        """

        argv.setdefault("mode", "center")
        style = get_style(**argv)
        style.setdefault("color", "#DCDCDC")

        tmp = {
            "type": "Markdown",
            "text": text,
            "fontsize": argv.setdefault("fontsize", 0.05),
            "style": style,
        }

        self._content.append(tmp)
        self._add_animation(**argv)
        return self

    def model3D(self, filename: str, **argv: Any) -> 'Slide':
        """
        Add a 3D model to the slide.

        Args:
            filename (str): Path to the 3D model file
            **argv: Styling options including:
                - animation (list/int): Animation sequence for this component
                - Additional positioning and appearance options

        Returns:
            Slide: Returns self for method chaining
        """
        style = get_style(**argv)

        with open(filename, "rb") as f:
            url = f.read()

        tmp = {
            "type": "model3D",
            "className": "interactable componentA",
            "src": url,
            "style": style,
        }

        self._content.append(tmp)
        self._add_animation(**argv)
        return self

    def img(self, url: str, **argv: Any) -> 'Slide':
        """
        Add an image to the slide.

        Supports both local file paths and URLs. Local files are read and embedded.

        Args:
            url (str): Path to local image file or URL to remote image
            **argv: Styling options including:
                - frame (bool): Whether to add a border frame. Defaults to False.
                - frame_color (str): Color of the frame border. Defaults to '#DCDCDC'.
                - animation (list/int): Animation sequence for this component
                - Additional CSS styling options

        Returns:
            Slide: Returns self for method chaining
        """

        if url[:4] != "http":
            with open(url, "rb") as f:
                url_content: Union[bytes, str] = f.read()
        else:
            url_content = url

        style = get_style(**argv)
        if argv.setdefault("frame", False):
            style["border"] = "2px solid " + argv.setdefault("frame_color", "#DCDCDC")

        tmp = {"type": "Img", "src": url_content, "style": style}
        self._content.append(tmp)
        self._add_animation(**argv)
        return self

    def shape(self, shapeID: str, **argv: Any) -> 'Slide':
        """
        Add a generated shape to the slide.

        Args:
            shapeID (str): Identifier for the shape type to generate
            **argv: Styling options including:
                - animation (list/int): Animation sequence for this component
                - Additional shape parameters and positioning options

        Returns:
            Slide: Returns self for method chaining
        """
        style = get_style(**argv)
        image = shape(shapeID, **argv)
        tmp = {"type": "Img", "src": image, "style": style}
        self._content.append(tmp)
        self._add_animation(**argv)
        return self

    def youtube(self, videoID: str, **argv: Any) -> 'Slide':
        """
        Add a YouTube video to the slide.

        Args:
            videoID (str): YouTube video ID (the part after 'v=' in YouTube URLs)
            **argv: Styling options including:
                - mode (str): Display mode. Defaults to 'full'.
                - animation (list/int): Animation sequence for this component
                - Additional CSS styling options

        Returns:
            Slide: Returns self for method chaining
        """

        argv.setdefault("mode", "full")
        style = get_style(**argv)

        url = f"https://www.youtube.com/embed/{videoID}?controls=0&rel=0"

        tmp = {
            "type": "Iframe",
            "className": "interactable",
            "src": url,
            "style": style.copy(),
        }
        self._content.append(tmp)
        self._add_animation(**argv)
        return self

    def matplotlib(self, fig: Any, **argv: Any) -> 'Slide':
        """
        Add a matplotlib figure to the slide.

        Args:
            fig: Matplotlib figure object
            **argv: Styling options including:
                - animation (list/int): Animation sequence for this component
                - Additional positioning and appearance options

        Returns:
            Slide: Returns self for method chaining
        """
        style = get_style(**argv)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        buf.seek(0)
        url = buf.getvalue()
        buf.close()
        tmp = {"type": "Img", "src": url, "style": style}

        self._content.append(tmp)
        self._add_animation(**argv)

        return self

    def bokeh(self, graph: Any, **argv: Any) -> 'Slide':
        """
        Add a Bokeh plot to the slide.

        Args:
            graph: Bokeh plot object
            **argv: Styling options including:
                - animation (list/int): Animation sequence for this component
                - Additional positioning and appearance options

        Returns:
            Slide: Returns self for method chaining.
        """
        process_bokeh(graph)
        style = get_style(**argv)
        item = json_item(graph)

        tmp = {"type": "Bokeh", "graph": item, "style": style}
        self._content.append(tmp)
        self._add_animation(**argv)
        return self

    def plotly(self, fig: Any, **argv: Any) -> 'Slide':
        """
        Add a Plotly graph to the slide.

        Args:
            fig: Plotly figure object or path to JSON file (string)
            **argv: Styling options including:
                - animation (list/int): Animation sequence for this component
                - Additional positioning and appearance options

        Returns:
            Slide: Returns self for method chaining
        """
        if isinstance(fig, str):
            fig = pio.read_json(fig + ".json")

        style = get_style(**argv)
        fig = process_plotly(fig)
        fig_json = fig.to_json()

        component = {"type": "Plotly", "figure": fig_json, "style": style}
        self._content.append(component)
        self._add_animation(**argv)
        return self

    def molecule(self, structure: Any, **argv: Any) -> 'Slide':
        """
        Add a molecular structure visualization to the slide.

        Args:
            structure: Molecular structure data
            **argv: Styling options including:
                - mode (str): Display mode. Defaults to 'full'.
                - animation (list/int): Animation sequence for this component
                - Additional CSS styling options

        Returns:
            Slide: Returns self for method chaining
        """
        argv.setdefault("mode", "full")
        style = get_style(**argv)

        tmp = {
            "type": "molecule",
            "style": style,
            "structure": structure,
            "backgroundColor": self._style["backgroundColor"],
        }

        self._content.append(tmp)
        self._add_animation(**argv)
        return self

    def python(self, **argv: Any) -> 'Slide':
        """
        Add an interactive Python REPL to the slide.

        Uses JupyterLite to provide a Python interpreter in the browser.

        Args:
            **argv: Styling options including:
                - animation (list/int): Animation sequence for this component
                - Additional positioning and appearance options

        Returns:
            Slide: Returns self for method chaining
        """

        style = get_style(**argv)
        url = (
            "https://jupyterlite.readthedocs.io/en/stable/_static/repl/"
            "index.html?kernel=python&theme=JupyterLab Dark&toolbar=1"
        )

        tmp = {"type": "Iframe", "src": url, "style": style}

        self._content.append(tmp)
        self._add_animation(**argv)
        return self

    def embed(self, url: str, **argv: Any) -> 'Slide':
        """
        Embed external content via iframe.

        Args:
            url (str): URL of the content to embed
            **argv: Styling options including:
                - animation (list/int): Animation sequence for this component
                - Additional positioning and appearance options

        Returns:
            Slide: Returns self for method chaining
        """

        style = get_style(**argv)
        tmp = {"type": "Iframe", "src": url, "style": style}
        self._content.append(tmp)
        self._add_animation(**argv)
        return self

    def show(self, **kwargs: Any) -> None:
        """
        Show the slide as a single-slide presentation.

        Args:
            **kwargs: Additional arguments passed to the presentation show method

        Returns:
            None: Opens presentation in web browser
        """
        from .presentation import Presentation

        Presentation([self]).show(**kwargs)

    def save_standalone(self, directory: str = "output") -> None:
        """
      
        Creates a self-contained presentation directory with PlixLab.
     

        Args:
            directory (str): Output directory name. Defaults to 'output'.

        Note:
            - PlixLab core assets (JS/CSS) are saved locally
            - Third-party libraries (Plotly, Bokeh, etc.) use CDN links
        """

        Presentation([self]).save_standalone(directory=directory)

       

    def save_binary(self, filename: str = "data") -> None:
        """
        Save presentation data to a .plx file.

        Saves the presentation data in a binary format that can be loaded later.

        Args:
            filename (str): Output filename without extension. Defaults to 'data'.
        """    

        Presentation([self]).save_binary(filename=filename)

       

    def get_data(self) -> dict:
        """
        Get the slide data (as a dict) as a presentation.

        Returns:
            dict: Slide data formatted as a single-slide presentation
        """

        return Presentation([self]).get_data()
    
    def get_binary(self,title:str='default') -> bytes:
        """
        Get the binary data as a single-slide presentation.

        Returns:
            bytes: Binarized single-presentation data
        """
        return Presentation([self],title).get_binary()
     
