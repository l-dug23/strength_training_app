import streamlit as st

st.set_page_config(page_title="Conditioning Session Builder", page_icon="🏃")

# --- 1. TEST -> MAS / ASR CALCULATIONS ---
def calc_mas(distance_m, time_seconds):
    """MAS (Maximal Aerobic Speed) in m/s from any distance/time time trial."""
    if not distance_m or distance_m <= 0 or not time_seconds or time_seconds <= 0:
        return None
    return distance_m / time_seconds

def calc_asr(mas_ms, max_speed_ms):
    """ASR (Anaerobic Speed Reserve) = max sprint speed - MAS, both already in m/s."""
    if not mas_ms or not max_speed_ms or max_speed_ms <= 0:
        return None, None
    return max_speed_ms - mas_ms, max_speed_ms

def speed_to_kmh(speed_ms):
    return speed_ms * 3.6

def speed_to_pace_per_km(speed_ms):
    if not speed_ms or speed_ms <= 0:
        return "-"
    sec_per_km = 1000 / speed_ms
    mins = int(sec_per_km // 60)
    secs = int(round(sec_per_km % 60))
    if secs == 60:
        mins += 1
        secs = 0
    return f"{mins}:{secs:02d}/km"

def get_target_speed(mas_ms, asr_ms, intensity_type, pct):
    """Speed in m/s for a given %MAS or %ASR intensity."""
    if intensity_type == "MAS":
        return mas_ms * (pct / 100.0) if mas_ms else None
    else:  # ASR
        if mas_ms is None or asr_ms is None:
            return None
        return mas_ms + (pct / 100.0) * asr_ms

def fmt_duration(seconds):
    seconds = round(seconds)
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"

def fmt_distance(metres):
    return f"{round(metres / 5) * 5}m"  # round to nearest 5m

# --- 2. WEEK PROGRESSION ---
WEEK_FLOW = ["Base", "Load 1", "Load 2", "Perform"]

def build_week_values(base, progression_variable, step):
    """Apply a per-week step to exactly one of reps / effort_value / intensity_pct,
    holding the other two fixed at their base value."""
    out = []
    for i, wk in enumerate(WEEK_FLOW):
        reps = base["reps"]
        effort = base["effort_value"]
        intensity = base["intensity_pct"]
        if progression_variable == "Reps/Sets":
            reps = base["reps"] + i * step
        elif progression_variable == "Volume/Duration":
            effort = base["effort_value"] + i * step
        elif progression_variable == "Intensity":
            intensity = base["intensity_pct"] + i * step
        out.append({"week": wk, "reps": max(1, int(round(reps))), "effort_value": max(0.1, effort), "intensity_pct": intensity})
    return out

def render_session(protocol, metric_mode, progression_variable, step, mas_ms, asr_ms):
    """Build the full week-by-week text block for a protocol."""
    base_speed = get_target_speed(mas_ms, asr_ms, protocol["intensity_type"], protocol["intensity_pct"])
    if metric_mode == "Time":
        base_effort_value = protocol["effort_s"]
    else:  # Distance - derive once from the protocol's base duration x base intensity speed
        base_effort_value = protocol["effort_s"] * base_speed

    base = {"reps": protocol["reps"], "effort_value": base_effort_value, "intensity_pct": protocol["intensity_pct"]}
    weeks = build_week_values(base, progression_variable, step)

    lines = []
    for w in weeks:
        speed = get_target_speed(mas_ms, asr_ms, protocol["intensity_type"], w["intensity_pct"])
        if speed is None:
            lines.append(f"\nWEEK: {w['week'].upper()}\n" + "-" * 30)
            lines.append("  Missing MAS/ASR input for this intensity.")
            continue
        if metric_mode == "Time":
            duration_s = w["effort_value"]
            distance_m = duration_s * speed
            main, companion, companion_label = fmt_duration(duration_s), fmt_distance(distance_m), "≈ distance"
        else:
            distance_m = w["effort_value"]
            duration_s = distance_m / speed
            main, companion, companion_label = fmt_distance(distance_m), fmt_duration(duration_s), "≈ time"
        lines.append(f"\nWEEK: {w['week'].upper()}\n" + "-" * 30)
        lines.append(
            f"  {w['reps']} x {main} ({companion_label}: {companion}) "
            f"@ {w['intensity_pct']:.1f}% {protocol['intensity_type']} "
            f"({speed_to_pace_per_km(speed)}) | rest {protocol['rest_s']}s"
        )
    return "\n".join(lines)

# --- 3. SESSION STATE ---
if 'cond_history' not in st.session_state:
    st.session_state.cond_history = []

# --- 4. DEFAULT PROTOCOL LIBRARY ---
# PLACEHOLDER CONTENT: structural examples only. Each protocol is defined by a
# single base prescription (reps, effort duration in seconds, rest in seconds,
# intensity type/%). The week-by-week plan is generated at build time from
# whichever variable is chosen to progress (Reps/Sets, Volume/Duration, or
# Intensity) and whichever unit (Time or Distance) is chosen to plan off.
# Replace these with your own prescriptions before using this for real programming.
RUNNING_PROTOCOLS = {
    "Capacity": {
        "Long_Intervals": {"reps": 6, "effort_s": 180, "rest_s": 90, "intensity_type": "MAS", "intensity_pct": 85},
    },
    "Output": {
        "VO2max_Reps": {"reps": 8, "effort_s": 90, "rest_s": 90, "intensity_type": "MAS", "intensity_pct": 100},
    },
    "Repeatability": {
        "Short_Rep_Sprint": {"reps": 10, "effort_s": 6, "rest_s": 24, "intensity_type": "ASR", "intensity_pct": 30},
    },
}

PROGRESSION_STEP_LABELS = {
    "Reps/Sets": "Step (extra reps per week)",
    "Volume/Duration": None,  # set dynamically below based on metric_mode
    "Intensity": "Step (extra % per week)",
}

# --- 5. UI ---
st.title("🏃 Conditioning Session Builder")

tab_builder, tab_protocols = st.tabs(["🏗️ Session Builder", "📈 Protocol Library"])

with tab_builder:
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

    test_type = st.selectbox("Test Type", ["Distance/Time Trial", "Direct MAS Entry"])
    st.caption("Distance/Time Trial covers any fixed-distance test (1200m, 2000m, 5min TT, etc). "
               "More specific named tests (30-15IFT, VAM-Eval, etc.) can be added later.")

    if test_type == "Distance/Time Trial":
        c1, c2, c3 = st.columns(3)
        test_distance_m = c1.number_input("Distance (m)", min_value=50, value=1200, step=50)
        test_min = c2.number_input("Time — minutes", min_value=0, max_value=30, value=4, step=1)
        test_sec = c3.number_input("Time — seconds", min_value=0, max_value=59, value=0, step=1)
        test_time_s = test_min * 60 + test_sec
        mas_ms = calc_mas(test_distance_m, test_time_s)
    else:  # Direct MAS Entry
        mas_ms = st.number_input("MAS (m/s)", min_value=0.0, value=5.0, step=0.05)

    max_speed_ms = st.number_input(
        "Max Sprint Speed (m/s) — from a flying sprint test",
        min_value=0.0, value=0.0, step=0.05,
        help="Used for %ASR intensities (Repeatability work). Leave at 0 if not needed."
    )
    asr_ms, vmax_ms = calc_asr(mas_ms, max_speed_ms)

    if mas_ms:
        summary = (
            f"MAS: **{mas_ms:.2f} m/s** | {speed_to_kmh(mas_ms):.1f} km/h | "
            f"{speed_to_pace_per_km(mas_ms)} pace"
        )
        if asr_ms is not None:
            summary += (
                f"  \nMax Speed: **{vmax_ms:.2f} m/s** ({speed_to_kmh(vmax_ms):.1f} km/h) | "
                f"ASR: **{asr_ms:.2f} m/s** ({speed_to_kmh(asr_ms):.1f} km/h)"
            )
        st.success(summary)

    st.divider()
    st.subheader("2. Programme Type")
    prog_type = st.selectbox("Programme Focus", ["Capacity", "Output", "Repeatability"])
    avail_protocols = list(RUNNING_PROTOCOLS.get(prog_type, {}).keys())
    protocol_choice = st.selectbox("Protocol", avail_protocols) if avail_protocols else None

    if protocol_choice:
        protocol = RUNNING_PROTOCOLS[prog_type][protocol_choice]
        with st.expander("Preview base prescription (Week 1, before progression)"):
            st.json(protocol)
        if protocol["intensity_type"] == "ASR" and not asr_ms:
            st.warning("This protocol uses %ASR — enter a max sprint speed above to build it.")

    st.divider()
    st.subheader("3. Plan & Progression")

    metric_mode = st.radio(
        "Plan sessions by",
        ["Time", "Distance"],
        horizontal=True,
        help="Time: fix the effort duration, the app tells you the distance that covers. "
             "Distance: fix the effort distance, the app tells you the time it should take."
    )

    progression_variable = st.selectbox(
        "Progress each week by",
        ["Intensity", "Reps/Sets", "Volume/Duration"],
        help="Whichever variable you pick here changes week to week (Base -> Load 1 -> Load 2 -> Perform); "
             "the other two stay fixed at the base prescription."
    )

    if progression_variable == "Reps/Sets":
        step = st.number_input("Step — extra reps per week", min_value=0, value=1, step=1)
    elif progression_variable == "Intensity":
        step = st.number_input("Step — extra % per week", min_value=0.0, value=3.0, step=0.5)
    else:  # Volume/Duration
        unit_label = "seconds" if metric_mode == "Time" else "metres"
        step = st.number_input(f"Step — extra {unit_label} per week", min_value=0.0, value=15.0 if metric_mode == "Time" else 50.0, step=5.0)

    st.divider()
    if st.button("🎯 Build Conditioning Session", type="primary"):
        if not mas_ms:
            st.error("Enter a valid 1200m time first.")
        elif not protocol_choice:
            st.error(f"No protocols defined yet for {prog_type}.")
        else:
            protocol = RUNNING_PROTOCOLS[prog_type][protocol_choice]
            if protocol["intensity_type"] == "ASR" and not asr_ms:
                st.error("This protocol needs a max sprint speed to calculate %ASR targets.")
            else:
                header = [
                    f"CONDITIONING BLOCK: {mode} | {prog_type} ({protocol_choice})",
                    f"Plan by: {metric_mode} | Progressing: {progression_variable} (step {step})",
                    f"MAS: {mas_ms:.2f} m/s ({speed_to_kmh(mas_ms):.1f} km/h, {speed_to_pace_per_km(mas_ms)})",
                ]
                if asr_ms is not None:
                    header.append(
                        f"Max Speed: {vmax_ms:.2f} m/s ({speed_to_kmh(vmax_ms):.1f} km/h) | "
                        f"ASR: {asr_ms:.2f} m/s ({speed_to_kmh(asr_ms):.1f} km/h)"
                    )
                header.append("=" * 60)
                body = render_session(protocol, metric_mode, progression_variable, step, mas_ms, asr_ms)
                session_text = "\n".join(header) + body
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

with tab_protocols:
    st.header("📈 Conditioning Protocol Library")

    view_focus = st.radio("View Programme Focus", ["Capacity", "Output", "Repeatability"], horizontal=True)
    current_data = RUNNING_PROTOCOLS.get(view_focus, {})

    if not current_data:
        st.warning("No protocols found for this focus.")
    else:
        for name, proto in current_data.items():
            with st.expander(f"📘 {name}", expanded=True):
                st.dataframe(
                    [{
                        "Reps": proto["reps"],
                        "Effort": f"{proto['effort_s']}s",
                        "Rest": f"{proto['rest_s']}s",
                        "Intensity": f"{proto['intensity_pct']}% {proto['intensity_type']}",
                    }],
                    use_container_width=True,
                    hide_index=True,
                )
