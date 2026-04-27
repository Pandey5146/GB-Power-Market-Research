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

Small research note

Triple-condition probability analysis tests whether extreme prices arise most strongly when multiple market stresses and timing effects occur simultaneously. This is often closer to real power-market behaviour than single-factor analysis.

Research note

The regime structure identified in the January 2023 pilot generalizes well to the full-year 2023 sample. Signal periods and spike periods remain clearly distinguishable from the unconditional market baseline by higher prices, more positive imbalance, lower wind generation, and higher gas generation.

Research note

Spike frequency in full-year 2023 is materially lower than in the January pilot sample, indicating that January represented a relatively spike-rich stress window rather than an average month. This strengthens the value of scaling from pilot analysis to full-year validation.

Research note

The full-year 2023 summary provides the first strong evidence that the regime-based framework is not merely month-specific, but may reflect a more persistent structural feature of GB balancing price behaviour.

The January pilot suggested a broad multi-factor stress mechanism, while full-year 2023 results show that very high gas generation is the strongest single-condition indicator of spike risk, with imbalance also playing a major role.

Important nuance about wind

The wind conditions still matter, but not strongly enough on their own across the whole year.

That likely means:

low wind is an important supporting condition
but its strongest effect may appear in combination with:
time-of-day
imbalance
gas

So wind may be more powerful in interactions than as a standalone full-year variable.

That is actually very plausible in power markets.

Research note

The unconditional full-year 2023 spike probability is approximately 0.69%, much lower than in the January pilot. This confirms that January was a spike-rich pilot window rather than a representative spike frequency for the whole year.

Research note

Across the full-year sample, gas > 15000 is the strongest single-condition spike indicator, raising spike probability to 2.69%, or nearly four times the full-year baseline.

Research note

Imbalance remains an important spike driver at full-year scale, while wind appears weaker as a standalone predictor and may play a more important role through interaction effects.

Research note

Full-year 2023 triple-condition analysis shows that spike risk increases sharply when multiple stress conditions align. The strongest full-year regime is imbalance > 150, gas > 15000, and hour 16 to 19, with a spike probability of 11.8%.

Research note

This result indicates that evening timing acts as a strong conditioning factor, materially amplifying the spike risk associated with system shortness and thermal-stack stress.

Research note

Compared with the January pilot, the full-year sample places relatively greater emphasis on gas-driven structural scarcity, while still confirming the importance of interaction effects and time-of-day concentration.

Research note

Monthly 2023 analysis shows that extreme-price behaviour was highly concentrated in Q1, especially January, with a sharp decline in spike frequency from April onward.

Research note

The 2023 market is better understood as a sequence of monthly stress regimes rather than a single homogeneous annual sample.

Research note

January 2023 should be treated as a stress-rich pilot month, while April to September represent a much quieter low-spike regime. This strengthens the case for regime-dependent modelling and seasonal interpretation.
Most important monthly pattern

You can now describe 2023 as three broad seasonal regimes:

Regime A — Winter/Q1 stress regime
January, February, March
highest prices
highest spike probabilities
relatively high gas
still meaningful wind, but not enough to suppress stress
Regime B — Spring/Summer low-stress regime
April to September
almost no spikes
much lower average prices
more negative average imbalance in several months
Regime C — Autumn transition regime
October and November
some spikes return
prices rise relative to summer
stress returns, but not like Q1

December sits somewhat separately because it is:

winter calendar-wise
but high-wind and low-price structurally

Small research notes
Research note

Monthly 2023 analysis shows that extreme-price activity was highly concentrated in Q1, especially January, while April to September formed a much quieter low-spike regime.

Research note

The year 2023 is better understood as a sequence of monthly market environments rather than a single stationary process. This supports a regime-based research framework.

Research note

Monthly averages alone do not fully explain spike realization, indicating that within-month event structure, timing, and interaction effects remain important even after seasonal regime classification.

Research note

Seasonal grouping confirms that Q1 2023 was the dominant stress regime, accounting for 111 of the 120 annual spikes.

Research note

April to September formed a very quiet regime with only one spike across 8783 half-hour periods, indicating a structurally different low-risk market environment.

Research note

December behaved as a distinct wind-heavy low-price regime, despite being a winter month, highlighting the importance of generation mix rather than calendar season alone.

Research note

The Q1 stress regime is not characterized by the lowest wind conditions. In fact, the quieter April–September regime shows a much higher share of half-hours with wind < 8000, yet almost no extreme spikes.

Research note

This indicates that weak wind alone is insufficient to explain extreme price formation. The stronger distinguishing features of the Q1 stress regime are a higher incidence of large positive imbalance and materially greater thermal-stack stress, reflected in the higher share of gas > 15000.

