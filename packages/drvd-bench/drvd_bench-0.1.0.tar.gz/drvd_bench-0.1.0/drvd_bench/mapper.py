#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
drvd_bench.mapper
=================

map_result
----------
根据 DeepSeek Chat API 将结果映射为选项字母。

用法示例::
    from drvd_bench.mapper import map_result
    map_result(
        api_key="sk-...",
        input_path="predictions.jsonl",
        output_path="mapped.jsonl",
    )
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Mapping

from openai import OpenAI
from tqdm import tqdm

__all__ = ["map_result"]


def _map_answer_to_option(
    client: OpenAI,
    question: str,
    options: List[str],
    original_answer: str,
) -> str | None:
    """向 DeepSeek 请求，把自由回答映射为 ABCD 字母。"""
    opt_text = "\n".join(options)
    prompt = (
        "You are a medical assistant. Given the question, the list of options, and a "
        "response from another model, map the response to the best matching option "
        "letter (A, B, C, or D). Only output the letter.\n\n"
        f"Question: {question}\n\nOptions:\n{opt_text}\n\n"
        f"Other model's answer: {original_answer}\n\n"
        "Instruction: Only output the single letter. Do not add any other text."
    )

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=False,
        )
        return resp.choices[0].message.content.strip().upper()
    except Exception as e:  # pragma: no cover
        print(f"❗ DeepSeek request failed: {e}")
        return None


def _load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _save_jsonl(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")


def map_result(
    api_key: str,
    input_path: str | Path,
    output_path: str | Path,
    *,
    base_url: str = "https://api.deepseek.com",
    show_preview: int = 5,
):
    """
    Parameters
    ----------
    api_key : str
        DeepSeek API key（必填）。
    input_path : str | Path
        待映射的 JSONL 路径；需包含 ``question``、``options``、``model_response`` 等字段。
    output_path : str | Path
        保存映射后 JSONL 的路径。
    base_url : str, default "https://api.deepseek.com"
        如有私有部署可自定义。
    show_preview : int, default 5
        调试：映射完成后在终端打印前 N 条样例。

    Returns
    -------
    None
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    # 读取数据
    dataset = _load_jsonl(input_path)

    client = OpenAI(api_key=api_key, base_url=base_url)

    mapped_results: List[Mapping] = []
    total, failed, preview_cnt = 0, 0, 0

    for sample in tqdm(dataset, desc="Processing and Mapping"):
        task = sample.get("task", "")
        # 自由描述题（caption）直接跳过
        if task == "caption":
            mapped_results.append(sample)
            continue

        options = sample.get("options", [])
        raw_answer = sample.get("model_response", "").strip()

        pred_letter = _map_answer_to_option(
            client,
            sample.get("question", ""),
            options,
            raw_answer,
        )

        letter2opt = {opt[0]: opt for opt in options if opt}
        if pred_letter in letter2opt:
            sample["model_response"] = letter2opt[pred_letter]
        else:
            sample["model_response"] = None
            failed += 1

        total += 1
        if preview_cnt < show_preview:
            print(sample)
            preview_cnt += 1

        mapped_results.append(sample)

    # 保存
    _save_jsonl(output_path, mapped_results)

    # 统计信息
    print(f"\n✅ Mapping complete. Processed {total} samples.")
    print(f"❌ Failed to map (no matching option): {failed}")
    if total:
        print(f"✅ Success rate: {round((total - failed) / total * 100, 2)}%")
    print(f"\n📁 Saved to: {output_path.resolve()}")