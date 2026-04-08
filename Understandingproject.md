Q: Why do we use requests?
👉 To send HTTP requests and fetch data from APIs.

Q: Why pandas?
👉 To convert raw data into structured tables and analyze it.

Q: What is a GET request?
👉 A request to retrieve data from a server.

Q: What is JSON?
👉 A structured format for data exchange (like a Python dictionary).

Q: Why use json_normalize?
👉 To flatten nested JSON into a tabular format.

Q: Why do we check shape?
A: To understand dataset size and confirm data was loaded correctly.

🟢 Main generation types
Code	Meaning
CCGT	Gas (Combined Cycle Gas Turbine)
OCGT	Gas (Open Cycle – peaking)
COAL	Coal
NUCLEAR	Nuclear
BIOMASS	Biomass
OIL	Oil
WIND	Wind

🔵 Hydro & storage
Code	Meaning
NPSHYD	Hydro
PS	Pumped Storage (VERY important for batteries comparison)

🟡 Interconnectors (imports/exports)
Code	Meaning
INTELEC	Interconnector
INTEW	Interconnector
INTFR	France
INTIFA2	IFA2
INTIRL	Ireland
INTNED	Netherlands
INTNEM	Nemo
INTNSL	North Sea Link

Q1. Why do we group fuel types?

👉 To simplify analysis and make results interpretable.

Q2. Why combine CCGT and OCGT?

👉 Both are gas-based generation with similar price behaviour.

Q3. Why treat interconnectors as one group?

👉 Because they represent cross-border flows rather than domestic generation.

Q4. Why keep pumped storage separate?

👉 Because it behaves like storage and is important for flexibility analysis.

Q5. Why not keep all 18 categories?

👉 Too granular → noisy analysis, harder interpretation

Q1. What is a pivot table?

👉 A transformation that reshapes data from long format to wide format.

Q2. Why do we use startTime as index?

👉 Because time is the primary key for analysis.

Q3. Why use fuelType as columns?

👉 To compare different fuels side-by-side.

Q4. Why use sum?

👉 To safely aggregate any duplicate entries.

Q1. What did the pivot achieve?

A: It transformed long-format fuel data into a wide-format table with one row per timestamp.

Q2. Why is wide format better here?

A: It makes time-series analysis, regression, SQL storage, and Power BI reporting much easier.

Q3. Why might some values be negative?

A: Because some categories represent directional flows or storage charging/discharging.

Q4. Why do we care about startTime so much?

A: Because it is the time key that links all future datasets together

Q1. Why combine CCGT and OCGT into gas_gen?

A: Because both are gas-based fuels and are better analysed together at this stage.

Q2. Why keep pumped_storage separate?

A: Because it behaves like storage and is analytically important for flexibility comparisons.

Q3. Why create df_clean?

A: To move from raw engineering data toward a research-ready analytical dataset.

Q1. Why separate scripts from data?

👉 To maintain modular and scalable project structure.

Q2. Why not create too many folders now?

👉 Over-structuring early slows learning and adds unnecessary complexity.

Q: What does KeyError: 'data' indicate?

👉 The expected JSON structure is missing — usually due to incorrect endpoint or empty response.

Q: How do you debug API issues?

👉 By printing and inspecting the raw response before parsing.

Q: Why did KeyError: 'data' happen?
Because the API response was not a normal data payload. It was a 404 error object, so there was no "data" key.

Q: What does 404 mean here?
The resource path does not exist.

Q: What is the lesson?
Never assume endpoint names. Check the official documentation structure first.

Q: Why was pd.json_normalize(data_price["data"]) valid here but failed earlier?
Because earlier the response was a 404 error object, not a normal data object. Now the JSON actually contains a data key.

Q: Why do we inspect columns and shape again?
Because every dataset must be validated before cleaning and merging.

Q1. Why does the price table have 48 rows?
A: Because one day in the GB market has 48 half-hour settlement periods.

Q2. Why are we keeping both systemSellPrice and systemBuyPrice?
A: Because they represent imbalance pricing conditions and may be useful for later comparison or feature selection.

Q3. Why does date coverage matter before merging?
A: Because mismatched time ranges reduce overlap and can create missing records.

Q: Why is this called a master table?
Because it combines the core datasets needed for analysis into one time-aligned table.

Q: Why is this merge important?
Because fuel data alone does not explain market value; price data turns it into a market analysis dataset.

Q: Why are no missing values a big positive?
Because it means the time alignment worked cleanly and the table is immediately usable.

Q1: What is the most important insight from this dataset?
A: The power market shows high intra-day volatility, with prices ranging from negative to very high levels, likely driven by changes in wind generation and system imbalance.

Q2: Which fuel appears most stable? Why?
A: Nuclear, because it has very low standard deviation and behaves as baseload.

Q3: Which variable indicates arbitrage behavior?
A: Pumped storage, because it switches between negative and positive values.

Q4: Why is wind important in price analysis?
A: Because its variability directly affects supply conditions and therefore price formation.