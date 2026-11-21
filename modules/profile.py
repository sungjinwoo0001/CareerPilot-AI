
import fitz
import json
from ai_engine import client


def extract_resume_text(uploaded_file):
    """Extract text from an uploaded PDF resume."""
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    text = ""
    for page in pdf:
        text += page.get_text() + "\n"

    pdf.close()
    return text


def analyze_resume(resume_text):
    """Use Groq to extract a structured candidate profile."""

    prompt = f"""
    Analyze the following resume and extract the candidate's information.

    Return ONLY valid JSON in this format:

    {{
        "name": "",
        "education": [],
        "skills": [],
        "programming_languages": [],
        "projects": [],
        "experience": [],
        "certifications": [],
        "strengths": [],
        "missing_information": []
    }}

    Do not invent information.
    If something is missing, leave it empty.

    RESUME:
    {resume_text}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are an expert resume analyzer. Return valid JSON only."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content

    # Remove Markdown code fences if the model adds them
    result = result.replace("```json", "").replace("```", "").strip()

    return json.loads(result)


def save_profile(profile, filename="candidate_profile.json"):
    """Save the extracted profile."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=4, ensure_ascii=False)

    return True
