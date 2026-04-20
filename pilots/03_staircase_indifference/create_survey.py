#!/usr/bin/env python3
"""
Staircase indifference-point pilot — mortality reflection vs outgroup chat.

Design:
  - Single staircase: 3-min outgroup conversation vs X-min mortality reflection
  - Staircase titrates mortality duration; outgroup chat fixed at 3 min
  - Between-subjects randomization: outgroup conversation is human vs bot
  - Outgroup party derived from participant's own party ID (Dem ↔ Rep)
  - After indifference reached, final binary pick at those durations
  - CHOICES ARE REAL: participant actually does whichever task they pick
    - Mortality → classic TMT writing prompt + timer (threshold duration)
    - Chat → survey ends; external redirect handled by researcher
"""

import os
import time
import requests
from dotenv import load_dotenv
from qualtrics_sdk import QualtricsAPI

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
api = QualtricsAPI(
    api_token=os.getenv("QUALTRICS_API_TOKEN"),
    data_center=os.getenv("QUALTRICS_DATA_CENTER", "upenn.qualtrics.com"),
)
DC = os.getenv("QUALTRICS_DATA_CENTER", "upenn.qualtrics.com")

# URL of the deployed chat-pair Render app (see ./chat-pair-app/).
# Override via env var HUMAN_CHAT_URL once deployed.
HUMAN_CHAT_URL = os.getenv("HUMAN_CHAT_URL", "https://staircase-chat-pair.onrender.com")


def pause(n=3):
    time.sleep(n)


def force_response(survey_id, question_id):
    pause()
    q_data = api.get_question(survey_id, question_id)
    q_data["Validation"] = {"Settings": {"ForceResponse": "ON", "ForceResponseType": "ON", "Type": "None"}}
    api.update_question(survey_id, question_id, q_data)
    pause()


def set_question_js(survey_id, question_id, js_code):
    token = os.getenv("QUALTRICS_API_TOKEN")
    headers = {"X-API-TOKEN": token, "Content-Type": "application/json"}
    pause()
    r = requests.get(f"https://{DC}/API/v3/survey-definitions/{survey_id}/questions/{question_id}", headers=headers)
    q = r.json()["result"]
    q["QuestionJS"] = js_code
    requests.put(f"https://{DC}/API/v3/survey-definitions/{survey_id}/questions/{question_id}", headers=headers, json=q)
    pause()


# ── Content ─────────────────────────────────────────────────────────────────

CONSENT_HTML = """
<div style="max-width:650px; margin:0 auto; font-family: -apple-system, BlinkMacSystemFont, sans-serif; line-height:1.7; padding:20px; color:#1a1a1a;">
<h2 style="text-align:center;">Informed Consent</h2>
<p>You are invited to participate in a brief research study conducted by researchers at the University of Pennsylvania.</p>
<p><strong>What you'll do:</strong> You will make a series of choices between two tasks: (a) having a brief conversation with a member of the other political party (or a chatbot representing one), and (b) writing a short reflection on mortality. <strong>At the end of the study, you will actually do the task you prefer.</strong></p>
<p><strong>Time:</strong> This study takes approximately 5&ndash;10 minutes, depending on the task you pick.</p>
<p><strong>Risks:</strong> There are no known risks beyond those of everyday life. The mortality task involves briefly writing about death and dying, which some people find mildly unpleasant.</p>
<p><strong>Confidentiality:</strong> Your responses are anonymous and will be used only for research purposes.</p>
<p><strong>Voluntary:</strong> Participation is voluntary. You may stop at any time without penalty.</p>
<p>By continuing, you confirm that you are at least 18 years old and consent to participate.</p>
</div>
"""

INSTRUCTIONS_HTML = """
<div style="max-width:650px; margin:0 auto; font-family: -apple-system, BlinkMacSystemFont, sans-serif; line-height:1.8; padding:20px; color:#1a1a1a;">
<h2 style="text-align:center; color:#1a1a1a;">Instructions</h2>
<p style="margin-bottom:1.4em;">In this study, you'll choose between two tasks, and at the end <strong>you will actually do the one you pick</strong>.</p>
<p style="margin-bottom:1.4em;">First, we'll let you briefly try the mortality reflection task so you know what it feels like. Then we'll ask a series of <strong>would you rather</strong> questions to figure out the combination of task durations you're equally willing to do.</p>
<p style="margin-bottom:1.4em;">Your choices are real. Whichever option you pick at the end, you'll do it &mdash; so please answer based on what you'd genuinely choose.</p>
</div>
"""


