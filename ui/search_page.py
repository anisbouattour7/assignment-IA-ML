import streamlit as st

from ui import search_state as state
from ui.graph_editor import render_graph_editor
from ui.search_controls import render_search_controls


def render_search_page() -> None:
    state.init_state()
    st.title("🔎 Algorithmes de recherche")
    st.caption("Graphe orienté pondéré · recherche non informée et informée · pas à pas")
    tab_graph, tab_search = st.tabs(["🕸️ Graphe", "🔎 Recherche"])
    with tab_graph:
        render_graph_editor()
    with tab_search:
        render_search_controls()
