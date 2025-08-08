"""
DrVD-Bench: Benchmark Toolkit
=============================
公开四个顶级函数，方便用户直接调用::

    from drvd_bench import (
        get_drvd_data,
        map_result,
        compute_choice_metric,
        compute_report_generation_metric,
    )
"""

from importlib.metadata import version, PackageNotFoundError

from .data_loader import get_drvd_data           # noqa: F401
from .mapper import map_result                   # noqa: F401
from .choice_metric import compute_choice_metric # noqa: F401
from .report_metric import compute_report_generation_metric  # noqa: F401

__all__ = [
    "get_drvd_data",
    "map_result",
    "compute_choice_metric",
    "compute_report_generation_metric",
]

try:
    __version__ = "0.2.0"
except PackageNotFoundError:  # pip editable 模式下可能取不到
    __version__ = "0.0.0"