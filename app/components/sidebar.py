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
        # st.image("../assets/logo_b7.png")

        # Machine selection
        machine_type = st.selectbox(
            label="Lifetime",
            placeholder="Pilih Jenis Mesin",
            options=machine_options,
            index=0,
        )

        # Navigation menu
        st.markdown("### Menu Navigasi")
        st.page_link("main.py", label="Kanban")
        st.page_link("main.py", label="Monitoring Expense")
        st.page_link("main.py", label="Kolaborasi CKG dan PG")
        st.page_link("main.py", label="CMMS")

    return machine_type
