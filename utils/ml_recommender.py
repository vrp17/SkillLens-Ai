import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def train_skill_model(job_descriptions):
    
    #Train TF-IDF model on job descriptions
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(job_descriptions)

    return vectorizer, tfidf_matrix

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import math


def recommend_next_skills(
    input_skills,
    role_jobs,
    all_skills,
    top_n=8
):
    """
    ML-based skill recommendation with frequency + similarity + IDF weighting
    """

    corpus = role_jobs["description"].tolist()
    total_jobs = len(corpus)

    # Train TF-IDF on role-specific jobs
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # User input vector
    input_text = " ".join(input_skills)
    input_vector = vectorizer.transform([input_text])

    # Cosine similarity (per job)
    similarity_scores = cosine_similarity(input_vector, tfidf_matrix)[0]

    skill_scores = {}
    skill_job_count = {}

    # Count skill occurrences per job
    for desc in corpus:
        for skill in all_skills:
            if skill in desc:
                skill_job_count[skill] = skill_job_count.get(skill, 0) + 1

    # Score skills
    for idx, desc in enumerate(corpus):
        for skill in all_skills:
            if skill in desc and skill not in input_skills:
                tf_sim = similarity_scores[idx]
                freq = skill_job_count.get(skill, 1)

                # Inverse frequency weighting
                idf_weight = math.log((total_jobs + 1) / freq)

                score = tf_sim * freq * idf_weight
                skill_scores[skill] = skill_scores.get(skill, 0) + score

    if not skill_scores:
        return pd.DataFrame(columns=["Skill", "Priority"])

    df = pd.DataFrame(skill_scores.items(), columns=["Skill", "Priority"])

    # Normalize 0–1
    df["Priority"] = df["Priority"] / df["Priority"].max()

    # Round for UI
    df["Priority"] = df["Priority"].round(4)

    return df.sort_values("Priority", ascending=False).head(top_n)
