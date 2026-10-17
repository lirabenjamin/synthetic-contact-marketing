#!/usr/bin/env python3
"""
Create the Chatbot → Game study on Qualtrics.

Design:
  - 2 conditions: outgroup chatbot (treatment) vs dogs chatbot (control)
  - After chatbot, participants play the marketing game (V2: total-only feedback, 55% noise)
  - DVs: round-level allocations and revenue from the game
  - No belief questions, no experience ratings — just behavior
"""

import os, re
from dotenv import load_dotenv
from qualtrics_sdk import QualtricsAPI

import time

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
api = QualtricsAPI(
    api_token=os.getenv("QUALTRICS_API_TOKEN"),
    data_center=os.getenv("QUALTRICS_DATA_CENTER", "upenn.qualtrics.com")
)
DC = os.getenv("QUALTRICS_DATA_CENTER", "upenn.qualtrics.com")

# Rate limit helper
def pause(n=3):
    time.sleep(n)


def force_response(survey_id, question_id):
    pause()
    q_data = api.get_question(survey_id, question_id)
    q_data["Validation"] = {"Settings": {"ForceResponse": "ON", "ForceResponseType": "ON", "Type": "None"}}
    api.update_question(survey_id, question_id, q_data)
    pause()


def set_question_js(survey_id, question_id, js_code):
    """Set QuestionJS via the API (for iframe/game JS that Qualtrics strips from inline script tags)."""
    import requests
    token = os.getenv("QUALTRICS_API_TOKEN")
    headers = {'X-API-TOKEN': token, 'Content-Type': 'application/json'}
    pause()
    r = requests.get(f'https://{DC}/API/v3/survey-definitions/{survey_id}/questions/{question_id}', headers=headers)
    q = r.json()['result']
    q['QuestionJS'] = js_code
    requests.put(f'https://{DC}/API/v3/survey-definitions/{survey_id}/questions/{question_id}', headers=headers, json=q)
    pause()


# ── Game HTML (V2: total-only feedback, 55% noise, fixed K=2) ────────────────

# Read from create_survey_v2.py
v2_path = os.path.join(os.path.dirname(__file__), 'create_survey_v2.py')
with open(v2_path) as f:
    v2_content = f.read()

match = re.search(r"return r'''(.*?)'''", v2_content, re.DOTALL)
game_full_html = match.group(1).strip()

# Split HTML (style + div) from JS (script contents)
script_start = game_full_html.find('<script>') + len('<script>')
script_end = game_full_html.find('</script>')
GAME_JS_RAW = game_full_html[script_start:script_end].strip()
GAME_HTML = game_full_html[:game_full_html.find('<script>')].strip()

# Strip IIFE wrapper — addOnload provides function scope
GAME_JS_INNER = GAME_JS_RAW
if GAME_JS_INNER.startswith('(function(){'):
    GAME_JS_INNER = GAME_JS_INNER[len('(function(){'):]
if GAME_JS_INNER.endswith('})();'):
    GAME_JS_INNER = GAME_JS_INNER[:-len('})();')]
GAME_ONLOAD_JS = f"Qualtrics.SurveyEngine.addOnload(function(){{\n{GAME_JS_INNER.strip()}\n}});"


# ── Chatbot iframe JS (from SV_5tZyHd6IadEfqWW) ────────────────────────────

