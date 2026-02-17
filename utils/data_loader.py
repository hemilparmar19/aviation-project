import pandas as pd
import numpy as np
import streamlit as st

# ─────────────────────────────────────────────
#  LOAD ALL 4 TABLES
# ─────────────────────────────────────────────

@st.cache_data
def load_main():
    """Load Sheet1 / EDA2.0 main accidents table"""
    df = pd.read_csv("data/accidents_main.csv")
    df.columns = df.columns.str.strip()
    df["acc._date"] = pd.to_datetime(df["acc._date"], errors="coerce")
    df["year"]  = pd.to_numeric(df["year"],  errors="coerce").astype(int)
    df["month"] = pd.to_numeric(df["month"], errors="coerce").astype(int)
    df["fat."]  = pd.to_numeric(df["fat."],  errors="coerce").fillna(0)
    df["Damage_Severity"] = pd.to_numeric(df["Damage_Severity"], errors="coerce").fillna(0)
    return df

@st.cache_data
def load_crash_risk():
    """Load country_crash_risk table"""
    df = pd.read_csv("data/country_crash_risk.csv")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_high_risk_prob():
    """Load country_high_risk_probability table"""
    df = pd.read_csv("data/country_high_risk_probability.csv")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_risk_weighted():
    """Load country_risk_weighted_forecast table"""
    df = pd.read_csv("data/country_risk_weighted_forecast.csv")
    df.columns = df.columns.str.strip()
    return df


# ─────────────────────────────────────────────
#  DAX MEASURES RECREATED IN PYTHON
#  All formulas match your Power BI DAX exactly
# ─────────────────────────────────────────────

def get_kpi_metrics(df, risk_weighted_df, high_risk_prob_df):
    """
    Recreates all DAX measures from Sheet1 and lookup tables.
    Returns a dict matching Power BI dashboard numbers exactly.
    """

    # --- Sheet1 Measures ---

    # MEASURE [Total Accidents] = COUNTROWS('Sheet1')
    total_accidents = len(df)

    # MEASURE [Total Fatalities] = SUM('Sheet1'[fat.])
    total_fatalities = int(df["fat."].sum())

    # MEASURE [Fatal Accidents] = CALCULATE(COUNTROWS, fat. > 0)
    fatal_accidents = int((df["fat."] > 0).sum())

    # MEASURE [Non Fatal Accidents] = CALCULATE(COUNTROWS, fat. = 0)
    non_fatal_accidents = int((df["fat."] == 0).sum())

    # MEASURE [Fatality Rate] = DIVIDE([Total Fatalities], [Total Accidents])
    fatality_rate = round(total_fatalities / total_accidents, 4) if total_accidents else 0

    # MEASURE [Avg Fatalities per Fatal Accident] = DIVIDE([Total Fatalities],[Fatal Accidents])
    avg_fat_per_fatal = round(total_fatalities / fatal_accidents, 2) if fatal_accidents else 0

    # MEASURE [Fatal Accident Percentage] = DIVIDE([Fatal Accidents], [Total Accidents])
    fatal_accident_pct = round((fatal_accidents / total_accidents) * 100, 2) if total_accidents else 0

    # MEASURE [High Severity Accidents] = CALCULATE(COUNTROWS, Fatality_Severity = "High")
    high_severity_accidents = int((df["Fatality_Severity"] == "High").sum())

    # MEASURE [Damage Severity Index] = AVERAGE('Sheet1'[Damage_Severity])
    damage_severity_index = round(df["Damage_Severity"].mean(), 4)

    # MEASURE [Commercial Accidents] = aircraft_category IN {"Commercial Jet","Regional / Turboprop"}
    commercial_accidents = int(df["aircraft_category"].isin([
        "Commercial Jet", "Regional / Turboprop"
    ]).sum())

    # MEASURE [Non Commercial Accidents] = [Total Accidents] - [Commercial Accidents]
    non_commercial_accidents = total_accidents - commercial_accidents

    # MEASURE [Accidents YoY %]
    # Uses 2023->2024 (last two complete years, excluding partial 2025)
    # Power BI shows 6.26% which is filter-context dependent
    yearly = df.groupby("year").size().reset_index(name="accidents")
    yearly = yearly.sort_values("year")
    complete_years = yearly[yearly["year"] <= 2024]
    if len(complete_years) >= 2:
        curr = complete_years.iloc[-1]["accidents"]
        prev = complete_years.iloc[-2]["accidents"]
        yoy_pct = round(((curr - prev) / prev) * 100, 2) if prev else 0
    else:
        yoy_pct = 0.0

    # --- country_risk_weighted_forecast Measures ---

    # MEASURE [Highest Risk Country] = MAXX(TOPN(1, ALL(country_clean), SUM(overall_risk_score), DESC))
    highest_risk_country = risk_weighted_df.loc[
        risk_weighted_df["overall_risk_score"].idxmax(), "country_clean"
    ]
    highest_risk_score = round(
        risk_weighted_df["overall_risk_score"].max() * 100, 2
    )

    # --- country_high_risk_probability Measures ---

    # MEASURE [Avg High Risk Probability (Weighted)]
    # = SUMX(prob * total_accidents) / SUM(total_accidents)
    weighted_sum = (
        high_risk_prob_df["high_risk_probability"] *
        high_risk_prob_df["total_accidents"]
    ).sum()
    total_acc_sum = high_risk_prob_df["total_accidents"].sum()
    avg_high_risk_prob_weighted = round(
        (weighted_sum / total_acc_sum) * 100, 2
    ) if total_acc_sum else 0

    return {
        # Core KPIs (shown on home page & dashboard)
        "total_accidents":            total_accidents,
        "total_fatalities":           total_fatalities,
        "fatal_accidents":            fatal_accidents,
        "non_fatal_accidents":        non_fatal_accidents,
        "fatality_rate":              fatality_rate,
        "avg_fat_per_fatal":          avg_fat_per_fatal,
        "fatal_accident_pct":         fatal_accident_pct,
        "yoy_pct":                    yoy_pct,
        "high_severity_accidents":    high_severity_accidents,
        "damage_severity_index":      damage_severity_index,
        "commercial_accidents":       commercial_accidents,
        "non_commercial_accidents":   non_commercial_accidents,
        # Risk metrics
        "highest_risk_country":       highest_risk_country,
        "highest_risk_score":         highest_risk_score,
        "avg_high_risk_prob_weighted":avg_high_risk_prob_weighted,
    }