Research note

The result strengthens the interaction-based interpretation of GB balancing prices and argues against one-factor explanations of spike behaviour.
Research note

Within the Q1 stress regime, the strongest single-condition spike indicators are gas > 15000 and imbalance > 150, with conditional spike probabilities above 6%.

Research note

Wind remains relevant, but its standalone spike signal is weaker than the strongest gas- and imbalance-based conditions, reinforcing the view that weak wind is more important as part of an interacting stress structure than as a sole driver.
esearch note

Within the Q1 stress regime, the strongest combined-condition spike signal is wind < 8000 and hour 16 to 19, with a conditional spike probability of 19.81%.

Research note

The strongest Q1 pairs all include the late afternoon / evening window, confirming time-of-day as a major conditioning factor in spike realization.

Research note

The Q1 results differ subtly from the full-year annual structure, suggesting that low-wind conditions play a more prominent role inside concentrated winter stress regimes than they do across the broader annual sample.
Research note

Within the Q1 stress regime, the late afternoon/evening window acts as a strong conditioning factor, sharply increasing spike probability when combined with weak wind, high imbalance, or high gas.

Research note

The strongest Q1 pair differs from the strongest full-year pair, which supports the argument that GB balancing price formation is regime-dependent rather than fully stable across the year.
This is one of the strongest results in the whole project so far because it supports all of your core ideas:

the market is regime-dependent
drivers are interaction-based
time-of-day is a major amplifier
the strongest stress mechanism changes by regime

That is much stronger than just saying:

“gas matters”
“wind matters”
“imbalance matters”

Now you can say:

In the Q1 stress regime, extreme-price formation is most sharply associated with the joint occurrence of strong positive imbalance, weak wind output, and late afternoon/evening timing.

Research note

Within the Q1 stress regime, the strongest triple-condition spike configuration is imbalance > 150, wind < 8000, and hour 16 to 19, producing a conditional spike probability of 34.06%.

Research note

This result suggests that winter stress spikes are best understood as a joint product of system shortness, renewable weakness, and vulnerable evening timing.

Research note

The strongest Q1 triple condition differs from the strongest full-year triple condition, reinforcing the conclusion that GB balancing price formation is regime-dependent and seasonally variable

Q: Why are we doing this now?

Because this becomes the template table for 2024 and 2025 too.

Q: Is this final?

Not fully. This is the first structured fingerprint table. We will refine it.

Q: Why only Q1 has strongest-condition fields filled?

Because that is the regime we have analyzed deeply so far. We will fill the others as we progress.

Research note

The 2023 regime fingerprint table confirms that the GB balancing market in 2023 is best understood as a set of distinct seasonal regimes rather than a single annual process.

Research note

Q1 is the main annual stress regime and contains the overwhelming majority of annual spikes, while April to September forms a structurally quiet low-risk regime.

Research note

The strongest Q1 spike mechanism is not a single variable but an interacting regime defined by positive imbalance, weak wind, and late afternoon/evening timing.
Small Q&A
Q: Do we need timestamp validation for 2024?

Not now. The row count is exactly complete for a leap year.

Q: What is the next research question?

Whether 2024 has the same monthly stress structure as 2023 or a different one.
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

Small research note

False positives are not always meaningless errors. In power markets, a false positive can represent a stressed or expensive period that did not quite cross the spike threshold. Studying their price distribution helps distinguish a useful stress detector from a poor classifier.

Small research notes
Research note

Inspection of the highest false positives shows that many occur at prices very close to the spike threshold, such as 242–249 £/MWh. This suggests that a substantial portion of the model’s false positives are actually borderline extreme-price events rather than low-value errors.

Research note

The current low precision is therefore partly influenced by the sharp binary threshold at 250 £/MWh. In practical market terms, periods priced at 245–249 £/MWh may still represent materially stressed conditions.

Research note

This supports interpreting the model as a detector of stressed and near-extreme market regimes, rather than a pure binary spike classifier.

our middle rule seems to identify periods where the market is already under economic stress:

gas stack elevated
wind relatively insufficient
imbalance materially positive

Those conditions often lead to:

high prices
near-spikes
spikes

So the rule is picking up the environment in which spikes are likely, not always the exact boundary crossing itself.

That is actually valuable.

Small research notes
Research note

Price-band analysis shows that the middle-rule signals are concentrated overwhelmingly in medium-to-high price periods rather than in low-price or negative-price hours.

Research note

Only 61 of 828 middle-rule signals occurred in the 0_to_100 band, and none occurred in negative-price periods. This suggests the model is not randomly activating during benign market conditions.

