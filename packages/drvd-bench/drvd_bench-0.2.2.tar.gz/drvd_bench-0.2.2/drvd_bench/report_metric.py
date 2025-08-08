#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_report_generation_metric
--------------------------------
复用原 `report_generation_metric.py`，封装为函数。
"""

from __future__ import annotations

import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple

from bert_score import score as bert_score
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from openai import OpenAI
from tqdm import tqdm

__all__ = ["compute_report_generation_metric"]


def _extract_key_info_factory(client: OpenAI, cache: Dict[str, str]):
    """
    闭包：返回一个 `extract_key_info(text)->str`，带缓存 & client。
    """

    def _fn(text: str) -> str:
        if text in cache:
            return cache[text]
        prompt = (
            "Given the following description of a medical image, extract only clinically "
            "relevant information that can be visually determined from the image. "
            "This includes both normal findings and abnormal findings.\n\n"
            f"{text}\n\n"
            "Return a concise, comma-separated list of visually identifiable features."
        )
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = resp.choices[0].message.content.strip()
        cache[text] = content
        return content

    return _fn


def _parallel_extract(
    rows: List[Tuple[str, str, str]],
    extract_fn,
    max_workers: int = 50,
) -> List[Tuple[str, str]]:
    out = [("", "")] * len(rows)
    future2idxkind = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for idx, (_, ref, _) in enumerate(rows):
            future2idxkind[pool.submit(extract_fn, ref)] = (idx, "ref")
        for idx, (_, _, pred) in enumerate(rows):
            future2idxkind[pool.submit(extract_fn, pred)] = (idx, "pred")

        for fut in tqdm(as_completed(future2idxkind), total=len(future2idxkind)):
            idx, kind = future2idxkind[fut]
            try:
                result = fut.result()
            except Exception:
                result = "ERROR"
            if kind == "ref":
                out[idx] = (result, out[idx][1])
            else:
                out[idx] = (out[idx][0], result)
    return out


def compute_report_generation_metric(
    api_key: str,
    json_path: str | Path,
    *,
    base_url: str = "https://api.deepseek.com",
):
    """
    Parameters
    ----------
    api_key : str
        DeepSeek API Key。
    json_path : str | Path
        含`answer` 和 `model_response` 字段的 JSONL。
    base_url : str, default "https://api.deepseek.com"
        镜像地址 / 私有部署地址。
    """
    client = OpenAI(api_key=api_key.strip(), base_url=base_url)
    cache: Dict[str, str] = {}
    extract_key_info = _extract_key_info_factory(client, cache)

    json_path = Path(json_path)
    caption_rows: List[Tuple[str, str, str]] = []
    with json_path.open("r", encoding="utf-8") as f:
        for ln in f:
            item = json.loads(ln)
            ref = item.get("answer")
            pred = item.get("model_response")
            modality = item.get("modality", "Unknown")
            if ref and pred:
                caption_rows.append((modality, ref, pred))

    # 提取关键词
    extracted = _parallel_extract(caption_rows, extract_key_info)

    # 汇总
    refs_by_mod, preds_by_mod = defaultdict(list), defaultdict(list)
    for (modality, _, _), (ref_kw, pred_kw) in zip(caption_rows, extracted):
        if "ERROR" not in (ref_kw, pred_kw):
            refs_by_mod[modality].append(ref_kw)
            preds_by_mod[modality].append(pred_kw)

    smoothie = SmoothingFunction().method4
    for modality in tqdm(refs_by_mod.keys(), desc="Scoring"):
        refs, preds = refs_by_mod[modality], preds_by_mod[modality]

        _, _, F1 = bert_score(
            preds,
            refs,
            model_type="microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract",
            num_layers=12,
            lang="en",
            rescale_with_baseline=False,
            device="cpu",
        )
        bert_f1 = F1.mean().item()

        bleu_vals = [
            sentence_bleu([r.split()], p.split(), smoothing_function=smoothie)
            for r, p in zip(refs, preds)
        ]
        bleu = sum(bleu_vals) / len(bleu_vals) if bleu_vals else 0.0

        print(f"{modality}: BERTScore F1 = {bert_f1:.4f}, BLEU = {bleu:.4f}")