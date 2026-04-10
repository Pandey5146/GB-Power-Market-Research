# GB POWER MARKET RESEARCH

---

## 1. Research Definition

### Title

A Data-Driven Study of Great Britain Electricity Prices and Fuel Mix: Comparing Batteries with Other Fuel Types (2023–2025)

### Aim

To analyse how different fuel types and system conditions influence electricity prices in Great Britain, and to compare the role of batteries with other generation sources.

Objective

To test whether extreme GB system price spikes in January 2023 can be explained using a simple interpretable rule based on system imbalance and generation mix.

### Research Question

How do generation mix and system conditions affect electricity prices in Great Britain, and how do batteries compare with other fuel types in this relationship?

## Research Question 1: What drives system price in the GB power market?

Objective:
To identify which generation sources and system variables are associated with system price movements.

Key variables considered:
- Fuel generation (gas, wind, nuclear, etc.)
- Net imbalance volume
- Interconnector flows

Approach:
Use correlation analysis as an initial statistical method to identify relationships between variables and system price.

## Follow-up Research Questions

- Does the negative relationship between wind and price remain consistent across larger samples?
- Does gas become more strongly correlated with price during peak-demand periods?
- Is pumped storage responding to price, or helping shape price outcomes?
- How do interconnector flows behave during extreme price events?
- Do these relationships remain stable across 2023, 2024, and 2025?

## Next Analytical Step: Event-Based Price Classification

Objective:
To classify market periods into price-event categories and compare average system conditions across them.

Motivation:
This will help identify whether imbalance, wind, gas, and interconnector behaviour differ systematically between normal periods, negative-price periods, and extreme-price events.

Are price movements mainly driven by fuel mix, by imbalance/system stress, by weather, or by policy regime?

### Scope

* Region: Great Britain
* Time Period: 2023–2025
* Resolution: Half-hourly

A spike threshold of £250/MWh was used to identify extreme price events. This threshold was chosen to isolate materially abnormal half-hour periods while still preserving a sufficient number of observations for analysis.
---The spike threshold of systemSellPrice >= 250 is a modelling choice rather than a formal market rule. It is used to identify clearly extreme price periods and create a consistent event class for analysis. The threshold should later be tested for robustness against alternative values such as 200 and 300.

A good spike model should not depend completely on one arbitrary threshold. Testing multiple thresholds helps check whether the model captures a real market mechanism or only fits one specific event definition.

Regime A — Balancing stress regime

When imbalance is large, prices spike due to real-time system tightness.

Regime B — Structural scarcity regime

When gas is high and wind is not strong enough to suppress the stack, prices can become extreme even without very large imbalance.

That is a serious and useful insight.

It means price formation is not one-dimensional.

## 2. Data Design

### Master Table: market_data_master

| Column           | Description            | Unit     |
| ---------------- | ---------------------- | -------- |
| datetime         | Timestamp              | datetime |
| price            | Electricity price      | £/MWh    |
| imbalance_price  | System imbalance price | £/MWh    |
| demand           | Total demand           | MW       |
| gas_gen          | Gas generation         | MW       |
| wind_gen         | Wind generation        | MW       |
| solar_gen        | Solar generation       | MW       |
| nuclear_gen      | Nuclear generation     | MW       |
| biomass_gen      | Biomass generation     | MW       |
| hydro_gen        | Hydro generation       | MW       |
| battery_gen      | Battery output         | MW       |
| imports          | Imports                | MW       |
| exports          | Exports                | MW       |
| carbon_intensity | Carbon intensity       | gCO₂/kWh |
| frequency        | System frequency       | Hz       |

---
Data quality
Expected half-hourly observations for January 2023: 1488
Actual observations in merged dataset: 1484
Missing timestamps: 4
Duplicate timestamps: 0

Missing timestamps occurred at:

2023-01-17 20:30
2023-01-22 04:00
2023-01-22 04:30
2023-01-22 05:00

These gaps were small in number, but some occurred near stressed market periods, so they should be acknowledged in any formal write-up.
## 3. Data Sources

