⚡ GB Power Market Research & Trading Analysis
📌 Overview

This project builds a data-driven analysis and modelling framework for the Great Britain (GB) electricity market using real system data from the Elexon BMRS API.

The goal is to understand:

What drives electricity prices
How imbalance affects price formation
How generation mix (wind, gas, etc.) influences market behaviour
How to build predictive models for price spikes

This project is evolving into a quantitative power trading and analytics platform.

🧠 Key Objectives
Analyse half-hourly GB market data (prices + generation mix)
Identify drivers of price volatility
Build rule-based and mathematical models
Develop predictive signals for extreme price events
Expand toward machine learning & forecasting models
📊 Data Sources

Data is pulled directly from the Elexon BMRS API:

⚡ System Prices (SBP / SSP)
🔋 Net Imbalance Volume
🌬️ Generation mix:
Wind
Gas (CCGT)
Nuclear
Biomass
Hydro
Interconnectors
🏗️ Project Structure
GB Power Market Research/
│
├── scripts/
│   ├── data_pull.py        # Fetch data from API (daily → monthly)
│   ├── data_process.py     # Clean & transform raw data
│   ├── analysis.py         # Analysis + modelling logic
│   └── __init__.py
│
├── data/
│   └── processed/          # (ignored in Git)
│
├── research_notes.md       # Insights & findings
├── Understandingproject.md
├── README.md
└── requirements.txt

Pipeline Workflow
1. Data Collection
Fetches daily data for:
system prices
fuel mix
Aggregates into monthly datasets
2. Data Processing
Cleans timestamps
Converts to half-hourly format
Aggregates generation by fuel type
Merges:
price data
generation data
imbalance data
3. Analysis
Correlation analysis
Volatility measurement
Price distribution
Hourly patterns
Extreme event detection
4. Modelling (Current Stage)
🔹 Threshold Model
IF imbalance > 100 → high probability of price spike
Explains ~93% of spikes (weekly dataset)
🔹 Hybrid Model (Key Result)
Spike occurs if:
    imbalance > 100
    OR
    (low wind AND high gas)
Achieved 100% accuracy on weekly data
📈 Key Insights (So Far)
⚡ Imbalance drives price
Strong positive correlation with price
Extreme prices occur under system short conditions
🌬️ Wind reduces prices
High wind → lower prices
Negative correlation observed
🔥 Gas increases prices
High gas generation → higher prices
Indicates marginal pricing impact
🧠 Non-linear behaviour
Price spikes can occur at moderate imbalance levels
Market behaviour is not linear
⚙️ Dual Market Regimes
Imbalance-driven spikes
Generation-mix-driven spikes
📅 Current Progress
✅ Built full pipeline (data → processing → analysis)
✅ Generated January 2023 dataset (~1484 rows)
✅ Developed first quantitative models
✅ Identified key market drivers
🚧 Validating models on full monthly data
🚀 Next Steps
Validate models on full month & multiple months
Extend dataset (2023 → 2025)
Add:
weather data
demand forecasts
Build:
probability models
regression models
machine learning models (XGBoost / Logistic Regression)
Develop trading strategies & signals

⚡ GB Power Market Research & Trading Analysis
📌 Overview

This project builds a data-driven analysis and modelling framework for the Great Britain (GB) electricity market using real system data from the Elexon BMRS API.

The goal is to understand:

What drives electricity prices
How imbalance affects price formation
How generation mix (wind, gas, etc.) influences market behaviour
How to build predictive models for price spikes

This project is evolving into a quantitative power trading and analytics platform.

🧠 Key Objectives
Analyse half-hourly GB market data (prices + generation mix)
Identify drivers of price volatility
Build rule-based and mathematical models
Develop predictive signals for extreme price events
Expand toward machine learning & forecasting models
📊 Data Sources

Data is pulled directly from the Elexon BMRS API:

⚡ System Prices (SBP / SSP)
🔋 Net Imbalance Volume
🌬️ Generation mix:
Wind
Gas (CCGT)
Nuclear
Biomass
Hydro
Interconnectors
🏗️ Project Structure
GB Power Market Research/
│
├── scripts/
│   ├── data_pull.py        # Fetch data from API (daily → monthly)
│   ├── data_process.py     # Clean & transform raw data
│   ├── analysis.py         # Analysis + modelling logic
│   └── __init__.py
│
├── data/
│   └── processed/          # (ignored in Git)
│
├── research_notes.md       # Insights & findings
├── Understandingproject.md
├── README.md
└── requirements.txt

Pipeline Workflow
1. Data Collection
Fetches daily data for:
system prices
fuel mix
Aggregates into monthly datasets
2. Data Processing
Cleans timestamps
Converts to half-hourly format
Aggregates generation by fuel type
Merges:
price data
generation data
imbalance data
3. Analysis
Correlation analysis
Volatility measurement
Price distribution
Hourly patterns
Extreme event detection
4. Modelling (Current Stage)
🔹 Threshold Model
IF imbalance > 100 → high probability of price spike
Explains ~93% of spikes (weekly dataset)
🔹 Hybrid Model (Key Result)
Spike occurs if:
    imbalance > 100
    OR
    (low wind AND high gas)
Achieved 100% accuracy on weekly data
📈 Key Insights (So Far)
⚡ Imbalance drives price
Strong positive correlation with price
Extreme prices occur under system short conditions
🌬️ Wind reduces prices
High wind → lower prices
Negative correlation observed
🔥 Gas increases prices
High gas generation → higher prices
Indicates marginal pricing impact
🧠 Non-linear behaviour
Price spikes can occur at moderate imbalance levels
Market behaviour is not linear
⚙️ Dual Market Regimes
Imbalance-driven spikes
Generation-mix-driven spikes
📅 Current Progress
✅ Built full pipeline (data → processing → analysis)
✅ Generated January 2023 dataset (~1484 rows)
✅ Developed first quantitative models
✅ Identified key market drivers
🚧 Validating models on full monthly data
🚀 Next Steps
Validate models on full month & multiple months
Extend dataset (2023 → 2025)
Add:
weather data
demand forecasts
Build:
probability models
regression models
machine learning models (XGBoost / Logistic Regression)
Develop trading strategies & signals