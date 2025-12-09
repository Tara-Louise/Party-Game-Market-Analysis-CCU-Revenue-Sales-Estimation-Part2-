"""
party_games_analysis.py

End-to-end pipeline for:
- Loading Steam CCU and review-based sales data
- Estimating monthly unit sales from positive reviews (×30)
- Estimating lifetime revenue per game using 50% of Steam list price
- Generating interactive Plotly charts:
    1) Monthly Peak CCU by Game
    2) Monthly Estimated Sales by Game
    3) Estimated Lifetime Revenue by Game (bar chart)
- Generating a simple 4-up HTML dashboard layout
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------------------------------------------
# 0. CONFIGURATION
# --------------------------------------------------------------------------------------

# Input data paths (adjust these to match your repo layout)
CCU_CSV = "CCU_V10(CCU_All_Games).csv"        # monthly CCU data
SALES_CSV = "Chart2_Master.csv"              # monthly review / est_sales_x30 data

# Output directory
OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

# Steam prices (current store price, not realised)
STEAM_PRICES_GBP = {
    "Human Fall Flat": 15.99,
    "Overcooked AYCE": 29.99,
    "Overcooked 2": 4.99,
    "Gang Beasts": 6.39,
    "Pummel Party": 12.79,
    "Overcooked": 12.99,
    "Rubber Bandits": 1.59,
    "PHOGS!": 22.49,
    "Cake Bash": 2.32,
}

# Proportion of list price used to estimate realised ASP (industry rule-of-thumb)
REALISATION_RATE = 0.5

# --------------------------------------------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------------------------------------------

def load_data(ccu_path: str = CCU_CSV, sales_path: str = SALES_CSV):
    """Load CCU and sales CSVs into DataFrames."""
    ccu = pd.read_csv(ccu_path)
    sales = pd.read_csv(sales_path)

    # Build a date column from year + month if present
    for df in (ccu, sales):
        if {"year", "month"}.issubset(df.columns):
            df["date"] = pd.to_datetime(
                df["year"].astype(int).astype(str)
                + "-"
                + df["month"].astype(int).astype(str)
                + "-01"
            )

    return ccu, sales


# --------------------------------------------------------------------------------------
# 2. PREPARE DATA (REMOVE OUTLIERS, AGGREGATE)
# --------------------------------------------------------------------------------------

def prepare_data(ccu: pd.DataFrame, sales: pd.DataFrame):
    """
    Prepare CCU and sales datasets:
    - Exclude Fall Guys (and optionally other big outliers)
    - Ensure we have est_sales_x30 column in sales
    """
    # Normalise game column name if needed
    if "game" not in ccu.columns and "Game" in ccu.columns:
        ccu = ccu.rename(columns={"Game": "game"})
    if "game" not in sales.columns and "Game" in sales.columns:
        sales = sales.rename(columns={"Game": "game"})

    # Exclude Fall Guys from time-series charts to keep scale readable
    ccu_no_fg = ccu[ccu["game"] != "Fall Guys (Paid Era)"].copy()
    sales_no_fg = sales[sales["game"] != "Fall Guys (Paid Era)"].copy()

    # Ensure we have an estimated sales column (positive reviews × 30)
    if "est_sales_x30" not in sales_no_fg.columns:
        if "positive_reviews" in sales_no_fg.columns:
            sales_no_fg["est_sales_x30"] = sales_no_fg["positive_reviews"] * 30
        else:
            raise ValueError("Sales data needs 'est_sales_x30' or 'positive_reviews' column.")

    return ccu_no_fg, sales_no_fg


# --------------------------------------------------------------------------------------
# 3. LIFETIME UNITS & REVENUE SUMMARY
# --------------------------------------------------------------------------------------

def build_revenue_summary(sales_no_fg: pd.DataFrame) -> pd.DataFrame:
    """
    Build a per-game summary of lifetime units & revenue.

    - Estimated units: sum(est_sales_x30)
    - Price: from STEAM_PRICES_GBP
    - Realised ASP: price * REALISATION_RATE
    - Revenue: units * realised ASP
    """
    lifetime_units = (
        sales_no_fg.groupby("game")["est_sales_x30"]
        .sum()
        .sort_values(ascending=False)
    )

    price_series = pd.Series(STEAM_PRICES_GBP)

    summary = (
        pd.DataFrame({
            "game": lifetime_units.index,
            "estimated_units": lifetime_units.values,
        })
        .assign(
            price_gbp=lambda d: d["game"].map(price_series),
        )
    )

    # Filter out any games not in the price dict
    summary = summary[~summary["price_gbp"].isna()].copy()

    summary["realised_price_gbp"] = summary["price_gbp"] * REALISATION_RATE
    summary["revenue_gbp"] = summary["estimated_units"] * summary["realised_price_gbp"]
    summary["revenue_m_gbp"] = summary["revenue_gbp"] / 1e6
    summary["units_k"] = summary["estimated_units"] / 1e3

    # Save CSV version for transparency
    summary.to_csv(OUT_DIR / "Chart3_Summary_Units_Revenue.csv", index=False)

    return summary


# --------------------------------------------------------------------------------------
# 4. STYLING HELPER
# --------------------------------------------------------------------------------------

def style_black_theme(fig):
    """Apply a consistent black/‘neon’ theme to a Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
    )
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor="white",
        mirror=True,
        gridcolor="#333333",
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor="white",
        mirror=True,
        gridcolor="#333333",
    )
    return fig


