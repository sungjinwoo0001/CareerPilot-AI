
from ai_engine import client
import json


def generate_projects(candidate_profile, skill_gap, target_role):
    prompt = f"""
    You are an expert technical project mentor.

    Recommend 3 portfolio projects that help this candidate
    become suitable for the target role.

    Candidate:
    {json.dumps(candidate_profile, indent=2)}

    Skill gaps:
    {json.dumps(skill_gap, indent=2)}

    Target role:
    {target_role}

    Return ONLY valid JSON in this format:

    {{
        "projects": [
            {{
                "title": "",
                "difficulty": "",
                "problem_statement": "",
                "technologies": [],
                "skills_covered": [],
                "key_features": [],
                "expected_outcome": ""
            }}
        ]
    }}

    Rules:
    - Recommend exactly 3 projects.
    - Projects must address the candidate's missing skills.
    - Avoid generic beginner projects.
    - Make projects realistic and suitable for a GitHub portfolio.
    - Include measurable outcomes.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a technical project mentor. Return valid JSON only."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    result = response.choices[0].message.content
    result = result.replace("```json", "").replace("```", "").strip()

    return json.loads(result)
