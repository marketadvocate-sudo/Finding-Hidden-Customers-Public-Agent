#!/usr/bin/env python3
"""
Cannonball GTM - Finding Hidden Customers Agent v0.5
pip3 install anthropic flask
export ANTHROPIC_API_KEY="your-key" && python3 cannonball.py
"""
import os, sys, json, uuid
try:
    import anthropic
    from flask import Flask, request, jsonify, Response
except ImportError:
    print("Run: pip3 install anthropic flask")
    sys.exit(1)
if not os.environ.get("ANTHROPIC_API_KEY"):
    print("Set: export ANTHROPIC_API_KEY='your-key'")
    sys.exit(1)

app = Flask(__name__)
client = anthropic.Anthropic()
sessions = {}

PROMPTS = {
    "lookup": "Given a brand name or URL, provide a 2-3 sentence summary of what the company does and who they sell to. Plain text only.",

    "stage0": "You are the Finding Hidden Customers Agent by Cannonball GTM. Produce ONLY a Stage 0 Brand Profile. Search the web.\n\nOutput in markdown:\n## Brand Profile\n**Company:** [name]\n**Product:** [1-2 sentences]\n**Who buys it:** [buyer titles and company types]\n**Lead vertical:** [primary vertical]\n**Company stage:** [startup/growth/mature, funding]\n**Estimated Annual Contract Value (ACV):** [pricing estimate]\n**Differentiator:** [1 sentence]\n\nEnd with: Review this profile. If anything is off, share corrections below before continuing.\nKeep it SHORT.",

    "stage1": "You are the Finding Hidden Customers Agent. Confirmed brand profile is in history. Produce ONLY Stage 1: Industry Analysis and Data Sources.\n\nBefore findings write: We mapped the regulatory environment and identified public databases that could reveal target companies. These government-maintained records are how we find buyers most sales teams never look for.\n\nResearch: 1) Regulatory environment 2) Industry pressures 3) Public data sources. Always check: OSHA IMIS, CISA KEV, SAM.gov, EPA ECHO, CMS, FTC, state boards, NVD, demographic data, bond records, permits.\n\nCRITICAL: For EACH data source, include a one-line explanation of WHAT IT IS before describing what it contains. Example: 'CMS Provider of Services File — a federal database maintained by the Centers for Medicare and Medicaid Services listing every Medicare-certified healthcare facility in the United States. Contains: facility name, address, type, certification status. Searchable by name and location. Free. Updated quarterly.'\n\nDo NOT assume the reader knows what OSHA IMIS or CISA KEV or MSRB EMMA means. Spell out every acronym the first time: OSHA (Occupational Safety and Health Administration), CISA KEV (Cybersecurity and Infrastructure Security Agency Known Exploited Vulnerabilities catalog), etc.\n\nONLY Stage 1.",

    "stage2": "You are the Finding Hidden Customers Agent. Profile and context in history. Produce ONLY Stage 2: Pain Segments.\n\nBefore findings: We identified groups of companies based on their position relative to a systemic pain condition — not by size or industry, but by what is happening to them right now.\n\nGOLD FIRST. Use headers: ## GOLD SEGMENT: [Name] (Recommended) then ## SILVER SEGMENT: [Name] then ## BRONZE SEGMENT: [Name]\n\nFor EACH: memorable name, pain from buyer perspective, systemic condition driving it (embedded not separate), buying motivation, estimated segment size with rationale, viability scores (Urgency/Observability/Value Prop Fit/Buyer Resonance/Market Density each 1-5 with rationale), projected meetings using Meeting Book Rate, actionability.\n\nMEETING PROJECTION MATH (use this exact framework):\nShow three tiers:\n- SPAM/TAM rate (traditional targeting): segment size x 4 contacts x 0.00025 = X meetings. This is what most outbound produces.\n- Pain segment floor (Cannonball methodology): segment size x 4 contacts x 0.01 = Y meetings. This is the baseline for a validated pain segment.\n- PVP messaging (optimized): segment size x 4 contacts x 0.04 = Z meetings. This is achievable with strong Permissionless Value Propositions.\nThe progression from X to Y to Z IS the methodology's value.\n\nSpell out all acronyms on first use: Annual Contract Value (ACV), Meeting Book Rate (MBR), Existential Data Point (EDP).\n\nFor GOLD: This segment represents hidden customers — companies experiencing systemic pain visible through public compliance data but invisible to competitors using traditional targeting.\n\nACV floors: under $50K ACV = 1,000 companies minimum. $50K-$250K = 500. $250K+ = 250.\nONLY Stage 2.",

    "stage3": "You are the Finding Hidden Customers Agent. All prior stages in history. Produce ONLY Stage 3: Verdict, Data Availability, Execution Roadmap.\n\n## Verdict\n\nFirst, provide a one-line calibration: 'Strong Fit means the methodology found actionable public data, systemic pain conditions, and a segment large enough to sustain a campaign. What follows is the specific evidence.'\n\nState: Strong Fit / Viable but Needs Expert Guidance / Not the Right Approach.\n\nCRITICAL: Explain WHY with three specific data-grounded reasons tied to evidence from the analysis.\n\nFor NOT RECOMMENDED: equal specificity, acknowledge what IS valid, suggest alternatives.\n\n## Data Availability\nFor EACH data source mentioned, clearly state WHICH SEGMENT it supports. Example: 'CMS Quality Payment Program data (supports GOLD segment: Medicare Advantage Payment Disruption) — provides practice-level MIPS scores...'\n\nDo NOT list data sources without connecting them to a specific segment. The reader must be able to trace: this data source serves this segment for this reason.\n\n## Execution Roadmap\n### For the GTM Engineer:\nStep-by-step recipe: specific databases to query, exact filters, how to cross-reference sources for compound signals, contact titles to enrich, how to load for an email campaign. This is the RECIPE — not the list itself.\n### For the Sales/Marketing Leader:\nReview target list quality. Develop messaging using the pain language identified in the segment analysis. Establish a Meeting Book Rate (MBR) baseline before campaign launch. Set up measurement framework.\n\n## Projected Meetings\nShow the three-tier progression for the GOLD segment:\n- Traditional targeting (SPAM/TAM rate, 0.01-0.025%): segment size x 4 contacts x 0.00025 = X meetings. This is what most outbound produces today.\n- Pain segment floor (1% MBR): segment size x 4 contacts x 0.01 = Y meetings. This is the baseline when targeting a validated pain segment.\n- PVP-quality messaging (4% MBR): segment size x 4 contacts x 0.04 = Z meetings. This is achievable with strong Permissionless Value Propositions.\n\nThe Meeting Book Rate (MBR) is the percentage of outreach activities that produce a booked meeting. The jump from SPAM rates to pain segment rates IS the methodology's value. Meeting rates improve further as messaging quality increases.\n\n## Confidence\nLevel, what would increase it, what would decrease it.\n\nSpell out ALL acronyms. No channels beyond email. No list generation. No tool sequencing.",

    "revise": "You are the Finding Hidden Customers Agent. Operator has feedback on current stage. Regenerate the ENTIRE stage incorporating feedback. If input is a question, answer it AND regenerate with insights incorporated. One unified output. Spell out all acronyms.",

    "gtm_recipe": "You are the Finding Hidden Customers Agent. The full analysis is in the conversation history. The operator wants a standalone GTM Engineer Recipe for the GOLD segment.\n\nProduce a CLEAR, STEP-BY-STEP recipe that a GTM engineer can follow to build the target list. Format it as a numbered checklist:\n\n## GTM Engineer Recipe: [Gold Segment Name]\n\n### Step 1: Build the Base List\n[Specific database, URL if possible, exact search/filter criteria]\n\n### Step 2: Apply Pain Filter\n[Which data source to cross-reference, what to look for, how to match records]\n\n### Step 3: Compound Signal (if applicable)\n[Additional data source to layer, how it strengthens targeting]\n\n### Step 4: Enrich Contacts\n[Specific titles to target, why these titles, recommended enrichment approach]\n\n### Step 5: Load for Campaign\n[How to structure the list for email outbound, any segmentation within the list]\n\n### Expected Output\nEstimated list size: [number]\nMeeting projections at three tiers:\n- Traditional outbound (0.01-0.025% Meeting Book Rate): [X] meetings\n- Pain segment floor (1% MBR): [Y] meetings\n- PVP-quality messaging (4% MBR): [Z] meetings\n\nBe specific enough that someone who was NOT in this conversation could follow the recipe and build the list. Name actual databases and actual filters."
}

