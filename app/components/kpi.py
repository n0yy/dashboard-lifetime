import pandas as pd
import streamlit as st
from typing import Dict, List
from utils.helpers import get_date_info
from utils.helpers import convert_days_to_readable


def calculate_kpis(
    df: pd.DataFrame, machine: str, date_info: Dict[str, str]
) -> List[Dict[str, str]]:
    """Calculate KPIs for the dashboard with robust error handling."""
    try:
        if df is None or df.empty:
            return [
                {"KPI": f"Total Sparepart Terpantau ({machine})", "Nilai": "0 part"},
                {"KPI": "Part akan diganti minggu ini", "Nilai": "0 part"},
                {"KPI": "Part overdue (belum diganti)", "Nilai": "0 part"},
            ]

        df["Penggantian Selanjutnya"] = pd.to_datetime(
            df["Penggantian Selanjutnya"], format="%d/%m/%Y", errors="coerce"
        )
        today = pd.to_datetime(date_info["today"], format="%d-%m-%Y")
        df["Jadwal Penggantian"] = (df["Penggantian Selanjutnya"] - today).dt.days
        df = df.drop_duplicates(subset=["Part"])
        return [
            {
                "KPI": f"Total Sparepart Terpantau ({machine})",
                "Nilai": f"{len(df['Part'].drop_duplicates())} part",
            },
            {
                "KPI": f"Sparepart Vital",
                "Nilai": f"{df['Category'].str.contains('Vital', na=False).sum()} part",
            },
            {
                "KPI": "Part akan diganti minggu ini",
                "Nilai": f"{df['Jadwal Penggantian'].between(0, 7).sum()} part",
            },
            {
                "KPI": "Part overdue (belum diganti)",
                "Nilai": f"{df['STATUS'].str.contains('Melewati', na=False).sum()} part",
            },
        ]
    except KeyError as e:
        st.error(f"Missing required column: {e}")
        return []


def render_kpi_section(
    df: pd.DataFrame, machine: str, date_info: Dict[str, str]
) -> None:
    """Render KPI summary section with exclusive table display."""
    st.subheader("Ringkasan Lifetime Sparepart (Summary KPI)")

    # Use a single state variable to track which table to show
    if "active_table" not in st.session_state:
        st.session_state.active_table = None

    def toggle_table(table_name: str) -> None:
        """Toggle table visibility, hiding others when one is shown."""
        st.session_state.active_table = (
            table_name if st.session_state.active_table != table_name else None
        )

    kpi_data = calculate_kpis(df, machine, date_info)
    st.dataframe(pd.DataFrame(kpi_data), hide_index=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        sparepart, vital, lifetime = st.columns(3)
        with sparepart:
            if st.button("Tampilkan Sparepart Terpantau", key=f"sparepart_{machine}"):
                toggle_table("sparepart")
        with vital:
            if st.button("Tampilkan Sparepart Vital", key=f"vital_{machine}"):
                toggle_table("vital")
        with lifetime:
            if st.button("Tampilkan Lifetime", key=f"lifetime_{machine}"):
                toggle_table("lifetime")
    with col2:
        st.write("")

    # Show only the active table
    if st.session_state.active_table == "sparepart":
        df_sparepart = df[["Kode Part", "Part"]].drop_duplicates(subset=["Kode Part"])
        df_sparepart.index = range(1, len(df_sparepart) + 1)
        st.dataframe(df_sparepart)

    elif st.session_state.active_table == "vital":
        df_vital = df[df["Category"].str.contains("Vital", na=False)][
            ["Kode Part", "Part"]
        ]
        df_vital.index = range(1, len(df_vital) + 1)
        st.dataframe(df_vital)

    elif st.session_state.active_table == "lifetime":
        try:
            date_info = get_date_info()
            df["Penggantian Selanjutnya"] = pd.to_datetime(
                df["Penggantian Selanjutnya"], format="%d/%m/%Y", errors="coerce"
            )
            today = pd.to_datetime(date_info["today"], format="%d-%m-%Y")
            df["Jadwal Penggantian"] = (df["Penggantian Selanjutnya"] - today).dt.days

            df_part = df[df["Jadwal Penggantian"] > 0].sort_values("Jadwal Penggantian")
            df_part["Jadwal Penggantian"] = (
                df_part["Jadwal Penggantian"]
                .astype(int)
                .apply(convert_days_to_readable)
            )
            df_part = df_part[["Part", "Jadwal Penggantian"]]
            df_part.index = range(1, len(df_part) + 1)
            st.dataframe(df_part)
        except Exception as e:
            st.error(f"Error calculating lifetime: {e}")

    st.markdown("---")
