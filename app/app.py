import sys
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from utils.skill_analysis import get_skill_demand, get_missing_skills


# Load Data

data_path = os.path.join(PROJECT_ROOT, "data")

jobs = pd.read_csv(os.path.join(data_path, "job_descriptions.csv"))
skills_df = pd.read_csv(os.path.join(data_path, "skill_dictionary.csv"))

# Valid skills set (for validation)
VALID_SKILLS = set(skills_df["skill"].str.lower().tolist())


# Text Cleaning

import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z ]', '', text)
    return text

jobs["clean_description"] = jobs["description"].apply(clean_text)


# Skill Extraction

skill_list = skills_df["skill"].tolist()

def extract_skills(text):
    return [skill for skill in skill_list if skill in text]

jobs["extracted_skills"] = jobs["clean_description"].apply(extract_skills)


# Streamlit UI

st.set_page_config(page_title="SkillLens", layout="centered")

st.title("🔍 SkillLens")
st.subheader("AI-Based Job Skill Gap Analyzer")

st.write(
    "Analyze job descriptions and find out which skills you should learn next."
)


# Skill Demand

skill_demand = get_skill_demand(jobs["extracted_skills"])

demand_df = pd.DataFrame(
    skill_demand.items(),
    columns=["Skill", "Demand"]
).sort_values(by="Demand", ascending=False)

st.markdown("### 📊 Market Skill Demand")
st.dataframe(demand_df)


# Visualization

st.markdown("### 📈 Skill Demand Chart")

fig, ax = plt.subplots()
ax.bar(demand_df["Skill"], demand_df["Demand"])
plt.xticks(rotation=45)
st.pyplot(fig)


# User Input

st.markdown("### 🧑‍💻 Your Skills")
user_skills = st.text_input(
    "Enter your skills (comma separated)",
    placeholder="python, sql"
)

missing_skills = []


if user_skills:
    user_skill_list = [s.strip().lower() for s in user_skills.split(",")]

    # Separate valid and invalid skills
    valid_input_skills = [s for s in user_skill_list if s in VALID_SKILLS]
    invalid_input_skills = [s for s in user_skill_list if s not in VALID_SKILLS]

    if not valid_input_skills:
        st.error("❌ Please enter at least one valid technical skill.")
        st.info(f"Valid skills include: {', '.join(sorted(list(VALID_SKILLS))[:8])} ...")

    else:
        if invalid_input_skills:
            st.warning(f"⚠️ Ignored invalid skills: {', '.join(invalid_input_skills)}")

        missing_skills = get_missing_skills(
            market_skills=demand_df["Skill"].tolist(),
            user_skills=valid_input_skills
        )

        st.markdown("### 🎯 Skills You Should Learn Next")
        if missing_skills:
            st.success(", ".join(missing_skills))
        else:
            st.success("You already have all required skills! 🎉")


   