CHATBOT_OUTGROUP_JS = '''Qualtrics.SurveyEngine.addOnReady(function () {
  const base =
    "https://reframe001-7a186c892e5e.herokuapp.com" +
    "?condition=" + encodeURIComponent("${e://Field/condition}") +
    "&fixed=" + encodeURIComponent("${e://Field/fixed}") +
    "&id=" + encodeURIComponent("${e://Field/ResponseID}");

  const container = this.getQuestionContainer();

  const wrap = document.createElement("div");
  wrap.style.width = "100%";
  wrap.style.maxWidth = "1200px";
  wrap.style.margin = "0 auto";
  wrap.style.border = "1px solid #e5e5e5";
  wrap.style.borderRadius = "14px";
  wrap.style.overflow = "hidden";

  const iframe = document.createElement("iframe");
  iframe.style.width = "100%";
  iframe.style.height = "70vh";
  iframe.style.border = "0";
  iframe.setAttribute("scrolling", "no");

  const controls = document.createElement("div");
  controls.style.display = "flex";
  controls.style.gap = "12px";
  controls.style.alignItems = "center";
  controls.style.padding = "12px";
  controls.style.borderTop = "1px solid #e5e5e5";
  controls.style.background = "#fafafa";

  const status = document.createElement("div");
  status.style.flex = "1";
  status.style.fontSize = "14px";
  status.textContent = "Loading activity…";

  const retryBtn = document.createElement("button");
  retryBtn.type = "button";
  retryBtn.textContent = "Reload";
  retryBtn.style.padding = "8px 14px";
  retryBtn.style.borderRadius = "10px";
  retryBtn.style.border = "1px solid #ccc";
  retryBtn.style.cursor = "pointer";
  retryBtn.style.background = "#ffffff";

  controls.appendChild(status);
  controls.appendChild(retryBtn);

  wrap.appendChild(iframe);
  wrap.appendChild(controls);
  container.appendChild(wrap);

  function loadIframe() {
    status.textContent = "Loading activity…";
    const cacheBust = "&_t=" + Date.now();
    iframe.src = base + cacheBust;
    clearTimeout(loadIframe._timer);
    loadIframe._timer = setTimeout(() => {
      status.textContent =
        "If the activity does not appear or you see an error message, click Reload below.";
    }, 10000);
  }

  retryBtn.addEventListener("click", () => {
    try { Qualtrics.SurveyEngine.setEmbeddedData("iframe_reload_clicked", "1"); } catch (e) {}
    loadIframe();
  });

  iframe.addEventListener("load", () => {
    clearTimeout(loadIframe._timer);
    status.textContent = "";
  });

  loadIframe();
});'''

CHATBOT_DOGS_JS = CHATBOT_OUTGROUP_JS.replace(
    '"?condition=" + encodeURIComponent("${e://Field/condition}")',
    '"?condition=dogs"'
)


# ── Create survey ────────────────────────────────────────────────────────────

survey = api.create_survey("Synthetic Contact → Marketing Game Pilot")
sid = survey["SurveyID"]
print(f"Created survey: {sid}")

