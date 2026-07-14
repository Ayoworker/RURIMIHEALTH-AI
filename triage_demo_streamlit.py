"""
Ndiri Kunzwa Sei? — Symptom Triage Demo (Streamlit)

A click-through simulation of the Shona/Ndebele-first triage MVP.
No backend, no LLM call, no real data storage — session-only, for demoing
the patient flow and rule-engine logic to stakeholders.

Run:
    pip install streamlit
    streamlit run triage_demo_streamlit.py
"""

import streamlit as st
from datetime import datetime

# ---------------------------------------------------------------------------
# Content / copy
# ---------------------------------------------------------------------------

STR = {
    "sn": {
        "kicker": "Demo · Inoshanda pasina network",
        "title": "Ndiri Kunzwa Sei?",
        "lang_label": "Mutauro",
        "step1": "Nhamba 1 / 3",
        "q1": "Uri kunzwa sei nhasi?",
        "sub1": "Sarudza zvinhu zvose zvaunonzwa. Unogona kusarudza zvinopfuura chimwe.",
        "step2": "Nhamba 2 / 3",
        "q2": "Zvatanga riini?",
        "sub2": "Tsvedzera kuti utaure kuti zvave nguva yakareba sei.",
        "days": lambda n: "Nhasi chaiyo" if n == 0 else ("Zuva rimwe chete" if n == 1 else f"{n} mazuva"),
        "next": "Enderera mberi",
        "back": "Dzokera",
        "step3": "Nhamba 3 / 3",
        "q3": "Chinhu chimwe chekupedzisira",
        "sub3": "Izvi zvinotibatsira kuti tinyatso ronga zvakanaka.",
        "age_label": "Zera",
        "ages": ["Mwana (pasi pemakore 5)", "Mudiki (5–17)", "Mukuru (18–59)", "Chembere/Sekuru (60+)"],
        "preg_label": "Wakazvitakura here?",
        "preg_opts": ["Kwete", "Hongu", "Hazvishandi"],
        "submit": "Ona mhinduro",
        "result_label": "Mhedzisiro",
        "green": {
            "tag": "GREEN — Chirwere chidiki",
            "h": "Zvakanaka kuzvirapa pamba",
            "body": "Zviratidzo zvako hazviratidze njodzi. Zorora, unwa mvura yakawanda, uye tarisisa kana zviri kuipa.",
            "shona": "“Chinhu ichi chinokubatsira kuziva zvekuita, asi hachisi chiremba. "
                     "Kana zvichiramba zvichikuvhundutsa, enda kuchipatara.”",
        },
        "yellow": {
            "tag": "YELLOW — Enda kukiriniki",
            "h": "Ona munamiridzi mukati memaawa 48",
            "body": "Zviratidzo zvako zvinoda kuongororwa nemunamiridzi kana chiremba mukati "
                    "memazuva maviri, kunyangwe zvisati zviri njodzi izvozvi.",
            "shona": "“Sarudzo yako yakachenjera ndeye kuenda kukiriniki iri pedyo newe mukati memaawa 48.”",
        },
        "red": {
            "tag": "RED — Njodzi, enda ikozvino",
            "h": "Enda kuchipatara ikozvino chaiyo",
            "body": "Zviratidzo zvako zvinoreva kuti pane njodzi. Sarudza kubatsirwa nekukurumidza — usamirira.",
            "shona": "“Izvi zvinoda rubatsiro rwekurumidza. Enda kuchipatara kana kufonera rubatsiro ikozvino.”",
        },
        "followup": "Follow-up: SMS ichatumirwa mumaawa 72 kuti ibvunze kana wateerera zano rino.",
        "disclaimer": "Chinhu ichi hachisi chiremba — chinongokupa mazano.",
        "log_title": "Nhoroondo yezviitiko (demo)",
        "restart": "Tanga patsva",
        "symptoms_needed": "Sarudza chiratidzo chimwe chete kuti uenderere mberi.",
    },
    "en": {
        "kicker": "Demo · Works offline",
        "title": "How Are You Feeling?",
        "lang_label": "Language",
        "step1": "Step 1 / 3",
        "q1": "What are you feeling today?",
        "sub1": "Select everything that applies. You can pick more than one.",
        "step2": "Step 2 / 3",
        "q2": "When did it start?",
        "sub2": "Slide to show roughly how long it's been going on.",
        "days": lambda n: "Today" if n == 0 else ("1 day" if n == 1 else f"{n} days"),
        "next": "Continue",
        "back": "Back",
        "step3": "Step 3 / 3",
        "q3": "One last thing",
        "sub3": "This helps the system route you correctly.",
        "age_label": "Age",
        "ages": ["Child (under 5)", "Youth (5–17)", "Adult (18–59)", "Older adult (60+)"],
        "preg_label": "Are you pregnant?",
        "preg_opts": ["No", "Yes", "Not applicable"],
        "submit": "See result",
        "result_label": "Result",
        "green": {
            "tag": "GREEN — Minor",
            "h": "Safe to manage at home",
            "body": "Your symptoms don't show danger signs. Rest, drink plenty of fluids, "
                    "and monitor for changes.",
            "shona": "“This tool helps you know what to do, but it is not a doctor. "
                     "If you're still worried, go to the clinic.”",
        },
        "yellow": {
            "tag": "YELLOW — See a clinic",
            "h": "See a nurse or clinic within 48 hours",
            "body": "Your symptoms warrant a clinical check within the next two days, "
                    "even though nothing points to immediate danger.",
            "shona": "“Your safest move is to visit your nearest clinic within the next 48 hours.”",
        },
        "red": {
            "tag": "RED — Urgent",
            "h": "Go to a hospital right now",
            "body": "Your symptoms suggest a possible emergency. Seek urgent care "
                    "immediately — don't wait.",
            "shona": "“This needs urgent help. Go to the hospital or call for emergency assistance now.”",
        },
        "followup": "Follow-up: an SMS will be sent in 72 hours to check whether you followed this advice.",
        "disclaimer": "This tool is not a doctor — it only offers guidance.",
        "log_title": "Episode log (demo)",
        "restart": "Start over",
        "symptoms_needed": "Select at least one symptom to continue.",
    },
}

