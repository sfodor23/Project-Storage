from pathlib import Path
import pandas as pd
import re

cwd = Path.cwd()

DATA_DIR = cwd / 'CombinedRedditData.csv'

TITLES_DIR = cwd / 'SteamTitles.csv'

OUTPUT_DIR = cwd / 'Output'

OUTPUT_DIR.mkdir(exist_ok=True)

output_file = OUTPUT_DIR / 'FilteredRedditData.csv'

# ── COLLEGE / STUDENT KEYWORDS ───────────────────────────────────────────────
# Self-identified college student signals. Acronyms excluded per Enrico's note.
COLLEGE_KEYWORDS = [
    # Academic life
    "finals", "midterm", "midterms", "semester", "quarter",
    "syllabus", "lecture", "professor", "prof", "ta", "teaching assistant",
    "office hours", "thesis", "dissertation", "major", "minor",
    "undergrad", "undergraduate", "grad student", "graduate student",
    "college", "university", "campus",
    # Living / social
    "dorm", "dormitory", "roommate", "resident advisor", "dining hall",
    "fraternity", "sorority", "greek life",
    # Performance / stress
    "gpa", "dean's list", "academic probation", "drop out",
    "scholarship", "student loan", "tuition", "financial aid",
    # Admissions
    "application", "applying to college", "acceptance letter", "transfer student",
]

titles_df = pd.read_csv(TITLES_DIR)

titles_df = titles_df[titles_df["Reviews Total"] > 60600]

titles = titles_df["Title"].tolist()

# ── GAMING KEYWORDS ──────────────────────────────────────────────────────────
# Broad gaming language; game titles kept generic (no acronyms)
GAMING_KEYWORDS = [
    # General terms
    "video game", "gaming", "gamer", "esport", "esports", "streamer", "streaming",
    "twitch", "discord", "multiplayer", "online game", "console",
    "playstation", "xbox", "nintendo", "steam", "pc game",
    # Game titles / series (full names only — no acronyms)
    "minecraft", "league of legends", "world of warcraft", "dota", "dota 2",
    "fortnite", "valorant", "call of duty", "roblox",
    "grand theft auto", "overwatch", "apex legends",
    "counter-strike", "counterstrike",
    # IGD / problematic gaming signals (DSM-5 criteria)
    "addicted to gaming", "gaming addiction", "can't stop playing", "stop gaming",
    "gaming disorder", "compulsive gaming", "game too much", "gaming too much",
    "neglect", "withdrawal from gaming", "game all night", "game all day",
]

#GAMING_KEYWORDS.extend(titles)

print(GAMING_KEYWORDS)

# ── MENTAL HEALTH KEYWORDS ───────────────────────────────────────────────────
MENTAL_HEALTH_KEYWORDS = [
    # Conditions
    "anxiety", "anxious", "panic attack", "panic disorder",
    "depression", "depressed", "depressive",
    "mental health", "mental illness", "mental disorder",
    "stress", "stressed", "burnout",
    "addiction", "addicted",
    "phobia", "agoraphobia", "social anxiety", "selective mutism",
    "ocd", "obsessive compulsive",
    "ptsd", "trauma",
    # Emotional/behavioral
    "lonely", "loneliness", "isolated", "isolation",
    "suicidal", "self-harm", "self harm",
    "therapy", "therapist", "psychologist", "psychiatrist", "counseling",
    "antidepressant", "medication",
    "insomnia", "sleep", "sleeping problems",
    # IGD escape criterion
    "escape", "cope", "coping",
]

