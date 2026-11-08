import os
import signal

import streamlit as st

from ui.expert_system_page import render_expert_system_page
from ui.search_page import render_search_page

st.set_page_config(page_title="IA et ML – Assignment 1", page_icon="🤖", layout="wide")


def home_page() -> None:
    st.title("Menu principal")
    st.write("Assignment 1 · IA et ML · Systèmes experts et algorithmes de recherche")
    if st.button("1. 🧠 Systèmes experts"):
        st.switch_page(PAGE_SE)
    if st.button("2. 🔎 Algorithmes de recherche"):
        st.switch_page(PAGE_SEARCH)
    if st.button("3. 🚪 Quitter"):
        st.success("Application arrêtée. Vous pouvez fermer cet onglet.")
        os.kill(os.getpid(), signal.SIGTERM)  # arrête le serveur Streamlit


PAGE_HOME = st.Page(home_page, title="Menu principal", icon="🏠", default=True)
PAGE_SE = st.Page(
    render_expert_system_page, title="Systèmes experts", icon="🧠", url_path="systemes-experts"
)
PAGE_SEARCH = st.Page(
    render_search_page, title="Algorithmes de recherche", icon="🔎", url_path="recherche"
)

st.navigation([PAGE_HOME, PAGE_SE, PAGE_SEARCH]).run()
