import gspread
import pandas as pd
import time
import streamlit as st
import json
from google.oauth2.service_account import Credentials

# --- Constants ---
SHEET_ID = "14d7-QMAdXBvCtVO-XKqHGZdtl6HrthCb2tqQoUXPOCk"
MACHINE_OPTIONS = ["ILAPAK", "SIG"]
STATUS_OPTIONS = ["Semua", "Segera Jadwalkan Penggantian", "Segera Lakukan Pemesanan"]

# --- Setup Page ---
st.set_page_config(
    page_title="Dashboard Database Lifetime Machine", page_icon=":eye:", layout="wide"
)


# --- Helper Functions ---
def get_date_info():
    """Return current date info"""
    return {"today": time.strftime("%Y-%m-%d"), "month": time.strftime("%Y-%m")}


def setup_google_sheets():
    """Setup and return Google Sheets client"""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials_dict = st.secrets["spreadsheet"]
    credential = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    client = gspread.authorize(credential)
    return client.open_by_key(SHEET_ID)


def load_worksheet_data(sheet, worksheet_name):
    """Load data from a specific worksheet"""
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_values()
    if len(data) < 2:
        return pd.DataFrame()
    headers = data[1]
    rows = data[2:]
    return pd.DataFrame(rows, columns=headers)


def load_all_data(sheet):
    """Load data for all machine types"""
    data_frames = {}
    for machine in MACHINE_OPTIONS:
        data_frames[machine] = load_worksheet_data(sheet, machine)
    return data_frames


def prepare_dataframe(df):
    """Prepare dataframe for analysis by converting types"""
    df_copy = df.copy()
    df_copy["Leadtime (Hari)"] = pd.to_numeric(
        df_copy["Leadtime (Hari)"], errors="coerce"
    )
    return df_copy


def calculate_kpis(df, machine, date_info):
    """Calculate KPIs for the dashboard"""
    return [
        {
            "KPI": f"Total Sparepart Terpantau ({machine})",
            "Nilai": f"{len(df['Part'].unique())} part",
        },
        {
            "KPI": "Part akan diganti bulan ini",
            "Nilai": f"{len(df[df['Penggantian Selanjutnya'].str.contains(date_info['month'], na=False)])} part",
        },
        {
            "KPI": "Part overdue (belum diganti)",
            "Nilai": f"{df['STATUS'].str.contains('Segera Jadwalkan Penggantian', na=False).sum()} part",
        },
        {
            "KPI": "Rata-rata lead time",
            "Nilai": f"{round(df['Leadtime (Hari)'].fillna(0).mean())} hari",
        },
    ]


def filter_vital_parts(df, status_filter):
    """Filter vital and urgent parts based on status"""
    vital_df = df[
        (df["Category"] == "Vital") & (df["STATUS"].str.contains("Segera", na=False))
    ]
    if status_filter != "Semua":
        vital_df = vital_df[vital_df["STATUS"].str.contains(status_filter, na=False)]
    return vital_df


def render_sidebar(date_info):
    """Render sidebar content"""
    with st.sidebar:
        st.markdown(f"# Sidebar\n{date_info['today']}")
        st.markdown("---")
        st.markdown("Home")


def render_kpi_section(df, machine, date_info):
    """Render KPI summary section"""
    st.subheader("Ringkasan Lifetime Sparepart (Summary KPI)")
    kpi_data = calculate_kpis(df, machine, date_info)
    st.markdown("---")
    st.dataframe(pd.DataFrame(kpi_data), hide_index=True)
    st.markdown("---")


def render_vital_parts_section(df, machine):
    """Render vital parts notification section"""
    st.subheader(f"Notifikasi Prioritas - {machine}")

    col_filter, col_space = st.columns([1, 3])
    with col_filter:
        status_filter = st.selectbox(
            "Filter berdasarkan STATUS", options=STATUS_OPTIONS
        )

    with col_space:
        query_search = st.text_input(
            "Search bar", placeholder="Cari berdasarkan mesin atau kode part"
        )

    # Menerapkan filter status
    vital_df = filter_vital_parts(df, status_filter)

    # Menerapkan filter pencarian
    if query_search:
        query_lower = query_search.lower()
        vital_df = vital_df[
            vital_df[["Mesin", "Kode Part"]]
            .apply(lambda x: x.str.lower().str.contains(query_lower, na=False))
            .any(axis=1)
        ]

    if not vital_df.empty:
        st.markdown(
            f"**Menampilkan {len(vital_df)} item Vital dan Urgent untuk {machine}**"
        )
        with st.container():
            render_vital_parts_list(vital_df)
    else:
        st.warning(
            f"Tidak ada data Vital dan Urgent yang sesuai dengan filter untuk {machine}."
        )


def render_vital_parts_list(vital_df):
    """Render list of vital parts"""
    for _, row in vital_df.iterrows():
        status_icon = "🟡" if row["STATUS"] == "Segera Lakukan Pemesanan" else "🔴"
        with st.expander(
            f"{status_icon} {row['Mesin']} - {row['Kode Part']} - {row['Part']}"
        ):
            st.markdown(f"**Status:** {row['STATUS']}")
            st.markdown(
                f"**Penggantian Selanjutnya:** :calendar: {row['Penggantian Selanjutnya']}"
            )
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Quantity:** 📦 {row['Qty']}")
                st.markdown(f"**Category:** 🏷️ {row['Category']}")
                st.markdown(f"**Lifetime:** ⏳ {row['Lifetime (Bulan)']} bulan")
            with col2:
                st.markdown(
                    f"**Penggantian Terakhir:** 🛠️ {row['Penggantian Terakhir']}"
                )


def main():
    """Main application function"""
    date_info = get_date_info()
    sheet = setup_google_sheets()
    all_data = load_all_data(sheet)

    render_sidebar(date_info)
    machine = st.selectbox(label="Pilih Jenis Mesin", options=MACHINE_OPTIONS)
    df = prepare_dataframe(all_data[machine])

    render_kpi_section(df, machine, date_info)
    render_vital_parts_section(df, machine)


if __name__ == "__main__":
    main()
