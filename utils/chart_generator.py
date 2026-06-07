import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

COLORS = {
    "reactions": "#0077B5",
    "comments":  "#00A0DC",
    "views":     "#5AB4D6",
    "shares":    "#004182",
}


def generate_analytics_chart(posts: list) -> bytes:
    """
    posts = [{"label": str, "reactions": int, "comments": int,
              "views": int, "shares": int, "tracked_at": str}, ...]
    Returns PNG bytes.
    """
    if not posts:
        raise ValueError("No data to chart")

    labels = [p["label"][:30] + "…" if len(p["label"]) > 30 else p["label"] for p in posts]
    reactions = [p.get("reactions", 0) for p in posts]
    comments  = [p.get("comments", 0) for p in posts]
    views     = [p.get("views", 0) for p in posts]
    shares    = [p.get("shares", 0) for p in posts]
    has_views = any(v > 0 for v in views)

    n = len(posts)
    fig_h = max(5, 3 + n * 0.8)
    fig, axes = plt.subplots(1, 2 if has_views else 1, figsize=(13 if has_views else 8, fig_h))
    if not has_views:
        axes = [axes]

    fig.patch.set_facecolor("#0F1117")
    for ax in axes:
        ax.set_facecolor("#1C1E26")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#3A3D4A")
        ax.spines["bottom"].set_color("#3A3D4A")
        ax.tick_params(colors="#C8CAD0")
        ax.yaxis.label.set_color("#C8CAD0")
        ax.title.set_color("#F0F2F5")

    y = np.arange(n)
    bar_h = 0.28

    # Left chart: reactions + comments + shares
    ax1 = axes[0]
    if n > 1:
        ax1.barh(y + bar_h, reactions, bar_h, label="Reactions", color=COLORS["reactions"])
        ax1.barh(y,         comments,  bar_h, label="Comments",  color=COLORS["comments"])
        ax1.barh(y - bar_h, shares,    bar_h, label="Shares",    color=COLORS["shares"])
        ax1.set_yticks(y)
        ax1.set_yticklabels(labels, fontsize=9)
    else:
        metrics = ["Reactions", "Comments", "Shares"]
        values  = [reactions[0], comments[0], shares[0]]
        colors  = [COLORS["reactions"], COLORS["comments"], COLORS["shares"]]
        bars = ax1.barh(metrics, values, color=colors, height=0.5)
        for bar, val in zip(bars, values):
            ax1.text(bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height() / 2,
                     str(val), va="center", color="#F0F2F5", fontsize=11, fontweight="bold")

    ax1.set_title("Engagement", fontsize=13, fontweight="bold", pad=12)
    ax1.set_xlabel("Count", fontsize=9)
    if n > 1:
        ax1.legend(loc="lower right", facecolor="#1C1E26", labelcolor="#C8CAD0", edgecolor="#3A3D4A", fontsize=8)

    # Right chart: views
    if has_views:
        ax2 = axes[1]
        bar_color = "#5AB4D6"
        if n > 1:
            ax2.barh(y, views, 0.5, color=bar_color)
            ax2.set_yticks(y)
            ax2.set_yticklabels(labels, fontsize=9)
        else:
            b = ax2.barh(["Views"], [views[0]], color=bar_color, height=0.5)
            ax2.text(b[0].get_width() + views[0] * 0.02, b[0].get_y() + b[0].get_height() / 2,
                     str(views[0]), va="center", color="#F0F2F5", fontsize=11, fontweight="bold")
        ax2.set_title("Impressions / Views", fontsize=13, fontweight="bold", pad=12)
        ax2.set_xlabel("Count", fontsize=9)

    fig.suptitle("LinkedIn Post Analytics — Laura", fontsize=15, fontweight="bold",
                 color="#F0F2F5", y=1.02)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()
