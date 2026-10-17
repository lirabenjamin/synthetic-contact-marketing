#!/usr/bin/env python3
"""Create the Green Market game survey on Qualtrics."""

import os
from dotenv import load_dotenv
from qualtrics_sdk import QualtricsAPI

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
api = QualtricsAPI(
    api_token=os.getenv("QUALTRICS_API_TOKEN"),
    data_center=os.getenv("QUALTRICS_DATA_CENTER", "upenn.qualtrics.com")
)


# ── Game HTML builder ────────────────────────────────────────────────────────

def build_game_html():
    return r'''
<span id="gm-diff" style="display:none">${e://Field/difficulty}</span>

<style>
#gm-root{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;max-width:680px;margin:0 auto;color:#1f2937}
.gm-header{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:12px}
.gm-title{font-size:20px;font-weight:800;color:#111827}
.gm-sub{font-size:12px;color:#6b7280}
.gm-green{color:#16a34a}
.gm-red{color:#dc2626}
.gm-budget{font-size:18px;font-weight:800}
.gm-bar-wrap{height:8px;background:#e5e7eb;border-radius:4px;overflow:hidden;margin-bottom:16px}
.gm-bar-fill{height:100%;border-radius:4px;transition:width .2s}
.gm-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px}
.gm-card{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:12px}
.gm-card-name{font-size:13px;font-weight:700;color:#111827;margin-bottom:1px}
.gm-card-arch{font-size:10px;color:#9ca3af;margin-bottom:5px}
.gm-pbar{display:flex;height:18px;border-radius:4px;overflow:hidden}
.gm-pbar-r{background:#dc2626;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff}
.gm-pbar-d{background:#2563eb;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff}
.gm-tag{display:inline-block;padding:1px 6px;border-radius:9999px;font-size:10px;font-weight:700}
.gm-tag-low{background:#dcfce7;color:#15803d}
.gm-tag-med{background:#fef9c3;color:#a16207}
.gm-tag-hi{background:#fee2e2;color:#b91c1c}
.gm-tag-vhi{background:#fce7f3;color:#9d174d}
.gm-ctrl{margin-top:8px}
.gm-ctrl-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:2px}
.gm-ctrl-label{font-size:11px;font-weight:600;color:#374151}
.gm-ctrl-val{font-size:11px;font-weight:700}
.gm-slider{width:100%;accent-color:#16a34a;margin-bottom:4px}
.gm-num{width:100%;padding:4px 8px;border:1px solid #d1d5db;border-radius:5px;font-size:12px;outline:none;box-sizing:border-box}
.gm-actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center;justify-content:center;margin-top:8px}
.gm-btn-pri{background:#16a34a;color:#fff !important;border:none;border-radius:7px;padding:10px 24px;font-size:15px;font-weight:600;cursor:pointer}
.gm-btn-pri:hover{background:#15803d}
.gm-btn-pri:disabled{background:#9ca3af;color:#fff !important;cursor:not-allowed}
.gm-btn-sec{background:#e5e7eb;color:#374151;border:none;border-radius:7px;padding:8px 18px;font-size:13px;font-weight:600;cursor:pointer}
.gm-btn-sec:hover{background:#d1d5db}
.gm-btn-sec:disabled{background:#f3f4f6;color:#9ca3af;cursor:not-allowed}
.gm-warn{color:#dc2626;text-align:center;margin-top:6px;font-size:13px}
.gm-table{width:100%;border-collapse:collapse;margin-bottom:14px;background:#fff;border-radius:8px;overflow:hidden;border:1px solid #e5e7eb}
.gm-table th,.gm-table td{padding:7px 10px;text-align:left;border-bottom:1px solid #e5e7eb;font-size:13px}
.gm-table th{font-weight:700;color:#374151;background:#f9fafb}
.gm-summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:16px}
.gm-scard{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:10px;text-align:center}
.gm-big{font-size:22px;font-weight:800;margin-top:2px}
.gm-intro{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:16px;margin-bottom:16px}
.gm-intro h3{color:#15803d;margin:0 0 8px;font-size:16px}
.gm-intro ul{margin:6px 0 0;padding-left:18px;font-size:13px;line-height:1.8}
</style>

<div id="gm-root"></div>

<script>
(function(){
var diffEl=document.getElementById("gm-diff");
var difficulty=diffEl?diffEl.textContent.trim():"medium";
var PARAMS={easy:{halfMax:25000,K:1.5,noise:.2},medium:{halfMax:30000,K:2,noise:.3},hard:{halfMax:35000,K:2.5,noise:.35}};
var P=PARAMS[difficulty]||PARAMS.medium;
var RECEP={dem:.75,rep:.65};
var PRICE=7,BUDGET=100000,ROUNDS=8;
var TOWNS=[
{id:"harlan",name:"Harlan County, KY",arch:"Rural Appalachian",rS:.78,dS:.22,mkt:50000,comp:.20},
{id:"williamson",name:"Williamson County, TN",arch:"Affluent Southern Suburb",rS:.72,dS:.28,mkt:75000,comp:.35},
{id:"burlington",name:"Burlington, VT",arch:"New England College Town",rS:.32,dS:.68,mkt:45000,comp:.45},
{id:"middlesex",name:"Middlesex County, MA",arch:"Urban Northeast Metro",rS:.28,dS:.72,mkt:65000,comp:.85}
];

function normalDraw(m,s){var u1,u2;do{u1=Math.random()}while(u1===0);u2=Math.random();return m+s*Math.sqrt(-2*Math.log(u1))*Math.cos(2*Math.PI*u2)}
function sC(a){return(a*a)/(a*a+P.halfMax*P.halfMax)}
function expRev(t,a){if(a<=0)return 0;var r=t.mkt*(t.rS*RECEP.rep+t.dS*RECEP.dem);return r*sC(a)*Math.exp(-P.K*t.comp)*PRICE}
function payoff(t,a){if(a<=0)return 0;var m=expRev(t,a);var s=m*P.noise+Math.sqrt(a)*2;return Math.max(0,normalDraw(m,s))}
function compOpt(){var step=5000,al={};TOWNS.forEach(function(t){al[t.id]=0});for(var i=0;i<BUDGET/step;i++){var best=null,bg=-1/0;TOWNS.forEach(function(t){var g=expRev(t,al[t.id]+step)-expRev(t,al[t.id]);if(g>bg){bg=g;best=t.id}});al[best]+=step}var tot=0;TOWNS.forEach(function(t){tot+=expRev(t,al[t.id])});return{alloc:al,total:tot}}
var OPT=compOpt();

function fmt(n){return"$"+Math.round(n).toLocaleString()}
function compLabel(c){if(c<=.25)return{t:"Low",c:"gm-tag-low"};if(c<=.5)return{t:"Medium",c:"gm-tag-med"};if(c<=.75)return{t:"High",c:"gm-tag-hi"};return{t:"Very High",c:"gm-tag-vhi"}}
function setED(k,v){try{Qualtrics.SurveyEngine.setEmbeddedData(k,String(v))}catch(e){}}

var state={round:1,screen:"tut0",allocs:{},cumRev:0,history:[],tutStep:0};
TOWNS.forEach(function(t){state.allocs[t.id]=0});
var root=document.getElementById("gm-root");

var nbObs;try{var nb=document.getElementById("NextButton");if(nb){nb.style.display="none";nb.style.visibility="hidden";nbObs=new MutationObserver(function(){nb.style.display="none";nb.style.visibility="hidden"});nbObs.observe(nb,{attributes:true,attributeFilter:["style"]})}}catch(e){}

function render(){
if(state.screen.indexOf("tut")===0)renderTutorial();
else if(state.screen==="alloc")renderAlloc();
else if(state.screen==="results")renderResults();
else if(state.screen==="done")renderDone();
}

function tutMsg(icon,title,body,btnText,nextScreen){
var h='<div style="text-align:center;padding:24px;max-width:520px;margin:0 auto">';
h+='<div style="font-size:40px;margin-bottom:8px">'+icon+'</div>';
h+='<div style="font-size:22px;font-weight:800;color:#111827;margin-bottom:12px">'+title+'</div>';
h+='<div style="font-size:15px;color:#374151;line-height:1.7;margin-bottom:20px">'+body+'</div>';
h+='<button class="gm-btn-pri" id="gm-tut-next" style="font-size:15px;padding:10px 32px">'+btnText+'</button></div>';
root.innerHTML=h;
document.getElementById("gm-tut-next").onclick=function(){state.screen=nextScreen;render()};
}

function renderTutorial(){
var s=state.screen;
if(s==="tut0"){
tutMsg("&#127807;","Green Market",'You\'re the marketing director for <strong>EcoChoice</strong>, a sustainable home products company.',"Next \u2192","tut1");
}else if(s==="tut1"){
tutMsg("&#128176;","Your Budget",'Each round you get <strong>$100,000</strong> to spend across <strong>4 US markets</strong>.',"Next \u2192","tut2");
}else if(s==="tut2"){
tutMsg("&#128205;","The Markets",'Each market has a <strong>political lean</strong> and a <strong>competition level</strong>. Both affect your revenue.',"Show me \u2192","tut3");
}else if(s==="tut3"){
// Show the 4 market cards (no sliders) so they can see the layout
var h='<div style="max-width:520px;margin:0 auto;padding:12px">';
h+='<div style="font-size:18px;font-weight:800;color:#111827;margin-bottom:4px;text-align:center">These are your 4 markets</div>';
h+='<div style="font-size:13px;color:#6b7280;text-align:center;margin-bottom:14px">The <span style="color:#dc2626;font-weight:700">red</span>/<span style="color:#2563eb;font-weight:700">blue</span> bar shows political lean. The tag shows competition.</div>';
h+='<div class="gm-grid">';
TOWNS.forEach(function(t){
var rP=Math.round(t.rS*100),dP=100-rP,cl=compLabel(t.comp);
h+='<div class="gm-card"><div class="gm-card-name">'+t.name+'</div><div class="gm-card-arch">'+t.arch+'</div>';
h+='<div class="gm-pbar"><div class="gm-pbar-r" style="width:'+rP+'%">'+(rP>12?rP+"% R":"")+'</div><div class="gm-pbar-d" style="width:'+dP+'%">'+(dP>12?dP+"% D":"")+'</div></div>';
h+='<div style="margin-top:3px"><span class="gm-tag '+cl.c+'">'+cl.t+' competition</span></div></div>';
});
h+='</div><div style="text-align:center;margin-top:10px"><button class="gm-btn-pri" id="gm-tut-next" style="font-size:15px;padding:10px 32px">Got it \u2192</button></div></div>';
root.innerHTML=h;
document.getElementById("gm-tut-next").onclick=function(){state.screen="tut4";render()};
}else if(s==="tut4"){
tutMsg("&#127918;","How It Works",'Use the <strong>sliders</strong> to split your budget, then hit <strong>Submit</strong>. You\'ll see how much revenue each market generated.',"Next \u2192","tut5");
}else if(s==="tut5"){
tutMsg("&#127942;","Ready?",'Play <strong>8 rounds</strong>. Maximize your <strong>total revenue</strong>. Learn which markets pay off.',"Let\'s play! \u2192","alloc");
}
}

function renderAlloc(){
var tA=0;TOWNS.forEach(function(t){tA+=state.allocs[t.id]});
var rem=BUDGET-tA,over=tA>BUDGET,none=tA===0,pct=Math.min(100,(tA/BUDGET)*100);
var h="";
h+='<div class="gm-header"><div><div class="gm-title">Round '+state.round+' <span class="gm-sub">of '+ROUNDS+'</span></div>';
h+='<div class="gm-sub">Cumulative: <b class="gm-green">'+fmt(state.cumRev)+'</b></div></div>';
h+='<div style="text-align:right"><div class="gm-budget '+(over?"gm-red":"gm-green")+'">'+(over?"Over by "+fmt(tA-BUDGET):fmt(rem)+" left")+'</div>';
h+='<div class="gm-sub">Budget: '+fmt(BUDGET)+'</div></div></div>';
h+='<div class="gm-bar-wrap"><div class="gm-bar-fill" style="width:'+pct+'%;background:'+(over?"#dc2626":"#16a34a")+'"></div></div>';
h+='<div class="gm-grid">';
TOWNS.forEach(function(t){
var a=state.allocs[t.id],ap=Math.round((a/BUDGET)*100),cl=compLabel(t.comp);
var rP=Math.round(t.rS*100),dP=100-rP;
h+='<div class="gm-card">';
h+='<div class="gm-card-name">'+t.name+'</div>';
h+='<div class="gm-card-arch">'+t.arch+'</div>';
h+='<div class="gm-pbar"><div class="gm-pbar-r" style="width:'+rP+'%">'+(rP>12?rP+"% R":"")+'</div><div class="gm-pbar-d" style="width:'+dP+'%">'+(dP>12?dP+"% D":"")+'</div></div>';
h+='<div style="margin-top:3px"><span class="gm-tag '+cl.c+'">'+cl.t+' competition</span></div>';
h+='<div class="gm-ctrl"><div class="gm-ctrl-row"><span class="gm-ctrl-label">Allocation</span><span class="gm-green gm-ctrl-val">'+fmt(a)+" ("+ap+"%)</span></div>";
h+='<input type="range" class="gm-slider" min="0" max="'+BUDGET+'" step="5000" value="'+a+'" data-tid="'+t.id+'">';
h+='<input type="number" class="gm-num" min="0" max="'+BUDGET+'" step="1000" value="'+a+'" data-tid="'+t.id+'">';
h+='</div></div>';
});
h+='</div>';
h+='<div class="gm-actions">';
h+='<button class="gm-btn-sec" id="gm-clear">Clear All</button>';
h+='<button class="gm-btn-sec" id="gm-scale"'+(none?" disabled":"")+'>Scale to $100k</button>';
h+='<button class="gm-btn-pri" id="gm-submit"'+(over||none?" disabled":"")+'>Submit Allocations &#8594;</button>';
h+='</div>';
if(over)h+='<div class="gm-warn">Over budget — reduce allocations before submitting.</div>';
root.innerHTML=h;

root.querySelectorAll(".gm-slider").forEach(function(el){
el.addEventListener("input",function(){state.allocs[this.dataset.tid]=Math.round(Number(this.value)/1000)*1000;render()});
});
root.querySelectorAll(".gm-num").forEach(function(el){
el.addEventListener("change",function(){state.allocs[this.dataset.tid]=Math.max(0,Math.round(Number(this.value)/1000)*1000);render()});
});
document.getElementById("gm-clear").onclick=function(){TOWNS.forEach(function(t){state.allocs[t.id]=0});render()};
document.getElementById("gm-scale").onclick=function(){
var tot=0;TOWNS.forEach(function(t){tot+=state.allocs[t.id]});if(tot===0)return;
var f=BUDGET/tot;TOWNS.forEach(function(t){state.allocs[t.id]=Math.round(state.allocs[t.id]*f/1000)*1000});
var nT=0;TOWNS.forEach(function(t){nT+=state.allocs[t.id]});state.allocs[TOWNS[0].id]+=BUDGET-nT;render();
};
document.getElementById("gm-submit").onclick=function(){submitRound()};
}

function submitRound(){
var payouts={},rT=0,rAlloc=0;
TOWNS.forEach(function(t){
var p=payoff(t,state.allocs[t.id]);payouts[t.id]=p;rT+=p;
if(t.rS>.5)rAlloc+=state.allocs[t.id];
});
var entry={round:state.round,allocs:{},payouts:payouts,total:rT,pctR:Math.round((rAlloc/BUDGET)*100)};
TOWNS.forEach(function(t){entry.allocs[t.id]=state.allocs[t.id]});
state.history.push(entry);state.cumRev+=rT;
var r=state.round;
TOWNS.forEach(function(t){
setED("game_round_"+r+"_alloc_"+t.id,entry.allocs[t.id]);
setED("game_round_"+r+"_rev_"+t.id,Math.round(payouts[t.id]));
});
setED("game_round_"+r+"_total_rev",Math.round(rT));
setED("game_round_"+r+"_pct_R",entry.pctR);
setED("game_cumulative_revenue",Math.round(state.cumRev));
if(state.round===ROUNDS){
setED("game_pct_optimal",Math.round((state.cumRev/(OPT.total*ROUNDS))*100));
var totR=0,totB=0;state.history.forEach(function(h){TOWNS.forEach(function(t){if(t.rS>.5)totR+=h.allocs[t.id]});totB+=BUDGET});
setED("game_total_pct_R",Math.round((totR/totB)*100));
}
state.screen="results";render();
}

function renderResults(){
var entry=state.history[state.history.length-1];
var prev=state.history.length>=2?state.history[state.history.length-2]:null;
var isLast=state.round===ROUNDS;
var h='<div class="gm-title">Round '+state.round+" Results</div>";
h+='<div class="gm-sub" style="margin-bottom:12px">'+(state.round<=3?"Early days — keep exploring!":state.round<=7?"Notice any patterns?":isLast?"Final round complete!":"Almost done — optimize your strategy.")+"</div>";
h+='<table class="gm-table"><thead><tr><th>Market</th><th style="text-align:right">Spent</th><th style="text-align:right">Revenue</th><th style="text-align:right">ROI</th></tr></thead><tbody>';
TOWNS.forEach(function(t){
var a=entry.allocs[t.id],p=entry.payouts[t.id],did=a>0;
var roi=did?(p/a).toFixed(2)+"x":"\u2014";
h+='<tr style="opacity:'+(did?1:.4)+'"><td><b style="font-size:12px">'+t.name+'</b><br><span class="gm-sub">'+t.arch+'</span></td>';
h+='<td style="text-align:right;font-size:12px">'+(did?fmt(a):"\u2014")+"</td>";
h+='<td style="text-align:right;font-size:12px;font-weight:'+(did?700:400)+";color:"+(did?"#111827":"#999")+'">'+(did?fmt(p):"\u2014")+"</td>";
h+='<td style="text-align:right;font-size:12px">'+roi+"</td></tr>";
});
h+="</tbody></table>";
h+='<div class="gm-summary">';
h+='<div class="gm-scard"><div class="gm-sub">This Round</div><div class="gm-big gm-green">'+fmt(entry.total)+"</div></div>";
if(prev){var d=entry.total-prev.total;h+='<div class="gm-scard"><div class="gm-sub">vs Round '+(state.round-1)+'</div><div class="gm-big">'+(d>=0?"+":"")+fmt(d)+"</div></div>"}
h+='<div class="gm-scard"><div class="gm-sub">Cumulative</div><div class="gm-big">'+fmt(state.cumRev)+"</div></div></div>";
if(isLast)h+='<div class="gm-actions"><button class="gm-btn-pri" id="gm-next">Finish Game &#8594;</button></div>';
else h+='<div class="gm-actions"><button class="gm-btn-pri" id="gm-next">Begin Round '+(state.round+1)+" &#8594;</button></div>";
root.innerHTML=h;
document.getElementById("gm-next").onclick=function(){
if(isLast){state.screen="done";render()}
else{state.round++;state.screen="alloc";TOWNS.forEach(function(t){state.allocs[t.id]=0});render()}
};
}

function renderDone(){
root.innerHTML='<div style="text-align:center;padding:30px"><div style="font-size:28px;font-weight:800;color:#16a34a">Game Complete!</div><div style="font-size:36px;font-weight:800;color:#16a34a;margin:16px 0">'+fmt(state.cumRev)+'</div><div style="font-size:14px;color:#6b7280;margin-bottom:16px">Total revenue across 8 rounds</div><div class="gm-sub">Your results have been saved. Click Next to continue.</div></div>';
try{if(nbObs)nbObs.disconnect();var nb=document.getElementById("NextButton");if(nb){nb.style.display="";nb.style.visibility="visible"}}catch(e){}
}

render();
})();
</script>
'''


