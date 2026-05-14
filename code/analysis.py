import pandas as pd

DOMAIN_NAMES = {
    "A.5": "Organizational Controls",
    "A.6": "People Controls",
    "A.7": "Physical Controls",
    "A.8": "Technological Controls",
}

IMPLEMENTATION_SCORES = {
    "Implemented": 1.0,
    "Partially Implemented": 0.5,
    "Not Implemented": 0.0
}

def calculate_risk(effectiveness):
    risk_score = round(100 - effectiveness, 2)
    if risk_score <= 20:
        level = "Low"
    elif risk_score <= 50:
        level = "Medium"
    else:
        level = "High"
    return risk_score, level

def analyze_dataframe(df):
    results = []
    df = df.copy().fillna(0)
    
    # Ensure numeric types for evidence attributes
    evidence_cols = ["Completeness", "Currency", "Consistency", "Verifiability"]
    for col in evidence_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 1. Calculate Individual Control Scores (Evidence Quality Coefficient)
    # Formula: (Completeness + Currency + Consistency + Verifiability) / 4
    df["EQL"] = df[evidence_cols].mean(axis=1)

    # 2. Calculate Adjusted Score per Control
    # Formula: impl_score * (0.5 + 0.5 * EQL)
    df["Adjusted Score"] = df["impl_score"] * (0.5 + 0.5 * df["EQL"])

    # Group by Domain for Dashboard
    grouped = df.groupby("domain")
    total_adjusted_sum = df["Adjusted Score"].sum()
    total_controls_count = len(df)

    for domain, group in grouped:
        domain_total_controls = len(group)
        domain_adj_sum = group["Adjusted Score"].sum()
        
        # Effectiveness = (Sum of Adjusted Scores of Applicable Controls / Total Applicable Controls) * 100
        effectiveness = round((domain_adj_sum / domain_total_controls) * 100, 2)
        
        risk_score, risk_level = calculate_risk(effectiveness)
        avg_eql = round(group["EQL"].mean(), 2)

        results.append((
            domain,
            DOMAIN_NAMES.get(domain, "Unknown"),
            round(domain_adj_sum, 2),
            domain_total_controls,
            effectiveness,
            risk_score,
            risk_level,
            avg_eql
        ))

    # Overall Metrics
    overall_eff = round((total_adjusted_sum / total_controls_count) * 100, 2)
    overall_risk = round(100 - overall_eff, 2)
    
    # Audit Readiness = (Sum of EQL of Applicable Controls / Total Applicable Controls) * 100
    audit_score = round(df["EQL"].mean() * 100, 2)
    
    if audit_score >= 85:
        status = "Audit Ready"
    elif audit_score >= 70:
        status = "Almost Ready"
    elif audit_score >= 40:
        status = "Partially Ready"
    else:
        status = "Not Ready"

    return results, overall_eff, overall_risk, audit_score, status