(https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?publishDateTimeFrom=2023-01-01&publishDateTimeTo=2023-01-07)
Dataset 1 — Generation by Fuel Type
Source: Elexon BMRS API
Endpoint: FUELHH
Resolution: Half-hourly
Description: Provides generation output by fuel type for each settlement period
Variables:
settlementDate
settlementPeriod
fuelType

### Dataset 2 — System Prices

- Source: Elexon BMRS API
- Endpoint family: balancing / settlement / system-prices
- Resolution: Half-hourly
- Key variables:
  - startTime
  - systemSellPrice
  - systemBuyPrice
  - netImbalanceVolume
- Purpose:
  - represent imbalance price conditions
  - measure system stress and balancing state

---

## 4. Methodology

### Initial Data Inspection
- Loaded FUELHH data from Elexon BMRS API
- Converted JSON response into pandas DataFrame
- Inspected first rows, column names, and dataset shape before cleaning

### FUELHH Initial Inspection
- Dataset loaded successfully from Elexon BMRS API
- Returned columns:
  - dataset
  - publishTime
  - startTime
  - settlementDate
  - settlementPeriod
  - fuelType
  - generation
- The dataset is in long format:
  - one row per fuel type per settlement period
- `startTime` provides a usable half-hour timestamp
- `generation` is measured in MW

### Data Transformation — Pivot

- Converted dataset from long format to wide format
- Each fuel type is now a column
- Each row represents one half-hour timestamp
- Used pivot_table with:
  - index: startTime
  - columns: fuelType
  - values: generation

### Fuel Type Classification

Raw dataset contains 18 fuel types.

These were grouped into broader categories:

- Gas: CCGT, OCGT
- Wind: WIND
- Nuclear: NUCLEAR
- Biomass: BIOMASS
- Hydro: NPSHYD
- Pumped Storage: PS
- Coal: COAL
- Oil: OIL
- Interconnectors: all INT* categories
- Other: OTHER

This grouping simplifies analysis and aligns with market behaviour.

### Pivot Result

- Successfully converted FUELHH data from long to wide format
- Each row now represents one half-hour timestamp
- Each fuel type is represented as a separate column
- Some fuel values are negative:
  - interconnector values may reflect import/export direction
  - pumped storage values may reflect charging vs generation
- A boundary timestamp before the requested date was returned and will be filtered later if needed

### Data Cleaning
- Filtered timestamps to match the intended analysis window exactly
- Removed boundary timestamps outside the requested date range
- Checked missing values across all grouped fuel columns

### Data Validation

- Final dataset contains 96 half-hourly observations
- Covers full 2-day period (48 settlement periods per day)
- No missing values across any variables
- Dataset is now clean and ready for analysis and integration

### Price Data Preparation
- Pulled half-hourly settlement system prices from Elexon BMRS API
- Converted JSON response into pandas DataFrame
- Selected core analytical fields:
  - startTime
  - systemSellPrice
  - systemBuyPrice
  - netImbalanceVolume
- Converted startTime into datetime format

### Price Data Validation

- Detailed system price data loaded successfully
- Dataset contains 48 half-hourly observations for one day
- Selected variables:
  - startTime
  - systemSellPrice
  - systemBuyPrice
  - netImbalanceVolume
- No missing values found
- Price data currently covers a shorter period than the fuel dataset, so merge results will only include overlapping timestamps

### Master Table Construction

- Merged grouped fuel-mix dataset with system price dataset
- Join key: startTime
- Join type: inner join
- Result:
  - 48 half-hourly observations
  - 14 columns
- No missing values in merged dataset
- This table forms the first version of the market master dataset

## Methodology: Correlation Analysis

- A correlation matrix is computed using the merged dataset (df_master)
- Only numeric variables are included
- Focus is placed on correlation with:
  - systemSellPrice

Purpose:
- To identify linear relationships between price and other variables
- To form initial hypotheses (not conclusions)

## Research Workflow Structure

The project follows a three-stage pipeline:

