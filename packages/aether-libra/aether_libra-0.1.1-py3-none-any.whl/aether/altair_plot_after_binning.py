from IPython.display import display, Markdown

import polars as pl
import altair as alt
from typing import Literal

from .polars_binning import get_col_bin_auto
from .polars_aggregation import agg_col_y, agg_cols_y
from .debug_tracer import tracer

alt.themes.enable('dark')


"""
plot_histogram_after_binning
"""
@tracer
def plot_histogram_after_binning(
    *dfs: pl.DataFrame,
    col_x: str,
    col_y: str = None,
    col_color: str = 'data_name', # 優先
    chart_title: str = None,

    # scale
    agg_func = pl.count,
    normalize: bool = False,
    num_x_scale_zero: bool = True,

    # binning - numeric
    num_n_bins: int = 10,
    num_sig_digits: int = 3,
    # binning - datetime
    dt_truncate_unit: str = "1mo",

    # color
    col_color_scale_mode: Literal["scheme", "domain_range"] = "domain_range",
    col_color_scale_domain: list[str] = ['train', 'test'], # map元(値)
    col_color_scale_range: list[str] = ['royalblue', 'indianred'], # map先(色)
    col_color_scale_scheme: str = 'category10',
    col_color_legend_title: str = None, 
    opacity_bar: float = 0.5,

    verbose: int = 0,
) -> alt.Chart:

    # if verbose:
    #     print('dfs')
    #     display(dfs)
    
    # bin処理（共通のbinを作る）
    *dfs_binned, trace = get_col_bin_auto(
        *dfs, 
        col=col_x,
        num_n_bins=num_n_bins,
        num_sig_digits=num_sig_digits,
        dt_truncate_unit=dt_truncate_unit,
        verbose=verbose,
        traceable=True,
        )
    df_bin_detail_info = trace.df_bin_detail_info
    col_x_bin = f"{col_x}_bin"
    dfs = [df.with_columns(df_binned) for df, df_binned in zip(dfs, dfs_binned)]

    # col_colorを持っているDataFrameが1つもない場合、col_color_histを外付けする
    # (複数dfの場合などでdf自体への色付け指定と見做す)
    any_df_has_col_color_hist = any(col_color in df.columns for df in dfs)
    if not any_df_has_col_color_hist:
        def _complete_col_color_dataframe(df: pl.DataFrame, index: int) -> pl.DataFrame:
            # col_color 列が無いなら補う
            df = df.with_columns(pl.lit(col_color_scale_domain[index]).alias(col_color))
            return df
        dfs = [_complete_col_color_dataframe(df, index) for index, df in enumerate(dfs)]

    # col_colorを持ってないdfに列を補完する
    dtype_col_color = next(df.schema[col_color] for df in dfs if col_color in df.columns)
    def _complete_col_color(
        df: pl.DataFrame,
    ) -> pl.DataFrame:
        # col_color 列が無いならNull列を足しとく
        if col_color not in df.columns:
            df = df.with_columns(
                pl.lit(None).cast(dtype_col_color).alias(col_color)
            )
        return df
    dfs = [_complete_col_color(df) for df in dfs]

    # col_yを持ってないdfに列を補完する
    if col_y:
        dtype_col_y = next(df.schema[col_y] for df in dfs if col_y in df.columns)
        def _complete_col_y(
            df: pl.DataFrame,
        ) -> pl.DataFrame:
            # col_y 列が無いならNull列を足しとく
            if col_y not in df.columns:
                df = df.with_columns(
                    pl.lit(None).cast(dtype_col_y).alias(col_y)
                )
            return df
        dfs = [_complete_col_y(df) for df in dfs]

    # agg
    # col_y_agg = f'{col_y} ({agg_func.__name__})'
    col_y_agg = None
    def _agg(df):
        nonlocal col_y_agg
        df_agg, trace = agg_col_y(
            df,
            col_x=col_x_bin,
            col_y=col_y,
            col_color=col_color,
            agg_func=agg_func,
            traceable=True,
            )
        col_y_agg = trace.col_y_agg
        return df_agg
    dfs_agg = [_agg(df) for df in dfs]

    # normalize処理 (オプション引数)
    if normalize:
        def _normalize(df_agg):
            # count_total = df_agg.select(pl.col(col_y_agg_count).sum()).item()
            count_total = df_agg.select(pl.col(col_y_agg).sum()).item()
            df_agg = df_agg.with_columns(
                # (pl.col(col_y_agg_count) / count_total).alias(col_y_agg_ratio)
                (pl.col(col_y_agg) / count_total)
            )
            return df_agg
        dfs_agg = [_normalize(df_agg) for df_agg in dfs_agg]
    # col_y_agg = col_y_agg_count if not normalize else col_y_agg_ratio

    # ヒストグラムチャート
    chart_hist = _plot_histogram_over_bin(
        *dfs_agg,
        col_x_bin=col_x_bin,
        col_y_agg=col_y_agg,
        df_bin_detail_info=df_bin_detail_info,
        chart_title=chart_title,

        num_x_scale_zero=num_x_scale_zero,

        col_color_scale_domain=col_color_scale_domain,
        col_color=col_color,
        col_color_scale_mode=col_color_scale_mode,
        col_color_scale_range=col_color_scale_range, # map先(色)
        col_color_scale_scheme=col_color_scale_scheme,
        col_color_legend_title=col_color_legend_title,
        opacity_bar=opacity_bar,

        verbose=verbose,
    )

    return chart_hist


