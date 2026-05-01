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

Research note

Interconnector combined-condition analysis reveals a strong year-specific contrast. In 2024, no spikes occur under the high-interconnector quartile when combined with major stress drivers, while spikes in 2023 remain compatible with high interconnector conditions.

Research note

This suggests that high interconnector conditions may have been more protective in 2024, whereas in 2023 interconnectors appear more as a stress-accompanying system feature than a reliable stress-relief condition.

Research note

The results support a broader interpretation of price formation in which interconnectors are neither uniformly benign nor uniformly stress-inducing, but instead play a regime-dependent structural role.

Price-band structure
↓
Threshold robustness
↓
Spike realization
↓
Dynamic build-up

In 2023, the transition from broad stress to extreme imbalance prices was marked by a clear tightening of physical system conditions. Average gas generation rose from around 11.4 GW in the £100+ regime to 19.0 GW in the £250+ regime, while average wind generation fell from 7.1 GW to 5.5 GW. The evening-peak share also increased sharply, from 22.9% to 69.2%, indicating that time-of-day acted as a major amplifier of scarcity pricing.

In 2024, the stress ladder was much steeper than in 2023. Only 0.88% of periods exceeded £150/MWh, but those periods were already characterised by very high gas generation and low wind output. At the £250+ threshold, every spike occurred with gas generation above 15 GW and wind generation below 8 GW, indicating a much more thermally concentrated extreme-price regime than in 2023.

normal price regime
↓
broad stress regime
↓
strong stress regime
↓
near-spike regime
↓
spike regime
↓
extreme spike regime

In 2023, time-of-day amplification was central to spike realization. While £100+ and £150+ prices occurred across all time bands, the upper tail became progressively concentrated in the evening peak. By the £250+ threshold, 83 of 120 spike periods occurred during 16:00–19:59, and by the £300+ threshold, 18 of 21 extreme periods were in the evening peak. This indicates that evening demand conditions acted as a major amplifier converting stressed system states into extreme imbalance prices.

In 2024, evening peak remained the highest-risk time band at lower thresholds, but the extreme price tail was less exclusively evening-driven than in 2023. At the £250+ threshold, 11 periods occurred during evening peak, but 13 occurred across morning ramp, midday, and afternoon. This suggests that 2024 spikes were linked to a broader physical scarcity environment, with very high gas generation and very low wind output across several active system periods, rather than only evening demand amplification.

Research note 1

Do not say evening peak “causes” spikes.

Say:

Evening peak acts as an amplifier of already stressed system conditions.

Research note 2

In 2024, the key is not that evening disappeared. It is that the extreme regime became less dependent on evening concentration.

Research note 3

Night remains structurally low risk in both years.

Late evening is also much weaker than evening peak.

That matters because it shows that the danger is not simply “after dark”; it is the specific 16:00–19:59 system peak window.

The annual location of spike risk shifted materially between years. In 2023, almost all £250+ periods were concentrated in Q1. In 2024, all £250+ periods were concentrated in the late-year Oct-Nov transition and December stress regimes, with no £250+ periods in Q1 or Apr-Sep.

Q1 regime-level stress
+
evening peak amplification
+
imbalance / low-wind / high-gas combinations
=
broad and concentrated spike formation

Q1 regime-level stress
+
evening peak amplification
+
imbalance / low-wind / high-gas combinations
=
broad and concentrated spike formation

Threshold-by-regime analysis confirms that high-price periods were strongly regime-dependent rather than randomly distributed across the year. In 2023, the Q1 stress regime accounted for 111 of 120 annual £250+ periods and 18 of 21 £300+ periods, demonstrating that the 2023 price tail was overwhelmingly concentrated in the first-quarter stress environment. By contrast, 2024 showed no £250+ periods during Q1 or Apr-Sep. All 24 annual £250+ periods occurred in the Oct-Nov transition and December stress regimes. This indicates a clear shift in the annual location of spike risk, from early-year stress in 2023 to late-year stress in 2024.

Research note 1

This table validates our regime groups. They are not arbitrary monthly buckets. They explain where stress actually appears.

Research note 2

2023 and 2024 both had spike clustering, but the calendar location of clustering changed.

This becomes important later when we add external event/policy/outage overlays.

Research note 3

The December 2023 row is interesting because the wider regime was windy, but its rare spikes occurred under extremely low wind and very high gas.

That supports a useful concept:

regime background ≠ local event condition

Oct-Nov 2024 should not be ignored. It produced 10 of 24 annual £250+ spikes and 6 of 17 £300+ periods.

So the 2024 story is not only December. It is:

Oct-Nov transition + December stress

The 7 March 2023 £1950/MWh event occurred during an already stressed internal system state: low wind, high gas generation, strongly positive imbalance, evening peak timing, and relatively low interconnector support. REMIT messages also indicate contemporaneous interconnector restrictions and thermal generation unavailability, suggesting the price event coincided with a wider scarcity and availability-stress context.

The 14 October 2024 spike occurred in the Oct-Nov transition regime under very low wind, high gas generation, very positive imbalance, and lower interconnector support. REMIT messages show multiple contemporaneous generation availability reductions, including fossil gas and wind units. This supports classifying the event as a high-confidence scarcity-context event, although causality should be framed as association rather than a single-unit cause.

The 11 December 2024 midday spike appears more strongly linked to the physical background of very low wind and extreme gas dependence than to imbalance escalation alone. REMIT messages show several generation and flexibility asset unavailabilities during the broader window, while interconnector restrictions became more relevant later in the afternoon.

The 12 December 2024 evening spike occurred during very low wind and very high gas generation, with moderate aggregate interconnector flow. REMIT messages show simultaneous Moyle and EWIC interconnector restrictions, with periods of zero capacity during the spike window. This suggests the event sat within a low-wind, high-thermal, reduced-cross-border-flexibility context.

The 7 March 2023 £1950/MWh event occurred during a compound scarcity context: low wind, high gas generation, strongly positive imbalance, evening-peak timing, reduced interconnector availability, and multiple thermal generation availability reductions. REMIT evidence therefore supports a high-confidence association between the price event and wider asset-availability stress, although the analysis does not attribute causality to any single unit.

In 2024, priority spike events also coincided with REMIT-reported capacity events. Thermal generation unavailability showed high-confidence association with price events up to £669/MWh, while interconnector unavailability showed high-confidence association around December stress episodes. This supports the interpretation that 2024’s spike formation was linked to physical scarcity and reduced flexibility rather than imbalance alone.

Earlier, we were doing mainly structural analysis:

price bands
thresholds
time bands
regime groups
interconnectors
spike build-up
near-spikes
clusters

That explained what kind of market conditions are linked with different price regimes.

But then you correctly clarified that you wanted to go deeper:

If a wind turbine, gas turbine, interconnector, or other asset went into outage/maintenance/unavailability, did that coincide with the price jump? And what were wind, gas, imbalance, and interconnector flow at that moment?

That shifted the work from broad regime analysis into:

event-level price formation
+
asset/event-led explanation
+
REMIT availability evidence

This was the right move.

1. Main research note: why event-level analysis matters

The earlier tables showed that high prices are associated with:

high gas
low wind
positive imbalance
evening peak
interconnector context
specific annual regimes

But this does not fully answer:

Why did the price jump at that exact moment?

The event-level analysis starts answering that by checking whether specific price events coincided with:

gas unit unavailability
wind asset unavailability
interconnector restriction
planned maintenance
unplanned outage
capacity reduction
system flexibility constraints

This is important because imbalance price spikes are not only about average system conditions. They can form when an already stressed system loses marginal flexibility or has reduced available capacity.

2. What we built in the event-analysis branch

We built a sequence of tables.

A. Price event candidates

File:

outputs/tables/2023_2024_price_event_candidates.csv

Purpose:

To identify exact windows where price behaviour was interesting.

Event types included:

positive_spike_cluster      price >= 250
extreme_spike_cluster       price >= 300
near_spike_cluster          200 <= price < 250
negative_price_cluster      price < 0
large_upward_jump           price jump >= +100 from previous period
large_downward_reversal     price fall <= -100 from previous period

Research note:

This table moved the project away from yearly averages and into exact price-event windows.

B. Priority price events for external check

File:

outputs/tables/2023_2024_priority_price_events_for_external_check.csv

Purpose:

The full event-candidate table had 1,872 rows, which was too many to check manually against REMIT.

