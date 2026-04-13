from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

# Genres grouped into families for partial matching
GENRE_FAMILIES = {
    "lofi":              "chill",
    "ambient":           "chill",
    "dream pop":         "chill",
    "indie folk":        "chill",
    "pop":               "upbeat",
    "indie pop":         "upbeat",
    "synthwave":         "upbeat",
    "rock":              "rock",
    "metalcore":         "rock",
    "progressive metal": "rock",
    "post-metal":        "rock",
    "blackgaze":         "rock",
    "soundtrack":        "cinematic",
    "jazz":              "jazz",
}

# Moods grouped into families for partial matching
MOOD_FAMILIES = {
    "happy":      "positive",
    "fun":        "positive",
    "nostalgic":  "positive",
    "chill":      "calm",
    "relaxed":    "calm",
    "focused":    "calm",
    "moody":      "dark",
    "dark":       "dark",
    "emotional":  "dark",
    "reflective": "dark",
    "intense":    "intense",
    "aggressive": "intense",
    "epic":       "intense",
}

@dataclass
class Song:
    """A single song and its audio attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """A user's taste preferences used to score and rank songs."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields converted to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        float(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                "instrumentalness": float(row["instrumentalness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences, returning (score, reasons) with points for genre, mood, and energy."""
    score = 0.0
    reasons = []

    # Genre: +2.0 for exact match, +1.0 for same family
    user_genre = user_prefs.get("genre", "")
    song_genre = song.get("genre", "")
    if song_genre == user_genre:
        score += 2.0
        reasons.append(f"genre match (+2.0)")
    elif GENRE_FAMILIES.get(song_genre) == GENRE_FAMILIES.get(user_genre) and user_genre:
        score += 1.0
        reasons.append(f"similar genre: {song_genre} is in the same family as {user_genre} (+1.0)")

    # Mood: +1.5 for exact match, +0.75 for same family
    user_mood = user_prefs.get("mood", "")
    song_mood = song.get("mood", "")
    if song_mood == user_mood:
        score += 1.5
        reasons.append(f"mood match (+1.5)")
    elif MOOD_FAMILIES.get(song_mood) == MOOD_FAMILIES.get(user_mood) and user_mood:
        score += 0.75
        reasons.append(f"similar mood: {song_mood} is in the same family as {user_mood} (+0.75)")

    # Energy: +1.0 if within 0.10, +0.5 if within 0.25
    user_energy = user_prefs.get("energy")
    if user_energy is not None:
        diff = abs(song["energy"] - user_energy)
        if diff <= 0.10:
            score += 1.0
            reasons.append(f"energy close match: {song['energy']} ~= {user_energy} (+1.0)")
        elif diff <= 0.25:
            score += 0.5
            reasons.append(f"energy partial match: {song['energy']} near {user_energy} (+0.5)")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort highest to lowest, and return the top k as (song, score, explanation) tuples."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "No strong match found"
        scored.append((song, score, explanation))

    # sorted() returns a new list — the original song catalog stays unchanged
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return ranked[:k]
