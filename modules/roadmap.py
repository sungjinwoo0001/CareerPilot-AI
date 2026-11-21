
from ai_engine import client
import json



def generate_roadmap(
    candidate_profile,
    skill_gap,
    target_role,
    duration_weeks=12,
    interview_history=None,
    completed_tasks=None
):
    interview_history = interview_history or []
    completed_tasks = completed_tasks or []

    prompt = f"""
    You are an adaptive AI career mentor.

    Create a realistic {duration_weeks}-week learning roadmap.

    Candidate:
    {json.dumps(candidate_profile, indent=2)}

    Target role:
    {target_role}

    Skill gap:
    {json.dumps(skill_gap, indent=2)}

    Previous interview performance:
    {json.dumps(interview_history, indent=2)}

    Completed learning tasks:
    {json.dumps(completed_tasks, indent=2)}

    Return ONLY valid JSON:
    {{
        "roadmap": [
            {{
                "week": 1,
                "focus": "",
                "skills": [],
                "tasks": [],
                "deliverable": "",
                "reason": ""
            }}
        ],
        "adaptation_summary": ""
    }}

    Rules:
    - Create exactly {duration_weeks} weeks.
    - Prioritize skills the candidate is missing.
    - Use interview feedback to identify weak areas.
    - Do not repeat completed tasks.
    - Increase difficulty gradually.
    - Include practical coding tasks.
    - Make every deliverable measurable.
    - Explain why the roadmap was adapted.
    - Never assume the candidate knows a missing skill.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are an adaptive career mentor. Return valid JSON only."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    result = response.choices[0].message.content
    result = result.replace("```json", "").replace("```", "").strip()

    return json.loads(result)

