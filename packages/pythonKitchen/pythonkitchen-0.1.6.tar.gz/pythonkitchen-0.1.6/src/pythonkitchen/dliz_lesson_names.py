import os
import pandas as pd
from pathlib import Path
import openai
from dotenv import load_dotenv
import time

# Load env for OPENAI_API_KEY
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
assert openai.api_key, "OPENAI_API_KEY not found in environment or .env file"

INPUT_CSV = '/Users/suhail/Desktop/deeplizard_lessons.csv'
OUTPUT_CSV = '/Users/suhail/Desktop/deeplizard_lessons_short_names.csv'

def generate_short_name(long_name):
    """Use OpenAI to generate a concise lesson name."""
    prompt = (
        f"The following is a lesson title:\n"
        f"\"{long_name}\"\n\n"
        f"Create a short, concise, human-friendly name for this lesson. "
        f"Keep it to 2-5 words. Do NOT repeat 'course', 'chapter', or similar. "
        f"Return only the name, no commentary or punctuation."
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant specialized in summarizing lesson titles into short, catchy names."},
        {"role": "user", "content": prompt}
    ]
    # You may want to rate-limit here if you have many rows!
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_completion_tokens=15,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def main():
    df = pd.read_csv(INPUT_CSV)
    # The 'description' column is your current long lesson title
    long_names = df['description'].astype(str).tolist()
    short_names = []
    for long_name in long_names:
        try:
            short = generate_short_name(long_name)
        except Exception as e:
            print(f"Error for '{long_name}': {e}")
            short = ""
        short_names.append(short)
        time.sleep(0.8)  # To be gentle on API

    df.insert(df.columns.get_loc('description') + 1, 'short_name', short_names)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved output to {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
