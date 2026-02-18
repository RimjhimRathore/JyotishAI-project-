import os 
from dotenv import load_dotenv 
load_dotenv() 
GROK_API_KEY = os.getenv("GROK_API_KEY") 
from groq import Groq 
def get_output(dob,time,place): 
    client = Groq( api_key=GROK_API_KEY, ) 
    prompt = f"""Act as a professional Vedic astrologer.

Generate a complete Janam Kundali (birth chart) using traditional Vedic astrology based on the following birth details:

Date of Birth: {dob} 
Time of Birth: {time}
Place of Birth: {place}
Provide the analysis under the following headings:

- Ascendant (Lagna) and Rashi
- Moon Sign and Sun Sign
- Nakshatra and Pada
- Manglik Dosha Analysis
- Planet Strength Analysis
- Personality Traits
- Career Indications
- Marriage and Relationships


IMPORTANT INSTRUCTIONS:

1. Return the result ONLY in valid JSON format.
2. Do NOT include any explanations, markdown, or extra text.
3. Each heading must be a JSON key.
4. The corresponding detailed description must be the value (as a string).
5. Use clear, human-readable descriptions as values.
6. Ensure the JSON is properly formatted and parseable.



"""
    chat_completion = client.chat.completions.create( messages=[ { "role": "user", "content": prompt, } ], model="llama-3.3-70b-versatile", ) 
    return chat_completion.choices[0].message.content 
if __name__ == "__main__":
    result = 10

     