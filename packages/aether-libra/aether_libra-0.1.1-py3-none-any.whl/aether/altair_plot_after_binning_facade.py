from IPython.display import display, Markdown

import polars as pl
import altair as alt
from typing import Literal

from .altair_plot_after_binning import *
from .debug_tracer import tracer

alt.themes.enable('dark')


"""
plot_histogram_line_after_binning
"""
@tracer
def plot_histogram_line_after_binning(
    *dfs: pl.DataFrame,
    col_x: str,
    col_y1_hist: str = None,
    col_y2_line: str = "sales",
    col_color_scale_domain: list[str] = ['train', 'test'], # map元(値)
    chart_title: str = None,

    # binning - numeric
    num_n_bins: int = 10,
    num_sig_digits: int = 3,
    # binning - datetime
    dt_truncate_unit: str = "1mo",
    col_color: str = 'data_name', # 優先

    # histogram
    # scale
    agg_func_hist = pl.count,
    num_x_scale_zero_hist: bool = True,
    normalize_hist: bool = False,
    # color
    col_color_scale_mode_hist: Literal["scheme", "domain_range"] = "domain_range",
    col_color_scale_range_hist: list[str] = ['royalblue', 'indianred'], # map先(色)
    col_color_scale_scheme_hist: str = 'category10',
    col_color_legend_title_hist: str = None, #'data',
    opacity_bar_hist: float = 0.5,
    
    # line
    # scale
    agg_func_line = pl.mean,
    num_y_scale_zero_line: bool = True,
    # color
    col_color_scale_mode_line: Literal["scheme", "domain_range"] = "domain_range",
    col_color_scale_range_line: list[str] = ['gold', 'orange'], # map先(色)
    col_color_scale_scheme_line: str = 'category20', # 'blues', 'reds'
    col_color_legend_title_line: str = None, #'target',
    opacity_line_point: float = 0.7,
    size_line: int = 1,
    size_point: int = 5,

    # degug
    verbose: int = 0,
) -> alt.Chart:

    chart_hist = plot_histogram_after_binning(
        *dfs,
        col_x=col_x,
        col_y=col_y1_hist,
        col_color_scale_domain=col_color_scale_domain,
        chart_title=chart_title,

        num_n_bins=num_n_bins,
        num_sig_digits=num_sig_digits,
        dt_truncate_unit=dt_truncate_unit,
        col_color=col_color,

        agg_func=agg_func_hist,
        normalize=normalize_hist,
        num_x_scale_zero=num_x_scale_zero_hist,

        col_color_scale_mode=col_color_scale_mode_hist,
        col_color_scale_range=col_color_scale_range_hist,
        col_color_scale_scheme=col_color_scale_scheme_hist,
        col_color_legend_title=col_color_legend_title_hist,
        opacity_bar=opacity_bar_hist,

        verbose=verbose,
    )

    chart_line = plot_line_after_binning(
        *dfs,
        col_x=col_x,
        col_y=col_y2_line,
        col_color_scale_domain=col_color_scale_domain,
        chart_title=chart_title,

        num_n_bins=num_n_bins,
        num_sig_digits=num_sig_digits,
        dt_truncate_unit=dt_truncate_unit,
        col_color=col_color,

        agg_func=agg_func_line,
        num_y_scale_zero=num_y_scale_zero_line,

        col_color_scale_mode=col_color_scale_mode_line,
        col_color_scale_range=col_color_scale_range_line,
        col_color_scale_scheme=col_color_scale_scheme_line,
        col_color_legend_title=col_color_legend_title_line,
        opacity_line_point=opacity_line_point,
        size_line=size_line,
        size_point=size_point,

        verbose=verbose,
    )

    # 総合チャート（ヒストグラム＋折れ線群）
    chart = alt.layer(chart_hist, chart_line).resolve_scale(
        y='independent', color='independent'
    )
    # chart = chart_line
    return chart


"""
plot_lines_after_binning
"""
@tracer
def plot_lines_y1y2_after_binning(
    df: pl.DataFrame,
    # *cols_y: str | list[str],
    col_x: str,
    cols_y1: list[str] = [],
    cols_y2: list[str] = [],
    chart_title: str = None,

    # binning - numeric
    num_n_bins: int = 10,
    num_sig_digits: int = 3,
    # binning - datetime
    dt_truncate_unit: str = "1mo",

    # scale
    agg_func = pl.mean,
    num_y_scale_zero: bool = True,

    # color
    col_color_scale_domain_y1: list[str] = None, # map元(値)
    col_color_scale_mode_line_y1: Literal["scheme", "domain_range"] = "scheme",
    col_color_scale_range_line_y1: list[str] = None, # map先(色)
    col_color_scale_scheme_line_y1: str = 'set2',
    col_color_legend_title_line_y1: str = '',

    col_color_scale_domain_y2: list[str] = None, # map元(値)
    col_color_scale_mode_line_y2: Literal["scheme", "domain_range"] = "scheme",
    col_color_scale_range_line_y2: list[str] = None, # map先(色)
    col_color_scale_scheme_line_y2: str = 'set1',
    col_color_legend_title_line_y2: str = '',

    opacity_line_point: float = 0.7,
    size_line: int = 1,
    size_point: int = 5,

    # degug
    verbose: int = 0,
) -> alt.Chart:

    charts = []
    if cols_y1:
        chart_y1 = plot_lines_after_binning(
            df, 
            col_x=col_x,
            cols_y=cols_y1, 
            y_axis_orient='left',
            chart_title=chart_title,

            num_n_bins = num_n_bins,
            num_sig_digits = num_sig_digits,
            dt_truncate_unit = dt_truncate_unit,

            agg_func = agg_func,
            num_y_scale_zero = num_y_scale_zero,

            col_color_scale_domain=col_color_scale_domain_y1,
            col_color_scale_mode=col_color_scale_mode_line_y1,
            col_color_scale_range=col_color_scale_range_line_y1, # map先(色)
            col_color_scale_scheme=col_color_scale_scheme_line_y1, # 'blues', 'reds'
            col_color_legend_title=col_color_legend_title_line_y1, #'target',
            opacity_line_point = opacity_line_point,
            size_line = size_line,
            size_point = size_point,

            verbose=verbose,
            )
        charts.append(chart_y1)
    if cols_y2:
        chart_y2 = plot_lines_after_binning(
            df, 
            col_x=col_x,
            cols_y=cols_y2, 
            y_axis_orient='right',
            chart_title=chart_title,

            num_n_bins = num_n_bins,
            num_sig_digits = num_sig_digits,
            dt_truncate_unit = dt_truncate_unit,
            
            agg_func = agg_func,
            num_y_scale_zero = num_y_scale_zero,

            col_color_scale_domain=col_color_scale_domain_y2,
            col_color_scale_mode=col_color_scale_mode_line_y2,
            col_color_scale_range=col_color_scale_range_line_y2, # map先(色)
            col_color_scale_scheme=col_color_scale_scheme_line_y2, # 'blues', 'reds'
            col_color_legend_title=col_color_legend_title_line_y2, #'target',
            opacity_line_point = opacity_line_point,
            size_line = size_line,
            size_point = size_point,

            verbose=verbose,
            )
        charts.append(chart_y2)


    # 総合チャート（ヒストグラム＋折れ線群）
    chart = alt.layer(*charts).resolve_scale(
        y='independent', color='independent'
    )
    return chart