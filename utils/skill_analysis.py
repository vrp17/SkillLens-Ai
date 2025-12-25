from collections import Counter

def get_skill_demand(extracted_skills):
    """
    Takes a list of skill lists and returns skill demand count
    """
    all_skills = []
    for skills in extracted_skills:
        all_skills.extend(skills)

    return Counter(all_skills)


def get_missing_skills(market_skills, user_skills):
    """
    Compares market skills with user skills
    """
    return sorted(set(market_skills) - set(user_skills))