Research note

A large share of rule activations occurred in the 200_to_250 and 250_plus regions, supporting the interpretation that the model is detecting stressed and near-extreme pricing regimes rather than noise.

Small research note

A useful regime signal should activate in periods with materially higher average prices than the unconditional market average, even if it does not always identify only formal spikes.

Small research notes
Research note

The middle-rule signal periods have an average price of £175.93/MWh, compared with £134.93/MWh across the full sample. This indicates that the rule identifies materially more expensive market conditions, even when it does not isolate only formal spikes.

Research note

The average price during actual spike periods is £269.11/MWh, which confirms that the model signal sits between normal market conditions and true extreme-price events. This supports a regime-based interpretation.

Regime logic emerging
Normal periods: lower prices, higher wind, lower gas, low/neutral imbalance
Signal periods: elevated prices, tighter system, reduced wind, higher gas
Spike periods: extreme prices, strong imbalance stress, much lower wind, very high gas
---
Small research notes
Research note

Driver comparison reveals a strong monotonic pattern from all periods to signal periods to spike periods. As prices rise, average imbalance becomes more positive, wind generation declines, and gas generation increases substantially.

Research note

Signal periods represent an intermediate regime between normal market conditions and full price spikes. This supports interpreting the rule as a detector of stressed market states rather than only a binary spike classifier.

Research note

The spike regime is characterized by a combination of strong positive imbalance, materially lower wind output, and significantly higher gas generation, consistent with both operational stress and structural scarcity mechanisms.

Research note

Signal periods are distributed across the full day but become more frequent during morning and evening active system windows, especially around hours 17–19.

Research note

Spike periods are much more concentrated than signal periods, with a strong clustering in late afternoon and evening hours. This suggests that time-of-day acts as an additional conditioning factor in extreme price formation.

Research note

The results support a layered regime interpretation: fuel mix and imbalance define the stress environment, while time-of-day helps determine when that stress is most likely to convert into an extreme spike.

Research note

January 2023 should be treated as a pilot methodology window in which candidate quantitative models are tested before scaling the framework to full multi-year analysis.

Research note

The most appropriate next mathematical models are interpretable models that strengthen causal and regime-based understanding, especially conditional probability analysis, logistic regression, and stress-index construction.

Research note

The January 2023 pilot study reveals a monotonic transition from all periods to signal periods to spike periods. Extreme price formation is associated with increasingly positive imbalance, lower wind output, and higher gas generation.

Research note

The signal-period group acts as an intermediate stressed regime between ordinary market conditions and full spike events, supporting a regime-based interpretation of GB balancing price dynamics.

Research note

Conditional probability measures the likelihood of a spike under a specific market condition, such as high imbalance or low wind. It is more informative than unconditional spike frequency because it quantifies how much a condition changes spike risk.

Research note

In this project, conditional probabilities help translate qualitative market intuition into measurable regime relationships.

Research note

The unconditional probability of a spike in January 2023 is 4.72%. All tested conditions increase spike probability materially above this baseline.

Research note

The strongest single conditions in the January pilot are imbalance > 150 and gas > 15000, both of which raise spike probability to above 11%.

Research note

No single market condition alone produces a very high spike probability, supporting the view that extreme prices emerge from multi-factor stressed regimes rather than one-dimensional triggers.

Small research note

Combined conditional probabilities test whether spike formation is driven more strongly by interacting market stresses than by isolated variables. This is especially important in power markets, where extreme prices often emerge when multiple conditions align.

Small research notes
Research note

Combined-condition analysis shows that spike probabilities rise much more sharply under interacting stress conditions than under any single variable alone.

Research note

The strongest January pilot combinations involve low wind, positive imbalance, and late afternoon to evening timing, with conditional spike probabilities rising to roughly 29–39%.

Research note

These results support a regime-based and interaction-based interpretation of GB balancing price formation, rather than a one-factor explanation.

Small research notes
Research note

In the current pilot study, a spike is defined as an extreme price-level event rather than a period-to-period price jump. Specifically, spike periods are those in which systemSellPrice >= 250.

Research note

This definition allows the analysis to focus on extreme-price regimes and their associated market conditions, including imbalance, wind, gas, and time-of-day effects.

Research note

A jump-based definition could be introduced later as a separate event class, but it should not be confused with the current extreme-price threshold framework.

In the January 2023 pilot, single stress conditions roughly doubled spike risk, double conditions raised spike probabilities into the 20–40% range, and the strongest triple condition — high imbalance, low wind, and the 16:00–19:00 window — produced a spike probability of 82.8%
Research note

