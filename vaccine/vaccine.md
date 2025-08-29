
# Population-Level Vaccination and Its Dynamic Link to Mortality Rate Through Lag-Adjusted CFR
**By Muhammad Fuad Dhiya Ulhaq**

This is document contains all notes of this project

## 1. The General
### 1.1 Research Purpose
The purpose of this research is to investigate the statistical relationship between the progression of the COVID-19 vaccination population percentage and the corresponding changes in the Case Fatality Rate (CFR) of COVID-19 in Indonesia.

### 1.2 Research Question
How significantly does the rollout of COVID-19 vaccines influence the Case-to-Death Ratio?

### 1.3 Data Used
**Countries**   : Indonesia
**Period**      : 2021 - 2022

---

## 2. Data Description
### 2.1 Data 1: Covid-19 Data
**Source** : https://www.kaggle.com/datasets/hendratno/covid19-indonesia (see sites for details)

#### How we use the data
The initial COVID-19 dataset is first loaded from a CSV file. The treatment process is straightforward:
1. **Filtering** : The data is filtered to include only rows where the Location is "Indonesia".
2. **Column Selection** : Only the essential columns for this analysis—Date, New Cases, and New Deaths—are selected to create a new DataFrame called df_id.
3. **Data Type Conversion**: The Date column, initially a string, is converted into a proper datetime format to enable time-series analysis.

### 2.2 Data 2: Vaccination Data
**source**  : https://www.kaggle.com/datasets/gpreda/covid-world-vaccination-progress?select=country_vaccinations_by_manufacturer.csv (see sites for details)

#### How we use the data
The vaccination data undergoes more significant manipulation to make it suitable for measuring its impact.
1. **Filtering and Selection**: Similar to the COVID data, it's filtered for "Indonesia," and the date, people_fully_vaccinated_per_hundred, and daily_vaccinations_per_million columns are selected.
2. **Handling Missing Values**: Any null values in the people_fully_vaccinated_per_hundred column are filled in by propagating the last or next valid observation forward or backward (ffill, bfill).
3. **Creating the Lagged Variable**: This is a key step. A new column, vaccinated_cumulative_lagged, is created by shifting the people_fully_vaccinated_per_hundred data forward by 14 days. This is done to account for the real-world delay between receiving a full vaccination and developing maximum immunity.

### 2.3 Data 3: Merged and Final Data
Once the two datasets are cleaned and prepared, they are combined and transformed into the final dataset used for the regression.
1. **Merging** : The vaccination DataFrame's date column is renamed to Date, and then it's merged with the df_id (COVID data) using a left join on the Date column. This creates the main df_merged DataFrame.
2. **Creating the Lag-Adjusted CFR** : To fix the time mismatch between infection and death, a New Cases_lagged_14d column is created by shifting the New Cases data forward by 14 days. This allows for a more accurate Case Fatality Rate (CFR) calculation.
3. **Weekly Resampling**: To smooth out daily noise, the entire dataset is resampled from a daily to a weekly frequency (resample('W')). From this weekly data, the two final variables are created:
4. **lag_adjusted_cfr**: The sum of weekly deaths divided by the sum of weekly lagged cases.
5. **avg_vaccination_level**: The weekly average of the vaccinated_cumulative_lagged column.
6. **Final Filtering**: The resulting weekly data is then filtered to only include periods where the average vaccination level was above 3% to ensure the analysis is performed on stable data. This final df_weekly is the dataset used in the scatter plot, correlation matrix, and OLS regression model.

---

## 3. Research Method
The analysis uses an Ordinary Least Squares (OLS) Regression to quantify the relationship between vaccination levels and COVID-19 mortality. The key steps of the methodology are as follows:
1. **Data Preparation** : Daily data on New Cases, New Deaths, and people_fully_vaccinated_per_hundred for Indonesia was cleaned and merged into a single time-series dataset.
2. **Creation of a Lag-Adjusted Case Fatality Rate (CFR)** : To account for the time lag between infection and death, a core metric called the Lag-Adjusted CFR was created. This was calculated by dividing the number of New Deaths on a given day by the number of New Cases from 14 days prior.
3. **Creation of a Lagged Vaccination Metric** : To account for the time it takes to build immunity, the people_fully_vaccinated_per_hundred variable was lagged by 14 days.
4. **Weekly Aggregation** : The daily data was resampled into weekly data points to smooth out daily noise. The final metrics used for the analysis were:
- lag_adjusted_cfr: The sum of weekly deaths divided by the sum of weekly lagged cases.
- avg_vaccination_level: The average of the lagged cumulative vaccination percentage over the week.
5. **Statistical Analysis** : A Pearson correlation and an OLS regression model were used to analyze the relationship between the avg_vaccination_level (independent variable) and the lag_adjusted_cfr (dependent variable).

