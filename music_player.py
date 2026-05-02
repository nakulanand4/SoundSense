# music_player.py — SoundSense YouTube Player

import re
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def get_youtube_embed_url(song_name: str, artist: str) -> str | None:

    query = f"{song_name} {artist} official audio"
    search_url = "https://www.youtube.com/results"

    try:
        resp = requests.get(
            search_url,
            params={"search_query": query},
            headers=HEADERS,
            timeout=8,
        )
        resp.raise_for_status()

        matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)
        if not matches:
            return None

        video_id = matches[0]
        return f"https://www.youtube.com/embed/{video_id}?autoplay=1&rel=0"

    except Exception:
        return None


def render_player(embed_url: str) -> str:
    return f"""
    <div style="
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #2a2a4a;
        margin: 12px 0 20px 0;
        background: #0d0d1a;
    ">
        <iframe
            width="100%"
            height="200"
            src="{embed_url}"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write;
                   encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
        ></iframe>
    </div>
    """