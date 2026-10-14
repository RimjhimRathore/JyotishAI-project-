import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")   # same .env name you already use
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

SECTIONS = [
    "Personality Traits",
    "Career Indications",
    "Marriage and Relationships",
    "Manglik Dosha Analysis",
    "Planet Strength Analysis",
    "Finance and Wealth",
    "Health and Wellbeing",
]


def chart_to_text(chart):
    """Turn the calculated chart into plain text the AI can read."""
    lagna = chart["lagna"]
    lines = [f"Lagna (Ascendant): {lagna['sign']} {lagna['degree']}°, "
             f"{lagna['nakshatra']} pada {lagna['pada']}"]
    for name, p in chart["planets"].items():
        retro = " (retrograde)" if p["retrograde"] else ""
        lines.append(f"{name}: {p['sign']} {p['degree']}°, house {p['house']}, "
                     f"{p['nakshatra']} pada {p['pada']}{retro}")
    return "\n".join(lines)


def get_output(chart):
    client = Groq(api_key=GROK_API_KEY)
    keys = ", ".join(f'"{s}"' for s in SECTIONS)

    prompt = f"""You are an expert Vedic (Jyotish) astrologer.

Below is an ALREADY CALCULATED sidereal (Lahiri) birth chart using whole-sign houses.
Do NOT recalculate or change any placement. Only interpret what is given.

{chart_to_text(chart)}

For each section, write 4-6 clear sentences in simple language that an ordinary
person can understand. Base every point on the specific planets, signs and houses
above, and mention which placement you are using.

Return ONLY a JSON object with exactly these keys: {keys}.
Each value must be a plain string."""

    resp = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    return resp.choices[0].message.content