def call_api(system, messages, max_tokens=4000, tools=True):
    kwargs = dict(model="claude-sonnet-4-6", max_tokens=max_tokens, system=system, messages=messages)
    if tools:
        kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
    resp = client.messages.create(**kwargs)
    return "".join(b.text for b in resp.content if b.type == "text")

@app.route('/')
def index():
    return HTML_PAGE

@app.route('/app.js')
def serve_js():
    return Response(JS_CODE, mimetype='application/javascript')


@app.route('/api/auth', methods=['POST'])
def auth():
    pw = request.json.get('password', '').strip()
    correct = os.environ.get('CANNONBALL_PASSWORD', 'cannonball2026')
    if pw == correct:
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Incorrect password."})

@app.route('/api/lookup', methods=['POST'])
def lookup():
    brand = request.json.get('brand', '').strip()
    if not brand: return jsonify({"error": "No brand"})
    try:
        return jsonify({"summary": call_api(PROMPTS["lookup"], [{"role": "user", "content": "Look up: " + brand}], 400)})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/stage', methods=['POST'])
def run_stage():
    data = request.json
    sid = data.get('session_id', '')
    stage = data.get('stage', 0)
    context = data.get('context', '')
    if stage == 0:
        sid = str(uuid.uuid4())
        sessions[sid] = {"messages": [], "stages": {}}
        sessions[sid]["messages"].append({"role": "user", "content": context})
        try:
            text = call_api(PROMPTS["stage0"], sessions[sid]["messages"], 1500)
            sessions[sid]["messages"].append({"role": "assistant", "content": text})
            sessions[sid]["stages"][0] = text
            return jsonify({"output": text, "session_id": sid})
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        if not sid or sid not in sessions: return jsonify({"error": "Session not found."})
        s = sessions[sid]
        pkeys = {1: "stage1", 2: "stage2", 3: "stage3"}
        s["messages"].append({"role": "user", "content": "Continue to Stage " + str(stage) + "."})
        try:
            text = call_api(PROMPTS[pkeys[stage]], s["messages"], 8000 if stage >= 2 else 5000)
            s["messages"].append({"role": "assistant", "content": text})
            s["stages"][stage] = text
            return jsonify({"output": text, "session_id": sid})
        except Exception as e:
            return jsonify({"error": str(e)})