Triple-condition analysis shows that spike risk rises sharply when system stress, renewable weakness, and vulnerable timing coincide. The strongest January 2023 pilot condition — imbalance > 150, wind < 8000, and hour 16 to 19 — produced a spike probability of 82.76%.

Research note

This result suggests that time-of-day is not merely descriptive but acts as an important conditioning factor that converts broad stress into realized extreme-price events.

Research note

The January pilot therefore supports a layered regime interpretation in which imbalance and generation mix define the stress environment, while the late afternoon/evening window sharply increases the probability of spike realization.

Research note

The January 2023 pilot has now moved beyond exploratory analysis and produced a coherent regime-based findings section suitable for use in a formal paper draft.

Research note

The strongest pilot result is the very high spike probability observed under the joint condition of high imbalance, low wind, and late-day timing.

Research note

The first logistic regression model confirms the expected directional effects of the main explanatory variables: imbalance and gas enter positively, while wind enters negatively. Time-of-day also contributes positively, consistent with the concentration of spike events in later hours.

Research note

At the default 0.5 probability threshold, the model achieves high spike precision (0.600) but low spike recall (0.214). This indicates that the model is selective and conservative, identifying a smaller subset of high-confidence spike periods.

Research note

The logistic model therefore complements the earlier rule-based analysis: rule-based methods were broad and high-recall, while logistic regression is narrower and higher-precision.
In rare-event modelling, the classification threshold matters as much as the model itself. A 0.5 cutoff is often too conservative for rare spikes, so threshold testing is needed to understand the precision–recall trade-off.

Small research note

The 2023 full-year merged dataset is near-complete, with only 8 missing half-hour periods out of 17,520 and no duplicate timestamps. This is sufficiently robust for full-year regime and probabilistic modelling.

The January pilot analysis file has now become too large and mixed for safe extension. For full-year scaling, the correct approach is to temporarily simplify the analysis layer and then rebuild it in modular form once the 2023 framework is validated.

The project has now moved beyond pilot validation. A clean full-year 2023 dataset has been constructed and validated, which means the next stage is to test whether the January regime structure generalizes to the full-year sample.

You now have two layers of modelling:

Layer 1 — Regime filter

Rule-based logic identifies broad stressed conditions.

Layer 2 — Probabilistic spike filter

Logistic regression assigns a sharper probability of actual spike realization.

This is very good for a paper and very good for future trading logic

Research note

Threshold testing shows that the logistic regression model exhibits the expected precision–recall trade-off. Lower probability thresholds improve spike recall, while higher thresholds improve spike precision.

Research note

A 0.5 threshold is too conservative for the January 2023 rare-event setting. More informative pilot thresholds are in the range of 0.10 to 0.30.

Research note

Compared with the earlier rule-based model, logistic regression provides materially higher precision at the cost of lower recall. This suggests that the two approaches serve different purposes: regime detection versus selective spike classification.

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

anuary 2023 Pilot Findings
1. Purpose of the pilot study

January 2023 was used as a pilot sample to develop and test the initial quantitative research framework for GB balancing price analysis. The purpose of this pilot was not to make final multi-year claims, but to establish whether interpretable market variables such as net imbalance volume, wind generation, gas generation, and time-of-day could explain stressed and extreme price behaviour in a meaningful way.

The pilot therefore served three functions:

to validate the data engineering and preprocessing workflow
to identify candidate price drivers and market regimes
to test whether simple quantitative rules could capture extreme-price conditions in an interpretable way
2. Data and sample overview

The January 2023 pilot dataset was constructed from half-hourly Elexon BMRS data, combining:

system prices
net imbalance volume
fuel mix generation data

The cleaned master dataset contained 1,484 half-hourly observations for the month. A timestamp validation exercise showed that the dataset was largely complete, with only four missing timestamps and no duplicate periods. This was considered sufficiently robust for pilot-stage analysis, although the missing periods should be acknowledged in any formal write-up.

The analytical dataset included the following core variables:

systemSellPrice
systemBuyPrice
netImbalanceVolume
wind_gen
gas_gen
other fuel-mix variables including nuclear, biomass, hydro, pumped storage, coal, oil, other generation, and interconnectors
3. Initial market structure findings

The pilot analysis showed that January 2023 balancing prices were not random, but displayed clear structure in relation to both system conditions and generation mix.

The main descriptive findings were:

higher imbalance was associated with higher prices
lower wind generation was associated with higher prices
higher gas generation was associated with higher prices
extreme prices were concentrated in late afternoon and evening hours
negative prices and high-price spikes both appeared in the sample, indicating strong regime variation within the month

These results suggested that price formation could not be explained using a single linear factor alone. Instead, the market appeared to move through different pricing states, ranging from normal conditions to stressed conditions and finally to extreme-price spike conditions.