So we shortlisted:

top positive spikes
all extreme spikes
top negative price clusters
largest upward jumps
largest downward reversals

Research note:

This table helped us avoid random event research. It told us which price events were most worth checking externally.

C. Priority price event windows

File:

outputs/tables/2023_2024_priority_price_event_windows.csv

Purpose:

For each priority event, we created external checking windows:

2 hours before event start
event period itself
2 hours after event end

Research note:

This gave a clean time window for REMIT / outage / maintenance checks.

D. REMIT query windows

File:

outputs/tables/2023_2024_remit_query_windows.csv

Purpose:

This converted price-event windows into API-ready windows.

Important dates identified:

2023-01-02
2023-01-25
2023-01-26
2023-03-07
2023-06-12
2023-10-16
2023-12-01

2024-10-14
2024-11-05
2024-12-11
2024-12-12

Research note:

The most important windows were:

2023-03-07
2024-10-14
2024-12-11
2024-12-12

These became our first case-study set.

E. Filtered REMIT events near price events

File:

outputs/tables/2023_2024_filtered_remit_events_near_price_events.csv

Purpose:

To pull REMIT messages around the main price-event windows and filter them for meaningful availability/capacity events.

Important REMIT fields included:

remit_eventType
remit_unavailabilityType
remit_assetType
remit_affectedUnit
remit_fuelType
remit_normalCapacity
remit_availableCapacity
remit_unavailableCapacity
remit_eventStatus
remit_eventStartTime
remit_eventEndTime
remit_cause
remit_relatedInformation
remit_outageProfile

Research note:

This confirmed that REMIT data can directly support the paper’s structural overlay layer.

F. Asset-event price impact table

File:

outputs/tables/2023_2024_asset_event_price_impact.csv

Purpose:

To summarise REMIT events by price event and external event type.

This table connected:

price event
internal market state
external asset/interconnector event
unavailable capacity
association strength

This was the first proper event-level impact table.

G. Price event case studies

File:

outputs/tables/2023_2024_price_event_case_studies.csv

Purpose:

To turn technical REMIT outputs into paper-readable case studies.

Cases:

Case 1: 2023-03-07 £1950/MWh event
Case 2: 2024-10-14 £669.21/MWh event
Case 3: 2024-12-11 £590.45/MWh event
Case 4: 2024-12-12 £521.09/MWh event
H. Case-study research notes

File:

outputs/tables/2023_2024_case_study_research_notes.csv

Purpose:

To lock the case studies into paper-ready research notes and future scenario labels.

Scenario labels:

compound_scarcity_with_asset_and_interconnector_stress

imbalance_amplified_scarcity_with_generation_availability_stress

physical_scarcity_low_wind_high_gas_less_imbalance_driven

physical_scarcity_with_interconnector_restriction_and_low_wind

Research note:

These scenario labels can later be used for 2025 comparison and eventually a 2026/2027 scenario-risk framework.

3. Main event-level findings
Finding 1: 7 March 2023 was a compound scarcity event

The key 2023 event was:

2023-03-07
max price: £1950/MWh
regime: q1_stress
time band: evening peak

Internal market state:

very high gas generation
very low wind
strong positive imbalance
relatively low interconnector support
evening peak timing

REMIT evidence showed:

thermal gas unavailability
interconnector unavailability
wind unavailability
maintenance/de-load
other capacity events

The summary table showed:

interconnector_unavailability: high confidence, 500 MW
thermal_gas_unavailability: high confidence, 4825 MW
wind_unavailability: medium confidence, 882 MW
maintenance_or_deload: medium confidence, 492 MW
other capacity changes: medium confidence, 2210 MW
Research note

This is probably the strongest single case study in the whole 2023–2024 analysis.

It connects nearly every layer of the paper:

Q1 stress regime
evening peak amplification
low wind
high gas
positive imbalance
reduced interconnector support
thermal generation unavailability
interconnector restrictions
Paper-safe interpretation

The 7 March 2023 £1950/MWh event occurred during a compound scarcity context. The price event coincided with low wind, high gas generation, strongly positive imbalance, evening-peak timing, relatively low interconnector support, and REMIT-reported thermal and interconnector availability constraints. This supports a high-confidence association between the price event and wider scarcity/availability stress, but does not prove causality from any single asset.

Finding 2: 14 October 2024 was an imbalance-amplified scarcity event

The key October 2024 event was:

2024-10-14
max price: £669.212/MWh
regime: oct_nov_transition
time band: evening peak

Internal market state:

very positive imbalance
very low wind
high gas generation
lower interconnector support
evening peak timing

REMIT evidence showed:

thermal gas availability reductions
wind unavailability
other capacity reductions

Examples from the REMIT output included gas and wind unit availability reductions around the event window.

Research note

This event proves that 2024 stress did not begin only in December.

The oct_nov_transition regime was a real stress-transition regime, not just a mild seasonal label.

Paper-safe interpretation

The 14 October 2024 spike occurred in the Oct-Nov transition regime under very low wind, high gas generation, strongly positive imbalance, lower interconnector support, and REMIT-reported generation availability reductions. This supports interpreting the event as an imbalance-amplified scarcity episode.

Finding 3: 11 December 2024 was more physical-scarcity driven than imbalance driven

The 11 December 2024 event was:

2024-12-11
max price: £590.45/MWh
regime: dec_stress
time band: midday

Internal market state:

very low wind
extremely high gas generation
imbalance not extremely high
interconnectors still moderate/high in the midday event

This is important because the price was high even without a huge imbalance signal.

REMIT evidence included:

thermal gas unavailability
wind unavailability
hydro/pumped storage unavailability
biomass availability events
interconnector events becoming relevant later in the day
Research note

This event supports the idea that December 2024 was a physical scarcity regime.

In this case, the system was already stretched by very low wind and extremely high gas dependence. The price did not require a very large imbalance trigger to move into the upper tail.

Paper-safe interpretation

The 11 December 2024 event occurred in the December stress regime. Price reached £590.45/MWh while wind was very low and gas generation was extremely high. Unlike the October event, imbalance was not the dominant signal. REMIT records show generation, wind, flexibility and interconnector-related capacity events in the wider window. This supports the interpretation that the event was mainly a physical scarcity / low-wind high-gas episode.

Finding 4: 12 December 2024 combined physical scarcity with interconnector restrictions

The 12 December 2024 event was:

2024-12-12
max price: £521.09/MWh
regime: dec_stress
time band: evening peak

Internal market state:

very low wind
very high gas generation
moderate imbalance
interconnectors lower than 11 Dec midday
evening peak

REMIT evidence showed:

EWIC interconnector restriction
Moyle interconnector restriction
thermal gas unavailability
wind unavailability
other generation availability events

Important REMIT details from the output:

EWIC unavailable/restricted around 13:00–20:00
Moyle unavailable/restricted around 14:00–21:00
both had periods with zero available capacity during the afternoon/evening window
Research note

This is the best 2024 case for the interconnector layer.

It supports the idea that interconnectors were not just a background variable. During some high-price events, reduced cross-border flexibility coincided with very low wind and high gas generation.

Paper-safe interpretation

The 12 December 2024 event occurred during the December stress regime. Price reached £521.09/MWh with very low wind and very high gas generation. REMIT evidence shows interconnector restrictions and generation availability reductions during the event window. This supports interpreting the event as a low-wind, high-thermal, reduced-flexibility scarcity episode.

4. Key cross-year research notes
Research note 1: 2023 and 2024 had different event architectures

2023’s main case was:

compound scarcity
+
positive imbalance
+
evening peak
+
interconnector restriction
+
thermal availability stress

2024 had two types:

October 2024:
imbalance-amplified scarcity

December 2024:
physical scarcity / low-wind high-gas stress
with interconnector restrictions becoming important

So the paper should not say:

“Spikes are caused by low wind and high gas.”

It should say:

“Extreme imbalance prices emerge through different event architectures depending on the year and regime.”

Research note 2: REMIT evidence strengthens but does not prove causality

The REMIT layer is powerful because it shows that price events coincided with real asset and interconnector availability conditions.

But we must be careful.

Correct wording:

coincided with
occurred during
is consistent with
suggests contribution
supports a high-confidence association

Avoid:

caused by
proved by
directly caused

Because a price event can be influenced by multiple interacting factors:

