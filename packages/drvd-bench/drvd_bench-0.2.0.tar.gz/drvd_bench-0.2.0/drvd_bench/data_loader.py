#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
drvd_bench.data_loader
======================

get_drvd_data
-------------
惰性读取 JSONL，并按照 qwen2.5vl_example.py 中的逻辑
**生成最终 prompt**（与 single / joint 类型相关）。

返回值
------
Iterator[(img_path, prompt, record)]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator, Tuple

from tqdm import tqdm

__all__ = ["get_drvd_data"]


def _build_prompt_single(record: Dict, mode: str) -> str:
    """
    构造 single 类型下的 prompt。
    - mode == 'analysis' | 'discrete'
    """
    if mode == "analysis":
        if record.get("task") == "report_generation":
            return (
                record["question"]
                + "\n\nWrite the image report as a single coherent paragraph, no more than 500 words."
            )
        else:
            return (
                "Question: "
                + record["question"]
                + "\nOptions:\n"
                + "\n".join(record.get("options", []))
                + "\n\nProvide only the letter as your answer."
            )
    else:  # discrete
        return (
            "You are participating in an educational exercise based on visual information.\n\n"
            f"Question:\n{record['question']}\nOptions:\n"
            + "\n".join(record.get("options", []))
            + "\n\nPlease answer with a single letter (A-H) only."
        )


def _build_prompt_joint(record: Dict) -> str:
    """联合推理模式直接使用数据中的 `joint_prompt` 字段。"""
    return record.get("joint_prompt", "")


def get_drvd_data(
    jsonl_path: str | Path,
    image_root: str | Path,
    *,
    data_type: str = "single",  # 'single' | 'joint'
    verbose: bool = True,
) -> Iterator[Tuple[str, str, Dict]]:
    """
    Parameters
    ----------
    jsonl_path : str | Path
        数据集 JSONL 路径。
    image_root : str | Path
        图片根目录。
    data_type : {"single", "joint"}, default "single"
        与 qwen2.5vl_example.py 中 --type 一致。
    verbose : bool, default True
        显示 tqdm 进度条。

    Yields
    ------
    (img_path, prompt, record)
        prompt 即 api_infer 所需的最终提示词。
    """
    jsonl_path = Path(jsonl_path)
    image_root = Path(image_root)

    # ---------- 判定 single 模式下的 analysis / discrete ----------
    mode = None  # 仅 single 时使用
    if data_type == "single":
        with jsonl_path.open("r", encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    first_rec = json.loads(ln)
                    mode = "analysis" if "task" in first_rec else "discrete"
                    break
        if mode is None:
            raise ValueError(f"{jsonl_path} appears empty.")

    # ---------- 主迭代 ----------
    with jsonl_path.open("r", encoding="utf-8") as f:
        iterator = tqdm(f, desc="Loading DrVD items") if verbose else f
        for ln in iterator:
            if not ln.strip():
                continue
            record = json.loads(ln)

            # 图片绝对路径
            img_rel = record.get("image_paths", "")
            img_path = image_root / img_rel

            # prompt
            if data_type == "single":
                prompt = _build_prompt_single(record, mode)
            elif data_type == "joint":
                prompt = _build_prompt_joint(record)
            else:  # pragma: no cover
                raise ValueError("data_type must be 'single' or 'joint'")

            yield str(img_path), prompt, record