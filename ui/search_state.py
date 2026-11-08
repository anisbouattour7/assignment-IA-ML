from pathlib import Path

import streamlit as st

from graph_search.models.graph_model import GraphModel

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
GRAPH_DIR = DATA_DIR / "graphs"  # graphes sauvegardés par l'utilisateur
SAMPLE_FILE = DATA_DIR / "sample_graph.json"


def init_state() -> None:
    if "gs_graph" not in st.session_state:
        st.session_state.gs_graph = GraphModel.load_json(SAMPLE_FILE)
    st.session_state.setdefault("gs_result", None)
    st.session_state.setdefault("gs_visible", 0)
    st.session_state.setdefault("gs_compare", None)


def graph() -> GraphModel:
    return st.session_state.gs_graph


def set_graph(new_graph: GraphModel) -> None:
    st.session_state.gs_graph = new_graph
    after_graph_change()


def reset_run() -> None:
    """Efface la recherche en cours (résultat, étape affichée, comparaison)."""
    st.session_state.gs_result = None
    st.session_state.gs_visible = 0
    st.session_state.gs_compare = None


def after_graph_change() -> None:
    """Le graphe a changé : on efface la recherche et les champs de saisie de l'éditeur."""
    reset_run()
    for key in [k for k in st.session_state.keys() if k.startswith("ge_")]:
        del st.session_state[key]


def notify(channel: str, kind: str, text: str) -> None:
    """Message affiché au prochain rendu (kind : success, error ou warning)."""
    st.session_state[f"gs_msg_{channel}"] = (kind, text)


def show_message(channel: str) -> None:
    msg = st.session_state.pop(f"gs_msg_{channel}", None)
    if msg:
        getattr(st, msg[0])(msg[1])