# Subreddit → category assignment
# Categories: 'mental_health', 'gaming', 'college'
SUBREDDIT_CATEGORIES = {
    # ── Mental health subs ────────────────────────────────────────────────
    "Anxiety":          "mental_health",
    "mentalhealth":     "mental_health",
    "depression":       "mental_health",
    "depression_help":  "mental_health",
    "addiction":        "mental_health",
    "Agoraphobia":      "mental_health",
    "Anxietyhelp":      "mental_health",
    "emetophobia":      "mental_health",
    "Phobia":           "mental_health",
    "socialanxiety":    "mental_health",
    "PanicAttack":      "mental_health",
    "selectivemutism":  "mental_health",
    # ── Gaming subs ───────────────────────────────────────────────────────
    "gaming":           "gaming",
    "Games":            "gaming",
    "pcgaming":         "gaming",
    "truegaming":       "gaming",
    "StopGaming":       "gaming",
    "gamers":           "gaming",
    "patientgamers":    "gaming",
    "AdultGamers":      "gaming",
    "GirlGamers":       "gaming",
    "Minecraft":        "gaming",
    "leagueoflegends":  "gaming",
    "wow":              "gaming",
    "DotA2":            "gaming",
    "FortNiteBR":       "gaming",
    "VALORANT":         "gaming",
    "CallOfDuty":       "gaming",
    "roblox":           "gaming",
    "GTA":              "gaming",
    # ── College/student subs ──────────────────────────────────────────────
    "college":          "college",
    "GradSchool":       "college",
    "ApplyingToCollege":"college",
    "CollegeRant":      "college",
    "collegeadvice":    "college",
    "University":       "college",
    "Student":          "college",
    # ── Dual-signal subs (college + gaming) ───────────────────────────────
    "adulting":         "college",   # filter: gaming + mental health
    "productivity":     "college",   # filter: gaming + mental health
}

def make_pattern(keywords: list[str]) -> re.Pattern:
    """Build a compiled regex that matches any keyword as a whole word."""
    escaped = [re.escape(kw) for kw in keywords]
    pattern = r"\b(?:" + "|".join(escaped) + r")\b"
    return re.compile(pattern, re.IGNORECASE)

COLLEGE_PAT = make_pattern(COLLEGE_KEYWORDS)
GAMING_PAT = make_pattern(GAMING_KEYWORDS)
MENTAL_HEALTH_PAT = make_pattern(MENTAL_HEALTH_KEYWORDS)

df = pd.read_csv(DATA_DIR)

df["subreddit"].fillna("")
df["title"].fillna("")
df["selftext"].fillna("")

mask_config = dict(na=False, regex=True)

college_mask = (
    (df["title"].str.contains(GAMING_PAT, **mask_config)) |
    (df["selftext"].str.contains(GAMING_PAT, **mask_config))
) & (
    (df["title"].str.contains(MENTAL_HEALTH_PAT, **mask_config)) |
    (df["selftext"].str.contains(MENTAL_HEALTH_PAT, **mask_config))
) & (
    df["subreddit"].map(SUBREDDIT_CATEGORIES).eq("college")
)

gaming_mask = (
    (df["title"].str.contains(COLLEGE_PAT, **mask_config)) |
    (df["selftext"].str.contains(COLLEGE_PAT, **mask_config))
) & (
    (df["title"].str.contains(MENTAL_HEALTH_PAT, **mask_config)) |
    (df["selftext"].str.contains(MENTAL_HEALTH_PAT, **mask_config))
) & (
    df["subreddit"].map(SUBREDDIT_CATEGORIES).eq("gaming")
)

mental_health_mask = (
    (df["title"].str.contains(GAMING_PAT, **mask_config)) |
    (df["selftext"].str.contains(GAMING_PAT, **mask_config))
) & (
    (df["title"].str.contains(COLLEGE_PAT, **mask_config)) |
    (df["selftext"].str.contains(COLLEGE_PAT, **mask_config))
) & (
    df["subreddit"].map(SUBREDDIT_CATEGORIES).eq("mental_health")
)

college_df = df[college_mask]

gaming_df = df[gaming_mask]

mental_health_df = df[mental_health_mask]

output_df = pd.concat([college_df, gaming_df, mental_health_df])

print(f"Filtered Message Count: {len(output_df)}")
print(f"Total Message Count: {len(df)}")
print(f"Total Retention: {round(((len(output_df)/len(df)) * 100), 4)}%")

for subreddit in SUBREDDIT_CATEGORIES:
    subreddit_df = df[df["subreddit"] == subreddit]
    output_subreddit_df = output_df[output_df["subreddit"] == subreddit]

    if len(subreddit_df) != 0:
        print(f"{subreddit} Subreddit Retention: {round(((len(output_subreddit_df)/len(subreddit_df)) * 100), 4)}%") 
    else:
        print(f"{subreddit} Subreddit had no entries: No Recorded Retention")


output_df.to_csv(output_file)




