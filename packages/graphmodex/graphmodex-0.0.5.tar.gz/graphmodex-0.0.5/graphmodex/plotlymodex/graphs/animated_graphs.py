import os
import sys

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from typing import Union, Literal, Optional, Dict

sys.path.append(os.path.abspath('..'))
from graphmodex import plotlymodex


__all__ = [
    'animated_scatter',
    'animated_bar',
]


def animated_scatter(
        df:pd.DataFrame,
        x:str,
        y:str,
        animation_frame:str,
        color:Optional[str]=None,
        size:Optional[str]=None,
        symbol:Optional[str]=None,
        colorscale:Optional[list]=None,
        title:str=None,
        width:int=800,
        height:int=600,
        y_range:Optional[tuple]=None,
        x_range:Optional[tuple]=None,
        layout_kwargs:Optional[Dict]=None,
        trace_kwargs:Optional[Dict]=None,
        animation:bool=True,
        auto_fit:bool=True,
        ascending:bool=True,
    ) -> go.Figure:
    """
    Create an animated scatter plot using Plotly Express.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the data to be visualized.
    x : str
        Column name for the x-axis.
    y : str
        Column name for the y-axis.
    animation_frame : str
        Column name for the animation frame (e.g., time or step).
    color : str, optional
        Column name to determine point colors.
    size : str, optional
        Column name to determine the size of each point.
    symbol : str, optional
        Column name to determine the symbol/marker type.
    colorscale : list, optional
        List of color codes to use as the discrete color sequence.
    title : str, optional
        Title of the chart. If None, a default title is generated.
    width : int, optional
        Width of the figure in pixels. Default is 800.
    height : int, optional
        Height of the figure in pixels. Default is 600.
    y_range : tuple, optional
        A tuple (min, max) specifying the y-axis range.
    x_range : tuple, optional
        A tuple (min, max) specifying the x-axis range.
    layout_kwargs : dict, optional
        Additional keyword arguments passed to `fig.update_layout()`.
    trace_kwargs : dict, optional
        Additional keyword arguments to update each trace (e.g., marker settings).
    animation : bool, optional
        If False, disables the animation feature, removing frames and controls.
    auto_fit : bool, default=True
        If True, automatically adjusts the x and y ranges based on the data.
    ascending : bool, default=True
        If True, sorts the DataFrame by the animation frame and color columns in ascending order.

    Returns
    -------
    go.Figure
        A Plotly Figure object representing the animated scatter plot.

    Notes
    -----
    This function wraps `plotly.express.scatter` and applies a custom layout
    using `plotlymodex.main_layout`.

    Examples
    --------
    >>> fig = animated_scatter(
    ...     df=data,
    ...     x='GDP',
    ...     y='LifeExpectancy',
    ...     animation_frame='Year',
    ...     color='Continent',
    ...     size='Population',
    ...     x_log=True
    ... )
    >>> fig.show()
    """

    columns = [animation_frame]
    if color is not None:
        columns.append(color)
    if symbol is not None:
        columns.append(symbol)
    
    df = df.copy(deep=True)
    df = df.sort_values(by=columns, ascending=ascending)

    if isinstance(colorscale, str):
        colorscale = [colorscale]
        
    # Create the scatter plot
    fig = px.scatter(
        df,
        x=x,
        y=y,
        animation_frame=animation_frame,
        color=color,
        size=size,
        symbol=symbol,
        color_discrete_sequence=colorscale,
    )
    
    # Apply trace-level updates if specified
    if trace_kwargs:
        for trace in fig.data:
            trace.update(**trace_kwargs)

    if title is None:
        title = f"Scatter | {x} vs {y} with {animation_frame}"
    
    if (auto_fit):
        # Automatically adjust x and y ranges based on data
        x_range = (df[x].min(), df[x].max()) if x_range is None else x_range
        y_range = (df[y].min(), df[y].max()) if y_range is None else y_range

    # Use your custom layout function
    plotlymodex.main_layout(
        fig=fig,
        title=title,
        x=x,
        y=y,
        width=width,
        height=height,
        y_range=y_range,
        x_range=x_range,
    )

    # Apply additional layout keyword arguments if provided
    if layout_kwargs:
        fig.update_layout(**layout_kwargs)

    if animation is False:
        fig.frames = None
        fig.layout.updatemenus = None
        fig.layout.sliders = None

    return fig