1. Data Collection (`data_pull.py`)
   - Pulls data from the Elexon BMRS API
   - Loads raw API responses into pandas DataFrames

2. Data Processing (`data_process.py`)
   - Cleans and reshapes the raw data
   - Groups fuel types
   - Merges fuel and price datasets into a master table

3. Data Analysis (`analysis.py`)
   - Performs descriptive statistics
   - Computes correlations and other analytical outputs

### Data Storage
- Raw API data is initially stored in memory as pandas DataFrames
- Processed outputs are currently saved as CSV files in `data/processed/`

## Step 9: Weekly Dataset Validation and Interpretation

The dataset was successfully expanded from a 1-day sample to a 7-day sample.

### Dataset Structure
- Rows: 336
- Columns: 14
- Resolution: Half-hourly
- Coverage: 7 days

### Key Observation
Compared with the 1-day sample, correlation strengths became weaker but more realistic. This indicates that the single-day results were influenced by sample-specific conditions, while the weekly sample provides a more representative view of market behaviour.

Spike definition

Extreme price spike defined as:

systemSellPrice >= 250

Under this definition:

Total January spikes = 70
Model 1 — Imbalance-only rule

Rule:

netImbalanceVolume > 100

Result:

Spikes explained: 56 / 70
Spike recall: 0.80

Interpretation:
Imbalance is a major driver of extreme prices, but does not fully explain all spike events.

Model 2 — Strict multi-factor rule

Rule:

high_imbalance AND low_wind AND high_gas

with:

high_imbalance = netImbalanceVolume > 100
low_wind = wind_gen < 11000 or originally 8000
high_gas = gas_gen > 8000

Result with strict AND logic:

Spikes explained: 39 / 70
Recall: 0.557

Interpretation:
This rule is too restrictive and captures only a subset of spikes.

Model 3 — Hybrid regime rule

Rule:

high_imbalance OR (low_wind AND high_gas)

with:

high_imbalance = netImbalanceVolume > 100
low_wind = wind_gen < 11000
high_gas = gas_gen > 8000

Result:

Spikes explained: 70 / 70
Spike recall: 1.00

Interpretation:
This strongly supports a two-regime explanation of extreme price formation in the January 2023 sample.

Market interpretation

The results suggest two distinct but related spike mechanisms:

Imbalance-driven spikes
caused by real-time system stress
associated with high positive net imbalance volume
Generation-mix / scarcity-driven spikes
occur even when imbalance is not extreme
associated with elevated gas generation and wind levels insufficient to suppress marginal prices
Important caution

This result is currently based on:

one month only
in-sample testing
recall only

Therefore, the current model should be viewed as:

a strong research hypothesis
a strong descriptive rule
not yet a production trading model

Research note

Threshold sensitivity testing shows that the hybrid spike model remains strong across multiple spike definitions. This suggests the model captures a real underlying market mechanism rather than fitting only one arbitrary threshold.

Research note

At lower thresholds such as >= 200, the event set becomes broader and includes less extreme high-price periods. This reduces model recall slightly, which is expected because moderate high-price events are more heterogeneous than severe spikes.

Research note

At >= 250 and >= 300, the hybrid model achieved full recall on the January 2023 sample. This supports the idea that the most extreme price events are strongly linked to either imbalance stress or high-gas / weaker-wind structural conditions.

Research note

The hybrid rule achieved perfect recall for January 2023 spikes at the >= 250 threshold, but precision was only 7.5%. This means the rule captures all spike events but also flags a large number of non-spike periods.

Research note

The current hybrid model should therefore be interpreted as a broad market stress regime detector rather than a selective spike prediction model.

Research note

The result suggests that imbalance and generation-mix conditions may be necessary components of spike formation, but they are not sufficient on their own. Additional filters are needed to improve precision.

Research note

Spike and non-spike are researcher-defined classes created by applying a threshold to a continuous price series. In this project, a spike is currently defined as systemSellPrice >= 250.

Research note

Recall measures the proportion of actual spikes captured by the model. It answers the question: “Of all true spike events, how many were detected?”

