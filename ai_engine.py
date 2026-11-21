
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def test_connection():
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": "Reply with: CareerPilot AI connected successfully!"}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print(test_connection())