4. Spike definition and baseline event frequency

For the pilot study, an extreme-price spike was defined as:

systemSellPrice >= 250

This definition was chosen as a practical research threshold for identifying clearly extreme half-hour periods. Under this rule, the January 2023 sample contained:

70 spike periods
out of 1,484 total periods

This implies an unconditional spike probability of:

70 / 1484 = 4.72%

This baseline is important because it provides the reference point against which all later conditional and regime-based probabilities were compared.

5. Rule-based pilot model results
Imbalance-only rule

A simple imbalance-based rule was tested first. This showed that imbalance alone explained a meaningful share of extreme events, confirming that operational system stress is an important driver of high prices. However, imbalance on its own did not explain all spike events.

This was an important early result, because it showed that while imbalance is a major factor, spike formation is not purely an imbalance-only phenomenon.

Hybrid rule

A broader hybrid rule was then tested, combining:

high imbalance, or
lower wind together with higher gas

This rule achieved very high spike recall in the pilot sample, meaning it captured most or all true spike periods depending on the threshold calibration used. However, precision remained low, meaning the rule also flagged many non-spike periods.

This initially appeared to weaken the model, but further inspection showed that many of the so-called false positives were actually near-spike or materially elevated price periods. This led to a more refined interpretation: the rule was not merely a spike detector, but a detector of a broader stressed-price regime.

6. Regime-based interpretation

One of the strongest findings of the January pilot was that the market appears to move through a structured progression rather than a simple binary spike/non-spike split.

A regime-style comparison was made across three groups:

all periods
signal periods identified by the middle-rule stress filter
spike periods (systemSellPrice >= 250)

The average values across these groups were:

Group	Count	Avg Price	Avg Imbalance	Avg Wind	Avg Gas
All periods	1484	134.93	-8.42	10807.04	10041.62
Signal periods	828	175.93	125.64	8997.17	13454.68
Spike periods	70	269.11	318.61	6420.39	18230.99

This table shows a clear monotonic progression:

prices rise from normal to stressed to spike conditions
imbalance becomes more positive
wind falls materially
gas rises materially

This is strong evidence for a regime-based interpretation of January 2023 price behaviour.

7. Time-of-day effects

The pilot also showed that timing plays an important role in spike realization.

Signal periods were distributed across much of the day, but spike periods were much more concentrated in late afternoon and evening hours, especially:

16:00
17:00
18:00
19:00

This suggests that time-of-day acts as more than a descriptive pattern. It appears to function as a conditioning factor that helps convert broad stress into realized extreme-price events.

In other words:

imbalance, wind, and gas help define the stress environment
time-of-day helps determine when that stress is most likely to turn into a true spike
8. Conditional probability results
Single-condition probabilities

The pilot first tested whether individual market conditions raised spike probability above the unconditional baseline of 4.72%.

Examples included:

imbalance > 100
imbalance > 150
wind < 11000
wind < 8000
gas > 10000
gas > 15000

All single conditions raised spike probability to roughly 9.5% to 11.5%, showing that each factor individually increases event risk. However, no single variable alone produced a very high spike probability. This indicated that spike formation is not one-dimensional.

Double-condition probabilities

The analysis then tested combinations of two conditions. These raised spike probability substantially, in some cases into the 20% to 39% range.

Strong examples included:

imbalance > 150 and wind < 8000
imbalance > 150 and hour 16 to 19
wind < 8000 and hour 16 to 19

This showed that interacting conditions explain spikes much better than isolated variables.

Triple-condition probabilities

The strongest pilot result came from triple-condition analysis.

The most important condition was:

imbalance > 150
wind < 8000
hour 16 to 19

This condition occurred in 29 periods, and 24 of those were spikes, giving:

P(spike | imbalance > 150 and wind < 8000 and hour 16 to 19) = 82.76%

This is a very strong pilot result. It suggests that when system shortness, weak wind, and the vulnerable late-day time window align, extreme price realization becomes highly likely.

Other triple conditions also increased spike probability meaningfully, but none were as strong as the low-wind, high-imbalance, evening combination.

9. Interpretation of the January pilot

The January 2023 pilot supports the following working interpretation of GB balancing price behaviour:

Extreme prices are not explained by imbalance alone.
Wind and gas materially influence whether stressed conditions emerge.
Time-of-day plays a major conditioning role in whether stress converts into an actual spike.
Many model false positives are not meaningless errors, but near-spike or elevated-price stressed periods.
The balancing market is better understood through a regime-based framework than through a simple binary event model alone.

The strongest pilot evidence points toward a layered market mechanism in which:

