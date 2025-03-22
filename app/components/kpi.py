import pandas as pd
import streamlit as st
from typing import Dict, List


def calculate_kpis(
    df: pd.DataFrame, machine: str, date_info: Dict[str, str]
) -> List[Dict[str, str]]:
    """Calculate KPIs for the dashboard.

    Args:
        df: Source dataframe
        machine: Machine name
        date_info: Dictionary with date information

    Returns:
        List of KPI dictionaries
    """
    if df.empty:
        return [
            {"KPI": f"Total Sparepart Terpantau ({machine})", "Nilai": "0 part"},
            {"KPI": "Part akan diganti bulan ini", "Nilai": "0 part"},
            {"KPI": "Part overdue (belum diganti)", "Nilai": "0 part"},
        ]

    return [
        {
            "KPI": f"Total Sparepart Terpantau ({machine})",
            "Nilai": f"{len(df['Part'].unique())} part",
        },
        {
            "KPI": "Part akan diganti bulan ini",
            "Nilai": f"{sum(df['Penggantian Selanjutnya'].str.contains(date_info['month'], na=False))} part",
        },
        {
            "KPI": "Part overdue (belum diganti)",
            "Nilai": f"{sum(df['STATUS'].str.contains('Segera Jadwalkan Penggantian', na=False))} part",
        },
    ]


def render_kpi_section(
    df: pd.DataFrame, machine: str, date_info: Dict[str, str]
) -> None:
    """Render KPI summary section.

    Args:
        df: Source dataframe
        machine: Machine name
        date_info: Dictionary with date information
    """
    st.subheader("Ringkasan Lifetime Sparepart (Summary KPI)")
    kpi_data = calculate_kpis(df, machine, date_info)
    st.markdown("---")
    st.dataframe(pd.DataFrame(kpi_data), hide_index=True)
    st.markdown("---")