Research note

Precision measures the proportion of predicted spikes that were actually true spikes. It answers the question: “When the model signals a spike, how often is it correct?”

Research note

A model can have high recall and low precision if it identifies broad stressed market conditions rather than only the most extreme price events.

High recall with low precision means the model catches most spike events but also signals too many non-spike periods. The next research step is to make the rule more selective and observe the recall-precision tradeoff.

Research note

Tightening the thresholds reduced the number of predicted spike signals from 935 to 593, improving precision from approximately 7.5% to 10.3%, but recall declined from 100% to 87.1%.

Research note

This confirms the expected recall–precision trade-off: stricter conditions reduce false positives, but they also exclude some true spike periods.

Research note

The stricter rule remains more of a stressed-regime filter than a precise spike predictor, though it is moving in a more selective direction.

Group 1 — Moderate imbalance spikes

Examples:

2023-01-01 18:00 → imbalance 185.836
2023-01-01 19:00 → imbalance 181.843
2023-01-02 18:30 → imbalance 167.553

These are real spikes, but your new imbalance threshold > 200 is too strict for them.

So one lesson is:

Research note

Some spikes occur with moderately high imbalance, not only extremely high imbalance. Raising the imbalance threshold from 100 to 200 removes part of the genuine spike population.

Group 2 — High price with low gas

Example:

2023-01-01 22:30 → price 290, imbalance 149.124, wind 4767, gas 5039

This one is interesting.

It is a spike, but:

imbalance is below 200
gas is not high at all
wind is low

So this suggests there may be another mechanism:

low wind plus scarcity from something else
not necessarily high gas alone

This is a very important research clue.

Research note

Not all structural spikes are “high-gas spikes.” Some may be associated with low wind and broader system tightness even when gas generation itself is not extreme.

Group 3 — Very high gas but wind cutoff too strict

Examples:

2023-01-19 17:30 → wind 9996, gas 22470
2023-01-25 17:30 → wind 9473, gas 21767
2023-01-25 19:30 → wind 10880, gas 20154

These are the same kind of cases we saw before.

They are missed because:

wind is not below 9000 in all cases
but gas is very high
imbalance is low

So the stricter wind threshold is now excluding real structural spikes.

Research note

Tightening the wind threshold from 11000 to 9000 removes genuine structural scarcity spikes where gas generation is very high but wind remains only moderately low.

Group 4 — Moderate gas structural cases

Example:

2023-01-21 00:30 → wind 5743, gas 9286, imbalance 28.311

This is also useful.

It tells us:

some spikes may happen with low wind and only moderately high gas
your gas threshold > 15000 may now be too harsh
Research note

Increasing the gas threshold to 15000 may be too restrictive, because some real spikes occur with low wind and only moderate gas levels.

Your stricter rule improved precision because it became more selective.

But the rows you shared show that it became too selective in three ways:

imbalance threshold too high
wind threshold too low
gas threshold too high

So it is no surprise recall fell.

This is a classic modelling lesson:

Your original broad rule was capturing a wide stress regime.

Your stricter rule tries to isolate only the most intense stress.

But real spikes can happen in a middle zone too:

imbalance not huge, but still meaningful
wind not extremely low, but low enough
gas not extreme, but still important

So spike formation is not all-or-nothing.

It lives in a gradient.

The stricter rule improved precision a bit, but it missed real spikes because it excluded moderate imbalance cases, moderate gas cases, and structural scarcity cases where wind was not low enough to pass the new cutoff.

The real research lesson

You are discovering a very mature result:

Current variables are good for regime detection

but

not sufficient for precise event timing

That is not a failure.

That is a serious research conclusion.

It means your next modelling improvement probably needs:

more variables
or better engineered features
not just endless threshold tweaking

Small research notes
Research note

The middle rule improves precision slightly relative to the original broad rule while retaining high recall. This suggests that moderate threshold tightening can reduce false alarms without destroying event coverage.

Research note

However, precision remains low across all threshold configurations. This indicates that the current feature set identifies stressed market conditions better than it predicts the exact timing of extreme price spikes.

