# staircase-chat-pair

Tiny WebSocket pairing service for the staircase-indifference pilot.
Pairs Democrat ↔ Republican participants and gives them a 3-minute
chat window; reports completion to the parent Qualtrics survey via
`postMessage`.

## Local dev

```bash
cd pilots/03_staircase_indifference/chat-pair-app
npm install
node server.js
```

Open two tabs:
- `http://localhost:3000/?party=Democrat&id=alice`
- `http://localhost:3000/?party=Republican&id=bob`

They should pair and chat.

## Deploy to Render

This lives inside the existing `marketing` repo. You don't need a new repo —
Render deploys fine from a subdirectory.

1. Make sure the repo is pushed to GitHub / GitLab with this folder committed.
2. Render → **New → Web Service** (*not* Blueprint) → connect the repo.
3. Settings:
   - **Root Directory:** `pilots/03_staircase_indifference/chat-pair-app`
   - **Runtime:** Node (auto-detected from `package.json`)
   - **Build Command:** `npm install`
   - **Start Command:** `node server.js`
   - **Plan:** Free is fine for a pilot
4. Deploy. Note the URL (e.g. `https://staircase-chat-pair.onrender.com`).
5. Set `HUMAN_CHAT_URL=...` in your `.env` (or export it) and re-run
   `../create_survey.py` to rebuild the survey with the live URL.

The included `render.yaml` is for anyone who wants to use Render Blueprints
later; manual Web Service setup is simpler for a one-off subdirectory deploy.

**Free-tier caveat:** Render spins the service down after ~15 min idle
and takes ~30 s to wake. For a live pilot, either upgrade to a paid
plan or ping `/healthz` every 10 min.

## Protocol

Client → server:
- `join { party, qualtricsId }` — enter the queue
- `message "<text>"` — send a message

Server → client:
- `waiting` — you're in the queue
- `matched { roomId, endsAt }` — paired; chat until `endsAt` (ms epoch)
- `message { from, text, ts }` — relayed chat message
- `chatEnded { reason }` — 3-min timer expired (`reason: "timeout"`)
- `partnerLeft` — partner disconnected
- `noMatch` — 2-min wait timeout with no pairing

Client → parent (via `window.parent.postMessage`):
- `{ type: "chat_ended", reason, qid }` — chat finished (timer / drop / noMatch)
- `{ type: "chat_continue", reason, qid }` — user clicked Continue

## State

In-memory. Server restart drops all rooms. Acceptable for short pilots;
swap in Redis if this goes to production scale.