def force_response(survey_id, question_id):
    """Set ForceResponse on a question by fetching it first to get its type."""
    q_data = api.get_question(survey_id, question_id)
    q_data["Validation"] = {"Settings": {"ForceResponse": "ON", "ForceResponseType": "ON", "Type": "None"}}
    api.update_question(survey_id, question_id, q_data)


# ── Main survey creation ─────────────────────────────────────────────────────

survey = api.create_survey("Green Market Game Pilot")
sid = survey["SurveyID"]
print(f"Created survey: {sid}")

try:
    # ── Embedded data ────────────────────────────────────────────────────────
    fields = {"difficulty": {"type": "text", "value": "medium"}}
    for r in range(1, 9):
        for town in ["harlan", "williamson", "burlington", "middlesex"]:
            fields[f"game_round_{r}_alloc_{town}"] = {"type": "text"}
            fields[f"game_round_{r}_rev_{town}"] = {"type": "text"}
        fields[f"game_round_{r}_total_rev"] = {"type": "text"}
        fields[f"game_round_{r}_pct_R"] = {"type": "text"}
    fields["game_cumulative_revenue"] = {"type": "text"}
    fields["game_pct_optimal"] = {"type": "text"}
    fields["game_total_pct_R"] = {"type": "text"}
    api.set_embedded_data_fields(sid, fields, position="start")
    print("Set embedded data fields")

    # ── Blocks ───────────────────────────────────────────────────────────────
    consent_block = api.create_block(sid, "Consent & Instructions")["BlockID"]
    beliefs_pre_block = api.create_block(sid, "Pre-Game Beliefs")["BlockID"]
    game_block = api.create_block(sid, "The Game")["BlockID"]
    beliefs_post_block = api.create_block(sid, "Post-Game Beliefs")["BlockID"]
    demographics_block = api.create_block(sid, "Demographics")["BlockID"]
    print("Created blocks")

    # ── Randomizer for difficulty ────────────────────────────────────────────
    api.add_randomizer(
        sid,
        elements=[
            {"difficulty": "easy"},
            {"difficulty": "medium"},
            {"difficulty": "hard"},
        ],
        subset=1,
        even_presentation=True,
        position=1,
    )
    print("Added difficulty randomizer")

    # ── Block 1: Consent ─────────────────────────────────────────────────────
    api.create_descriptive_text(sid, """
<p>In this study you'll play a short <strong>marketing strategy game</strong> (~10 min). By proceeding you consent to participate in this University of Pennsylvania research study. Responses are anonymous. You may withdraw at any time.</p>
""", block_id=consent_block)
    print("  Consent added")

    # ── Block 2: Pre-Game Beliefs ────────────────────────────────────────────
    # Create a single slider, then update to have two choices (Dem + Rep)
    DEM = '<span style="color:#2563eb;font-weight:700">Democrats</span>'
    REP = '<span style="color:#dc2626;font-weight:700">Republicans</span>'

    q = api.create_slider_question(
        sid,
        f"What <strong>%</strong> of each group would buy <strong>eco-friendly home products</strong>?",
        min_value=0, max_value=100, left_label="0%", right_label="100%",
        block_id=beliefs_pre_block,
    )
    q_data = api.get_question(sid, q["QuestionID"])
    q_data["Choices"] = {
        "1": {"Display": DEM},
        "2": {"Display": REP},
    }
    q_data["ChoiceOrder"] = [1, 2]
    api.update_question(sid, q["QuestionID"], q_data)
    force_response(sid, q["QuestionID"])

    q = api.create_slider_question(
        sid,
        f"If you had <strong>$100k</strong> to market eco-friendly products, what % would you spend in {REP}-leaning areas?",
        min_value=0, max_value=100,
        left_label="0%", right_label="100%",
        block_id=beliefs_pre_block,
    )
    force_response(sid, q["QuestionID"])
    print("  Pre-game beliefs added")

    # ── Block 3: The Game ────────────────────────────────────────────────────
    game_html = build_game_html()
    q_game = api.create_descriptive_text(sid, game_html, block_id=game_block)
    print(f"  Game question: {q_game['QuestionID']}")

    # ── Block 4: Post-Game Beliefs ───────────────────────────────────────────
    q = api.create_slider_question(
        sid,
        f"What <strong>%</strong> of each group would buy <strong>eco-friendly home products</strong>?",
        min_value=0, max_value=100, left_label="0%", right_label="100%",
        block_id=beliefs_post_block,
    )
    q_data = api.get_question(sid, q["QuestionID"])
    q_data["Choices"] = {
        "1": {"Display": DEM},
        "2": {"Display": REP},
    }
    q_data["ChoiceOrder"] = [1, 2]
    api.update_question(sid, q["QuestionID"], q_data)
    force_response(sid, q["QuestionID"])

    q = api.create_slider_question(
        sid,
        f"If you had <strong>$100k</strong> to market eco-friendly products, what % would you spend in {REP}-leaning areas?",
        min_value=0, max_value=100,
        left_label="0%", right_label="100%",
        block_id=beliefs_post_block,
    )
    force_response(sid, q["QuestionID"])

    q = api.create_text_entry_question(sid, "What <strong>strategy</strong> did you use when allocating your budget?", text_type="ML", block_id=beliefs_post_block)
    api.add_page_break(sid, q["QuestionID"])
    force_response(sid, q["QuestionID"])
    q = api.create_text_entry_question(sid, "What did you <strong>learn</strong> about the different markets?", text_type="ML", block_id=beliefs_post_block)
    force_response(sid, q["QuestionID"])

    # ── Game experience measures (for difficulty calibration) ─────────────
    api.add_page_break(sid, q["QuestionID"])
    experience_items = [
        ("The game was <strong>difficult</strong>.", "exp_difficult"),
        ("I found the game <strong>engaging</strong>.", "exp_engaging"),
        ("I felt <strong>frustrated</strong> while playing.", "exp_frustrated"),
        ("I could see how my decisions affected the results.", "exp_feedback_clear"),
        ("I felt like I was <strong>learning</strong> as I played.", "exp_learning"),
        ("The game felt <strong>too long</strong>.", "exp_too_long"),
    ]
    likert_choices = [
        "Strongly disagree", "Disagree", "Somewhat disagree",
        "Neither agree nor disagree",
        "Somewhat agree", "Agree", "Strongly agree",
    ]
    for item_text, item_tag in experience_items:
        q = api.create_multiple_choice_question(
            sid, item_text, choices=likert_choices,
            block_id=beliefs_post_block,
        )
        force_response(sid, q["QuestionID"])
        # Tag with recode values for clean export
        q_data = api.get_question(sid, q["QuestionID"])
        q_data["DataExportTag"] = item_tag
        api.update_question(sid, q["QuestionID"], q_data)

    print("  Post-game beliefs + experience measures added")

    # ── Block 5: Demographics ────────────────────────────────────────────────
    q = api.create_text_entry_question(sid, "What is your age?", text_type="SL", block_id=demographics_block)
    force_response(sid, q["QuestionID"])

    for text, choices in [
        ("What is your gender?", ["Male", "Female", "Non-binary", "Prefer not to say"]),
        ("Which best describes your political affiliation?", ["Strong Democrat", "Lean Democrat", "Independent", "Lean Republican", "Strong Republican"]),
        ("What is the highest level of education you have completed?", ["High school or less", "Some college", "Bachelor's degree", "Graduate degree"]),
    ]:
        q = api.create_multiple_choice_question(sid, text, choices=choices, block_id=demographics_block)
        force_response(sid, q["QuestionID"])
    print("  Demographics added")

    # ── Print URL ────────────────────────────────────────────────────────────
    url = api.get_survey_url(sid)
    print(f"\n{'='*60}")
    print(f"Survey ID: {sid}")
    print(f"Preview URL: {url}")
    print(f"{'='*60}")

except Exception as e:
    print(f"\nERROR: {e}")
    print(f"Survey {sid} was partially created.")
    import traceback
    traceback.print_exc()