@app.route('/api/revise', methods=['POST'])
def revise():
    data = request.json
    sid, stage, feedback = data.get('session_id',''), data.get('stage',0), data.get('feedback','').strip()
    if not sid or sid not in sessions: return jsonify({"error": "Session not found."})
    if not feedback: return jsonify({"error": "No feedback."})
    s = sessions[sid]
    s["messages"].append({"role": "user", "content": "Feedback on Stage " + str(stage) + ": " + feedback + "\n\nRegenerate complete Stage " + str(stage) + " incorporating this."})
    try:
        text = call_api(PROMPTS["revise"], s["messages"], 8000 if stage >= 2 else 5000)
        s["messages"].append({"role": "assistant", "content": text})
        s["stages"][stage] = text
        return jsonify({"output": text, "session_id": sid})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/gtm_recipe', methods=['POST'])
def gtm_recipe():
    sid = request.json.get('session_id', '')
    if not sid or sid not in sessions: return jsonify({"error": "Session not found."})
    s = sessions[sid]
    s["messages"].append({"role": "user", "content": "Generate the standalone GTM Engineer Recipe for the gold segment."})
    try:
        text = call_api(PROMPTS["gtm_recipe"], s["messages"], 4000)
        s["messages"].append({"role": "assistant", "content": text})
        return jsonify({"recipe": text})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/report', methods=['POST'])
