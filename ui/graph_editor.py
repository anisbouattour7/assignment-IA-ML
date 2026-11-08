import re
from pathlib import Path

import streamlit as st

from graph_search.algorithms.base import fmt
from graph_search.models.graph_model import GraphError, GraphModel
from ui import search_state as state
from ui.visualization import build_figure

CH = "graph"  # canal des messages de cet onglet


def _parse_h(text: str) -> float | None:
    """Champ vide = pas de valeur. Accepte la virgule décimale."""
    text = text.strip().replace(",", ".")
    if not text:
        return None
    try:
        value = float(text)
    except ValueError as exc:
        raise GraphError(f"« {text} » n'est pas un nombre.") from exc
    return int(value) if value.is_integer() else value


# ---------------------------------------------------------------- callbacks : sommets
def _add_node() -> None:
    name = st.session_state.ge_node_name
    try:
        h = _parse_h(st.session_state.ge_node_h)
        state.graph().add_node(name, h)
    except GraphError as exc:
        state.notify(CH, "error", str(exc))
        return
    state.notify(CH, "success", f"Sommet « {name.strip()} » ajouté.")
    state.after_graph_change()


def _delete_node(name: str) -> None:
    try:
        state.graph().remove_node(name)
    except GraphError as exc:
        state.notify(CH, "error", str(exc))
        return
    state.notify(CH, "success", f"Sommet « {name} » supprimé (ainsi que ses arcs).")
    state.after_graph_change()


def _set_heuristic() -> None:
    node = st.session_state.ge_h_node
    try:
        value = _parse_h(st.session_state.ge_h_value)
        state.graph().set_heuristic(node, value)
    except GraphError as exc:
        state.notify(CH, "error", str(exc))
        return
    text = "effacée" if value is None else f"définie à {fmt(value)}"
    state.notify(CH, "success", f"Heuristique de « {node} » {text}.")
    state.after_graph_change()


# ---------------------------------------------------------------- callbacks : arcs
def _add_edge() -> None:
    source, target = st.session_state.ge_edge_src, st.session_state.ge_edge_dst
    cost = st.session_state.ge_edge_cost
    cost = int(cost) if float(cost).is_integer() else cost
    try:
        state.graph().add_edge(source, target, cost)
    except GraphError as exc:
        state.notify(CH, "error", str(exc))
        return
    state.notify(CH, "success", f"Arc {source} → {target} ajouté (coût {fmt(cost)}).")
    state.after_graph_change()


def _delete_edge(source: str, target: str) -> None:
    try:
        state.graph().remove_edge(source, target)
    except GraphError as exc:
        state.notify(CH, "error", str(exc))
        return
    state.notify(CH, "success", f"Arc {source} → {target} supprimé.")
    state.after_graph_change()


# ---------------------------------------------------------------- callbacks : départ / objectif
def _on_start_change() -> None:
    state.graph().start = st.session_state.ge_start
    state.reset_run()


def _on_goal_change() -> None:
    state.graph().goal = st.session_state.ge_goal
    state.reset_run()


# ---------------------------------------------------------------- callbacks : fichiers
def _graph_files() -> dict[str, Path]:
    files = {"Graphe d'exemple": state.SAMPLE_FILE}
    if state.GRAPH_DIR.exists():
        for path in sorted(state.GRAPH_DIR.glob("*.json")):
            files[path.name] = path
    return files


def _save_graph() -> None:
    name = re.sub(r"[^\w\-]", "_", Path(st.session_state.ge_save_name.strip()).stem)
    if not name:
        state.notify(CH, "error", "Donnez un nom de fichier.")
        return
    try:
        state.GRAPH_DIR.mkdir(parents=True, exist_ok=True)
        path = state.GRAPH_DIR / f"{name}.json"
        state.graph().save_json(path)
    except OSError as exc:
        state.notify(CH, "error", f"Sauvegarde impossible : {exc}")
        return
    state.notify(CH, "success", f"Graphe sauvegardé dans data/graphs/{path.name}.")


def _load_graph() -> None:
    label = st.session_state.ge_load_file
    try:
        loaded = GraphModel.load_json(_graph_files()[label])
    except (OSError, ValueError) as exc:  # fichier absent, JSON invalide, graphe incohérent
        state.notify(CH, "error", f"Chargement impossible : {exc}")
        return
    errors = loaded.validate()
    if errors:
        state.notify(CH, "error", "Graphe invalide : " + " ; ".join(errors))
        return
    state.set_graph(loaded)
    state.notify(CH, "success", f"Graphe « {label} » chargé.")