wind output
gas generation
imbalance
time of day
interconnector flows
asset availability
BM bid stack
reserve scarcity
demand level
network constraints
Research note 3: December 2024 was not mainly an imbalance story

This is very important.

In the December 2024 case studies, imbalance was not always extreme.

But prices were still high because:

wind was extremely low
gas generation was extremely high
asset/flexibility availability was reduced
interconnectors were restricted in some windows

So December 2024 should be described as:

physical scarcity / low-wind high-gas regime

not only:

positive imbalance regime
Research note 4: October 2024 was different from December 2024

October 2024 had:

very positive imbalance
low wind
high gas
availability stress
evening peak

December 2024 had:

very low wind
extreme gas
interconnector/flexibility restrictions
but not always extreme imbalance

So 2024 has at least two late-year mechanisms:

Oct-Nov transition: imbalance-amplified scarcity
December stress: physical scarcity / high gas dependence

This is a strong finding.

Research note 5: Interconnector restrictions matter at event level

Earlier, our interconnector tables showed that interconnectors behaved differently across years.

Now the REMIT layer gives event-level support.

Examples:

7 March 2023:
Moyle / EWIC restrictions around the high-price window

12 December 2024:
Moyle / EWIC restrictions around the high-price window

So we can now say:

Interconnector conditions were not only associated with price regimes statistically; in key case-study windows, REMIT records also showed interconnector restrictions.

That is a strong bridge between quantitative analysis and external evidence.

Research note 6: This branch prepares the future scenario model

The case-study notes produced four scenario labels:

compound_scarcity_with_asset_and_interconnector_stress

imbalance_amplified_scarcity_with_generation_availability_stress

physical_scarcity_low_wind_high_gas_less_imbalance_driven

physical_scarcity_with_interconnector_restriction_and_low_wind

These are exactly the labels we can later use when applying the framework to 2025 and then building a 2026/2027 scenario outlook.

The future model should not blindly predict exact prices.

It should classify market states into scenario types.

Example:

low wind
high gas
positive imbalance
low interconnector support
REMIT thermal outage
evening peak

Scenario:

compound scarcity / high spike-risk event
5. What this means for 2025

When we analyse 2025, we should test whether events resemble:

2023-03-07 compound scarcity
2024-10-14 imbalance-amplified scarcity
2024-12-11 physical low-wind/high-gas scarcity
2024-12-12 physical scarcity with interconnector restriction

The question for 2025 is not only:

How many spikes happened?

The better question is:

Which event architecture did 2025 follow?

Possible outcomes:

2025 looks like 2023:
broader compound scarcity with imbalance and evening amplification

2025 looks like 2024 October:
transition-season imbalance-amplified scarcity

2025 looks like 2024 December:
physical scarcity under low wind and high gas

2025 is different:
new structure, perhaps more negative prices or more interconnector-driven behaviour
6. Event-analysis Q&A
Q1: Did we find evidence that outages or maintenance coincided with price spikes?

Yes. For the main case-study windows, REMIT data showed asset or interconnector availability events around the same periods as major price events.

Examples included:

thermal gas unavailability
wind unavailability
interconnector restrictions
maintenance / de-load events
other generation capacity changes
Q2: Did we prove that one gas turbine or one wind farm caused the price spike?

No.

We should not claim that.

The correct conclusion is:

The price event occurred during stressed internal market conditions and coincided with REMIT-reported availability constraints.

That is association, not single-asset causality.

Q3: Why is the 7 March 2023 case so important?

Because it combines almost every stress layer:

Q1 stress regime
evening peak
low wind
high gas
positive imbalance
lower interconnector support
thermal generation unavailability
interconnector unavailability

It is the best example of a compound scarcity event.

Q4: Why is 14 October 2024 important?

Because it shows 2024 stress began before December.

The Oct-Nov transition regime was not just a mild transition. It produced a major spike under:

low wind
high gas
very positive imbalance
lower interconnector support
generation availability stress
Q5: Why are 11 and 12 December 2024 important?

Because they show a different mechanism.

The December 2024 events were more about:

very low wind
extreme gas generation
reduced flexibility
interconnector restrictions

rather than purely extreme imbalance.

Q6: What is the difference between October 2024 and December 2024?

October 2024 looked more like:

imbalance-amplified scarcity

December 2024 looked more like:

physical scarcity / low-wind high-gas regime

This distinction is important for the paper.

Q7: Why include REMIT data?

Because REMIT gives real external evidence of:

planned outages
unplanned outages
availability reductions
interconnector restrictions
capacity changes
asset-level events

This lets us connect market-price behaviour with real system events.

Q8: What does “high confidence association” mean?

It means:

the price event was severe
internal scarcity indicators were strong
and relevant REMIT availability events were present in the event window

It does not mean:

the REMIT event directly caused the price
Q9: Why did we not pull every REMIT event for every price event?

Because the REMIT API returned hundreds of messages per window.

Pulling all 23 windows fully would be slow and noisy.

So we focused first on the four strongest case-study windows:

2023-03-07
2024-10-14
2024-12-11
2024-12-12

This was the correct research approach.

Q10: What should we do later with negative price events?

Negative prices need a separate event-analysis branch.

For negative prices, the mechanism is different:

high wind
low gas
negative imbalance
low demand / surplus conditions
downward balancing pressure
possible export/interconnector constraints

We have not fully done that yet.

That should come later, likely after 2025 or as a separate paper subsection.

Q11: How will this help with 2026 or 2027?

It gives scenario templates.

Instead of predicting exact prices, we can say:

If 2026 has conditions similar to the 7 March 2023 compound scarcity case, the system is in a high spike-risk scenario.

Or:

If 2026 has low wind, high gas, and interconnector restrictions like 12 December 2024, the system resembles a physical scarcity / reduced-flexibility scenario.

This is more credible than exact price forecasting.

Q12: What is the best wording for the paper?

Use:

Event-level REMIT analysis shows that the largest price events coincided with both stressed internal market conditions and external asset/interconnector availability constraints.

Avoid:

The outage caused the price spike.

7. Final event-layer conclusion

The event-analysis branch has added a major new layer to the paper.

The research story is now:

Price regimes show where stress forms.

Thresholds show how stress becomes extreme.

Time bands show when stress is amplified.

Regime groups show where annual stress concentrates.

Interconnector analysis shows cross-year differences in flexibility context.

Event-level REMIT analysis shows that the largest price events coincided with real asset and interconnector availability constraints.

That is a much stronger research paper than a simple correlation study.

The next big step is now:

Build 2025 full-year dataset
validate it
apply the same framework
compare 2023–2024–2025
then build scenario labels for 2026/2027 outlook

For 2023–2024, we focused heavily on upper-tail price spikes. But the 2025 validation result is already telling us not to ignore the lower tail.

2025 may become important for:

negative-price frequency
high-wind / low-gas surplus conditions
downward balancing pressure
price volatility around surplus regimes

This does not replace the spike analysis. It expands the paper into both:

scarcity price formation
and
surplus / negative-price formation

“GB imbalance prices form through multiple annual architectures: 2023 Q1 scarcity stress, 2024 late-year physical scarcity, and 2025 mixed-tail behaviour with both January scarcity spikes and frequent negative-price regimes.”

2025 must not be treated as merely a moderate year. Its annual average is lower than 2023, but its maximum event is more extreme.
2025 does not have as many broad £250+ spike periods as 2023, but it has a more severe extreme tail at the £300+ level.
The lower tail became progressively more frequent across the three years, suggesting that surplus/downward-price regimes became more prominent alongside upper-tail scarcity episodes.
2025 looks like a mixed year: lower average price than 2023 but higher than 2024, with both increased negative-price frequency and a severe extreme-price tail.
2025 combines higher average wind and more negative average imbalance with a higher frequency of negative prices, which supports a stronger surplus/downward-price regime. But it also has a severe upper tail, meaning scarcity episodes still occur inside a more renewable/surplus-prone year.

Across 2023–2025, GB imbalance price formation shows a shift from broad scarcity stress toward increasingly mixed-tail behaviour. 2023 had the highest average price and the largest number of £250+/MWh periods, consistent with a broad Q1 scarcity regime. 2024 was quieter overall, with lower average prices and fewer upper-tail events, but late-year physical scarcity still produced concentrated spikes. 2025 had fewer £250+ periods than 2023 but more £300+ periods than either prior year, while also recording the highest number of negative-price periods. This indicates that 2025 combined more frequent surplus/downward-price conditions with a severe upper-tail risk.