try:
    # ── Embedded data ────────────────────────────────────────────────────────
    fields = {
        "PROLIFIC_PID": {"type": "text"},
        "fixed": {"type": "text", "value": "0"},
        "treatment_num": {"type": "text"},
        "condition": {"type": "text"},
        "IngroupLabel": {"type": "text"},
        "OutgroupLabel": {"type": "text"},
        "PartyNumeric": {"type": "text"},
        "chatClicked": {"type": "text"},
        "iframe_reload_clicked": {"type": "text"},
    }
    # Only declare fields needed for flow logic / piped text.
    # Game fields (game_round_*) are auto-created by setEmbeddedData() in the JS at runtime.
    api.set_embedded_data_fields(sid, fields, position="start")
    print("Set embedded data fields"); pause(5)

    # ── Blocks ───────────────────────────────────────────────────────────────
    consent_block = api.create_block(sid, "Consent & Party ID")["BlockID"]; pause()
    chatbot_outgroup_block = api.create_block(sid, "Chatbot — Outgroup")["BlockID"]; pause()
    chatbot_dogs_block = api.create_block(sid, "Chatbot — Dogs (Control)")["BlockID"]; pause()
    game_block = api.create_block(sid, "Marketing Game")["BlockID"]; pause()
    demographics_block = api.create_block(sid, "Demographics")["BlockID"]; pause()
    print("Created blocks")

    # ── Block: Consent & Party ID ────────────────────────────────────────────
    q_consent = api.create_descriptive_text(sid, """
<div style="max-width: 700px; margin: 0 auto; line-height: 1.5;">
<p>You are invited to take part in a research study about public attitudes toward environmental issues.</p>
<p>The study takes approximately <strong>15–20 minutes</strong>. You will first have a short conversation with a chatbot, then play a marketing strategy game.</p>
<p>By proceeding you consent to participate in this University of Pennsylvania research study. Responses are anonymous. You may withdraw at any time.</p>
</div>
""", block_id=consent_block); pause()

    DEM = '<span style="color:#2563eb;font-weight:700">Democrat</span>'
    REP = '<span style="color:#dc2626;font-weight:700">Republican</span>'

    q_party = api.create_multiple_choice_question(
        sid,
        '<div style="text-align: center; margin: 20px 0;">'
        '<img alt="Politics icon" src="https://raw.githubusercontent.com/lirabenjamin/twins_pilot2/main/materials/qualtrics/images/politics.png" '
        'style="max-width: 500px; width: 100%; height: auto;">'
        '</div>\nWhich political party do you most identify with?',
        choices=["Democrat", "Republican"],
        block_id=consent_block,
    )
    force_response(sid, q_party["QuestionID"])

    q_extremity_dem = api.create_slider_question(
        sid,
        f"How strongly do you identify as a {DEM}?",
        min_value=0, max_value=100,
        left_label="Not at all", right_label="Very strongly",
        block_id=consent_block,
    )
    force_response(sid, q_extremity_dem["QuestionID"])
    # Display logic: show only if Democrat
    api.add_display_logic(
        sid, q_extremity_dem["QuestionID"],
        q_party["QuestionID"],
        "Selected",
        choice_locator=f"q://{q_party['QuestionID']}/SelectableChoice/1",
    )

    q_extremity_rep = api.create_slider_question(
        sid,
        f"How strongly do you identify as a {REP}?",
        min_value=0, max_value=100,
        left_label="Not at all", right_label="Very strongly",
        block_id=consent_block,
    )
    force_response(sid, q_extremity_rep["QuestionID"])
    api.add_display_logic(
        sid, q_extremity_rep["QuestionID"],
        q_party["QuestionID"],
        "Selected",
        choice_locator=f"q://{q_party['QuestionID']}/SelectableChoice/2",
    )
    print("  Consent & party ID added")

    # ── Block: Chatbot Outgroup ──────────────────────────────────────────────
    q_intro_chat = api.create_descriptive_text(sid, """
<div style="text-align: center; margin: 20px 0;">
<img alt="bot icon" src="https://raw.githubusercontent.com/lirabenjamin/twins_pilot2/main/materials/qualtrics/images/bot.png"
     style="max-width: 500px; width: 100%; height: auto;">
</div>
Once you click next, you will be redirected to a chatbot that has been designed to represent the views of a typical member of the opposite political party from yours. Please have a conversation with the chatbot to learn about their views on environmental issues. When you are done, click the button to continue.
""", block_id=chatbot_outgroup_block)

    q_chatbot_outgroup = api.create_descriptive_text(sid, "&nbsp;", block_id=chatbot_outgroup_block)
    set_question_js(sid, q_chatbot_outgroup["QuestionID"], CHATBOT_OUTGROUP_JS)
    print(f"  Chatbot outgroup: {q_chatbot_outgroup['QuestionID']}")

    # ── Block: Chatbot Dogs (Control) ────────────────────────────────────────
    q_intro_dogs = api.create_descriptive_text(sid, """
<div style="text-align: center; margin: 20px 0;">
<img alt="bot icon" src="https://raw.githubusercontent.com/lirabenjamin/twins_pilot2/main/materials/qualtrics/images/bot.png"
     style="max-width: 500px; width: 100%; height: auto;">
</div>
Once you click next, you will be redirected to a chatbot. Please have a conversation with the chatbot about the topic it presents. When you are done, click the button to continue.
""", block_id=chatbot_dogs_block)

    q_chatbot_dogs = api.create_descriptive_text(sid, "&nbsp;", block_id=chatbot_dogs_block)
    set_question_js(sid, q_chatbot_dogs["QuestionID"], CHATBOT_DOGS_JS)
    print(f"  Chatbot dogs: {q_chatbot_dogs['QuestionID']}")

    # ── Block: Marketing Game ────────────────────────────────────────────────
    q_game_intro = api.create_descriptive_text(sid, """
<div style="text-align: center; margin: 20px 0;">
<img style="max-width: 500px; width: 100%; height: auto;" alt="game icon"
     src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Joystick_icon.svg/1200px-Joystick_icon.svg.png">
</div>
<p style="text-align: center;">Now you'll play a short <strong>marketing strategy game</strong>. You'll allocate a budget across different U.S. markets to sell eco-friendly products. Try to maximize your revenue!</p>
""", block_id=game_block)

    q_game = api.create_descriptive_text(sid, GAME_HTML, block_id=game_block)
    set_question_js(sid, q_game["QuestionID"], GAME_ONLOAD_JS)
    print(f"  Game question: {q_game['QuestionID']}")

    # ── Block: Demographics ──────────────────────────────────────────────────
    q_gender = api.create_multiple_choice_question(
        sid, "What is your gender?",
        choices=["Male", "Female", "Non-binary", "Prefer not to say"],
        block_id=demographics_block,
    )
    force_response(sid, q_gender["QuestionID"])

    q_age = api.create_text_entry_question(sid, "What is your age?", text_type="SL", block_id=demographics_block)
    force_response(sid, q_age["QuestionID"])

    q_race = api.create_multiple_choice_question(
        sid, "Which races/ethnicities do you identify with?",
        choices=["White", "Black or African American", "Hispanic or Latino", "Asian", "Other"],
        allow_multiple=True,
        block_id=demographics_block,
    )
    force_response(sid, q_race["QuestionID"])

    q_education = api.create_multiple_choice_question(
        sid, "What is the highest level of education you have completed?",
        choices=["High school or less", "Some college", "Bachelor's degree", "Graduate degree"],
        block_id=demographics_block,
    )
    force_response(sid, q_education["QuestionID"])

    q_comments = api.create_text_entry_question(
        sid,
        "<p><b>Thank you for participating!</b></p><p>You can leave any comments for the researchers below.</p>",
        text_type="ML",
        block_id=demographics_block,
    )
    print("  Demographics added")

    # ── Randomizer: treatment vs control ─────────────────────────────────────
    api.add_randomizer(
        sid,
        elements=[
            {"treatment_num": "1"},  # outgroup chatbot
            {"treatment_num": "2"},  # dogs chatbot (control)
        ],
        subset=1,
        even_presentation=True,
        position=1,  # after embedded data
    )
    print("  Randomizer added")

    # ── Branch logic: route to correct chatbot block ─────────────────────────
    # Treatment (treatment_num = 1) → outgroup chatbot block
    api.add_branch_embedded(
        sid,
        field_name="treatment_num",
        operator="EqualTo",
        value="1",
        block_ids=[chatbot_outgroup_block],
        description="Treatment: Outgroup chatbot",
    )

    # Control (treatment_num = 2) → dogs chatbot block
    api.add_branch_embedded(
        sid,
        field_name="treatment_num",
        operator="EqualTo",
        value="2",
        block_ids=[chatbot_dogs_block],
        description="Control: Dogs chatbot",
    )
    print("  Branch logic added")

    # ── Set condition label based on party (needs to be in flow) ─────────────
    # PartyNumeric piped from the party question
    # We need embedded data logic to set IngroupLabel, OutgroupLabel, condition
    # This is handled by the Heroku app based on the condition param,
    # but we need to set condition based on party choice.
    # In the original study, there are branches that set condition = twin_democrat or twin_republican
    # based on OutgroupLabel.
    # For now, set PartyNumeric from the slider, and condition from party choice.

    # Add branches to set condition based on party (only for treatment group)
    # Democrat → outgroup is Republican → condition = twin_republican
    api.add_branch(
        sid,
        conditions=[
            {
                "source_question_id": q_party["QuestionID"],
                "operator": "Selected",
                "choice_locator": f"q://{q_party['QuestionID']}/SelectableChoice/1",
            }
        ],
        block_ids=[],  # no block, just set embedded data
        description="Democrat → set outgroup labels",
    )

    api.add_branch(
        sid,
        conditions=[
            {
                "source_question_id": q_party["QuestionID"],
                "operator": "Selected",
                "choice_locator": f"q://{q_party['QuestionID']}/SelectableChoice/2",
            }
        ],
        block_ids=[],
        description="Republican → set outgroup labels",
    )
    print("  Condition routing added")

    # ── Prolific header ──────────────────────────────────────────────────────
    api.set_survey_header(sid, '<script src="https://assets.prolific.com/assets/js/qualtrics/qualtrics.min.js?rid=${e://Field/ResponseID}&t=CpL5AGiRrd86jdAomBBbrTReQAIiZz1fpQVd3tgpBD1RuS50WMY-66AT2FYwW_fYjCh1zopVqmR-vgnPHHwzb9J3Y4ZQWZRh3WTCRJApCSKv25sJCXWcmVAp"></script>')
    print("  Prolific header added")

    # ── Activate ─────────────────────────────────────────────────────────────
    api.activate_survey(sid)
    print("  Survey activated")

    # ── Print URLs ───────────────────────────────────────────────────────────
    preview_url = api.get_survey_url(sid)
    edit_url = f"https://{DC}/survey-builder/{sid}/edit"
    print(f"\n{'='*60}")
    print(f"Survey ID:   {sid}")
    print(f"Preview URL: {preview_url}")
    print(f"Edit URL:    {edit_url}")
    print(f"{'='*60}")

except Exception as e:
    print(f"\nERROR: {e}")
    print(f"Survey {sid} was partially created.")
    print(f"Edit URL: https://{DC}/survey-builder/{sid}/edit")
    import traceback
    traceback.print_exc()
