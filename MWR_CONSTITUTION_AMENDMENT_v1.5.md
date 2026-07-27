# MWR Constitution Amendment — v1.5

**Target file:** MWR_CONSTITUTION.md (currently v1.4 in the repo)
**Ratified by Doug, July 27, 2026.** Claude Code applies these as edits, bumps
the version to 1.5, and records the changes in the Section 8 version log.

---

## Amendment 1 — Section 4, Gold Standard 1 (the action test)

Append to Standard 1:

> Useful means actionable. The mechanical check: complete the sentence "after
> reading this, the buyer would ______" with something the buyer was not
> already doing. If the blank cannot be filled, this standard fails.
> Information the buyer cannot act on is trivia, however accurate and however
> well sourced. A cost benchmark, a date, or a peer comparison passes only
> when it changes what the buyer does next.

## Amendment 2 — Section 4, Gold Standard 4 (the one-sentence test)

Append to Standard 4:

> The insight must be statable in one sentence, and that sentence must be the
> reason the action in Standard 1 exists. If the sentence produces an
> observation ("states differ in readiness") rather than a directive lens
> ("your exemption logic predates the rule that changed it, so audit these
> three things"), this standard fails.

## Amendment 3 — Section 4, new closing paragraph (the keystone rule)

Append after Standard 7:

> **The keystone rule.** Standard 4 is the keystone. If Standard 4 fails,
> Standards 5, 6, and 7 fail automatically. Each is a property of the
> insight, not of the message: Standard 5 measures whether the insight
> advances past pain, Standard 6 whether the insight is what the buyer does
> not know, Standard 7 whether the specifics serve the insight. A message
> cannot earn downstream passes by decorating an empty center. Six dates and
> two dollar figures with no insight is not concrete and specific; it is
> concrete and specific about nothing.

## Amendment 4 — Section 4 or 5, the entailment rule (new)

Insert as its own ruled block:

> **The entailment rule.** Every factual assertion about the buyer must be
> entailed by segment membership as defined by the EDP, or backed by a
> per-member public signal carried in the artifact (members[].edp_value or a
> resolved_conditions signal covering that member).
>
> A conditional about the buyer's own situation (if, whether, may have,
> likely, probably, in case) is an automatic flag with exactly three exits:
>
> 1. **Rewrite** the claim down to what segment membership entails.
> 2. **Resolve** the condition from a per-member signal already in the
>    artifact.
> 3. **Decline**, naming the missing signal as the gap. The decline's
>    what_would_change_the_verdict field states the work order for FHC:
>    which public signal, resolved per member, would permit the assertion.
>
> The word "if" aimed at the buyer is a data-lineage alarm, not a style
> choice. Conditionals about the world ("if the deadline holds") are
> permitted; conditionals about the buyer are not.

## Amendment 5 — Section 5, format rules (length and structure)

Add to Section 5:

> - **Body length:** 150 words maximum, with a ten percent buffer (165 hard
>   ceiling) available only when the extra words are load-bearing.
> - **Subject line:** eight words or fewer.
> - **The insight must be reachable within the first two sentences of the
>   body.** A message that earns attention in paragraph three has buried its
>   reason to exist.

## Amendment 6 — Section 7, reviewer's charge (grading order)

Amend the standards check to grade in dependency order:

> **Standards check:** grade Standard 4 first. If it fails, record Standards
> 5, 6, and 7 as failed per the keystone rule and count four misses before
> examining anything else. Then grade Standards 1, 2, 3 independently. Then,
> only if Standard 4 passed, grade 5, 6, 7 on their own merits. Apply the
> entailment rule as a format-level check alongside em-dashes and length:
> any unresolved buyer-conditional fails the message regardless of scores.
> Zero misses is PVP and ships. One miss routes back for a single revision
> pass. Two or more misses is PQS and is rejected.

## Version log entry

> v1.5 — July 27, 2026. Action test (GS1), one-sentence test (GS4), keystone
> dependency rule, entailment rule with three-exit conditional handling,
> length and structure format rules, dependency-ordered grading. Origin: the
> first Kahuna grading session against live HMA output, in which a message
> scoring 7/7 on criteria presence scored 2/7 on criteria function, and a
> buyer-conditional exposed a missing membership roster in the FHC contract.