"""
_plot_histogram_over_bin
"""
@tracer
def _plot_histogram_over_bin(
    *dfs_agg: pl.DataFrame,
    col_x_bin: str,
    col_y_agg: str,
    col_color: str = 'data_name', # 優先
    df_bin_detail_info: pl.DataFrame = None,
    chart_title: str = None,

    # scale
    num_x_scale_zero: bool = False,

    # color
    col_color_scale_mode: Literal["scheme", "domain_range"] = "domain_range",
    col_color_scale_domain: list[str] = ['train', 'test'], # map元(値)
    col_color_scale_range: list[str] = ['royalblue', 'indianred'], # map先(色)
    col_color_scale_scheme: str = 'category10',
    col_color_legend_title: str = None, #'data',
    opacity_bar: float = 0.5,
    
    verbose: int = 0,
) -> alt.Chart:

    if verbose:
        print('dfs_agg')
        display(dfs_agg)
    
    if chart_title is None:
        if col_x_bin.endswith("_bin"):
            chart_title = col_x_bin.removesuffix("_bin")
        else:
            chart_title = col_x_bin

    if col_color_legend_title is None:
        col_color_legend_title = chart_title
    
    # 色のスケール(変換ルール)を作成する
    if col_color_scale_mode == 'domain_range':
        col_color_scale_hist=alt.Scale(domain=col_color_scale_domain, range=col_color_scale_range)
    else:
        col_color_scale_hist=alt.Scale(scheme=col_color_scale_scheme) 

    # グラフ描画で必要な列
    cols_needed = [col_x_bin]
    if col_color and col_color not in cols_needed:
        cols_needed.append(col_color)

    # 結合
    df_agg_concat = pl.concat(dfs_agg)

    if df_bin_detail_info is not None:

        df_agg_concat = df_agg_concat.join(df_bin_detail_info, on=col_x_bin, how='left')

        col_bin_start = f"{col_x_bin}_start"
        col_bin_end = f"{col_x_bin}_end"

        df_plot = df_agg_concat.with_columns([
            pl.col(col_bin_start).alias("bin_left"),
            pl.col(col_bin_end).alias("bin_right"),
            pl.col(col_y_agg).alias("bin_top"),
            pl.lit(0).alias("bin_bottom")
        ])

        dtype = df_plot.schema["bin_left"]
        bin_type = "temporal" if dtype in (pl.Datetime, pl.Date) else "quantitative"

        chart = alt.Chart(df_plot).encode(
            x=alt.X("bin_left", type=bin_type, title=None, scale=alt.Scale(zero=num_x_scale_zero)),
            x2="bin_right",
            y=alt.Y("bin_bottom:Q", title=col_y_agg), #, title="count"),
            y2=alt.Y2("bin_top:Q")
        )

    else:
        chart = alt.Chart(df_agg_concat).encode(
            x=alt.X(f"{col_x_bin}:N", title="category"),
            y=alt.Y(f"{col_y_agg}:Q", title="count")
        )

    chart = chart.mark_bar(opacity=opacity_bar, stroke='gray', strokeWidth=1).properties(title=chart_title)

    # mark_bar 後の色指定
    # col_colorの型が数値かカテゴリカルかでスケール表示が変わる
    # 色のタイプ判定（カテゴリ or 数値）
    dtype_col_color = next(df_agg.schema[col_color] for df_agg in dfs_agg if col_color in df_agg.columns)
    is_color_quantitative = col_color and dtype_col_color in (pl.Int64, pl.Float64)
    color_type = 'Q' if is_color_quantitative else 'N'
    col_color_legend_title += f' / {col_color}' if color_type == 'Q' else ''

    # 色エンコーディング
    def _get_enc_color(legend_required:bool) -> alt.Color:
        if col_color:
            enc_color = (
                alt.Color(
                    f"{col_color}:{color_type}",
                    legend=alt.Legend(title=col_color_legend_title) if legend_required else None,
                    scale=col_color_scale_hist
                )
            )
        else:
            enc_color = alt.Undefined
        return enc_color

    chart = chart.encode(
        color=_get_enc_color(legend_required=True)
    )

    return chart


