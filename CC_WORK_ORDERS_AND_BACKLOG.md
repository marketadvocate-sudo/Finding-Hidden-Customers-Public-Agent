# Claude Code Work Orders + PVP Capability Backlog

Two work orders, one per repo, in dependency order (contract first, then the
agent that consumes it). Plus the running backlog, because this session solved
one challenge, not the whole problem.

---

## Work Order 1 — FHC side (contract + upstream agent)

Paste into a Claude Code session on the repo that owns the contract:

```
Read FHC_CONTRACT_AMENDMENT.md. Plan first, no code until I approve.

1. Amend fhc_output.schema.json: add the required members array and optional
   resolved_conditions to the segment definition, per the amendment doc.
   Reconcile field names against the FHC agent's live export format before
   committing. Add schema_version if absent.
2. Amend the FHC agent spec with the condition sourcing rule from Section 3
   of the amendment doc.
3. Bring the HMA fixture up to the amended contract: stamp the members array
   from the KFF Work Requirements Tracker (state, implementation status, one
   shared source_ref per the tracker). Flag any state whose status you cannot
   read from the tracker rather than guessing.
4. Re-validate the fixture against the amended schema. Report the member
   count and coverage.
End with open questions as a numbered list.
```

## Work Order 2 — MWR side (constitution + agent + fixtures)

Run after Work Order 1 merges, so the agent updates against the amended
contract:

```
Read MWR_CONSTITUTION_AMENDMENT_v1.5.md. Plan first, no code until I approve.

1. Apply all six amendments to MWR_CONSTITUTION.md. Bump to v1.5, update the
   Section 8 version log with the provided entry.
2. Update AGENT.md: Stage 4 drafts from the insight outward (state the
   one-sentence insight and the buyer action first, then draft, then verify
   every specific serves them; check every buyer claim against members and
   resolved_conditions before asserting). Stage 5 grades in dependency order
   per amended Section 7 and applies the entailment rule's three exits.
3. Update mwr_output.schema.json: the scorecard records keystone-cascade
   failures distinctly from independent failures, and the decline's
   what_would_change_the_verdict carries the FHC work order when the
   entailment rule's third exit fires.
4. Replace examples/mwr_output.hma.json with the v1.5-passing rewrite Doug
   provides. Add the rejected first message as
   examples/mwr_output.hma.REJECTED.json with its 2/7 scorecard, labeled as
   the negative golden fixture: ingredient-stuffing without an insight.
5. Update gate.py if it can mechanically check any of the new rules (word
   counts, subject length, buyer-conditional detection via if/whether/may
   have aimed at second person, entailment lookups against members). Keep
   judgment calls out of the script; it stays the bouncer, not the author.
6. Re-run GATE_RUN_CHECKLIST.md end to end. The agent must produce
   insight-led, entailed, under-165-word output unprompted.
7. Tag v1.1 after the gate run passes.
End with open questions as a numbered list.
```

Before running Work Order 2, Doug supplies: the final edited rewrite text
(his pass on the 148-word draft), and rulings on the two open Kahuna calls
below.

---

## PVP Capability Backlog

This session resolved one challenge. The rest of the known list, so nothing
silently drops. Statuses: OPEN (needs a ruling or a build), PARTIAL
(addressed but unproven), WATCH (monitor across runs before acting).

**1. Entailment / conditionals — RESOLVED IN PRINCIPLE this session.**
Amendments drafted, work orders above. Unproven until the gate run passes
and a fresh artifact with a members roster flows through.

**2. Insight generation quality — OPEN, and the hard one.** The v1.5 rules
let the grader catch a missing insight. Nothing yet makes the agent reliably
FIND the best insight rather than the first passable one. Candidate
approaches: Stage 4 generates three candidate insights and grades them
against each other before drafting; or a distinct insight-selection stage
with its own criteria. Needs design, not just rules. This is the core PVP
capability and deserves its own session.

**3. GS6 market-knowledge judgment — OPEN Kahuna call, recurring.** Every
asymmetry pass rests on an assumption about what this buyer already tracks.
Currently a human call per message. Worth deciding: does the constitution
encode per-vertical heuristics (e.g., "assume state Medicaid directors do
not track other states' cost filings"), sourced into vertical-context files,
or does this stay permanently human?

**4. Sender-credential presence — OPEN Kahuna call from the rewrite
session.** The 150-word cap and the credential paragraph cannot coexist. Rule
needed: does the exemplar carry one credential sentence, or does identity
live entirely in the signature block? The agent faces this on every run.

**5. Self-score inflation — PARTIAL.** The keystone rule and mechanical
checks close the ingredient-stuffing route. The evidence-citation
requirement exists. WATCH across the next several runs: does the agent's
Stage 5 self-score match Doug's Red-hat score? Divergence means the
disqualifiers need more teeth.

**6. Cannonball voice adherence — OPEN.** No mechanical check exists or
likely can. Current control is the model plus the constitution's voice
clause. Consider: a voice checklist derived from the Doug Voice Bible as a
Stage 4 reference, and voice as an explicit line in the reviewer's charge.

**7. Silver/Bronze fixture gap — OPEN, carried from recovery.** Run 2 of the
gate checklist still cannot execute. Resolves free of charge when Work Order
1's fixture re-stamp happens IF a fresh FHC export restores the full segment
set; otherwise still needs synthetic scaffolding.

**8. Multi-segment behavior — WATCH.** Verdict-per-segment is specified but
has only ever run against a one-segment fixture. First multi-segment
artifact should get a deliberate review.