From the annual table, 2025 looked like a mixed-tail year. Now we need to prove where that mixed-tail behaviour came from:

January 2025 likely = upper-tail scarcity
June 2025 likely = mixed-tail / dual-tail volatility
September 2025 likely = negative-price dominant
October 2025 likely = transition stress

major_spike_months: Jan, Feb, Mar
total £250+ spikes in major spike months: 111
max price: £1950/MWh

2023 was dominated by Q1 scarcity. This matches our earlier 2023 framework.

Research note:
2023’s spike risk was broad and concentrated early in the year. The year’s main story remains Q1 stress, not a late-year or mixed-tail structure.

quiet_or_normal_months: 5
negative_price_dominant_months: 3
spike_active_months: Oct, Nov, Dec
total £250+ spikes in spike-active months: 24
max price: £669.212/MWh

2024 had no major spike month under this rule, but Q4 activated spike risk.

Research note:
2024 was not broadly stressed. Its upper-tail events were concentrated in late-year transition/winter stress, especially October to December.

major_spike_months: Jan only
mixed_tail_months: Jun and Oct
negative_price_dominant_months: May, Aug, Sep
max price: £2900/MWh

This confirms the earlier interpretation. 2025 is not simply a scarcity year or a quiet year.

It has:

January scarcity shock
June and October mixed-tail volatility
May/Aug/Sep negative-price dominance

Research note:
2025 is a mixed-tail year: it combines a severe upper-tail event structure with more frequent lower-tail negative-price periods.

2. Important comparison across years
Major spike months
2023: 3 months — Jan, Feb, Mar
2024: 0 months
2025: 1 month — Jan

This says:

2023 had the broadest scarcity regime. 2025 had a concentrated January scarcity regime. 2024 did not have a broad major-spike month but still had late-year spike-active months.

Negative-price dominant months
2023: 1 month
2024: 3 months
2025: 3 months

This confirms that negative-price regimes became more prominent after 2023.

Research note:
The lower tail became more structurally important in 2024 and 2025. This supports adding a surplus/negative-price formation section to the paper.

Mixed-tail months
2023: Oct, Dec
2024: none under this label
2025: Jun, Oct

This is important.

2025 has two months where both negative prices and spikes appeared. June is especially interesting because summer months are often thought of as surplus/low-price periods, yet June still produced £250+ and £300+ events.

Research note:
2025 shows that surplus-prone months can still contain scarcity episodes. This is important for any future scenario model.

3. Paper-ready interpretation

You can write:

The monthly comparison shows that annual averages conceal sharply different within-year architectures. In 2023, upper-tail price risk was concentrated in a broad Q1 scarcity regime, with January to March classified as major spike months. In 2024, most months were quiet or negative-price dominated, while upper-tail stress appeared only in late-year spike-active months. In 2025, the structure changed again: January became a major spike month, while June and October displayed mixed-tail behaviour, combining negative-price frequency with upper-tail spike events. This indicates that GB imbalance price formation is increasingly characterised by both scarcity and surplus extremes rather than a single annual stress pattern.

2023 = Q1 compound scarcity architecture
2024 = late-year physical scarcity architecture
2025 = mixed-tail scarcity/surplus architecture

Why this next?

Because monthly comparison tells us when regimes occurred. Price-band comparison tells us what system conditions set each price regime in 2025.

It will answer:

At negative prices in 2025, what were wind, gas, imbalance, interconnectors?
At £100–150 in 2025, what changed?
At £250+ and £300+ in 2025, what were system conditions?

Do negative prices in 2025 occur under high wind, low gas and negative imbalance?

Does the £300+ band occur under very low wind, very high gas, positive imbalance and evening peak?

Is the £250–300 band different from the £300+ band?

Does 2025’s upper tail look more like 2023 Q1, 2024 December, or a new structure?

1. Main 2025 price-band finding

2025 has a very clear two-tail structure:

Negative prices:
high wind
very low gas
strongly negative imbalance
low interconnector levels

Extreme positive prices:
very low wind
very high gas
positive imbalance
high evening-peak share
some low-interconnector exposure

So 2025 is not random. It has a clear surplus regime and a clear scarcity regime.

2. Negative-price regime in 2025

Negative-price band:

periods: 1121
avg_price: -16.4235
avg_imbalance: -506.0298
avg_wind: 11918.355 MW
avg_gas: 3183.7333 MW
avg_interconnectors: 1218.2712 MW
share_imbalance_lt_minus_150: 0.8698
share_wind_gt_10000: 0.6869
share_wind_gt_12000: 0.5112
share_gas_lt_5000: 0.9376
share_evening_peak: 0.0375

This is a very clean surplus fingerprint.

Research note:

Negative prices in 2025 were not just slightly low-price periods. They were structurally different from normal prices: strongly negative imbalance, high wind, very low gas generation, and low evening-peak exposure.

Paper interpretation:

The 2025 negative-price regime was primarily a surplus-balancing regime, characterised by high wind output, low gas generation and strongly negative imbalance. The very low evening-peak share suggests negative prices were not typically formed during demand-tight peak conditions, but during surplus periods.

3. Normal price regime: 0 to 100
periods: 10803
annual_share: 0.6166
avg_price: 66.5475
avg_imbalance: -125.45
avg_wind: 8145.1911 MW
avg_gas: 8310.5946 MW
avg_interconnectors: 3557.4613 MW

This is the dominant 2025 regime.

Research note:

Most 2025 periods sat in the £0–100/MWh range. This regime had moderately negative imbalance, moderate-to-high wind, and moderate gas generation.

This explains why average 2025 price was not as high as 2023, despite the extreme £2900 event.

4. Stress entry: 100 to 150
periods: 5128
annual_share: 0.2927
avg_imbalance: 214.7828
avg_wind: 7128.6866 MW
avg_gas: 10688.1901 MW
share_imbalance_gt_150: 0.5322
share_evening_peak: 0.2713

This is where the market clearly moves from surplus/normal into stress.

Research note:

The £100–150/MWh band is the first clear stress-entry layer in 2025. Average imbalance flips strongly positive, gas generation rises, wind falls, and evening-peak share increases.

This matches what we saw in 2023–2024: crossing above £100 is structurally meaningful.

5. High-stress regime: 150 to 200
periods: 400
avg_imbalance: 289.9667
avg_wind: 5366.2 MW
avg_gas: 18556.475 MW
share_gas_gt_15000: 0.7625
share_gas_gt_20000: 0.5175
share_evening_peak: 0.47

This band is a real scarcity regime.

Research note:

By £150–200/MWh, 2025 prices are clearly associated with high gas generation, lower wind, positive imbalance and a much higher evening-peak share.

This is the transition from broad stress to scarcity pricing.

6. Near-spike regime: 200 to 250
periods: 26
avg_imbalance: 387.2849
avg_wind: 2948.4231 MW
avg_gas: 21871.8846 MW
share_wind_lt_8000: 1.0
share_gas_gt_15000: 0.9231
share_gas_gt_20000: 0.8077
share_evening_peak: 0.5385

This is a very strong near-spike fingerprint.

Research note:

Near-spikes in 2025 already had very low wind, very high gas and strongly positive imbalance. They were not normal periods that randomly failed to spike; they were stressed scarcity states.

This mirrors the earlier spike-vs-near-spike work.

7. Spike regime: 250 to 300
periods: 15
avg_imbalance: 261.6613
avg_wind: 2901.4667 MW
avg_gas: 20910.8 MW
share_wind_lt_8000: 1.0
share_gas_gt_15000: 0.8
share_gas_gt_20000: 0.8
share_evening_peak: 0.6667

This looks very similar to the near-spike regime.

Research note:

The £250–300/MWh band in 2025 is scarcity-driven, but its average imbalance is lower than the £200–250 band. This suggests the final move into spike territory was not purely imbalance magnitude; low wind, high gas and timing also mattered.

8. Extreme spike regime: 300+
periods: 27
avg_price: 1296.0599
max_price: 2900
avg_imbalance: 289.4384
avg_wind: 3034.1111 MW
avg_gas: 22843.9259 MW
share_wind_lt_8000: 1.0
share_wind_lt_3000: 0.7037
share_gas_gt_15000: 0.8519
share_gas_gt_20000: 0.8148
share_evening_peak: 0.6296
share_interconnectors_lt_2500: 0.4074

