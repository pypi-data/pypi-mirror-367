import os
import inspect
from functools import wraps

# tracerの有効/無効を環境変数で制御
TRACER_ENABLED = os.getenv("TRACER_MODE", "1").lower() in ("1", "true", "on")


def tracer(_func=None, *, verbose_key: str = "verbose"):
    """
    関数呼び出しのトレース（関数名の自動出力）を行うデコレータ。

    verbose の値に応じて、関数名のログを表示する。
    - 最初の関数は verbose の値そのままで出力判定される。
    - サブ関数（他の @tracer 関数から呼ばれたもの）は verbose を1減らして判定される。
    - verbose が 0 以下になるとログ出力されない。

    環境変数 `TRACER_MODE` が "0", "false", "off" のいずれかであれば、
    デコレータは無効化され、ロギングも `inspect` の使用も一切行わない。

    Parameters
    ----------
    _func : Callable | None
        デコレータの内部処理用。通常は指定不要。
    verbose_key : str, optional
        verbose 引数の名前（デフォルト: "verbose"）

    Returns
    -------
    Callable
        トレース機能付き関数 or 元の関数（無効時）

    使用例
    -------
    >>> @tracer
    ... def main_task(verbose=2):
    ...     sub_task(verbose=verbose)

    >>> @tracer
    ... def sub_task(verbose=0):
    ...     pass

    実行:
    >>> main_task(verbose=2)
    --- function: main_task ---
    --- function: sub_task ---

    環境変数:
    $ export TRACER_MODE=off  # 無効化
    $ export TRACER_MODE=on   # 有効化（デフォルト）

    注意:
    - トレースは関数チェーンの深さを意識した verbose で制御する。
    - `main_task(verbose=1)` とすれば、main_task は出力され、sub_task はされない。
    """
    def decorator(func):
        if not TRACER_ENABLED:
            # tracer無効なら何もせずそのまま返す（高速）
            return func

        @wraps(func)
        def wrapper(*args, **kwargs):
            verbose = kwargs.get(verbose_key, 0)

            # サブ関数なら verbose を減らす
            if _is_called_by_traced_func():
                verbose = max(0, verbose - 1)

            # ログ出力
            if verbose > 0:
                print(f"--- function: {func.__name__} ---")

            # 減らした verbose を関数に渡す
            kwargs[verbose_key] = verbose
            return func(*args, **kwargs)

        return wrapper

    return decorator(_func) if _func else decorator


def _is_called_by_traced_func():
    """
    呼び出し元が @tracer デコレータの関数であるかを判定する。

    Returns
    -------
    bool
        呼び出し元が tracer の wrapper 関数なら True
    """
    if not TRACER_ENABLED:
        return False

    stack = inspect.stack()
    for frame in stack[2:]:
        if frame.function == "wrapper":
            return True
    return False
