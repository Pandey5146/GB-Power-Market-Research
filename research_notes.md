# GB POWER MARKET RESEARCH

---

## 1. Research Definition

### Title

A Data-Driven Study of Great Britain Electricity Prices and Fuel Mix: Comparing Batteries with Other Fuel Types (2023–2025)

### Aim

To analyse how different fuel types and system conditions influence electricity prices in Great Britain, and to compare the role of batteries with other generation sources.

### Research Question

How do generation mix and system conditions affect electricity prices in Great Britain, and how do batteries compare with other fuel types in this relationship?

### Scope

* Region: Great Britain
* Time Period: 2023–2025
* Resolution: Half-hourly

---

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
---

## 5. Findings

### Early Observations
- The first merged market table was created successfully
- It contains fuel generation, system prices, and imbalance volume
- Price values vary sharply across half-hours, including negative and high positive values
- This suggests strong intra-day market volatility even within a single day

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
---

## 7. Policy Notes

(To be filled)