imbalance and generation mix define the stress environment
late afternoon and evening timing sharpens the probability of extreme-price realization
10. Pilot limitations

The January findings are strong, but they remain pilot-stage evidence and should be interpreted carefully.

The main limitations are:

only one month was analyzed in full detail
some conditional and triple-condition sample sizes are small
the spike definition is based on a research threshold rather than an official market label
the current framework focuses on interpretable rule-based analysis rather than full probabilistic regression or forecasting models

Because of this, the January pilot should be treated as:

a methodology validation stage
a first regime-identification exercise
a foundation for full-year and multi-year analysis

rather than a final proof of market behaviour across all periods.

11. Conclusion of the pilot stage

The January 2023 pilot has successfully established a strong initial quantitative framework for the project.

It has shown that:

the data pipeline is robust enough for serious research
the GB balancing market exhibits identifiable stressed and extreme-price regimes
imbalance, wind, gas, and time-of-day interact in meaningful ways
the strongest spike conditions arise when multiple stress factors align

This provides a strong foundation for the next stage of the project, which should extend the same methodology to broader historical samples and test whether the January regime structure remains stable across 2023, 2024, and 2025.
Research note

The monthly 2024 regime table shows a sharply different annual structure from 2023, with no spike activity from January to September and stress concentrated instead in Q4.

Research note

This indicates that GB balancing-market stress is not only regime-dependent within a year, but also temporally variable across years, with the seasonal timing of stress shifting materially between 2023 and 2024.

Research note

December 2024 emerges as the main stress month of the year, contrasting strongly with January 2023 as the dominant stress month in the previous year.
January 2023 Probabilistic Modelling Findings

Research note

The 2024 regime fingerprint table confirms that the annual stress structure is materially different from 2023. There is no Q1 stress regime in 2024; instead, spike activity is concentrated in late-year transition and December stress periods.

Research note

This supports the view that GB balancing-market stress is not only regime-dependent within a year, but also time-shifting across years.
Research note

The cross-year regime fingerprint comparison shows that the dominant annual stress window shifted from Q1 in 2023 to Q4, especially December, in 2024.

Research note

The main 2024 stress regime was materially weaker than the main 2023 stress regime, indicating that annual spike intensity as well as seasonal timing can vary substantially across years.

Research note

The presence of recurring broad regimes such as quiet, transition, and stress periods suggests structural regularity, but the internal composition of those regimes remains year-dependent.

Research note

In 2024, gas > 15000 is the strongest single-condition spike indicator, with a conditional spike probability of 1.05%, well above all other standalone conditions.

Research note

All 24 observed 2024 spikes occurred under gas > 15000, suggesting that very high thermal-stack stress was a near-universal background feature of spike periods in that year.

Research note

This contrasts with 2023, where the dominant stress mechanism was more clearly tied to a Q1 winter regime and later interaction effects involving low wind and evening timing.

Research note

In 2024, the strongest combined-condition spike signals are imbalance > 150 and gas > 15000 and gas > 15000 and hour 16 to 19, both with conditional spike probabilities of about 1.5%.

Research note

This reinforces the view that 2024 spike formation was more strongly centered on thermal-stack stress than the 2023 Q1 regime, where low wind and evening timing played a more dominant combined role.

Research note

Weak wind remains relevant in 2024, but appears less decisive than very high gas generation as the core stress environment.

Research note

The strongest 2024 triple-condition spike regime is imbalance > 150, gas > 15000, and hour 16 to 19, with a conditional spike probability of 2.29%.

Research note

Unlike 2023 Q1, where weak wind played the leading role in the sharpest triple interaction, the 2024 spike structure is more clearly anchored in thermal-stack stress, with gas > 15000 appearing in all of the strongest triple conditions.

Research note

This suggests that the dominant GB balancing-market spike mechanism is not stable across years: 2023 was more winter-wind-sensitive, while 2024 was more gas-centered and materially less intense.

The GB balancing market has a recurring intra-day stress window in the evening peak, but the severity of that window changes materially across years.

Research note

The 2023–2024 time-band comparison shows that the evening peak is the dominant intra-day stress window in both years, with the highest spike probabilities, highest average prices, strongest positive imbalance, and highest gas generation.

Research note

Although the dangerous time window is structurally stable across years, its intensity is not. Evening-peak spike probability is much higher in 2023 than in 2024, indicating that recurring time-of-day vulnerability is modulated by broader annual regime conditions.

Research note

Night periods in both years show strongly negative average imbalance and near-zero spike activity, suggesting a recurring low-risk system-long environment.

