import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from io import BytesIO

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WellCampus Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fb; }
    .block-container { padding-top: 1.5rem; }
    h1 { color: #1a3c5e; }
    h2, h3 { color: #2c5f8a; }
    .metric-box {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        text-align: center;
    }
    .metric-label { font-size: 13px; color: #888; margin-bottom: 4px; }
    .metric-value { font-size: 26px; font-weight: 700; color: #1a3c5e; }
    .metric-delta { font-size: 12px; color: #4caf50; }
    .insight-box {
        background: #eef4fb;
        border-left: 4px solid #2c7be5;
        border-radius: 6px;
        padding: 10px 16px;
        margin-top: 8px;
        font-size: 13.5px;
        color: #333;
    }
    .section-header {
        background: linear-gradient(90deg, #1a3c5e, #2c7be5);
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    raw = pd.read_csv("wellcampus_raw_data.csv")
    clean = pd.read_csv("wellcampus_cleaned_data.csv")
    return raw, clean

raw_df, df = load_data()

PALETTE = ["#2c7be5", "#00b4d8", "#4cc9a0", "#f4a261", "#e63946", "#8338ec", "#fb8500"]
sns.set_theme(style="whitegrid", font_scale=0.95)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/university.png", width=60)
    st.title("WellCampus")
    st.caption("B2B Mental Health Platform for Students")
    st.markdown("---")
    st.markdown("**Navigation**")
    page = st.radio("", [
        "🏠 Overview",
        "📊 Descriptive Statistics",
        "🔗 Correlation Analysis",
        "📈 EDA: Sales Pipeline",
        "🎓 Student Wellness Metrics",
        "🧹 Data Cleaning Log",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Filters**")
    tier_filter = st.multiselect("City Tier", options=df["City_Tier"].unique().tolist(),
                                  default=df["City_Tier"].unique().tolist())
    source_filter = st.multiselect("Lead Source", options=df["Lead_Source"].unique().tolist(),
                                    default=df["Lead_Source"].unique().tolist())
    filtered_df = df[(df["City_Tier"].isin(tier_filter)) & (df["Lead_Source"].isin(source_filter))]

# ── Helper ────────────────────────────────────────────────────────────────────
def insight(text):
    st.markdown(f'<div class="insight-box">💡 <b>Insight:</b> {text}</div>', unsafe_allow_html=True)

def fig_to_st(fig, caption=None):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=130)
    buf.seek(0)
    st.image(buf)
    if caption:
        st.caption(caption)
    plt.close(fig)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("🎓 WellCampus — Business Validation Dashboard")
    st.markdown("**Startup Idea:** A B2B Mental Health & Wellness SaaS platform sold to colleges and universities across India, providing students with counseling booking, stress tracking, and wellness resources.")
    st.markdown("---")

    won = filtered_df[filtered_df["Pipeline_Stage"] == "Closed Won"]
    total_leads = len(filtered_df)
    conv_rate = round(len(won) / total_leads * 100, 1)
    total_rev = won["Final_Deal_Value_INR"].sum()
    avg_deal = won["Final_Deal_Value_INR"].mean()
    avg_nps = filtered_df["Student_Satisfaction_NPS"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        ("Total Leads", f"{total_leads:,}", "College institutions"),
        ("Conversion Rate", f"{conv_rate}%", "Closed Won"),
        ("Total Revenue (INR)", f"₹{total_rev/1e7:.2f} Cr", "From closed deals"),
        ("Avg Deal Size (INR)", f"₹{avg_deal/1e5:.1f}L", "Per institution"),
        ("Avg Student NPS", f"{avg_nps:.1f}/10", "Satisfaction score"),
    ]
    for col, (label, val, sub) in zip([c1, c2, c3, c4, c5], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-delta">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Pipeline Stage Distribution</div>', unsafe_allow_html=True)
        stage_counts = filtered_df["Pipeline_Stage"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.barh(stage_counts.index, stage_counts.values, color=PALETTE[:len(stage_counts)])
        ax.set_xlabel("Number of Leads")
        ax.set_title("Leads by Pipeline Stage", fontweight="bold")
        for bar, val in zip(bars, stage_counts.values):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, str(val), va="center", fontsize=9)
        plt.tight_layout()
        fig_to_st(fig)
        insight("Most leads are still in early stages (Awareness/Interest), highlighting the need to improve mid-funnel nurturing to push leads toward Demo and Proposal.")

    with col2:
        st.markdown('<div class="section-header">Revenue by Lead Source</div>', unsafe_allow_html=True)
        rev_src = won.groupby("Lead_Source")["Final_Deal_Value_INR"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(rev_src.index, rev_src.values / 1e5, color=PALETTE[:len(rev_src)])
        ax.set_ylabel("Revenue (₹ Lakhs)")
        ax.set_title("Closed Revenue by Lead Source", fontweight="bold")
        ax.tick_params(axis='x', rotation=20)
        plt.tight_layout()
        fig_to_st(fig)
        insight("College Partnerships and Referrals drive the highest revenue, validating that relationship-driven sales outperform digital channels for institutional B2B sales.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: DESCRIPTIVE STATISTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Descriptive Statistics":
    st.title("📊 Descriptive Statistics")

    st.markdown("### Raw vs Cleaned Dataset Comparison")
    c1, c2, c3 = st.columns(3)
    c1.metric("Raw Dataset Rows", len(raw_df))
    c2.metric("Cleaned Dataset Rows", len(df))
    c3.metric("Rows Removed", len(raw_df) - len(df))

    st.markdown("---")
    st.markdown("### Summary Statistics — Numerical Variables")
    num_cols = ["Lead_Score", "Deal_Value_INR", "Final_Deal_Value_INR", "Discount_Percent",
                "Student_Count", "Days_in_Pipeline", "Avg_Student_Stress_Score",
                "Monthly_Sessions_Used", "Student_Satisfaction_NPS", "Counseling_Utilization_Pct"]
    st.dataframe(filtered_df[num_cols].describe().round(2), use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribution of Lead Scores")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(filtered_df["Lead_Score"], bins=20, color="#2c7be5", edgecolor="white", alpha=0.85)
        ax.axvline(filtered_df["Lead_Score"].mean(), color="#e63946", linestyle="--", label=f"Mean: {filtered_df['Lead_Score'].mean():.1f}")
        ax.axvline(filtered_df["Lead_Score"].median(), color="#f4a261", linestyle="--", label=f"Median: {filtered_df['Lead_Score'].median():.1f}")
        ax.legend(); ax.set_xlabel("Lead Score"); ax.set_ylabel("Frequency")
        ax.set_title("Lead Score Distribution", fontweight="bold")
        plt.tight_layout()
        fig_to_st(fig)
        insight("Lead scores follow a roughly normal distribution with a slight positive skew. Most leads cluster between 50–70, indicating moderate-quality inbound pipeline.")

    with col2:
        st.markdown("#### Distribution of Final Deal Values")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(filtered_df["Final_Deal_Value_INR"] / 1e5, bins=25, color="#4cc9a0", edgecolor="white", alpha=0.85)
        ax.set_xlabel("Deal Value (₹ Lakhs)")
        ax.set_ylabel("Frequency")
        ax.set_title("Final Deal Value Distribution", fontweight="bold")
        plt.tight_layout()
        fig_to_st(fig)
        insight("Deal values are right-skewed — most deals are in the ₹5–20L range, but a few enterprise deals push the mean significantly above the median.")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Willingness to Pay — Survey Results")
        wtp = filtered_df["Willingness_to_Pay"].value_counts()
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(wtp.values, labels=wtp.index, autopct="%1.1f%%", colors=PALETTE[:3],
               startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2})
        ax.set_title("Willingness to Pay", fontweight="bold")
        plt.tight_layout()
        fig_to_st(fig)
        insight("Over 60% of surveyed institutions show High or Medium willingness to pay — a strong market validation signal for WellCampus's pricing model.")

    with col2:
        st.markdown("#### Contract Type Preference")
        ct = filtered_df["Contract_Type"].value_counts()
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(ct.index, ct.values, color=PALETTE[2:5], edgecolor="white")
        ax.set_ylabel("Count"); ax.set_title("Contract Type Distribution", fontweight="bold")
        plt.tight_layout()
        fig_to_st(fig)
        insight("Annual contracts are most preferred, indicating institutions value long-term commitments — great for WellCampus ARR predictability.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: CORRELATION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔗 Correlation Analysis":
    st.title("🔗 Correlation Analysis")
    st.markdown("Understanding how key business variables relate to each other.")

    corr_cols = ["Lead_Score", "Final_Deal_Value_INR", "Discount_Percent",
                 "Student_Count", "Days_in_Pipeline", "Avg_Student_Stress_Score",
                 "Monthly_Sessions_Used", "Student_Satisfaction_NPS",
                 "Counseling_Utilization_Pct", "Pain_Point_Rating", "Converted"]
    corr_matrix = filtered_df[corr_cols].corr()

    st.markdown("### Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(11, 8))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn",
                center=0, vmin=-1, vmax=1, ax=ax, linewidths=0.5,
                annot_kws={"size": 9})
    ax.set_title("Pearson Correlation Matrix — WellCampus Variables", fontweight="bold", fontsize=13)
    plt.tight_layout()
    fig_to_st(fig)
    insight("Strong positive correlation between Lead_Score and Converted (r≈0.65) confirms lead scoring is a valid predictor of deal closure. Student_Count positively correlates with Final_Deal_Value, as expected for per-student pricing.")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Lead Score vs Final Deal Value")
        fig, ax = plt.subplots(figsize=(6, 4))
        sc = ax.scatter(filtered_df["Lead_Score"], filtered_df["Final_Deal_Value_INR"]/1e5,
                        c=filtered_df["Converted"], cmap="RdYlGn", alpha=0.6, edgecolors="none", s=40)
        m, b = np.polyfit(filtered_df["Lead_Score"], filtered_df["Final_Deal_Value_INR"]/1e5, 1)
        x_line = np.linspace(filtered_df["Lead_Score"].min(), filtered_df["Lead_Score"].max(), 100)
        ax.plot(x_line, m * x_line + b, color="#e63946", linewidth=2, linestyle="--", label="Trend")
        plt.colorbar(sc, ax=ax, label="Converted (1=Yes)")
        ax.set_xlabel("Lead Score"); ax.set_ylabel("Final Deal Value (₹ Lakhs)")
        ax.set_title("Lead Score vs Deal Value", fontweight="bold")
        ax.legend(); plt.tight_layout()
        fig_to_st(fig)
        insight("Higher lead scores not only correlate with larger deal values but also with conversion (green dots cluster top-right). This validates investing in lead qualification early.")

    with col2:
        st.markdown("#### Student Count vs Deal Value")
        fig, ax = plt.subplots(figsize=(6, 4))
        colors = [PALETTE[0] if t == "Tier 1" else PALETTE[2] for t in filtered_df["City_Tier"]]
        ax.scatter(filtered_df["Student_Count"]/1000, filtered_df["Final_Deal_Value_INR"]/1e5,
                   c=colors, alpha=0.55, s=40)
        t1 = mpatches.Patch(color=PALETTE[0], label="Tier 1")
        t2 = mpatches.Patch(color=PALETTE[2], label="Tier 2")
        ax.legend(handles=[t1, t2])
        ax.set_xlabel("Student Count (thousands)"); ax.set_ylabel("Final Deal Value (₹ Lakhs)")
        ax.set_title("Student Count vs Deal Value by Tier", fontweight="bold")
        plt.tight_layout()
        fig_to_st(fig)
        insight("Tier 1 colleges (blue) tend to have higher student counts AND higher deal values, making them the most attractive segment for WellCampus's enterprise sales team.")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Stress Score vs Monthly Sessions Used")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(filtered_df["Avg_Student_Stress_Score"], filtered_df["Monthly_Sessions_Used"],
                   color="#8338ec", alpha=0.45, s=35)
        m, b = np.polyfit(filtered_df["Avg_Student_Stress_Score"], filtered_df["Monthly_Sessions_Used"], 1)
        x_line = np.linspace(4, 9, 100)
        ax.plot(x_line, m * x_line + b, color="#e63946", linewidth=2, linestyle="--")
        ax.set_xlabel("Avg Student Stress Score"); ax.set_ylabel("Monthly Sessions Used")
        ax.set_title("Stress Score vs Platform Usage", fontweight="bold")
        plt.tight_layout()
        fig_to_st(fig)
        insight("Higher campus stress scores correlate with more platform sessions — proving product-market fit: students most in need are the ones actively using WellCampus.")

    with col2:
        st.markdown("#### Discount % vs Conversion")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=filtered_df, x="Converted", y="Discount_Percent",
                    palette={0: "#e63946", 1: "#4cc9a0"}, ax=ax)
        ax.set_xticklabels(["Not Converted", "Converted"])
        ax.set_ylabel("Discount %"); ax.set_title("Discount % by Conversion Outcome", fontweight="bold")
        plt.tight_layout()
        fig_to_st(fig)
        insight("Converted deals show slightly lower average discounts — indicating that price is not the primary decision driver. Value proposition and lead quality matter more.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: SALES PIPELINE EDA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 EDA: Sales Pipeline":
    st.title("📈 EDA — Sales Pipeline Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Conversion Rate by Lead Source")
        conv_src = filtered_df.groupby("Lead_Source")["Converted"].mean().sort_values(ascending=False) * 100
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(conv_src.index, conv_src.values, color=PALETTE[:len(conv_src)])
        ax.set_ylabel("Conversion Rate (%)"); ax.set_title("Conversion Rate by Lead Source", fontweight="bold")
        ax.tick_params(axis='x', rotation=20)
        for bar, val in zip(bars, conv_src.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f"{val:.1f}%", ha="center", fontsize=9)
        plt.tight_layout()
        fig_to_st(fig)
        insight("Referral and College Partnership channels show the highest conversion rates (often 2–3× vs Cold Email). Budget should be reallocated from digital ads to partnership development.")

    with col2:
        st.markdown("#### Avg Deal Value by Contract Type")
        deal_ct = filtered_df[filtered_df["Converted"]==1].groupby("Contract_Type")["Final_Deal_Value_INR"].mean() / 1e5
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(deal_ct.index, deal_ct.values, color=PALETTE[3:6])
        ax.set_ylabel("Avg Deal Value (₹ Lakhs)"); ax.set_title("Avg Deal Value by Contract Type", fontweight="bold")
        for i, val in enumerate(deal_ct.values):
            ax.text(i, val + 0.3, f"₹{val:.1f}L", ha="center", fontsize=9)
        plt.tight_layout()
        fig_to_st(fig)
        insight("Annual contracts deliver the highest deal values on average. Pushing prospects toward annual contracts should be a key sales objective to maximize ARR.")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Deal Size Category Distribution")
        dsc = filtered_df["Deal_Size_Category"].value_counts()
        order = ["Small", "Medium", "Large", "Enterprise"]
        dsc = dsc.reindex([o for o in order if o in dsc.index])
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(dsc.index, dsc.values, color=PALETTE[:4])
        ax.set_ylabel("Count"); ax.set_title("Deal Size Category Distribution", fontweight="bold")
        plt.tight_layout()
        fig_to_st(fig)
        insight("The pipeline is dominated by Small and Medium deals. However, a handful of Large/Enterprise deals likely account for disproportionate revenue — a classic 80/20 distribution.")

    with col2:
        st.markdown("#### Days in Pipeline by Stage")
        stage_order = ["Awareness", "Interest", "Demo", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
        fig, ax = plt.subplots(figsize=(6, 4))
        stage_data = [filtered_df[filtered_df["Pipeline_Stage"] == s]["Days_in_Pipeline"].values
                      for s in stage_order if s in filtered_df["Pipeline_Stage"].values]
        stage_labels = [s for s in stage_order if s in filtered_df["Pipeline_Stage"].values]
        bp = ax.boxplot(stage_data, labels=stage_labels, patch_artist=True)
        for patch, color in zip(bp['boxes'], PALETTE[:len(stage_data)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.tick_params(axis='x', rotation=25)
        ax.set_ylabel("Days in Pipeline"); ax.set_title("Pipeline Duration by Stage", fontweight="bold")
        plt.tight_layout()
        fig_to_st(fig)
        insight("Negotiation and Proposal stages show the widest spread in duration, indicating inconsistent sales execution at these critical stages — a training and process improvement opportunity.")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Lead Score Band vs Conversion Rate")
        lsb = filtered_df.groupby("Lead_Score_Band", observed=True)["Converted"].mean() * 100
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(lsb.index.astype(str), lsb.values, color=["#e63946", "#f4a261", "#2c7be5", "#4cc9a0"])
        ax.set_ylabel("Conversion Rate (%)"); ax.set_title("Conversion Rate by Lead Score Band", fontweight="bold")
        for i, val in enumerate(lsb.values):
            ax.text(i, val + 0.5, f"{val:.1f}%", ha="center", fontsize=9)
        plt.tight_layout()
        fig_to_st(fig)
        insight("Premium leads (score 80–100) convert at rates often 5–8× higher than Cold leads. This strongly validates using a lead scoring model to prioritize sales rep time.")

    with col2:
        st.markdown("#### Top Feature Priority — Student Survey")
        fp = filtered_df["Top_Feature_Priority"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(fp.index, fp.values, color=PALETTE[:len(fp)])
        ax.set_xlabel("Count"); ax.set_title("Most Wanted Feature (Student Survey)", fontweight="bold")
        for i, val in enumerate(fp.values):
            ax.text(val + 0.5, i, str(val), va="center", fontsize=9)
        plt.tight_layout()
        fig_to_st(fig)
        insight("Counseling Booking and Stress Tracker are the most demanded features — confirming the product roadmap should prioritize these above Meditation or Sleep Tracker for MVP launch.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5: STUDENT WELLNESS METRICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎓 Student Wellness Metrics":
    st.title("🎓 Student Wellness Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Stress Score Distribution by City Tier")
        fig, ax = plt.subplots(figsize=(6, 4))
        for tier, color in zip(["Tier 1", "Tier 2"], [PALETTE[0], PALETTE[2]]):
            data = filtered_df[filtered_df["City_Tier"] == tier]["Avg_Student_Stress_Score"]
            ax.hist(data, bins=15, alpha=0.6, label=tier, color=color, edgecolor="white")
        ax.set_xlabel("Avg Stress Score (out of 10)"); ax.set_ylabel("Frequency")
        ax.set_title("Stress Score by City Tier", fontweight="bold")
        ax.legend(); plt.tight_layout()
        fig_to_st(fig)
        insight("Tier 1 city colleges report marginally higher stress scores, likely due to more competitive academic environments — making them a high-priority target for WellCampus's outreach.")

    with col2:
        st.markdown("#### NPS Score Distribution")
        fig, ax = plt.subplots(figsize=(6, 4))
        nps_counts = filtered_df["Student_Satisfaction_NPS"].value_counts().sort_index()
        colors_nps = ["#e63946" if x <= 6 else "#f4a261" if x <= 8 else "#4cc9a0" for x in nps_counts.index]
        ax.bar(nps_counts.index, nps_counts.values, color=colors_nps, edgecolor="white")
        ax.set_xlabel("NPS Score (1–10)"); ax.set_ylabel("Count")
        ax.set_title("Student Satisfaction NPS Distribution", fontweight="bold")
        detractor = mpatches.Patch(color="#e63946", label="Detractors (1–6)")
        passive = mpatches.Patch(color="#f4a261", label="Passives (7–8)")
        promoter = mpatches.Patch(color="#4cc9a0", label="Promoters (9–10)")
        ax.legend(handles=[detractor, passive, promoter]); plt.tight_layout()
        fig_to_st(fig)
        insight("A significant share of Promoters (NPS 9–10) validates strong product satisfaction at early adopter colleges — ideal candidates for referral programs and case studies.")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Counseling Utilization by Course Type")
        fig, ax = plt.subplots(figsize=(6, 4))
        course_util = filtered_df.groupby("Course_Type")["Counseling_Utilization_Pct"].mean().sort_values(ascending=False)
        ax.bar(course_util.index, course_util.values, color=PALETTE[:len(course_util)])
        ax.set_ylabel("Avg Utilization (%)"); ax.set_title("Counseling Utilization by Course Type", fontweight="bold")
        ax.tick_params(axis='x', rotation=15)
        plt.tight_layout()
        fig_to_st(fig)
        insight("Medical and Engineering students show highest counseling utilization, confirming these as primary use-case segments. Sales decks should feature these verticals prominently.")

    with col2:
        st.markdown("#### Sessions Used vs Satisfaction NPS")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(filtered_df["Monthly_Sessions_Used"], filtered_df["Student_Satisfaction_NPS"],
                   color="#8338ec", alpha=0.4, s=30)
        m, b = np.polyfit(filtered_df["Monthly_Sessions_Used"], filtered_df["Student_Satisfaction_NPS"], 1)
        x_line = np.linspace(0, 20, 100)
        ax.plot(x_line, m * x_line + b, color="#e63946", linewidth=2, linestyle="--")
        ax.set_xlabel("Monthly Sessions Used"); ax.set_ylabel("Student Satisfaction NPS")
        ax.set_title("Platform Usage vs Student Satisfaction", fontweight="bold")
        plt.tight_layout()
        fig_to_st(fig)
        insight("Students who use WellCampus more frequently report higher NPS scores, validating that platform engagement directly drives satisfaction — a key retention and upsell metric.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6: DATA CLEANING LOG
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧹 Data Cleaning Log":
    st.title("🧹 Data Cleaning & Transformation Log")

    st.markdown("### Step-by-Step Cleaning Applied")
    steps = [
        ("1", "Duplicate Removal", f"{len(raw_df) - len(df)} duplicate Lead_IDs detected and removed using keep='first' strategy.", "Drop duplicates"),
        ("2", "Missing Value Imputation", "18 missing values in Lead_Source (~5%) filled with mode ('College Partnership') to preserve row count.", "fillna(mode)"),
        ("3", "Gender Standardization", "10 inconsistent entries (male, FEMALE, M, F, non binary) mapped to canonical values (Male, Female, Non-binary).", "String mapping"),
        ("4", "Outlier Clipping", "Lead_Score clipped to valid range [0, 100] to remove any data entry errors.", "clip(0, 100)"),
        ("5", "Feature Engineering", "Added: Converted (binary), Revenue_per_Student_INR, Lead_Score_Band, Deal_Size_Category, High_Stress_Campus.", "Derived columns"),
        ("6", "Categorical Encoding", "Label-encoded: Lead_Source, Pipeline_Stage, Contract_Type, City_Tier, Willingness_to_Pay for correlation analysis.", "Label encoding"),
    ]
    for step, name, desc, method in steps:
        with st.expander(f"Step {step}: {name}"):
            col1, col2 = st.columns([3, 1])
            col1.markdown(desc)
            col2.code(method)

    st.markdown("---")
    st.markdown("### Before vs After — Key Column Stats")
    comparison = pd.DataFrame({
        "Column": ["Lead_Source (nulls)", "Gender (inconsistent)", "Duplicate Rows", "Total Rows"],
        "Before Cleaning": [18, 10, 14, len(raw_df)],
        "After Cleaning": [0, 0, 0, len(df)],
    })
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Sample — Cleaned Dataset (First 20 Rows)")
    st.dataframe(df.head(20), use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("⬇️ Download Raw Dataset (CSV)",
                           data=raw_df.to_csv(index=False).encode(),
                           file_name="wellcampus_raw_data.csv", mime="text/csv")
    with col2:
        st.download_button("⬇️ Download Cleaned Dataset (CSV)",
                           data=df.to_csv(index=False).encode(),
                           file_name="wellcampus_cleaned_data.csv", mime="text/csv")