# ── Staircase JS (mortality-only) ──────────────────────────────────────────

STAIRCASE_JS_TEMPLATE = r"""Qualtrics.SurveyEngine.addOnload(function() {
    var qEngine = this;
    qEngine.hideNextButton();

    var PARTY = "${q://__PARTY_QID__/ChoiceGroup/SelectedChoices}";
    var OUTGROUP = (PARTY.toLowerCase().indexOf("democrat") === 0) ? "Republican" : "Democrat";
    var PARTNER  = "${e://Field/chat_partner}" || "human";
    var CHAT_TITLE = (PARTNER === "bot")
        ? ("Talk to a " + OUTGROUP + " AI")
        : ("Talk to a " + OUTGROUP);
    var CHAT_SUB = (PARTNER === "bot")
        ? "Chat with an AI trained to represent the other party"
        : "Have a conversation with someone from the other party";

    Qualtrics.SurveyEngine.setEmbeddedData("outgroup_label", OUTGROUP);

    var TASK = {
        icon:  "\uD83D\uDC80",
        label: "Mortality Reflection",
        desc:  "Write about death and dying"
    };

    var root = document.getElementById("staircase-root");

    var style = document.createElement("style");
    style.textContent = [
        "#staircase-root { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 750px; margin: 0 auto; color: #1a1a1a; }",
        ".sr-phase { text-align:center; font-size:12px; text-transform:uppercase; letter-spacing:1px; color:#555; margin-bottom:4px; }",
        ".sr-header { text-align: center; margin-bottom: 6px; font-size: 15px; color: #333; font-weight: 500; }",
        ".sr-task-label { text-align: center; margin-bottom: 20px; font-size: 22px; color: #1a1a1a; font-weight: 700; }",
        ".sr-cards { display: flex; gap: 20px; justify-content: center; align-items: stretch; }",
        ".sr-card { flex: 1; max-width: 300px; border: 2px solid #ccc; border-radius: 12px; padding: 28px 20px; text-align: center; cursor: pointer; transition: all 0.15s ease; background: #fff; }",
        ".sr-card:hover { border-color: #2563eb; box-shadow: 0 2px 12px rgba(37,99,235,0.18); transform: translateY(-2px); }",
        ".sr-card.selected { border-color: #2563eb; background: #eff6ff; }",
        ".sr-card .icon { font-size: 40px; margin-bottom: 12px; }",
        ".sr-card .title { font-size: 16px; font-weight: 600; margin-bottom: 6px; color: #1a1a1a; }",
        ".sr-card .subtitle { font-size: 13px; color: #444; line-height: 1.4; }",
        ".sr-card .duration { font-size: 22px; font-weight: 700; color: #2563eb; margin-top: 12px; }",
        ".taste-wrap { max-width: 540px; margin: 0 auto; text-align: center; padding: 20px; }",
        ".taste-wrap .taste-desc { font-size: 14px; color: #555; margin-bottom: 16px; }",
        ".taste-wrap input[type=number] { font-size: 18px; padding: 10px 16px; border: 2px solid #ccc; border-radius: 8px; text-align: center; width: 120px; outline: none; }",
        ".taste-wrap input:focus { border-color: #2563eb; }",
        ".taste-btn { display: inline-block; margin-top: 16px; padding: 10px 32px; background: #2563eb !important; color: #fff !important; border: none !important; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; -webkit-appearance: none; appearance: none; }",
        ".taste-btn:hover { background: #1d4ed8 !important; }",
        ".taste-btn:disabled { background: #94a3b8 !important; cursor: default; opacity: 0.7; }",
        ".taste-feedback { margin-top: 14px; font-size: 15px; font-weight: 500; color:#555; }"
    ].join("\n");
    document.head.appendChild(style);

    function fmtDur(mins) {
        if (mins === Math.floor(mins)) return mins + (mins === 1 ? " minute" : " minutes");
        return mins.toFixed(1) + " minutes";
    }

    // ── Taste trial for mortality ───────────────────────────────────────
    function runTaste(onDone) {
        root.innerHTML = [
            '<div class="taste-wrap">',
            '  <div style="font-size:22px; font-weight:700; color:#1a1a1a; margin-bottom:4px;">' + TASK.icon + ' ' + TASK.label + '</div>',
            '  <div class="sr-phase">Try it out first</div>',
            '  <p class="taste-desc">If you pick this task at the end, you\'ll write short reflections on death and dying. Here\'s a quick sample question to give you a feel for it:</p>',
            '  <p style="font-size:16px; margin:20px 0;">How old do you think you will be when you die?</p>',
            '  <input type="number" id="taste-input" placeholder="Age">',
            '  <br><button class="taste-btn" id="taste-submit">Submit</button>',
            '  <div class="taste-feedback" id="taste-fb"></div>',
            '</div>'
        ].join("");
        var btn = document.getElementById("taste-submit");
        var inp = document.getElementById("taste-input");
        inp.focus();
        inp.addEventListener("keydown", function(e) { if (e.key === "Enter") btn.click(); });
        btn.addEventListener("click", function() {
            var val = parseInt(inp.value);
            if (!isFinite(val)) { inp.focus(); return; }
            Qualtrics.SurveyEngine.setEmbeddedData("taste_age_at_death", String(val));
            var fb = document.getElementById("taste-fb");
            fb.textContent = "Thanks. The real task is similar, but longer.";
            btn.disabled = true;
            setTimeout(onDone, 1500);
        });
    }

    // ── Staircase ───────────────────────────────────────────────────────
    function runStaircase(onDone) {
        var currentValue = 10;
        var step = 5;
        var minStep = 0.5;
        var minVal = 0.5;
        var maxVal = 30;
        var trials = [];
        var reversals = [];
        var lastChoice = null;
        var trialNum = 0;
        var maxTrials = 8;

        function showTrial() {
            trialNum++;
            root.innerHTML = [
                '<div class="sr-phase">' + TASK.icon + ' ' + TASK.label + ' vs. conversation</div>',
                '<div class="sr-header">Choice ' + trialNum + ' of ~' + maxTrials + '</div>',
                '<div class="sr-task-label">Which would you rather do?</div>',
                '<div class="sr-cards">',
                '  <div class="sr-card" id="sr-conv">',
                '    <div class="icon">\uD83D\uDCAC</div>',
                '    <div class="title">' + CHAT_TITLE + '</div>',
                '    <div class="subtitle">' + CHAT_SUB + '</div>',
                '    <div class="duration">3 minutes</div>',
                '  </div>',
                '  <div class="sr-card" id="sr-task">',
                '    <div class="icon">' + TASK.icon + '</div>',
                '    <div class="title">' + TASK.label + '</div>',
                '    <div class="subtitle">' + TASK.desc + '</div>',
                '    <div class="duration">' + fmtDur(currentValue) + '</div>',
                '  </div>',
                '</div>'
            ].join("");

            var convCard = document.getElementById("sr-conv");
            var taskCard = document.getElementById("sr-task");

            function handleChoice(chose) {
                if (chose === "conversation") convCard.classList.add("selected");
                else taskCard.classList.add("selected");
                convCard.style.pointerEvents = "none";
                taskCard.style.pointerEvents = "none";

                var isReversal = (lastChoice !== null && lastChoice !== chose);
                if (isReversal) {
                    reversals.push(currentValue);
                    step = Math.max(minStep, step / 2);
                }

                trials.push({
                    trial: trialNum, duration: currentValue, choice: chose,
                    step: step, reversal: isReversal
                });

                if (chose === "conversation") {
                    currentValue = Math.max(minVal, currentValue - step);
                } else {
                    currentValue = Math.min(maxVal, currentValue + step);
                }
                currentValue = Math.round(currentValue * 2) / 2;
                lastChoice = chose;

                var smallReversals = 0;
                for (var i = 0; i < trials.length; i++) {
                    if (trials[i].reversal && trials[i].step <= 1) smallReversals++;
                }

                setTimeout(function() {
                    if (trialNum >= maxTrials || smallReversals >= 3) {
                        var threshold;
                        if (reversals.length >= 2) {
                            threshold = (reversals[reversals.length - 1] + reversals[reversals.length - 2]) / 2;
                        } else if (reversals.length === 1) {
                            threshold = reversals[0];
                        } else {
                            threshold = currentValue;
                        }
                        threshold = Math.round(threshold * 2) / 2;
                        onDone(threshold, trials);
                    } else {
                        showTrial();
                    }
                }, 350);
            }

            convCard.addEventListener("click", function() { handleChoice("conversation"); });
            taskCard.addEventListener("click", function() { handleChoice("task"); });
        }

        showTrial();
    }

    runTaste(function() {
        runStaircase(function(threshold, trials) {
            Qualtrics.SurveyEngine.setEmbeddedData("mortality_threshold", String(threshold));
            Qualtrics.SurveyEngine.setEmbeddedData("mortality_trials", JSON.stringify(trials));
            qEngine.clickNextButton();
        });
    });
});
"""


