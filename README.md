# Party Game Market Analysis – CCU, Revenue & Sales Estimation

This repository contains a complete data analysis of the Steam premium party-game market, based on CCU activity, estimated unit sales, and estimated lifetime revenue.
The analysis was created for a commercial pitch to demonstrate market size, performance benchmarks, and commercial potential for new titles in the genre.

## Full Analysis Script

The entire analysis (loading data, estimating units & revenue, and generating all 4 charts + dashboard) is contained in:

party_games_analysis.py

You can run it end-to-end with:
bash
python party_games_analysis.py 




# Included Charts
1. Monthly Peak CCU by Game (Interactive)

File: CCU_Interactive_NoFG_AllPeaks_HFFAnnotated_2016_2026.html
An interactive line chart showing monthly peak concurrent players for nine premium party games (Fall Guys and Among Us excluded to keep the scale readable).
<img width="1260" height="691" alt="image" src="https://github.com/user-attachments/assets/39cf542c-63cc-4104-98a9-de835bff7757" />


Data sourced from SteamDB

Displays engagement trends, spikes around updates, promotions, and long-tail patterns

Human: Fall Flat's CCU peak (127k+) is annotated and scaled for visibility

# Monthly Estimated Unit Sales (Reviews × 30)

File: Chart2_Interactive_NoFG_PeakLabels_25kAxis.html
A time-series estimate of monthly unit sales, using the industry-standard heuristic:
<img width="1258" height="687" alt="image" src="https://github.com/user-attachments/assets/6a3fc2c5-a05d-4980-bc4a-23ff2134b7d5" />


Positive Steam reviews × 30 ≈ estimated units sold

All monthly sales values are derived directly from Steam review data

Peak monthly sales are labelled for each title

Excludes Fall Guys for clarity

# Total Estimated Lifetime Revenue by Game

File: Chart3_Total_Revenue_Interactive.html
A per-game revenue comparison using a consistent and transparent method:

Units sold = lifetime positive reviews × 30
<img width="1258" height="680" alt="image" src="https://github.com/user-attachments/assets/e56c2fbe-cb21-4851-8db9-a8e2637827b3" />


Revenue = units × (50% of current Steam price)
This 50% realisation rate is commonly used in industry analysis to account for discounts, bundles, regional pricing and free weekends.
Each bar includes:

Current Steam price

Realised ASP (50%)

Estimated lifetime units

Estimated lifetime revenue (£ millions)

# Combined 4-Chart Dashboard (Optional)

File: Party_Game_4up_Dashboard_Final.html
A single-page dashboard arranging the three charts above plus a summary table.
Useful for pitch decks and presentations.
<img width="1258" height="654" alt="image" src="https://github.com/user-attachments/assets/6a9cb15e-e1ed-49f2-8a5a-c2046facab13" />


📁 Folder Structure
│
├── CCU_Interactive_NoFG_AllPeaks_HFFAnnotated_2016_2026.html
├── Chart2_Interactive_NoFG_PeakLabels_25kAxis.html
├── Chart3_Total_Revenue_Interactive.html
├── Party_Game_4up_Dashboard_Final.html
├── data/
│   ├── CCU_Monthly.csv
│   ├── Sales_Monthly.csv
│   ├── Steam_Prices.csv
│   └── Revenue_Summary.csv
└── README.md

# Data Sources

All analysis is fully traceable and based on publicly accessible Steam data:

SteamDB – Peak concurrent players (CCU), review counts, historical charts

Steam Store – Current list price for each title

Industry-standard formulas

Unit estimation: positive reviews × 30

Revenue estimation: units × 50% of Steam price

A separate Source of Truth file can be provided with all URLs and raw data used.

# Purpose of This Project

This analysis was created to:

Benchmark commercial performance of premium party games

Demonstrate market demand, longevity and revenue potential

Support pitch decks and greenlight discussions

Provide transparent, reproducible methodology for forecasting

# Technologies Used

Python, Pandas – Data cleaning and calculations

Plotly – Interactive charts

HTML – Packaging visualisations for sharing and presentation

# Technical Pipeline
1. Data Collection & Ingestion
1.1 CCU Data (Peak Concurrent Players)

Source: SteamDB “Charts → CCU → History → Monthly Peak”

Data manually exported for each title

Saved as CSV files, e.g.:

CCU_Overcooked.csv
CCU_HumanFallFlat.csv
CCU_PummelParty.csv
...

1.2 Review-Based Sales Data

Source: SteamDB → “Reviews → Positive per month”

Exported to CSV for each game

Then cleaned and merged into a master file:

Sales_Monthly.csv

Column added:

est_sales_x30 = positive_reviews * 30

1.3 Steam Price Data

Source: Steam store page (current live price)

