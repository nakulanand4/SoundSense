# ollama_search.py — SoundSense Natural Language Search (Local LLM)
import json
import requests
import numpy as np
import pandas as pd

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

MOODS = ["Happy", "Sad", "Romantic", "Energetic", "Dark", "Calm", "Melancholic", "Motivational"]
GENRES = ["Pop", "Rock", "Hip Hop", "Electronic", "Bollywood Pop", "Bollywood Rock", "R&B", "Indie Pop", "Folk", "Sufi",
          "Punjabi Pop"]
LANGUAGES = ["English", "Hindi"]


def _call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["response"]
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Ollama! Please make sure the Ollama app is running on your computer.")


def parse_query(user_query: str) -> dict:
    prompt = f"""
You are a music preference parser. Extract structured preferences from the user's query.
User query: "{user_query}"
Available moods: {', '.join(MOODS)}
Available genres: {', '.join(GENRES)}
Available languages: {', '.join(LANGUAGES)}

Return ONLY a valid JSON object with these keys:
- "mood": array
- "genre": array
- "language": array
- "energy": float 0.0 to 1.0, or null
- "valence": float 0.0 to 1.0, or null
- "explanation": string explaining the logic
"""
    raw_response = _call_ollama(prompt)
    return json.loads(raw_response)


def search_by_query(user_query: str, df: pd.DataFrame, top_n: int = 8) -> tuple[pd.DataFrame, str]:
    parsed = parse_query(user_query)
    explanation = parsed.get("explanation", "")

    scores = np.ones(len(df), dtype=float)

    if parsed.get("mood"):
        moods_lower = [m.lower() for m in parsed["mood"]]
        scores += df["mood"].str.lower().isin(moods_lower).astype(float) * 2.0

    if parsed.get("genre"):
        genres_lower = [g.lower() for g in parsed["genre"]]
        scores += df["genre"].str.lower().isin(genres_lower).astype(float) * 1.5

    if parsed.get("language"):
        langs_lower = [l.lower() for l in parsed["language"]]
        scores += df["language"].str.lower().isin(langs_lower).astype(float) * 1.0

    if parsed.get("energy") is not None:
        scores += (1 - abs(df["energy"] - float(parsed["energy"]))) * 1.0

    scores += (df["popularity"] / 100) * 0.3

    df_result = df.copy()
    df_result["_score"] = scores
    df_result = df_result.sort_values("_score", ascending=False).head(top_n)
    df_result = df_result[
        ["song", "artist", "genre", "mood", "language", "energy", "danceability", "valence"]].reset_index(drop=True)
    df_result.index += 1

    return df_result, explanation