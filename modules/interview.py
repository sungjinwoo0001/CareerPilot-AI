
from ai_engine import client
import json


def generate_interview_question(target_role, difficulty, previous_questions=None):
    previous_questions = previous_questions or []

    prompt = f"""
    Generate one realistic interview question for this role.

    Target role: {target_role}
    Difficulty: {difficulty}
    Previous questions: {json.dumps(previous_questions)}

    Return ONLY valid JSON:

    {{
        "question": "",
        "topic": "",
        "difficulty": ""
    }}

    Do not repeat previous questions.
    """ 

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a professional technical interviewer. Return valid JSON only."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    result = response.choices[0].message.content
    result = result.replace("```json", "").replace("```", "").strip()

    return json.loads(result)


def evaluate_answer(question, answer, target_role):
    prompt = f"""
    Evaluate this candidate's interview answer.

    Role: {target_role}
    Question: {question}
    Candidate answer: {answer}

    Return ONLY valid JSON:

    {{
        "score": 0,
        "technical_accuracy": 0,
        "clarity": 0,
        "relevance": 0,
        "strengths": [],
        "improvements": [],
        "ideal_answer": ""
    }}

    Rules:
    - Score each numeric field from 0 to 10.
    - Be fair and specific.
    - Do not reward incorrect technical claims.
    - Give actionable feedback.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a strict but fair technical interview evaluator. Return valid JSON only."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content
    result = result.replace("```json", "").replace("```", "").strip()

    return json.loads(result)