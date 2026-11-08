import re
from pathlib import Path

import streamlit as st

from expert_system.models.knowledge_base import KnowledgeBase
from expert_system.models.rule import Rule
from expert_system.services.expert_system import ExpertSystem

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# Clés des champs de formulaire à réinitialiser après chaque changement de la base
_FORM_KEY_PREFIXES = ("km_rid_", "km_cond_", "km_concl_", "km_ren_", "km_new_")


# ---------------------------------------------------------------- utilitaires
def _kb() -> KnowledgeBase:
    return st.session_state.se_system.knowledge_base


def _notify(kind: str, text: str) -> None:
    """Message affiché au prochain rendu (kind : success, error ou warning)."""
    st.session_state.km_msg = (kind, text)


def _after_change() -> None:
    """La base a changé : on efface la trace, l'objectif choisi et les champs de saisie."""
    st.session_state.se_result = None
    st.session_state.se_visible = 0
    st.session_state.se_error = None
    st.session_state.pop("se_goal", None)
    for key in [k for k in st.session_state.keys() if k.startswith(_FORM_KEY_PREFIXES)]:
        del st.session_state[key]


def _parse_conditions(text: str) -> tuple[str, ...]:
    return tuple(c.strip() for c in text.replace(";", ",").split(",") if c.strip())


def _next_rule_id() -> str:
    used = {r.id for r in _kb().get_rules()}
    i = 1
    while f"R{i}" in used:
        i += 1
    return f"R{i}"


def _md(text: str) -> str:
    return text.replace("_", "\\_")


# ---------------------------------------------------------------- callbacks : faits
def _add_fact() -> None:
    name = st.session_state.km_new_fact
    try:
        added = _kb().add_fact(name)
    except ValueError as exc:
        _notify("error", str(exc))
        return
    if added:
        _notify("success", f"Fait « {name.strip()} » ajouté.")
        _after_change()
    else:
        _notify("warning", f"Le fait « {name.strip()} » existe déjà.")


def _delete_fact(name: str) -> None:
    try:
        _kb().remove_fact(name)
    except ValueError as exc:
        _notify("error", str(exc))
        return
    _notify("success", f"Fait « {name} » supprimé.")
    _after_change()


def _rename_fact() -> None:
    old, new = st.session_state.km_ren_old, st.session_state.km_ren_new
    try:
        _kb().update_fact(old, new)
    except ValueError as exc:
        _notify("error", str(exc))
        return
    _notify("success", f"Fait « {old} » renommé en « {new.strip()} ».")
    _after_change()


# ---------------------------------------------------------------- callbacks : règles
def _add_rule() -> None:
    rule_id = st.session_state.km_new_rid
    conditions = _parse_conditions(st.session_state.km_new_cond)
    conclusion = st.session_state.km_new_concl
    try:
        _kb().add_rule(Rule(rule_id, conditions, conclusion))
    except ValueError as exc:
        _notify("error", str(exc))
        return
    _notify("success", f"Règle « {rule_id.strip()} » ajoutée.")
    _after_change()


def _save_rule(old_id: str) -> None:
    new_id = st.session_state[f"km_rid_{old_id}"]
    conditions = _parse_conditions(st.session_state[f"km_cond_{old_id}"])
    conclusion = st.session_state[f"km_concl_{old_id}"]
    try:
        _kb().update_rule(old_id, Rule(new_id, conditions, conclusion))
    except ValueError as exc:
        _notify("error", str(exc))
        return
    _notify("success", f"Règle « {old_id} » modifiée.")
    _after_change()


def _delete_rule(rule_id: str) -> None:
    try:
        _kb().remove_rule(rule_id)
    except ValueError as exc:
        _notify("error", str(exc))
        return
    _notify("success", f"Règle « {rule_id} » supprimée.")
    _after_change()


# ---------------------------------------------------------------- callbacks : sauvegarde
def _save_kb() -> None:
    name = re.sub(r"[^\w\-]", "_", Path(st.session_state.km_save_name.strip()).stem)
    if not name:
        _notify("error", "Donnez un nom de fichier.")
        return
    try:
        DATA_DIR.mkdir(exist_ok=True)
        path = DATA_DIR / f"{name}.json"
        _kb().save_json(path)
    except OSError as exc:
        _notify("error", f"Sauvegarde impossible : {exc}")
        return
    _notify("success", f"Base sauvegardée dans data/{path.name}.")