Research note

The imbalance–wind–gas framework appears to capture broad market regimes rather than a narrow execution-grade trading signal.
---

## 5. Findings

### Early Observations
- The first merged market table was created successfully
- It contains fuel generation, system prices, and imbalance volume
- Price values vary sharply across half-hours, including negative and high positive values
- This suggests strong intra-day market volatility even within a single day

## Results: Correlation with System Price

### Key Findings
- System price shows a strong positive relationship with net imbalance volume (0.902)
- Interconnector flows are also strongly positively correlated with system price (0.851)
- Pumped storage shows strong positive correlation with system price (0.801)
- Gas generation has a moderate positive correlation with system price (0.591)
- Wind generation has a moderate negative correlation with system price (-0.516)
- Nuclear generation shows weak correlation with system price (0.143)
- Oil generation returned NaN, likely due to no variation in the sample

### Initial Interpretation
These results suggest that higher prices are associated with tighter system conditions, stronger balancing activity, and greater use of flexible resources.
Higher wind output appears associated with lower prices, supporting the hypothesis that renewable generation can suppress market prices.

### Wind and Price
Wind generation continues to show a negative relationship with system prices in the weekly dataset, although the magnitude is weaker than in the single-day sample. This suggests that wind suppresses prices, but its effect interacts with other system-wide drivers.

### Imbalance and Price
Net imbalance volume remains the strongest correlate of system price in the weekly dataset, reinforcing the importance of system stress and balancing conditions in short-term price formation.

### Volatility
The 7-day sample remains highly volatile, with a price standard deviation close to 100 £/MWh. Price extremes ranged from -95.71 £/MWh to 300 £/MWh, demonstrating the coexistence of surplus and scarcity conditions within the same week.

The weekly analysis confirms that GB electricity prices are shaped by a combination of system imbalance, generation mix, and intraday demand cycles. While wind generation continues to exhibit a price-suppressing effect, the strongest explanatory relationship is observed with net imbalance volume, highlighting the importance of system tightness. Price volatility remains substantial across the week, with both negative-price events and extreme scarcity-price episodes occurring within a short time horizon.

## Role of Imbalance Volume in Price Formation

Net imbalance volume represents real-time deviations between electricity supply and demand.

A strong positive correlation (~0.81) is observed between imbalance volume and system prices in the weekly dataset.

When the system is short (positive imbalance), higher-cost generation must be dispatched urgently, leading to price spikes. Conversely, when the system is long (negative imbalance), excess generation must be curtailed, often resulting in negative pricing.

This indicates that short-term price formation in the GB market is driven more by system balancing conditions than by individual generation sources alone.

The analysis reveals that electricity price formation in the GB market is strongly driven by system imbalance conditions. Extreme price events occur during periods of positive imbalance, low wind generation, and high gas dispatch, indicating system scarcity. Conversely, negative price events coincide with strongly negative imbalance, high wind output, and reduced gas generation, reflecting surplus system conditions. This demonstrates that short-term price dynamics are governed by the interaction between renewable variability and balancing requirements rather than generation levels alone.

## Imbalance Threshold Behaviour

Extreme price events occur at imbalance levels significantly lower than the maximum observed system imbalance. The minimum imbalance associated with extreme prices (~+86) suggests that price spikes can be triggered even under moderate system short conditions, rather than requiring extreme system stress.

This indicates a non-linear relationship between imbalance and price formation.
The relationship between imbalance volume and price is non-linear. While higher imbalance generally corresponds to higher prices, extreme price events can occur at moderate imbalance levels, suggesting the influence of market mechanisms such as marginal pricing, scarcity effects, and balancing actions.

## Imbalance Threshold and Price Spikes

A simple threshold-based analysis shows that approximately 93% of extreme price events (systemSellPrice ≥ 250 £/MWh) occur when net imbalance volume exceeds 100.