# ── Final pick JS: 2 options (outgroup chat 3 min vs mortality at threshold) ─

FINAL_PICK_JS_TEMPLATE = r"""Qualtrics.SurveyEngine.addOnload(function() {
    var qEngine = this;
    qEngine.hideNextButton();

    var PARTY = "${q://__PARTY_QID__/ChoiceGroup/SelectedChoices}";
    var OUTGROUP = (PARTY.toLowerCase().indexOf("democrat") === 0) ? "Republican" : "Democrat";
    var PARTNER  = "${e://Field/chat_partner}" || "human";
    var CHAT_TITLE = (PARTNER === "bot")
        ? ("Talk to a " + OUTGROUP + " AI")
        : ("Talk to a " + OUTGROUP);
    var CHAT_SUB = (PARTNER === "bot")
        ? "Chat with an AI trained to represent the other party"
        : "Have a conversation with someone from the other party";

    var mortalityDur = parseFloat("${e://Field/mortality_threshold}");
    if (!isFinite(mortalityDur) || mortalityDur <= 0) mortalityDur = 3;

    function fmtDur(mins) {
        if (mins === Math.floor(mins)) return mins + (mins === 1 ? " minute" : " minutes");
        return mins.toFixed(1) + " minutes";
    }

    var root = document.getElementById("final-pick-root");

    var style = document.createElement("style");
    style.textContent = [
        "#final-pick-root { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 750px; margin: 0 auto; color: #1a1a1a; }",
        "#final-pick-root .fp-header { text-align:center; font-size:22px; font-weight:700; margin-bottom:8px; }",
        "#final-pick-root .fp-sub { text-align:center; font-size:14px; color:#555; margin-bottom:24px; line-height:1.5; }",
        "#final-pick-root .fp-real { text-align:center; font-size:13px; color:#dc2626; font-weight:600; margin-bottom:20px; }",
        "#final-pick-root .fp-cards { display:flex; gap:20px; justify-content:center; align-items:stretch; }",
        "#final-pick-root .fp-card { flex:1; max-width:320px; border:2px solid #ccc; border-radius:12px; padding:28px 20px; text-align:center; cursor:pointer; background:#fff; transition:all 0.15s; }",
        "#final-pick-root .fp-card:hover { border-color:#2563eb; box-shadow:0 2px 12px rgba(37,99,235,0.18); transform:translateY(-2px); }",
        "#final-pick-root .fp-card.selected { border-color:#2563eb; background:#eff6ff; }",
        "#final-pick-root .fp-card .icon { font-size:40px; margin-bottom:12px; }",
        "#final-pick-root .fp-card .title { font-size:16px; font-weight:600; margin-bottom:6px; }",
        "#final-pick-root .fp-card .sub { font-size:13px; color:#444; line-height:1.4; }",
        "#final-pick-root .fp-card .dur { font-size:22px; font-weight:700; color:#2563eb; margin-top:12px; }"
    ].join("\n");
    document.head.appendChild(style);

    root.innerHTML = [
        '<div class="fp-header">Final choice &mdash; which will you actually do?</div>',
        '<div class="fp-sub">Based on your earlier choices, you\'d be about equally willing to do either of these at the durations shown.</div>',
        '<div class="fp-real">Your pick is real: you\'ll do it next.</div>',
        '<div class="fp-cards">',
        '  <div class="fp-card" data-key="chat">',
        '    <div class="icon">\uD83D\uDCAC</div>',
        '    <div class="title">' + CHAT_TITLE + '</div>',
        '    <div class="sub">' + CHAT_SUB + '</div>',
        '    <div class="dur">3 minutes</div>',
        '  </div>',
        '  <div class="fp-card" data-key="mortality">',
        '    <div class="icon">\uD83D\uDC80</div>',
        '    <div class="title">Mortality Reflection</div>',
        '    <div class="sub">Write about death and dying</div>',
        '    <div class="dur">' + fmtDur(mortalityDur) + '</div>',
        '  </div>',
        '</div>'
    ].join("");

    var cards = root.querySelectorAll(".fp-card");
    for (var c = 0; c < cards.length; c++) {
        cards[c].addEventListener("click", function() {
            var k = this.getAttribute("data-key");
            this.classList.add("selected");
            for (var x = 0; x < cards.length; x++) cards[x].style.pointerEvents = "none";
            Qualtrics.SurveyEngine.setEmbeddedData("final_pick", k);
            Qualtrics.SurveyEngine.setEmbeddedData(
                "final_pick_duration",
                k === "chat" ? "3" : String(mortalityDur)
            );
            setTimeout(function() { qEngine.clickNextButton(); }, 400);
        });
    }
});
"""


