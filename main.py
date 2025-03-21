import gspread
import pandas as pd
import time
import streamlit as st
from google.oauth2.service_account import Credentials

# --- Constants ---
SHEET_ID = "14d7-QMAdXBvCtVO-XKqHGZdtl6HrthCb2tqQoUXPOCk"

# Semua opsi mesin yang tersedia
MACHINE_OPTIONS = ["ILAPAK", "SIG", "CHIMEI", "JINSUNG", "UNIFILL"]
STATUS_OPTIONS = ["Semua", "Segera Jadwalkan Penggantian", "Segera Lakukan Pemesanan"]

# --- Setup Page ---
st.set_page_config(
    page_title="Dashboard Database Lifetime", page_icon=":eye:", layout="wide"
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
    try:
        worksheet = sheet.worksheet(worksheet_name)
        data = worksheet.get_all_values()
        if len(data) < 2:
            return pd.DataFrame()
        headers = data[1]
        rows = data[2:]
        return pd.DataFrame(rows, columns=headers)
    except Exception as e:
        st.error(f"Error loading worksheet {worksheet_name}: {str(e)}")
        return pd.DataFrame()


def load_all_data(sheet):
    """Load data for all machine types"""
    data_frames = {}

    # Hanya coba muat worksheet yang ada
    available_worksheets = [ws.title for ws in sheet.worksheets()]

    for machine in MACHINE_OPTIONS:
        if machine in available_worksheets:
            data_frames[machine] = load_worksheet_data(sheet, machine)
        else:
            # Buat DataFrame kosong dengan kolom standar jika worksheet tidak ditemukan
            data_frames[machine] = pd.DataFrame(
                columns=[
                    "Mesin",
                    "Kode Part",
                    "Part",
                    "Qty",
                    "Category",
                    "Lifetime (Bulan)",
                    "Penggantian Terakhir",
                    "Penggantian Selanjutnya",
                    "STATUS",
                    "Leadtime (Hari)",
                ]
            )
            st.warning(f"Worksheet untuk mesin {machine} tidak ditemukan.")

    return data_frames


def prepare_dataframe(df):
    """Prepare dataframe for analysis by converting types"""
    if df.empty:
        return df

    df_copy = df.copy()

    # Pastikan semua kolom yang dibutuhkan ada
    required_columns = [
        "Mesin",
        "Kode Part",
        "Part",
        "Qty",
        "Category",
        "Lifetime (Bulan)",
        "Penggantian Terakhir",
        "Penggantian Selanjutnya",
        "STATUS",
        "Leadtime (Hari)",
    ]

    for col in required_columns:
        if col not in df_copy.columns:
            df_copy[col] = ""

    # Konversi tipe data
    try:
        df_copy["Leadtime (Hari)"] = pd.to_numeric(
            df_copy["Leadtime (Hari)"], errors="coerce"
        )

        # Pastikan kolom STATUS memiliki string, bukan NaN
        df_copy["STATUS"] = df_copy["STATUS"].fillna("")

        # Pastikan kolom Penggantian Selanjutnya memiliki string, bukan NaN
        df_copy["Penggantian Selanjutnya"] = df_copy["Penggantian Selanjutnya"].fillna(
            ""
        )
    except Exception as e:
        st.error(f"Error saat menyiapkan data: {str(e)}")

    return df_copy


def calculate_kpis(df, machine, date_info):
    """Calculate KPIs for the dashboard"""
    # Handle empty DataFrame
    if df.empty:
        return [
            {"KPI": f"Total Sparepart Terpantau ({machine})", "Nilai": "0 part"},
            {"KPI": "Part akan diganti bulan ini", "Nilai": "0 part"},
            {"KPI": "Part overdue (belum diganti)", "Nilai": "0 part"},
        ]

    # Hitung KPIs
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


def filter_vital_parts(df, status_filter):
    """Filter vital and urgent parts based on status"""
    # Handle empty DataFrame
    if df.empty:
        return df

    # Filter berdasarkan Category "Vital" dan STATUS mengandung "Segera"
    vital_df = df[
        (df["Category"].str.contains("Vital", case=False, na=False))
        & (df["STATUS"].str.contains("Segera", na=False))
    ]

    # Filter tambahan berdasarkan status yang dipilih
    if status_filter != "Semua":
        vital_df = vital_df[vital_df["STATUS"].str.contains(status_filter, na=False)]

    return vital_df


def render_sidebar(date_info):
    """Render sidebar content"""
    with st.sidebar:
        st.image("logo_b7.png")

        # Gunakan selectbox dengan opsi mesin yang tersedia
        machine_type = st.selectbox(
            label="Lifetime",
            placeholder="Pilih Jenis Mesin",
            options=MACHINE_OPTIONS,
            index=0,  # Default ke opsi pertama
        )

        # Menu navigasi (menggunakan main.py untuk mockup sesuai permintaan)
        st.markdown("### Menu Navigasi")
        st.page_link("main.py", label="Kanban")
        st.page_link("main.py", label="Monitoring Expense")
        st.page_link("main.py", label="Kolaborasi CKG dan PG")
        st.page_link("main.py", label="CMMS")

    return machine_type


def render_machine_data(df, date_info):
    """Render data untuk satu mesin"""
    if df.empty:
        st.warning("Tidak ada data untuk mesin ini.")
        return

    # Coba ekstrak mesin yang unik dari data
    machines = df["Mesin"].unique()
    # Filter out empty strings
    machines = [m for m in machines if m]

    if not machines:
        st.warning("Tidak ada data mesin dalam dataset.")
        render_kpi_section(df, "Tidak Ada Data", date_info)
        return

    # Buat tab untuk setiap mesin
    tabs = st.tabs([machine for machine in machines])

    for tab, machine in zip(tabs, machines):
        with tab:
            df_selected = df[df["Mesin"] == machine]
            render_kpi_section(df_selected, machine, date_info)
            render_vital_parts_section(df_selected, machine)


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
            "Filter berdasarkan STATUS",
            options=STATUS_OPTIONS,
            key=f"status_filter_{machine}",  # Unique key untuk setiap mesin
        )

    with col_space:
        query_search = st.text_input(
            "Search bar",
            placeholder="Cari berdasarkan mesin atau kode part",
            key=f"search_{machine}",  # Unique key untuk setiap mesin
        )

    # Menerapkan filter status
    vital_df = filter_vital_parts(df, status_filter)

    # Menerapkan filter pencarian
    if query_search:
        query_lower = query_search.lower()
        vital_df = vital_df[
            vital_df[["Mesin", "Kode Part"]]
            .astype(str)  # Ensure all values are strings
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
        st.warning(f"Tidak ada jadwal penggantian dan pemesanan sparepart")


def render_vital_parts_list(vital_df):
    """Render list of vital parts"""
    for idx, row in vital_df.iterrows():
        # Default value jika STATUS kosong
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


def main():
    """Main application function"""
    try:
        st.title("Dashboard Monitoring Sparepart")

        # Load data
        date_info = get_date_info()
        sheet = setup_google_sheets()
        all_data = load_all_data(sheet)

        # Render sidebar dan dapatkan mesin yang dipilih
        selected_machine = render_sidebar(date_info)

        # Check if data exists for the selected machine
        if selected_machine in all_data:
            df = prepare_dataframe(all_data[selected_machine])
            render_machine_data(df, date_info)
        else:
            st.error(f"Data untuk mesin {selected_machine} tidak tersedia.")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
