import streamlit as st
import random
import json
import os
import re

# --- 1. CONFIGURATION & FILE MANAGEMENT ---
APP_VERSION = "v7.0"
st.set_page_config(page_title=f"Strength Programme Builder {APP_VERSION}", layout="wide", page_icon="🏋️")

EXERCISE_FILE = "exercises.json"
PROTOCOL_FILE = "protocols.json"
 
# --- 2. DEFAULT DATA ---
DEFAULT_EXERCISES = [
    # --- TOTAL BODY: OLYMPIC / POWER (Primary) ---
    {"name": "Med Ball Slam", "level": 1, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "High Velocity", "tags": ["Plyo", "Power"]},
    {"name": "DB Thruster", "level": 1, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "High Velocity", "tags": ["Plyo", "Power", "Push"]},
    {"name": "BB Thruster", "level": 2, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "High Velocity", "tags": ["Plyo", "Power", "Push"]},
    {"name": "Squat Jerk", "level": 3, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "High Velocity", "tags": ["Plyo", "Power", "Push"]},
    {"name": "Split Jerk", "level": 3, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "High Velocity", "tags": ["Plyo", "Power", "Push"]},
    {"name": "Kettlebell Swing", "level": 1, "tier": "Total Body", "type": "Secondary", "pattern": "Hinge", "stance": "Bilateral", "fv_zone": "Speed-Strength", "tags": ["Ham Dom", "Hinge"]},
    {"name": "DB Clean", "level": 1, "tier": "Total Body", "type": "Secondary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Speed-Strength", "tags": ["Explosive", "Power"]},
    {"name": "DB SA Snatch", "level": 1, "tier": "Total Body", "type": "Secondary", "pattern": "Power", "stance": "Unilateral", "fv_zone": "Speed-Strength", "tags": ["Explosive", "Power"]},
    {"name": "Hang Clean", "level": 2, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Strength-Speed", "tags": ["Explosive", "Pull"]},
    {"name": "Hang High Pull", "level": 2, "tier": "Total Body", "type": "Secondary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Strength-Speed", "tags": ["Explosive", "Pull"]},
    {"name": "Power Clean", "level": 3, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Strength-Speed", "tags": ["Explosive", "Pull"]},
    {"name": "Snatch Balance", "level": 2, "tier": "Total Body", "type": "Secondary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Strength-Speed", "tags": ["Explosive", "Pull"]},
    {"name": "Hang Snatch", "level": 3, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Strength-Speed", "tags": ["Explosive", "Pull"]},
    {"name": "Clean Complex", "level": 3, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Strength-Speed", "tags": ["Explosive", "Pull"]},
    {"name": "Snatch Complex", "level": 3, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Strength-Speed", "tags": ["Explosive", "Pull"]},
    {"name": "Snatch", "level": 3, "tier": "Total Body", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Strength-Speed", "tags": ["Explosive", "Pull"]},

    # --- TOTAL BODY: STRUCTURAL (Primary) ---
    {"name": "Sumo Deadlift", "level": 1, "tier": "Total Body", "type": "Primary", "pattern": "Hinge", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Pull", "Hinge"]},
    {"name": "Trap Bar Deadlift", "level": 2, "tier": "Total Body", "type": "Primary", "pattern": "Hinge", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Pull", "Hinge"]},
    {"name": "Deadlift", "level": 3, "tier": "Total Body", "type": "Primary", "pattern": "Hinge", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Pull", "Hinge"]},
    
    # --- TOTAL BODY: ASSISTANCE (Secondary) ---
    {"name": "Hip Hinge", "level": 1, "tier": "Total Body", "type": "Secondary", "pattern": "Hinge", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Ham Dom", "Pull"]},
    {"name": "SL RDL", "level": 2, "tier": "Total Body", "type": "Secondary", "pattern": "Hinge", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["Ham Dom", "Pull"]},
    {"name": "SL Goodmorning", "level": 2, "tier": "Total Body", "type": "Secondary", "pattern": "Hinge", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["Ham Dom", "Pull"]},
    {"name": "Barbell RDL", "level": 3, "tier": "Total Body", "type": "Secondary", "pattern": "Hinge", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Ham Dom", "Pull"]},
    {"name": "Goodmorning", "level": 3, "tier": "Total Body", "type": "Secondary", "pattern": "Hinge", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Ham Dom", "Pull"]},
    
    # --- CARRIES (Auxiliary) ---
    {"name": "DB Farmer Carry", "level": 1, "tier": "Total Body", "type": "Auxiliary", "pattern": "Carry", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Core", "Carry"]},
    {"name": "DB Suitcase Carry", "level": 1, "tier": "Total Body", "type": "Auxiliary", "pattern": "Carry", "stance": "Unilateral", "fv_zone": "Hypertrophy", "tags": ["Core", "Carry"]},
    {"name": "DB Waiter Carry", "level": 1, "tier": "Total Body", "type": "Auxiliary", "pattern": "Carry", "stance": "Unilateral", "fv_zone": "Hypertrophy", "tags": ["Core", "Carry"]},

    # --- PLYO (Mix of Primary/Secondary) ---
    {"name": "Box Jump", "level": 1, "tier": "Plyo", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "High Velocity", "tags": ["Plyo", "Knee Ext"]},
    {"name": "Broad Jump", "level": 2, "tier": "Plyo", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "High Velocity", "tags": ["Plyo", "Hinge"]},
    {"name": "Lateral Bound", "level": 2, "tier": "Plyo", "type": "Secondary", "pattern": "Power", "stance": "Unilateral", "fv_zone": "High Velocity", "tags": ["Plyo"]},
    {"name": "Depth Jump", "level": 3, "tier": "Plyo", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "High Velocity", "tags": ["Plyo", "Power"]},
    {"name": "Hurdle Hops", "level": 2, "tier": "Plyo", "type": "Secondary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "High Velocity", "tags": ["Plyo", "Power"]},
    {"name": "Trap Bar Jump", "level": 2, "tier": "Plyo", "type": "Primary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Speed-Strength", "tags": ["Plyo", "Power"]},
    {"name": "Weighted Box Jump", "level": 2, "tier": "Plyo", "type": "Secondary", "pattern": "Power", "stance": "Bilateral", "fv_zone": "Speed-Strength", "tags": ["Plyo", "Power"]},

    # --- LOWER BODY: PRIMARY ---
    {"name": "Goblet Squat", "level": 1, "tier": "Lower Body", "type": "Primary", "pattern": "Squat", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom", "Knee Ext"]},
    {"name": "Front Squat", "level": 3, "tier": "Lower Body", "type": "Primary", "pattern": "Squat", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom", "Knee Ext"]},
    {"name": "Back Squat", "level": 3, "tier": "Lower Body", "type": "Primary", "pattern": "Squat", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom", "Knee Ext"]},
    {"name": "Overhead Squat", "level": 3, "tier": "Lower Body", "type": "Primary", "pattern": "Squat", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom", "Overhead"]},

    # --- LOWER BODY: SECONDARY ---
    {"name": "Leg Press", "level": 1, "tier": "Lower Body", "type": "Secondary", "pattern": "Squat", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom"]},
    {"name": "BW Lunges", "level": 1, "tier": "Lower Body", "type": "Secondary", "pattern": "Lunge", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom", "Unilateral"]},
    {"name": "Loaded Lunges", "level": 2, "tier": "Lower Body", "type": "Secondary", "pattern": "Lunge", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom", "Unilateral"]},
    {"name": "RFE Split Squat", "level": 3, "tier": "Lower Body", "type": "Secondary", "pattern": "Lunge", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom", "Unilateral"]},
    {"name": "BW Step Ups", "level": 1, "tier": "Lower Body", "type": "Secondary", "pattern": "Lunge", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom", "Unilateral"]},
    {"name": "Loaded Step Ups", "level": 2, "tier": "Lower Body", "type": "Secondary", "pattern": "Lunge", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom", "Unilateral"]},
    {"name": "High Box Step Ups", "level": 3, "tier": "Lower Body", "type": "Secondary", "pattern": "Lunge", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["Quad Dom", "Unilateral"]},

    # --- UPPER BODY: PRIMARY ---
    {"name": "Push Ups", "level": 2, "tier": "Upper Body", "type": "Primary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Push", "Horizontal"]},
    {"name": "Assisted Push Ups", "level": 1, "tier": "Upper Body", "type": "Primary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Push", "Horizontal"]},
    {"name": "Loaded Push Ups", "level": 3, "tier": "Upper Body", "type": "Primary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Push", "Horizontal"]},
    {"name": "BB Bench Press", "level": 3, "tier": "Upper Body", "type": "Primary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Push", "Horizontal"]},
    {"name": "OHP", "level": 3, "tier": "Upper Body", "type": "Primary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Push", "Vertical"]},
    {"name": "Pull Ups", "level": 3, "tier": "Upper Body", "type": "Primary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Pull", "Vertical"]},
    {"name": "Chin Ups", "level": 2, "tier": "Upper Body", "type": "Primary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Pull", "Vertical"]},
    {"name": "BB Bench Rows", "level": 3, "tier": "Upper Body", "type": "Primary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Pull", "Horizontal"]},

    # --- UPPER BODY: SECONDARY ---
    {"name": "Plyo Push Up", "level": 2, "tier": "Upper Body", "type": "Secondary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "High Velocity", "tags": ["UB Push", "Power"]},
    {"name": "DB Incline Press", "level": 2, "tier": "Upper Body", "type": "Secondary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Push", "Horizontal"]},
    {"name": "Kneeling Landmine Press", "level": 1, "tier": "Upper Body", "type": "Secondary", "pattern": "Push", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["UB Push", "Vertical"]},
    {"name": "Seated DB Shoulder Press", "level": 2, "tier": "Upper Body", "type": "Secondary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Push", "Vertical"]},
    {"name": "Dips", "level": 2, "tier": "Upper Body", "type": "Secondary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Push", "Vertical"]},
    {"name": "Band / Cable Pull Down", "level": 1, "tier": "Upper Body", "type": "Secondary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Pull", "Vertical"]},
    {"name": "DB Row", "level": 1, "tier": "Upper Body", "type": "Secondary", "pattern": "Pull", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["UB Pull", "Horizontal"]},
    {"name": "Renegade Row", "level": 2, "tier": "Upper Body", "type": "Secondary", "pattern": "Pull", "stance": "Unilateral", "fv_zone": "Max Strength", "tags": ["UB Pull", "Horizontal"]},
    {"name": "Chest Supported Row", "level": 1, "tier": "Upper Body", "type": "Secondary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Pull", "Horizontal"]},
    {"name": "Seated Cable Row", "level": 1, "tier": "Upper Body", "type": "Secondary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Pull", "Horizontal"]},
    {"name": "Lat Pulldown", "level": 1, "tier": "Upper Body", "type": "Secondary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Max Strength", "tags": ["UB Pull", "Vertical"]},

    # --- ISO & ACCESSORY (Auxiliary) ---
    {"name": "Bicep Curl", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Arm"]},
    {"name": "Tricep Extension", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Arm"]},
    {"name": "Plank", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Anterior Core"]},
    {"name": "BW Sit Up", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Anterior Core"]},
    {"name": "Loaded Sit Up", "level": 2, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Anterior Core"]},
    {"name": "Sit Up and Throw", "level": 3, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Anterior Core"]},
    {"name": "Loaded Plank", "level": 2, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Anterior Core"]},
    {"name": "Supine Hold", "level": 2, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Anterior Core"]},
    {"name": "Loaded Supine Hold", "level": 3, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Anterior Core"]},
    {"name": "Supine Hold Anti Extension", "level": 3, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Anterior Core"]},
    {"name": "Kneeling Side Plank", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Unilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Lateral Core"]},
    {"name": "Prone Hold", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Posterior Core"]},
    {"name": "Band Rotations", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Core", "stance": "Unilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Rotational Core"]}, 
    {"name": "Ham Bridge", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Ham Dom"]},
    {"name": "Ham Curls", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Ham Dom"]},
    {"name": "Nordic Curls", "level": 1, "tier": "Iso", "type": "Secondary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Ham Dom"]},
    {"name": "Glute External Clams", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Push", "stance": "Unilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Glute"]},
    {"name": "Calf Raises", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Calf"]},
    {"name": "Adductor Step Ins", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Push", "stance": "Unilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Adductor"]},
    {"name": "Lateral Raises", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Push", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Shoulder"]},
    {"name": "Reverse Flies", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Shoulder"]},
    {"name": "Face Pull", "level": 1, "tier": "Iso", "type": "Auxiliary", "pattern": "Pull", "stance": "Bilateral", "fv_zone": "Hypertrophy", "tags": ["Iso", "Shoulder"]}
]

DEFAULT_PROTOCOLS = {
    "Accumulation": {
        "High_Volume": {"Base": "3x10 @ 60%", "Load 1": "3x10 @ 65%", "Load 2": "4x10 @ 65%", "De-Re-Load": "2x8 @ 55%", "Perform": "3x8 @ 70%", "De-load": "2x10 @ 50%"},
        "German_Volume_Training": {"Base": "10x10 @ 60% (Shock)", "Load 1": "10x10 @ 60% (Strict 60s Rest)", "Load 2": "10x10 @ 62.5% (Fail=Stop)", "De-Re-Load": "5x10 @ 60%", "Perform": "3x10 @ 70% (Recovery)", "De-load": "Rest"},
        "Triphasic_Eccentric": {"Base": "4x6 @ 70% (5s Down)", "Load 1": "4x5 @ 75% (5s Down)", "Load 2": "4x4 @ 80% (5s Down)", "De-Re-Load": "3x4 @ 60% (3s Down)", "Perform": "3x3 @ 85% (Fast)", "De-load": "3x5 @ 50%"},
        "Triphasic_Isometric": {"Base": "4x5 @ 72% (3s Pause)", "Load 1": "4x4 @ 77% (3s Pause)", "Load 2": "4x3 @ 82% (3s Pause)", "De-Re-Load": "3x3 @ 65% (No Pause)", "Perform": "3x2 @ 87% (Fast)", "De-load": "3x5 @ 50%"},
        "VAT_568": {"Base": "3x5 @ 72.5, 75, 77.5%", "Load 1": "3x6 @ 77.5%", "Load 2": "3x8 @ 77.5%", "De-Re-Load": "3x5 @ 77.5%", "Perform": "3x8 @ 77.5%", "De-load": "3x5 @ 62.5%"},
        "Juggernaut_10s": {"Base": "5x10 @ 60% (RPE 8)", "Load 1": "5x10 @ 67.5% (RPE 9)", "Load 2": "3x10 @ 75% (RPE 9.5)", "De-Re-Load": "3x10 @ 60%", "Perform": "AMRAP Set @ 75%", "De-load": "2x10 @ 50%"},
        "Cluster_Hypertrophy": {"Base": "3x(4+4+4) @ 70% [15s rest]", "Load 1": "3x(5+5+5) @ 70% [15s rest]", "Load 2": "4x(5+5+5) @ 70% [15s rest]", "De-Re-Load": "2x(4+4+4) @ 65%", "Perform": "3x(6+6+6) @ 70%", "De-load": "3x8 Straight Sets @ 60%"}
    },
    "Intensification": {
        "Classic_5x5": {"Base": "5x5 @ 70% (Linear)", "Load 1": "5x5 @ 72.5% (Linear)", "Load 2": "5x5 @ 75% (Linear)", "De-Re-Load": "3x5 @ 60%", "Perform": "5x5 @ 80% (Test)", "De-load": "3x5 @ 50%"},
        "Poliquin_Waves": {"Base": "2 Waves: 7,5,3 @ 70,75,80%", "Load 1": "2 Waves: 6,4,2 @ 75,80,85%", "Load 2": "2 Waves: 5,3,1 @ 80,85,90%", "De-Re-Load": "1 Wave: 5,3,1 @ 70,75,80%", "Perform": "Test Max", "De-load": "3x5 @ 50%"},
        "Texas_Method_Volume": {"Base": "5x5 @ 75% (Grind)", "Load 1": "5x5 @ 77.5% (Grind)", "Load 2": "5x5 @ 80% (Grind)", "De-Re-Load": "3x5 @ 70%", "Perform": "5RM Test", "De-load": "3x5 @ 50%"},
        "Baker_Wave": {
            "Base": "3 x 8 @ 60%", 
            "Load 1": "3 x 8,6,5 @ 60,65,70%", 
            "Load 2": "3 x 6,5,3 @ 65,72.5,77.5%", 
            "De-Re-Load": "3 x 8,6,5 @ 60,67.5,72.5%", 
            "Load 3": "3 x 6,5,3 @ 67.5,75,80%", 
            "Perform": "3 x 5,3,2 @ 75,82.5,87.5%"
        },
        "Wendler_531_Classic": {"Base": "5/5/5+ @ 65, 75, 85%", "Load 1": "3/3/3+ @ 70, 80, 90%", "Load 2": "5/3/1+ @ 75, 85, 95%", "De-Re-Load": "3x5 @ 60% (Deload)", "Perform": "TM Test: 3-5 reps @ 100% TM", "De-load": "3x5 @ 50%"},
        "Cluster_Strength": {"Base": "4x(1-1-1-1-1) @ 85% [20s rest]", "Load 1": "5x(1-1-1-1-1) @ 87% [20s rest]", "Load 2": "5x(1-1-1-1-1) @ 90% [20s rest]", "De-Re-Load": "3x(1-1-1) @ 80%", "Perform": "4x(1-1-1-1-1) @ 92% [30s rest]", "De-load": "3x3 Straight Sets @ 70%"}
    },
    "Realisation": {
         "Peaking": {"Base": "3x3 @ 80%", "Load 1": "3x2 @ 85%", "Load 2": "2x2 @ 90%", "Perform": "1RM Test", "De-Re-Load": "3x1 @ 80%", "De-load": "Rest"},
         "French_Contrast": {"Base": "4 Rnds: 2 Reps @ 80% + 3 Plyos", "Load 1": "4 Rnds: 2 Reps @ 85% + 3 Plyos", "Load 2": "3 Rnds: 1 Rep @ 90% + 2 Plyos", "De-Re-Load": "3 Rnds: 2 Reps @ 70% + 2 Plyos", "Perform": "Test / Compete", "De-load": "Rest"},
         "Dynamic_Effort_Speed": {"Base": "9x3 @ 50% + Bands (45s Rest)", "Load 1": "8x3 @ 55% + Bands (45s Rest)", "Load 2": "6x3 @ 60% + Bands (60s Rest)", "De-Re-Load": "6x2 @ 50% (Fast)", "Perform": "Test Velocity / Vertical Jump", "De-load": "Rest"},
         "Juggernaut_3s": {"Base": "7x3 @ 75% (RPE 8)", "Load 1": "8x3 @ 80% (RPE 9)", "Load 2": "5x3 @ 85% (RPE 9.5)", "Perform": "AMRAP Set @ 85% or 1RM", "De-Re-Load": "3x3 @ 60%", "De-load": "Rest"}
    }
}

# --- 3. ROBUST DATA LOADING (FIXED) ---
def load_data():
    # EXERCISES
    if not os.path.exists(EXERCISE_FILE):
        with open(EXERCISE_FILE, 'w') as f: json.dump(DEFAULT_EXERCISES, f, indent=4)
        exercises = DEFAULT_EXERCISES
    else:
        with open(EXERCISE_FILE, 'r') as f: exercises = json.load(f)
        
    # PROTOCOLS (WITH MERGE LOGIC)
    if not os.path.exists(PROTOCOL_FILE):
        with open(PROTOCOL_FILE, 'w') as f: json.dump(DEFAULT_PROTOCOLS, f, indent=4)
        protocols = DEFAULT_PROTOCOLS
    else:
        with open(PROTOCOL_FILE, 'r') as f: protocols = json.load(f)
        
        # MERGE LOGIC: Force code defaults into existing file
        updated = False
        for phase, data in DEFAULT_PROTOCOLS.items():
            if phase not in protocols:
                protocols[phase] = data
                updated = True
            else:
                for scheme_name, scheme_data in data.items():
                    if scheme_name not in protocols[phase]:
                        protocols[phase][scheme_name] = scheme_data
                        updated = True
        
        if updated:
            with open(PROTOCOL_FILE, 'w') as f: json.dump(protocols, f, indent=4)
            
    return exercises, protocols

def save_exercises(data):
    with open(EXERCISE_FILE, 'w') as f: json.dump(data, f, indent=4)

def save_protocols(data):
    with open(PROTOCOL_FILE, 'w') as f: json.dump(data, f, indent=4)

master_exercises, t1_schemes = load_data()

# --- 4. SESSION STATE INIT ---
# --- 4. SESSION STATE INIT ---
if 'cycle_count' not in st.session_state: st.session_state.cycle_count = 1
if 'previous_t1' not in st.session_state: st.session_state.previous_t1 = None
if 'history_text' not in st.session_state: st.session_state.history_text = [] 
if 'draft_plan' not in st.session_state: st.session_state.draft_plan = None
if 'accessory_progression' not in st.session_state:
    st.session_state.accessory_progression = {"T2": 0, "T3": 0, "T4": 0}

# --- 5. STATIC DEFINITIONS ---
style_map = {
    "Agonist : Antagonist": {"UB Push": "UB Pull", "UB Pull": "UB Push", "Quad Dom": "Ham Dom", "Ham Dom": "Quad Dom", "Power": "Plyo", "Explosive": "Plyo"},
    "Compound : Isolation": {"UB Push": "Iso", "UB Pull": "Iso", "Quad Dom": "Iso", "Ham Dom": "Iso", "Total Body": "Iso"},
    "Strength : Power": {"Explosive": "Plyo", "Quad Dom": "Plyo", "Ham Dom": "Plyo", "Total Body": "Plyo"}
}

tier_defaults = {
    "Accumulation": {
        "T2": "3x12", 
        "T3": "3x15", 
        "T4": "3 Sets (Quality)", 
        "Iso_Time": "3x30s",    # NEW
        "Core_Time": "3x30s",   # NEW
        "Carry_Dist": "3x20m"   # NEW
    }, 
    "Intensification": {
        "T2": "3x8", 
        "T3": "3x10", 
        "T4": "3 Sets (Heavy)", 
        "Iso_Time": "3x20s (Weighted)", 
        "Core_Time": "3x20s (Weighted)",
        "Carry_Dist": "3x30m"
    }, 
    "Realisation": {
        "T2": "3x5", 
        "T3": "3x8", 
        "T4": "2 Sets (Speed/Iso)", 
        "Iso_Time": "3x10s (Max Effort)", 
        "Core_Time": "3x15s",
        "Carry_Dist": "3x15m (Heavy)"
    }
}

flow_definitions = {
    3: ["Load 1", "Load 2", "Perform"],
    4: ["Base", "Load 1", "Load 2", "Perform"],
    5: ["Base", "Load 1", "Load 2", "De-Re-Load", "Perform"],
    6: ["Base", "Load 1", "Load 2", "De-Re-Load", "Perform", "De-load"]
}

special_flows = {
    "Baker_Wave": ["Base", "Load 1", "Load 2", "De-Re-Load", "Load 3", "Perform"]
}

default_rotation = [
    {"T1": "Total Body", "T2": "Lower Body", "T3": "Upper Body", "T4": "Iso"},
    {"T1": "Lower Body", "T2": "Upper Body", "T3": "Total Body", "T4": "Iso"},
    {"T1": "Upper Body", "T2": "Total Body", "T3": "Lower Body", "T4": "Iso"}
]

# --- 6. LOGIC FUNCTIONS ---
def get_ex_by_name(name):
    for ex in master_exercises:
        if ex["name"] == name: return ex
    return {"name": name, "tags": [], "pattern": "None", "stance": "None", "type": "None", "tier": "None"}

def get_smart_ex(tier=None, required_tag=None, required_pattern=None, required_type=None, level=1, exclude_names=None, exclude_stance=None, exclude_pattern=None, fuzzy_exclude=None, force_tier=None):
    if exclude_names is None: exclude_names = []

    # fuzzy_exclude now takes an exercise NAME (e.g. T1's primary name) and
    # blocks candidates that share the same movement pattern, so "Front Squat"
    # as T1 won't let "Back Squat" slip in as T2, etc.
    fuzzy_exclude_pattern = None
    if fuzzy_exclude:
        fuzzy_ex_obj = get_ex_by_name(fuzzy_exclude)
        fuzzy_exclude_pattern = fuzzy_ex_obj.get("pattern")

    # 1. GATHER CANDIDATES
    candidates = []
    for ex in master_exercises:
        # Basic Safety: Never show exercises higher than user level
        if ex["level"] > level: continue
        
        if ex["name"] in exclude_names: continue
        if tier and ex["tier"] != tier: continue
        if force_tier and ex["tier"] != force_tier: continue
        if required_tag and required_tag not in ex["tags"]: continue
        
        ex_stance = ex.get("stance", "Bilateral") 
        ex_pattern = ex.get("pattern", "None")
        ex_type = ex.get("type", "Auxiliary") 
        
        # Hierarchy Filter
        if required_type:
            if isinstance(required_type, list):
                if ex_type not in required_type: continue
            elif ex_type != required_type:
                continue

        # Attribute Filters
        if required_pattern and ex_pattern != required_pattern: continue
        if exclude_stance and ex_stance == exclude_stance: continue
        if exclude_pattern and ex_pattern == exclude_pattern: continue

        # Movement-pattern exclude (replaces old word-matching fuzzy logic)
        if fuzzy_exclude_pattern and ex_pattern == fuzzy_exclude_pattern:
            continue
        
        candidates.append(ex)

    # 2. SELECTION LOGIC
    if candidates:
        # --- STRICT TIER 1 LOGIC ---
        # If this is a Primary (T1) slot, enforce strict level matching.
        if required_type == "Primary":
            # Try to find exercises that MATCH the athlete level exactly.
            strict_matches = [ex for ex in candidates if ex["level"] == level]
            
            if strict_matches:
                return random.choice(strict_matches)
            
            # EDGE CASE: If no strict match exists (e.g., Level 3 user, but DB only has Level 2 for this pattern),
            # try one level down.
            backup_matches = [ex for ex in candidates if ex["level"] == level - 1]
            if backup_matches:
                return random.choice(backup_matches)

        # --- RELAXED LOGIC (T2, T3, T4) ---
        # For non-primary tiers, allow any exercise up to the user's level.
        # Ideally prefer higher level exercises if available, but mix is fine.
        return random.choice(candidates)
    
    # 3. LAST RESORT (Recovery)
    return {"name": "Recovery/Mobility", "tags": []}

def calculate_weight(protocol_str, one_rm, tm_percentage=100, rounding=2.5):
    if not one_rm: return protocol_str
    tm = one_rm * (tm_percentage / 100.0)

def apply_progression(scheme_str, offset):
    """Shift the rep/time/distance number in a T2-T4 scheme string by `offset`
    reps, leaving sets and any suffix untouched. Never drops below 1."""
    if offset == 0:
        return scheme_str

    def replacer(match):
        sets = match.group(1)
        reps = int(match.group(2))
        new_reps = max(1, reps + offset)
        return f"{sets}x{new_reps}"

    return re.sub(r'(\d+)\s*x\s*(\d+)', replacer, scheme_str, count=1)

    def replace_group(match):
        nums = re.findall(r"\d+(?:\.\d+)?", match.group(0))
        out = []
        for n in nums:
            w = tm * (float(n) / 100.0)
            rw = round(w / rounding) * rounding
            out.append(f"{int(rw) if rw % 1 == 0 else rw}kg")
        return ",".join(out)

    # Matches a run of comma-separated numbers that ends in a single trailing %
    # e.g. "65, 75, 85%" -> "162.5kg,187.5kg,212.5kg"
    return re.sub(r"\d+(?:\.\d+)?(?:\s*,\s*\d+(?:\.\d+)?)*%", replace_group, protocol_str)

# --- 7. UI STRUCTURE ---
st.title(f"🏋️ Strength Programme Builder {APP_VERSION}")
with st.sidebar:
    st.write("🔧 **Tools**")
    if st.button("🗑️ Reset All Data (Use if buggy)"):
        if os.path.exists(EXERCISE_FILE): os.remove(EXERCISE_FILE)
        if os.path.exists(PROTOCOL_FILE): os.remove(PROTOCOL_FILE)
        st.session_state.clear()
        st.rerun()

tab_builder, tab_db, tab_protocols, tab_calc = st.tabs(["🏗️ Program Builder", "📚 Exercise Database", "📈 Protocol Library", "🧮 Load Calculator"])

# ==========================================
# TAB 1: PROGRAM BUILDER
# ==========================================
with tab_builder:
    col_l, col_r = st.columns([1, 2])
    
    with col_l:
        st.subheader("1. Configuration")
        st.caption(f"Cycle #{st.session_state.cycle_count}")
        prog = st.session_state.accessory_progression
        st.caption(f"Accessory volume offset — T2: {prog['T2']:+d} | T3: {prog['T3']:+d} | T4: {prog['T4']:+d}")
        
        user_level = st.selectbox("Athlete Level", [1, 2, 3], index=1)
        phase_input = st.selectbox("Phase", ["Accumulation", "Intensification", "Realisation"])
        
        avail_protocols = list(t1_schemes.get(phase_input, {}).keys())
        protocol_choice = st.selectbox("Protocol", avail_protocols) if avail_protocols else "Default"
        
        is_override = protocol_choice in special_flows
        
        if is_override:
            st.info(f"🔒 Duration locked by **{protocol_choice}** protocol.")
            current_flow_weeks = special_flows[protocol_choice]
            weeks = len(current_flow_weeks)
        else:
            weeks = st.slider("Duration (Weeks)", 3, 6, 4)
            current_flow_weeks = flow_definitions.get(weeks)

        active_scheme = {}
        # Only show customizer if not Default
        if protocol_choice != "Default":
            default_scheme = t1_schemes[phase_input][protocol_choice]
            with st.expander("✏️ Customize Rep Scheme", expanded=False):
                st.caption("Edit sets/reps below:")
                for wk_label in current_flow_weeks:
                    def_val = default_scheme.get(wk_label, "3x5")
                    new_val = st.text_input(f"{wk_label}", value=def_val, key=f"cust_{protocol_choice}_{wk_label}")
                    active_scheme[wk_label] = new_val

        st.divider()
        st.subheader("2. Override & Logic")
        
        use_fixed_t1 = False
        override_ex = {}

        if st.session_state.previous_t1:
            use_fixed_t1 = st.checkbox(f"Keep Previous T1s ({', '.join(st.session_state.previous_t1)})", value=True)
        
        with st.expander("Override Specific Slots"):
            for i, day in enumerate(["Day 1", "Day 2", "Day 3"]):
                st.markdown(f"**{day}**")
                c1, c2 = st.columns(2)
                t1_force = c1.selectbox(f"{day} T1 Override", ["Auto"] + [e["name"] for e in master_exercises if e["tier"] == default_rotation[i]["T1"]], key=f"force_t1_{i}")
                if t1_force != "Auto": override_ex[f"S{i}_T1"] = t1_force
                
                t2_force = c2.selectbox(f"{day} T2 Override", ["Auto"] + [e["name"] for e in master_exercises if e["tier"] == default_rotation[i]["T2"]], key=f"force_t2_{i}")
                if t2_force != "Auto": override_ex[f"S{i}_T2"] = t2_force

        st.subheader("3. Pairing Logic")
        active_pair_map = {}
        with st.expander("Configure Pairings", expanded=False):
            entities = ["T1", "T2", "T3", "Total Body", "Lower Body", "Upper Body"]
            styles = ["None", "Agonist : Antagonist", "Compound : Isolation", "Strength : Power", "French Contrast (Tri)", "French Contrast (Quad)"]
            for i in range(3):
                c1, c2 = st.columns([1, 2])
                e = c1.selectbox(f"Target {i+1}", ["-"] + entities, key=f"pe_{i}")
                s = c2.selectbox(f"Style {i+1}", styles, key=f"ps_{i}")
                if e != "-" and s != "None": active_pair_map[e] = s

        if st.button("🎲 Create Draft Program", type="primary"):
            st.session_state.draft_plan = [] 
            temp_used = []
            
            for i, template in enumerate(default_rotation):
                session_data = {"meta": template}
                t1_attributes = {"stance": None, "pattern": None, "name": None, "tier": None}
                
                for tier_key in ["T1", "T2", "T3", "T4"]:
                    tier_group = template.get(tier_key, "Iso")
                    
                    slot_id = f"S{i}_{tier_key}"
                    if slot_id in override_ex:
                        primary_ex = get_ex_by_name(override_ex[slot_id])
                    elif tier_key == "T1" and use_fixed_t1 and st.session_state.previous_t1:
                        primary_ex = get_ex_by_name(st.session_state.previous_t1[i])
                    else:
                        avoid_stance = None
                        avoid_pattern = None
                        req_pat = None
                        req_type = None 
                        
                        fuzzy_bad = t1_attributes["name"] if tier_key == "T2" else None 
                        
                        if tier_key == "T1":
                            req_type = "Primary"
                        elif tier_key == "T2":
                            req_type = "Secondary"
                            if t1_attributes["stance"] == "Unilateral": avoid_stance = "Unilateral"
                            if t1_attributes["pattern"]: avoid_pattern = t1_attributes["pattern"]
                        elif tier_key == "T3":
                            req_type = ["Secondary", "Auxiliary"]
                        elif tier_key == "T4":
                            req_pat = "Core"
                            req_type = ["Auxiliary"]

                        primary_ex = get_smart_ex(tier=tier_group, required_type=req_type, required_pattern=req_pat, level=user_level, exclude_names=temp_used, exclude_stance=avoid_stance, exclude_pattern=avoid_pattern, fuzzy_exclude=fuzzy_bad)

                    if tier_key == "T1":
                        t1_attributes["stance"] = primary_ex.get("stance")
                        t1_attributes["pattern"] = primary_ex.get("pattern")
                        t1_attributes["name"] = primary_ex.get("name")
                        t1_attributes["tier"] = primary_ex.get("tier")
                    
                    if primary_ex["name"] not in temp_used: temp_used.append(primary_ex["name"])
                    
                    style_by_key = active_pair_map.get(tier_key)
                    style_by_group = active_pair_map.get(tier_group)
                    if style_by_key and style_by_group and style_by_key != style_by_group:
                        st.warning(
                            f"Session {i+1} {tier_key} ({tier_group}): both a '{tier_key}' pairing "
                            f"style and a '{tier_group}' pairing style are set ('{style_by_key}' vs "
                            f"'{style_by_group}'). Using '{style_by_key}'."
                        )
                    style = style_by_key or style_by_group
                    aux_list = [] 
                    
                    if style and tier_key != "T4":
                        # FRENCH CONTRAST
                        if "French Contrast" in style:
                            required_count = 2 if "(Tri)" in style else 3
                            for _ in range(required_count):
                                partner_ex = get_smart_ex(required_tag="Plyo", level=user_level, exclude_names=temp_used)
                                if partner_ex["name"] == "Recovery/Mobility":
                                     partner_ex = get_smart_ex(required_tag="Power", level=user_level, exclude_names=temp_used)
                                aux_list.append(partner_ex["name"])
                                temp_used.append(partner_ex["name"])
                        else:
                            # STANDARD PAIRING
                            partner_tag = None
                            pair_force_tier = None 

                            for tag in primary_ex["tags"]:
                                if tag in style_map.get(style, {}):
                                    partner_tag = style_map[style][tag]
                                    break
                            
                            # Fallback Logic
                            if not partner_tag and style == "Compound : Isolation": partner_tag = "Iso"
                            
                            # Strength : Power Logic (Strict Tier Matching)
                            if style == "Strength : Power": 
                                partner_tag = "Power"
                                # Match Pairing Tier to Primary Tier to avoid Leg Jumps with Arm Press
                                if t1_attributes["tier"] == "Upper Body": 
                                    pair_force_tier = "Upper Body" 
                                elif t1_attributes["tier"] == "Lower Body":
                                    pair_force_tier = "Plyo" 
                                elif t1_attributes["tier"] == "Total Body":
                                    pair_force_tier = "Plyo"

                            # Agonist : Antagonist Fix
                            if style == "Agonist : Antagonist":
                                # LOGIC FIX: Match the tier of the CURRENT exercise, NOT T1
                                pair_force_tier = primary_ex["tier"] 
                                if "Push" in primary_ex["tags"]: partner_tag = "Pull" 
                                elif "Pull" in primary_ex["tags"]: partner_tag = "Push" 
                                if "UB Push" in primary_ex["tags"]: partner_tag = "UB Pull"
                                if "UB Pull" in primary_ex["tags"]: partner_tag = "UB Push"

                            partner_ex = get_smart_ex(required_tag=partner_tag, level=user_level, exclude_names=temp_used, force_tier=pair_force_tier)
                            
                            if partner_ex["name"] != "Recovery/Mobility":
                                aux_list.append(partner_ex["name"])
                                temp_used.append(partner_ex["name"])

                    session_data[tier_key] = {
                        "primary": primary_ex["name"],
                        "aux_list": aux_list, 
                        "style": style
                    }
                st.session_state.draft_plan.append(session_data)
            st.rerun()

    with col_r:
        if st.session_state.draft_plan:
            st.subheader("📝 Review & Edit Draft")
            st.info("You can change any exercise below before finalizing.")
            
            finalized_plan = []
            
            with st.form("draft_editor"):
                for s_idx, session in enumerate(st.session_state.draft_plan):
                    st.markdown(f"### Session {s_idx + 1}")
                    cols = st.columns(4)
                    tier_keys = ["T1", "T2", "T3", "T4"]
                    
                    updated_session = {}
                    
                    for t_idx, t_key in enumerate(tier_keys):
                        data = session[t_key]
                        group = session["meta"].get(t_key, "Iso")
                        
                        with cols[t_idx]:
                            st.caption(f"**{t_key} ({group})**")
                            
                            options = [e["name"] for e in master_exercises if e["tier"] == group]
                            if t_key == "T4":
                                options = [e["name"] for e in master_exercises if e["pattern"] == "Core" or e["tier"] == "Iso"]

                            if data["primary"] not in options: options.append(data["primary"])
                            
                            new_primary = st.selectbox(
                                f"Main", 
                                options, 
                                index=options.index(data["primary"]), 
                                key=f"s{s_idx}_{t_key}_p"
                            )
                            
                            new_aux_list = []
                            if data["aux_list"]:
                                aux_options = [e["name"] for e in master_exercises] 
                                for i, aux_ex in enumerate(data["aux_list"]):
                                    curr_opts = list(aux_options)
                                    if aux_ex not in curr_opts: curr_opts.append(aux_ex)
                                    val = st.selectbox(f"Aux {i+1}", curr_opts, index=curr_opts.index(aux_ex), key=f"s{s_idx}_{t_key}_aux_{i}")
                                    new_aux_list.append(val)
                            
                            updated_session[t_key] = {
                                "primary": new_primary,
                                "aux_list": new_aux_list,
                                "style": data["style"]
                            }
                    finalized_plan.append(updated_session)
                
                st.divider()
                submitted = st.form_submit_button("✅ Finalize & Build Program")

            if submitted:
                if is_override:
                    week_sequence = special_flows[protocol_choice]
                else:
                    week_sequence = flow_definitions.get(weeks)

                prog = [f"BLOCK #{st.session_state.cycle_count}: {len(week_sequence)} Wks | {phase_input} ({protocol_choice})", "="*60]
                curr_t1s = []
                letters = ['a', 'b', 'c', 'd', 'e'] 
                
                for wk_idx, wk_label in enumerate(week_sequence):
                    prog.append(f"\nWEEK {wk_idx + 1}: {wk_label.upper()}\n" + "-" * 30)
                    for i, session in enumerate(finalized_plan):
                        prog.append(f"SESSION {i+1}:")
                        
                        if wk_idx == 0: curr_t1s.append(session["T1"]["primary"])

                        for t in ["T1", "T2", "T3", "T4"]:
                            d = session[t]
                            
                            # --- 1. DETERMINE SCHEME ---
                            sch = "3 Sets" # Fallback
                            
                            # T1 Logic (Protocol Based)
                            if t == "T1":
                                if wk_label in active_scheme:
                                    sch = active_scheme[wk_label]
                                else:
                                    try:
                                        sch = t1_schemes[phase_input][protocol_choice][wk_label]
                                    except KeyError:
                                        sch = "3x5"
                            
                            # T2/T3/T4 Logic (Default Based)
                                else:
                                main_ex_obj = get_ex_by_name(d['primary'])
                                tags = main_ex_obj.get("tags", [])
                                pattern = main_ex_obj.get("pattern", "None")
                                
                                if pattern == "Carry" or "Carry" in tags:
                                    base_sch = tier_defaults.get(phase_input, {}).get("Carry_Dist", "3x20m")
                                elif "Iso" in tags or "Core" in tags or pattern == "Core":
                                    base_sch = tier_defaults.get(phase_input, {}).get("Core_Time", "3x30s")
                                else:
                                    base_sch = tier_defaults.get(phase_input, {}).get(t, "3 Sets")
                                
                                offset = st.session_state.accessory_progression.get(t, 0)
                                sch = apply_progression(base_sch, offset)

                            # --- 2. WRITE TO PROGRAM ---
                            if d["aux_list"]:
                                # Primary Line
                                prog.append(f"  {t}a: {d['primary'].ljust(22)} | {sch} ({d.get('style')})")
                                
                                # Aux Lines
                                for idx, aux in enumerate(d["aux_list"]):
                                    let = letters[idx+1]
                                    
                                    # Check Aux exercise for special handling too (e.g., Plank as super set)
                                    aux_obj = get_ex_by_name(aux)
                                    aux_tags = aux_obj.get("tags", [])
                                    aux_pattern = aux_obj.get("pattern", "None")
                                    
                                    aux_sch = sch # Default to matching the main lift
                                    
                                    # If Aux is Core/Iso/Carry, give it time/distance instead of reps
                                    aux_offset = st.session_state.accessory_progression.get(t, 0)
                                    if aux_pattern == "Carry" or "Carry" in aux_tags:
                                        aux_sch = apply_progression(tier_defaults.get(phase_input, {}).get("Carry_Dist", "3x20m"), aux_offset)
                                    elif "Iso" in aux_tags or "Core" in aux_tags or aux_pattern == "Core":
                                        aux_sch = apply_progression(tier_defaults.get(phase_input, {}).get("Core_Time", "3x30s"), aux_offset)
                                        
                                    prog.append(f"  {t}{let}: {aux.ljust(22)} | {aux_sch}")
                            else:
                                prog.append(f"  {t} : {d['primary'].ljust(22)} | {sch}")

                st.session_state.history_text.append("\n".join(prog))
                st.session_state.previous_t1 = curr_t1s
                st.session_state.cycle_count += 1

                # Progress T2/T3/T4 volume for the NEXT block built:
                # Accumulation -> reps go up next time, Intensification/Realisation -> reps go down
                direction = 1 if phase_input == "Accumulation" else -1
                for tier_key in ["T2", "T3", "T4"]:
                    st.session_state.accessory_progression[tier_key] += direction

                st.session_state.draft_plan = None
                st.success("Program Built! Scroll down to History.")
                st.rerun()

        if st.session_state.history_text:
            st.divider()
            st.subheader("📜 Program History")
            st.download_button("Download All", "\n\n".join(st.session_state.history_text), "Macrocycle.txt")
            for idx, block in enumerate(reversed(st.session_state.history_text)):
                with st.expander(f"Block History", expanded=(idx==0)): st.text(block)

# ==========================================
# TAB 2: EXERCISE DATABASE
# ==========================================
with tab_db:
    st.header("📚 Master Exercise Library")
    
    with st.expander("➕ Add New Exercise", expanded=False):
        with st.form("add_ex_form"):
            c1, c2, c3 = st.columns([2, 1, 1])
            new_name = c1.text_input("Name")
            new_lvl = c2.selectbox("Level", [1, 2, 3])
            new_tier = c3.selectbox("Tier", ["Total Body", "Lower Body", "Upper Body", "Plyo", "Iso"])
            
            c4, c5, c6 = st.columns(3)
            new_pattern = c4.selectbox("Pattern", ["Squat", "Hinge", "Lunge", "Push", "Pull", "Power", "Carry", "Core", "None"])
            new_stance = c5.selectbox("Stance", ["Bilateral", "Unilateral", "Staggered", "None"])
            new_type = c6.selectbox("Hierarchy", ["Primary", "Secondary", "Auxiliary"])
            
            new_tags = st.multiselect("Tags", [
                "Plyo", "Power", "Explosive", "Pull", "Hinge", "Ham Dom", "Quad Dom", "Knee Ext", 
                "Unilateral", "UB Push", "UB Pull", "Horizontal", "Vertical", "Iso",
                "Core", "Carry", "Anterior Core", "Lateral Core", "Posterior Core", "Rotational Core",
                "Glute", "Calf", "Adductor", "Arm", "Shoulder", "Overhead"
            ])
            
            if st.form_submit_button("Add Exercise"):
                if new_name:
                    existing_names = [e["name"].strip().lower() for e in master_exercises]
                    if new_name.strip().lower() in existing_names:
                        st.error(f"'{new_name}' already exists in the database. Edit or rename it instead of adding a duplicate.")
                    else:
                        master_exercises.append({
                            "name": new_name, 
                            "level": new_lvl, 
                            "tier": new_tier, 
                            "pattern": new_pattern, 
                            "stance": new_stance, 
                            "type": new_type,
                            "fv_zone": "None", 
                            "tags": new_tags
                        })
                        save_exercises(master_exercises)
                        st.success(f"Added {new_name}")
                        st.rerun()

    st.divider()
    
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    s_term = c1.text_input("🔍 Search DB")
    f_tier = c2.multiselect("Filter Tier", ["Total Body", "Lower Body", "Upper Body", "Plyo", "Iso"])
    f_pattern = c3.selectbox("Filter Pattern", ["All", "Squat", "Hinge", "Lunge", "Push", "Pull", "Power", "Carry", "Core"])
    f_type = c4.selectbox("Filter Hierarchy", ["All", "Primary", "Secondary", "Auxiliary"])

    display_data = []
    for ex in master_exercises:
        if s_term and s_term.lower() not in ex["name"].lower(): continue
        if f_tier and ex["tier"] not in f_tier: continue
        if f_pattern != "All" and ex.get("pattern") != f_pattern: continue
        if f_type != "All" and ex.get("type") != f_type: continue
        
        display_data.append({
            "Name": ex["name"], 
            "Type": ex.get("type", "-"),
            "Pattern": ex.get("pattern", "-"), 
            "Stance": ex.get("stance", "-"),
            "Tags": ", ".join(ex["tags"])
        })
    
    st.dataframe(display_data, use_container_width=True, hide_index=True)

# ==========================================
# TAB 3: PROTOCOLS
# ==========================================
with tab_protocols:
    st.header("📈 Protocol Library")
    
    with st.expander("➕ Add New Protocol"):
        with st.form("add_proto"):
            pp = st.selectbox("Phase", ["Accumulation", "Intensification", "Realisation"])
            pn = st.text_input("Name")
            c1, c2, c3 = st.columns(3)
            b = c1.text_input("Wk1 (Base)", "3x5 @ 70%")
            l1 = c2.text_input("Wk2 (Load 1)", "3x5 @ 75%")
            l2 = c3.text_input("Wk3 (Load 2)", "4x4 @ 80%")
            
            c4, c5, c6 = st.columns(3)
            l3 = c4.text_input("Wk4 (Load 3 / Opt)", "-") 
            p = c5.text_input("Wk5 (Perform)", "3x3 @ 85%")
            drl = c6.text_input("De-Re-Load", "Deload")
            
            dl = st.text_input("Final Deload", "Deload")
            
            if st.form_submit_button("Add"):
                if pn:
                    if pp not in t1_schemes: t1_schemes[pp] = {}
                    new_proto = {
                        "Base": b, "Load 1": l1, "Load 2": l2, 
                        "Perform": p, "De-Re-Load": drl, "De-load": dl
                    }
                    if l3 and l3 != "-":
                        new_proto["Load 3"] = l3
                        
                    t1_schemes[pp][pn] = new_proto
                    save_protocols(t1_schemes)
                    st.rerun()

    st.divider()
    
    view_phase = st.radio("View Phase", ["Accumulation", "Intensification", "Realisation"], horizontal=True)
    current_data = t1_schemes.get(view_phase, {})
    
    if not current_data:
        st.warning("No protocols found. Please delete 'protocols.json' to reset defaults.")
    else:
        for name, data in current_data.items():
            with st.expander(f"📘 {name}", expanded=True):
                st.dataframe([data], use_container_width=True, hide_index=True)

# ==========================================
# TAB 4: LOAD CALCULATOR
# ==========================================
with tab_calc:
    st.header("🧮 1RM Load Calculator")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("Reference: 1RM Chart")
        ref_data = {
            "Reps": [1, 2, 3, 4, 5, 6, 8, 10, 12],
            "%1RM": ["100%", "95%", "93%", "90%", "87%", "85%", "80%", "75%", "70%"]
        }
        st.table(ref_data)
        
    with c2:
        st.subheader("Input Data")
        ex_name = st.text_input("Exercise Name (e.g., Squat)")
        one_rm = st.number_input("One Rep Max (1RM)", value=100.0, step=2.5)
        tm_pct = st.number_input("Training Max % (Default 100, Wendler 90)", value=100, step=5)
        rounding = st.number_input("Round to nearest", value=2.5, step=0.5)
        
    with c3:
        st.subheader("Select Protocol")
        calc_phase = st.selectbox("Calc Phase", ["Accumulation", "Intensification", "Realisation"], key="c_ph")
        calc_protos = list(t1_schemes.get(calc_phase, {}).keys())
        calc_choice = st.selectbox("Calc Protocol", calc_protos, key="c_pr")
    
    st.divider()
    
    if st.button("🚀 Calculate Weights", type="primary"):
        if calc_choice:
            st.success(f"Generated Loads for **{ex_name}** (1RM: {one_rm})")
            
            raw_proto = t1_schemes[calc_phase][calc_choice]
            calculated_data = []
            order = ["Base", "Load 1", "Load 2", "Load 3", "De-Re-Load", "Perform", "De-load"]
            
            for key in order:
                if key in raw_proto:
                    original_str = raw_proto[key]
                    new_str = calculate_weight(original_str, one_rm, tm_pct, rounding)
                    calculated_data.append({"Week": key, "Protocol": new_str})
            
            st.dataframe(calculated_data, use_container_width=True, hide_index=True)
            st.caption(f"Training Max used: {one_rm * (tm_pct/100)} kg/lbs")
