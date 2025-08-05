from IPython.display import display
import polars as pl
import types
import matplotlib.ticker as mticker
import math
from dataclasses import dataclass

from .debug_tracer import tracer


@dataclass
class agg_col_y_trace:
    col_y_agg: str

@tracer
def agg_col_y(
    df: pl.DataFrame,
    col_x: str, # グルーピングのキー列(bin列など)
    col_y: str = None, # 値を集約したい列(指定なければcol_xのcount)
    col_color: str = None, # 色分けで表現するもう1軸
    col_y_agg: str = None, # 集約値の列名
    agg_func = pl.mean,
    verbose: int = 0,
    traceable: bool = False,
) -> agg_col_y_trace:

    # y軸に使う値の集約列名（例: "value (mean)"）
    if col_y is None:
        print(f"集計関数に'{agg_func.__name__}'が指定されましたが、col_yが指定されていないため'count'を設定します")
        agg_func = pl.count
        if col_y_agg is None:
            col_y_agg = f'{col_x} ({agg_func.__name__})'
    else:
        if col_y_agg is None:
            col_y_agg = f'{col_y} ({agg_func.__name__})'

    # 集約キー
    group_keys = [col_x]
    
    # 集約式リスト
    if col_y is None:
        exprs = [agg_func().alias(col_y_agg)]
    else:
        # y軸値は常に集約
        exprs = [agg_func(col_y).alias(col_y_agg)]
    
    # 集約キー：カテゴリ列なら色ごとに線を分けたいので group_by に含める
    # 数値colorのとき：集約後も色分けに使いたいため、代表値として mean で保持
    if col_color:
        dtype_col_color = df.schema[col_color]
        is_col_color_categorical = col_color and dtype_col_color not in (pl.Int64, pl.Float64)
        if is_col_color_categorical:
            group_keys += [col_color]
        else:
            exprs.append(pl.col(col_color).mean().alias(col_color))  # or .first()

    df_agg = df.group_by(group_keys).agg(exprs).sort(group_keys)
    if traceable:
        trace = agg_col_y_trace(col_y_agg=col_y_agg)
        return df_agg, trace
    return df_agg


@dataclass
class agg_cols_y_trace:
    cols_y_agg: list[str]

@tracer
def agg_cols_y(
    df: pl.DataFrame,
    col_x: str, # グルーピングのキー列(bin列など)
    cols_y: list[str], # 値を集約したい列
    suffix_col_agg: str = None, # 集約値の列名
    agg_func = pl.mean,
    verbose: int = 0,
    traceable: bool = False,
) -> pl.DataFrame:

    # binとcolorごとに集約する
    
    # y軸に使う値の集約列名（例: "value (mean)"）
    if suffix_col_agg is None:
        suffix_col_agg = f' ({agg_func.__name__})'
    cols_y_agg = [f'{col_y}{suffix_col_agg}' for col_y in cols_y]

    # 集約キー
    group_keys = [col_x]

    # 集約式リスト
    exprs = [agg_func(col_y).alias(col_y_agg) for col_y, col_y_agg in zip(cols_y, cols_y_agg)]

    df_agg = df.group_by(group_keys).agg(exprs).sort(group_keys)
    
    if traceable:
        trace = agg_cols_y_trace(cols_y_agg=cols_y_agg)
        return df_agg, trace
    return df_agg