"""
plot_line_after_binning
"""
@tracer
def plot_line_after_binning(
    *dfs: pl.DataFrame,
    col_x: str,
    col_y: str = "sales",
    chart_title: str = None,

    # binning - numeric
    num_n_bins: int = 10,
    num_sig_digits: int = 3,
    # binning - datetime
    dt_truncate_unit: str = "1mo",
    col_color: str = 'data_name', # 優先

    # scale
    agg_func = pl.mean,
    num_y_scale_zero: bool = True,

    # color
    col_color_scale_mode: Literal["scheme", "domain_range"] = "domain_range",
    col_color_scale_domain: list[str] = ['train', 'test'], # map元(値)
    col_color_scale_range: list[str] = ['gold', 'orange'], # map先(色)
    col_color_scale_scheme: str = 'category20', # 'blues', 'reds'
    col_color_legend_title: str = None, #'target',
    opacity_line_point: float = 0.7,
    size_line: int = 1,
    size_point: int = 5,

    verbose: int = 0,
) -> alt.Chart:

    # if verbose:
    #     print('dfs')
    #     display(dfs)
    
    # bin処理（共通のbinを作る）
    *dfs_binned, trace = get_col_bin_auto(
        *dfs, 
        col=col_x,
        num_n_bins=num_n_bins,
        num_sig_digits=num_sig_digits,
        dt_truncate_unit=dt_truncate_unit,
        verbose=verbose,
        traceable=True,
        )
    df_bin_detail_info = trace.df_bin_detail_info
    col_x_bin = f"{col_x}_bin"
    dfs = [df.with_columns(df_binned) for df, df_binned in zip(dfs, dfs_binned)]

    # col_color_histを持っているDataFrameが1つもない場合、col_color_histを外付けする
    # (複数dfの場合などでdf自体への色付け指定と見做す)
    any_df_has_col_color_hist = any(col_color in df.columns for df in dfs)
    if not any_df_has_col_color_hist:
        def _complete_col_color_dataframe(df: pl.DataFrame, index: int) -> pl.DataFrame:
            # col_color 列が無いなら補う
            df = df.with_columns(pl.lit(col_color_scale_domain[index]).alias(col_color))
            return df
        dfs = [_complete_col_color_dataframe(df, index) for index, df in enumerate(dfs)]

    # col_colorを持ってないdfに列を補完する
    dtype_col_color = next(df.schema[col_color] for df in dfs if col_color in df.columns)
    def _complete_col_color(
        df: pl.DataFrame,
    ) -> pl.DataFrame:
        # col_color 列が無いならNull列を足しとく
        if col_color not in df.columns:
            df = df.with_columns(
                pl.lit(None).cast(dtype_col_color).alias(col_color)
            )
        return df
    dfs = [_complete_col_color(df) for df in dfs]

    # col_yを持ってないdfに列を補完する
    if col_y:
        dtype_col_y = next(df.schema[col_y] for df in dfs if col_y in df.columns)
        def _complete_col_y(
            df: pl.DataFrame,
        ) -> pl.DataFrame:
            # col_y 列が無いならNull列を足しとく
            if col_y not in df.columns:
                df = df.with_columns(
                    pl.lit(None).cast(dtype_col_y).alias(col_y)
                )
            return df
        dfs = [_complete_col_y(df) for df in dfs]

    # agg
    # col_y_agg = f'{col_y} ({agg_func.__name__})'
    col_y_agg = None
    def _agg(df):
        nonlocal col_y_agg
        df_agg, trace = agg_col_y(
            df,
            col_x=col_x_bin,
            col_y=col_y,
            col_color=col_color,
            # col_y_agg=col_y_agg,
            agg_func=agg_func,
            traceable=True,
            )
        col_y_agg = trace.col_y_agg
        return df_agg
    dfs_agg = [_agg(df) for df in dfs]

    # bin情報からxとして採用する情報を決定
    if df_bin_detail_info is not None:
        dfs_agg = [
            df_agg.join(df_bin_detail_info, on=col_x_bin, how="left")
            for df_agg in dfs_agg
        ]
        col_bin_median = f"{col_x_bin}_median"
        col_x_line = col_bin_median
    else:
        col_x_line = col_x_bin

    # 折れ線チャート
    chart_line = plot_line(
        *dfs_agg,
        col_x=col_x_line,
        col_y=col_y_agg,
        y_axis_orient='right',
        chart_title=chart_title,

        num_y_scale_zero=num_y_scale_zero,

        col_color=col_color, # 優先
        col_color_scale_mode=col_color_scale_mode,
        col_color_scale_domain=col_color_scale_domain,
        col_color_scale_range=col_color_scale_range, # map先(色)
        col_color_scale_scheme=col_color_scale_scheme,
        col_color_legend_title=col_color_legend_title,
        opacity_line_point=opacity_line_point,
        size_line=size_line,
        size_point=size_point,

        verbose=verbose,
    )

    return chart_line


