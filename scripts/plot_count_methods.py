"""세트당 데이터 건수 그래프 — 셈법 A(주 지표)·C 막대 + 2026 목표(세트당) 점선, 분야마다 한 장 → docs/fig/.
B 는 보고서 본문에만(사용자 10-15) — 그래프에 안 넣는다. 이름 = 10-15 바꿈(A 레시피 1 + 측정·분석 · C 트리플).
태양전지 = ChemDX 2026 실데이터(count_methods.py) · 석유화학촉매 = registry 레시피 1세트 추산(lab_estimate.py — 실데이터 전).

사용: python3 -I scripts/plot_count_methods.py reports/count-methods-<빌드>.json reports/lab-estimate-registry-v<판>.json
"""
import json, pathlib, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

plt.rcParams.update({"font.family": "Apple SD Gothic Neo", "axes.unicode_minus": False})   # ponytail: 맥 글꼴 — 다른 OS 면 이름만 바꿈
OUT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "fig"
COLOR = {"A": "#2f3d8f", "C": "#8a93b8", "plan": "#b5651d"}
TICKS = ["A 레시피 1\n+ 측정·분석", "C 지식그래프\n트리플"]


def num(v):
    return f"{v:,.0f}" if v >= 100 else f"{v:.1f}".rstrip("0").rstrip(".")


def plot(path, title, plan, a, c, a_rep=None):
    """a_rep = 같은 자리를 반복 측정했을 때의 A(빗금으로 덧댐)."""
    fig, ax = plt.subplots(figsize=(4.6, 4.4), dpi=200)
    ax.bar(range(2), [a, c], width=0.55, color=[COLOR["A"], COLOR["C"]])
    ax.axhline(plan, ls="--", lw=1.5, color=COLOR["plan"], label=f"2026 목표 (세트당 {num(plan)}건)")
    if a_rep:
        ax.bar(0, a_rep - a, bottom=a, width=0.55, color="none", edgecolor=COLOR["A"], hatch="///", lw=0.8,
               label=f"같은 자리 반복 측정 시 (A {num(a_rep)})")
    for x, v, label in [(0, a, f"{num(a)}~{num(a_rep)}" if a_rep else num(a)), (1, c, num(c))]:
        ax.text(x, v / 1.1, label, ha="center", va="top", fontsize=10, fontweight="bold", color="white")   # 막대 안 — 점선과 안 겹치게
    ax.legend(loc="upper right", fontsize=8.5, frameon=False)
    ax.set_yscale("log")
    ax.set_ylim(1, 8000)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_ylabel("세트당 데이터 건수 (로그 눈금)")
    ax.set_xticks(range(2), TICKS, fontsize=9)
    ax.set_title(title, fontsize=11, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main(chemdx, lab):
    real, est = json.loads(pathlib.Path(chemdx).read_text()), json.loads(pathlib.Path(lab).read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    plot(OUT / "count-methods-solar.png", f"태양전지 — ChemDX 2026 실데이터 {real['sets']}세트",
         est["태양전지"]["plan_per_set"], real["A"], real["C"])
    pcc = est["석유화학촉매"]["recipes"]["PCC-RCP-01"]
    plot(OUT / "count-methods-catalyst.png", "석유화학촉매 — registry 레시피 1세트 추산",
         est["석유화학촉매"]["plan_per_set"], pcc["A"], pcc["C"], pcc["A2"])


if __name__ == "__main__":
    main(*sys.argv[1:3])
