import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cycling Data", page_icon="🚴")

st.title("🚴 Cycling Analytics")
st.write("This is a separate page running on the same server!")

# Example: Upload a file
uploaded_file = st.file_uploader("Upload your Strava GPX/CSV", type=['csv', 'gpx'])