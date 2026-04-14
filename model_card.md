# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

A content-based music recommender that matches songs to a listener's stated taste profile using genre, mood, energy, and acoustic preference.

---

## 2. Intended Use

VibeFinder is designed to suggest songs from a small catalog that fit a user's mood and energy at a given moment. The user tells the system their favorite genre, preferred mood, target energy level, and whether they like acoustic music. The system returns the top 5 songs that best match those preferences.

**Intended use:** Demonstration of how content-based recommendation logic works. Suitable for learning and experimentation.

**Not intended for:** Real production use, large catalogs, users with complex or evolving tastes, or any context where a biased or inaccurate recommendation would cause harm. The system makes no attempt to learn from listening history, skips, or user feedback.

---

## 3. How the Model Works

Imagine you walk into a record store and tell the clerk: "I like lofi music, I'm in a chill mood, and I want something low-energy and acoustic." The clerk mentally goes through every record in the store and gives each one a score based on how well it matches what you said.

VibeFinder does exactly this for all 18 songs at once. It awards points for each match:

- **+2 points** if the song's genre matches your favorite genre (the most important factor)
- **+1 point** if the song's mood matches your preferred mood
- **Up to +1 point** based on how close the song's energy is to your target — songs that are a perfect match get the full point, songs that are far away get less or nothing
- **Up to +0.5 points** based on how acoustic the song is relative to your preference

After scoring every song, it sorts them from highest to lowest and returns the top results. Songs that match all four criteria can score up to 4.5 points. Songs that match nothing score near zero.

---

## 4. Data

The catalog contains 18 songs stored in `data/songs.csv`. Each song has 10 attributes: id, title, artist, genre, mood, energy (0–1 scale), tempo in BPM, valence (emotional positivity, 0–1), danceability (0–1), and acousticness (0–1).

**Genres represented:** lofi, pop, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, country, classical, folk, edm, indie rock, soul (9 distinct genres across 18 songs)

**Moods represented:** happy, chill, intense, relaxed, focused, moody, confident, sad, nostalgic, melancholic, peaceful, euphoric, uplifting (10+ distinct moods)

The original starter dataset had 10 songs. 8 songs were added to improve genre and mood diversity - particularly to include hip-hop, r&b, country, classical, folk, edm, and soul, which were absent from the original catalog.

**What's still missing:** Most genres have only one or two songs. There are no songs in Spanish, K-pop, or other global genres. The data reflects a Western, English-language musical perspective. Tempo, valence, and danceability are collected but not used in scoring.

---

## 5. Strengths

- **Works well for well-represented genres.** When a user's preferred genre has multiple songs in the catalog (e.g., lofi has 3, pop has 2), the system produces a meaningful ranked list with clear differentiation between results.
- **Handles opposite vibes correctly.** A "chill lofi acoustic" profile and a "high-energy EDM hype" profile produce completely non-overlapping top results - the system reliably separates opposite musical tastes.
- **Transparent and explainable.** Every recommendation comes with a plain-English reason explaining exactly which rules fired and how many points each earned. A user can see precisely why a song ranked #1.
- **Proportional energy scoring.** The proximity formula rewards "close but not exact" energy matches with partial credit rather than zero, which produces more graceful degradation when no song perfectly matches the target.

---

## 6. Limitations and Bias

**Genre dominance and catalog thin spots.** Genre carries +2.0 points — double the mood weight — so any song that matches the user's genre starts with a large head start over all other songs. During testing, a user asking for "country / nostalgic" got a perfect #1 result (the single country song scores 4.40), but ranks #2–5 were generic acoustic songs that had nothing to do with country music. Because only one country song exists in the 18-song catalog, the system has nothing meaningful to recommend once that slot is filled, exposing a *filter bubble*: users of underrepresented genres get one great result and then the system quietly gives up and falls back to energy proximity.

**Energy proximity favors mid-range songs when genre is absent.** When a user's genre has no catalog match, the energy term becomes the only meaningful differentiator. Songs near energy=0.5 are always "close enough" to any target, which means a neutral or cross-genre user will always see the same cluster of mid-energy tracks regardless of their actual taste. Doubling the energy weight (experiment: genre halved to 1.0, energy multiplied by 2.0) showed that the top-3 rankings barely changed for profiles *with* a catalog genre match, but for the neutral profile the bias toward low-acousticness mid-energy songs became even more pronounced — confirming that energy alone cannot substitute for rich categorical matching.

**Three features are collected but never used.** Every `Song` stores `valence`, `danceability`, and `tempo_bpm`, yet none appear in the scoring function. This means two songs with identical genre, mood, and energy can receive the exact same score even if one is highly danceable and the other is not. 

**Binary acoustic preference loses nuance.** `likes_acoustic` is a `True`/`False` flag, so a user who "slightly" prefers acoustic music and one who exclusively listens to acoustic recordings are treated identically. A song with acousticness=0.55 and one with acousticness=0.95 produce different raw scores, but the same binary preference signal amplifies or mutes them uniformly, with no way to express "somewhat acoustic" as a target.

---

## 7. Evaluation

Six user profiles were tested: Chill Lofi Listener, High-Energy Pop Fan, Deep Intense Rock, Conflicting Prefs (high energy + sad mood), Genre With No Catalog Match (country), and a Perfectly Neutral Profile. For each, the top 5 recommendations were inspected by hand and compared against intuition.

**What I looked for:** Whether the #1 result was obvious and "correct," whether the #2–5 results made sense as fallbacks, and whether any unexpected song appeared in the top 3 that shouldn't be there.

