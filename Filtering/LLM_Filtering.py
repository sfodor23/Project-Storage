import requests
import json
import pandas as pd
from pathlib import Path

def classify_post(post: str, base_prompt: str, session) -> dict:
    prompt = base_prompt

    prompt = prompt.replace("{post_text}", post)
    
    payload = {
      "model": "qwen3.5:4b",
      "prompt": prompt,
      "stream": False,
      "format": {
    "type": "object",
    "properties": {
      "results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": { "type": "integer" },
            "complete_match": { "type": "boolean" },
            "categories": {
              "type": "object",
              "properties": {
                "College": {
                  "type": "object",
                  "properties": {
                    "fit": { "type": "boolean" },
                    "confidence": { "type": "number" },
                    "matching_terms": {
                      "type": "array",
                      "items": { "type": "string" }
                    }
                  },
                  "required": ["fit", "confidence", "matching_terms"]
                },
                "Mental Health": {
                  "type": "object",
                  "properties": {
                    "fit": { "type": "boolean" },
                    "confidence": { "type": "number" },
                    "matching_terms": {
                      "type": "array",
                      "items": { "type": "string" }
                    }
                  },
                  "required": ["fit", "confidence", "matching_terms"]
                },
                "Gaming": {
                  "type": "object",
                  "properties": {
                    "fit": { "type": "boolean" },
                    "confidence": { "type": "number" },
                    "matching_terms": {
                      "type": "array",
                      "items": { "type": "string" }
                    }
                  },
                  "required": ["fit", "confidence", "matching_terms"]
                }
              },
              "required": ["College", "Mental Health", "Gaming"]
            }
          },
          "required": ["id", "complete_match", "categories"]
        }
      }
    },
    "required": ["results"]
  }
    }

    response = session.post("http://localhost:11434/api/generate", json=payload)
    response.raise_for_status()

    result = response.json()
    output_text = result.get("response", "")

    if not output_text:
      output_text = result.get("thinking", "")

    return json.loads(output_text)

cwd = Path.cwd()

DATA_DIR = cwd / 'CombinedRedditData.csv'

df = pd.read_csv(DATA_DIR)

df["subreddit"] = df["subreddit"].fillna("")
df["title"] = df["title"].fillna("")
df["selftext"] = df["selftext"].fillna("")

output_df = pd.DataFrame(columns=df.columns)

with open("keywords.json", "r", encoding="utf-8") as f:
    keyword_data = json.load(f)
    gaming_keywords = ", ".join(keyword_data["GAMING_KEYWORDS"])
    college_keywords = ", ".join(keyword_data["COLLEGE_KEYWORDS"])
    mental_health_keywords = ", ".join(keyword_data["MENTAL_HEALTH_KEYWORDS"])

BASE_PROMPT_DIR = cwd / 'prompt.txt'

with open(BASE_PROMPT_DIR, "r", encoding="utf-8") as f:
    base_prompt = f.read()
    base_prompt = base_prompt.replace("{college_keywords}", college_keywords)
    base_prompt = base_prompt.replace("{mental_health_keywords}", mental_health_keywords)
    base_prompt = base_prompt.replace("{gaming_keywords}", gaming_keywords)

session = requests.Session()

textual_df = df[["author","created_datetime"]].copy()
textual_df["ctext"] = df[["selftext", "title", "subreddit"]].agg(" - ".join, axis=1)

for row in textual_df.itertuples(index=True):
    combined_post_text = row.ctext

    Classification = classify_post(combined_post_text, base_prompt, session)

    results = Classification.get("results", [])

    if results:
        final_result = results[0]["complete_match"]
    else:
        final_result = None

    print(Classification)

    if row.Index > 10:
        break