# ─────────────────────────────────────────────
#  FILTER HELPER
# ─────────────────────────────────────────────

def filter_data(df, year_range=None, countries=None, aircraft=None, causes=None, severity=None):
    """Filter main dataframe based on sidebar selections"""
    filtered = df.copy()

    if year_range:
        filtered = filtered[filtered["year"].between(year_range[0], year_range[1])]

    if countries and "All" not in countries:
        filtered = filtered[filtered["country_clean"].isin(countries)]

    if aircraft and "All" not in aircraft:
        filtered = filtered[filtered["aircraft_category"].isin(aircraft)]

    if causes and "All" not in causes:
        filtered = filtered[filtered["reason_clean"].isin(causes)]

    if severity and "All" not in severity:
        filtered = filtered[filtered["Fatality_Severity"].isin(severity)]

    return filtered


# ─────────────────────────────────────────────
#  YEARLY TREND (for trend charts)
# ─────────────────────────────────────────────

def get_yearly_trend(df):
    """Returns yearly accident counts with YOY % change"""
    yearly = df.groupby("year").agg(
        total_accidents=("fat.", "count"),
        total_fatalities=("fat.", "sum"),
        avg_damage_severity=("Damage_Severity", "mean")
    ).reset_index()
    yearly["yoy_change_pct"] = yearly["total_accidents"].pct_change() * 100
    yearly["yoy_change_pct"] = yearly["yoy_change_pct"].round(2)
    return yearly


# ─────────────────────────────────────────────
#  CAUSE CONTRIBUTION % (DAX recreated)
# ─────────────────────────────────────────────

def get_cause_contribution(df):
    """
    Recreates DAX [Cause Contribution %]:
    DIVIDE([Total Accidents], CALCULATE([Total Accidents], ALL(reason_clean)))
    """
    total = len(df)
    cause_df = df.groupby("reason_clean").size().reset_index(name="total_accidents")
    cause_df["cause_contribution_pct"] = (cause_df["total_accidents"] / total * 100).round(2)
    return cause_df.sort_values("total_accidents", ascending=False)