This suggests that imbalance is a dominant driver of price spikes and that threshold-based models can effectively capture extreme price behaviour in the GB electricity market.
1 spike NOT explained by imbalance > 100
However, not all extreme price events are explained by imbalance alone, indicating that additional factors such as system constraints, outages, or market interventions also contribute to price formation.

## Multi-Factor Price Formation Model

While imbalance is the dominant driver of price spikes, incorporating additional system conditions improves interpretability of price formation.

A hybrid model shows that price spikes occur when either:

1. System imbalance exceeds a threshold, or  
2. Low renewable generation coincides with high thermal generation  

This reflects real market behaviour where both system stress and generation mix influence marginal pricing.

## Hybrid Price Spike Model

A hybrid rule-based model was developed to explain extreme price events in the GB electricity market.

The model defines a price spike (≥ £250/MWh) as occurring when either:

1. Net imbalance volume exceeds a threshold of 100, or  
2. Wind generation is low while gas generation is high  

This model successfully explains 100% of extreme price events within the dataset, demonstrating that price formation is driven by both system imbalance and generation mix conditions.

## Code Structure

The project code was modularised into three components:

- `data_pull.py` for extracting raw data from the Elexon BMRS API
- `data_process.py` for transforming, cleaning, and merging datasets
- `analysis.py` for descriptive statistics and correlation analysis

This structure improves clarity, reproducibility, and maintainability of the research workflow.

### Caution
These results are based on a limited sample and represent association only, not causation.

## 6. Insights

- System prices show high intra-day volatility
- Prices range from negative (-48) to extreme highs (290)
- Median price (~200) suggests many periods operate at high marginal cost

- Wind generation varies significantly across the day
- Large swings suggest strong impact on supply conditions and price formation

- Gas generation shows wide variation, indicating its role as a balancing fuel
- High maximum values suggest gas responds to periods of system stress

- Nuclear generation remains nearly constant throughout the day
- Confirms its role as baseload supply in the GB system

- Pumped storage shows both charging (negative values) and generation (positive values)
- Indicates active arbitrage behavior in response to price signals

- Interconnector flows vary significantly and can be both positive and negative
- Suggests cross-border trading responds dynamically to system conditions

- Net imbalance volume fluctuates around zero but shows large deviations
- Indicates periods of both system surplus and shortage within the same day

- The GB power system exhibits strong intra-day dynamics
- Renewable variability (wind) and demand balancing (gas, storage) appear closely linked to price volatility
- Extreme price events coincide with system imbalance conditions

Overnight periods exhibit negative pricing, indicating surplus generation relative to demand, likely driven by high renewable output and reduced system load.

The highest price levels occur during evening peak hours, reflecting increased demand combined with reduced renewable generation, particularly solar output.

Electricity prices in the GB market exhibit strong temporal patterns, with negative prices during low-demand, high-renewable periods (overnight), and peak prices during evening demand surges when reliance on marginal gas generation increases.

## Step 6: Time-Based Price Behaviour

An hourly analysis of system prices reveals clear intraday patterns:

### Key Observations:

- Overnight (00:00–08:00): Predominantly negative prices due to low demand and high renewable generation.
- Morning Ramp (08:00–10:00): Rapid increase in prices as demand rises.
- Midday Plateau (10:00–16:00): Sustained high prices driven by steady demand.
- Evening Peak (17:00–20:00): Highest price levels observed due to peak demand and reduced renewable output.
- Late Evening (21:00–23:00): Prices begin to decline as demand decreases.

### Interpretation:

These patterns confirm that electricity prices are highly sensitive to demand cycles and renewable generation availability, with the evening peak representing the most constrained system conditions.

## Step 7: Price Volatility and Extremes

The analysis reveals substantial price volatility in the GB electricity market, with a standard deviation of 125.5 £/MWh.

### Key Observations:

- Price spikes (up to £290/MWh) occur primarily during afternoon and evening hours (15:30–17:30), coinciding with peak demand and reduced renewable generation.
- A late-night spike (22:30) suggests the presence of imbalance-driven events or forecasting errors.
- Negative pricing events (as low as -£48/MWh) occur consistently during early morning hours (02:30–07:00), indicating periods of excess generation relative to demand.