"""
_plot_line_over_bin
"""
@tracer
def plot_line(
    *dfs: pl.DataFrame,
    col_x: str,
    col_y: str,
    y_axis_orient: Literal['left', 'right'],
    chart_title: str = None,
    
    # scale
    num_y_scale_zero: bool = True,
    
    # color
    col_color: str = None, # 優先
    col_color_scale_mode: Literal["scheme", "domain_range"] = "domain_range",
    col_color_scale_domain: list[str] = ['train', 'test'], # map元(値)
    col_color_scale_range: list[str] = ['gold', 'orange'], # map先(色)
    col_color_scale_scheme: str = 'category20',
    col_color_legend_title: str = 'target',
    opacity_line_point: float = 0.7,
    size_line: int = 1,
    size_point: int = 5,

    verbose: int = 0,
) -> alt.Chart:

    if verbose:
        print('dfs')
        display(dfs)
    
    if chart_title is None:
        if col_x.endswith("_bin"):
            chart_title = col_x.removesuffix("_bin")
        else:
            chart_title = col_x

    if col_color_legend_title is None:
        col_color_legend_title = col_y
    
    # 色のスケール(変換ルール)を作成する
    if col_color_scale_mode == 'domain_range':
        col_color_scale_line=alt.Scale(domain=col_color_scale_domain, range=col_color_scale_range)
    else:
        col_color_scale_line=alt.Scale(scheme=col_color_scale_scheme) 

    # col_color_lineを持っているDataFrameが1つもない場合、col_color_lineを外付けする(複数dfの場合などでdf自体への色付け指定と見做す)
    any_df_has_col_color_line = any(col_color in df.columns for df in dfs)
    def _complete_col_color(df: pl.DataFrame, index: int) -> pl.DataFrame:
        # col_color 列が無いなら補う
        if not any_df_has_col_color_line:
            df = df.with_columns(pl.lit(col_color_scale_domain[index]).alias(col_color))
        return df
    dfs = [_complete_col_color(df, index) for index, df in enumerate(dfs)]

    # グラフ描画で必要な列
    cols_needed = [col_x]
    if col_y and col_y not in cols_needed:
        cols_needed.append(col_y)
    if col_color and col_color not in cols_needed:
        cols_needed.append(col_color)

    # 結合
    df_concat = pl.concat(dfs)

    # グラフベースと共通エンコーディング
    chart_base = alt.Chart(df_concat)
    enc_x = alt.X(col_x)
    enc_y = alt.Y(
        f"{col_y}:Q",
        axis=alt.Axis(orient=y_axis_orient),
        scale=alt.Scale(zero=num_y_scale_zero),
        # title=col_y2_agg,
        title=col_y,
    )

    # col_colorの型が数値かカテゴリカルかでスケール表示が変わる
    # 色のタイプ判定（カテゴリ or 数値）
    dtype_col_color = next(df.schema[col_color] for df in dfs if col_color in df.columns)
    is_color_quantitative = col_color and dtype_col_color in (pl.Int64, pl.Float64)
    color_type = 'Q' if is_color_quantitative else 'N'
    # col_color_legend_title += f' / {col_color}' if color_type == 'Q' else ''
    if color_type == 'Q':
        col_color_legend_title += f' / {col_color}'
    else:
        if col_color_legend_title == col_y:
            col_color_legend_title = col_y

    # 色エンコーディング
    def _get_enc_color(legend_required:bool) -> alt.Color:
        if col_color:
            enc_color = (
                alt.Color(
                    f"{col_color}:{color_type}",
                    legend=alt.Legend(title=col_color_legend_title) if legend_required else None,
                    scale=col_color_scale_line
                )
            )
        else:
            enc_color = alt.Undefined
        return enc_color

    # chart_point
    chart_point = chart_base.mark_point(
        size=size_point,
        opacity=opacity_line_point
    ).encode(
        x=enc_x,
        y=enc_y,
        color=_get_enc_color(legend_required=True)
    )

    # chart_line
    if not is_color_quantitative: # col_colorが数値の場合lineは描画せず、散布図とする
        chart_line = chart_base.mark_line(
            size=size_line,
            opacity=opacity_line_point
        ).encode(
            x=enc_x,
            y=enc_y,
            color=_get_enc_color(legend_required=False)
        )
        # line + point
        chart = alt.layer(chart_line, chart_point).resolve_scale(
            y='shared', color='independent', shape='independent'
        )
    else:
        # 数値color → pointのみ
        chart = chart_point

    return chart