---

## 4. Result
The analysis found a strong, statistically significant negative relationship between vaccination levels and the case fatality rate in Indonesia.

### 4.1 Visual Analysis
- Time-series plots show that the second major wave of cases in early 2022 was substantially less deadly than the first wave in mid-2021, which corresponds with the period of higher vaccination coverage.
- A scatter plot of the weekly data shows a clear downward trend: as the average vaccination level increases, the lag-adjusted case fatality rate decreases.

### 4.2 Correlation Analysis
The Pearson correlation coefficient between avg_vaccination_level and lag_adjusted_cfr is -0.866. This indicates a very strong inverse linear relationship.

###  4.3 OLS Regression Model
The regression model confirms the visual and correlation findings:
- **R-squared** : The model has an R-squared value of 0.750, meaning that 75% of the variation in the case fatality rate can be explained by the average vaccination level.
- **Coefficient** : The coefficient for avg_vaccination_level is -0.0590 with a p-value of 0.000. This is highly statistically significant and means that for every one-percentage-point increase in the average lagged vaccination level, the case fatality rate is predicted to decrease by 0.059.

---

## Appendix
### 1. Variables
#### 1.1 Strata 1: Critical Variables
1. df_weekly
- What it contains: The final, analysis-ready DataFrame where each row represents a week. It has two main columns: lag_adjusted_cfr and avg_vaccination_level.
- What it's for: This is the primary dataset used to create the final scatter plot, calculate the correlation, and run the OLS regression model.
2. y (lag_adjusted_cfr)
- What it contains: The dependent variable for the regression model, representing the weekly lag-adjusted case fatality rate.
- What it's for: It's the outcome variable that the model tries to explain.
3. X1 (avg_vaccination_level)
- What it contains: The independent variable for the regression model, representing the average weekly vaccination level.
- What it's for: It's the variable used to predict or explain the changes in the dependent variable (y).
4. model
- What it contains: The fitted OLS (Ordinary Least Squares) regression model object from the statsmodels library.
- What it's for: It holds all the statistical results of the analysis, including the R-squared, coefficients, and p-values, which are displayed in the summary table.

#### 1.2 Strata 2: Important Intermediate Variables
These variables are the essential building blocks created during the data manipulation process. The final results depend heavily on their correct construction.
1. df_merged
- What it contains: A daily DataFrame created by merging the cleaned COVID-19 data (df_id) and the vaccination data (df_id_vaccination_temporary).
- What it's for: It's the main dataset that combines both sources of information before the final weekly aggregation.
2. df_analysis
- What it contains: A copy of df_merged that is sliced to only include the date range where vaccination data is available.
- What it's for: It serves as the basis for the final weekly calculations, ensuring the analysis is performed only on the relevant time period.
3. vaccinated_cumulative_lagged
- What it contains: A column with the people_fully_vaccinated_per_hundred data shifted forward by 14 days.
- What it's for: This crucial variable accounts for the time it takes to build immunity after vaccination, forming the basis for the final independent variable.
4. New Cases_lagged_14d
- What it contains: A column with the New Cases data shifted forward by 14 days.
- What it's for: This variable is essential for creating the lag_adjusted_cfr, as it correctly aligns the number of deaths with the cases that likely caused them.
5. weekly_sums & weekly_vax_mean
- What they contain: weekly_sums holds the 2-week sum of New Deaths and New Cases_lagged_14d. weekly_vax_mean holds the 2-week average of vaccinated_cumulative_lagged.
- What they're for: These are the direct results of resampling the daily data into a weekly format and are used to construct the final df_weekly DataFrame.

#### 1.3 Strata 3: Foundational & Temporary Variables 
These variables are used for loading, initial cleaning, and temporary steps. They are necessary for the script to run but are not part of the final analytical model itself.
1. path1, path2, path3
- What they contain: String paths to the raw CSV files.
- What they're for: Loading the initial datasets into pandas.
2. df_covid & df_vaccination
- What they contain: The raw, unfiltered DataFrames loaded directly from the CSV files.
- What they're for: They are the initial sources of data before any cleaning or filtering is applied.
3. df_id & df_id_vaccination
- What they contain: DataFrames filtered to only include data for Indonesia, with selected columns.
- What they're for: These are the cleaned, country-specific datasets that are prepared for merging.
4. begin_date & last_date
- What they contain: The first and last dates for which valid vaccination data exists.
- What they're for: They define the time window for the final analysis and are used to slice df_analysis.
5. df_id_vaccination_temporary
- What it contains: A temporary DataFrame holding just the Date and vaccinated_cumulative_lagged columns.
- What it's for: It's a convenience variable created to perform a clean merge with the df_id DataFrame.
>>>>>>> 81337a4 (Initial commit)
