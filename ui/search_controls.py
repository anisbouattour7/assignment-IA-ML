import time

import streamlit as st

from graph_search.algorithms.base import CATEGORY_INFORMED, CATEGORY_UNINFORMED, fmt
from graph_search.algorithms.registry import ALGORITHMS, CATEGORY_LABELS, algorithms_in
from graph_search.models.graph_model import GraphError, GraphModel
from graph_search.models.search_config import SearchConfig
from graph_search.models.search_step import (
    ACTION_DISCOVER,
    ACTION_EXPAND,
    ACTION_GOAL,
    ACTION_IGNORE,
    ACTION_INIT,
    ACTION_STOP,
    ACTION_UPDATE,
    SearchStep,
)
from graph_search.services.search_service import SearchService
from ui import search_state as state
from ui.visualization import build_figure

CH = "search"
ICONS = {
    ACTION_INIT: "🏁",
    ACTION_EXPAND: "📤",
    ACTION_DISCOVER: "🔍",
    ACTION_UPDATE: "🔄",
    ACTION_IGNORE: "⏭️",
    ACTION_GOAL: "🎯",
    ACTION_STOP: "⛔",
}


def _md(text: str) -> str:
    """Échappe les underscores pour que Markdown n'italicise pas les noms de sommets."""
    return text.replace("_", "\\_")


# ---------------------------------------------------------------- callbacks
def _run(service: SearchService, config: SearchConfig) -> None:
    state.reset_run()
    try:
        result = service.run(state.graph(), config)
    except GraphError as exc:
        state.notify(CH, "error", str(exc))
        return
    st.session_state.gs_result = result
    st.session_state.gs_visible = 1  # on affiche la première étape


def _next_step() -> None:
    total = len(st.session_state.gs_result.steps)
    st.session_state.gs_visible = min(st.session_state.gs_visible + 1, total)


def _show_all() -> None:
    st.session_state.gs_visible = len(st.session_state.gs_result.steps)


def _compare() -> None:
    """Lance les 5 algorithmes sur le graphe courant et compare les performances."""
    graph = state.graph()
    service = SearchService()
    rows = []
    for code in ALGORITHMS:
        config = SearchConfig(graph.start, graph.goal, code)
        errors = service.validate(graph, config)
        if errors:
            rows.append(
                {
                    "Algorithme": code,
                    "Trouvé": "—",
                    "Coût": "—",
                    "Chemin": "—",
                    "Sommets développés": "—",
                    "Temps (ms)": "—",
                    "Remarque": " ; ".join(errors),
                }
            )
            continue
        start = time.perf_counter()
        result = service.run(graph, config)
        elapsed_ms = (time.perf_counter() - start) * 1000
        rows.append(
            {
                "Algorithme": code,
                "Trouvé": "Oui" if result.found else "Non",
                "Coût": fmt(result.total_cost) if result.found else "—",
                "Chemin": " → ".join(result.path) if result.found else "—",
                "Sommets développés": str(result.expanded_count),
                "Temps (ms)": f"{elapsed_ms:.2f}",
                "Remarque": " ".join(result.warnings),
            }
        )
    st.session_state.gs_compare = rows


# ---------------------------------------------------------------- affichage
def _check(service, graph: GraphModel, category: str, code: str):
    """Retourne (erreurs bloquantes, configuration)."""
    errors = []
    if graph.start is None:
        errors.append("Choisissez l'état initial dans l'onglet Graphe.")
    if graph.goal is None:
        errors.append("Choisissez l'état objectif dans l'onglet Graphe.")
    if errors:
        return errors, None
    config = SearchConfig(graph.start, graph.goal, code, category)
    return service.validate(graph, config), config


def _render_frontier(step: SearchStep) -> None:
    if not step.frontier:
        frontier = "vide"
    elif step.frontier_costs:
        frontier = ", ".join(
            f"`{n}` ({fmt(c)})" for n, c in zip(step.frontier, step.frontier_costs, strict=False)
        )
    else:
        frontier = ", ".join(f"`{n}`" for n in step.frontier)
    st.markdown(f"**Frontière :** {frontier}")
    st.markdown("**Développés :** " + (", ".join(f"`{n}`" for n in step.visited) or "aucun"))
    st.caption("Valeur entre parenthèses : priorité du sommet (g, h ou f selon l'algorithme).")


def _render_result(result) -> None:
    st.subheader("Résultat")
    if result.found:
        st.success(result.message)
    else:
        st.error(result.message)
    for warning in result.warnings:
        st.warning(warning)
    col1, col2, col3 = st.columns(3)
    col1.metric("Statut", "Chemin trouvé" if result.found else "Aucun chemin")
    col2.metric("Coût total", fmt(result.total_cost) if result.total_cost is not None else "—")
    col3.metric("Sommets développés", result.expanded_count)
    if result.found:
        st.markdown("**Chemin :** " + " → ".join(f"`{n}`" for n in result.path))


def _render_run(graph: GraphModel) -> None:
    result = st.session_state.gs_result
    if result is None:
        st.pyplot(build_figure(graph))
        return

    total = len(result.steps)
    visible = st.session_state.gs_visible
    final = visible >= total
    st.progress(visible / total, text=f"Étape {visible} / {total}")
    col1, col2, col3 = st.columns(3)
    col1.button("⏭️ Étape suivante", on_click=_next_step, disabled=final)
    col2.button("⏩ Tout afficher", on_click=_show_all, disabled=final)
    col3.button("🔄 Réinitialiser", on_click=state.reset_run)

    step = result.steps[visible - 1]
    col_fig, col_trace = st.columns([3, 2])
    with col_fig:
        path = result.path if final and result.found else ()
        st.pyplot(build_figure(graph, step, path))
        _render_frontier(step)
    with col_trace:
        with st.container(height=420):
            for s in result.steps[:visible]:
                st.markdown(f"**{s.index}.** {ICONS.get(s.action, '•')} {_md(s.explanation)}")
    if final:
        _render_result(result)


def render_search_controls() -> None:
    state.show_message(CH)
    graph = state.graph()
    service = SearchService()

    st.subheader("Configuration de la recherche")
    category = st.radio(
        "Type de recherche",
        [CATEGORY_UNINFORMED, CATEGORY_INFORMED],
        format_func=CATEGORY_LABELS.get,
        horizontal=True,
        key="sc_category",
        on_change=state.reset_run,
    )
    labels = {a.code: a.label for a in algorithms_in(category)}
    code = st.selectbox(
        "Algorithme",
        list(labels),
        format_func=labels.get,
        key=f"sc_algo_{category}",
        on_change=state.reset_run,
    )
    st.caption(ALGORITHMS[code].priority)
    st.markdown(
        f"**État initial :** `{graph.start or '—'}` · **État objectif :** `{graph.goal or '—'}`"
    )

    errors, config = _check(service, graph, category, code)
    for message in errors:
        st.error(message)
    st.button(
        "🚀 Lancer la recherche",
        type="primary",
        disabled=bool(errors),
        on_click=_run,
        args=(service, config),
    )

    st.divider()
    _render_run(graph)

    st.divider()
    with st.expander("📊 Comparer tous les algorithmes"):
        st.caption(
            "Exécute les cinq algorithmes sur le graphe courant (départ et objectif choisis)."
        )
        st.button(
            "Lancer la comparaison",
            on_click=_compare,
            disabled=graph.start is None or graph.goal is None,
        )
        if st.session_state.gs_compare:
            st.dataframe(st.session_state.gs_compare, hide_index=True)
