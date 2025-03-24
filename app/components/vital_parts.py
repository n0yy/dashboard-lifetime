import pandas as pd
import streamlit as st
from typing import List

from utils.helpers import filter_vital_parts


def render_vital_parts_section(
    df: pd.DataFrame, machine: str, status_options: List[str]
) -> None:
    """Render vital parts notification section.

    Args:
        df: Source dataframe
        machine: Machine name
        status_options: List of status filter options
    """
    st.subheader(f"Urgent Notification - {machine}")

    col_filter, col_space = st.columns([1, 3])
    with col_filter:
        status_filter = st.selectbox(
            "Filter berdasarkan STATUS",
            options=status_options,
            key=f"status_filter_{machine}",
        )

    with col_space:
        query_search = st.text_input(
            "Search bar",
            placeholder="Cari berdasarkan mesin atau kode part",
            key=f"search_{machine}",
        )

    # Apply status filter
    vital_df = filter_vital_parts(df, status_filter)

    # Apply search filter
    if query_search:
        query_lower = query_search.lower()
        vital_df = vital_df[
            vital_df[["Mesin", "Kode Part"]]
            .astype(str)
            .apply(lambda x: x.str.lower().str.contains(query_lower, na=False))
            .any(axis=1)
        ]

    if not vital_df.empty:
        st.markdown(f"**Menampilkan {len(vital_df)} item Sparepart**")
        with st.container():
            _render_vital_parts_list(vital_df)
    else:
        st.warning(f"Tidak ada jadwal penggantian dan pemesanan sparepart")


def _render_vital_parts_list(vital_df: pd.DataFrame) -> None:
    """Render list of vital parts.

    Args:
        vital_df: Filtered dataframe with vital parts
    """
    for _, row in vital_df.iterrows():
        status = row.get("STATUS", "")
        status_icon = "🟡" if "Segera Lakukan Pemesanan" in status else "🔴"

        with st.expander(
            f"{status_icon} {row.get('Mesin', 'N/A')} - {row.get('Kode Part', 'N/A')} - {row.get('Part', 'N/A')}"
        ):
            st.markdown(f"**Status:** {row.get('STATUS', 'N/A')}")
            st.markdown(
                f"**Penggantian Selanjutnya:** :calendar: {row.get('Penggantian Selanjutnya', 'N/A')}"
            )
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Quantity:** 📦 {row.get('Qty', 'N/A')}")
                st.markdown(f"**Category:** 🏷️ {row.get('Category', 'N/A')}")
                st.markdown(
                    f"**Lifetime:** ⏳ {row.get('Lifetime (Bulan)', 'N/A')} bulan"
                )
            with col2:
                st.markdown(
                    f"**Penggantian Terakhir:** 🛠️ {row.get('Penggantian Terakhir', 'N/A')}"
                )
