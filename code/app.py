import streamlit as st
import pandas as pd
import analysis
import plotly.express as px
import os

# Page Configuration 
st.set_page_config(page_title="EviSure - 3D Audit Model", layout="wide")

st.title("🔐 EviSure - Framework-Independent Control Assessment System")

uploaded_file = st.file_uploader("Upload Controls CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.markdown("## 📝 Control Assessment")

    impl_options = list(analysis.IMPLEMENTATION_SCORES.keys())

    if "Implementation" not in df.columns:
        df["Implementation"] = "Not Implemented"

    for col in ["Completeness", "Currency", "Consistency", "Verifiability"]:
        if col not in df.columns:
            df[col] = 0.0

    edited_df = st.data_editor(
        df,
        column_config={
            "Implementation": st.column_config.SelectboxColumn(
                "Implementation Status",
                options=impl_options,
                help="Select current deployment level"
            ),
            "Completeness": st.column_config.NumberColumn("Completeness (0-1)", min_value=0.0, max_value=1.0, step=0.1),
            "Currency": st.column_config.NumberColumn("Currency (0-1)", min_value=0.0, max_value=1.0, step=0.1),
            "Consistency": st.column_config.NumberColumn("Consistency (0-1)", min_value=0.0, max_value=1.0, step=0.1),
            "Verifiability": st.column_config.NumberColumn("Verifiability (0-1)", min_value=0.0, max_value=1.0, step=0.1),
        },
        width="stretch",
        hide_index=True
    )

    edited_df["impl_score"] = edited_df["Implementation"].str.strip().map(
        analysis.IMPLEMENTATION_SCORES
    ).fillna(0)

    results, overall_eff, overall_risk, audit_score, audit_status = analysis.analyze_dataframe(edited_df)

    st.markdown("---")
    st.markdown("## 📊 Assessment Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Overall Effectiveness", 
            value=f"{overall_eff}%",
            help="85-100%: Effective\n50-84%: Partial\n0-49%: Ineffective"
        )

    with col2:
        st.metric(
            label="Overall Risk Score", 
            value=overall_risk,
            help="0-20: Low Risk\n21-50: Medium Risk\n51-100: High Risk"
        )

    with col3:
        st.metric(
            label="Audit Readiness", 
            value=f"{audit_score}%",
            help="85-100%: Audit Ready\n70-84%: Almost Ready\n40-69%: Partially Ready\n<40%: Not Ready"
        )

    st.write(f"**Current Audit Status:** `{audit_status}`")

    # Domain Results Table
    columns = [
        "Domain Code", "Domain Name", "Adjusted Score", 
        "Total Controls", "Effectiveness (%)", "Risk Score", 
        "Risk Level", "Evidence Quality"
    ]
    result_df = pd.DataFrame(results, columns=columns)
    st.dataframe(result_df, width="stretch", hide_index=True)

    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("### 📊 Domain Effectiveness")
        fig_bar = px.bar(
            result_df,
            x="Domain Code",
            y="Effectiveness (%)",
            color="Effectiveness (%)",
            text="Effectiveness (%)",
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_v2:
        st.markdown("### 📉 Risk Distribution")
        fig_pie = px.pie(
            result_df,
            names="Risk Level",
            color="Risk Level",
            color_discrete_map={'Low':'green', 'Medium':'orange', 'High':'red'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Evidence Quality Breakdown ---
    st.markdown("### 📂 Evidence Quality Compliance")
    st.caption("Hover over bars to see the Evidence Quality (EQL) coefficient (0.0 - 1.0).")

    for _, row in result_df.iterrows():
        st.write(f"**{row['Domain Code']} - {row['Domain Name']}**")
        st.progress(row["Evidence Quality"])

        if row["Evidence Quality"] >= 0.8:
            st.success(f"Strong Evidence Quality ({row['Evidence Quality']})")
        elif row["Evidence Quality"] >= 0.5:
            st.warning(f"Moderate Evidence Quality ({row['Evidence Quality']})")
        else:
            st.error(f"Weak Evidence Quality ({row['Evidence Quality']})")

    # --- Evidence File Management ---
    st.markdown("---")
    st.markdown("## 📎 Evidence Management")
    
    if not os.path.exists("evidence"):
        os.makedirs("evidence")

    uploaded_evidence = st.file_uploader(
        "Upload Audit Evidence (Policy, Screenshot, Logs)",
        type=["pdf", "png", "jpg", "jpeg", "xlsx", "docx"]
    )

    if uploaded_evidence:
        file_path = os.path.join("evidence", uploaded_evidence.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_evidence.getbuffer())
        st.success(f"Uploaded: {uploaded_evidence.name}")

    st.markdown("### Stored Repository")
    files = os.listdir("evidence")
    if files:
        for f in files: st.text(f"📄 {f}")
    else:
        st.info("No evidence uploaded yet.")

else:
    st.info("Please upload a controls.csv file to begin your assessment.")