def gen_report():
    sid = request.json.get('session_id', '')
    if not sid or sid not in sessions: return jsonify({"error": "Session not found."})
    stages = sessions[sid].get("stages", {})
    combined = ""
    for i in sorted(stages.keys()):
        combined += "\n\n---\n\n" + stages.get(i, "")
    return jsonify({"markdown": combined})

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cannonball GTM - Finding Hidden Customers</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&family=Inconsolata:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{--cream:#F5F3ED;--ink:#2D2D20;--orange:#FF4F00;--dim:rgba(45,45,32,0.55);--rule:rgba(45,45,32,0.15);--green:#2a7d3f;--red:#a0392d;--gold:#b8860b;--silver:#6b7280;--bronze:#92400e}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--cream);color:var(--ink);font-family:'Montserrat',system-ui,sans-serif;min-height:100vh;font-size:17px}
.wrap{max-width:900px;margin:0 auto;padding:24px 28px;padding-bottom:180px}
.mono{font-family:'Inconsolata',monospace}
.hdr{border-bottom:4px solid var(--ink);padding:14px 0;display:flex;justify-content:space-between;align-items:center;margin-bottom:32px}
.kick{display:inline-block;background:var(--orange);color:var(--cream);font-weight:700;font-size:12px;letter-spacing:0.14em;text-transform:uppercase;padding:4px 12px 5px;margin-bottom:14px;box-shadow:3px 3px 0 var(--ink)}
h1{font-weight:900;font-size:34px;line-height:1.05;margin:10px 0 8px;text-transform:uppercase}
h1 .o{color:var(--orange)}
.sub{font-size:16px;color:var(--dim);max-width:580px;line-height:1.55;margin-bottom:28px}
input[type="text"],textarea{width:100%;padding:13px 16px;border:2px solid var(--ink);background:white;font-family:'Inconsolata',monospace;font-size:16px;outline:none;color:var(--ink)}
textarea{resize:vertical;min-height:70px}
.btn{padding:13px 24px;border:2px solid var(--ink);font-family:'Inconsolata',monospace;font-weight:700;font-size:13px;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer}
.btn-o{background:var(--orange);color:var(--cream);box-shadow:4px 4px 0 var(--ink)}
.btn-d{background:var(--ink);color:var(--cream)}
.btn-s{background:transparent;color:var(--dim);border-color:var(--rule)}
.btn-g{background:var(--green);color:white;box-shadow:4px 4px 0 var(--ink)}
.lbl{font-family:'Inconsolata',monospace;font-size:13px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--dim);display:block;margin-bottom:8px}
.hint{font-size:14px;color:rgba(45,45,32,0.4);margin-top:5px}
.fg{margin-bottom:18px}
.card{border:2px solid var(--ink);padding:24px 28px;background:white;margin-bottom:18px;box-shadow:6px 6px 0 rgba(45,45,32,0.1)}
.card h3{font-weight:800;font-size:19px;text-transform:uppercase;margin-bottom:8px}
.card p{font-size:16px;line-height:1.55;color:rgba(45,45,32,0.65)}
.step{display:none}.step.active{display:block}
.pbar{display:flex;gap:3px;flex-wrap:wrap;margin-bottom:8px}
.ps{display:flex;align-items:center;gap:5px;padding:7px 12px;font-family:'Inconsolata',monospace;font-size:12px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;transition:all 0.2s}
.ps.done{background:var(--ink);color:var(--cream);cursor:pointer}.ps.done:hover{background:var(--orange)}
.ps.cur{background:var(--orange);color:var(--cream)}.ps.off{background:rgba(45,45,32,0.07);color:rgba(45,45,32,0.3)}
.pct{height:10px;background:rgba(45,45,32,0.1);margin-bottom:5px;border-radius:5px;overflow:hidden}
.pct-f{height:100%;background:var(--orange);transition:width 0.5s}
.pct-l{font-family:'Inconsolata',monospace;font-size:14px;color:var(--dim);margin-bottom:18px}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
.dot{width:7px;height:7px;border-radius:50%;background:var(--orange);display:inline-block;animation:pulse 1s infinite;margin-left:4px}
.sblk{border:2px solid var(--ink);background:white;padding:28px 32px;margin-bottom:18px;box-shadow:4px 4px 0 rgba(45,45,32,0.08);font-size:17px;line-height:1.75;position:relative}
.sblk .stag{font-family:'Inconsolata',monospace;font-size:13px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--orange);margin-bottom:14px}
.sblk h1{font-size:24px;margin:24px 0 12px;text-transform:uppercase}
.sblk h2{font-size:21px;margin:28px 0 12px;border-top:2px solid var(--ink);padding-top:14px;color:var(--orange)}
.sblk h3{font-size:18px;margin:20px 0 10px}
.sblk p{margin-bottom:12px}.sblk ul{margin:10px 0 14px 24px}.sblk li{margin-bottom:6px}
.sblk strong{font-weight:700}
.sblk .gold-seg{border-left:5px solid var(--gold);padding:14px 18px;margin:18px 0;background:rgba(184,134,11,0.05)}
.sblk .silver-seg{border-left:5px solid var(--silver);padding:14px 18px;margin:18px 0;background:rgba(107,114,128,0.05)}
.sblk .bronze-seg{border-left:5px solid var(--bronze);padding:14px 18px;margin:18px 0;background:rgba(146,64,14,0.05)}
.copy-b{position:absolute;top:10px;right:10px;padding:5px 12px;background:rgba(45,45,32,0.06);border:1px solid var(--rule);font-family:'Inconsolata',monospace;font-size:11px;cursor:pointer;text-transform:uppercase;color:var(--dim)}
.copy-b:hover{background:var(--orange);color:white;border-color:var(--orange)}
.recipe-block{border:3px solid var(--green);background:white;padding:28px 32px;margin:18px 0;box-shadow:6px 6px 0 var(--green);font-size:17px;line-height:1.75;position:relative}
.recipe-block .rtag{font-family:'Inconsolata',monospace;font-size:13px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--green);margin-bottom:14px}
.recipe-block h2{font-size:21px;margin:24px 0 12px;color:var(--green)}
.recipe-block h3{font-size:18px;margin:18px 0 10px}
.recipe-block p{margin-bottom:12px}.recipe-block ul{margin:10px 0 14px 24px}.recipe-block li{margin-bottom:6px}
.recipe-block strong{font-weight:700}
.err{border:2px solid var(--red);background:rgba(160,57,45,0.06);padding:14px 18px;font-family:'Inconsolata',monospace;font-size:15px;color:var(--red);margin-bottom:18px}
.actions{display:flex;gap:12px;margin-bottom:22px;flex-wrap:wrap}
.dlg{position:fixed;bottom:0;left:0;right:0;background:var(--cream);border-top:3px solid var(--ink);padding:14px 28px 18px;z-index:100;display:none}
.dlg .inner{max-width:900px;margin:0 auto}
.dlg .row{display:flex;gap:10px;align-items:flex-end}
.dlg .row textarea{min-height:44px;font-size:15px}
.dlg .ctx{font-family:'Inconsolata',monospace;font-size:13px;color:var(--dim);margin-bottom:6px}
.dlg .sts{font-family:'Inconsolata',monospace;font-size:13px;color:var(--orange);font-style:italic;margin-bottom:6px;display:none}
.footer{border-top:4px solid var(--ink);padding-top:16px;margin-top:36px;display:flex;justify-content:space-between;font-family:'Inconsolata',monospace;font-size:12px}
</style>
</head>
<body>
<div class="wrap">
  <div class="hdr"><span class="mono" style="font-weight:700;font-size:13px;letter-spacing:0.18em;text-transform:uppercase;">Cannonball GTM</span><span class="mono" style="font-size:12px;letter-spacing:0.08em;text-transform:uppercase;color:var(--dim);">Finding Hidden Customers</span></div>
    <div id="s-auth" class="step active">
    <div class="kick mono">Finding Hidden Customers Agent</div>
    <h1>Welcome to <span class="o">Cannonball.</span></h1>
    <p class="sub">This agent is available to Cannonball GTM subscribers. Enter your access code to continue.</p>
    <div class="fg"><label class="lbl">Access Code</label><div style="display:flex;gap:10px;"><input type="password" id="f-pw" placeholder="Enter your access code" style="width:100%;padding:13px 16px;border:2px solid var(--ink);background:white;font-family:Inconsolata,monospace;font-size:16px;outline:none;"><button class="btn btn-o" id="b-auth">Enter</button></div></div>
    <div id="auth-err" class="mono" style="font-size:14px;color:var(--red);display:none;margin-top:8px;"></div>
  </div>
  <div id="s-welcome" class="step">
    <div class="kick mono">Finding Hidden Customers Agent</div>
    <h1>Find the buyers your competitors <span class="o">can't see.</span></h1>
    <p class="sub">This agent identifies pain segments from public compliance data. You guide the analysis stage by stage, correcting and refining as you go.</p>
    <p class="sub" style="font-size:15px;"><strong>How it works:</strong> Enter a brand. Review the profile. Provide context. Walk through each stage with feedback at every step.</p>
    <div class="fg"><label class="lbl">What brand do you want to investigate?</label><div style="display:flex;gap:10px;"><input type="text" id="f-brand" placeholder="Brand name or URL (URL works best)"><button class="btn btn-d" id="b-go">Let's Go</button></div></div>
    <div id="w-st" class="mono" style="font-size:14px;color:var(--dim);font-style:italic;display:none;"></div>
  </div>
  <div id="s-confirm" class="step"><div class="card"><div class="lbl" style="margin-bottom:10px;">Is this the right brand?</div><p id="brand-sum" style="font-size:17px;line-height:1.6;margin-bottom:16px;color:var(--ink);"></p><div style="display:flex;gap:12px;"><button class="btn btn-o" id="b-yes">Yes, continue</button><button class="btn btn-s" id="b-no">No, try again</button></div></div></div>
  <div id="s-intake" class="step"><div class="card"><h3>Help Us Target the Analysis</h3><p style="margin-bottom:20px;">The more context you share, the better. Leave blank anything you are unsure about.</p><div class="fg"><label class="lbl">What are you hoping the Cannonball will uncover?</label><textarea id="f-goal" rows="3" placeholder="e.g., We need mid-market buyers struggling with compliance."></textarea><div class="hint">Start big. What is the challenge?</div></div><div class="fg"><label class="lbl">Anything the agent should know that is NOT on the website?</label><textarea id="f-ctx" rows="2" placeholder="e.g., Real play is B2B enterprise."></textarea></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;"><div class="fg"><label class="lbl">Estimated deal size</label><input type="text" id="f-acv" placeholder="e.g., $50,000"></div><div class="fg"><label class="lbl">Sales cycle</label><input type="text" id="f-cyc" placeholder="e.g., 3-6 months"></div></div><div style="display:flex;gap:12px;"><button class="btn btn-s" id="b-back">Back</button><button class="btn btn-o" style="flex:1;" id="b-analyze">Start Analysis</button></div></div></div>
  <div id="s-analysis" class="step"><div class="pbar" id="pbar"></div><div class="pct"><div class="pct-f" id="pctf" style="width:0%;"></div></div><div class="pct-l" id="pctl"></div><div id="stages-box"></div><div id="recipe-box"></div><div id="mid-actions" style="display:none;"><div class="actions"><button class="btn btn-o" id="b-next" style="flex:1;">Continue to Next Stage</button><button class="btn btn-s" id="b-restart">Start Over</button></div></div><div id="end-actions" style="display:none;"><div class="actions"><button class="btn btn-g" id="b-gtm">Generate GTM Engineer Recipe</button><button class="btn btn-g" id="b-report">Generate Shareable Report</button><button class="btn btn-d" id="b-msg" style="opacity:0.5;">Move to Messaging (Coming Soon)</button><button class="btn btn-s" id="b-new">Run Another Brand</button></div></div></div>
  <div id="s-error" class="step"><div class="err" id="err"></div><button class="btn btn-s" id="b-retry">Start Over</button></div>
  <div class="footer"><span style="font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">Cannonball GTM</span><span style="color:var(--dim);">Finding Hidden Customers Agent v0.5 Beta</span></div>
