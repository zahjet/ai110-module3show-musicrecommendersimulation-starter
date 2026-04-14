"""
Command line runner for the Music Recommender Simulation.
"""

from src.recommender import load_songs, recommend_songs


PROFILES = [
    # --- Standard profiles ---
    (
        "Chill Lofi Listener",
        {"genre": "lofi", "mood": "chill", "energy": 0.40, "likes_acoustic": True},
    ),
    (
        "High-Energy Pop Fan",
        {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
    ),
    (
        "Deep Intense Rock",
        {"genre": "rock", "mood": "intense", "energy": 0.90, "likes_acoustic": False},
    ),
    # --- Adversarial / edge-case profiles ---
    (
        "Conflicting Prefs (High Energy + Sad Mood)",
        # Energy 0.9 normally signals hype, but sad mood is low-valence and introspective.
        # Exposes whether the system treats energy and mood as independent axes (it does).
        {"genre": "r&b", "mood": "sad", "energy": 0.90, "likes_acoustic": False},
    ),
    (
        "Genre With No Catalog Match (country)",
        # Only one country song exists. Top pick is obvious; ranks 2-5 reveal what the
        # system falls back on when genre points are unavailable for most songs.
        {"genre": "country", "mood": "nostalgic", "energy": 0.38, "likes_acoustic": True},
    ),
    (
        "Perfectly Neutral Profile",
        # No genre, no mood, energy=0.5, no acoustic preference.
        # All songs score on energy proximity alone — reveals score ties and arbitrary ordering.
        {"genre": "", "mood": "", "energy": 0.50, "likes_acoustic": False},
    ),
]


def main() -> None:
    songs = load_songs("data/songs.csv")

    for label, user_prefs in PROFILES:
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print(f"\n{'=' * 55}")
        print(f"  Profile: {label}")
        print(f"  Prefs:   {user_prefs}")
        print(f"{'=' * 55}")
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"  #{rank}  {song['title']} ({song['genre']} / {song['mood']})")
            print(f"      Score: {score:.2f}  |  {explanation}")
        print()


if __name__ == "__main__":
    main()