# --------------------------------------------------------------------------------------
# 5. CHART 1 – MONTHLY PEAK CCU
# --------------------------------------------------------------------------------------

def make_ccu_chart(ccu_no_fg: pd.DataFrame):
    """Create an interactive CCU-over-time line chart."""
    fig = px.line(
        ccu_no_fg,
        x="date",
        y="peak_ccu",
        color="game",
        title="Monthly Peak CCU by Game (Fall Guys excluded)",
    )

    fig.update_traces(mode="lines", line=dict(width=2))
    fig = style_black_theme(fig)
    fig.update_xaxes(title="Month")
    fig.update_yaxes(title="Peak CCU")
    fig.update_layout(legend_title_text="Game", margin=dict(l=40, r=40, t=80, b=40))

    # Optional: annotate Human Fall Flat peak if present
    if "Human Fall Flat" in ccu_no_fg["game"].unique():
        hff_rows = ccu_no_fg[ccu_no_fg["game"] == "Human Fall Flat"]
        hff_peak = hff_rows["peak_ccu"].max()
        peak_row = hff_rows.loc[hff_rows["peak_ccu"].idxmax()]
        fig.add_annotation(
            x=peak_row["date"],
            y=hff_peak,
            text=f"Human Fall Flat peak ≈ {int(hff_peak):,} CCU",
            showarrow=True,
            arrowhead=2,
            ay=-40,
            font=dict(color="white", size=11),
            bgcolor="rgba(0,0,0,0.6)",
        )

    out_path = OUT_DIR / "CCU_Interactive_NoFG.html"
    fig.write_html(out_path)
    return fig, out_path


# --------------------------------------------------------------------------------------
# 6. CHART 2 – MONTHLY ESTIMATED SALES
# --------------------------------------------------------------------------------------

def make_sales_chart(sales_no_fg: pd.DataFrame):
    """Create an interactive estimated-monthly-sales chart."""
    fig = px.line(
        sales_no_fg,
        x="date",
        y="est_sales_x30",
        color="game",
        title="Monthly Estimated Sales by Game (Positive Reviews × 30, Fall Guys excluded)",
    )

    fig.update_traces(mode="lines", line=dict(width=2))
    fig = style_black_theme(fig)
    fig.update_xaxes(title="Month")
    fig.update_yaxes(title="Estimated Monthly Sales (units)")
    fig.update_layout(legend_title_text="Game", margin=dict(l=40, r=40, t=80, b=40))

    # Optional: annotate peak month for each game
    for game, df_g in sales_no_fg.groupby("game"):
        peak_row = df_g.loc[df_g["est_sales_x30"].idxmax()]
        fig.add_annotation(
            x=peak_row["date"],
            y=peak_row["est_sales_x30"],
            text=f"{int(peak_row['est_sales_x30']):,}",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            font=dict(color="white", size=9),
            bgcolor="rgba(0,0,0,0.6)",
        )

    out_path = OUT_DIR / "Chart2_Interactive_NoFG_Sales.html"
    fig.write_html(out_path)
    return fig, out_path


# --------------------------------------------------------------------------------------
# 7. CHART 3 – LIFETIME REVENUE BAR CHART
# --------------------------------------------------------------------------------------

def make_revenue_bar_chart(summary: pd.DataFrame):
    """Create an interactive lifetime revenue bar chart."""
    summary_sorted = summary.sort_values("revenue_gbp", ascending=False)

    fig = px.bar(
        summary_sorted,
        x="game",
        y="revenue_m_gbp",
        title=(
            "Estimated Lifetime Steam Revenue by Game\n"
            "(Positive Reviews × 30; revenue uses 50% of current Steam store price)"
        ),
    )
    fig.update_traces(
        marker_color="#636EFA",
        marker_line_color="white",
        marker_line_width=1.2,
        text=[
            f"{row['units_k']:.0f}k units\n£{row['revenue_m_gbp']:.1f}m"
            for _, row in summary_sorted.iterrows()
        ],
        textposition="outside",
    )
    fig = style_black_theme(fig)
    fig.update_xaxes(title="Game")
    fig.update_yaxes(title="Estimated Lifetime Revenue (£ millions)")
    fig.update_layout(margin=dict(l=40, r=40, t=90, b=80))

    out_path = OUT_DIR / "Chart3_Total_Revenue_Interactive.html"
    fig.write_html(out_path)
    return fig, out_path


