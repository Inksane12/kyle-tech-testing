#!/usr/bin/env python3
"""Regenerate public static charts directly from the preserved telemetry CSVs.

Requires matplotlib only when regenerating the PNGs. The hosted site itself has
no Python or third-party runtime dependency.
"""
from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSET = ROOT / "assets"
CAPTURES = {
    "Idle baseline": ROOT / "data" / "idle.csv",
    "Mixed ComfyUI trial": ROOT / "data" / "mixed-comfyui.csv",
}
COLORS = {"Idle baseline": "#9cb0c2", "Mixed ComfyUI trial": "#66baff"}
BG = "#0b1119"
PANEL = "#101923"
GRID = "#2d3d4d"
TEXT = "#dce7f0"
MUTED = "#a6b6c5"
METRICS = {
    "temperature_c": ("GPU temperature", "°C", (20, 70), 10),
    "utilization_pct": ("GPU utilization", "%", (0, 100), 20),
    "memory_used_mib": ("VRAM used", "MiB", (0, 12_000), 2_000),
    "power_w": ("GPU-reported power", "W", (0, 200), 40),
}
COMPARISON_MAX = {
    "temperature_c": 70,
    "utilization_pct": 40,
    "memory_used_mib": 9_000,
    "power_w": 70,
}


def load_capture(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 59:
        raise ValueError(f"{path.name}: expected 59 source samples, found {len(rows)}")
    return rows


def style_axis(ax: plt.Axes, *, mobile: bool) -> None:
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=11 if mobile else 10, length=0, pad=7)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.9)
    ax.set_axisbelow(True)


def timestamp_seconds(rows: list[dict[str, str]]) -> list[float]:
    times = [datetime.fromisoformat(row["timestamp_utc"].replace("Z", "+00:00")) for row in rows]
    start = times[0]
    return [(stamp - start).total_seconds() for stamp in times]


def draw_comparison(*, mobile: bool) -> None:
    names = list(CAPTURES)
    rows_by_name = {name: load_capture(path) for name, path in CAPTURES.items()}
    if mobile:
        fig, axes = plt.subplots(4, 1, figsize=(8, 19), constrained_layout=True)
    else:
        fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
        axes = axes.ravel()
    fig.patch.set_facecolor(BG)
    fig.suptitle("GPU TELEMETRY  /  FULL-CAPTURE MEANS", color=TEXT,
                 fontsize=22 if mobile else 25, fontweight="bold", x=0.04, ha="left")
    for ax, (metric, (title, unit, _limits, _step)) in zip(axes, METRICS.items()):
        style_axis(ax, mobile=mobile)
        mean_values = [float(sum(Decimal(row[metric]) for row in rows_by_name[name]) / Decimal(59)) for name in names]
        bars = ax.bar(names, mean_values, color=[COLORS[name] for name in names], width=0.55,
                      edgecolor="none", zorder=3)
        ax.set_title(title, loc="left", color=TEXT, fontsize=17 if mobile else 15, fontweight="bold", pad=14)
        ax.set_ylabel(unit, color=MUTED, fontsize=12 if mobile else 10, labelpad=9)
        ax.set_ylim(0, COMPARISON_MAX[metric])
        ax.set_yticks(np.linspace(0, COMPARISON_MAX[metric], 5))
        ax.set_xticks(range(len(names)), ["Idle baseline", "Mixed trial\n(includes idle)"] if mobile else ["Idle baseline", "Mixed trial (includes idle)"])
        ax.tick_params(axis="x", colors=TEXT, labelsize=11 if mobile else 9, pad=9)
        for bar, value in zip(bars, mean_values):
            label = f"{value:,.2f}"
            ax.annotate(label, (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 6), textcoords="offset points", ha="center", va="bottom",
                        color=TEXT, fontsize=12 if mobile else 10, fontweight="bold")
    target = ASSET / ("capture-means-mobile.png" if mobile else "capture-means.png")
    fig.savefig(target, dpi=180, facecolor=BG, bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)


def draw_metric(metric: str, *, mobile: bool) -> None:
    title, unit, limits, step = METRICS[metric]
    if mobile:
        fig, ax = plt.subplots(figsize=(8, 7.5), constrained_layout=True)
    else:
        fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    fig.patch.set_facecolor(BG)
    style_axis(ax, mobile=mobile)
    for name, path in CAPTURES.items():
        rows = load_capture(path)
        ax.plot(timestamp_seconds(rows), [float(row[metric]) for row in rows],
                color=COLORS[name], linewidth=2.4 if mobile else 2.1, marker="o",
                markersize=2.8 if mobile else 2.1, label=name, zorder=3)
    ax.set_title(f"{title}  /  {unit}", loc="left", color=TEXT, fontsize=17 if mobile else 15,
                 fontweight="bold", pad=14)
    ax.set_xlabel("Elapsed time from capture start (seconds)", color=MUTED, fontsize=12 if mobile else 10, labelpad=10)
    ax.set_ylabel(unit, color=MUTED, fontsize=12 if mobile else 10, labelpad=9)
    ax.set_ylim(limits)
    ax.set_yticks(np.arange(limits[0], limits[1] + step, step))
    ax.set_xlim(left=0)
    ax.legend(frameon=False, labelcolor=TEXT, fontsize=11 if mobile else 10, loc="upper left")
    suffix = "-mobile" if mobile else ""
    fig.savefig(ASSET / f"{metric_to_name(metric)}{suffix}.png", dpi=180, facecolor=BG, bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)


def metric_to_name(metric: str) -> str:
    return {
        "temperature_c": "temperature",
        "utilization_pct": "utilization",
        "memory_used_mib": "vram",
        "power_w": "power",
    }[metric]


def main() -> None:
    draw_comparison(mobile=False)
    draw_comparison(mobile=True)
    for metric in METRICS:
        draw_metric(metric, mobile=False)
        draw_metric(metric, mobile=True)
    print("Generated dark, CSV-derived desktop and mobile charts from 118 preserved telemetry samples.")


if __name__ == "__main__":
    main()