A strong final paper should treat both the spike threshold and the explanatory variable set as methodological choices to be tested, rather than fixed truths. The current framework uses price >= 250 and the core variables of imbalance, wind, and gas as a first structural basis, but later robustness checks should widen both the event definition and the driver set.

Spikes are usually not isolated one-step events. They emerge from a short pre-spike build-up process, but the nature of that build-up differs across years.

Pre-spike build-up analysis shows that both 2023 and 2024 spikes were preceded by progressive tightening over the prior four half-hours, with rising prices, strengthening imbalance, increasing gas generation, and declining wind output.

Research note

The structure of pre-spike tightening differs across years. In 2023, spikes appear more closely associated with stronger imbalance escalation, whereas in 2024 spikes arise within an already extreme low-wind, high-gas environment.

Research note

The final half-hour before the spike is especially important in both years, indicating that spike realization often occurs through a late acceleration phase rather than an entirely abrupt one-period shock.

Near-spikes and spikes do not emerge from completely different worlds.

They often share a common stressed background, but real spikes are distinguished by:

more severe wind weakness,
more severe gas stress,
and/or a sharper final escalation in imbalance and price.

Research note

Near-spikes in both years already occur under stressed conditions, indicating that extreme price formation is not a binary transition from normality but an escalation from an already tightened state.

Research note

In 2023, the main separation between spikes and near-spikes is associated with materially lower wind and higher gas in real spike periods, alongside stronger imbalance escalation.

Research note

In 2024, both spikes and near-spikes occur in an already extreme low-wind, high-gas environment, suggesting that the distinction between them is more strongly related to the intensity of final escalation rather than the mere presence of structural stress.

Research note

These results support a layered interpretation of GB balancing stress in which background conditions, amplifiers, and final triggers all play distinct roles.

Extreme balancing-price events in GB are usually not isolated half-hours. In both 2023 and 2024, the majority of spikes occurred as part of clustered sequences, indicating persistence in stressed market states.

Research note

In both 2023 and 2024, most spike periods are clustered rather than isolated, indicating that extreme balancing-price conditions often persist over multiple consecutive settlement periods.

Research note

This suggests that GB balancing stress is not merely episodic but frequently exhibits short-run persistence, consistent with sustained tightness rather than purely instantaneous shocks.

Research note

Although 2024 was much quieter overall than 2023, the clustered nature of spike events remained broadly similar, implying that persistence is a recurring structural feature even when total spike frequency changes.

The spike clustering table shows whether extreme price periods occur as isolated settlement periods or as parts of longer consecutive stress runs. This helps distinguish random one-off spikes from persistent stress episodes.

Cluster length distribution helps distinguish brief spike events from sustained stress episodes, which is essential for understanding whether extreme balancing prices are transient shocks or persistent regime states.

Research note

Cluster-length analysis shows that 2023 contained a broader distribution of spike episode lengths, including a substantial number of 2-, 3-, and 4+ period clusters, consistent with a more intense and persistent stress environment.

Research note

Although 2024 was quieter overall, it still exhibited long multi-period spike clusters, indicating that persistent balancing-market stress can arise even in lower-spike years.

Research note

The contrast between 2023 and 2024 suggests that year-to-year differences in spike intensity are reflected not only in total spike counts but also in the distribution of event persistence.

Research note

The price-band driver table shows that GB balancing prices are set in clearly different physical and market environments across the price distribution, rather than varying smoothly within one homogeneous regime.

Research note

Negative-price periods in both 2023 and 2024 are associated with strongly negative imbalance, very high wind generation, and very low gas generation, indicating system-long renewable-heavy conditions.

Research note

The transition from 0_to_100 to 100_to_150 marks a major structural shift, with average imbalance turning sharply positive and gas generation increasing materially in both years.

Research note

The 250_plus regime represents a distinct extreme-price state in both years, characterized by strong positive imbalance, elevated gas generation, and reduced wind output. In 2024 this upper-tail regime is rarer but more thermally extreme than in 2023.

GB balancing prices are not only associated with different system states across price bands, but the transitions between price regimes themselves reveal distinct escalation mechanisms, and those escalation mechanisms vary across years.

Research note

The transition from 0_to_100 to 100_to_150 appears to be the clearest entry point into a stress regime in both 2023 and 2024, marked by a large positive shift in imbalance and a meaningful rise in gas generation.

Research note

The upper-tail transitions differ materially across years. In 2023, the jump from 200_to_250 to 250_plus is associated with a stronger collapse in wind and a larger gas increase, while in 2024 the same jump is characterized by a more explosive price increase within an already gas-heavy environment.

Research note

These results suggest that price formation in the GB balancing market is not governed by one fixed escalation path. Different years appear to move through the upper price ladder through different mechanisms.