# id, shona label, english label, weight, special flags
SYMPTOMS = [
    dict(id="fever", sn="Fivha", en="Fever", weight=2),
    dict(id="headache", sn="Kurwadziwa musoro", en="Headache", weight=1),
    dict(id="cough", sn="Kukosora", en="Cough", weight=1),
    dict(id="chestpain", sn="Kurwadziwa muchipfuva", en="Chest pain", weight=4),
    dict(id="breathless", sn="Kunetseka kufema", en="Difficulty breathing", weight=4),
    dict(id="diarrhoea", sn="Kurutsa/manyoro", en="Diarrhoea", weight=2),
    dict(id="vomiting", sn="Kurutsa", en="Vomiting", weight=2),
    dict(id="stomachpain", sn="Kurwadziwa dumbu", en="Stomach pain", weight=2),
    dict(id="rash", sn="Mhezi", en="Rash", weight=1),
    dict(id="confusion", sn="Kupenga/kusanzwisisa", en="Confusion", weight=5, always_red=True),
    dict(id="convulsions", sn="Kuwira pasi (zvipusha)", en="Convulsions", weight=5, always_red=True),
    dict(id="bleeding", sn="Kubuda ropa kwakawandisa", en="Heavy bleeding", weight=5, always_red=True),
]

TRIAGE_COLORS = {
    "green": "#2f7a4d",
    "yellow": "#c98a1f",
    "red": "#a13a2e",
}
TRIAGE_BG = {
    "green": "#e3efe1",
    "yellow": "#faedd2",
    "red": "#f4dcd6",
}

# ---------------------------------------------------------------------------
# Rule engine (mirrors the deterministic engine in the technical spec —
# the point of keeping it separate and readable is that a clinical partner
# can review this function on its own, without touching UI code)
# ---------------------------------------------------------------------------

def run_triage(selected_ids, duration_days, age_index, preg_index):
    selected = [s for s in SYMPTOMS if s["id"] in selected_ids]

    has_chest_breath_pair = (
        "chestpain" in selected_ids and "breathless" in selected_ids
    )
    has_always_red = any(s.get("always_red") for s in selected)
    high_fever_in_child = (
        age_index == 0 and "fever" in selected_ids and duration_days >= 1
    )

    if has_chest_breath_pair or has_always_red or high_fever_in_child:
        return "red"

    score = sum(s["weight"] for s in selected)
    if duration_days >= 5:
        score += 2
    if age_index in (0, 3):  # young child or older adult
        score += 1
    if preg_index == 1:  # pregnant
        score += 2

    if score >= 6:
        return "yellow"
    return "green"


# ---------------------------------------------------------------------------
# Streamlit app
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Symptom Triage Demo", page_icon="🩺", layout="centered")

