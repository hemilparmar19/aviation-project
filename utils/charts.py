import plotly.express as px
import plotly.graph_objects as go

# ── THEME COLORS ─────────────────────────────
THEME = {
    "bg":        "#0a0e1a",
    "card_bg":   "#0d1117",
    "line":      "#4da6ff",
    "fill":      "rgba(77,166,255,0.1)",
    "grid":      "#1a2035",
    "text":      "#ffffff",
    "subtext":   "#8899aa",
    "accent":    "#4da6ff",
    "danger":    "#ff0044",
    "warning":   "#ffcc00",
    "safe":      "#00ff88",
}

def apply_dark_theme(fig, height=380):
    """Apply consistent dark theme to any plotly figure"""
    fig.update_layout(
        plot_bgcolor=THEME["card_bg"],
        paper_bgcolor=THEME["card_bg"],
        font=dict(color=THEME["text"], size=12),
        xaxis=dict(gridcolor=THEME["grid"], zerolinecolor=THEME["grid"]),
        yaxis=dict(gridcolor=THEME["grid"], zerolinecolor=THEME["grid"]),
        margin=dict(l=20, r=20, t=40, b=20),
        height=height,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=THEME["grid"],
            font=dict(color=THEME["text"])
        )
    )
    return fig


# ── CHART 1: Global Trend Line ────────────────
def trend_line_chart(yearly_df):
    """Line chart of total accidents per year with fill"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=yearly_df["year"],
        y=yearly_df["total_accidents"],
        mode="lines+markers",
        name="Total Accidents",
        line=dict(color=THEME["line"], width=3),
        marker=dict(size=8, color=THEME["line"],
                    line=dict(color="#ffffff", width=1)),
        fill="tozeroy",
        fillcolor=THEME["fill"],
        hovertemplate="<b>Year:</b> %{x}<br><b>Accidents:</b> %{y}<extra></extra>"
    ))

    fig.update_layout(title="Global Aviation Accidents Trend (2015–2025)")
    return apply_dark_theme(fig)


# ── CHART 2: YOY % Bar Chart ─────────────────
def yoy_bar_chart(yearly_df):
    """Bar chart showing year-over-year % change"""
    df = yearly_df.dropna(subset=["yoy_change_pct"])
    colors = [THEME["danger"] if v > 0 else THEME["safe"]
              for v in df["yoy_change_pct"]]

    fig = go.Figure(go.Bar(
        x=df["year"],
        y=df["yoy_change_pct"],
        marker_color=colors,
        hovertemplate="<b>Year:</b> %{x}<br><b>YOY Change:</b> %{y:.2f}%<extra></extra>"
    ))

    fig.add_hline(y=0, line_color="#ffffff", line_width=1)
    fig.update_layout(title="Year-over-Year Accident Change (%)")
    return apply_dark_theme(fig)


# ── CHART 3: Aircraft Category Bar ───────────
def aircraft_bar_chart(df):
    """Horizontal bar chart - accidents by aircraft category"""
    cat_df = (df.groupby("aircraft_category")
                .size()
                .reset_index(name="total_accidents")
                .sort_values("total_accidents", ascending=True))

    fig = px.bar(
        cat_df,
        x="total_accidents",
        y="aircraft_category",
        orientation="h",
        color="total_accidents",
        color_continuous_scale=[[0, "#1a3a6f"], [1, "#4da6ff"]],
        labels={"total_accidents": "Total Accidents",
                "aircraft_category": "Aircraft Category"},
    )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(title="Accidents by Aircraft Category")
    return apply_dark_theme(fig)


# ── CHART 4: Top Countries Bar ───────────────
def top_countries_chart(df, top_n=10):
    """Horizontal bar chart - top N countries by accidents"""
    country_df = (df.groupby("country_clean")
                    .size()
                    .reset_index(name="total_accidents")
                    .sort_values("total_accidents", ascending=False)
                    .head(top_n)
                    .sort_values("total_accidents", ascending=True))

    fig = px.bar(
        country_df,
        x="total_accidents",
        y="country_clean",
        orientation="h",
        color="total_accidents",
        color_continuous_scale=[[0, "#1a3a6f"], [1, "#4da6ff"]],
        labels={"total_accidents": "Total Accidents",
                "country_clean": "Country"},
    )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(title=f"Top {top_n} Countries by Accident Count")
    return apply_dark_theme(fig)


# ── CHART 5: Cause Contribution ──────────────
def cause_contribution_chart(cause_df):
    """Horizontal bar chart - accident causes with contribution %"""
    plot_df = cause_df.sort_values("total_accidents", ascending=True).tail(12)

    fig = go.Figure(go.Bar(
        x=plot_df["total_accidents"],
        y=plot_df["reason_clean"],
        orientation="h",
        marker_color=THEME["line"],
        text=plot_df["cause_contribution_pct"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        hovertemplate=(
            "<b>Cause:</b> %{y}<br>"
            "<b>Accidents:</b> %{x}<br>"
            "<extra></extra>"
        )
    ))
    fig.update_layout(title="Primary Causes of Aviation Accidents")
    return apply_dark_theme(fig, height=420)


# ── CHART 6: Fatality Severity Donut ─────────
def fatality_severity_donut(df):
    """Donut chart of Fatality_Severity distribution"""
    sev_df = df["Fatality_Severity"].value_counts().reset_index()
    sev_df.columns = ["severity", "count"]

    colors = {
        "Non-Fatal": "#00ff88",
        "Low":       "#ffcc00",
        "Medium":    "#ff6600",
        "High":      "#ff0044"
    }
    color_list = [colors.get(s, "#aaaaaa") for s in sev_df["severity"]]

    fig = go.Figure(go.Pie(
        labels=sev_df["severity"],
        values=sev_df["count"],
        hole=0.55,
        marker=dict(colors=color_list),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>"
    ))
    fig.update_layout(title="Fatality Severity Distribution")
    return apply_dark_theme(fig)


# ── CHART 7: Damage Severity Index Trend ─────
def damage_severity_trend(yearly_df):
    """Line chart showing Damage Severity Index over years"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=yearly_df["year"],
        y=yearly_df["avg_damage_severity"],
        mode="lines+markers",
        name="Damage Severity Index",
        line=dict(color=THEME["warning"], width=3),
        marker=dict(size=8, color=THEME["warning"]),
        fill="tozeroy",
        fillcolor="rgba(255,204,0,0.1)",
        hovertemplate=(
            "<b>Year:</b> %{x}<br>"
            "<b>Damage Severity Index:</b> %{y:.3f}<extra></extra>"
        )
    ))

    fig.update_layout(title="Damage Severity Index by Year")
    return apply_dark_theme(fig)