# ── Mortality reflection task JS (TMT prompts + timer) ─────────────────────

CHAT_JS_TEMPLATE = r"""Qualtrics.SurveyEngine.addOnload(function() {
    var qEngine = this;
    qEngine.hideNextButton();

    var PARTNER  = "${e://Field/chat_partner}" || "human";
    var OUTGROUP = "${e://Field/outgroup_label}" || "Republican";
    var PARTY    = "${q://__PARTY_QID__/ChoiceGroup/SelectedChoices}";
    var botCond  = "twin_" + OUTGROUP.toLowerCase();
    var rid      = "${e://Field/ResponseID}";
    var HUMAN_CHAT_URL = "__HUMAN_CHAT_URL__";

    var root = document.getElementById("chat-root");

    var style = document.createElement("style");
    style.textContent = [
        "#chat-root { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 960px; margin: 0 auto; color: #1a1a1a; }",
        "#chat-root .timer-bar { position:sticky; top:0; background:#fff; padding:14px 0; z-index:10; border-bottom:1px solid #eee; margin-bottom:12px; text-align:center; }",
        "#chat-root .timer { display:inline-block; font-size:26px; font-weight:700; font-variant-numeric:tabular-nums; }",
        "#chat-root .timer.low { color:#dc2626; }",
        "#chat-root .timer-label { font-size:12px; color:#555; text-transform:uppercase; letter-spacing:1px; margin-right:8px; }",
        "#chat-root .chat-intro { text-align:center; color:#555; font-size:14px; margin-bottom:12px; line-height:1.5; }",
        "#chat-root .iframe-wrap { width:100%; border:1px solid #e5e5e5; border-radius:14px; overflow:hidden; background:#fafafa; }",
        "#chat-root iframe { width:100%; height:75vh; min-height:500px; border:0; display:block; }",
        "#chat-root .human-placeholder { padding:40px 24px; text-align:center; border:2px dashed #d4d4d4; border-radius:12px; background:#fafafa; }",
        "#chat-root .human-placeholder h3 { margin-top:0; color:#1a1a1a; }",
        "#chat-root .done-btn { display:block; margin:20px auto 0; padding:12px 28px; font-size:16px; background:#2563eb; color:#fff; border:none; border-radius:8px; cursor:pointer; font-weight:600; }",
        "#chat-root .done-btn:disabled { background:#94a3b8; cursor:default; }",
        "#chat-root .done-note { text-align:center; margin-top:14px; color:#555; font-size:13px; }"
    ].join("\n");
    document.head.appendChild(style);

    function fmtTime(s) {
        var m = Math.floor(s/60), r = s%60;
        return m + ':' + (r<10?'0':'') + r;
    }

    if (PARTNER === "bot") {
        var durSec = 180;  // 3 minutes
        var botUrl = "https://reframe001-7a186c892e5e.herokuapp.com/?condition=" +
                     encodeURIComponent(botCond) + "&id=" + encodeURIComponent(rid);
        root.innerHTML = [
            '<div class="timer-bar"><span class="timer-label">Time remaining</span><span class="timer" id="chat-timer">' + fmtTime(durSec) + '</span></div>',
            '<p class="chat-intro">You\'ve been connected to an AI trained to represent a typical ' + OUTGROUP + '. Chat with them for 3 minutes about their political views.</p>',
            '<div class="iframe-wrap"><iframe id="bot-iframe" src="' + botUrl + '" scrolling="no"></iframe></div>',
            '<p class="done-note">The continue button will appear when the timer ends.</p>',
            '<button class="done-btn" id="chat-done" style="display:none;">Continue</button>'
        ].join("");
        Qualtrics.SurveyEngine.setEmbeddedData("chat_start_ts", String(Date.now()));

        var timerEl = document.getElementById("chat-timer");
        var doneBtn = document.getElementById("chat-done");
        var remaining = durSec;
        var interval = setInterval(function() {
            remaining--;
            timerEl.textContent = fmtTime(Math.max(0, remaining));
            if (remaining <= 30) timerEl.className = "timer low";
            if (remaining <= 0) {
                clearInterval(interval);
                Qualtrics.SurveyEngine.setEmbeddedData("chat_end_ts", String(Date.now()));
                doneBtn.style.display = "block";
                doneBtn.addEventListener("click", function() { qEngine.clickNextButton(); });
            }
        }, 1000);

    } else {
        // Human condition: iframe the Render pair-chat app
        var humanUrl = HUMAN_CHAT_URL +
            "/?party=" + encodeURIComponent(PARTY) +
            "&outgroup=" + encodeURIComponent(OUTGROUP) +
            "&id=" + encodeURIComponent(rid);
        root.innerHTML = [
            '<p class="chat-intro">You\'ll be matched with another participant (a ' + OUTGROUP + ') for a 3-minute conversation.</p>',
            '<div class="iframe-wrap"><iframe id="human-iframe" src="' + humanUrl + '"></iframe></div>',
            '<p class="done-note" id="human-status">Matching in progress&hellip;</p>',
            '<button class="done-btn" id="chat-done" style="display:none;">Continue</button>'
        ].join("");
        Qualtrics.SurveyEngine.setEmbeddedData("chat_start_ts", String(Date.now()));

        var doneBtn = document.getElementById("chat-done");
        var statusEl = document.getElementById("human-status");

        window.addEventListener("message", function(evt) {
            if (!evt.data || !evt.data.type) return;
            if (evt.data.type === "chat_ended") {
                Qualtrics.SurveyEngine.setEmbeddedData("chat_end_ts", String(Date.now()));
                Qualtrics.SurveyEngine.setEmbeddedData("chat_end_reason", String(evt.data.reason || ""));
                statusEl.textContent = "Chat complete. Click Continue.";
                doneBtn.style.display = "block";
            } else if (evt.data.type === "chat_continue") {
                Qualtrics.SurveyEngine.setEmbeddedData("chat_end_ts", String(Date.now()));
                Qualtrics.SurveyEngine.setEmbeddedData("chat_end_reason", String(evt.data.reason || ""));
                qEngine.clickNextButton();
            }
        });

        doneBtn.addEventListener("click", function() { qEngine.clickNextButton(); });
    }
});
"""