# --------------------------------------------------------------------------------------
# 8. SALES/REVENUE TABLE (CHART 4)
# --------------------------------------------------------------------------------------

def make_sales_revenue_table(summary: pd.DataFrame):
    """Create a table view of units/revenue/price per game."""
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "Game",
                        "Est. Units (k)",
                        "Price used (£)",
                        "Realised price (50%)",
                        "Est. Revenue (£m)",
                    ],
                    fill_color="black",
                    line_color="white",
                    font=dict(color="white", size=13),
                    align="left",
                ),
                cells=dict(
                    values=[
                        summary["game"],
                        summary["units_k"].round(1),
                        summary["price_gbp"].round(2),
                        summary["realised_price_gbp"].round(2),
                        summary["revenue_m_gbp"].round(1),
                    ],
                    fill_color="black",
                    line_color="#555555",
                    font=dict(color="white", size=12),
                    align="left",
                ),
            )
        ]
    )

    fig.update_layout(
        title=(
            "Estimated Lifetime Sales & Revenue by Game\n"
            "(Positive Reviews × 30, 50% of current Steam price)"
        ),
        plot_bgcolor="black",
        paper_bgcolor="black",
        margin=dict(l=20, r=20, t=70, b=20),
    )

    out_path = OUT_DIR / "Chart1_Sales_Revenue_Table.html"
    fig.write_html(out_path)
    return fig, out_path


# --------------------------------------------------------------------------------------
# 9. 4-UP DASHBOARD WRAPPER
# --------------------------------------------------------------------------------------

def make_four_up_dashboard(
    table_file: Path,
    sales_file: Path,
    ccu_file: Path,
    revenue_file: Path,
):
    """
    Create a static HTML wrapper that arranges the four charts in a 2×2 grid
    using iframes. All files must live in the same directory.
    """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Party Game – Market Analysis Dashboard</title>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: #000000;
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      height: 100%;
      width: 100%;
    }}
    .dashboard {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 20px;
      padding: 16px;
      box-sizing: border-box;
      height: 100vh;
    }}
    .panel {{
      position: relative;
      display: flex;
      flex-direction: column;
      background: #05070a;
      border: 2px solid #39ff14;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 0 16px rgba(57,255,20,0.25);
    }}
    .panel-title {{
      padding: 6px 12px;
      font-size: 14px;
      font-weight: 600;
      border-bottom: 1px solid #39ff14;
      background: linear-gradient(to right, #05070a, #111827);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    iframe {{
      flex: 1;
      width: 100%;
      border: none;
    }}
  </style>
</head>
<body>
  <div class="dashboard">

    <div class="panel">
      <div class="panel-title">Lifetime Sales & Revenue Table</div>
      <iframe src="{table_file.name}"></iframe>
    </div>

    <div class="panel">
      <div class="panel-title">Monthly Estimated Sales (Positive Reviews × 30)</div>
      <iframe src="{sales_file.name}"></iframe>
    </div>

    <div class="panel">
      <div class="panel-title">Monthly Peak CCU by Game</div>
      <iframe src="{ccu_file.name}"></iframe>
    </div>

    <div class="panel">
      <div class="panel-title">Estimated Lifetime Revenue by Game</div>
      <iframe src="{revenue_file.name}"></iframe>
    </div>

  </div>
</body>
</html>
"""
    out_path = OUT_DIR / "Party_Game_4up_Dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


# --------------------------------------------------------------------------------------
# 10. MAIN – RUN FULL PIPELINE
# --------------------------------------------------------------------------------------

def main():
    # 1) Load
    ccu, sales = load_data()

    # 2) Prepare
    ccu_no_fg, sales_no_fg = prepare_data(ccu, sales)

    # 3) Summary (units + revenue)
    summary = build_revenue_summary(sales_no_fg)

    # 4) Charts
    ccu_fig, ccu_path = make_ccu_chart(ccu_no_fg)
    sales_fig, sales_path = make_sales_chart(sales_no_fg)
    rev_fig, rev_path = make_revenue_bar_chart(summary)
    table_fig, table_path = make_sales_revenue_table(summary)

    # 5) 4-up dashboard
    dashboard_path = make_four_up_dashboard(
        table_file=table_path,
        sales_file=sales_path,
        ccu_file=ccu_path,
        revenue_file=rev_path,
    )

    print("Outputs written to:", OUT_DIR.resolve())
    print(" - CCU chart:", ccu_path)
    print(" - Sales chart:", sales_path)
    print(" - Revenue chart:", rev_path)
    print(" - Sales/revenue table:", table_path)
    print(" - 4-up dashboard:", dashboard_path)


if __name__ == "__main__":
    main()