def animated_bar(
        df:pd.DataFrame,
        x:str,
        y:str,
        animation_frame:str,
        agg_func:Literal['count', 'sum', 'mean', 'median', 'min', 'max'] = 'count',
        color:Optional[str]=None,
        pattern_shape=None,
        colorscale:Optional[list]=None,
        title:str=None,
        width:int=800,
        height:int=600,
        barmode:Literal['relative', 'group', 'overlay']='relative',
        y_range:Optional[tuple]=None,
        x_range:Optional[tuple]=None,
        layout_kwargs:Optional[Dict]=None,
        trace_kwargs:Optional[Dict]=None,
        animation:bool=True,
        auto_fit:bool=True,
    ) -> go.Figure:
    """
    Generate an animated bar chart using Plotly Express with optional grouping, coloring, and patterns.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the data to visualize.
    x : str
        Column name to be used on the x-axis.
    y : str
        Column name to be aggregated and used on the y-axis.
    animation_frame : str
        Column name used to define the frames of the animation (e.g., time or step).
    agg_func : {'count', 'sum', 'mean', 'median', 'min', 'max'}, default='count'
        Aggregation function to apply to the y column.
    color : str, optional
        Column name used for color differentiation of bars.
    pattern_shape : str, optional
        Column name used to apply patterns to bars.
    colorscale : list of str or str, optional
        List of color names or a single color name to be used as the color scale.
    title : str, optional
        Title of the chart. If None, a default title will be generated.
    width : int, default=800
        Width of the figure in pixels.
    height : int, default=600
        Height of the figure in pixels.
    barmode : {'relative', 'group', 'overlay'}, default='relative'
        Bar mode to use for the bar chart layout.
    y_range : tuple, optional
        Tuple specifying the range for the y-axis.
    x_range : tuple, optional
        Tuple specifying the range for the x-axis.
    layout_kwargs : dict, optional
        Additional keyword arguments to update the layout.
    trace_kwargs : dict, optional
        Additional keyword arguments to update the bar traces.
    animation : bool, default=True
        Whether to include animation in the resulting figure.
    auto_fit : bool, default=True
        If True, automatically adjusts the x and y ranges based on the data.

    Returns
    -------
    go.Figure
        A Plotly Graph Objects figure containing the animated or static bar chart.

    Examples
    --------
    >>> fig = animated_bar(
    ...     df=data,
    ...     x='GDP',
    ...     y='LifeExpectancy',
    ...     animation_frame='Year',
    ...     agg_func='count',
    ...     color='Continent',
    ...     pattern_shape='Population',
    ... )
    >>> fig.show()
    """

    columns = [x, animation_frame]
    if (color is not None) and (color != x) and (color != y) and (color != animation_frame):
        columns.append(color)
    if (pattern_shape is not None)  and (pattern_shape != x) and (pattern_shape != y) and (pattern_shape != animation_frame) and (pattern_shape != color):
        columns.append(pattern_shape)
    
    df = df.copy(deep=True)
    
    if animation and (color or pattern_shape):
        agg_dict = {
            k: pd.Series.nunique
            for k in [color, pattern_shape]
            if k is not None and k in df.columns
        }

        if agg_dict:
            frame_counts = df.groupby(animation_frame).agg(agg_dict).fillna(0)

            if not frame_counts.empty:
                frame_counts["score"] = frame_counts.sum(axis=1)
                sorted_frames = frame_counts.sort_values("score", ascending=False).index.tolist()
                df[animation_frame] = pd.Categorical(df[animation_frame], categories=sorted_frames, ordered=True)

    df = df.groupby(columns, observed=False)[y].agg(agg_func=agg_func).reset_index()

    if isinstance(colorscale, str):
        colorscale = [colorscale]
        
    # Create the scatter plot
    fig = px.bar(
        df,
        x=x,
        y='agg_func',
        animation_frame=animation_frame,
        color=color,
        pattern_shape=pattern_shape,
        color_discrete_sequence=colorscale,
    )
    
    # Apply trace-level updates if specified
    if trace_kwargs:
        for trace in fig.data:
            trace.update(**trace_kwargs)

    if title is None:
        title = f"Bar | {x} vs {y} with {animation_frame}"
    
    if (auto_fit):
        # Automatically adjust x and y ranges based on data
        x_range = (df[x].min(), df[x].max()) if x_range is None else x_range
        y_range = (df['agg_func'].min(), df['agg_func'].max()) if y_range is None else y_range

    # Use your custom layout function
    plotlymodex.main_layout(
        fig=fig,
        title=title,
        x=x,
        y=agg_func + ' ' + y,
        width=width,
        height=height,
        y_range=y_range,
        x_range=x_range,
        barmode=barmode,
    )

    # Apply additional layout keyword arguments if provided
    if layout_kwargs:
        fig.update_layout(**layout_kwargs)

    if animation is False:
        fig.frames = None
        fig.layout.updatemenus = None
        fig.layout.sliders = None

    return fig