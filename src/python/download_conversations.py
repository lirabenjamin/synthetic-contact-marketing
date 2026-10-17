"""
Download conversations from all participants and compute conversation metrics.
Saves conversations as JSON and adds metrics to cleaned data.
"""

import psycopg2
import pandas as pd
import dotenv
import os
import json
from pathlib import Path

# Load environment variables
dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def load_conversation(user_id):
    """
    Load conversation for a specific user from the database.
    Returns a list of message dictionaries with role and content.
    """
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # Prepare the query for 'message'
    query_message = """
    SELECT 'user' as role, message as content, timestamp
    FROM conversation_logs
    WHERE user_id = %s and message is not null
    """
    cur.execute(query_message, (user_id,))
    rows_message = cur.fetchall()

    # Prepare the query for 'response'
    query_response = """
    SELECT 'assistant' as role, response as content, timestamp
    FROM conversation_logs
    WHERE user_id = %s and response is not null
    """
    cur.execute(query_response, (user_id,))
    rows_response = cur.fetchall()

    # Concatenate and sort the rows by timestamp
    all_rows = sorted(rows_message + rows_response, key=lambda x: x[2])

    # Format the rows into the desired dictionary format
    session_messages = [{"role": row[0], "content": row[1]} for row in all_rows]

    cur.close()
    conn.close()
    return session_messages


def compute_conversation_metrics(messages):
    """
    Compute conversation metrics from a list of messages.
    Returns:
    - user_turn_count: number of user messages
    - user_word_count: total words in user messages
    """
    user_messages = [msg for msg in messages if msg['role'] == 'user']
    user_turn_count = len(user_messages)
    user_word_count = sum(len(msg['content'].split()) for msg in user_messages)

    return {
        'user_turn_count': user_turn_count,
        'user_word_count': user_word_count
    }


def main():
    # Load participant IDs from Qualtrics data
    print("Loading participant data...")
    qualtrics_data = pd.read_parquet("data/raw/qualtrics.parquet")
    data2 = pd.read_parquet("t3 experiment pilot/analysis_data.parquet")

    # Filter to completed responses
    participant_ids1 = qualtrics_data[qualtrics_data['Status'] == 'IP Address']['ResponseId'].tolist()
    participant_ids2 = data2['ResponseId'].tolist()
    participant_ids = set(participant_ids1) | set(participant_ids2)
    print(f"Found {len(participant_ids)} participants")

    # Create output directory for conversations
    output_dir = Path("data/processed/conversations")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download conversations and compute metrics
    conversation_metrics = []

    for i, user_id in enumerate(participant_ids, 1):
        print(f"Processing participant {i}/{len(participant_ids)}: {user_id}")

        try:
            # Load conversation
            messages = load_conversation(user_id)

            # Save conversation as JSON
            conversation_file = output_dir / f"{user_id}.json"
            with open(conversation_file, 'w') as f:
                json.dump(messages, f, indent=2)

            # Compute metrics
            metrics = compute_conversation_metrics(messages)
            conversation_metrics.append({
                'ResponseId': user_id,
                'user_turn_count': metrics['user_turn_count'],
                'user_word_count': metrics['user_word_count'],
                'has_conversation': True
            })

        except Exception as e:
            print(f"  Error processing {user_id}: {e}")
            conversation_metrics.append({
                'ResponseId': user_id,
                'user_turn_count': 0,
                'user_word_count': 0,
                'has_conversation': False
            })

    # Save conversation metrics
    metrics_df = pd.DataFrame(conversation_metrics)
    metrics_df.to_parquet("data/processed/conversation_metrics.parquet", index=False)
    print(f"\nSaved conversation metrics to data/processed/conversation_metrics.parquet")

    # Print summary statistics
    print("\nConversation Metrics Summary:")
    print(f"Total participants: {len(metrics_df)}")
    print(f"Participants with conversations: {metrics_df['has_conversation'].sum()}")
    print(f"\nUser Turn Count:")
    print(metrics_df['user_turn_count'].describe())
    print(f"\nUser Word Count:")
    print(metrics_df['user_word_count'].describe())


if __name__ == "__main__":
    main()
