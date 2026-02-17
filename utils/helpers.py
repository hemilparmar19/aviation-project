def format_number(num):
    """Format large numbers with commas: 2596 → 2,596"""
    return f"{int(num):,}"

def format_pct(num, decimals=2):
    """Format as percentage: 17.37 → 17.37%"""
    return f"{num:.{decimals}f}%"

def risk_emoji(risk_pct):
    """Return colored circle emoji based on risk %"""
    if risk_pct < 20:   return "🟢"
    elif risk_pct < 40: return "🟡"
    elif risk_pct < 60: return "🟠"
    else:               return "🔴"

def risk_label(risk_pct):
    """Return text label based on risk %"""
    if risk_pct < 20:   return "LOW RISK"
    elif risk_pct < 40: return "MEDIUM RISK"
    elif risk_pct < 60: return "HIGH RISK"
    else:               return "VERY HIGH RISK"

def risk_color(risk_pct):
    """Return hex color based on risk %"""
    if risk_pct < 20:   return "#00ff88"
    elif risk_pct < 40: return "#ffcc00"
    elif risk_pct < 60: return "#ff6600"
    else:               return "#ff0044"

def severity_color(severity):
    """Return color for Fatality_Severity labels"""
    colors = {
        "Non-Fatal": "#00ff88",
        "Low":       "#ffcc00",
        "Medium":    "#ff6600",
        "High":      "#ff0044"
    }
    return colors.get(severity, "#aaaaaa")

def damage_label(damage_severity_int):
    """Convert numeric Damage_Severity (0-3) to readable label"""
    labels = {0: "None", 1: "Minor", 2: "Substantial", 3: "Destroyed"}
    return labels.get(int(damage_severity_int), "Unknown")

def yoy_arrow(yoy_pct):
    """Return up/down arrow based on YOY change"""
    if yoy_pct > 0:   return f"▲ +{yoy_pct:.2f}%"
    elif yoy_pct < 0: return f"▼ {yoy_pct:.2f}%"
    else:             return "→ 0.00%"
