# 12 Participant explorer

One HTML page to browse every participant of the two Prolific pilots: condition, choices (every click or round), money back, strategy text, comments and the full chat transcript. Filter by condition, sort (Riverton share, profit, words typed, topic mentions), search chats and answers, move with the arrow keys. Words about the product (solar, environment, climate...) are highlighted in chats; party and fairness words are highlighted in answers.

Build: run each pilot's `pull_data.py` (studies/08 and 10), then `python3 studies/12_participant_explorer/build_explorer.py`. The output `explorer.html` embeds chat text (no Prolific IDs), so it is gitignored; share it only privately.
