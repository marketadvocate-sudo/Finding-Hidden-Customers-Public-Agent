# FHC Contract Amendment — Segment Membership Roster

**Target file:** fhc_output.schema.json (the FHC to MWR contract)
**Status:** Proposed amendment, ratified in principle by Doug July 27, 2026.
Claude Code reconciles exact field names against the live FHC export before
committing.

---

## 1. The problem this fixes

The contract carries the EDP as a signal description but no membership roster.
MWR cannot verify that a claim about the buyer is entailed by segment
membership, because the artifact does not say who the members are or what
their EDP values are. The symptom: PVP exemplars forced into conditionals
("if your exemption logic predates June 1") because the data to assert is not
in the artifact. The word "if" in a PVP is a data-lineage alarm.

The Clay implementation of the methodology already does this correctly: the
pain datapoint arrives as a column per account. The contract is being brought
up to the standard the spreadsheet already meets.

## 2. Schema changes

### 2a. Add `members` to the segment definition (required)

Add to `$defs.segment.properties`:

```json
"members": {
  "type": "array",
  "description": "MWR-CRITICAL. The accounts that satisfy this segment's EDP condition, each with its observed EDP value and a stamped source. This is what makes segment membership an assertable fact about each buyer. A segment without members supports no assertions and MWR must treat every buyer claim as unentailed.",
  "minItems": 1,
  "items": {
    "type": "object",
    "required": ["name", "edp_value", "source"],
    "additionalProperties": false,
    "properties": {
      "name": {
        "type": "string",
        "description": "The account. Example: State of Georgia Department of Community Health."
      },
      "edp_value": {
        "type": "string",
        "description": "This member's observed value for the segment's EDP signal. Example: No declared implementation path as of June 2026."
      },
      "source": { "$ref": "#/$defs/source_ref" },
      "signals": {
        "type": "array",
        "description": "Optional per-member values for the segment's resolved_conditions (see 2b). Each entry resolves one condition for this member with a stamped source.",
        "items": {
          "type": "object",
          "required": ["condition_id", "value", "source"],
          "additionalProperties": false,
          "properties": {
            "condition_id": { "type": "string" },
            "value": { "type": "string" },
            "source": { "$ref": "#/$defs/source_ref" }
          }
        }
      }
    }
  }
}
```

Add `"members"` to `$defs.segment.required`.

### 2b. Add `resolved_conditions` to the segment definition (optional)

Some PVP angles depend on a finer condition than the EDP itself (example:
exemption guidance published before June 1, 2026). When FHC sources a public
signal that resolves such a condition per member, it declares the condition
here and carries the per-member values in `members[].signals`.

```json
"resolved_conditions": {
  "type": "array",
  "description": "Conditions beyond the EDP that FHC has resolved with per-member public signals. A condition declared here MUST have a corresponding signal entry for every member, or be marked partial with the uncovered members listed. MWR may assert a condition about a buyer only if it is the EDP or appears here with that member covered.",
  "items": {
    "type": "object",
    "required": ["condition_id", "statement", "signal_description", "coverage"],
    "additionalProperties": false,
    "properties": {
      "condition_id": { "type": "string" },
      "statement": {
        "type": "string",
        "description": "The condition as an assertable sentence template. Example: exemption guidance was last published before June 1, 2026."
      },
      "signal_description": {
        "type": "string",
        "description": "The public signal that resolves it. Example: publication date of the state's most recent exemption guidance on its Medicaid agency site, cross-checked against Medicaid.gov SPA and waiver filings."
      },
      "coverage": {
        "type": "string",
        "enum": ["complete", "partial"],
        "description": "complete: every member has a signal entry. partial: uncovered_members lists the gaps and MWR treats the condition as unentailed for them."
      },
      "uncovered_members": {
        "type": "array",
        "items": { "type": "string" }
      }
    }
  }
}
```

## 3. FHC agent spec amendment (upstream behavior change)

Add to the FHC agent's Investigate-stage instructions:

> **Condition sourcing rule.** If the segment's pvp_angle, or any candidate
> messaging angle surfaced during analysis, depends on a condition about the
> buyer beyond the EDP itself, FHC must attempt to source a public per-member
> signal that resolves that condition, and either (a) declare it in
> resolved_conditions with per-member signals, or (b) explicitly record in the
> artifact that the condition could not be publicly resolved, so downstream
> agents know the conditional is a dead end rather than an oversight. Finding
> public signals for conditions is the Investigate stage's job; an unresolved
> condition silently passed downstream is an Investigate-stage failure.

## 4. Migration notes

- The HMA fixture predates this amendment and has no members array. It
  remains valid against the pre-amendment schema; re-export from the FHC
  agent (or hand-stamp the 43 states from the KFF tracker) to bring it to
  the amended contract. The tracker makes hand-stamping feasible: state,
  implementation status, one shared source_ref.
- Version the schema. Add a top-level `schema_version` field if the live
  export does not already carry one, so MWR can distinguish pre-members
  artifacts and treat all buyer claims in them as unentailed.
- The Vercel application inherits this: the pipeline's data model carries
  accounts with per-account EDP values from the FHC step forward. List
  build, enrichment, and Instantly custom variables all consume
  members[].edp_value and members[].signals downstream.