</div>
<div class="dlg" id="dlg"><div class="inner"><div class="ctx" id="dlg-ctx">Stage 0: Brand Profile</div><div class="sts" id="dlg-sts">Regenerating...</div><div class="row"><textarea id="f-dlg" rows="2" placeholder="Feedback, corrections, or questions. The stage above will regenerate with your input..."></textarea><button class="btn btn-o" id="b-send" style="padding:13px 20px;white-space:nowrap;">Send</button></div></div></div>
<script src="/app.js"></script>
</body>
</html>"""

JS_CODE = r"""
var brand='',sid='',curStage=-1,maxStage=3;
var SNAMES=['Brand Profile','Industry Analysis','Pain Segments','Verdict + Roadmap'];
var SMSG=[
['Searching for brand...','Reading website...','Building profile...'],
['Mapping regulatory environment...','Searching databases...','Cataloging data sources...'],
['Analyzing pain signals...','Identifying segments...','Scoring viability...','Ranking gold, silver, bronze...'],
['Checking data availability...','Building execution roadmap...','Determining verdict...']
];
function show(id){var s=document.querySelectorAll('.step');for(var i=0;i<s.length;i++)s[i].classList.remove('active');document.getElementById(id).classList.add('active');}
function showDlg(){document.getElementById('dlg').style.display='block';}
function hideDlg(){document.getElementById('dlg').style.display='none';}
function reset(){brand='';sid='';curStage=-1;['f-brand','f-goal','f-ctx','f-acv','f-cyc','f-dlg'].forEach(function(id){document.getElementById(id).value='';});document.getElementById('stages-box').innerHTML='';document.getElementById('recipe-box').innerHTML='';hideDlg();show('s-welcome');}
function updatePbar(active){var el=document.getElementById('pbar');var h='';for(var i=0;i<SNAMES.length;i++){var c=i<active?'done':i===active?'cur':'off';var d=i===active?' <span class="dot"></span>':'';h+='<div class="ps '+c+'" data-stage="'+i+'">'+SNAMES[i]+d+'</div>';}el.innerHTML=h;var chips=el.querySelectorAll('.ps.done');for(var j=0;j<chips.length;j++){chips[j].addEventListener('click',function(){var t=document.getElementById('stage-'+this.getAttribute('data-stage'));if(t)t.scrollIntoView({behavior:'smooth',block:'start'});});}document.getElementById('pctf').style.width=Math.round(((active+1)/(SNAMES.length+0.5))*100)+'%';}
function applyBold(t){var r='',i=0;while(i<t.length){if(t[i]==='*'&&i+1<t.length&&t[i+1]==='*'){var e=t.indexOf('**',i+2);if(e>-1){r+='<strong>'+t.substring(i+2,e)+'</strong>';i=e+2;}else{r+=t[i];i++;}}else{r+=t[i];i++;}}return r;}
function md(text){if(!text)return'';var lines=text.split('\n'),html='',inList=false,seg='';for(var i=0;i<lines.length;i++){var L=lines[i],lo=L.toLowerCase();if(lo.indexOf('gold segment')>-1&&L.indexOf('#')===0){if(inList){html+='</ul>';inList=false;}if(seg)html+='</div>';seg='gold';html+='<div class="gold-seg"><h2>'+applyBold(L.replace(/^#+\s*/,''))+'</h2>';continue;}if(lo.indexOf('silver segment')>-1&&L.indexOf('#')===0){if(inList){html+='</ul>';inList=false;}if(seg)html+='</div>';seg='silver';html+='<div class="silver-seg"><h2>'+applyBold(L.replace(/^#+\s*/,''))+'</h2>';continue;}if(lo.indexOf('bronze segment')>-1&&L.indexOf('#')===0){if(inList){html+='</ul>';inList=false;}if(seg)html+='</div>';seg='bronze';html+='<div class="bronze-seg"><h2>'+applyBold(L.replace(/^#+\s*/,''))+'</h2>';continue;}if(seg&&L.indexOf('## ')===0&&lo.indexOf('segment')===-1){html+='</div>';seg='';}if(L.indexOf('### ')===0){if(inList){html+='</ul>';inList=false;}html+='<h3>'+applyBold(L.substring(4))+'</h3>';}else if(L.indexOf('## ')===0){if(inList){html+='</ul>';inList=false;}html+='<h2>'+applyBold(L.substring(3))+'</h2>';}else if(L.indexOf('# ')===0){if(inList){html+='</ul>';inList=false;}html+='<h1>'+applyBold(L.substring(2))+'</h1>';}else if(L.indexOf('- ')===0){if(!inList){html+='<ul>';inList=true;}html+='<li>'+applyBold(L.substring(2))+'</li>';}else if(L.indexOf('|')===0){if(L.indexOf('---')>-1)continue;var cells=L.split('|'),f=[];for(var c=0;c<cells.length;c++)if(cells[c].trim()!=='')f.push(cells[c].trim());if(f.length>0){html+='<div style="display:grid;grid-template-columns:repeat('+f.length+',1fr);gap:10px;padding:8px 0;border-bottom:1px solid rgba(45,45,32,0.1);font-size:15px;">';for(var j=0;j<f.length;j++)html+='<div>'+applyBold(f[j])+'</div>';html+='</div>';}}else if(L.trim()===''){if(inList){html+='</ul>';inList=false;}}else{if(inList){html+='</ul>';inList=false;}html+='<p>'+applyBold(L)+'</p>';}}if(inList)html+='</ul>';if(seg)html+='</div>';return html;}
function setStageBlock(stage,content){var box=document.getElementById('stages-box');var existing=document.getElementById('stage-'+stage);if(existing){existing.querySelector('.si').innerHTML=md(content);return;}var div=document.createElement('div');div.className='sblk';div.id='stage-'+stage;var tag=document.createElement('div');tag.className='stag';tag.textContent='Stage '+stage+': '+SNAMES[stage];div.appendChild(tag);var inner=document.createElement('div');inner.className='si';inner.innerHTML=md(content);div.appendChild(inner);var cb=document.createElement('button');cb.className='copy-b';cb.textContent='Copy';cb.addEventListener('click',function(){navigator.clipboard.writeText(inner.innerText);cb.textContent='Copied!';setTimeout(function(){cb.textContent='Copy';},2000);});div.appendChild(cb);box.appendChild(div);div.scrollIntoView({behavior:'smooth',block:'start'});}
function showActions(){document.getElementById('mid-actions').style.display=curStage<maxStage?'block':'none';document.getElementById('end-actions').style.display=curStage>=maxStage?'block':'none';if(curStage<maxStage)document.getElementById('b-next').textContent='Continue to '+SNAMES[curStage+1];}
function runStage(stage){curStage=stage;updatePbar(stage);document.getElementById('mid-actions').style.display='none';document.getElementById('end-actions').style.display='none';var msgs=SMSG[stage];document.getElementById('pctl').textContent=msgs[0];var mi=0,ti=setInterval(function(){mi++;if(mi<msgs.length)document.getElementById('pctl').textContent=msgs[mi];},5000);var body={session_id:sid,stage:stage};if(stage===0){var parts=['Brand: '+brand];var g=document.getElementById('f-goal').value;if(g)parts.push('Goal: '+g);var cx=document.getElementById('f-ctx').value;if(cx)parts.push('Context: '+cx);var av=document.getElementById('f-acv').value;if(av)parts.push('ACV: '+av);var cy=document.getElementById('f-cyc').value;if(cy)parts.push('Cycle: '+cy);body.context=parts.join('\n');}fetch('/api/stage',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(function(r){return r.json();}).then(function(d){clearInterval(ti);if(d.error){document.getElementById('err').textContent=d.error;show('s-error');return;}if(d.session_id)sid=d.session_id;setStageBlock(stage,d.output);updatePbar(stage);document.getElementById('pctf').style.width=Math.round(((stage+1)/SNAMES.length)*100)+'%';document.getElementById('pctl').textContent=SNAMES[stage]+' complete.';document.getElementById('dlg-ctx').textContent='Stage '+stage+': '+SNAMES[stage];showDlg();showActions();}).catch(function(e){clearInterval(ti);document.getElementById('err').textContent=e.message;show('s-error');});}
function sendFeedback(){var fb=document.getElementById('f-dlg').value.trim();if(!fb||curStage<0)return;var sts=document.getElementById('dlg-sts');sts.style.display='block';sts.textContent='Regenerating Stage '+curStage+'...';document.getElementById('f-dlg').value='';fetch('/api/revise',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sid,stage:curStage,feedback:fb})}).then(function(r){return r.json();}).then(function(d){sts.style.display='none';if(d.error){alert('Error: '+d.error);return;}setStageBlock(curStage,d.output);}).catch(function(e){sts.style.display='none';alert('Error: '+e.message);});}
function generateRecipe(){var btn=document.getElementById('b-gtm');btn.textContent='Generating recipe...';btn.style.opacity='0.5';btn.style.pointerEvents='none';fetch('/api/gtm_recipe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sid})}).then(function(r){return r.json();}).then(function(d){btn.textContent='Generate GTM Engineer Recipe';btn.style.opacity='1';btn.style.pointerEvents='auto';if(d.error){alert(d.error);return;}var box=document.getElementById('recipe-box');box.innerHTML='';var div=document.createElement('div');div.className='recipe-block';var tag=document.createElement('div');tag.className='rtag';tag.textContent='GTM Engineer Recipe';div.appendChild(tag);var inner=document.createElement('div');inner.innerHTML=md(d.recipe);div.appendChild(inner);var cb=document.createElement('button');cb.className='copy-b';cb.textContent='Copy Recipe';cb.addEventListener('click',function(){navigator.clipboard.writeText(inner.innerText);cb.textContent='Copied!';setTimeout(function(){cb.textContent='Copy Recipe';},2000);});div.appendChild(cb);box.appendChild(div);div.scrollIntoView({behavior:'smooth',block:'start'});}).catch(function(e){btn.textContent='Generate GTM Engineer Recipe';btn.style.opacity='1';btn.style.pointerEvents='auto';alert('Error: '+e.message);});}
function generateReport(){fetch('/api/report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sid})}).then(function(r){return r.json();}).then(function(d){if(d.error){alert(d.error);return;}var h='<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Finding Hidden Customers Report</title><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&family=Inconsolata:wght@400;600;700&display=swap" rel="stylesheet"><style>body{background:#F5F3ED;color:#2D2D20;font-family:Montserrat,system-ui,sans-serif;max-width:860px;margin:0 auto;padding:32px 28px;font-size:17px;line-height:1.75}h1{font-size:24px;margin:28px 0 12px;text-transform:uppercase;font-weight:900}h2{font-size:21px;margin:28px 0 12px;border-top:2px solid #2D2D20;padding-top:14px;color:#FF4F00;font-weight:800}h3{font-size:18px;margin:20px 0 10px;font-weight:700}p{margin-bottom:12px}ul{margin:10px 0 14px 24px}li{margin-bottom:6px}strong{font-weight:700}.gold-seg{border-left:5px solid #b8860b;padding:14px 18px;margin:18px 0;background:rgba(184,134,11,0.05)}.silver-seg{border-left:5px solid #6b7280;padding:14px 18px;margin:18px 0;background:rgba(107,114,128,0.05)}.bronze-seg{border-left:5px solid #92400e;padding:14px 18px;margin:18px 0;background:rgba(146,64,14,0.05)}.hdr{border-bottom:4px solid #2D2D20;padding:14px 0;display:flex;justify-content:space-between;margin-bottom:28px;font-family:Inconsolata,monospace;font-size:13px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase}.ftr{border-top:4px solid #2D2D20;padding-top:14px;margin-top:36px;display:flex;justify-content:space-between;font-family:Inconsolata,monospace;font-size:12px}</style></head><body><div class="hdr"><span>Cannonball GTM</span><span>Finding Hidden Customers</span></div>'+md(d.markdown)+'<div class="ftr"><span style="font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">Cannonball GTM</span><span style="color:rgba(45,45,32,0.5);">Finding Hidden Customers Agent v0.5 Beta</span></div></body></html>';var w=window.open('','_blank');w.document.write(h);w.document.close();}).catch(function(e){alert('Error: '+e.message);});}
document.getElementById('b-auth').addEventListener('click',function(){var pw=document.getElementById('f-pw').value;fetch('/api/auth',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw})}).then(function(r){return r.json();}).then(function(d){if(d.ok){document.getElementById('s-auth').classList.remove('active');show('s-welcome');}else{var e=document.getElementById('auth-err');e.style.display='block';e.textContent=d.error||'Incorrect password.';}}).catch(function(e){document.getElementById('auth-err').style.display='block';document.getElementById('auth-err').textContent='Error: '+e.message;});});
document.getElementById('f-pw').addEventListener('keydown',function(e){if(e.key==='Enter')document.getElementById('b-auth').click();});
document.getElementById('b-go').addEventListener('click',function(){brand=document.getElementById('f-brand').value.trim();if(!brand)return;var st=document.getElementById('w-st');st.style.display='block';st.textContent='Looking up brand...';fetch('/api/lookup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({brand:brand})}).then(function(r){return r.json();}).then(function(d){st.style.display='none';if(d.error){st.style.display='block';st.textContent='Error: '+d.error;return;}document.getElementById('brand-sum').textContent=d.summary;show('s-confirm');}).catch(function(e){st.textContent='Error: '+e.message;});});
document.getElementById('f-brand').addEventListener('keydown',function(e){if(e.key==='Enter')document.getElementById('b-auth').addEventListener('click',function(){var pw=document.getElementById('f-pw').value;fetch('/api/auth',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw})}).then(function(r){return r.json();}).then(function(d){if(d.ok){document.getElementById('s-auth').classList.remove('active');show('s-welcome');}else{var e=document.getElementById('auth-err');e.style.display='block';e.textContent=d.error||'Incorrect password.';}}).catch(function(e){document.getElementById('auth-err').style.display='block';document.getElementById('auth-err').textContent='Error: '+e.message;});});
document.getElementById('f-pw').addEventListener('keydown',function(e){if(e.key==='Enter')document.getElementById('b-auth').click();});
document.getElementById('b-go').click();});
document.getElementById('b-yes').addEventListener('click',function(){show('s-intake');});
document.getElementById('b-no').addEventListener('click',function(){show('s-welcome');});
document.getElementById('b-back').addEventListener('click',function(){show('s-confirm');});
document.getElementById('b-analyze').addEventListener('click',function(){show('s-analysis');runStage(0);});
document.getElementById('b-next').addEventListener('click',function(){if(curStage<maxStage)runStage(curStage+1);});
document.getElementById('b-restart').addEventListener('click',reset);
document.getElementById('b-retry').addEventListener('click',reset);
document.getElementById('b-new').addEventListener('click',reset);
document.getElementById('b-send').addEventListener('click',sendFeedback);
document.getElementById('f-dlg').addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendFeedback();}});
document.getElementById('b-msg').addEventListener('click',function(){alert('Messages Worth Receiving agent coming soon.');});
document.getElementById('b-report').addEventListener('click',generateReport);
document.getElementById('b-gtm').addEventListener('click',generateRecipe);
"""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print()
    print("=" * 56)
    print("  CANNONBALL GTM - Finding Hidden Customers Agent")
    print("=" * 56)
    print("  Open: http://127.0.0.1:" + str(port))
    print("  Ctrl+C to stop.")
    print("=" * 56)
    print()
    app.run(host='0.0.0.0', port=port, debug=False)
