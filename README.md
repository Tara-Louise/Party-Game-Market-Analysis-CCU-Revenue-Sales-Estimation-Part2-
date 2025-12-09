# Party Game Market Analysis – CCU, Revenue & Sales Estimation

This repository contains a complete data analysis of the Steam premium party-game market, based on CCU activity, estimated unit sales, and estimated lifetime revenue.
The analysis was created for a commercial pitch to demonstrate market size, performance benchmarks, and commercial potential for new titles in the genre.

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

4. Combined 4-Chart Dashboard (Optional)

File: Party_Game_4up_Dashboard_Final.html
A single-page dashboard arranging the three charts above plus a summary table.
Useful for pitch decks and presentations.

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

📡 Data Sources

All analysis is fully traceable and based on publicly accessible Steam data:

SteamDB – Peak concurrent players (CCU), review counts, historical charts

Steam Store – Current list price for each title

Industry-standard formulas

Unit estimation: positive reviews × 30

Revenue estimation: units × 50% of Steam price

A separate Source of Truth file can be provided with all URLs and raw data used.

📈 Purpose of This Project

This analysis was created to:

Benchmark commercial performance of premium party games

Demonstrate market demand, longevity and revenue potential

Support pitch decks and greenlight discussions

Provide transparent, reproducible methodology for forecasting

🛠 Technologies Used

Python, Pandas – Data cleaning and calculations

Plotly – Interactive charts

HTML – Packaging visualisations for sharing and presentatio