def _load_kb() -> None:
    name = st.session_state.km_load_file
    try:
        kb = KnowledgeBase.load_json(DATA_DIR / name)
    except (OSError, ValueError) as exc:  # JSON invalide, format inattendu, fichier absent
        _notify("error", f"Chargement impossible : {exc}")
        return
    errors = kb.validate()
    if errors:
        _notify("error", "Base invalide : " + " ; ".join(errors))
        return
    st.session_state.se_system = ExpertSystem(kb)
    _notify("success", f"Base « {name} » chargée.")
    _after_change()


def _new_empty_kb() -> None:
    st.session_state.se_system = ExpertSystem(KnowledgeBase())
    _notify("success", "Nouvelle base vide créée.")
    _after_change()


# ---------------------------------------------------------------- affichage
def _render_facts() -> None:
    st.subheader("Faits")
    facts = _kb().get_facts()
    if not facts:
        st.caption("Aucun fait.")
    for fact in facts:
        col_name, col_del = st.columns([6, 1])
        col_name.markdown(f"`{fact.name}`")
        col_del.button(
            "🗑️",
            key=f"km_delf_{fact.name}",
            on_click=_delete_fact,
            args=(fact.name,),
            help="Supprimer ce fait",
        )

    with st.form("km_form_add_fact"):
        st.text_input("Nouveau fait", key="km_new_fact", placeholder="ex. cable_branche")
        st.form_submit_button("➕ Ajouter le fait", on_click=_add_fact)

    if facts:
        with st.form("km_form_rename_fact"):
            st.selectbox("Fait à renommer", [f.name for f in facts], key="km_ren_old")
            st.text_input("Nouveau nom", key="km_ren_new")
            st.form_submit_button("✏️ Renommer", on_click=_rename_fact)


def _render_rules() -> None:
    st.subheader("Règles")
    st.caption("Les conditions d'une règle sont reliées par **ET**.")
    for rule in _kb().get_rules():
        rid = rule.id
        with st.expander(_md(str(rule))):
            with st.form(f"km_form_{rid}"):
                st.text_input("Identifiant", value=rid, key=f"km_rid_{rid}")
                st.text_input(
                    "Conditions (séparées par des virgules)",
                    value=", ".join(rule.conditions),
                    key=f"km_cond_{rid}",
                )
                st.text_input("Conclusion", value=rule.conclusion, key=f"km_concl_{rid}")
                col_save, col_del = st.columns(2)
                col_save.form_submit_button("💾 Enregistrer", on_click=_save_rule, args=(rid,))
                col_del.form_submit_button("🗑️ Supprimer", on_click=_delete_rule, args=(rid,))

    with st.form("km_form_add_rule"):
        st.markdown("**Nouvelle règle**")
        st.text_input("Identifiant", value=_next_rule_id(), key="km_new_rid")
        st.text_input(
            "Conditions (séparées par des virgules)",
            key="km_new_cond",
            placeholder="ex. voyant_alimentation_eteint, cable_branche",
        )
        st.text_input("Conclusion", key="km_new_concl", placeholder="ex. probleme_alimentation")
        st.form_submit_button("➕ Ajouter la règle", on_click=_add_rule)


def _render_persistence() -> None:
    st.subheader("Sauvegarde et chargement")
    col_save, col_load = st.columns(2)
    with col_save:
        st.text_input("Nom du fichier", value="ma_base", key="km_save_name")
        st.button("💾 Sauvegarder dans data/", on_click=_save_kb)
    with col_load:
        files = sorted(p.name for p in DATA_DIR.glob("*.json")) if DATA_DIR.exists() else []
        if files:
            st.selectbox("Base à charger", files, key="km_load_file")
            st.button("📂 Charger", on_click=_load_kb)
        else:
            st.caption("Aucun fichier JSON dans data/.")
    st.button("📄 Nouvelle base vide", on_click=_new_empty_kb)


def render_knowledge_management() -> None:
    msg = st.session_state.pop("km_msg", None)
    if msg:
        getattr(st, msg[0])(msg[1])
    st.caption("Les modifications s'appliquent immédiatement à l'onglet Raisonnement.")
    col_facts, col_rules = st.columns([1, 2])
    with col_facts:
        _render_facts()
    with col_rules:
        _render_rules()
    st.divider()
    _render_persistence()
