import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import random
import os

np.random.seed(42)
random.seed(42)
N = 350

# --- Reference Lists ---
colleges = [
    "IIT Delhi", "IIT Bombay", "Delhi University", "Mumbai University",
    "Pune University", "VIT Vellore", "SRM Chennai", "Manipal University",
    "Amity University", "BITS Pilani", "Christ University", "Symbiosis Pune",
    "Jamia Millia", "Osmania University", "Anna University"
]
cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune", "Chennai",
          "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]
city_tiers = {"Mumbai": "Tier 1", "Delhi": "Tier 1", "Bangalore": "Tier 1",
              "Hyderabad": "Tier 1", "Pune": "Tier 1", "Chennai": "Tier 1",
              "Kolkata": "Tier 2", "Ahmedabad": "Tier 2", "Jaipur": "Tier 2", "Lucknow": "Tier 2"}
lead_sources = ["LinkedIn", "College Partnership", "Referral", "Google Ads", "Cold Email", "Conference"]
pipeline_stages = ["Awareness", "Interest", "Demo", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
decision_makers = ["Dean of Students", "HOD Wellness", "Registrar", "VP Academics", "Director"]
contract_types = ["Annual", "Semester", "Pilot (3 months)"]
payment_methods = ["Bank Transfer", "Cheque", "Online Portal"]
genders = ["Male", "Female", "Non-binary"]
course_types = ["Engineering", "MBA", "Medical", "Arts & Science", "Law"]

# --- Generate Raw Synthetic Data ---
lead_ids = [f"LC{str(i).zfill(4)}" for i in range(1, N+1)]
college_names = [random.choice(colleges) for _ in range(N)]
city_col = [random.choice(cities) for _ in range(N)]
tier_col = [city_tiers[c] for c in city_col]
lead_source = [random.choice(lead_sources) for _ in range(N)]
decision_maker = [random.choice(decision_makers) for _ in range(N)]
contract_type = [random.choice(contract_types) for _ in range(N)]
course_type = [random.choice(course_types) for _ in range(N)]

# Lead score (0-100), higher for referral/partner
lead_score = []
for src in lead_source:
    base = {"LinkedIn": 55, "College Partnership": 75, "Referral": 80,
            "Google Ads": 45, "Cold Email": 35, "Conference": 65}[src]
    lead_score.append(min(100, max(0, int(np.random.normal(base, 12)))))

# Pipeline stage weighted by lead score
def assign_stage(score):
    if score >= 80:
        return np.random.choice(pipeline_stages, p=[0.05, 0.05, 0.10, 0.15, 0.15, 0.40, 0.10])
    elif score >= 60:
        return np.random.choice(pipeline_stages, p=[0.10, 0.15, 0.20, 0.20, 0.10, 0.15, 0.10])
    elif score >= 40:
        return np.random.choice(pipeline_stages, p=[0.20, 0.20, 0.20, 0.10, 0.05, 0.05, 0.20])
    else:
        return np.random.choice(pipeline_stages, p=[0.35, 0.25, 0.15, 0.05, 0.02, 0.03, 0.15])

stage = [assign_stage(s) for s in lead_score]

# Student count per college (affects deal size)
student_count = [random.randint(2000, 25000) for _ in range(N)]

# Deal value based on student count and contract type
deal_value = []
for i in range(N):
    base_per_student = {"Annual": 120, "Semester": 70, "Pilot (3 months)": 40}[contract_type[i]]
    val = int(student_count[i] * base_per_student * np.random.uniform(0.6, 1.2))
    deal_value.append(val)

# Discount (%) — higher for large deals / cold leads
discount_pct = []
for i in range(N):
    base_disc = 5 if lead_score[i] > 70 else 15 if lead_score[i] > 50 else 22
    discount_pct.append(round(min(35, max(0, np.random.normal(base_disc, 5))), 1))

final_deal_value = [int(deal_value[i] * (1 - discount_pct[i]/100)) for i in range(N)]

# Introduce intentional dirty data (nulls, inconsistencies) for cleaning task
# ~5% nulls in lead_source
lead_source_dirty = lead_source.copy()
for i in random.sample(range(N), 18):
    lead_source_dirty[i] = None

# ~3% inconsistent gender entries
gender = [random.choice(genders) for _ in range(N)]
gender_dirty = gender.copy()
for i in random.sample(range(N), 10):
    gender_dirty[i] = random.choice(["male", "FEMALE", "M", "F", "non binary"])

# ~4% duplicate rows (will mark same lead_id)
dup_indices = random.sample(range(N), 14)

# Student-level metrics
avg_stress_score = [round(np.random.uniform(4, 9), 1) for _ in range(N)]  # out of 10
sessions_per_month = [max(0, int(np.random.normal(8, 3))) for _ in range(N)]
satisfaction_nps = [random.randint(1, 10) for _ in range(N)]
counseling_utilization_pct = [round(np.random.uniform(10, 85), 1) for _ in range(N)]

# Survey fields
pain_point_rating = [random.randint(1, 10) for _ in range(N)]   # how painful is current situation
willingness_to_pay = [random.choice(["High", "Medium", "Low"]) for _ in range(N)]
feature_priority = [random.choice(["Counseling Booking", "Stress Tracker", "Meditation", "Peer Support", "Sleep Tracker"]) for _ in range(N)]

# Time in pipeline (days)
days_in_pipeline = [random.randint(7, 180) for _ in range(N)]

# Close date (month)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
close_month = [random.choice(months) for _ in range(N)]

payment_method = [random.choice(payment_methods) if stage[i] == "Closed Won" else None for i in range(N)]

# Build raw DataFrame
raw_df = pd.DataFrame({
    "Lead_ID": lead_ids,
    "College_Name": college_names,
    "City": city_col,
    "City_Tier": tier_col,
    "Lead_Source": lead_source_dirty,
    "Decision_Maker_Role": decision_maker,
    "Course_Type": course_type,
    "Student_Count": student_count,
    "Lead_Score": lead_score,
    "Pipeline_Stage": stage,
    "Contract_Type": contract_type,
    "Days_in_Pipeline": days_in_pipeline,
    "Deal_Value_INR": deal_value,
    "Discount_Percent": discount_pct,
    "Final_Deal_Value_INR": final_deal_value,
    "Payment_Method": payment_method,
    "Close_Month": close_month,
    "Gender_of_Contact": gender_dirty,
    "Avg_Student_Stress_Score": avg_stress_score,
    "Monthly_Sessions_Used": sessions_per_month,
    "Student_Satisfaction_NPS": satisfaction_nps,
    "Counseling_Utilization_Pct": counseling_utilization_pct,
    "Pain_Point_Rating": pain_point_rating,
    "Willingness_to_Pay": willingness_to_pay,
    "Top_Feature_Priority": feature_priority,
})

# Mark duplicates
for i in dup_indices:
    raw_df.loc[i, "Lead_ID"] = raw_df.loc[min(i+1, N-1), "Lead_ID"]

# --- Save RAW dataset ---
raw_df.to_csv("/home/claude/wellcampus/wellcampus_raw_data.csv", index=False)

# ============================================================
# CLEANED DATASET
# ============================================================
clean_df = raw_df.copy()

# 1. Remove duplicates
clean_df = clean_df.drop_duplicates(subset=["Lead_ID"], keep="first").reset_index(drop=True)

# 2. Fill missing Lead_Source with mode
clean_df["Lead_Source"] = clean_df["Lead_Source"].fillna(clean_df["Lead_Source"].mode()[0])

# 3. Standardize Gender
gender_map = {"male": "Male", "FEMALE": "Female", "M": "Male", "F": "Female",
              "non binary": "Non-binary", "Male": "Male", "Female": "Female", "Non-binary": "Non-binary"}
clean_df["Gender_of_Contact"] = clean_df["Gender_of_Contact"].map(lambda x: gender_map.get(x, x))

# 4. Treat outliers in Lead_Score (clip to 0-100)
clean_df["Lead_Score"] = clean_df["Lead_Score"].clip(0, 100)

# 5. Derived columns
clean_df["Converted"] = (clean_df["Pipeline_Stage"] == "Closed Won").astype(int)
clean_df["Revenue_per_Student_INR"] = (clean_df["Final_Deal_Value_INR"] / clean_df["Student_Count"]).round(2)
clean_df["Lead_Score_Band"] = pd.cut(clean_df["Lead_Score"], bins=[0,40,60,80,100],
                                      labels=["Cold", "Warm", "Hot", "Premium"])
clean_df["Deal_Size_Category"] = pd.cut(clean_df["Final_Deal_Value_INR"],
                                          bins=[0, 500000, 1500000, 3000000, 99999999],
                                          labels=["Small", "Medium", "Large", "Enterprise"])
clean_df["High_Stress_Campus"] = (clean_df["Avg_Student_Stress_Score"] >= 7).astype(int)

# 6. Encode categorical for correlation
le_map = {}
for col in ["Lead_Source", "Pipeline_Stage", "Contract_Type", "City_Tier",
            "Willingness_to_Pay", "Lead_Score_Band", "Deal_Size_Category"]:
    codes, uniques = pd.factorize(clean_df[col])
    clean_df[f"{col}_Code"] = codes
    le_map[col] = dict(enumerate(uniques))

clean_df.to_csv("/home/claude/wellcampus/wellcampus_cleaned_data.csv", index=False)
print(f"Raw rows: {len(raw_df)} | Cleaned rows: {len(clean_df)}")
print("Datasets saved.")