# これもy1, y2とかやめて、重ねるFacadeを作る★
# Facadeも単に重ねるのではなく、最適化してもいいけどな。いや最適化は処理分散するか…極力避けたい
"""
plot_lines_after_binning
"""
@tracer
def plot_lines_after_binning(
    df: pl.DataFrame,
    col_x: str,
    cols_y: list[str] = [],
    y_axis_orient: Literal['left', 'right'] = 'left',
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
    col_color_scale_domain: list[str] = None, # map元(値)
    col_color_scale_mode: Literal["scheme", "domain_range"] = "scheme",
    col_color_scale_range: list[str] = None, # map先(色)
    col_color_scale_scheme: str = 'set2',
    col_color_legend_title: str = '',
    opacity_line_point: float = 0.7,
    size_line: int = 1,
    size_point: int = 5,

    # degug
    verbose: int = 0,
) -> alt.Chart:

    # if verbose:
    #     print('df')
    #     display(df)
    
    # bin処理（共通のbinを作る）
    df_binned, trace = get_col_bin_auto(
        df, 
        col=col_x,
        num_n_bins=num_n_bins,
        num_sig_digits=num_sig_digits,
        dt_truncate_unit=dt_truncate_unit,
        verbose=verbose,
        traceable=True,
        )
    df_bin_detail_info = trace.df_bin_detail_info
    col_x_bin = f"{col_x}_bin"
    df = df.with_columns(df_binned)

    # 集約
    df_agg, trace = agg_cols_y(
        df,
        col_x=col_x_bin,
        cols_y=cols_y,
        agg_func=agg_func,
        traceable=True,
        )
    cols_y_agg = trace.cols_y_agg

    # 折れ線チャート
    chart_line = plot_lines(
        df = df_agg,
        col_x=col_x_bin,
        cols_y=cols_y_agg,
        y_axis_orient=y_axis_orient,
        chart_title=chart_title,

        num_y_scale_zero=num_y_scale_zero,

        col_color_scale_domain=col_color_scale_domain,
        col_color_scale_mode=col_color_scale_mode,
        col_color_scale_range=col_color_scale_range, # map先(色)
        col_color_scale_scheme=col_color_scale_scheme, # 'blues', 'reds'
        col_color_legend_title=col_color_legend_title, #'target',
        opacity_line_point=opacity_line_point,
        size_line=size_line,
        size_point=size_point,

        verbose=verbose,
    )
    return chart_line


