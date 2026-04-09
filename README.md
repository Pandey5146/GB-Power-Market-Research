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
