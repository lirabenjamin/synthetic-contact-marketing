"""
Bot Validity Check: Ask the Democrat and Republican bots the 6 environmental
attitude questions and derive a calibrated score per question using log probabilities.

For each (bot, question) pair we:
  1. Send one chat-completion request with max_tokens=1.
  2. Collect the top-20 log-probabilities for the first generated token.
  3. Isolate the log-probs for tokens "1"–"5", convert to probabilities, renormalize.
  4. Compute the expected value: E = Σ i * p_i   (a continuous score on [1,5]).

Output: data/processed/bot_survey.csv
"""

import math
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── System prompts (identical to the study chatbots) ────────────────────────
SYSTEM_PROMPTS = {
    "Democrat": (
        "You are an american consumer who identifies as a democrat. "
        "You will be asked questions about your beliefs, habits, and preferences. "
        "Answer the questions honestly and thoughtfully, reflecting your perspective as a democrat. "
        "Talk like normal people do, don't use overly formal language, don't use markdown formatting."
    ),
    "Republican": (
        "You are an american consumer who identifies as a republican. "
        "You will be asked questions about your beliefs, habits, and preferences. "
        "Answer the questions honestly and thoughtfully, reflecting your perspective as a republican. "
        "Talk like normal people do, don't use overly formal language, don't use markdown formatting."
    ),
}

# ── The 6 Green/Environmental Attitudes items ────────────────────────────────
QUESTIONS = [
    "It is important to me that the products I use do not harm the environment.",
    "I consider the potential environmental impact of my actions when making many of my decisions.",
    "My purchase habits are affected by my concern for our environment.",
    "I am concerned about wasting the resources of our planet.",
    "I would describe myself as environmentally responsible.",
    "I am willing to be inconvenienced in order to take actions that are more environmentally friendly.",
]

SCALE_INSTRUCTION = (
    "Rate the following statement on a scale from 1 to 5, "
    "where 1 = 'Disagree strongly' and 5 = 'Agree strongly'. "
    "Reply with a single digit (1, 2, 3, 4, or 5) and nothing else."
)


def logprob_score(system_prompt: str, question: str) -> tuple[float, dict]:
    """
    Return (expected_value, probability_dict) for a given (bot, question) pair.
    expected_value is the log-prob-weighted mean of the five response options.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{SCALE_INSTRUCTION}\n\nStatement: {question}"},
        ],
        max_tokens=1,
        logprobs=True,
        top_logprobs=20,
        temperature=1,
    )

    top = response.choices[0].logprobs.content[0].top_logprobs

    # Collect raw log-probs for digits 1–5; assign -100 for any digit not surfaced.
    raw = {str(d): -100.0 for d in range(1, 6)}
    for item in top:
        tok = item.token.strip()
        if tok in raw:
            raw[tok] = item.logprob

    # Convert to probabilities and renormalize over the five options.
    probs = {d: math.exp(lp) for d, lp in raw.items()}
    total = sum(probs.values())
    probs = {d: p / total for d, p in probs.items()}

    ev = sum(int(d) * p for d, p in probs.items())
    return ev, probs


def main():
    results = []
    for party, system_prompt in SYSTEM_PROMPTS.items():
        for i, question in enumerate(QUESTIONS, start=1):
            print(f"  {party} bot | Q{i} …", end=" ", flush=True)
            ev, probs = logprob_score(system_prompt, question)
            print(f"EV = {ev:.3f}")
            results.append(
                {
                    "bot_party": party,
                    "question_num": i,
                    "question": question,
                    "expected_value": ev,
                    **{f"p{d}": probs[str(d)] for d in range(1, 6)},
                }
            )

    df = pd.DataFrame(results)
    out_path = "data/processed/bot_survey.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved → {out_path}")
    print(df[["bot_party", "question_num", "expected_value"]].to_string(index=False))


if __name__ == "__main__":
    main()