"""
plot_lines
"""
@tracer
def plot_lines(
    df: pl.DataFrame,
    col_x: str,
    cols_y: list[str] = [],
    y_axis_orient: Literal['left', 'right'] = 'left',
    chart_title: str = None,

    # scale
    num_y_scale_zero: bool = True,

    # color
    col_color_scale_domain: list[str] = None, # map元(値)
    col_color_scale_mode: Literal["scheme", "domain_range"] = "scheme",
    col_color_scale_range: list[str] = None, # map先(色)
    col_color_scale_scheme: str = 'set2',
    col_color_legend_title: str = '',
    opacity_line_point: float = 0.7,
    size_line: int = 1,
    size_point: int = 5,

    verbose: int = 0,
) -> alt.Chart:

    if verbose:
        print('df')
        display(df)
    
    if chart_title is None:
        if col_x.endswith("_bin"):
            chart_title = col_x.removesuffix("_bin")
        else:
            chart_title = col_x

    # 色のスケール(変換ルール)を作成する
    if col_color_scale_mode == 'domain_range':
        col_color_scale_line=alt.Scale(domain=col_color_scale_domain, range=col_color_scale_range)
    else:
        col_color_scale_line=alt.Scale(scheme=col_color_scale_scheme) 

    # 結合
    def _unpivot(df: pl.DataFrame) -> pl.DataFrame:
        df_unpivoted = df.unpivot(
            on=cols_y,
            index=[col_x],
            variable_name='col_y_name',
            value_name='col_y_value',
        )
        return df_unpivoted
    df_agg_concat = _unpivot(df)

    # if verbose:
    #     print('df_agg_concat')
    #     display(df_agg_concat)

    # グラフベースと共通エンコーディング
    chart_base = alt.Chart(df_agg_concat)
    enc_x = alt.X(col_x)
    enc_y = alt.Y(
        # f"{col_y_agg}:Q",
        f'col_y_value:Q',
        axis=alt.Axis(orient=y_axis_orient), # ★
        scale=alt.Scale(zero=num_y_scale_zero),
        # title=', '.join(cols_y_agg),
        title=', '.join(cols_y),
    )

    color_type = 'N'

    # 色エンコーディング
    def _get_enc_color(legend_required:bool) -> alt.Color:
        enc_color = (
            alt.Color(
                # f"{col_color}:{color_type}",
                f"col_y_name:{color_type}",
                legend=alt.Legend(title=col_color_legend_title) if legend_required else None,
                scale=col_color_scale_line
            )
        )
        return enc_color

    # chart_point
    chart_point = chart_base.mark_point(
        size=size_point,
        opacity=opacity_line_point
    ).encode(
        x=enc_x,
        y=enc_y,
        color=_get_enc_color(legend_required=True)
    )

    # chart_line
    chart_line = chart_base.mark_line(
        size=size_line,
        opacity=opacity_line_point
    ).encode(
        x=enc_x,
        y=enc_y,
        color=_get_enc_color(legend_required=False)
    )
    # line + point
    chart = alt.layer(chart_line, chart_point).resolve_scale(
        y='shared', color='independent', shape='independent'
    )

    return chart