# --- minimal theming to keep it out of default-Streamlit-blue territory ---
st.markdown(
    """
    <style>
    .stApp { background-color: #efe9d8; }
    .block-container { max-width: 460px; padding-top: 2rem; }
    h1, h2, h3 { font-family: Georgia, 'Times New Roman', serif; }
    .kicker {
        font-family: 'Courier New', monospace;
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #164543;
    }
    .banner {
        border-radius: 14px;
        padding: 18px 20px 16px;
        margin-bottom: 14px;
    }
    .banner .tag {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .banner p { font-size: 14px; line-height: 1.55; margin: 4px 0; }
    .disclaimer {
        font-size: 12px; color: #4a5a4f; border-top: 1px dashed #d8cfb3;
        padding-top: 8px; margin-top: 6px;
    }
    .followup {
        background: #f8f4e8; border: 1px solid #d8cfb3; border-radius: 12px;
        padding: 12px 16px; font-size: 12.5px; color: #4a5a4f; margin-bottom: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "step" not in st.session_state:
    st.session_state.step = 1
if "selected" not in st.session_state:
    st.session_state.selected = set()
if "duration" not in st.session_state:
    st.session_state.duration = 1
if "age" not in st.session_state:
    st.session_state.age = 2
if "preg" not in st.session_state:
    st.session_state.preg = 0
if "log" not in st.session_state:
    st.session_state.log = []
if "lang" not in st.session_state:
    st.session_state.lang = "sn"


def t():
    return STR[st.session_state.lang]


def reset():
    st.session_state.step = 1
    st.session_state.selected = set()
    st.session_state.duration = 1
    st.session_state.age = 2
    st.session_state.preg = 0


# --- header ---
top_l, top_r = st.columns([3, 1])
with top_l:
    st.markdown(f"<div class='kicker'>{t()['kicker']}</div>", unsafe_allow_html=True)
    st.title(t()["title"])
with top_r:
    lang_choice = st.radio(
        t()["lang_label"], ["SN", "EN"],
        index=0 if st.session_state.lang == "sn" else 1,
        label_visibility="collapsed",
        horizontal=True,
    )
    st.session_state.lang = "sn" if lang_choice == "SN" else "en"

st.progress(min(st.session_state.step, 3) / 3)
st.divider()

# --- step 1: symptoms ---
if st.session_state.step == 1:
    st.caption(t()["step1"])
    st.subheader(t()["q1"])
    st.write(t()["sub1"])

    cols = st.columns(2)
    for i, s in enumerate(SYMPTOMS):
        label = s["sn"] if st.session_state.lang == "sn" else s["en"]
        checked = s["id"] in st.session_state.selected
        with cols[i % 2]:
            new_val = st.checkbox(label, value=checked, key=f"chk_{s['id']}")
            if new_val:
                st.session_state.selected.add(s["id"])
            else:
                st.session_state.selected.discard(s["id"])

    if len(st.session_state.selected) == 0:
        st.info(t()["symptoms_needed"])

    if st.button(t()["next"], type="primary", disabled=len(st.session_state.selected) == 0):
        st.session_state.step = 2
        st.rerun()

# --- step 2: duration ---
elif st.session_state.step == 2:
    st.caption(t()["step2"])
    st.subheader(t()["q2"])
    st.write(t()["sub2"])

    st.session_state.duration = st.slider(
        t()["days"](st.session_state.duration),
        min_value=0, max_value=14, value=st.session_state.duration,
        label_visibility="visible",
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button(t()["back"]):
            st.session_state.step = 1
            st.rerun()
    with c2:
        if st.button(t()["next"], type="primary"):
            st.session_state.step = 3
            st.rerun()

# --- step 3: context ---
elif st.session_state.step == 3:
    st.caption(t()["step3"])
    st.subheader(t()["q3"])
    st.write(t()["sub3"])

    st.session_state.age = t()["ages"].index(
        st.radio(t()["age_label"], t()["ages"], index=st.session_state.age)
    )
    st.session_state.preg = t()["preg_opts"].index(
        st.radio(t()["preg_label"], t()["preg_opts"], index=st.session_state.preg)
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button(t()["back"]):
            st.session_state.step = 2
            st.rerun()
    with c2:
        if st.button(t()["submit"], type="primary"):
            result = run_triage(
                st.session_state.selected,
                st.session_state.duration,
                st.session_state.age,
                st.session_state.preg,
            )
            st.session_state.result = result
            st.session_state.log.insert(0, {
                "time": datetime.now().strftime("%H:%M"),
                "result": result,
                "count": len(st.session_state.selected),
            })
            st.session_state.step = 4
            st.rerun()

# --- step 4: result ---
elif st.session_state.step == 4:
    r = st.session_state.result
    data = t()[r]
    bg = TRIAGE_BG[r]
    color = TRIAGE_COLORS[r]

    st.caption(t()["result_label"])
    st.markdown(
        f"""
        <div class="banner" style="background:{bg}; border:1px solid {color}55;">
            <div class="tag" style="color:{color};">{data['tag']}</div>
            <h3 style="margin:0 0 6px;">{data['h']}</h3>
            <p>{data['body']}</p>
            <p style="font-style:italic; color:#4a5a4f;">{data['shona']}</p>
            <div class="disclaimer">{t()['disclaimer']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div class='followup'>📩 {t()['followup']}</div>",
        unsafe_allow_html=True,
    )

    if st.button(t()["restart"], type="primary"):
        reset()
        st.rerun()

    if st.session_state.log:
        st.markdown(f"**{t()['log_title']}**")
        for entry in st.session_state.log[:5]:
            dot_color = TRIAGE_COLORS[entry["result"]]
            st.markdown(
                f"<span style='color:{dot_color};'>●</span> "
                f"{entry['count']} symptom(s) logged &nbsp;·&nbsp; "
                f"<span style='font-family:monospace; color:#4a5a4f;'>{entry['time']}</span>",
                unsafe_allow_html=True,
            )

st.caption("rule_engine_v0.1 · demo data is session-only · not a diagnosis")