Extracted manually for accuracy

Stored in a simple dictionary in Python:

steam_prices = {
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

🧹 2. Data Cleaning & Preparation
2.1 Standardising dates

Most SteamDB exports use “Month” + “Year” rather than a single timestamp.
To prepare the data for time-series charts:

df["date"] = pd.to_datetime(
    df["year"].astype(str) + "-" + df["month"].astype(str) + "-01"
)

2.2 Merging datasets

CCU and Sales were joined by:

game

date

All games were combined into:

CCU_Monthly.csv
Sales_Monthly.csv

2.3 Removing outliers for clarity

Fall Guys and Among Us were excluded from the CCU and Sales time-series because they distort the scale and hide the performance of standard premium titles.

📐 3. Analytical Methods & Calculations
3.1 Monthly Estimated Sales

Industry standard heuristic:

estimated_units = positive_reviews * 30


Stored as:

df["est_sales_x30"] = df["positive_reviews"] * 30

3.2 Estimated Lifetime Units

Total units per game:

lifetime_units = sales.groupby("game")["est_sales_x30"].sum()

3.3 Revenue Estimation

Revenue uses a 50% realisation rate of the current Steam price to account for:

Discounts

Regional pricing

Promotional giveaways

Bundle dilution

Long-term decay of ASP

Formula:
realised_price = current_price * 0.5
estimated_revenue = lifetime_units * realised_price

Code:
summary = (
    pd.DataFrame({
        "game": lifetime_units.index,
        "estimated_units": lifetime_units.values,
    })
    .assign(
        price_gbp=lambda d: d["game"].map(steam_prices),
        realised_price_gbp=lambda d: d["price_gbp"] * 0.5,
        revenue_gbp=lambda d: d["estimated_units"] * d["realised_price_gbp"],
        revenue_m_gbp=lambda d: d["revenue_gbp"] / 1e6,
    )
)

🎨 4. Visualisation (Plotly)

All charts were built using Plotly Python, with a custom black “neon” theme for pitch-deck readability.

4.1 CCU Chart – Monthly Peak CCU by Game
fig = px.line(
    ccu_no_fg,
    x="date",
    y="peak_ccu",
    color="game",
    title="Monthly Peak CCU by Game",
)
fig.update_traces(mode="lines", line=dict(width=2))

Human Fall Flat annotation:
fig.add_annotation(
    x=hff_peak_date,
    y=60000,  # visible region
    text=f"Human Fall Flat peak ≈ {hff_peak:,} CCU",
    showarrow=True,
    arrowhead=2,
)

4.2 Estimated Monthly Sales Chart
fig = px.line(
    sales_no_fg,
    x="date",
    y="est_sales_x30",
    color="game",
    title="Monthly Estimated Sales (Positive Reviews × 30)",
)


Peak labels added dynamically:

for game, df_g in sales_no_fg.groupby("game"):
    peak_row = df_g.loc[df_g["est_sales_x30"].idxmax()]
    fig.add_annotation(
        x=peak_row["date"],
        y=peak_row["est_sales_x30"],
        text=f"{int(peak_row['est_sales_x30']):,}",
        showarrow=True,
        arrowhead=2,
    )

4.3 Revenue Bar Chart
fig = px.bar(
    summary.sort_values("revenue_m_gbp", ascending=False),
    x="game",
    y="revenue_m_gbp",
    title="Estimated Lifetime Revenue by Game",
)
fig.update_traces(
    text=[f"{row['estimated_units']/1000:.0f}k units\n£{row['revenue_m_gbp']:.1f}m"
          for _, row in summary.iterrows()],
    textposition="outside",
)

4.4 Combined Dashboard (HTML 4-up Layout)

A custom HTML grid layout was used to display all charts together:

<div class="dashboard">
    <iframe src="Chart3_Total_Revenue_Interactive.html"></iframe>
    <iframe src="Chart2_Interactive_NoFG_PeakLabels_25kAxis.html"></iframe>
    <iframe src="CCU_Interactive_NoFG_AllPeaks_HFFAnnotated_2016_2026.html"></iframe>
    <iframe src="Chart1_Sales_Revenue_Table.html"></iframe>
</div>


Styled using CSS grid for a 2×2 responsive dashboard.

🧾 5. Deliverables

Your GitHub repo includes:

Interactive HTML charts

Master data files (CCU, sales, prices, revenue)

Dashboard layout

README documentation

Full technical write-up (this section)

🚀 6. Skills Demonstrated

Data sourcing from public APIs & web platforms

Data cleaning, merging, and time-series preparation

Revenue modelling & commercial estimation

Plotly interactive visualisation

Custom HTML/CSS dashboard design

Reproducible analytical workflow

Stakeholder-facing communication
