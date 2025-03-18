import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

# --- Setup Google Sheets ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
credential = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(credential)
SHEET_ID = "14d7-QMAdXBvCtVO-XKqHGZdtl6HrthCb2tqQoUXPOCk"
sheet = client.open_by_key(SHEET_ID)

# --- Fetch Data ---
ilapak = sheet.worksheet("ILAPAK")
list_of_lists = ilapak.get_all_values()
headers = list_of_lists[1]
data = list_of_lists[2:]
df = pd.DataFrame(data, columns=headers)
df.rename(columns={"Penggantian \nTerakhir": "Penggantian Terakhir"}, inplace=True)

# --- App Config ---
st.set_page_config("Dashboard Database Lifetime ILAPAK :eye:", layout="wide")
st.title("Dashboard Project Database ILAPAK :eye:")
st.markdown("---")

# --- Main Data Section ---
st.subheader("Main Data")
st.dataframe(df, use_container_width=True)
st.markdown("---")

# --- Data Vital dan Urgent Section ---
st.subheader("Data Vital dan Urgent")

# Filter Section
col_filter, col_space = st.columns([1, 3])
with col_filter:
    filter_option = st.selectbox(
        "Filter berdasarkan STATUS",
        options=["Semua", "Segera Jadwalkan Penggantian", "Segera Lakukan Pemesanan"],
    )

# Apply Filters
df_vital = df[
    (df["Category"] == "Vital") & (df["STATUS"].str.contains("Segera", na=False))
]
if filter_option != "Semua":
    df_vital = df_vital[df_vital["STATUS"].str.contains(filter_option, na=False)]

# Display Data
if not df_vital.empty:
    st.markdown(f"**Menampilkan {len(df_vital)} item Vital dan Urgent**")
    st.markdown("---")

    # List Container
    list_container = st.container()
    with list_container:
        for i, row in df_vital.iterrows():
            # Expander for each item
            status_icon = "🟡" if row["STATUS"] == "Segera Lakukan Pemesanan" else "🔴"
            with st.expander(
                f"{status_icon} {row['Mesin']} - {row['Kode Part']} - {row['Part']}"
            ):
                st.markdown(f"**Status:** {row['STATUS']}")
                st.markdown(
                    f"**Penggantian Selanjutnya:** :calendar: {row['Penggantian Selanjutnya']}"
                )

                # Two columns for details
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Quantity:** 📦 {row['Qty']}")
                    st.markdown(f"**Category:** 🏷️ {row['Category']}")
                    st.markdown(f"**Lifetime:** ⏳ {row['Lifetime (Bulan)']} bulan")
                with col2:
                    st.markdown(
                        f"**Penggantian Terakhir:** 🛠️ {row['Penggantian Terakhir']}"
                    )
                    if "Reorder Min" in row and row["Reorder Min"]:
                        st.markdown(f"**Reorder Min:** {row['Reorder Min']}")
                    if "On Hand" in row and row["On Hand"]:
                        st.markdown(f"**On Hand:** ✅ {row['On Hand']}")
                    if "Leadtime (Hari)" in row and row["Leadtime (Hari)"]:
                        st.markdown(f"**Leadtime:** 🚚 {row['Leadtime (Hari)']} hari")
else:
    st.warning("Tidak ada data yang sesuai dengan filter.")