This is one of the most important 2025 results.

Extreme spikes were almost entirely:

low-wind
high-gas
positive-imbalance
often evening-peak
sometimes lower-interconnector-support

Research note:

The 2025 £300+ regime is a severe scarcity regime. Every £300+ period occurred with wind below 8000 MW, more than 70% occurred with wind below 3000 MW, and more than 81% occurred with gas above 20000 MW.

This is very strong.

9. Important 2025 transition pattern

The progression is very clear:

negative:
imbalance -506, wind 11918, gas 3184

0_to_100:
imbalance -125, wind 8145, gas 8311

100_to_150:
imbalance +215, wind 7129, gas 10688

150_to_200:
imbalance +290, wind 5366, gas 18556

200_to_250:
imbalance +387, wind 2948, gas 21872

250_to_300:
imbalance +262, wind 2901, gas 20911

300_plus:
imbalance +289, wind 3034, gas 22844

So the structural movement is:

surplus → normal → positive imbalance stress → low-wind/high-gas scarcity → extreme scarcity

Research note:

2025 confirms that price bands represent distinct system states, not arbitrary price buckets.

10. What this adds to the 2023–2025 story

2025 now has a very clean interpretation:

Negative-price side:
high-wind, low-gas, negative-imbalance surplus regime

Upper-tail side:
low-wind, high-gas, positive-imbalance scarcity regime

Annual structure:
mixed-tail year because both regimes occurred frequently enough to matter

Paper-ready sentence:

The 2025 price-band structure shows a pronounced bifurcation between surplus and scarcity regimes. Negative prices were associated with high wind output, low gas generation and strongly negative imbalance, while £300+/MWh periods were associated with uniformly low wind, high gas generation, positive imbalance and elevated evening-peak exposure. This confirms that 2025 was a mixed-tail year, combining frequent surplus pricing with severe scarcity episodes.

1. Big result: the three-year price-setting structure is now visible

Across 2023–2025, the price bands show a consistent broad pattern:

negative prices
= high wind + low gas + strongly negative imbalance

£0–100
= normal / softer system state

£100–150
= stress-entry regime

£150–200
= high-stress regime

£200–250
= near-spike scarcity regime

£250–300
= ordinary spike regime

£300+
= extreme scarcity regime

But the strength of each layer differs by year.

That is exactly what this paper is about.

2. Negative-price regime: increasingly important lower tail

Negative-price periods:

2023: 849
2024: 1,073
2025: 1,121

Negative-price annual share:

2023: 4.85%
2024: 6.11%
2025: 6.40%

Negative-price fingerprints are very consistent:

2023 avg wind: 11,943.7 MW | avg gas: 3,552.8 MW | avg imbalance: -448.5
2024 avg wind: 11,604.4 MW | avg gas: 2,900.8 MW | avg imbalance: -415.9
2025 avg wind: 11,918.4 MW | avg gas: 3,183.7 MW | avg imbalance: -506.0

Research note:

Negative prices form under a very stable surplus fingerprint across all three years: high wind, very low gas and strongly negative imbalance. What changes is frequency: the lower tail becomes more frequent from 2023 to 2025.

Paper interpretation:

The lower tail is not random volatility. It is a repeated surplus-balancing regime that became more frequent after 2023.

3. Normal regime: £0–100 dominates, but less so in 2023

Annual share of £0–100:

2023: 48.21%
2024: 69.42%
2025: 61.66%

This is important:

2024 had the largest normal-price share.
2023 had the smallest normal-price share.
2025 sat between them.

Research note:

The very large £0–100 share in 2024 helps explain why 2024 had the lowest average annual price and the quietest broad upper-tail profile.

4. Stress-entry regime: £100–150

Annual share of £100–150:

2023: 30.50%
2024: 23.59%
2025: 29.27%

Average imbalance in this band:

2023: +151.4
2024: +229.6
2025: +214.8

Research note:

The £100–150 band is the first clear stress-entry layer across all three years. It is where average imbalance turns positive and gas generation rises relative to normal prices.

This supports our earlier conclusion:

crossing £100/MWh is a real structural transition
5. High-stress regime: £150–200

This band is where 2024 and 2025 become more thermally intense than 2023.

Average gas in £150–200:

2023: 11,625 MW
2024: 19,968 MW
2025: 18,556 MW

Share gas > 15,000 MW:

2023: 0.2977
2024: 0.8852
2025: 0.7625

Research note:

In 2024 and 2025, prices above £150 were much more tightly linked to high gas generation than in 2023. This suggests upper-tail stress became more thermally concentrated after 2023.

This is a strong cross-year finding.

6. Near-spike regime: £200–250

Average wind:

2023: 7,491.6 MW
2024: 2,695.2 MW
2025: 2,948.4 MW

Average gas:

2023: 14,318.4 MW
2024: 23,071.3 MW
2025: 21,871.9 MW

Share wind < 8,000 MW:

2023: 0.5916
2024: 1.0000
2025: 1.0000

Research note:

Near-spikes in 2024 and 2025 were already severe low-wind/high-gas states. In 2023, near-spikes were stressed but less physically extreme on average.

This is important because it says:

2024/2025 near-spikes were scarcity states that did not always convert into extreme spikes
7. Ordinary spike regime: £250–300

Average gas:

2023: 18,833.1 MW
2024: 24,537.0 MW
2025: 20,910.8 MW

Share wind < 8,000 MW:

2023: 0.8182
2024: 1.0000
2025: 1.0000

Share evening peak:

2023: 0.6566
2024: 0.4286
2025: 0.6667

Research note:

The £250–300 band is low-wind/high-gas dominated in all three years, but the timing layer differs. 2023 and 2025 have stronger evening-peak association than 2024.

8. Extreme spike regime: £300+

This is probably the most important upper-tail comparison.

£300+ periods:

2023: 21
2024: 17
2025: 27

Maximum price:

2023: £1950
2024: £669.212
2025: £2900

Average gas:

2023: 20,037.5 MW
2024: 24,821.9 MW
2025: 22,843.9 MW

Average wind:

2023: 5,293.5 MW
2024: 1,676.7 MW
2025: 3,034.1 MW

Share wind < 8,000 MW:

2023: 0.9048
2024: 1.0000
2025: 1.0000

Share gas > 20,000 MW:

2023: 0.7143
2024: 0.8824
2025: 0.8148

Share evening peak:

2023: 0.8571
2024: 0.4706
2025: 0.6296

Research note:

The extreme-spike regime is low-wind/high-gas dominated in all three years, but the shape differs. 2023 extreme spikes were most evening-peak concentrated. 2024 extreme spikes were the most physically severe in terms of low wind and high gas. 2025 had the most £300+ periods and the highest maximum price, suggesting a severe but more mixed extreme-tail structure.

2023:
Broad scarcity year.
High average price.
Many £250+ events.
Extreme spikes strongly evening-peak concentrated.

2024:
Quiet normal-price year for most periods.
Upper tail was rare but highly physical: very low wind and very high gas.
Stress concentrated late in the year.

2025:
Mixed-tail year.
Most negative-price periods.
More £300+ periods than 2023 or 2024.
Highest maximum price.
Extreme scarcity coexisted with frequent surplus pricing.

The three-year price-band comparison shows that GB imbalance prices are set through repeated but year-specific system states. Negative prices form consistently under high-wind, low-gas and strongly negative-imbalance conditions, with their frequency increasing from 2023 to 2025. The £100–150/MWh band marks a transition into positive-imbalance stress, while prices above £150/MWh increasingly reflect low-wind, high-gas scarcity. Extreme £300+/MWh prices are low-wind/high-gas dominated in all years, but the timing and severity differ: 2023 was most evening-peak concentrated, 2024 was most physically severe in low-wind/high-gas terms, and 2025 combined frequent negative-price periods with the largest single price event and the highest number of £300+/MWh periods.

Main transition findings
1. Negative → normal price transition is consistent across all years
2023: imbalance +263, wind -4713, gas +5820
2024: imbalance +340, wind -3963, gas +4924
2025: imbalance +381, wind -3773, gas +5127

This is very clean.

Research note:
The movement out of negative prices is consistently driven by a shift away from surplus conditions: imbalance becomes much less negative, wind falls sharply, and gas generation rises strongly.

Paper meaning:
Negative prices are not isolated anomalies. They sit at the bottom of a structured surplus regime, and the exit from that regime is marked by lower wind, higher gas and less negative imbalance.

