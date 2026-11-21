
from ai_engine import client
import json


def analyze_skill_gap(candidate_profile, target_role, job_description):
    prompt = f"""
    You are an expert career analyst.

    Compare the candidate's skills with the target job role.

    Candidate profile:
    {json.dumps(candidate_profile, indent=2)}

    Target role:
    {target_role}

    Job description:
    {job_description}

    Return ONLY valid JSON in this format:

    {{
        "matched_skills": [],
        "missing_skills": [],
        "partially_matched_skills": [],
        "priority_skills": [],
        "match_percentage": 0,
        "analysis": ""
    }}

    Rules:
    - Never invent candidate skills.
    - Identify skills explicitly required by the job description.
    - Prioritize missing skills by importance.
    - Match percentage must be between 0 and 100.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a professional career skill-gap analyst. Return valid JSON only."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content
    result = result.replace("```json", "").replace("```", "").strip()

    return json.loads(result)