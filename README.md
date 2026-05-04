# SoundSense — Intelligent Music Recommendation System

> Nakul Anand | 2026

SoundSense is a hybrid music recommendation web app built with Streamlit. It combines TF-IDF content-based filtering with session-aware collaborative signals and a local LLM (Ollama/Llama3) for natural language search — wrapped in a dark, animated UI with an embedded YouTube player, Firebase email authentication, and persistent user profiles.

## Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://soundsense.streamlit.app/)

> **Note:** The "Ask AI" tab requires Ollama running locally and won't work on the hosted demo. Everything else works fine.

---

## Features

- **Content-Based Recommendations** — TF-IDF vectorization on artist, genre, mood, and language, combined with normalized audio features (energy, danceability, valence, tempo, popularity) using cosine similarity
- **Hybrid Mode** — Once you play or like songs, the engine builds a taste profile from your history and blends it (30%) with content scores (70%) for personalized results
- **Mood Discovery** — Browse curated top songs across 8 moods: Happy, Sad, Romantic, Energetic, Dark, Calm, Melancholic, Motivational
- **Natural Language Search (Ask AI)** — Powered by a locally running Ollama model (Llama3). Type things like *"sad slow songs for a rainy night"* and it parses your intent into structured filters
- **Embedded YouTube Player** — Finds and embeds audio for any song directly in the app
- **Email Authentication** — Sign up and log in with email and password via Firebase Auth
- **Persistent User Profiles** — Play history and liked songs are saved to Firebase Firestore per user, so your taste profile carries over across sessions and devices

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Recommendation Engine | scikit-learn (TF-IDF, cosine similarity, MinMaxScaler) |
| NL Search | Ollama (Llama3, local) via REST API |
| Auth | Firebase Authentication (email/password) |
| Database | Firebase Firestore |
| Data | pandas, numpy |
| YouTube Player | requests + regex scraping |
| Language | Python 3.11+ |

---

## Project Structure

```
SoundSense/
├── app.py                # Main Streamlit app — UI, layout, session state, auth
├── recommender.py        # Hybrid recommendation engine (TF-IDF + session scoring)
├── ollama_search.py      # Natural language query parser using local Llama3
├── music_player.py       # YouTube embed URL fetcher and player renderer
├── dataset.csv           # Music dataset with audio features
├── requirements.txt      # Python dependencies
└── .streamlit/
    └── secrets.toml      # API keys and credentials (not committed to repo)
```

---

## How the Recommendation Engine Works

### Content-Based Scoring

Each song gets a feature vector built from two parts:

1. **Text features** (weighted 60%) — TF-IDF on a combined string of `artist + genre + mood + language`
2. **Audio features** (weighted 40%) — MinMax-normalized values for `energy`, `danceability`, `valence`, `tempo_bpm`, `popularity`

These are concatenated into a single matrix. When you pick a song, cosine similarity is computed between that song's vector and every other song in the dataset.

### Hybrid Session Scoring

When you've played or liked songs, the app builds a **taste profile** by averaging the feature vectors of those songs. This profile is scored against the full dataset via cosine similarity. The final score is:

```
final_score = 0.7 × content_score + 0.3 × session_score
```

If no history exists, it falls back to pure content-based scoring.

### Natural Language Search (Ask AI)

The "Ask AI" tab sends your query to a locally running Ollama instance. A structured prompt asks Llama3 to extract `mood`, `genre`, `language`, `energy`, and `valence` as JSON. Those parsed values are then used to score songs using weighted matching:

- Mood match → +2.0
- Genre match → +1.5
- Language match → +1.0
- Energy proximity → +1.0
- Popularity boost → +0.3

### User Profiles (Firebase)

When logged in, every play and like is written to Firestore under the user's email as a document ID. On next login, that history is pulled back into session state so the hybrid engine immediately has context to personalize from.

---

## Dataset

`dataset.csv` contains songs with the following columns:

| Column | Description |
|---|---|
| `song` | Song title |
| `artist` | Artist name |
| `genre` | Genre (Pop, Rock, Bollywood Pop, Sufi, etc.) |
| `mood` | Mood tag (Happy, Sad, Romantic, etc.) |
| `language` | Hindi or English |
| `energy` | Float 0–1, how energetic the track is |
| `danceability` | Float 0–1 |
| `valence` | Float 0–1, musical positivity |
| `tempo_bpm` | Beats per minute |
| `popularity` | 0–100 score |

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- A Firebase project with Authentication (email/password) and Firestore enabled
- [Ollama](https://ollama.com/) installed and running locally (only needed for the "Ask AI" tab)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/nakulanand4/SoundSense.git
cd SoundSense

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pull the Llama3 model (for Ask AI tab only)
ollama pull llama3

# 4. Add your secrets
mkdir -p .streamlit
touch .streamlit/secrets.toml
# fill in secrets.toml (see format below)

# 5. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

### secrets.toml format

```toml
FIREBASE_WEB_API_KEY = "your-firebase-web-api-key"

[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

> `secrets.toml` is listed in `.gitignore` and never committed to the repo.

---

## Known Limitations

- YouTube embed relies on scraping search results and can occasionally pick the wrong video for less popular songs
- The Ask AI tab requires Ollama running locally — it won't work on the hosted demo
- The Ask AI tab can be slow (5–15 seconds) depending on your machine's hardware
- Dataset is curated manually and limited in size

---

## Future Scope

- **Gesture-Based Controls** — Use the webcam to detect hand gestures (via MediaPipe or OpenCV) for play/pause, skip, and volume control without touching the keyboard
- **Local Music Playback** — Let users point the app at a local folder and stream their own music files directly, removing the YouTube dependency entirely
- **Cloud AI for Ask AI tab** — Replace local Ollama with a cloud model so natural language search works on the hosted version too without any local setup
- **Mobile App** — A Flutter or SwiftUI frontend backed by the same recommendation logic via a FastAPI backend

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Author

**Nakul Anand**
GitHub: [@nakulanand4](https://github.com/nakulanand4)