2. £0–100 → £100–150 is the main stress-entry transition
2023: imbalance +336, gas +1498
2024: imbalance +305, gas +3223
2025: imbalance +340, gas +2378

This confirms our earlier finding across all three years.

Research note:
The £100/MWh threshold is structurally meaningful. Across 2023, 2024 and 2025, moving above £100 corresponds to a large positive shift in imbalance and a rise in gas generation.

Paper meaning:
The £100–150 band should be treated as the first stress-entry regime, not merely a higher normal-price band.

3. £100–150 → £150–200 differs strongly by year
2023: wind +1410, gas +754
2024: wind -2542, gas +8920
2025: wind -1762, gas +7868

This is a major cross-year contrast.

Research note:
In 2024 and 2025, the move into £150–200 is a clear physical scarcity transition: wind falls sharply and gas rises sharply. In 2023, this transition is less physically scarcity-like and may reflect a different stress structure, with imbalance and pricing conditions playing a larger role.

Paper meaning:
After the first stress-entry layer, the pathway into higher stress is not identical across years. 2024 and 2025 become much more thermally dominated above £150.

4. £150–200 → £200–250 is especially severe in 2025
2023: wind -579, gas +2693, imbalance +63
2024: wind -1469, gas +3104, imbalance -18
2025: wind -2418, gas +3315, imbalance +97

2025 has the largest wind drop and strong gas increase here.

Research note:
The 2025 move from high stress into near-spike territory shows a very clear scarcity escalation: wind falls sharply, gas rises, and imbalance increases.

Paper meaning:
2025’s near-spike regime was not accidental. It emerged from a strong low-wind/high-gas transition.

5. £200–250 → £250–300 is not always a simple escalation
2023: wind -1990, gas +4515, evening share +0.354
2024: imbalance -118, wind -581, gas +1466
2025: imbalance -126, wind -47, gas -961

This is important.

Research note:
In 2023, moving from near-spike to £250–300 was a clear scarcity and timing escalation: wind fell sharply, gas rose sharply, and evening-peak share jumped. In 2024 and 2025, this transition is less straightforward, suggesting the £250–300 band may not be the final scarcity layer in those years.

Paper meaning:
The simple assumption that every higher band means every driver increases is wrong. The route into ordinary spike prices differs by year.

6. £250–300 → £300+ is the extreme-tail separator

This is the most important upper-tail transition.

2023: price +237, gas +1204, evening share +0.201, imbalance -44
2024: price +175, imbalance +253, wind -438, interconnectors -852
2025: price +1024, gas +1933, imbalance +28

Research note:
The final step into £300+ differs across years:

2023: stronger evening-peak concentration and higher gas
2024: large imbalance escalation plus falling wind and lower interconnector support
2025: very large price escalation with further gas increase, but without a big evening/timing increase

Paper meaning:
Extreme price formation is year-specific. The final extreme-tail jump is not caused by one universal driver.

Big paper conclusion from this table

This table supports one of your strongest arguments:

GB imbalance price formation is regime-dependent and transition-dependent. The market does not move from normal prices to spikes through one fixed pathway. Instead, different years show different escalation routes: 2023 relied more on evening-peak amplification and Q1 compound scarcity; 2024’s upper tail was more physical and interconnector-sensitive; 2025 combined surplus regimes with sharp scarcity jumps, including the largest maximum price in the sample.

How this fits the paper structure

This table belongs under:

B. Stress transition
C. Spike realization
D. Dynamic formation

Specifically:

Price-band table = what each price regime looks like
Transition table = how the system moves between regimes
Event/REMIT table = what external constraints coincided with major episodes

That is a strong methodological chain.

Core interpretation
1. Broad stress is highest in 2023

For price >= 100:

2023: 8220 periods, probability 0.4694
2024: 4299 periods, probability 0.2447
2025: 5596 periods, probability 0.3194

So 2023 had the broadest elevated-price environment. 2024 was much quieter, and 2025 sat in between.

2. 2024 and 2025 become physically severe much faster

At price >= 200, wind and gas conditions become very extreme:

2024: avg_wind 2047 MW, avg_gas 24284 MW
2025: avg_wind 2972 MW, avg_gas 22046 MW
2023: avg_wind 7151 MW, avg_gas 15111 MW

This is important. It means 2024 and 2025 did not have as much broad stress as 2023, but when prices did move high, they moved under much more severe low-wind/high-gas conditions.

3. 2025 has the strongest extreme-tail count

For price >= 300:

2023: 21 periods
2024: 17 periods
2025: 27 periods

So 2025 has the highest number of £300+ periods, even though 2023 has the highest number of £250+ periods.

4. Evening peak differs by year

At price >= 300:

2023: share_evening_peak 0.8571
2024: share_evening_peak 0.4706
2025: share_evening_peak 0.6296

This supports the idea that 2023 extreme prices were especially evening-peak amplified, while 2024 and 2025 extreme prices were more physically scarcity-driven and less purely evening-centred.

Research note

This table strengthens the main Paper 1 argument:

Price severity layers are not arbitrary. As the threshold rises, the market moves from broad stress into physical scarcity, but the pathway differs by year. 2023 shows broad and evening-amplified scarcity; 2024 shows rare but highly physical scarcity; 2025 shows a mixed-tail year with the highest extreme-price count.

Main interpretation
1. Evening peak is still the main 2025 risk window

At price >= 250:

evening_peak: 27 periods out of 42 total £250+ periods

That means:

64.3% of 2025 £250+ periods occurred during evening peak

At price >= 300:

evening_peak: 17 periods out of 27 total £300+ periods

That means:

63.0% of 2025 £300+ periods occurred during evening peak

So 2025 is clearly evening-amplified, but not exclusively evening-driven.

Research note:
2025 sits between 2023 and 2024. It is not as evening-dominated as 2023, but evening peak remains the most important time-band for extreme prices.

2. No night-time severe price events

At price >= 200, >=250, and >=300:

night: 0 periods

This is very clean.

Research note:
Night-time periods can move above £100 and £150, but the severe scarcity layers in 2025 did not occur overnight.

Paper meaning:
Severe 2025 price formation required more than low wind/high gas alone; it also needed demand/timing pressure.

3. Morning, midday and afternoon still matter for 2025 extremes

At price >= 300:

morning_ramp: 3 periods
midday: 4 periods
afternoon: 3 periods
evening_peak: 17 periods
late_evening: 0 periods

This matters because the 2025 extreme tail was not purely a classic evening-peak story.

Research note:
The existence of morning, midday and afternoon £300+ periods suggests that some 2025 extreme events were linked to broader scarcity or asset availability conditions, not just evening demand peak.

This will be important when we later investigate the January 2025 £2900 event.

4. Evening peak has the highest £250+ and £300+ probability

For price >= 250:

evening_peak probability: 0.0092
afternoon probability: 0.0027
midday probability: 0.0024
morning_ramp probability: 0.0010
late_evening probability: 0.0003
night probability: 0.0000

For price >= 300:

evening_peak probability: 0.0058
afternoon probability: 0.0021
midday probability: 0.0014
morning_ramp probability: 0.0010
night / late_evening: 0.0000

This confirms timing amplification.

Research note:
Evening peak is the highest-risk window for 2025 upper-tail pricing, but midday and afternoon events show that structural scarcity can also break through outside evening peak.

5. Physical scarcity is present across all severe time bands

At price >= 300, every non-empty time band has:

share_wind_lt_8000 = 1.0
share_gas_gt_15000 = 1.0
share_gas_gt_20000 = 1.0

For:

morning_ramp
midday
afternoon
evening_peak

That is very strong.

Research note:
The 2025 £300+ regime is physically scarce across time bands. Timing changes the probability, but low wind and high gas are universal features of the severe-price state.

6. Evening peak £300+ events are more imbalance-driven

At price >= 300:

evening_peak avg_imbalance: 378.1113
morning_ramp avg_imbalance: 125.1578
midday avg_imbalance: 135.5916
afternoon avg_imbalance: 156.3681

This is important.

Research note:
Evening-peak extreme events in 2025 were much more imbalance-stressed than non-evening extreme events. This suggests that evening peak acts as an imbalance amplifier on top of the physical scarcity background.

Paper wording:

In 2025, extreme prices outside evening peak still occurred under low-wind/high-gas scarcity, but evening-peak extreme prices were associated with much stronger positive imbalance.