MORTALITY_TASK_JS = r"""Qualtrics.SurveyEngine.addOnload(function() {
    var qEngine = this;
    qEngine.hideNextButton();

    var durMins = parseFloat("${e://Field/mortality_threshold}");
    if (!isFinite(durMins) || durMins <= 0) durMins = 3;
    var durSec = Math.round(durMins * 60);

    var root = document.getElementById("mortality-root");

    var style = document.createElement("style");
    style.textContent = [
        "#mortality-root { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 720px; margin: 0 auto; color: #1a1a1a; line-height:1.6; }",
        "#mortality-root h2 { text-align: center; margin-bottom: 8px; }",
        "#mortality-root .mort-intro { text-align:center; color:#555; font-size:14px; margin-bottom:20px; }",
        "#mortality-root .mort-prompt { background:#fef3f2; border-left:4px solid #dc2626; padding:14px 18px; margin:16px 0; border-radius:4px; font-size:15px; }",
        "#mortality-root textarea { width:100%; box-sizing:border-box; min-height:200px; padding:14px; font-size:15px; border:2px solid #ccc; border-radius:8px; resize:vertical; font-family:inherit; line-height:1.5; }",
        "#mortality-root textarea:focus { border-color:#2563eb; outline:none; }",
        "#mortality-root .timer-bar { position:sticky; top:0; background:#fff; padding:14px 0; z-index:10; border-bottom:1px solid #eee; margin-bottom:20px; text-align:center; }",
        "#mortality-root .timer { display:inline-block; font-size:28px; font-weight:700; font-variant-numeric:tabular-nums; color:#1a1a1a; }",
        "#mortality-root .timer.low { color:#dc2626; }",
        "#mortality-root .timer-label { font-size:12px; color:#555; text-transform:uppercase; letter-spacing:1px; margin-right:8px; }",
        "#mortality-root .done-note { text-align:center; margin-top:16px; color:#555; font-size:13px; }",
        "#mortality-root .done-btn { display:block; margin:20px auto 0; padding:12px 28px; font-size:16px; background:#2563eb; color:#fff; border:none; border-radius:8px; cursor:pointer; font-weight:600; }",
        "#mortality-root .done-btn:disabled { background:#94a3b8; cursor:default; }"
    ].join("\n");
    document.head.appendChild(style);

    function fmtTime(s) {
        var m = Math.floor(s/60), r = s%60;
        return m + ':' + (r<10?'0':'') + r;
    }

    root.innerHTML = [
        '<div class="timer-bar"><span class="timer-label">Time remaining</span><span class="timer" id="mort-timer">' + fmtTime(durSec) + '</span></div>',
        '<h2>\uD83D\uDC80 Mortality Reflection</h2>',
        '<p class="mort-intro">Please read each prompt and write your honest reflections. Write continuously until the timer ends.</p>',
        '<div class="mort-prompt"><strong>Prompt 1.</strong> Please briefly describe the emotions that the thought of your own death arouses in you.</div>',
        '<div class="mort-prompt"><strong>Prompt 2.</strong> Jot down, as specifically as you can, what you think will happen to you as you physically die, and once you are physically dead.</div>',
        '<textarea id="mort-text" placeholder="Write your reflections here..." autofocus></textarea>',
        '<p class="done-note">The continue button will appear when the timer ends.</p>',
        '<button class="done-btn" id="mort-done" style="display:none;">Continue</button>'
    ].join("");

    var textarea = document.getElementById("mort-text");
    textarea.focus();
    var lastSaved = "";
    function saveText() {
        var v = textarea.value;
        if (v !== lastSaved) {
            Qualtrics.SurveyEngine.setEmbeddedData("mortality_response", v);
            Qualtrics.SurveyEngine.setEmbeddedData("mortality_response_chars", String(v.length));
            lastSaved = v;
        }
    }
    textarea.addEventListener("input", saveText);
    var saveInterval = setInterval(saveText, 5000);

    var startTs = Date.now();
    var remaining = durSec;
    var timerEl = document.getElementById("mort-timer");
    var doneBtn = document.getElementById("mort-done");
    Qualtrics.SurveyEngine.setEmbeddedData("mortality_start_ts", String(startTs));

    var interval = setInterval(function() {
        remaining--;
        timerEl.textContent = fmtTime(Math.max(0, remaining));
        if (remaining <= 30) timerEl.className = "timer low";
        if (remaining <= 0) {
            clearInterval(interval);
            clearInterval(saveInterval);
            saveText();
            Qualtrics.SurveyEngine.setEmbeddedData("mortality_end_ts", String(Date.now()));
            doneBtn.style.display = "block";
            doneBtn.addEventListener("click", function() {
                saveText();
                qEngine.clickNextButton();
            });
        }
    }, 1000);
});
"""


