import streamlit as st
import pandas as pd

from config import (
    SHEET_ID,
    MACHINE_OPTIONS,
    STATUS_OPTIONS,
    REQUIRED_COLUMNS,
    PAGE_CONFIG,
)
from utils.helpers import get_date_info, prepare_dataframe
from data.loaders import DataLoader
from components.sidebar import render_sidebar
from components.kpi import render_kpi_section
from components.vital_parts import render_vital_parts_section


def render_machine_data(
    df: pd.DataFrame, date_info: dict, status_options: list
) -> None:
    """Render data for one machine.

    Args:
        df: Machine dataframe
        date_info: Dictionary with date information
        status_options: List of status filter options
    """
    if df.empty:
        st.warning("Tidak ada data untuk mesin ini.")
        return

    # Extract unique machines from data
    machines = [m for m in df["Mesin"].unique() if m]

    if not machines:
        st.warning("Tidak ada data mesin dalam dataset.")
        render_kpi_section(df, "Tidak Ada Data", date_info)
        return

    # Create tab for each machine
    tabs = st.tabs([machine for machine in machines])

    for tab, machine in zip(tabs, machines):
        with tab:
            df_selected = df[df["Mesin"] == machine]
            render_kpi_section(df_selected, machine, date_info)
            render_vital_parts_section(df_selected, machine, status_options)


def main() -> None:
    """Main application function."""
    try:
        # Configure the page
        st.set_page_config(**PAGE_CONFIG)
        st.title("Dashboard Monitoring Sparepart")

        # Get date info
        date_info = get_date_info()

        # Render sidebar and get selected machine
        selected_machine = render_sidebar(MACHINE_OPTIONS, date_info)

        # Load data
        loader = DataLoader(SHEET_ID, MACHINE_OPTIONS)
        all_data = loader.load_all_data()

        # Check if data exists for the selected machine
        if selected_machine in all_data:
            df = prepare_dataframe(all_data[selected_machine], REQUIRED_COLUMNS)
            render_machine_data(df, date_info, STATUS_OPTIONS)
        else:
            st.error(f"Data untuk mesin {selected_machine} tidak tersedia.")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
