### **Project Title: Philadelphia Crime Analysis & Forecasting (2006–Present)**

---

### **Phase 1: Project Setup & Objective**

**Goal:** To analyze temporal and spatial patterns of crime in Philadelphia, identify high-risk areas, and forecast future crime trends.

* **Tools:** Python (Pandas, NumPy, Matplotlib/Seaborn, Folium/Plotly for maps, Scikit-Learn).
* **Dataset:** [Crime Incidents - OpenDataPhilly](https://catalog.data.gov/dataset/crime-incidents-285df).

---

### **Phase 2: Data Loading & Preprocessing**

*Demonstrate your ability to handle large, raw datasets.*

1. **Ingestion Strategy:**
* The dataset is split by year. Write a script to loop through the URLs (e.g., 2006–2024 CSVs) and concatenate them into a single DataFrame.
* *Tip:* Use `pd.concat()` for merging and caching (save the combined file locally to avoid re-downloading).


2. **Data Cleaning:**
* **Date Parsing:** Convert `dispatch_date_time` to datetime objects. Extract features: `Year`, `Month`, `Day`, `Hour`, `DayOfWeek`.
* **Geolocation Filtering:** Remove rows with missing or invalid coordinates (`lat`, `lng`). Filter out outliers (points lying outside Philadelphia boundaries).
* **Standardization:** Rename columns for clarity (e.g., `text_general_code`  `Crime_Type`).
* **Categorization:** Create a new broad category column:
* *Violent Crimes:* Homicide, Rape, Aggravated Assault, Robbery.
* *Property Crimes:* Burglary, Theft, Motor Vehicle Theft, Arson.
* *Other:* Vandalism, Fraud, Narcotics.





---

### **Phase 3: Exploratory Data Analysis (EDA)**

*Showcase your ability to derive insights from data.*

**1. Temporal Analysis (When do crimes happen?)**

* **Trend Analysis:** Plot the total number of crimes per year. Is crime increasing or decreasing?
* **Seasonality:**
* *Monthly:* Do crimes spike in summer? (Boxplots of crime counts by month).
* *Daily/Hourly:* Heatmap of `DayOfWeek` vs. `Hour`. (e.g., Do robberies happen more on Friday nights?)


* **Impact of Events:** Annotate the timeline with major events (e.g., COVID-19 lockdown start date) to see their impact.

**2. Spatial Analysis (Where do crimes happen?)**

* **Static Maps:** Scatter plot of incidents colored by `Crime_Type`.
* **Interactive Maps (Folium/Kepler.gl):**
* Create a heatmap of violent crimes.
* Cluster markers for specific crime types (e.g., Homicides).


* **District Analysis:** Group by `dc_dist` (District) to find the safest and most dangerous districts. Visualization: Choropleth map (using district shapefiles).

**3. Categorical Analysis**

* **Top Crimes:** Bar chart of the top 10 most frequent crime types.
* **Resolution Rates:** If the dataset includes an "outcome" or "clearance" column, analyze arrest rates per crime type.

---

### **Phase 4: Advanced Analysis & Feature Engineering**

*Move beyond simple charts to show analytical depth.*

**1. Hotspot Identification (Clustering)**

* **Technique:** Use **K-Means** or **DBSCAN** clustering on `lat`/`lng` data.
* **Goal:** Identify specific neighborhoods or intersections that act as "crime hotspots" independent of official police districts.

**2. Safety Score Calculation**

* **Feature Engineering:** Create a grid system (e.g., H3 hexagons or simple lat/lon bins).
* **Metric:** Calculate a "Safety Score" for each grid cell based on the frequency and severity of crimes (weight violent crimes higher than property crimes).

---

### **Phase 5: Predictive Modeling (Machine Learning)**

*Demonstrate your ability to apply ML algorithms.*

**Option A: Time Series Forecasting (Recommended)**

* **Goal:** Predict the number of crimes for the next 6 months.
* **Method:**
1. Resample data to daily or weekly counts.
2. Use **Facebook Prophet** (easiest for beginners with seasonality support) or **SARIMA**.
3. **Validation:** Train on 2006–2023, Test on 2024 data. Compare RMSE/MAE.



**Option B: Crime Type Classification**

* **Goal:** Predict the type of crime based on location and time.
* **Method:** Random Forest or Gradient Boosting (XGBoost).
* **Features:** `Lat`, `Lng`, `Hour`, `DayOfWeek`, `Month`, `District`.
* **Target:** `Crime_Category` (Violent vs. Property).

---

### **Phase 6: Storytelling & Conclusion**

* **Executive Summary:** Summarize the top 3 findings (e.g., "Crime peaks in July at 10 PM," "District X has seen a 20% reduction in theft").
* **Recommendations:** Suggest actionable insights (e.g., "Patrols should be increased in Cluster 3 on Friday nights").
* **Next Steps:** Mention how you would improve the project (e.g., "Include weather data to see if rain affects crime rates").

### **Bonus: Interactive Dashboard**

If you want to go the extra mile, convert your analysis into a **Streamlit** app. Allow users to:

* Filter by Year/Month.
* Select a Crime Type.
* See the heatmap update dynamically.

### **Suggested Notebook Structure (Table of Contents)**

1. **Introduction**: Problem statement and data source.
2. **Setup**: Libraries and configuration.
3. **Data Ingestion**: Loading and cleaning functions.
4. **EDA - Temporal**: Time series plots and heatmaps.
5. **EDA - Spatial**: Maps and geospatial analysis.
6. **Deep Dive**: Specific analysis of Violent vs. Non-Violent crimes.
7. **Modeling**: Time series forecasting or clustering.
8. **Conclusion**: Summary of results.