import plotly.colors as pco
from plotly import express as px
from typing import Literal
from .layout import main_layout


__all__ = [
    'list_colors',
    'plot_colorscale',
    'list_colorscale',
]


def list_colors(n: int = 10, colors: list = [], weights: list = [0, 1], input_type: Literal['hex', 'rgb'] = 'hex'):
    """
    Generate a list of interpolated colors based on user-defined anchor colors and weights.

    Parameters
    ----------
    n : int, optional
        Total number of colors to generate. Default is 10.
    colors : list of str or list of tuple
        List of anchor colors to interpolate between. If `input_type` is 'hex',
        provide colors as hex strings (e.g., ['#ff0000', '#00ff00']). If 'rgb',
        provide as RGB tuples (e.g., [(255, 0, 0), (0, 255, 0)]).
    weights : list of float, optional
        Relative positions (in range [0, 1]) corresponding to each anchor color. Must start with 0.
        If fewer weights than colors are given, weights are automatically extended to 1.
        Default is [0, 1].
    input_type : {'hex', 'rgb'}, optional
        Format of input colors. 'hex' (default) or 'rgb'.

    Returns
    -------
    list of str
        A list of `n` interpolated colors in hexadecimal format (e.g., ['#ff0000', '#ee2200', ...]).

    Raises
    ------
    ValueError
        If `colors` is not a valid non-empty list.
        If `weights` does not start with 0.

    Notes
    -----
    - Colors are linearly interpolated between anchor points defined by `colors` and `weights`.
    - If segment lengths result in rounding discrepancies, adjustments are made to ensure exactly `n` colors.

    Examples
    --------
    >>> list_colors(n=5, colors=['#ff0000', '#0000ff'], weights=[0, 1])
    ['#ff0000', '#bf003f', '#800080', '#4000bf', '#0000ff']

    >>> list_colors(n=11, colors=['#ffffff', '#a3005a', '#212121'], weights=[0, 0.9, 1])
    ['#ffffff', '#f5e3ed', '#ebc6da', '#e0aac8', '#d68eb6', '#cc71a3', '#c25591', '#b7397f', '#ad1c6c', '#a3005a', '#212121'] 
    
    >>> list_colors(n=4, colors=[(255, 255, 0), (0, 255, 0)], input_type='rgb')
    ['#ffff00', '#aaff00', '#55ff00', '#00ff00']
    """
    def rgb_to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(*(int(round(c)) for c in rgb))

    if not colors or not isinstance(colors, list):
        raise ValueError("`colors` must be defined as ['#color', '#color', ...]")

    if weights[0] != 0:
        raise ValueError("`weights` must start with [0, ...]")

    while len(weights) > len(colors):
        weights.pop()
    while len(colors) > len(weights):
        weights.append(1)

    if input_type == 'hex':
        colors_rgb = [pco.hex_to_rgb(color) for color in colors]
    else:
        colors_rgb = colors

    # Compute how many colors each segment gets
    segment_counts = []
    for i in range(len(weights) - 1):
        segment_weight = weights[i + 1] - weights[i]
        segment_n = round(segment_weight * n)
        segment_counts.append(segment_n)

    # Adjust for rounding errors
    diff = n - sum(segment_counts)
    segment_counts[-1] += diff

    # Interpolate per segment
    final_colors = []
    for i in range(len(segment_counts)):
        c_start = colors_rgb[i]
        c_end = colors_rgb[i + 1]
        steps = segment_counts[i]

        if steps == 1:
            interpolated_colors = [c_start]
        else:
            interpolated_colors = px.colors.n_colors(c_start, c_end, steps, colortype='tuple')

        # Add colors, avoid duplicate between segments
        if i != 0:
            interpolated_colors = interpolated_colors[1:]
        final_colors.extend(interpolated_colors)

    # Final length fix: ensure final color is included if off by one
    while len(final_colors) < n:
        final_colors.append(colors_rgb[-1])
    while len(final_colors) > n:
        final_colors.pop()

    # Convert to hex
    hex_result = [rgb_to_hex(c) for c in final_colors]
    return hex_result


def list_colorscale(n: int = 10, colorscale: str = 'dense'):
    """
    Generate a list of hexadecimal color values sampled from a Plotly colorscale.

    Parameters
    ----------
    n : int, optional
        Number of colors to sample from the colorscale. Must be >= 2. Default is 10.
    colorscale : str, optional
        Name of the Plotly colorscale to sample from. Default is 'dense'.

    Returns
    -------
    list of str
        A list of hexadecimal color codes (e.g., '#ff5733') evenly sampled from the specified colorscale.

    Notes
    -----
    This function uses Plotly's `sample_colorscale()` function to get RGB color values.
    The RGB strings are manually converted to hexadecimal format.

    Examples
    -----
    >>> print(list_colorscale(n=10, colorscale='oxy'))
    ['#3f0505', '#6d080c', '#77342f', '#6f6e6e', '#8b8a8a', '#a9a9a8', '#cbcac9', '#e7ec94', '#e8da34', '#dcae19']
    """
    # Evenly spaced values from 0 to 1
    scale_values = [i / (n - 1) for i in range(n)]
    # Evenly spaced values from 0 to 1
    rgb_colors = pco.sample_colorscale(colorscale, scale_values)

    # Convert RGB to Hex manually
    def rgb_to_hex(rgb_str):
        r, g, b = [int(x) for x in rgb_str.strip("rgb() ").split(",")]
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    hex_colors = [rgb_to_hex(rgb) for rgb in rgb_colors]

    return hex_colors


# def plot_colorscale():
#     colorscales = {}
#     colorscales['sequential_cont'] = main_layout(px.colors.sequential.swatches_continuous(), width=500, height=1000, x=None, y=None, title='Sequential Continuous')
#     colorscales['sequential_disc'] = main_layout(px.colors.sequential.swatches(), width=500, height=1000, x=None, y=None, title='Sequential Discrete')
#     colorscales['diverging_cont'] = main_layout(px.colors.diverging.swatches_continuous(), width=500, height=600, x=None, y=None, title='Sequential Discrete')
#     colorscales['diverging_disc'] = main_layout(px.colors.diverging.swatches(), width=500, height=600, x=None, y=None, title='Sequential Discrete')
#     colorscales['cyclical_cont'] = main_layout(px.colors.cyclical.swatches_continuous(), width=500, height=400, x=None, y=None, title='Sequential Discrete')
#     colorscales['cyclical_disc'] = main_layout(px.colors.cyclical.swatches(), width=500, height=400, x=None, y=None, title='Sequential Discrete')
#     colorscales['cmocean_cont'] = main_layout(px.colors.cmocean.swatches_continuous(), width=500, height=500, x=None, y=None, title='Sequential Discrete')
#     colorscales['cmocean_disc'] = main_layout(px.colors.cmocean.swatches(), width=500, height=500, x=None, y=None, title='Sequential Discrete')
#     colorscales['carto_disc'] = main_layout(px.colors.carto.swatches(), width=500, height=700, x=None, y=None, title='Sequential Discrete')
#     return colorscales