Adding interconnectors to the price-band driver table shows that interconnector conditions vary systematically across price regimes, indicating that cross-border system context is relevant to balancing price formation.

Research note

The interconnector pattern differs between years. In 2023, higher-price bands are associated with higher aggregate interconnector levels, while in 2024 upper-tail price bands are associated with lower interconnector levels relative to the normal-price regime.

Research note

This suggests that interconnectors may play different structural roles across years, potentially acting as a stress-accompanying variable in some regimes and as a stress-relief-limited variable in others.

Research note

Interconnector condition analysis shows a marked cross-year contrast. In 2023, spikes are more associated with the upper interconnector distribution, whereas in 2024 no spikes occur in the high-interconnector regimes.

Research note

This suggests that aggregate interconnector conditions may play different structural roles across years: accompanying stress in some periods, while appearing more protective or stress-relieving in others.

Research note

The result strengthens the case for including interconnectors in the price-setting framework, while also highlighting the need for careful event-level interpretation and eventual flow-direction refinement.

1. Introduction

Following the descriptive and rule-based analysis of the January 2023 pilot sample, a formal probabilistic modelling stage was introduced using logistic regression. The purpose of this stage was to move beyond threshold rules and estimate spike probability directly as a function of key market variables.

The pilot logistic model used the following explanatory variables:

net imbalance volume
wind generation
gas generation
hour of day

The target variable remained the pilot spike definition:

systemSellPrice >= 250

This stage was intended to test whether the regime relationships identified earlier could also be confirmed within a formal statistical probability framework.

2. Logistic regression coefficient interpretation

The estimated model coefficients were directionally consistent with the broader January findings.

Net imbalance volume entered positively
Wind generation entered negatively
Gas generation entered positively
Hour of day entered positively

These signs are economically intuitive and strongly aligned with the earlier rule-based and descriptive results.

In particular, the model confirms that:

more positive imbalance is associated with higher spike risk
stronger wind output reduces spike risk
higher gas generation raises spike risk
later hours in the day are associated with greater spike likelihood

This is an important validation result because it shows that the pilot regime story is not only descriptive, but also supported by a formal probabilistic model.

3. Probability ranking and near-spike behaviour

The highest predicted-probability periods included both true spikes and several near-spike periods just below the 250 threshold. This is consistent with the earlier false-positive analysis from the rule-based framework.

This suggests that the logistic model is not simply identifying arbitrary binary labels. It is detecting the same broader stressed-price environment identified earlier in the pilot, where many high-risk periods sit very close to the formal spike threshold.

As a result, the model should be interpreted as estimating the probability of extreme-price realization within a broader stressed regime, rather than as a purely mechanical binary classifier.

4. Threshold trade-off results

Because spike events are rare in the January sample, the classification threshold applied to predicted probabilities was found to be critically important.

At the default threshold of 0.5, the model was highly selective:

spike precision was relatively high
spike recall was low

This showed that the default threshold was too conservative for the January rare-event setting.

Threshold testing across 0.10, 0.20, 0.30, 0.40, and 0.50 showed a clear precision–recall trade-off:

0.10 threshold: high recall, lower precision
0.20 threshold: better balance between coverage and selectivity
0.30 threshold: more balanced precision and recall
0.50 threshold: too strict for broad spike capture

This result is important because it shows that the logistic framework is flexible. It can be tuned depending on whether the goal is:

broader stress detection
balanced research classification
or more selective spike flagging
5. Comparison with rule-based models

The probabilistic model complements the earlier rule-based approach rather than replacing it.

The rule-based model:

captures broad stressed market states
achieves very high recall
but has low precision

The logistic model:

produces more selective predictions
materially improves precision
but captures fewer spikes at higher thresholds

This distinction is useful for research interpretation.

It suggests that the two modelling approaches operate at different levels:

the rule-based framework acts as a stressed-regime detector
the logistic regression model acts as a sharper spike-probability filter

This layered interpretation is particularly promising for later quantitative trading work, where regime identification and event-probability estimation can play different roles.

6. Pilot conclusion

The January 2023 logistic regression stage successfully provided the first formal probabilistic confirmation of the pilot regime hypothesis.

The main conclusions are:

The signs of the model coefficients strongly support the earlier market-structure interpretation.
Rare-event threshold choice materially affects classification behaviour.
Logistic regression offers a more selective alternative to rule-based filtering.
The strongest research value may come from combining the broad regime filter with a sharper probabilistic model.

Overall, the probabilistic modelling stage strengthens the pilot by showing that the January spike environment can be described not only through rules and conditional probabilities, but also through a formal statistical probability model.