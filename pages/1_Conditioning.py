import streamlit as st
import re

st.set_page_config(page_title="Conditioning Session Builder", page_icon="🏃")

# --- 1. TEST -> MAS / ASR CALCULATIONS ---
def calc_mas_from_1200m(time_seconds):
    """MAS (Maximal Aerobic Speed) in m/s from a 1200m time trial."""
    if not time_seconds or time_seconds <= 0:
        return None
    return 1200 / time_seconds

def calc_asr(mas_ms, max_speed_kmh):
    """ASR (Anaerobic Speed Reserve) = max sprint speed - MAS, both in m/s.
    Returns (asr_ms, max_speed_ms) or (None, None) if inputs are missing."""
    if not mas_ms or not max_speed_kmh or max_speed_kmh <= 0:
        return None, None
    max_speed_ms = max_speed_kmh / 3.6
    return max_speed_ms - mas_ms, max_speed_ms

def speed_to_kmh(speed_ms):
    return speed_ms * 3.6

def speed_to_pace_per_km(speed_ms):
    """Pace as mm:ss per km for a given speed in m/s."""
    if not speed_ms or speed_ms <= 0:
        return "-"
    sec_per_km = 1000 / speed_ms
    mins = int(sec_per_km // 60)
    secs = int(round(sec_per_km % 60))
    if secs == 60:
        mins += 1
        secs = 0
    return f"{mins}:{secs:02d}/km"

def apply_targets(protocol_str, mas_ms, asr_ms):
    """Replace N%MAS with the equivalent MAS-based pace (use up to ~120%),
    and N%ASR with the equivalent Anaerobic-Speed-Reserve-based pace
    (MAS + %ASR * ASR) for supramaximal/sprint-repeat work."""

    def mas_replacer(match):
        pct = float(match.group(1))
        if not mas_ms:
            return "-"
        return speed_to_pace_per_km(mas_ms * (pct / 100.0))

    def asr_replacer(match):
        pct = float(match.group(1))
        if not mas_ms or asr_ms is None:
            return "-"
        return speed_to_pace_per_km(mas_ms + (pct / 100.0) * asr_ms)

    text = re.sub(r"(\d+(?:\.\d+)?)%MAS", mas_replacer, protocol_str)
    text = re.sub(r"(\d+(?:\.\d+)?)%ASR", asr_replacer, text)
    return text

def protocol_needs_asr(protocol_dict):
    """Check whether any week in a protocol uses %ASR, so we know whether
    to require a max-speed input before building."""
    return any("%ASR" in v for v in protocol_dict.values())

# --- 2. SESSION STATE ---
if 'cond_history' not in st.session_state:
    st.session_state.cond_history = []

# --- 3. DEFAULT PROTOCOL LIBRARY ---
# PLACEHOLDER CONTENT: structural examples only, in the same shape as the
# strength app's protocol library (programme type -> named protocol -> week
# -> prescription). Replace these with your own prescriptions before using
# this for real programming.
#
# Use "%MAS" for intensities up to ~120% MAS, and "%ASR" for supramaximal /
# short sprint-repeat work above that (Anaerobic Speed Reserve method).
RUNNING_PROTOCOLS = {
    "Capacity": {
        "Long_Intervals": {
            "Base":    "6 x 3min @ 85%MAS, 90s rec",
            "Load 1":  "6 x 3min @ 88%MAS, 75s rec",
            "Load 2":  "7 x 3min @ 90%MAS, 75s rec",
            "Perform": "8 x 3min @ 90%MAS, 60s rec",
        },
    },
    "Output": {
        "VO2max_Reps": {
            "Base":    "8 x 90s @ 100%MAS, 90s rec",
            "Load 1":  "8 x 90s @ 105%MAS, 75s rec",
            "Load 2":  "10 x 90s @ 110%MAS, 75s rec",
            "Perform": "10 x 90s @ 115%MAS, 60s rec",
        },
    },
    "Repeatability": {
        "Short_Rep_Sprint": {
            "Base":    "10 x 6s @ 30%ASR, 24s rec",
            "Load 1":  "10 x 6s @ 35%ASR, 24s rec",
            "Load 2":  "12 x 6s @ 40%ASR, 20s rec",
            "Perform": "12 x 6s @ 45%ASR, 20s rec",
        },
    },
}

WEEK_FLOW = ["Base", "Load 1", "Load 2", "Perform"]

# --- 4. UI ---
st.title("🏃 Conditioning Session Builder")

mode = st.selectbox("Mode", ["Running", "Cycling", "Rowing", "Ski Erg"])

if mode != "Running":
    st.info(
        f"**{mode}** isn't configured yet — Running is the first mode built out. "
        f"Give me the test protocol you use for {mode} (e.g. 2km time, FTP test, "
        f"500m split) and the target metric it should produce, and this mode can "
        f"be added the same way Running was."
    )
    st.stop()

st.subheader("1. Test Result")

test_type = st.selectbox("Test Type", ["1200m Time Trial"])
st.caption("More test types can be added later — this is the first one wired up.")

c1, c2 = st.columns(2)
test_min = c1.number_input("1200m time — minutes", min_value=0, max_value=15, value=4, step=1)
test_sec = c2.number_input("1200m time — seconds", min_value=0, max_value=59, value=0, step=1)
test_time_s = test_min * 60 + test_sec
mas_ms = calc_mas_from_1200m(test_time_s)

max_speed_kmh = st.number_input(
    "Max Sprint Speed (km/h) — from a flying sprint test",
    min_value=0.0, value=0.0, step=0.1,
    help="Used for %ASR intensities above ~120% MAS (e.g. short sprint-repeat reps). "
         "Leave at 0 if not building a Repeatability session yet."
)
asr_ms, vmax_ms = calc_asr(mas_ms, max_speed_kmh)

if mas_ms:
    summary = (
        f"MAS: **{mas_ms:.2f} m/s** | {speed_to_kmh(mas_ms):.1f} km/h | "
        f"{speed_to_pace_per_km(mas_ms)} pace"
    )
    if asr_ms is not None:
        summary += (
            f"  \nMax Speed: **{vmax_ms:.2f} m/s** ({max_speed_kmh:.1f} km/h) | "
            f"ASR: **{asr_ms:.2f} m/s** ({speed_to_kmh(asr_ms):.1f} km/h)"
        )
    st.success(summary)

st.divider()
st.subheader("2. Programme Type")
prog_type = st.selectbox("Programme Focus", ["Capacity", "Output", "Repeatability"])
avail_protocols = list(RUNNING_PROTOCOLS.get(prog_type, {}).keys())
protocol_choice = st.selectbox("Protocol", avail_protocols) if avail_protocols else None

if protocol_choice:
    raw = RUNNING_PROTOCOLS[prog_type][protocol_choice]
    with st.expander("Preview raw protocol (before conversion)"):
        st.json(raw)
    if protocol_needs_asr(raw) and not asr_ms:
        st.warning("This protocol uses %ASR intensities — enter a max sprint speed above to build it.")

st.divider()
if st.button("🎯 Build Conditioning Session", type="primary"):
    if not mas_ms:
        st.error("Enter a valid 1200m time first.")
    elif not protocol_choice:
        st.error(f"No protocols defined yet for {prog_type}.")
    else:
        raw = RUNNING_PROTOCOLS[prog_type][protocol_choice]
        if protocol_needs_asr(raw) and not asr_ms:
            st.error("This protocol needs a max sprint speed to calculate %ASR targets.")
        else:
            lines = [
                f"CONDITIONING BLOCK: {mode} | {prog_type} ({protocol_choice})",
                f"MAS: {mas_ms:.2f} m/s ({speed_to_kmh(mas_ms):.1f} km/h, {speed_to_pace_per_km(mas_ms)})",
            ]
            if asr_ms is not None:
                lines.append(
                    f"Max Speed: {vmax_ms:.2f} m/s ({max_speed_kmh:.1f} km/h) | "
                    f"ASR: {asr_ms:.2f} m/s ({speed_to_kmh(asr_ms):.1f} km/h)"
                )
            lines.append("=" * 60)
            for wk in WEEK_FLOW:
                if wk in raw:
                    target = apply_targets(raw[wk], mas_ms, asr_ms)
                    lines.append(f"\nWEEK: {wk.upper()}\n" + "-" * 30)
                    lines.append(f"  {target}")
            session_text = "\n".join(lines)
            st.session_state.cond_history.append(session_text)
            st.success("Session built — see below.")

if st.session_state.cond_history:
    st.divider()
    st.subheader("📜 Session History")
    st.download_button(
        "Download All",
        "\n\n".join(st.session_state.cond_history),
        "conditioning_sessions.txt",
    )
    for idx, block in enumerate(reversed(st.session_state.cond_history)):
        with st.expander("Session", expanded=(idx == 0)):
            st.text(block)
