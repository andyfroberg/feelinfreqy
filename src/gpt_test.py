from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


client = OpenAI(
    api_key = os.getenv("OPEN_AI_API_KEY", default=None)
)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You will be provided with a description of a mood, and your task is to generate a list of ten songs that matches it."},
    {"role": "user", "content": "Energetic and happy."}
  ],
  temperature=0,
  max_tokens=1024
)

print(completion.choices[0].message)