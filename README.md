# GB Power Market Research and Trading Analysis

## Overview

This project develops a data-driven research and modelling framework for the Great Britain (GB) electricity market using real half-hourly system data from the Elexon BMRS API.

The purpose of the project is to study GB power market behaviour in a structured quantitative way, with a particular focus on price formation, imbalance dynamics, generation mix effects, and the development of interpretable analytical frameworks that can later support quantitative trading decisions.

The project is being built in stages, beginning with data engineering and pilot statistical analysis, and progressing toward multi-year regime analysis, probability-based modelling, and trading-oriented signal development.

## Research Goals

The project is designed to answer the following questions:

- What are the main drivers of GB balancing price behaviour?
- How strongly does net imbalance volume influence extreme price events?
- How do wind generation, gas generation, and generation mix shape market stress conditions?
- Can high-price and spike regimes be identified using interpretable quantitative rules?
- How can these findings later be translated into robust quantitative trading research?

## Current Scope

The current pilot study focuses on January 2023 as a methodology development window. This pilot has been used to:

- build and validate the data pipeline
- test data quality and timestamp continuity
- explore the relationship between price, imbalance, wind, and gas
- evaluate rule-based spike models
- begin developing a regime-based interpretation of market conditions

This pilot framework will later be extended to full-year analysis across 2023, 2024, and 2025.

## Data Sources

Data is pulled directly from the Elexon BMRS API.

### Core datasets
- System Sell Price (SSP)
- System Buy Price (SBP)
- Net Imbalance Volume (NIV)
- Half-hourly fuel mix generation data

### Fuel categories currently used
- Wind
- Gas
- Nuclear
- Biomass
- Hydro
- Pumped storage
- Coal
- Oil
- Other generation
- Interconnectors

## Project Structure

```text
GB Power Market Research/
│
├── scripts/
│   ├── data_pull.py        # Main pipeline runner
│   ├── data_process.py     # Data cleaning and transformation
│   ├── analysis.py         # Statistical analysis and modelling logic
│   └── __init__.py
│
├── data/
│   └── processed/          # Processed CSV outputs (ignored in Git where required)
│
├── research_notes.md       # Ongoing research notes and findings
├── Understandingproject.md # Project understanding and working notes
├── README.md
└── requirements.txt