### Interpretation:

These findings demonstrate that price volatility is driven by both predictable demand cycles and unpredictable system imbalances. The coexistence of extreme positive and negative prices highlights the increasing complexity of power systems with high renewable penetration.

## Initial Market Behaviour Observations (Sample Day Analysis)

### Wind Generation Impact
An inverse relationship is observed between wind generation and system prices. Periods of high wind output correspond to lower system prices, consistent with the merit order effect where low marginal cost renewable generation displaces more expensive sources.

### Gas Generation Impact
Gas generation shows a generally positive relationship with system prices, reflecting its role as a marginal price-setting fuel. However, instances were observed where gas generation remained high while prices were moderate, indicating the influence of concurrent renewable generation and system demand conditions.

### Imbalance Volume Impact
A strong positive correlation exists between net imbalance volume and system prices. Periods of high imbalance correspond to price spikes, suggesting increased reliance on balancing mechanisms and system stress conditions.

## Monthly Dataset Build: January 2023

The January 2023 master dataset was constructed successfully.

### Dataset Structure
- Rows: 1484
- Columns: 14
- Expected rows for full month: 1488
- Missing rows: 4

### Interpretation
The monthly pipeline is functioning correctly and has produced an almost complete half-hourly dataset for January 2023. A small number of timestamps appear to be missing and should be investigated before final model validation.

Regime 1 — imbalance shock regime

When:

net imbalance is strongly positive
system is operationally stressed
balancing price can spike sharply
Regime 2 — structural scarcity / marginal fuel regime

When:

wind is relatively low
gas is relatively high
the system is already sitting on an expensive generation stack

That is a very solid research interpretation

Regime 1 — Operational stress / imbalance regime

When netImbalanceVolume is high, the system is tight in real time, and balancing prices spike.

This is the classic short-term balancing stress mechanism.

Regime 2 — Structural scarcity / thermal stack regime

When gas generation is high and wind is not sufficiently suppressing the stack, prices can spike even without very high imbalance.

This is more like a system-wide marginal cost / scarcity condition.

That is a serious research insight.
It is much better than saying only “imbalance causes spikes.”
---
## 7. Debuuging Notes
## Debugging Note: Python Imports

An import error occurred because Python could not locate `scripts.data_process`.
The issue was traced to file/package structure rather than data logic.

Validation step:
- confirmed contents of the `scripts` directory
- ensured required files existed with correct names
- reran module execution from project root

## Debugging Note: Python Imports

An import error occurred because Python could not locate `scripts.data_process`.
The issue was traced to file/package structure rather than data logic.

Validation step:
- confirmed contents of the `scripts` directory
- ensured required files existed with correct names
- reran module execution from project root

## Debugging Note

A module import error occurred after restructuring the code into separate files.
The issue was traced to function resolution inside `data_process.py`.
This was addressed by verifying exact function names and restoring the processing module with clean definitions.

## Debugging Note

A second import error occurred for `run_basic_analysis` in `analysis.py`.
The issue was resolved by replacing the file contents with a clean function definition and rerunning the module from the project root.

## Debugging Note

A NameError occurred because analysis code was written outside the function scope.
The variable `df_master` is only available inside `run_basic_analysis()`, so all analysis logic must be placed within the function.

## Debugging Note

Although the weekly data pull was successful, the processed output only covered up to 2023-01-03 23:30 because the fuel-processing script still contained a hardcoded sample filter from the earlier 3-day stage.

The filter was updated from:

- startTime < "2023-01-04"

to:

- startTime < "2023-01-08"

This aligned the processing window with the intended 7-day research sample.

## Monthly Expansion Debugging

A KeyError occurred when attempting to pull January fuel data using a single large API request.
The response did not contain the expected `data` field.

Fix:
- Fuel data collection was changed from a single monthly API request to a day-by-day loop
- This made the data extraction more robust and aligned it with the daily price-data retrieval approach



## 8. Policy Notes

(To be filled)
