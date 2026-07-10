import io
from datetime import date
 
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
 
def save_chart_to_bytes(fig):
    """Save a matplotlib figure to an in-memory PNG buffer (no temp files)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return buf
 
def _build_stats_table(stats: dict, styles):
    """
    Turn a stats dict into a ReportLab Table.
    Accepts either:
      - flat form:      {"mean": 1.2, "std": 0.3, "25%": 1.0, "50%": 1.2, "75%": 1.5}
      - per-column form: {"revenue": {"mean": 1.2, "std": 0.3, ...}, "units": {...}}
    """
    if not stats:
        return Paragraph("No summary statistics provided.", styles["Normal"])
 
    # Detect per-column (nested dict) vs flat form
    is_nested = all(isinstance(v, dict) for v in stats.values())
 
    if is_nested:
        # Collect the union of stat names across columns, preserving order
        stat_names = []
        for col_stats in stats.values():
            for k in col_stats.keys():
                if k not in stat_names:
                    stat_names.append(k)
 
        header = ["Metric"] + list(stats.keys())
        rows = [header]
        for stat_name in stat_names:
            row = [stat_name]
            for col in stats.keys():
                val = stats[col].get(stat_name, "")
                row.append(_fmt(val))
            rows.append(row)
    else:
        header = ["Metric", "Value"]
        rows = [header] + [[k, _fmt(v)] for k, v in stats.items()]
 
    table = Table(rows, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E3A59")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F4F8")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table
 
 
def _fmt(val):
    if isinstance(val, float):
        return f"{val:,.2f}"
    return str(val)
 
 
def generate_report(df, charts, output_path, title="Data Report", stats=None):
    """
    Build a PDF report.
 
    Args:
        df: pandas DataFrame with the underlying data. If `stats` is not
            supplied, summary stats are computed from df.describe().
        charts: list of matplotlib Figure objects to embed, in order.
        output_path: path to write the PDF to, e.g. "output/report.pdf".
        title: report title text.
        stats: optional dict of aggregated stats (e.g. from P2's SQL
            queries) to use instead of/alongside df.describe(). Accepts
            flat {"mean": ..., "std": ...} or nested per-column form.
 
    Returns:
        output_path (str)
    """
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
 
    story = []
 
    # --- Title + date ---
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(date.today().strftime("%B %d, %Y"), styles["Normal"]))
    story.append(Spacer(1, 16))
 
    # --- Summary stats table ---
    story.append(Paragraph("Summary Statistics", styles["Heading2"]))
    story.append(Spacer(1, 6))
 
    if stats is None and df is not None:
        stats = df.describe().to_dict()
 
    story.append(_build_stats_table(stats, styles))
    story.append(Spacer(1, 20))
 
    # --- Charts ---
    if charts:
        story.append(Paragraph("Charts", styles["Heading2"]))
        story.append(Spacer(1, 6))
        for fig in charts:
            buf = save_chart_to_bytes(fig)
            img = Image(buf, width=6 * inch, height=3.5 * inch)
            story.append(img)
            story.append(Spacer(1, 14))
 
    doc.build(story)
    return output_path
 
 
if __name__ == "__main__":
    # Quick smoke test: run `python src/reporter.py` to generate a sample PDF
    import pandas as pd
    import matplotlib
 
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import os
 
    df = pd.DataFrame(
        {
            "revenue": [120, 135, 98, 150, 175, 160, 140],
            "units": [10, 12, 8, 14, 16, 15, 13],
        }
    )
 
    fig1, ax1 = plt.subplots()
    ax1.plot(df["revenue"], marker="o")
    ax1.set_title("Revenue Trend")
 
    fig2, ax2 = plt.subplots()
    ax2.bar(range(len(df["units"])), df["units"])
    ax2.set_title("Units Sold")
 
    os.makedirs("output", exist_ok=True)
    out = generate_report(
        df,
        charts=[fig1, fig2],
        output_path="output/sample_report.pdf",
        title="Weekly Sales Report",
    )
    print(f"Report written to {out}")
 