def _new_graph() -> None:
    state.set_graph(GraphModel())
    state.notify(CH, "success", "Nouveau graphe vide créé.")


# ---------------------------------------------------------------- affichage
def _render_nodes(graph: GraphModel) -> None:
    st.subheader("Sommets")
    nodes = graph.nodes()
    if not nodes:
        st.caption("Aucun sommet.")
    for name in nodes:
        col_name, col_h, col_del = st.columns([3, 2, 1])
        col_name.markdown(f"`{name}`")
        h = graph.get_heuristic(name)
        col_h.markdown("h = " + (f"`{fmt(h)}`" if h is not None else "—"))
        col_del.button(
            "🗑️",
            key=f"ge_delnode_{name}",
            on_click=_delete_node,
            args=(name,),
            help="Supprimer ce sommet et ses arcs",
        )

    with st.form("ge_form_node"):
        st.text_input("Nouveau sommet", key="ge_node_name", placeholder="ex. A")
        st.text_input("Heuristique h (optionnelle)", key="ge_node_h", placeholder="ex. 7")
        st.form_submit_button("➕ Ajouter le sommet", on_click=_add_node)

    if nodes:
        with st.form("ge_form_h"):
            st.selectbox("Sommet", nodes, key="ge_h_node")
            st.text_input("Valeur de h (vide = effacer)", key="ge_h_value")
            st.form_submit_button("✏️ Définir h", on_click=_set_heuristic)


def _render_edges(graph: GraphModel) -> None:
    st.subheader("Arcs orientés")
    edges = graph.edges()
    if not edges:
        st.caption("Aucun arc.")
    for source, target, cost in edges:
        col_edge, col_del = st.columns([5, 1])
        col_edge.markdown(f"`{source}` → `{target}` (coût {fmt(cost)})")
        col_del.button(
            "🗑️",
            key=f"ge_deledge_{source}_{target}",
            on_click=_delete_edge,
            args=(source, target),
            help="Supprimer cet arc",
        )

    nodes = graph.nodes()
    if not nodes:
        st.caption("Ajoutez d'abord des sommets.")
        return
    with st.form("ge_form_edge"):
        col_a, col_b, col_c = st.columns(3)
        col_a.selectbox("Source", nodes, key="ge_edge_src")
        col_b.selectbox("Cible", nodes, key="ge_edge_dst")
        col_c.number_input("Coût", min_value=0.0, value=1.0, step=1.0, key="ge_edge_cost")
        st.form_submit_button("➕ Ajouter l'arc", on_click=_add_edge)


def _render_start_goal(graph: GraphModel) -> None:
    st.subheader("État initial et état objectif")
    nodes = graph.nodes()
    if not nodes:
        st.caption("Ajoutez des sommets pour choisir le départ et l'objectif.")
        return
    col_start, col_goal = st.columns(2)
    col_start.selectbox(
        "État initial",
        nodes,
        key="ge_start",
        on_change=_on_start_change,
        index=nodes.index(graph.start) if graph.start in nodes else None,
        placeholder="Choisir un sommet",
    )
    col_goal.selectbox(
        "État objectif",
        nodes,
        key="ge_goal",
        on_change=_on_goal_change,
        index=nodes.index(graph.goal) if graph.goal in nodes else None,
        placeholder="Choisir un sommet",
    )


def _render_persistence() -> None:
    st.subheader("Sauvegarde et chargement")
    col_save, col_load = st.columns(2)
    with col_save:
        st.text_input("Nom du fichier", value="mon_graphe", key="ge_save_name")
        st.button("💾 Sauvegarder dans data/graphs/", on_click=_save_graph)
    with col_load:
        st.selectbox("Graphe à charger", list(_graph_files()), key="ge_load_file")
        st.button("📂 Charger", on_click=_load_graph)
    st.button("📄 Nouveau graphe vide", on_click=_new_graph)


def render_graph_editor() -> None:
    state.show_message(CH)
    graph = state.graph()
    col_nodes, col_edges = st.columns(2)
    with col_nodes:
        _render_nodes(graph)
    with col_edges:
        _render_edges(graph)
    st.divider()
    _render_start_goal(graph)
    st.divider()
    st.subheader("Aperçu du graphe")
    st.pyplot(build_figure(graph))
    st.divider()
    _render_persistence()
