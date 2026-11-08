from pathlib import Path

import streamlit as st

from expert_system.models.inference_step import (
    ACTION_APPLY_RULE,
    ACTION_CYCLE,
    ACTION_FACT_FOUND,
    ACTION_GOAL_KNOWN,
    ACTION_GOAL_REACHED,
    ACTION_NO_RULE,
    ACTION_RULE_FAILED,
    ACTION_STOP,
    ACTION_SUBGOAL,
    ACTION_TRY_RULE,
)
from expert_system.models.knowledge_base import KnowledgeBase
from expert_system.services.expert_system import (
    METHOD_BACKWARD,
    METHOD_FORWARD,
    METHOD_LABELS,
    ExpertSystem,
    ExpertSystemError,
)
from ui.knowledge_management import render_knowledge_management

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "example_knowledge_base.json"

ICONS = {
    ACTION_GOAL_KNOWN: "✅",
    ACTION_APPLY_RULE: "⚙️",
    ACTION_GOAL_REACHED: "🎯",
    ACTION_STOP: "⛔",
    ACTION_SUBGOAL: "🔎",
    ACTION_TRY_RULE: "📐",
    ACTION_FACT_FOUND: "✔️",
    ACTION_RULE_FAILED: "❌",
    ACTION_NO_RULE: "🚫",
    ACTION_CYCLE: "🔁",
}


# ---------------------------------------------------------------- état de session
def _init_state() -> None:
    if "se_system" not in st.session_state:
        st.session_state.se_system = ExpertSystem(KnowledgeBase.load_json(DATA_FILE))
    st.session_state.setdefault("se_result", None)
    st.session_state.setdefault("se_visible", 0)
    st.session_state.setdefault("se_error", None)


def _reset_run() -> None:
    """Efface la trace précédente (changement d'objectif ou de méthode)."""
    st.session_state.se_result = None
    st.session_state.se_visible = 0
    st.session_state.se_error = None


def _launch() -> None:
    _reset_run()
    try:
        result = st.session_state.se_system.run(
            st.session_state.se_goal, st.session_state.se_method
        )
    except ExpertSystemError as exc:
        st.session_state.se_error = str(exc)
        return
    st.session_state.se_result = result
    st.session_state.se_visible = 1  # on affiche la première étape


def _next_step() -> None:
    total = len(st.session_state.se_result.steps)
    st.session_state.se_visible = min(st.session_state.se_visible + 1, total)


def _show_all() -> None:
    st.session_state.se_visible = len(st.session_state.se_result.steps)


# ---------------------------------------------------------------- affichage
def _md(text: str) -> str:
    """Échappe les underscores pour que Markdown n'italicise pas les identifiants."""
    return text.replace("_", "\\_")


def _render_knowledge_base(system: ExpertSystem) -> None:
    kb = system.knowledge_base
    col_facts, col_rules = st.columns([1, 2])
    with col_facts:
        st.subheader("Faits initiaux")
        for fact in kb.get_facts():
            st.markdown(f"- `{fact.name}`")
    with col_rules:
        st.subheader("Règles")
        for rule in kb.get_rules():
            conditions = " **ET** ".join(f"`{c}`" for c in rule.conditions)
            st.markdown(f"**{rule.id}** : **SI** {conditions} **ALORS** `{rule.conclusion}`")


def _render_configuration(system: ExpertSystem) -> None:
    st.subheader("Configuration")
    kb = system.knowledge_base
    options = kb.known_symbols()
    if not options:
        st.warning("La base de connaissances est vide.")
        return

    rules = kb.get_rules()
    default = options.index(rules[-1].conclusion) if rules else 0

    st.selectbox(
        "Objectif à démontrer",
        options,
        index=default,
        key="se_goal",
        on_change=_reset_run,
    )
    if system.is_goal_known(st.session_state.se_goal):
        st.info("Cet objectif est déjà présent dans la base de faits.")
    else:
        st.warning("Cet objectif n'est pas présent dans les faits initiaux.")

    st.radio(
        "Méthode de chaînage",
        [METHOD_FORWARD, METHOD_BACKWARD],
        format_func=METHOD_LABELS.get,
        horizontal=True,
        key="se_method",
        on_change=_reset_run,
    )
    st.button("🚀 Lancer le raisonnement", type="primary", on_click=_launch)

    if st.session_state.se_error:
        st.error(st.session_state.se_error)


def _render_trace() -> None:
    result = st.session_state.se_result
    if result is None:
        return
    total = len(result.steps)
    visible = st.session_state.se_visible

    st.subheader("Trace du raisonnement")
    st.progress(visible / total, text=f"Étape {visible} / {total}")

    col1, col2, col3 = st.columns(3)
    col1.button("⏭️ Étape suivante", on_click=_next_step, disabled=visible >= total)
    col2.button("⏩ Tout afficher", on_click=_show_all, disabled=visible >= total)
    col3.button("🔄 Réinitialiser", on_click=_reset_run)

    for step in result.steps[:visible]:
        indent = "&emsp;" * step.depth
        icon = ICONS.get(step.action, "•")
        st.markdown(f"{indent}**{step.number}.** {icon} {_md(step.explanation)}")

    if visible >= total:
        _render_result(result)


def _render_result(result) -> None:
    st.subheader("Résultat")
    if result.success:
        st.success(result.message)
    else:
        st.error(result.message)

    col1, col2, col3 = st.columns(3)
    col1.metric("Statut", "Démontré" if result.success else "Non démontré")
    col2.metric("Méthode", result.method)
    col3.metric("Règles utilisées", len(result.rules_applied))

    if result.rules_applied:
        st.markdown("**Règles appliquées :** " + ", ".join(result.rules_applied))
    if result.derived_facts:
        st.markdown("**Faits déduits :** " + ", ".join(f"`{f}`" for f in result.derived_facts))


def render_expert_system_page() -> None:
    _init_state()
    st.title("🧠 Systèmes experts")
    st.caption("Base de faits + base de règles · chaînage avant et arrière · trace pas à pas")
    system: ExpertSystem = st.session_state.se_system

    tab_run, tab_manage = st.tabs(["🧠 Raisonnement", "🛠️ Gestion des connaissances"])
    with tab_run:
        _render_knowledge_base(system)
        st.divider()
        _render_configuration(system)
        st.divider()
        _render_trace()
    with tab_manage:
        render_knowledge_management()
