# Ndiri Kunzwa Sei? — Symptom Triage Demo

A Shona/Ndebele-first symptom triage prototype for a low-resource healthcare
context (Zimbabwe pilot). This repo contains **demo-only** front ends that
simulate the patient-facing triage flow and a deterministic, clinically
auditable rule engine — built to sanity-check UX, copy, and triage logic with
stakeholders before any real engineering investment.

> **This is a prototype, not a medical device.** No version in this repo
> makes real diagnostic claims, stores real patient data, or has been
> reviewed by a licensed clinician. See [Status & Limitations](#status--limitations).

---

## Contents

| File | What it is |
|---|---|
| `triage_demo.html` | Self-contained HTML/CSS/JS demo. Open directly in a browser, no install. |
| `triage_demo_streamlit.py` | Python/Streamlit port of the same flow — easier to run locally, share, and iterate on for internal stakeholder demos. |
| `zimbabwe_triage_mvp_grant_framework.md` | The underlying product spec and grant proposal framework this demo is built from (technical spec, glossary, M&E plan, ethical guardrails). |

---

## Quick Start

### Option A — HTML demo (no install)

```bash
git clone <this-repo-url>
cd <repo>
open triage_demo.html   # macOS
# or: xdg-open triage_demo.html   (Linux)
# or: just double-click the file in a file browser
```

No server, no dependencies, no network calls. Works fully offline once the
page is loaded (fonts are pulled from Google Fonts on first load only).

### Option B — Streamlit demo

```bash
git clone <this-repo-url>
cd <repo>
python3 -m venv venv && source venv/bin/activate   # optional but recommended
pip install streamlit
streamlit run triage_demo_streamlit.py
```

This opens the app in your browser at `http://localhost:8501`.

---

## What the Demo Does

Both versions walk through the same three-step flow:

1. **Symptom selection** — patient picks from a chip/checkbox list of common
   symptoms (Shona-first, English toggle available).
2. **Duration** — a slider capturing how long the symptom has been present.
3. **Context** — age band and pregnancy status, both of which affect
   triage weighting.

The app then returns one of three outcomes, mirroring the intended production
system:

| Result | Meaning | Trigger examples |
|---|---|---|
| 🟢 **Green** | Safe to self-manage at home | Low symptom score, short duration, no red flags |
| 🟡 **Yellow** | See a clinic within 48 hours | Moderate symptom score, longer duration, pregnancy, or age extremes |
| 🔴 **Red** | Seek urgent care immediately | Any hard-coded red flag: chest pain + breathlessness together, confusion, convulsions, heavy bleeding, or high fever in a child under 5 |

A simulated SMS follow-up message and a session-only "episode log" illustrate
the adherence-tracking and data-collection goals from the underlying spec,
without actually sending anything or persisting data anywhere.

---

## Rule Engine

The triage logic is intentionally **deterministic and separate from the UI**
in both versions — in the HTML file it's the `runTriage()` function; in the
Streamlit file it's `run_triage()`. This is a design choice carried over from
the technical spec, not an accident of how the demo was built:

- Red-flag conditions are checked first and short-circuit to `red` regardless
  of score.
- Everything else is scored by symptom weight, adjusted for duration, age
  band, and pregnancy, then thresholded into `yellow` or `green`.
- The scoring weights and thresholds in this repo are **placeholder values**
  for demo purposes. They have not been reviewed or signed off by a
  clinician and must not be used as-is in anything patient-facing.

If you're extending this into the real MVP, keep this function isolated and
version it — the goal is that a named clinical reviewer can read and approve
changes to *just this function* without touching UI code.

---

## Project Structure Notes

```
.
├── triage_demo.html              # standalone demo, vanilla JS
├── triage_demo_streamlit.py       # standalone demo, Python
└── zimbabwe_triage_mvp_grant_framework.md   # full product/grant spec
```

Both demo files are currently self-contained on purpose (no shared module)
so either can be handed to a stakeholder as a single file. If this grows past
the demo stage, the natural next step is to extract `run_triage()` /
`runTriage()` into a shared, tested module (e.g. a small Python package or a
JSON-defined rule set) so the HTML and Streamlit — or a future real
backend — all share one source of truth for triage logic.

---

## Status & Limitations

- **Not clinically validated.** Symptom weights, thresholds, and red-flag
  rules are illustrative and have not been reviewed by a doctor or nurse.
- **Not linguistically validated.** Shona terms and phrases are a draft
  starting point and need review by a Shona-speaking clinician or community
  health worker before any real use — see the glossary section of
  `zimbabwe_triage_mvp_grant_framework.md` for the full list and caveats.
  Ndebide localization does not exist yet in this repo.
- **No persistence, no real notifications.** The "SMS follow-up" is a static
  message, not a real integration. Episode logs live only in the current
  browser session / Streamlit session and disappear on refresh.
- **No LLM integration.** The full spec describes a lightweight LLM layer
  for free-text parsing and explanation generation; both demos in this repo
  use fixed checkbox/chip inputs instead, to keep the prototype dependency-free.

## Suggested Next Steps

1. Clinical review and sign-off of the red-flag rules and scoring weights.
2. Native-speaker review of all Shona (and a separate Ndebele build) copy.
3. Decide on a shared rule-engine module if both front ends are kept long-term.
4. Replace the fixed inputs with free-text + voice input, backed by the
   parsing LLM layer described in the spec, once the rule engine itself is
   validated.

## License / Attribution

Internal prototype — add a license here before making this repo public if
that's the intent (MIT/Apache-2.0 are common defaults for this kind of
tooling, but check with your organization first, especially given the
health-data context).
