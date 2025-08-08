#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_choice_metric
---------------------
单/多级选择题指标。
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Literal

__all__ = ["compute_choice_metric"]


def _single(jsonl_path: Path):
    stats = defaultdict(lambda: defaultdict(lambda: {"correct": 0, "total": 0}))
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            modality = data.get("modality")
            task = data.get("task") if "task" in data else data.get("level")
            answer = data.get("answer", "")
            resp = data.get("model_response")
            correct_option = answer.split(".")[0].strip()
            stats[modality][task]["total"] += 1
            if resp == correct_option:
                stats[modality][task]["correct"] += 1

    for modality, tasks in stats.items():
        print(f"Modality: {modality}")
        for task, cnt in tasks.items():
            total = cnt["total"]
            correct = cnt["correct"]
            acc = correct / total if total else 0
            print(f"  {task}: {acc:.2%} ({correct}/{total})")
        print()


def _joint(jsonl_path: Path):
    levels = ["modality", "organ", "lesion", "diagnosis"]
    metrics = defaultdict(lambda: defaultdict(lambda: {"total": 0, "correct": 0}))

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            mod = d.get("modality", "Unknown")
            tokens = d.get("model_response", "").split(",") if isinstance(d.get("model_response"), str) else []

            for idx, lv in enumerate(levels):
                metrics[mod][lv]["total"] += 1
                ans_field = d.get(f"{lv}_answer", "")
                correct = ans_field[0] if ans_field else ""
                if idx < len(tokens) and tokens[idx] == correct:
                    metrics[mod][lv]["correct"] += 1

    print("\n✅ Hierarchical Accuracy Report by Modality:")
    for mod, lv_stats in metrics.items():
        print(f"\nModality: {mod}")
        for lv in levels:
            tot = lv_stats[lv]["total"]
            corr = lv_stats[lv]["correct"]
            acc = corr / tot if tot else 0
            print(f"  {lv:>12}: {acc:.2%} ({corr}/{tot})")


def compute_choice_metric(
    jsonl_path: str | Path,
    mode: Literal["single", "joint"] = "single",
):
    """
    计算选择题指标。

    Parameters
    ----------
    jsonl_path : str | Path
        结果 JSONL。
    mode : {"single", "joint"}, default "single"
        - "single": 独立任务
        - "joint": 逐级联合推理
    """
    jsonl_path = Path(jsonl_path)
    if mode == "single":
        _single(jsonl_path)
    elif mode == "joint":
        _joint(jsonl_path)
    else:
        raise ValueError("data_type must be 'single' or 'joint'")