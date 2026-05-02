# recommender.py — SoundSense Hybrid Recommendation Engine


import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


def build_content_matrix(df: pd.DataFrame) -> np.ndarray:

    df = df.copy()
    df["text_features"] = (
        df["artist"] + " " +
        df["genre"]  + " " +
        df["mood"]   + " " +
        df["language"]
    )

    tfidf   = TfidfVectorizer(stop_words="english")
    tfidf_m = tfidf.fit_transform(df["text_features"]).toarray()

    # Numeric audio features
    numeric_cols = ["energy", "danceability", "valence", "tempo_bpm", "popularity"]
    scaler  = MinMaxScaler()
    num_m   = scaler.fit_transform(df[numeric_cols])

    combined = np.hstack([tfidf_m * 0.6, num_m * 0.4])
    return combined


def get_content_scores(song_idx: int, matrix: np.ndarray) -> np.ndarray:
    """Cosine similarity of the target song against all songs."""
    vec = matrix[song_idx].reshape(1, -1)
    return cosine_similarity(vec, matrix).flatten()


def get_session_scores(
    session_history: list[str],
    df: pd.DataFrame,
    matrix: np.ndarray,
) -> np.ndarray:
    if not session_history:
        return np.zeros(len(df))

    song_lower = df["song"].str.lower().tolist()
    indices    = []
    for name in session_history:
        try:
            indices.append(song_lower.index(name.lower()))
        except ValueError:
            pass

    if not indices:
        return np.zeros(len(df))

    profile = matrix[indices].mean(axis=0).reshape(1, -1)
    return cosine_similarity(profile, matrix).flatten()

# Hybrid recommender
def get_recommendations(
    song_name:       str,
    df:              pd.DataFrame,
    session_history: list[str] | None = None,
    top_n:           int = 5,
    content_weight:  float = 0.7,
) -> pd.DataFrame | None:

    song_lower = df["song"].str.lower().tolist()
    query      = song_name.lower()

    if query not in song_lower:
        return None

    idx    = song_lower.index(query)
    matrix = build_content_matrix(df)

    c_scores = get_content_scores(idx, matrix)

    history   = session_history or []
    s_scores  = get_session_scores(history, df, matrix)

    session_weight = 1 - content_weight if history else 0.0
    c_w            = 1.0 if not history else content_weight

    final_scores = c_w * c_scores + session_weight * s_scores

    scored = list(enumerate(final_scores))
    scored = sorted(scored, key=lambda x: x[1], reverse=True)
    scored = [s for s in scored if s[0] != idx]

    top_indices = [s[0] for s in scored[:top_n]]
    top_scores  = [round(s[1], 3) for s in scored[:top_n]]

    result = df.iloc[top_indices][
        ["song", "artist", "genre", "mood", "language",
         "energy", "danceability", "valence"]
    ].reset_index(drop=True)

    result["match_score"] = top_scores
    result.index += 1
    return result


# Mood based

def get_by_mood(mood: str, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Return top_n songs for a given mood, ranked by popularity."""
    filtered = df[df["mood"].str.lower() == mood.lower()].copy()
    filtered  = filtered.sort_values("popularity", ascending=False)
    return filtered[["song", "artist", "genre", "mood", "language"]].head(top_n)