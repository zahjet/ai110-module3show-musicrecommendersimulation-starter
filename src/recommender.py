import csv
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class Song:
    """Represents a song and its audio attributes."""
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
    """Stores a listener's taste preferences used for scoring."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """Scores and ranks songs against a UserProfile using content-based filtering."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> float:
        """Returns a numeric score for how well a song matches the user's profile."""
        score = 0.0

        if song.genre == user.favorite_genre:
            score += 2.0

        if song.mood == user.favorite_mood:
            score += 1.0

        energy_diff = abs(song.energy - user.target_energy)
        score += max(0.0, 1.0 - energy_diff)

        if user.likes_acoustic:
            score += song.acousticness * 0.5
        else:
            score += (1.0 - song.acousticness) * 0.5

        return score

    def _reasons(self, user: UserProfile, song: Song) -> List[str]:
        """Returns a list of human-readable reasons explaining a song's score."""
        reasons = []

        if song.genre == user.favorite_genre:
            reasons.append(f"genre match — {song.genre} (+2.0)")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood match — {song.mood} (+1.0)")

        energy_diff = abs(song.energy - user.target_energy)
        energy_pts = max(0.0, 1.0 - energy_diff)
        reasons.append(f"energy {song.energy:.2f} vs target {user.target_energy:.2f} (+{energy_pts:.2f})")

        if user.likes_acoustic:
            acoustic_pts = song.acousticness * 0.5
            reasons.append(f"acoustic-friendly — acousticness {song.acousticness:.2f} (+{acoustic_pts:.2f})")
        else:
            acoustic_pts = (1.0 - song.acousticness) * 0.5
            reasons.append(f"low-acoustic — acousticness {song.acousticness:.2f} (+{acoustic_pts:.2f})")

        return reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k songs ranked by their score for the given user."""
        return sorted(self.songs, key=lambda song: self._score_song(user, song), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a comma-separated explanation of why a song was recommended."""
        return ", ".join(self._reasons(user, song))


def load_songs(csv_path: str) -> List[Dict]:
    """Reads songs.csv and returns a list of dicts with numeric fields cast to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song for the given user prefs and returns the top-k as (song, score, explanation) tuples."""
    user = UserProfile(
        favorite_genre=user_prefs.get("genre", ""),
        favorite_mood=user_prefs.get("mood", ""),
        target_energy=float(user_prefs.get("energy", 0.5)),
        likes_acoustic=bool(user_prefs.get("likes_acoustic", False)),
    )
    rec = Recommender([Song(**s) for s in songs])

    scored: List[Tuple[Dict, float, str]] = [
        (s, rec._score_song(user, Song(**s)), rec.explain_recommendation(user, Song(**s)))
        for s in songs
    ]
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