# ── CHART 8: Risk Scatter (Fatality vs Damage) 
def risk_scatter_chart(risk_df):
    """
    Scatter plot: avg_fatal_risk (x) vs severe_damage_rate (y)
    Matches Power BI page 2 scatter chart
    """
    fig = px.scatter(
        risk_df,
        x="avg_fatal_risk",
        y="severe_damage_rate",
        size="total_accidents",
        color="overall_risk_score",
        hover_name="country_clean",
        color_continuous_scale="RdYlGn_r",
        labels={
            "avg_fatal_risk":      "Avg Fatal Risk",
            "severe_damage_rate":  "Severe Damage Rate",
            "overall_risk_score":  "Overall Risk Score",
            "total_accidents":     "Total Accidents"
        },
        size_max=40,
    )
    fig.update_layout(title="Risk Profile: Fatality Risk vs Severe Damage Rate")
    return apply_dark_theme(fig, height=420)


# ── CHART 9: Top Risk Countries Bar ──────────
def top_risk_countries_chart(risk_df, top_n=10):
    """Bar chart of top N countries by overall_risk_score"""
    plot_df = (risk_df.sort_values("overall_risk_score", ascending=False)
                      .head(top_n)
                      .sort_values("overall_risk_score", ascending=True))

    fig = px.bar(
        plot_df,
        x="overall_risk_score",
        y="country_clean",
        orientation="h",
        color="overall_risk_score",
        color_continuous_scale=[[0, "#1a3a6f"], [0.5, "#ffcc00"], [1, "#ff0044"]],
        labels={"overall_risk_score": "Overall Risk Score",
                "country_clean": "Country"},
    )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(title=f"Top {top_n} Highest Risk Countries")
    return apply_dark_theme(fig)


# ── CHART 10: Monthly Heatmap ─────────────────
def monthly_heatmap(df):
    """Heatmap of accidents by month and year"""
    pivot = (df.groupby(["year", "month"])
               .size()
               .reset_index(name="accidents")
               .pivot(index="month", columns="year", values="accidents")
               .fillna(0))

    month_names = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[str(y) for y in pivot.columns],
        y=month_names[:len(pivot.index)],
        colorscale="Blues",
        hovertemplate="<b>Year:</b> %{x}<br><b>Month:</b> %{y}<br><b>Accidents:</b> %{z}<extra></extra>"
    ))
    fig.update_layout(title="Accident Frequency Heatmap (Month × Year)")
    return apply_dark_theme(fig, height=380)
