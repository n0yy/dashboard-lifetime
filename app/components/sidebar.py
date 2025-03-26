import streamlit as st
from typing import Dict, List


def render_sidebar(machine_options: List[str], date_info: Dict[str, str]) -> str:
    """Render sidebar content and return selected machine type.

    Args:
        machine_options: List of machine types
        date_info: Dictionary with date information

    Returns:
        Selected machine type
    """
    with st.sidebar:
        st.image("app/assets/logo_b7.png")

        # Machine selection

        # Navigation menu
        st.markdown("### Menu Navigasi")
        machine_type = st.selectbox(
            label="Lifetime",
            label_visibility="hidden",
            placeholder="Pilih Jenis Mesin",
            options=machine_options,
            index=0,
        )
        st.page_link("pages/kanban.py", label="Kanban")
        st.page_link("pages/kanban.py", label="Monitoring Expense")
        st.page_link("pages/kanban.py", label="Kolaborasi CKG dan PG")
        st.page_link("pages/kanban.py", label="CMMS")

    return machine_type
