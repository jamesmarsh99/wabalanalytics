import streamlit as st
import random
from pathlib import Path

WABILI_ICON = str(Path(fr"C:\Users\James\Documents\codingProjects\wabalanalytics\data\wabiliIcon.png"))

st.set_page_config(
    page_title="TAnalytics",
    page_icon=WABILI_ICON,
    layout="wide")

# Set the title of the app
st.title("Wabalanalytics")

st.write("Welcome to Wabalanalytics!! Choose your app on the left menu bar.")

def random_emoji():
    st.session_state.emoji = random.choice(emojis)

# initialize emoji as a Session State variable
if "emoji" not in st.session_state:
    st.session_state.emoji = "👈"

emojis = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼"]

st.button(f"{st.session_state.emoji}", on_click=random_emoji)