Paper-ready interpretation

The 2025 threshold-by-time-band analysis shows that timing remained a major amplifier of upper-tail price formation. Evening peak accounted for 64.3% of £250+/MWh periods and 63.0% of £300+/MWh periods, despite representing only one of six time bands. No £200+/MWh events occurred overnight. However, £300+/MWh events also appeared during morning ramp, midday and afternoon periods, indicating that the 2025 extreme tail was not purely an evening-peak phenomenon. Across all non-empty £300+/MWh time bands, wind generation was below 8000 MW and gas generation exceeded 20000 MW, confirming a physical scarcity background. Evening-peak extreme events were distinguished by substantially higher positive imbalance, suggesting that timing amplified scarcity through imbalance pressure.

Initial interpretation from what we have
1. Evening peak is consistently the highest-risk window

At price >= 250:

2023 evening_peak: 83 periods, probability 0.0284
2024 evening_peak: 11 periods, probability 0.0038
2025 evening_peak: 27 periods, probability 0.0092

So:

2023 had the strongest evening-peak spike risk
2024 had much lower spike risk
2025 returned to stronger evening-peak risk than 2024, but still below 2023

This fits the paper story perfectly.

2. Night is not an important severe-price window

At price >= 300:

2023 night: 0 periods
2024 night: 0 periods
2025 night: 0 periods

At price >= 250:

2023 night: 2 periods
2024 night: 0 periods
2025 night: 0 periods

Research note:

Night periods can enter mild or moderate stress, but extreme scarcity pricing is not normally a night-time phenomenon in this sample.

3. 2023 was most evening-dominated

At price >= 300:

2023 evening_peak: 18 out of 21 £300+ periods

That is:

85.7%

This confirms our earlier finding that 2023 extreme spikes were highly evening-peak amplified.

4. 2024 was less evening-dominated

At price >= 300:

2024 morning_ramp: 5
2024 midday: 3
2024 afternoon: 1
2024 evening_peak: 8
2024 late_evening: 0
2024 night: 0

So 2024 had a more spread-out extreme tail, even though evening peak still had the highest single count.

Research note:

2024’s extreme-price events were not purely evening-driven. This supports the idea that 2024 upper-tail events were more physically scarcity-driven across selected periods.

5. 2025 sits between 2023 and 2024

From the previous 2025 table:

2025 £300+:
morning_ramp: 3
midday: 4
afternoon: 3
evening_peak: 17
late_evening: 0
night: 0

So:

2025 is less evening-dominated than 2023,
but more evening-concentrated than 2024.

This is a strong cross-year timing conclusion.

Paper-ready interpretation

The threshold-by-time-band comparison shows that timing acts as an amplifier rather than a standalone cause of extreme imbalance prices. Evening peak is the dominant high-risk window across all three years, particularly in 2023 where 18 of 21 £300+/MWh periods occurred during the evening peak. However, 2024 and 2025 also show morning, midday and afternoon extreme-price periods, indicating that severe physical scarcity can break through outside the evening peak. Night-time periods do not contribute materially to the extreme tail, with no £300+/MWh night events in any year.

Across 2023–2025, evening peak remained the most important high-risk window for upper-tail imbalance prices, but the degree of timing concentration varied by year. The 2023 extreme tail was highly evening-peak dominated, while 2024 and 2025 also produced morning, midday and afternoon extreme-price periods, indicating that physical scarcity can override normal timing patterns when system conditions are sufficiently tight.

2025 is not one simple year. It has seven internal regimes:

1. jan_spike_stress
2. feb_mar_broad_stress
3. apr_may_surplus_shift
4. jun_mixed_tail
5. jul_sep_surplus
6. oct_mixed_transition
7. nov_dec_quiet
Key interpretation
1. January = main upper-tail shock regime
rows: 1488
avg_price: 123.8734
max_price: 2900
£250+ periods: 23
£300+ periods: 19

January alone produced:

23 of 42 total £250+ periods
19 of 27 total £300+ periods

So January is the main 2025 extreme-price regime.

Research note:
The 2025 extreme tail is heavily concentrated in January, especially for £300+ events.

2. February–March = broad stress without spike realization
£100+ periods: 1249
£150+ periods: 172
£250+ periods: 0
£300+ periods: 0

This is important.

It shows stress existed, but it did not convert into spikes.

Research note:
February–March had broad elevated-price conditions but lacked the final scarcity trigger needed for £250+/£300+ realization.

3. April–May = surplus shift
negative periods: 239
£250+ periods: 0
avg_gas: 7058.388
avg_wind: 5968.8268

This is the transition away from winter stress into lower-price/surplus conditions.

Research note:
April–May marks the shift from broad stress into surplus/downward-price structure.

4. June = mixed-tail regime
negative periods: 227
£250+ periods: 6
£300+ periods: 4
max_price: 423.85

This is a key 2025 finding.

June had both:

high negative-price exposure
and
renewed upper-tail spike activity

Research note:
June is one of the clearest examples of mixed-tail volatility: surplus conditions and spike events occurring in the same regime period.

5. July–September = surplus-heavy summer
negative periods: 361
£250+ periods: 1
£300+ periods: 0
avg_gas: 7091.9099

This is mainly a lower-tail/surplus regime.

Research note:
July–September was not a major scarcity regime. It was mostly surplus-heavy, with limited upper-tail activity.

6. October = mixed transition
negative periods: 100
£250+ periods: 12
£300+ periods: 4
max_price: 487

October is very important because it looks like an autumn transition stress month.

Research note:
October 2025 combines negative-price exposure with renewed upper-tail stress. This makes it comparable to a mixed transition regime rather than a simple quiet month.

7. November–December = quiet late-year regime
£250+ periods: 0
£300+ periods: 0
negative periods: 51
avg_wind: 11282.237
max_price: 247.3104

This is surprising and useful.

Unlike 2024, where December was a stress month, 2025 finished quietly.

Research note:
Late 2025 did not repeat the 2024 December stress pattern. High wind and softer upper-tail conditions suppressed spike realization.

Main paper conclusion from this table

This is the clean sentence:

The 2025 regime fingerprint shows a mixed-tail annual architecture. January dominated the extreme upper tail, June and October produced mixed-tail volatility, July–September were surplus-heavy, and November–December were comparatively quiet. This differs from 2023’s broad Q1 scarcity structure and 2024’s late-year physical scarcity structure.

1. 2023: Q1 compound scarcity architecture

The main stress regime is:

2023_q1_compound_scarcity

Key figures:

rows: 4314
avg_price: 132.5373
max_price: 1950
£250+ periods: 111
£300+ periods: 18

Out of the full 2023 total:

2023 total £250+ periods: 120
2023 Q1 £250+ periods: 111

So:

92.5% of 2023 £250+ periods occurred in Q1

And:

2023 total £300+ periods: 21
2023 Q1 £300+ periods: 18

So:

85.7% of 2023 £300+ periods occurred in Q1
Interpretation

2023 was not evenly stressed across the year. It was dominated by a Q1 compound scarcity block.

Paper wording:

The 2023 upper tail was concentrated in a Q1 compound scarcity regime, which contained 92.5% of annual £250+/MWh periods and 85.7% of annual £300+/MWh periods.

2. 2024: late-year physical scarcity architecture

The main stress regimes are:

2024_oct_nov_transition
2024_dec_physical_scarcity

December is especially important:

2024_dec_physical_scarcity
rows: 1488
avg_price: 86.2649
max_price: 590.4504
£250+ periods: 14
£300+ periods: 11

Out of 2024 total:

2024 total £250+ periods: 24
December £250+ periods: 14

So:

58.3% of 2024 £250+ periods occurred in December

And:

2024 total £300+ periods: 17
December £300+ periods: 11

So:

64.7% of 2024 £300+ periods occurred in December
Interpretation

2024 was quiet for most of the year, but the upper tail returned late in the year.

Paper wording:

Unlike 2023, 2024 did not show broad Q1 scarcity. Its upper-tail risk was concentrated in late-year transition and December physical scarcity regimes.

3. 2025: mixed-tail scarcity/surplus architecture

The 2025 structure is more complex.

Main upper-tail regime:

2025_jan_spike_stress

Key figures:

rows: 1488
avg_price: 123.8734
max_price: 2900
£250+ periods: 23
£300+ periods: 19

Out of 2025 total:

2025 total £250+ periods: 42
January £250+ periods: 23

So:

54.8% of 2025 £250+ periods occurred in January

And:

2025 total £300+ periods: 27
January £300+ periods: 19

So:

70.4% of 2025 £300+ periods occurred in January

But 2025 also has mixed-tail regimes:

2025_jun_mixed_tail:
negative periods: 227
£250+ periods: 6
£300+ periods: 4

2025_oct_mixed_transition:
negative periods: 100
£250+ periods: 12
£300+ periods: 4
Interpretation

2025 was not a broad scarcity year like 2023 and not only a late-year physical scarcity year like 2024. It combined:

January upper-tail shock
June mixed-tail volatility
summer surplus conditions
October mixed transition
quiet November–December

Paper wording:

2025 shows a mixed-tail architecture. The extreme upper tail was concentrated in January, while June and October combined negative-price exposure with renewed spike activity. This makes 2025 structurally different from both 2023 and 2024.

4. Important contrast: December 2024 vs November–December 2025

This is a strong finding.

2024_dec_physical_scarcity:
£250+ periods: 14
£300+ periods: 11
max price: 590.4504

2025_nov_dec_quiet:
£250+ periods: 0
£300+ periods: 0
max price: 247.3104

So late-year conditions did not repeat.

Paper note:

December stress was not structurally persistent year-to-year. December 2024 was a physical scarcity regime, while November–December 2025 was a quiet high-wind regime with no £250+/MWh realization.

5. Paper-ready architecture paragraph

You can use this later:

The regime fingerprint comparison shows that GB imbalance price formation differed structurally across the thre

Key research finding from this table

For 2025, the strongest price-stress evidence is concentrated around:

8 January 2025
20 January 2025
22 January 2025
30 June 2025
1 July 2025
13–15 October 2025
22 October 2025

These are the most important candidate dates for external checks.

Very important observation

The table shows that some events are duplicated across event types.

Example:

2025_extreme_spike_cluster_2
2025_positive_spike_cluster_2
2025_large_upward_jump_366
2025_large_downward_reversal_374

All relate to the same major price episode on 8 January 2025.

That is not wrong. It means the same episode had:

extreme spike behaviour
positive spike behaviour
large upward jump behaviour
large downward reversal behaviour

So for the paper, we should not treat every row as a separate case study. We need to group them into event windows.

The main event windows to study
1. 8 January 2025: primary extreme spike case

This is the strongest event in the full 2025 dataset.

Key facts:

Max price: £2900/MWh
Main cluster: 14:30–18:30
Average price in cluster: ~£2644/MWh
Average gas: ~25,003 MW
Average wind: ~2,575 MW
Average imbalance: ~329 MWh

Paper interpretation:

The 8 January 2025 episode represents the clearest 2025 upper-tail stress event, combining very high gas generation, very low wind output and positive system imbalance. The event also showed sharp intraday price discontinuity, with prices moving from £600/MWh to £2900/MWh and later reversing sharply.

2. 20 January 2025: evening scarcity event

Key facts:

Max price: ~£678/MWh
Time: 16:30–17:30
Time band: evening peak
Average gas: ~26,911 MW
Average wind: ~2,143 MW
Interconnectors: ~1,909 MW

Paper interpretation:

The 20 January event shows a more conventional evening scarcity pattern: low wind, very high gas generation and lower interconnector support during the evening peak.

3. 22 January 2025: morning ramp scarcity event

Key facts:

Max price: £450/MWh
Time: 06:30–07:00
Time band: morning ramp
Average wind: ~115 MW
Average gas: ~25,772 MW

This is important because wind was extremely low.

Paper interpretation:

The 22 January event illustrates that scarcity conditions were not limited to evening peaks. Morning ramp periods also produced extreme pricing when wind output was exceptionally low and gas generation was already very high.

4. 30 June 2025: mixed-tail event

Key facts:

Max price: £423.85/MWh
Time: 17:00–18:30
Regime: jun_mixed_tail
Average imbalance: ~657 MWh
Average interconnectors: ~1,040 MW

This one is very important for the 2025 story because it is not just gas/wind. The imbalance and low interconnector support matter strongly.

Paper interpretation:

The 30 June event supports the mixed-tail interpretation of 2025. It occurred outside the January stress regime and was driven by strong positive imbalance, low wind and reduced interconnector support.

5. October 2025: renewed autumn stress

Important dates:

13 October 2025
14 October 2025
15 October 2025
22 October 2025

These show that stress returned in autumn, but not as strongly as January.

Paper interpretation:

October 2025 marked a renewed mixed-transition phase, with several short upper-tail events linked to low wind, high gas and positive imbalance conditions.

This means we now have a strong shortlist for the paper:

8 positive / near-spike cases
Jan 8 extreme £2900/MWh event
Jan 20 scarcity spike
Jan 22 morning ramp scarcity
Jun 30 mixed-tail spike
Jul 1 near-spike
Oct 13 autumn spike
Oct 14 evening spike
Oct 22 evening spike
4 negative-price cases
Mar 30 negative cluster
Apr 5 negative cluster
Jun 22 negative cluster
Sep 6 negative cluster

This is very useful because the paper can now say:

The 2025 extension shows a mixed-tail system architecture: upper-tail scarcity events remained concentrated around low-wind/high-gas/positive-imbalance episodes, while lower-tail negative-price clusters became increasingly visible under high-wind/negative-imbalance/surplus conditions.

Now the next step is to create a paper-ready case-study interpretation table. This will convert your technical case-window table into a clean table with:

case label
event type
price behaviour
internal driver summary
regime meaning
paper interpretation

This is now a paper-ready case-study table. It separates 2025 into:

Positive upper-tail cases

Jan 8 extreme spike — main 2025 shock case
Jan 20 evening scarcity
Jan 22 morning ramp scarcity
Jun 30 mixed-tail summer spike
Jul 1 near-spike continuation
Oct 13 autumn spike
Oct 14 evening spike
Oct 22 evening spike

Negative lower-tail cases

Mar 30 negative-price cluster
Apr 5 negative-price cluster
Jun 22 negative-price cluster
Sep 6 negative-price cluster
Key paper finding from this table

For 2025, the market did not behave like a simple scarcity-only year.

It had a mixed-tail structure:

January = major upper-tail scarcity stress
Spring/summer = strong negative-price/lower-tail exposure
June = both negative-price risk and positive spike risk
October = renewed upper-tail transition stress
Nov-Dec = comparatively quieter despite some near-stress events

It confirms that 2025 REMIT evidence should not be presented as “one outage caused one price spike.” Instead, your result says:

All 12 2025 case-study windows occurred during a repeated external availability background.

That means the REMIT layer is useful, but it is a structural/contextual layer, not the primary causal explanation.

What this means in simple terms

Your internal market data is still the main explanation:

wind + gas generation + imbalance + interconnectors + time band

The REMIT data adds this extra layer:

During those stressed price windows, GB also had repeated material asset availability issues across major generation/interconnector/storage/consumption-related assets.

But because many assets appear repeatedly across the year, we cannot say:

DRAX caused this spike.
NGIFA caused this spike.
KGL caused this spike.

Instead, we say:

These price events occurred against a repeated external availability background, which may have reinforced scarcity or surplus conditions, but the event-level price formation is still best explained by internal market regime conditions.

That is academically much safer.

Important conclusion from your result

Because the classification count is:

repeated_background_external_context    12

Your paper can now say:

Across all twelve selected 2025 case-study windows, REMIT filtering identified repeated material availability events. However, the dominant assets recurred across multiple case windows rather than appearing uniquely in one event. This indicates that REMIT evidence should be interpreted as a persistent external availability backdrop rather than direct single-event causality.

This is a strong methodological finding.

How to use this in the paper

Use it as a separate subsection:

External availability context from REMIT

Suggested wording:

The REMIT overlay was used to test whether selected price-event windows coincided with material asset availability events. The analysis found that all twelve 2025 case-study windows had material REMIT context after filtering for high- and medium-materiality events. However, the dominant REMIT assets appeared repeatedly across multiple case windows. This means the REMIT evidence does not support a simple one-event, one-outage causal explanation. Instead, it suggests that 2025 imbalance price stress occurred against a repeated external availability background, while the immediate price formation remained primarily linked to internal system conditions such as low wind, high gas generation, net imbalance, interconnector support and time-of-day demand stress.

This is the clean academic interpretation.

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