**What worked as expected:**
- Chill Lofi: Library Rain and Midnight Coding were the clear top 2 — both match genre, mood, and energy closely. The system ranked them almost identically (4.38 vs 4.33), separated only by acousticness.
- Deep Intense Rock: Storm Runner scored 4.44 and pulled far ahead of everything else. Only one rock/intense song exists, so the drop-off to #2 (Gym Hero, a pop song) was sharp.
- Country: Porch Swing Summer was a perfect 4.40 score — all four rules matched simultaneously. Ranks 2–5 were generic acoustic fallbacks.

**What surprised me:**
- *Gym Hero kept appearing for rock and pop profiles.* Gym Hero is a pop/intense song. It ranked #2 for both "High-Energy Pop" (genre match) and "Deep Intense Rock" (mood match). A non-programmer would expect a "rock" request to return only rock songs, but the system awards the same mood point to "intense" regardless of genre context.
- *The adversarial "sad + high energy" profile chose Heartbreak Hotel (score 3.73) even though its energy was 0.44 — far from the target of 0.90.* The genre + mood lock-in (3.0 pts combined) was so dominant that the energy mismatch couldn't overcome it. The system made the emotionally correct choice, but for the "wrong" reason.
- *The neutral profile produced a near-tie across 5 songs*, all scoring between 1.09 and 1.23. With no genre or mood to differentiate, the system essentially became a random picker within a narrow energy band.

**Logic experiment:** Genre weight halved (2.0→1.0), energy weight doubled (1x→2x multiplier). Result: top-3 rankings were unchanged for all three standard profiles. This confirmed that categorical matching (genre + mood) drives the ranking whenever a catalog match exists — tweaking numeric weights only matters when genre is absent from the catalog.

---

## 8. Future Work

- **Replace binary `likes_acoustic` with a float target (0–1).** A user could specify `target_acousticness: 0.6`, and the system would use the same proximity formula already used for energy. This would add real nuance without changing the architecture.
- **Add `valence` and `danceability` to scoring.** Both are already stored on every song. Adding even a small weight (e.g., +0.5 pts for valence proximity) would break tie scores and give users a way to ask for "uplifting" vs "melancholic" songs within the same genre.
- **Introduce a diversity penalty.** Currently the top 5 can all be from the same genre. A simple re-ranking pass that reduces the score of any song whose genre already appeared in the top 3 would force more variety into recommendations.

---

## 9. Personal Reflection

**Biggest learning moment**

The weight-shift experiment was the clearest moment of the whole project. I expected that doubling the importance of energy and halving genre would noticeably change the recommendations — after all, energy is the most immediate quality you feel when a song plays. But the top-3 results didn't change at all for any of the three profiles tested. Genre was doing almost all the work the entire time, and I hadn't noticed because the outputs "looked right." That gap — between a system that appears to work and one you actually understand — is something I'll carry forward. It made me realize that you can't trust the output of a model just because it seems reasonable. You have to poke it deliberately.

**How AI tools helped — and when I had to double-check them**

AI tools were useful at three points: generating the initial CSV rows for the 18-song catalog, suggesting the proximity formula `max(0, 1 - |song.energy - target|)` as a way to reward nearness rather than raw magnitude, and helping draft the Mermaid flowchart structure. But each of those needed a check. The generated CSV rows had to be verified so that the numeric ranges were consistent with the existing songs and that no two songs accidentally had identical attributes. The Mermaid block was pasted into the README without the code fences, which broke the render — the AI gave correct content but assumed I knew how GitHub parses fenced code blocks. That was a small reminder that AI output is always a draft, not a deliverable.

The place where AI was least useful was the evaluation phase. When I ran the six profiles and saw Gym Hero appearing for a rock profile, no tool told me that was surprising or wrong — I had to notice it myself, think through why it happened, and decide whether it revealed a flaw or just a limitation. Judgment about whether a result "makes sense" is still entirely human.

**What surprised me about simple algorithms feeling like recommendations**

The neutral profile was the biggest surprise here. With no genre or mood preferences, all 18 songs scored between 1.09 and 1.23 — a range so narrow it was essentially noise. And yet if you showed someone that list without the scores, it would look like a real recommendation. Five song titles, formatted neatly, would feel like the system had made a choice. That gap between the appearance of intelligence and the actual computation underneath is what makes these systems feel more powerful than they are. A real user would never see the scores — they'd just see the titles and assume the app "knew."

The other surprise was how much the explanation text did to make the output feel valid. Seeing "genre match — lofi (+2.0), mood match — chill (+1.0)" next to a result made it feel justified even in cases where the logic was actually quite weak. Explainability is a double-edged feature: it can genuinely build trust when the reasoning is sound, but it can also make flawed reasoning sound confident.

**What I'd try next**

The first thing I'd add is `valence` to the scoring function. It's already in every song's data and represents emotional positivity — the difference between a song that feels hopeful and one that feels melancholic even at the same energy level. Adding even a small valence proximity weight would immediately improve the adversarial "high energy + sad mood" case, where the system currently ignores whether a song actually sounds sad.

The second change would be replacing the binary `likes_acoustic` flag with a float `target_acousticness` value, using the same proximity formula already in place for energy. One line of code, real improvement in nuance.

The longer-term goal would be adding a simple diversity pass: after scoring, reduce the score of any song whose genre already appeared in the top 2. This wouldn't change the architecture at all, but it would stop the system from returning three lofi songs in a row when the user asked for lofi — which is technically correct but practically boring.
