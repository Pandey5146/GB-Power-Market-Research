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

Pipeline Workflow
1. Data collection

The pipeline fetches daily BMRS data for:

system prices
net imbalance volume
half-hourly fuel mix

These daily pulls are then aggregated into larger datasets such as weekly and monthly samples.

2. Data processing

The processing layer:

standardizes timestamps
pivots generation by fuel type
constructs clean analytical columns such as gas_gen, wind_gen, and interconnectors
merges price, imbalance, and generation data into a unified master dataset
3. Analysis

The analysis layer currently includes:

descriptive statistics
correlation analysis
hourly price behaviour
volatility inspection
extreme event detection
rule-based spike analysis
regime-style comparison of normal, stressed, and spike periods
Current Analytical Variables

The cleaned master dataset currently includes the following core variables:

gas_gen
wind_gen
nuclear_gen
biomass_gen
hydro_gen
pumped_storage
coal_gen
oil_gen
other_gen
interconnectors
systemSellPrice
systemBuyPrice
netImbalanceVolume
Research Progress to Date
Data engineering
Built a working Python pipeline for BMRS data extraction, processing, and merging
Created daily, weekly, and monthly datasets
Generated a January 2023 monthly master dataset
Validated dataset structure and identified small timestamp gaps in the pilot sample
Descriptive findings

Initial January 2023 analysis shows that:

imbalance is positively associated with higher prices
wind generation is negatively associated with higher prices
gas generation is positively associated with higher prices
evening hours exhibit stronger price stress
extreme price behaviour is not purely linear and cannot be explained by one variable alone
Pilot spike modelling

The January 2023 pilot has been used to test several interpretable rule-based models.

Imbalance-only rule

A simple rule based on high imbalance captures a meaningful share of extreme price events, but does not explain all spikes.

Hybrid rule

A broader rule combining:

high imbalance, or
lower wind with higher gas

produces very strong spike recall in the January pilot.

However, additional analysis showed that while recall is high, precision is much lower, meaning the rule captures a broader stressed-price regime rather than serving as a clean binary spike classifier.

Regime interpretation

A key finding from the pilot work is that the GB balancing market appears to move through distinct price states rather than a simple spike/non-spike split.

The January pilot supports the following structure:

All periods represent the baseline market condition
Signal periods represent a stressed regime with higher prices, more positive imbalance, lower wind, and higher gas
Spike periods represent the most extreme market state with much stronger imbalance stress, materially lower wind, and significantly higher gas generation

This suggests that extreme prices are better understood as the endpoint of a broader stressed-market regime.

Conditional probability analysis

The pilot also introduced conditional spike probability analysis, showing that:

higher imbalance materially increases spike probability
weaker wind materially increases spike probability
stronger gas dependence materially increases spike probability

No single variable alone is sufficient to explain spikes fully, which supports a multi-factor regime-based interpretation.

Pilot January 2023 Summary

In the January 2023 pilot:

all periods had an average price of approximately 134.93 £/MWh
signal periods had an average price of approximately 175.93 £/MWh
spike periods had an average price of approximately 269.11 £/MWh

Across these groups:

average imbalance becomes progressively more positive
average wind falls materially
average gas rises materially

This monotonic progression is one of the strongest findings in the pilot analysis.

Current Research Interpretation

The project currently supports the following working hypothesis:

Extreme GB balancing prices are not driven by imbalance alone.
Wind and gas materially shape stressed market states.
Price behaviour appears to be regime-based rather than purely linear.
Many apparent model false positives are actually near-spike or elevated-price periods, indicating that regime detection may be more informative than strict binary classification.
Next Steps

The next stages of the project are:

Near-term
formalize January 2023 as a pilot methodology case study
extend the same framework to full-year 2023
build regime summary tables across broader samples
test additional interpretable mathematical models, including:
conditional probability models
logistic regression
regime scoring / stress-index methods
time-of-day and persistence effects
Medium-term
scale the analysis to full 2024 and 2025 datasets
compare regime behaviour across years
test robustness of findings across multiple market conditions
Longer-term
incorporate additional explanatory variables such as weather and demand-related drivers
develop stronger probabilistic and regression-based models
translate regime findings into trading-oriented research signals
build a broader quantitative power market research and analytics platform
Project Status

The project is currently in the pilot research phase.

Completed:

data pipeline
monthly pilot dataset
initial descriptive analysis
first interpretable spike models
regime-style pilot findings
conditional spike probability analysis

In progress:

strengthening the mathematical framework on the January 2023 pilot
preparing the methodology for scaling across full multi-year datasets
Technical Stack
Python
pandas
requests
matplotlib
Elexon BMRS API
Notes

This repository is being developed as a research-first project. The emphasis is currently on interpretable market understanding, robust methodology, and regime-based analysis rather than immediate black-box forecasting.

<<<<<<< HEAD
The long-term objective is to build a rigorous foundation for quantitative power market research and trading analysis in the GB market.
=======
The long-term objective is to build a rigorous foundation for quantitative power market research and trading analysis in the GB market.
>>>>>>> 8f8e677 (Add January pilot probabilistic modelling and logistic regression analysis)