# ── Create survey ───────────────────────────────────────────────────────────

survey = api.create_survey("Staircase Indifference Pilot — Mortality vs Outgroup Chat")
sid = survey["SurveyID"]
print(f"Created survey: {sid}")

try:
    fields = {
        "chat_partner":                 {"type": "text"},
        "outgroup_label":               {"type": "text"},
        "taste_age_at_death":           {"type": "text"},
        "mortality_threshold":          {"type": "text"},
        "mortality_trials":             {"type": "text"},
        "final_pick":                   {"type": "text"},
        "final_pick_duration":          {"type": "text"},
        "mortality_response":           {"type": "text"},
        "mortality_response_chars":     {"type": "text"},
        "mortality_start_ts":           {"type": "text"},
        "mortality_end_ts":             {"type": "text"},
        "chat_start_ts":                {"type": "text"},
        "chat_end_ts":                  {"type": "text"},
        "chat_end_reason":              {"type": "text"},
    }
    api.set_embedded_data_fields(sid, fields, position="start")
    print("Set embedded data fields"); pause(5)

    consent_block      = api.create_block(sid, "Consent")["BlockID"]; pause()
    party_block        = api.create_block(sid, "Party ID")["BlockID"]; pause()
    instructions_block = api.create_block(sid, "Instructions")["BlockID"]; pause()
    staircase_block    = api.create_block(sid, "Staircase")["BlockID"]; pause()
    final_pick_block   = api.create_block(sid, "Final Pick")["BlockID"]; pause()
    mortality_block    = api.create_block(sid, "Mortality Reflection Task")["BlockID"]; pause()
    chat_block         = api.create_block(sid, "Chat (Bot iframe or Human placeholder)")["BlockID"]; pause()
    end_block          = api.create_block(sid, "End")["BlockID"]; pause()
    print("Created blocks")

    # ── Consent ─────────────────────────────────────────────────────────────
    api.create_descriptive_text(sid, CONSENT_HTML, block_id=consent_block); pause()

    # ── Party ID ────────────────────────────────────────────────────────────
    q_party = api.create_multiple_choice_question(
        sid,
        "Which political party do you most identify with?",
        choices=["Democrat", "Republican"],
        block_id=party_block,
    )
    force_response(sid, q_party["QuestionID"])
    party_qid = q_party["QuestionID"]

    # ── Instructions ────────────────────────────────────────────────────────
    api.create_descriptive_text(sid, INSTRUCTIONS_HTML, block_id=instructions_block); pause()

    # ── Staircase ───────────────────────────────────────────────────────────
    staircase_js  = STAIRCASE_JS_TEMPLATE.replace("__PARTY_QID__", party_qid)
    final_pick_js = FINAL_PICK_JS_TEMPLATE.replace("__PARTY_QID__", party_qid)

    q_staircase = api.create_descriptive_text(
        sid,
        '<div id="staircase-root" style="min-height:400px;">Loading…</div>',
        block_id=staircase_block,
    )
    set_question_js(sid, q_staircase["QuestionID"], staircase_js)

    # ── Final pick ──────────────────────────────────────────────────────────
    q_final = api.create_descriptive_text(
        sid,
        '<div id="final-pick-root" style="min-height:300px;">Loading…</div>',
        block_id=final_pick_block,
    )
    set_question_js(sid, q_final["QuestionID"], final_pick_js)

    # ── Mortality reflection (real task) ────────────────────────────────────
    q_mortality = api.create_descriptive_text(
        sid,
        '<div id="mortality-root" style="min-height:500px;">Loading…</div>',
        block_id=mortality_block,
    )
    set_question_js(sid, q_mortality["QuestionID"], MORTALITY_TASK_JS)

    # ── Chat block (bot iframe or human placeholder) ────────────────────────
    chat_js = (CHAT_JS_TEMPLATE
               .replace("__PARTY_QID__", party_qid)
               .replace("__HUMAN_CHAT_URL__", HUMAN_CHAT_URL))
    q_chat = api.create_descriptive_text(
        sid,
        '<div id="chat-root" style="min-height:500px;">Loading…</div>',
        block_id=chat_block,
    )
    set_question_js(sid, q_chat["QuestionID"], chat_js)

    # ── End (shared final page) ─────────────────────────────────────────────
    api.create_descriptive_text(
        sid,
        """
<div style="max-width:600px; margin:0 auto; text-align:center; padding:40px 20px; font-family:-apple-system, sans-serif; line-height:1.7;">
<h2>Thank you!</h2>
<p>You've finished the study. Your responses have been recorded.</p>
</div>
""",
        block_id=end_block,
    ); pause()

    # ── Randomizer: chat_partner = human vs bot ─────────────────────────────
    api.add_randomizer(
        sid,
        elements=[
            {"chat_partner": "human"},
            {"chat_partner": "bot"},
        ],
        subset=1,
        even_presentation=True,
        position=1,
    )
    print("Added human/bot randomizer")

    # ── Branch: mortality pick → mortality task ─────────────────────────────
    api.add_branch_embedded(
        sid,
        field_name="final_pick",
        operator="EqualTo",
        value="mortality",
        block_ids=[mortality_block],
        description="Picked mortality → do mortality task",
    )
    print("Added mortality branch")

    # ── Branch: chat pick → chat block (bot iframe or human placeholder) ────
    api.add_branch_embedded(
        sid,
        field_name="final_pick",
        operator="EqualTo",
        value="chat",
        block_ids=[chat_block],
        description="Picked chat → chat block",
    )
    print("Added chat branch")

    # ── Activate ────────────────────────────────────────────────────────────
    api.activate_survey(sid)
    print("Survey activated")

    preview_url = api.get_survey_url(sid)
    edit_url = f"https://{DC}/survey-builder/{sid}/edit"
    print()
    print("=" * 60)
    print(f"Survey ID:   {sid}")
    print(f"Preview URL: {preview_url}")
    print(f"Edit URL:    {edit_url}")
    print("=" * 60)

except Exception as e:
    print(f"\nERROR: {e}")
    print(f"Survey {sid} was partially created.")
    print(f"Edit URL: https://{DC}/survey-builder/{sid}/edit")
    import traceback
    traceback.print_exc()
